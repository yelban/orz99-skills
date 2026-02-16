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


def main():
    parser = argparse.ArgumentParser(
        description="Scan a project for profiling: file tree, token counts, tech stack, metadata"
    )
    parser.add_argument(
        "path", nargs="?", default=".",
        help="Path to scan (default: current directory)",
    )
    parser.add_argument(
        "--format", choices=["json", "tree", "compact"],
        default="json", help="Output format (default: json)",
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

    if args.format == "json":
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
