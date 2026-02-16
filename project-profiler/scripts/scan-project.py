#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["tiktoken"]
# ///
"""
Project Scanner for project-profiler skill.
Scans a directory tree, respects .gitignore, and outputs file paths with token counts,
tech stack detection, package metadata, and entry point identification.

Forked from Cartographer's scan-codebase.py with additional profiling capabilities.

Run with: uv run scan-project.py [path] --format json
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import tiktoken
except ImportError:
    print("ERROR: tiktoken not installed.", file=sys.stderr)
    print("Run with: uv run scan-project.py", file=sys.stderr)
    sys.exit(1)

# Default patterns to always ignore
DEFAULT_IGNORE = {
    # Directories
    ".git", ".svn", ".hg", "node_modules", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", "venv", ".venv", "env", ".env",
    "dist", "build", ".next", ".nuxt", ".output", "coverage", ".coverage",
    ".nyc_output", "target", "vendor", ".bundle", ".cargo",
    # Files
    ".DS_Store", "Thumbs.db",
    "*.pyc", "*.pyo", "*.so", "*.dylib", "*.dll", "*.exe", "*.o", "*.a",
    "*.lib", "*.class", "*.jar", "*.war", "*.egg", "*.whl",
    "*.lock", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "bun.lockb", "Cargo.lock", "poetry.lock", "Gemfile.lock", "composer.lock",
    # Binary/media
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.ico", "*.svg", "*.webp",
    "*.mp3", "*.mp4", "*.wav", "*.avi", "*.mov",
    "*.pdf", "*.zip", "*.tar", "*.gz", "*.rar", "*.7z",
    "*.woff", "*.woff2", "*.ttf", "*.eot", "*.otf",
    # Large generated files
    "*.min.js", "*.min.css", "*.map", "*.chunk.js", "*.bundle.js",
}

# Extension to language mapping
EXT_TO_LANG = {
    ".py": "python", ".pyi": "python", ".pyx": "python",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".ts": "typescript", ".tsx": "typescript", ".mts": "typescript", ".cts": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby", ".rake": "ruby", ".gemspec": "ruby",
    ".java": "java", ".kt": "kotlin", ".kts": "kotlin", ".scala": "scala",
    ".cs": "csharp", ".fs": "fsharp", ".fsx": "fsharp",
    ".swift": "swift", ".m": "objective-c", ".mm": "objective-c",
    ".c": "c", ".h": "c", ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp", ".hpp": "cpp",
    ".php": "php",
    ".lua": "lua",
    ".r": "r", ".R": "r",
    ".jl": "julia",
    ".ex": "elixir", ".exs": "elixir",
    ".erl": "erlang", ".hrl": "erlang",
    ".hs": "haskell", ".lhs": "haskell",
    ".ml": "ocaml", ".mli": "ocaml",
    ".clj": "clojure", ".cljs": "clojure", ".cljc": "clojure",
    ".dart": "dart",
    ".zig": "zig",
    ".nim": "nim",
    ".v": "v",
    ".vue": "vue",
    ".svelte": "svelte",
    ".html": "html", ".htm": "html",
    ".css": "css", ".scss": "scss", ".sass": "sass", ".less": "less",
    ".sql": "sql",
    ".sh": "shell", ".bash": "shell", ".zsh": "shell", ".fish": "shell",
    ".yml": "yaml", ".yaml": "yaml",
    ".json": "json", ".jsonc": "json",
    ".toml": "toml",
    ".xml": "xml",
    ".md": "markdown", ".mdx": "markdown",
    ".tf": "terraform", ".hcl": "hcl",
    ".nix": "nix",
    ".proto": "protobuf",
    ".graphql": "graphql", ".gql": "graphql",
}


def parse_gitignore(root: Path) -> list[str]:
    """Parse .gitignore file and return patterns."""
    gitignore_path = root / ".gitignore"
    patterns = []
    if gitignore_path.exists():
        with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    return patterns


def matches_pattern(path: Path, pattern: str, root: Path) -> bool:
    """Check if a path matches a gitignore-style pattern."""
    import fnmatch
    rel_path = str(path.relative_to(root))
    name = path.name

    if pattern.startswith("!"):
        return False

    if pattern.endswith("/"):
        if not path.is_dir():
            return False
        pattern = pattern[:-1]

    if "/" in pattern:
        if pattern.startswith("/"):
            pattern = pattern[1:]
        return fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(
            rel_path, pattern + "/**"
        )
    else:
        return fnmatch.fnmatch(name, pattern)


def should_ignore(path: Path, root: Path, gitignore_patterns: list[str]) -> bool:
    """Check if a path should be ignored."""
    import fnmatch
    name = path.name

    for pattern in DEFAULT_IGNORE:
        if "*" in pattern:
            if fnmatch.fnmatch(name, pattern):
                return True
        elif name == pattern:
            return True

    for pattern in gitignore_patterns:
        if matches_pattern(path, pattern, root):
            return True

    return False


def count_tokens(text: str, encoding: tiktoken.Encoding) -> int:
    """Count tokens in text using tiktoken."""
    try:
        return len(encoding.encode(text))
    except Exception:
        return len(text) // 4


TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".vue", ".svelte",
    ".html", ".htm", ".css", ".scss", ".sass", ".less",
    ".json", ".yaml", ".yml", ".toml", ".xml",
    ".md", ".mdx", ".txt", ".rst",
    ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd",
    ".sql", ".graphql", ".gql", ".proto",
    ".go", ".rs", ".rb", ".php", ".java", ".kt", ".kts", ".scala",
    ".clj", ".cljs", ".edn", ".ex", ".exs", ".erl", ".hrl",
    ".hs", ".lhs", ".ml", ".mli", ".fs", ".fsx", ".fsi",
    ".cs", ".vb", ".swift", ".m", ".mm", ".h", ".hpp",
    ".c", ".cpp", ".cc", ".cxx", ".r", ".R", ".jl", ".lua",
    ".vim", ".el", ".lisp", ".scm", ".rkt", ".zig", ".nim",
    ".d", ".dart", ".v", ".sv", ".vhd", ".vhdl",
    ".tf", ".hcl", ".dockerfile", ".containerfile",
    ".makefile", ".cmake", ".gradle", ".groovy",
    ".rake", ".gemspec", ".podspec", ".cabal", ".nix", ".dhall",
    ".jsonc", ".json5", ".cson", ".ini", ".cfg", ".conf", ".config",
    ".env", ".env.example", ".env.local",
    ".gitignore", ".gitattributes", ".editorconfig",
    ".prettierrc", ".eslintrc", ".stylelintrc", ".babelrc",
    ".nvmrc", ".ruby-version", ".python-version", ".node-version",
    ".tool-versions", ".mjs", ".cjs", ".mts", ".cts", ".pyi", ".pyx",
    ".ipynb",
}

TEXT_NAMES = {
    "readme", "license", "licence", "changelog", "authors", "contributors",
    "copying", "dockerfile", "containerfile", "makefile", "rakefile",
    "gemfile", "procfile", "brewfile", "vagrantfile", "justfile", "taskfile",
}


def is_text_file(path: Path) -> bool:
    """Check if a file is likely a text file."""
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True

    if path.name.lower() in TEXT_NAMES:
        return True

    try:
        with open(path, "rb") as f:
            chunk = f.read(8192)
            if b"\x00" in chunk:
                return False
            try:
                chunk.decode("utf-8")
                return True
            except UnicodeDecodeError:
                return False
    except Exception:
        return False


def scan_directory(
    root: Path,
    encoding: tiktoken.Encoding,
    max_file_tokens: int = 50000,
) -> dict:
    """Scan a directory and return file information with token counts."""
    root = root.resolve()
    gitignore_patterns = parse_gitignore(root)

    files = []
    directories = []
    skipped = []
    total_tokens = 0
    lang_tokens: dict[str, int] = {}
    lang_files: dict[str, int] = {}

    def walk(current: Path, depth: int = 0):
        nonlocal total_tokens

        if should_ignore(current, root, gitignore_patterns):
            return

        if current.is_dir():
            rel_path = str(current.relative_to(root))
            if rel_path != ".":
                directories.append(rel_path)

            try:
                entries = sorted(current.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
                for entry in entries:
                    walk(entry, depth + 1)
            except PermissionError:
                skipped.append({"path": str(current.relative_to(root)), "reason": "permission_denied"})

        elif current.is_file():
            rel_path = str(current.relative_to(root))
            size_bytes = current.stat().st_size

            if size_bytes > 1_000_000:
                skipped.append({"path": rel_path, "reason": "too_large", "size_bytes": size_bytes})
                return

            if not is_text_file(current):
                skipped.append({"path": rel_path, "reason": "binary"})
                return

            try:
                # Special handling for Jupyter notebooks
                if current.suffix.lower() == ".ipynb":
                    content = read_notebook(current)
                    if content is None:
                        skipped.append({"path": rel_path, "reason": "notebook_parse_error"})
                        return
                else:
                    with open(current, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                tokens = count_tokens(content, encoding)

                if tokens > max_file_tokens:
                    skipped.append({"path": rel_path, "reason": "too_many_tokens", "tokens": tokens})
                    return

                files.append({
                    "path": rel_path,
                    "tokens": tokens,
                    "size_bytes": size_bytes,
                })
                total_tokens += tokens

                # Track language distribution
                lang = EXT_TO_LANG.get(current.suffix.lower())
                if lang:
                    lang_tokens[lang] = lang_tokens.get(lang, 0) + tokens
                    lang_files[lang] = lang_files.get(lang, 0) + 1

            except Exception as e:
                skipped.append({"path": rel_path, "reason": f"read_error: {str(e)}"})

    walk(root)

    return {
        "root": str(root),
        "files": files,
        "directories": directories,
        "total_tokens": total_tokens,
        "total_files": len(files),
        "skipped": skipped,
        "language_distribution": {
            "by_tokens": dict(sorted(lang_tokens.items(), key=lambda x: x[1], reverse=True)),
            "by_files": dict(sorted(lang_files.items(), key=lambda x: x[1], reverse=True)),
        },
    }


def read_json_file(path: Path) -> dict | None:
    """Safely read and parse a JSON file."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return json.loads(f.read())
    except Exception:
        return None


def read_toml_like(path: Path) -> dict[str, str]:
    """Minimal TOML reader for key = \"value\" pairs (no nested tables)."""
    result: dict[str, str] = {}
    current_table = ""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                table_match = re.match(r"^\[([^\]]+)\]", line)
                if table_match:
                    current_table = table_match.group(1) + "."
                    continue
                kv_match = re.match(r'^(\S+)\s*=\s*"([^"]*)"', line)
                if kv_match:
                    result[current_table + kv_match.group(1)] = kv_match.group(2)
    except Exception:
        pass
    return result


def detect_tech_stack(root: Path) -> dict:
    """Detect technology stack from project files."""
    frameworks: list[str] = []
    package_manager = None
    languages_detected: list[str] = []

    # --- Node.js / JavaScript / TypeScript ---
    pkg_json_path = root / "package.json"
    if pkg_json_path.exists():
        languages_detected.append("javascript")
        pkg = read_json_file(pkg_json_path)
        if pkg:
            all_deps = {}
            all_deps.update(pkg.get("dependencies", {}))
            all_deps.update(pkg.get("devDependencies", {}))

            framework_signals = {
                "next": "next.js", "nuxt": "nuxt", "remix": "remix",
                "@angular/core": "angular", "react": "react", "vue": "vue",
                "svelte": "svelte", "@sveltejs/kit": "sveltekit",
                "express": "express", "fastify": "fastify", "koa": "koa",
                "hono": "hono", "nestjs": "nestjs", "@nestjs/core": "nestjs",
                "prisma": "prisma", "@prisma/client": "prisma",
                "drizzle-orm": "drizzle", "typeorm": "typeorm",
                "sequelize": "sequelize",
                "electron": "electron", "tauri": "tauri",
                "@vercel/ai": "vercel-ai-sdk", "ai": "vercel-ai-sdk",
                "@langchain/core": "langchain",
                "llamaindex": "llamaindex",
                "@modelcontextprotocol/sdk": "mcp-sdk",
            }
            for dep, fw in framework_signals.items():
                if dep in all_deps and fw not in frameworks:
                    frameworks.append(fw)

        # Detect package manager
        if (root / "bun.lockb").exists() or (root / "bun.lock").exists():
            package_manager = "bun"
        elif (root / "pnpm-lock.yaml").exists():
            package_manager = "pnpm"
        elif (root / "yarn.lock").exists():
            package_manager = "yarn"
        elif (root / "package-lock.json").exists():
            package_manager = "npm"

    if (root / "tsconfig.json").exists():
        if "typescript" not in languages_detected:
            languages_detected.append("typescript")

    # --- Python ---
    pyproject = root / "pyproject.toml"
    setup_py = root / "setup.py"
    if pyproject.exists() or setup_py.exists():
        languages_detected.append("python")
        if pyproject.exists():
            toml_data = read_toml_like(pyproject)
            # Check build system
            build_backend = toml_data.get("build-system.build-backend", "")
            if "hatchling" in build_backend:
                frameworks.append("hatch")
            elif "setuptools" in build_backend:
                frameworks.append("setuptools")
            elif "poetry" in build_backend:
                frameworks.append("poetry")

            # Read raw for dependency detection
            try:
                content = pyproject.read_text(encoding="utf-8", errors="ignore")
                py_fw_signals = {
                    "fastapi": "fastapi", "django": "django", "flask": "flask",
                    "starlette": "starlette", "litestar": "litestar",
                    "sqlalchemy": "sqlalchemy", "tortoise-orm": "tortoise-orm",
                    "langchain": "langchain", "llama-index": "llamaindex",
                    "openai": "openai-sdk", "anthropic": "anthropic-sdk",
                    "mcp": "mcp-sdk",
                }
                for dep, fw in py_fw_signals.items():
                    if dep in content and fw not in frameworks:
                        frameworks.append(fw)
            except Exception:
                pass

        package_manager = package_manager or "uv" if (root / "uv.lock").exists() else package_manager or "pip"

    # --- Rust ---
    cargo_toml = root / "Cargo.toml"
    if cargo_toml.exists():
        languages_detected.append("rust")
        try:
            content = cargo_toml.read_text(encoding="utf-8", errors="ignore")
            rust_fw = {
                "actix-web": "actix-web", "axum": "axum", "rocket": "rocket",
                "warp": "warp", "tokio": "tokio", "tauri": "tauri",
            }
            for dep, fw in rust_fw.items():
                if dep in content and fw not in frameworks:
                    frameworks.append(fw)
        except Exception:
            pass

    # --- Go ---
    go_mod = root / "go.mod"
    if go_mod.exists():
        languages_detected.append("go")
        try:
            content = go_mod.read_text(encoding="utf-8", errors="ignore")
            go_fw = {
                "gin-gonic/gin": "gin", "labstack/echo": "echo",
                "gofiber/fiber": "fiber", "gorilla/mux": "gorilla-mux",
            }
            for dep, fw in go_fw.items():
                if dep in content and fw not in frameworks:
                    frameworks.append(fw)
        except Exception:
            pass

    # --- Java ---
    pom_xml = root / "pom.xml"
    build_gradle = root / "build.gradle"
    build_gradle_kts = root / "build.gradle.kts"
    if pom_xml.exists():
        languages_detected.append("java")
        package_manager = package_manager or "maven"
        try:
            content = pom_xml.read_text(encoding="utf-8", errors="ignore")
            if "spring-boot" in content:
                frameworks.append("spring-boot")
            if "quarkus" in content:
                frameworks.append("quarkus")
        except Exception:
            pass
    elif build_gradle.exists() or build_gradle_kts.exists():
        languages_detected.append("java")
        package_manager = package_manager or "gradle"
        gradle_path = build_gradle if build_gradle.exists() else build_gradle_kts
        try:
            content = gradle_path.read_text(encoding="utf-8", errors="ignore")
            if "spring-boot" in content or "org.springframework.boot" in content:
                frameworks.append("spring-boot")
            if "quarkus" in content or "io.quarkus" in content:
                frameworks.append("quarkus")
        except Exception:
            pass

    # --- C# / .NET ---
    sln_files = list(root.glob("*.sln"))
    csproj_files = list(root.glob("*.csproj"))
    if sln_files or csproj_files:
        languages_detected.append("csharp")
        package_manager = package_manager or "dotnet"
        for csproj in csproj_files:
            try:
                content = csproj.read_text(encoding="utf-8", errors="ignore")
                if "Microsoft.AspNetCore" in content or "Microsoft.NET.Sdk.Web" in content:
                    if "aspnet-core" not in frameworks:
                        frameworks.append("aspnet-core")
                if "Microsoft.AspNetCore.Components" in content or "Blazor" in content:
                    if "blazor" not in frameworks:
                        frameworks.append("blazor")
            except Exception:
                pass

    # --- PHP ---
    composer_json = root / "composer.json"
    if composer_json.exists():
        languages_detected.append("php")
        package_manager = package_manager or "composer"
        pkg = read_json_file(composer_json)
        if pkg:
            all_php_deps = {}
            all_php_deps.update(pkg.get("require", {}))
            all_php_deps.update(pkg.get("require-dev", {}))
            php_fw = {
                "laravel/framework": "laravel",
                "symfony/framework-bundle": "symfony",
                "symfony/symfony": "symfony",
            }
            for dep, fw in php_fw.items():
                if dep in all_php_deps and fw not in frameworks:
                    frameworks.append(fw)

    return {
        "languages_detected": languages_detected,
        "frameworks": frameworks,
        "package_manager": package_manager,
    }


def extract_package_metadata(root: Path) -> dict:
    """Extract package metadata from manifest files."""
    meta: dict[str, str | int | None] = {
        "name": None,
        "version": None,
        "license": None,
        "description": None,
        "dependencies_count": 0,
    }

    # Try package.json
    pkg_json = root / "package.json"
    if pkg_json.exists():
        pkg = read_json_file(pkg_json)
        if pkg:
            meta["name"] = pkg.get("name")
            meta["version"] = pkg.get("version")
            meta["license"] = pkg.get("license")
            meta["description"] = pkg.get("description")
            deps = len(pkg.get("dependencies", {}))
            dev_deps = len(pkg.get("devDependencies", {}))
            meta["dependencies_count"] = deps + dev_deps
            return meta

    # Try pyproject.toml
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        toml_data = read_toml_like(pyproject)
        meta["name"] = toml_data.get("project.name") or toml_data.get("tool.poetry.name")
        meta["version"] = toml_data.get("project.version") or toml_data.get("tool.poetry.version")
        meta["license"] = toml_data.get("project.license") or toml_data.get("tool.poetry.license")
        meta["description"] = toml_data.get("project.description") or toml_data.get("tool.poetry.description")
        # Count deps from raw content
        try:
            content = pyproject.read_text(encoding="utf-8", errors="ignore")
            in_deps = False
            count = 0
            for line in content.splitlines():
                stripped = line.strip()
                if re.match(r"^\[(project\.)?dependencies\]", stripped) or re.match(r"^\[tool\.poetry\.dependencies\]", stripped):
                    in_deps = True
                    continue
                if in_deps:
                    if stripped.startswith("["):
                        in_deps = False
                        continue
                    if stripped and not stripped.startswith("#"):
                        count += 1
            meta["dependencies_count"] = count
        except Exception:
            pass
        return meta

    # Try Cargo.toml
    cargo = root / "Cargo.toml"
    if cargo.exists():
        toml_data = read_toml_like(cargo)
        meta["name"] = toml_data.get("package.name")
        meta["version"] = toml_data.get("package.version")
        meta["license"] = toml_data.get("package.license")
        meta["description"] = toml_data.get("package.description")
        try:
            content = cargo.read_text(encoding="utf-8", errors="ignore")
            in_deps = False
            count = 0
            for line in content.splitlines():
                stripped = line.strip()
                if stripped == "[dependencies]" or stripped == "[dev-dependencies]":
                    in_deps = True
                    continue
                if in_deps:
                    if stripped.startswith("["):
                        in_deps = False
                        continue
                    if stripped and not stripped.startswith("#") and "=" in stripped:
                        count += 1
            meta["dependencies_count"] = count
        except Exception:
            pass
        return meta

    # Try go.mod
    go_mod = root / "go.mod"
    if go_mod.exists():
        try:
            content = go_mod.read_text(encoding="utf-8", errors="ignore")
            mod_match = re.search(r"^module\s+(\S+)", content, re.MULTILINE)
            if mod_match:
                meta["name"] = mod_match.group(1)
            go_match = re.search(r"^go\s+(\S+)", content, re.MULTILINE)
            if go_match:
                meta["version"] = go_match.group(1)
            # Count require statements
            requires = re.findall(r"^\s+\S+\s+v[\d.]+", content, re.MULTILINE)
            meta["dependencies_count"] = len(requires)
        except Exception:
            pass
        return meta

    # Fallback: use directory name
    meta["name"] = root.name
    return meta


def extract_all_dependencies(root: Path) -> set[str]:
    """Extract normalized dependency names from all manifest files."""
    deps: set[str] = set()

    # package.json
    pkg_json = root / "package.json"
    if pkg_json.exists():
        pkg = read_json_file(pkg_json)
        if pkg:
            for section in ("dependencies", "devDependencies"):
                deps.update(k.lower() for k in pkg.get(section, {}).keys())

    # pyproject.toml — PEP 621 array + poetry table
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8", errors="ignore")
            in_deps = False
            for line in content.splitlines():
                stripped = line.strip()
                if re.match(r"^\[(project\.)?dependencies\]", stripped) or re.match(
                    r"^\[tool\.poetry\.dependencies\]", stripped
                ):
                    in_deps = True
                    continue
                if in_deps:
                    if stripped.startswith("["):
                        in_deps = False
                        continue
                    if stripped and not stripped.startswith("#"):
                        # PEP 621 list item: "  requests>=2.0"
                        name_match = re.match(r'^["\']?([a-zA-Z0-9_.-]+)', stripped)
                        if name_match:
                            deps.add(name_match.group(1).lower())
        except Exception:
            pass

    # Cargo.toml
    cargo = root / "Cargo.toml"
    if cargo.exists():
        try:
            content = cargo.read_text(encoding="utf-8", errors="ignore")
            in_deps = False
            for line in content.splitlines():
                stripped = line.strip()
                if stripped in ("[dependencies]", "[dev-dependencies]"):
                    in_deps = True
                    continue
                if in_deps:
                    if stripped.startswith("["):
                        in_deps = False
                        continue
                    if stripped and not stripped.startswith("#") and "=" in stripped:
                        name = stripped.split("=")[0].strip().lower()
                        deps.add(name)
        except Exception:
            pass

    # go.mod
    go_mod = root / "go.mod"
    if go_mod.exists():
        try:
            content = go_mod.read_text(encoding="utf-8", errors="ignore")
            for m in re.finditer(r"^\s+(\S+)\s+v[\d.]+", content, re.MULTILINE):
                # Use last path segment as dep name
                parts = m.group(1).split("/")
                deps.add(parts[-1].lower())
        except Exception:
            pass

    # pom.xml (Java Maven)
    pom_xml = root / "pom.xml"
    if pom_xml.exists():
        try:
            content = pom_xml.read_text(encoding="utf-8", errors="ignore")
            for m in re.finditer(r"<artifactId>([^<]+)</artifactId>", content):
                deps.add(m.group(1).lower())
        except Exception:
            pass

    # build.gradle / build.gradle.kts (Java Gradle)
    for gradle_name in ("build.gradle", "build.gradle.kts"):
        gradle_path = root / gradle_name
        if gradle_path.exists():
            try:
                content = gradle_path.read_text(encoding="utf-8", errors="ignore")
                for m in re.finditer(r"""['"]([\w.-]+:[\w.-]+):[\w.-]+['"]""", content):
                    parts = m.group(1).split(":")
                    deps.add(parts[-1].lower())
            except Exception:
                pass

    # composer.json (PHP)
    composer_json = root / "composer.json"
    if composer_json.exists():
        pkg = read_json_file(composer_json)
        if pkg:
            for section in ("require", "require-dev"):
                for k in pkg.get(section, {}).keys():
                    # Skip php itself and extensions
                    if k != "php" and not k.startswith("ext-"):
                        parts = k.split("/")
                        deps.add(parts[-1].lower())

    # *.csproj (C# .NET)
    for csproj in root.glob("*.csproj"):
        try:
            content = csproj.read_text(encoding="utf-8", errors="ignore")
            for m in re.finditer(r'<PackageReference\s+Include="([^"]+)"', content):
                deps.add(m.group(1).lower())
        except Exception:
            pass

    return deps


def detect_conditional_sections(root: Path, dependency_names: set[str]) -> list[str]:
    """Detect which conditional sections to include based on dependencies and file presence."""
    sections: list[str] = []

    # 4.1 Storage Layer
    storage_deps = {
        "prisma", "@prisma/client", "sequelize", "typeorm", "drizzle-orm", "drizzle-kit",
        "knex", "pg", "postgres", "mysql2", "mariadb", "better-sqlite3",
        "sqlalchemy", "alembic", "django", "tortoise-orm", "peewee",
        "diesel", "sqlx", "sea-orm", "rusqlite",
        "gorm", "mongoose", "mongodb", "redis", "ioredis", "aioredis",
        "dynamodb", "firestore", "firebase-admin", "cassandra-driver", "couchbase",
    }
    storage_dirs = ["migrations", "prisma", "alembic", "db/migrate", "src/database", "drizzle"]
    if dependency_names & storage_deps or any((root / d).exists() for d in storage_dirs):
        sections.append("Storage")

    # 4.2 Embedding Pipeline (requires both embedding model + vector store)
    embedding_deps = {
        "openai", "sentence-transformers", "cohere",
        "tiktoken", "langchain", "@langchain/core",
    }
    vector_deps = {
        "pinecone", "chromadb", "qdrant-client", "weaviate-client",
        "pymilvus", "faiss-cpu", "faiss-gpu", "pgvector", "lancedb",
    }
    embedding_dirs = ["embeddings", "vectorstore", "vector_store"]
    has_embedding = bool(dependency_names & embedding_deps)
    has_vector = bool(dependency_names & vector_deps) or any((root / d).exists() for d in embedding_dirs)
    if has_embedding and has_vector:
        sections.append("Embedding")

    # 4.3 Infrastructure Layer
    infra_files = [
        "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
        "compose.yml", "compose.yaml", "vercel.json", "netlify.toml",
        "fly.toml", "render.yaml", "railway.json", "serverless.yml", "serverless.ts",
        "cdk.json", "Pulumi.yaml",
    ]
    infra_dirs = ["k8s", "kubernetes", ".k8s", "terraform", "CDK", "pulumi"]
    if any((root / f).exists() for f in infra_files) or any((root / d).is_dir() for d in infra_dirs):
        sections.append("Infrastructure")
    else:
        # Check for *.tf files
        if list(root.glob("*.tf")):
            sections.append("Infrastructure")

    # 4.4 Knowledge Graph
    graph_deps = {
        "neo4j", "neo4j-driver", "dgraph", "arangodb",
        "rdflib", "sparqlwrapper", "gremlin", "tinkerpop",
    }
    graph_dirs = ["graph", "ontology"]
    if dependency_names & graph_deps or any((root / d).is_dir() for d in graph_dirs):
        sections.append("Knowledge Graph")

    # 4.5 Scalability
    scale_deps = {
        "bullmq", "bull", "celery", "amqplib", "amqp",
        "kafkajs", "confluent-kafka", "nats",
        "rq",
    }
    scale_dirs = ["workers", "queues", "jobs", "tasks"]
    if dependency_names & scale_deps or any((root / d).is_dir() for d in scale_dirs):
        sections.append("Scalability")

    # 4.6 Concurrency & Multi-Agent
    concurrency_deps = {
        "aiohttp", "httpx",
        "crewai", "autogen", "langgraph",
    }
    concurrency_dirs = ["agents", "agent", "crew", "workflows", "orchestrator"]
    if dependency_names & concurrency_deps or any((root / d).is_dir() for d in concurrency_dirs):
        sections.append("Concurrency")

    return sections


def detect_workspaces(root: Path) -> list[dict]:
    """Detect monorepo workspace packages."""
    workspaces: list[dict] = []

    # Node.js workspaces (package.json)
    pkg_json = root / "package.json"
    if pkg_json.exists():
        pkg = read_json_file(pkg_json)
        if pkg and "workspaces" in pkg:
            ws = pkg["workspaces"]
            # Can be list of globs or object with packages key
            patterns = ws if isinstance(ws, list) else ws.get("packages", [])
            import glob as globmod
            for pattern in patterns:
                for match in sorted(globmod.glob(str(root / pattern))):
                    match_path = Path(match)
                    ws_pkg_json = match_path / "package.json"
                    if ws_pkg_json.exists():
                        ws_pkg = read_json_file(ws_pkg_json)
                        workspaces.append({
                            "name": ws_pkg.get("name", match_path.name) if ws_pkg else match_path.name,
                            "path": str(match_path.relative_to(root)),
                            "package_manager": "npm",
                        })

    # pnpm-workspace.yaml
    pnpm_ws = root / "pnpm-workspace.yaml"
    if pnpm_ws.exists() and not workspaces:
        try:
            content = pnpm_ws.read_text(encoding="utf-8", errors="ignore")
            import glob as globmod
            for line in content.splitlines():
                line = line.strip().lstrip("- ").strip("'\"")
                if line and not line.startswith("#") and not line.startswith("packages"):
                    for match in sorted(globmod.glob(str(root / line))):
                        match_path = Path(match)
                        if match_path.is_dir():
                            ws_pkg_json = match_path / "package.json"
                            ws_name = match_path.name
                            if ws_pkg_json.exists():
                                ws_pkg = read_json_file(ws_pkg_json)
                                ws_name = ws_pkg.get("name", ws_name) if ws_pkg else ws_name
                            workspaces.append({
                                "name": ws_name,
                                "path": str(match_path.relative_to(root)),
                                "package_manager": "pnpm",
                            })
        except Exception:
            pass

    # lerna.json
    lerna_json = root / "lerna.json"
    if lerna_json.exists() and not workspaces:
        lerna = read_json_file(lerna_json)
        if lerna:
            import glob as globmod
            for pattern in lerna.get("packages", ["packages/*"]):
                for match in sorted(globmod.glob(str(root / pattern))):
                    match_path = Path(match)
                    if match_path.is_dir():
                        workspaces.append({
                            "name": match_path.name,
                            "path": str(match_path.relative_to(root)),
                            "package_manager": "lerna",
                        })

    # Cargo workspace
    cargo = root / "Cargo.toml"
    if cargo.exists() and not workspaces:
        try:
            content = cargo.read_text(encoding="utf-8", errors="ignore")
            if "[workspace]" in content:
                in_members = False
                for line in content.splitlines():
                    stripped = line.strip()
                    if stripped == "members = [" or stripped.startswith("members"):
                        in_members = True
                        # Handle single-line: members = ["a", "b"]
                        bracket_match = re.search(r'members\s*=\s*\[([^\]]+)\]', stripped)
                        if bracket_match:
                            for m in re.finditer(r'"([^"]+)"', bracket_match.group(1)):
                                ws_path = root / m.group(1)
                                if ws_path.is_dir():
                                    workspaces.append({
                                        "name": ws_path.name,
                                        "path": m.group(1),
                                        "package_manager": "cargo",
                                    })
                            in_members = False
                        continue
                    if in_members:
                        if "]" in stripped:
                            in_members = False
                            continue
                        m = re.search(r'"([^"]+)"', stripped)
                        if m:
                            ws_path = root / m.group(1)
                            if ws_path.is_dir():
                                workspaces.append({
                                    "name": ws_path.name,
                                    "path": m.group(1),
                                    "package_manager": "cargo",
                                })
        except Exception:
            pass

    # Go workspace (go.work)
    go_work = root / "go.work"
    if go_work.exists() and not workspaces:
        try:
            content = go_work.read_text(encoding="utf-8", errors="ignore")
            for m in re.finditer(r"^\s+(\./?\S+)", content, re.MULTILINE):
                ws_path = root / m.group(1).lstrip("./")
                if ws_path.is_dir():
                    workspaces.append({
                        "name": ws_path.name,
                        "path": str(ws_path.relative_to(root)),
                        "package_manager": "go",
                    })
        except Exception:
            pass

    return workspaces


def read_notebook(path: Path) -> str | None:
    """Read a Jupyter notebook, returning only source cell content (no outputs)."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            nb = json.loads(f.read())
        cells = nb.get("cells", [])
        sources = []
        for cell in cells:
            cell_type = cell.get("cell_type", "")
            if cell_type in ("code", "markdown"):
                source = cell.get("source", [])
                if isinstance(source, list):
                    sources.append("".join(source))
                elif isinstance(source, str):
                    sources.append(source)
        return "\n\n".join(sources) if sources else ""
    except Exception:
        return None


def detect_entry_points(root: Path) -> list[dict]:
    """Detect project entry points (CLI, API, library)."""
    entries: list[dict] = []

    # Check package.json bin/main/exports
    pkg_json = root / "package.json"
    if pkg_json.exists():
        pkg = read_json_file(pkg_json)
        if pkg:
            if "bin" in pkg:
                bin_val = pkg["bin"]
                if isinstance(bin_val, str):
                    entries.append({"type": "cli", "path": bin_val})
                elif isinstance(bin_val, dict):
                    for name, path in bin_val.items():
                        entries.append({"type": "cli", "path": path, "name": name})

            if "main" in pkg:
                entries.append({"type": "library", "path": pkg["main"]})
            elif "exports" in pkg:
                exp = pkg["exports"]
                if isinstance(exp, str):
                    entries.append({"type": "library", "path": exp})
                elif isinstance(exp, dict) and "." in exp:
                    dot_exp = exp["."]
                    if isinstance(dot_exp, str):
                        entries.append({"type": "library", "path": dot_exp})

    # Check common entry point files
    api_candidates = [
        "src/server.ts", "src/server.js", "src/app.ts", "src/app.js",
        "server.ts", "server.js", "app.ts", "app.js",
        "src/main.ts", "src/main.js", "main.ts", "main.js",
        "src/index.ts", "src/index.js", "index.ts", "index.js",
        "app/main.py", "main.py", "app.py", "manage.py",
        "src/main.rs", "cmd/main.go", "main.go",
    ]

    for candidate in api_candidates:
        p = root / candidate
        if p.exists():
            # Determine type by peeking at content
            entry_type = "library"
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")[:2000]
                if any(kw in content for kw in ["listen(", "createServer", "app.run", "uvicorn", "serve("]):
                    entry_type = "api"
                elif any(kw in content for kw in ["argparse", "commander", "yargs", "clap", "cobra", "cli"]):
                    entry_type = "cli"
            except Exception:
                pass

            # Avoid duplicates
            if not any(e["path"] == candidate for e in entries):
                entries.append({"type": entry_type, "path": candidate})
            break  # Only take the first match

    return entries


def detect_project_features(root: Path) -> dict:
    """Detect project features like Docker, CI, tests."""
    has_dockerfile = (root / "Dockerfile").exists() or (root / "dockerfile").exists()
    has_docker_compose = (root / "docker-compose.yml").exists() or (root / "docker-compose.yaml").exists() or (root / "compose.yml").exists()

    # CI detection
    ci = None
    if (root / ".github" / "workflows").is_dir():
        ci = "github-actions"
    elif (root / ".gitlab-ci.yml").exists():
        ci = "gitlab-ci"
    elif (root / ".circleci").is_dir():
        ci = "circleci"
    elif (root / "Jenkinsfile").exists():
        ci = "jenkins"
    elif (root / ".travis.yml").exists():
        ci = "travis"
    elif (root / "bitbucket-pipelines.yml").exists():
        ci = "bitbucket-pipelines"

    # Test detection
    has_tests = False
    test_dirs = ["tests", "test", "__tests__", "spec", "specs", "e2e", "cypress", "playwright"]
    for d in test_dirs:
        if (root / d).is_dir():
            has_tests = True
            break

    if not has_tests:
        # Check for test config files
        test_configs = [
            "jest.config.js", "jest.config.ts", "vitest.config.ts", "vitest.config.js",
            "pytest.ini", "conftest.py", ".pytest.ini",
            "karma.conf.js", "cypress.config.js", "cypress.config.ts",
            "playwright.config.ts", "playwright.config.js",
        ]
        for tc in test_configs:
            if (root / tc).exists():
                has_tests = True
                break

    # Check for CODEBASE_MAP.md
    has_codebase_map = (root / "docs" / "CODEBASE_MAP.md").exists()

    return {
        "has_dockerfile": has_dockerfile,
        "has_docker_compose": has_docker_compose,
        "has_ci": ci,
        "has_tests": has_tests,
        "has_codebase_map": has_codebase_map,
    }


def format_tree(scan_result: dict, show_tokens: bool = True) -> str:
    """Format scan results as a tree structure."""
    lines = []
    root_name = Path(scan_result["root"]).name
    lines.append(f"{root_name}/")
    lines.append(f"Total: {scan_result['total_files']} files, {scan_result['total_tokens']:,} tokens")
    lines.append("")

    tree: dict = {}
    for f in scan_result["files"]:
        parts = Path(f["path"]).parts
        current = tree
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = f

    def print_tree(node: dict, prefix: str = ""):
        items = sorted(node.items(), key=lambda x: (not isinstance(x[1], dict) or "tokens" in x[1], x[0].lower()))

        for i, (name, value) in enumerate(items):
            is_last_item = i == len(items) - 1
            connector = "\u2514\u2500\u2500 " if is_last_item else "\u251c\u2500\u2500 "

            if isinstance(value, dict) and "tokens" not in value:
                lines.append(f"{prefix}{connector}{name}/")
                extension = "    " if is_last_item else "\u2502   "
                print_tree(value, prefix + extension)
            else:
                if show_tokens:
                    tokens = value.get("tokens", 0)
                    lines.append(f"{prefix}{connector}{name} ({tokens:,} tokens)")
                else:
                    lines.append(f"{prefix}{connector}{name}")

    print_tree(tree)
    return "\n".join(lines)


def format_summary(result: dict) -> str:
    """Format scan results as a concise summary for LLM consumption."""
    lines = []
    root_name = Path(result["root"]).name
    meta = result.get("package_metadata", {})
    tech = result.get("tech_stack", {})
    features = result.get("project_features", {})

    # Header
    lines.append(f"# {meta.get('name') or root_name}")
    lines.append(f"Total: {result['total_files']} files, {result['total_tokens']:,} tokens")
    lines.append("")

    # Package metadata
    lines.append("## Metadata")
    if meta.get("version"):
        lines.append(f"- Version: {meta['version']}")
    if meta.get("license"):
        lines.append(f"- License: {meta['license']}")
    if meta.get("description"):
        lines.append(f"- Description: {meta['description']}")
    lines.append(f"- Dependencies: {meta.get('dependencies_count', 0)}")
    lines.append("")

    # Tech stack
    lines.append("## Tech Stack")
    if tech.get("languages_detected"):
        lines.append(f"- Languages: {', '.join(tech['languages_detected'])}")
    if tech.get("frameworks"):
        lines.append(f"- Frameworks: {', '.join(tech['frameworks'])}")
    if tech.get("package_manager"):
        lines.append(f"- Package Manager: {tech['package_manager']}")
    lines.append("")

    # Language distribution (top 5)
    lang_dist = result.get("language_distribution", {}).get("by_tokens", {})
    if lang_dist:
        lines.append("## Language Distribution")
        total = sum(lang_dist.values()) or 1
        for i, (lang, tokens) in enumerate(lang_dist.items()):
            if i >= 5:
                break
            pct = tokens * 100 / total
            lines.append(f"- {lang}: {pct:.1f}% ({tokens:,} tokens)")
        lines.append("")

    # Entry points
    entries = result.get("entry_points", [])
    if entries:
        lines.append("## Entry Points")
        for e in entries:
            name = e.get("name", "")
            label = f" ({name})" if name else ""
            lines.append(f"- [{e['type']}] {e['path']}{label}")
        lines.append("")

    # Project features
    lines.append("## Features")
    if features.get("has_ci"):
        lines.append(f"- CI: {features['has_ci']}")
    lines.append(f"- Tests: {'Yes' if features.get('has_tests') else 'No'}")
    lines.append(f"- Docker: {'Yes' if features.get('has_dockerfile') else 'No'}")
    if features.get("has_docker_compose"):
        lines.append("- Docker Compose: Yes")
    if features.get("has_codebase_map"):
        lines.append("- Codebase Map: Yes")
    lines.append("")

    # Detected conditional sections
    detected = result.get("detected_sections", [])
    if detected:
        lines.append("## Detected Sections")
        for s in detected:
            lines.append(f"- {s}")
        lines.append("")

    # Workspaces
    workspaces = result.get("workspaces", [])
    if workspaces:
        lines.append("## Workspaces")
        for ws in workspaces:
            lines.append(f"- {ws['name']} ({ws['path']}) [{ws['package_manager']}]")
        lines.append("")

    # Top 20 largest files
    files_sorted = sorted(result["files"], key=lambda x: x["tokens"], reverse=True)
    lines.append("## Top 20 Files (by tokens)")
    for f in files_sorted[:20]:
        lines.append(f"  {f['tokens']:>8}  {f['path']}")
    lines.append("")

    # Directory structure (depth 3)
    lines.append("## Directory Structure (depth 3)")
    dir_tokens: dict[str, int] = {}
    for f in result["files"]:
        parts = Path(f["path"]).parts
        for depth in range(1, min(len(parts), 4)):
            dir_path = "/".join(parts[:depth])
            dir_tokens[dir_path] = dir_tokens.get(dir_path, 0) + f["tokens"]
    # Only show directories (not individual files at root)
    shown = set()
    for d in sorted(dir_tokens.keys()):
        depth = d.count("/")
        if depth <= 2 and d not in shown:
            indent = "  " * depth
            lines.append(f"{indent}{d}/ ({dir_tokens[d]:,} tokens)")
            shown.add(d)
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Scan a project for profiling: file tree, token counts, tech stack, metadata"
    )
    parser.add_argument(
        "path", nargs="?", default=".",
        help="Path to scan (default: current directory)",
    )
    parser.add_argument(
        "--format", choices=["summary", "json", "tree", "compact"],
        default="summary", help="Output format (default: summary)",
    )
    parser.add_argument(
        "--max-tokens", type=int, default=50000,
        help="Skip files with more than this many tokens (default: 50000)",
    )
    parser.add_argument(
        "--encoding", default="cl100k_base",
        help="Tiktoken encoding to use (default: cl100k_base)",
    )

    args = parser.parse_args()
    path = Path(args.path).resolve()

    if not path.exists():
        print(f"ERROR: Path does not exist: {path}", file=sys.stderr)
        sys.exit(1)

    if not path.is_dir():
        print(f"ERROR: Path is not a directory: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        encoding = tiktoken.get_encoding(args.encoding)
    except Exception as e:
        print(f"ERROR: Failed to load encoding '{args.encoding}': {e}", file=sys.stderr)
        sys.exit(1)

    # Core scan
    result = scan_directory(path, encoding, args.max_tokens)

    # Additional profiling data
    result["tech_stack"] = detect_tech_stack(path)
    result["package_metadata"] = extract_package_metadata(path)
    result["entry_points"] = detect_entry_points(path)
    result["project_features"] = detect_project_features(path)

    # New: dependency extraction, conditional sections, workspaces
    all_deps = extract_all_dependencies(path)
    result["detected_sections"] = detect_conditional_sections(path, all_deps)
    result["workspaces"] = detect_workspaces(path)

    if args.format == "summary":
        print(format_summary(result))
    elif args.format == "json":
        print(json.dumps(result, indent=2))
    elif args.format == "tree":
        print(format_tree(result, show_tokens=True))
    elif args.format == "compact":
        files_sorted = sorted(result["files"], key=lambda x: x["tokens"], reverse=True)
        print(f"# {result['root']}")
        print(f"# Total: {result['total_files']} files, {result['total_tokens']:,} tokens")
        print(f"# Tech: {', '.join(result['tech_stack']['frameworks']) or 'N/A'}")
        print()
        for f in files_sorted:
            print(f"{f['tokens']:>8} {f['path']}")


if __name__ == "__main__":
    main()
