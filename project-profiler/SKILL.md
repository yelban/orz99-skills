---
name: project-profiler
version: 1.0.0
description: |
  Generate an LLM-optimized project profile for any git repository.
  Outputs docs/{project-name}.md covering architecture, core abstractions,
  usage guide, design decisions, and recommendations.
  Trigger: "/project-profiler", "profile this project", "為專案建側寫"
user_invocable: true
argument_hint: "[target directory, default .]"
allowed-tools: [Read, Write, Edit, Grep, Glob, Bash, Task, WebSearch, WebFetch]
---

# project-profiler

Generate an **LLM-optimized project profile** — a judgment-rich document that lets any future LLM answer within 60 seconds:

1. **What are the core abstractions?**
2. **Which modules to modify for feature X?**
3. **What is the biggest risk/debt?**
4. **When should / shouldn't you use this?**

This is NOT a codebase map (directory + module navigation) or a diff schematic. This is **architectural judgment**: design tradeoffs, usage patterns, and when NOT to use.

---

## Model Strategy

- **Opus**: Orchestrator — runs all 6 phases, writes the final profile. Does NOT read source code directly.
- **Sonnet**: Subagents — read source code files, analyze patterns, report structured findings.
- All subagents launch in a **single message** (parallel, never sequential).

---

## Phase 0: Preflight

### 0.1 Target & Project Name

Determine the target directory (use argument if provided, else `.`).

Extract project name from the first available source:
1. `package.json` → `name`
2. `pyproject.toml` → `[project] name`
3. `Cargo.toml` → `[package] name`
4. `go.mod` → module path (last segment)
5. Directory name as fallback

### 0.2 Run Scanner

```bash
uv run {SKILL_DIR}/scripts/scan-project.py {TARGET_DIR} --format json
```

Capture the full JSON output. This provides:
- File tree with token counts
- Language distribution (by tokens and by files)
- Tech stack (languages, frameworks, package manager)
- Package metadata (name, version, license, deps count)
- Entry points (CLI, API, library)
- Project features (dockerfile, CI, tests, codebase_map)

### 0.3 Git Metadata

Run these commands (use Bash tool):

```bash
# Recent commits
git -C {TARGET_DIR} log --oneline -20

# Contributors
git -C {TARGET_DIR} log --format="%aN" | sort -u | head -20

# Version tags
git -C {TARGET_DIR} tag --sort=-v:refname | head -5

# First commit date
git -C {TARGET_DIR} log --format="%aI" --reverse | head -1
```

### 0.4 Check Existing CODEBASE_MAP

If `docs/CODEBASE_MAP.md` exists, note its presence. The profile will reference it rather than duplicating directory structure.

### 0.5 Token Budget → Execution Mode

Based on `total_tokens` from scanner, choose execution mode:

| Total Tokens | Mode | Strategy |
|-------------|------|----------|
| **≤ 80k** | **Direct** | **Skip subagents. Opus reads all files directly and performs all analysis in a single context.** |
| 80k – 200k | 2 agents | Agent AB (Core + Architecture), Agent CD (Usage + Decisions) |
| 200k – 400k | 3 agents | Agent A (Core), Agent BC (Architecture + Usage), Agent D (Decisions) |
| > 400k | 4 agents | Agent A, Agent B, Agent C, Agent D — each ≤150k tokens |

**Why 80k threshold**: Opus has 200k context. At ≤80k source tokens, loading all files + scanner output + git metadata + writing the profile all fit comfortably. Subagent overhead (spawn + communication + wait) adds 2-3 minutes for zero benefit.

**Direct mode workflow**: Skip Phase 2 entirely. After Phase 0+1, proceed to Phase 3 (but read files inline instead of from subagent reports), then Phase 4, then Phase 5. Read files on-demand during synthesis — do NOT pre-read all files; read only what's needed for each section.

---

## Phase 1: Community & External Data

> Run in parallel with Phase 2 subagent launches (or with Phase 3 file reads in direct mode).

### 1.1 GitHub Stats

Parse owner/repo from `.git/config` remote origin URL:

```bash
git -C {TARGET_DIR} remote get-url origin
```

Extract `owner/repo` from the URL. Then:

```bash
gh api repos/{owner}/{repo} --jq '{stars: .stargazers_count, forks: .forks_count, open_issues: .open_issues_count}'
```

If `gh` is unavailable or not a GitHub repo → fill with `N/A`. Do not fail.

### 1.2 Package Downloads

**npm** (if `package.json` exists):
```
WebFetch https://api.npmjs.org/downloads/point/last-month/{package_name}
```

**PyPI** (if `pyproject.toml` exists):
```
WebFetch https://pypistats.org/api/packages/{package_name}/recent
```

If fetch fails → fill with `N/A`.

### 1.3 License

Read from (in order): LICENSE file → package metadata field → `N/A`.

### 1.4 Maturity Assessment

Calculate from:
- **Git history length**: first commit date → now
- **Release count**: number of version tags
- **Contributor count**: unique authors

| Criteria | Score |
|----------|-------|
| < 3 months, < 3 releases, 1-2 contributors | experimental |
| 3-12 months, 3-10 releases, 2-5 contributors | growing |
| 1-3 years, 10-50 releases, 5-20 contributors | stable |
| > 3 years, > 50 releases, > 20 contributors | mature |

Use the **lowest** matching tier (conservative estimate).

---

## Phase 2: Parallel Deep Exploration

> **Direct mode (≤80k tokens): SKIP this entire phase.** Proceed to Phase 3. Opus reads files directly during synthesis.

Launch Sonnet subagents using the `Task` tool. **All subagents must be launched in a single message.**

Assign files to each agent based on the token budget from Phase 0.5. Use the scanner output to determine which files go to which agent.

### File Assignment Strategy

1. Sort all files by path
2. Group by top-level directory
3. Assign groups to agents based on their responsibility:
   - Agent A gets: core source files (src/lib, core/, models/, types/)
   - Agent B gets: architecture files (routes/, middleware/, config/, entry points)
   - Agent C gets: integration files (API, CLI, SDK, examples/, docs/)
   - Agent D gets: cross-cutting files (README, CHANGELOG, tests/, .github/)
4. If files don't fit neatly, distribute remaining to agents under budget

### Agent A: Core Abstractions

```
Task prompt for Agent A — subagent_type: "general-purpose", model: "sonnet"

## Mission
Identify ALL core types, interfaces, classes, and abstractions in this codebase.

## Files to Read
{LIST_OF_ASSIGNED_FILES}

## Output Format
For EACH core abstraction found, report:

### {Name}
- **Purpose**: {≤15 words}
- **Defined in**: `{file_path}:{line_number}`
- **Type**: {class / interface / type / trait / struct / protocol}
- **Public methods/fields**: {exact_count}
- **Adapters/implementations**: {count} — {names with file paths}
- **Imported by**: {count} files
- **Key pattern**: {factory / singleton / strategy / observer / none}

## Rules
- Every number must come from actual code (count imports, count methods)
- No subjective language (no "well-designed", "elegant", "robust", "clean")
- Every claim needs a `file:line` reference
- Do NOT skip minor abstractions — report ALL types that serve as module boundaries
- Report the TOTAL count of abstractions found
```

### Agent B: Architecture & Data Flow

```
Task prompt for Agent B — subagent_type: "general-purpose", model: "sonnet"

## Mission
Map the system topology, layer boundaries, and data flow paths.

## Files to Read
{LIST_OF_ASSIGNED_FILES}

## Output Format

### Topology
- **Architecture style**: {monolith / microservices / serverless / library / CLI tool / plugin system}
- **Entry points**: {list with file paths}
- **Layer count**: {N}

### Layers (table)
| Layer | Modules | Files | Responsibility |
|-------|---------|-------|---------------|

### Data Flow Paths
For each major user-facing operation:
1. **{Operation name}**: {step1_module} → {step2_module} → ... → {result}
   - Evidence: `{file:line}` for each step

### Mermaid Diagram Elements
Provide raw data for Mermaid diagrams:
- Nodes: {module_name} — {file_path}
- Edges: {from} → {to} — {relationship_type: imports/calls/extends}

### Boundary Violations
List any cases where a lower layer imports from a higher layer.

## Rules
- Every number must come from actual code
- No subjective language
- Every claim needs a `file:line` reference
- Focus on HOW data moves, not WHAT the code does
```

### Agent C: Usage & Integration

```
Task prompt for Agent C — subagent_type: "general-purpose", model: "sonnet"

## Mission
Document all consumption interfaces, deployment modes, and AI agent integration points.

## Files to Read
{LIST_OF_ASSIGNED_FILES}

## Output Format

### Consumption Interfaces
For each interface found:
- **Type**: {Python SDK / TS SDK / REST API / MCP / CLI / Vercel AI SDK / Library import}
- **Entry point**: `{file_path}:{line}`
- **Public surface**: {N} exported functions/classes/endpoints
- **Example usage**: {minimal code snippet from docs/examples or inferred from exports}

### Configuration
| Source | Path | Key Settings |
|--------|------|-------------|

### Deployment Modes
| Mode | Evidence | Prerequisites |
|------|----------|--------------|

### AI Agent Integration
- **MCP tools**: {count and names, if any}
- **Function calling schemas**: {count, if any}
- **Tool definitions**: {count, if any}
- **SDK integration**: {Vercel AI SDK / LangChain / LlamaIndex / custom}

### Security Surface
- **API key handling**: {how and where}
- **Auth mechanism**: {type and file}
- **CORS config**: {if applicable}

## Rules
- Every number must come from actual code
- No subjective language
- Every claim needs a `file:line` reference
- Include BOTH documented and undocumented interfaces
```

### Agent D: Design Decisions & Quality

```
Task prompt for Agent D — subagent_type: "general-purpose", model: "sonnet"

## Mission
Identify 3-5 key architectural decisions and assess code quality patterns.

## Files to Read
{LIST_OF_ASSIGNED_FILES}
Also read: README.md, CHANGELOG.md (if they exist)

## Output Format

### Design Decisions
For EACH decision (identify 3-5):

#### {Decision Title}
- **Problem**: {what needed solving}
- **Choice made**: {what was chosen}
- **Evidence**: `{file_path}:{line}` — {relevant code pattern}
- **Alternatives NOT chosen**: {what else could have been done}
- **Why not**: {concrete reason — performance / complexity / ecosystem / team preference}
- **Tradeoff**: {what is gained} vs. {what is lost}

### Architecture Risks
For EACH risk (identify 2-4):
- **Risk**: {specific description}
- **Location**: `{file_path}:{line}`
- **Impact**: {what breaks if this goes wrong}
- **Mitigation**: {how to fix or reduce risk}

### Recommendations
For EACH recommendation (identify 2-4):
- **Current state**: `{file_path}` — {what exists now}
- **Problem**: {specific issue — not "could be better"}
- **Fix**: {concrete action — not "consider refactoring"}
- **Effect**: {measurable outcome}

### Patterns Observed
- **Error handling**: {strategy and consistency}
- **Logging**: {framework and coverage}
- **Testing**: {framework, coverage level, patterns}
- **Type safety**: {strict / partial / none}

## Rules
- Every number must come from actual code
- No subjective language
- Every claim needs a `file:line` reference
- Each decision must have a "why NOT the alternative" answer
- Risks must be specific, not generic ("no tests" is only valid if there are actually no tests)
```

---

## Phase 3: Conditional Section Detection

After subagents return (or immediately after Phase 1 in direct mode), detect which optional sections to include.

Read the detection rules from `references/section-detection-rules.md`.

For each conditional section (Storage, Embedding, Infrastructure, Knowledge Graph, Scalability, Concurrency):

1. **Grep** the codebase for the import patterns listed in the rules — **exclude `project-profiler/references/`** to avoid false positives from detection rules matching themselves
2. **Glob** for the file presence patterns
3. **Cross-reference** with subagent reports (skip in direct mode)

If **any** detection method triggers → mark section for inclusion.

Record results as a checklist:
```
- [x] Storage Layer — detected: prisma import in src/db.ts
- [ ] Embedding Pipeline — not detected
- [x] Infrastructure Layer — detected: Dockerfile present
- [ ] Knowledge Graph — not detected
- [ ] Scalability — not detected
- [x] Concurrency — detected: Promise.all in src/worker.ts
```

---

## Phase 4: Synthesis & Draft

### 4.1 Merge Reports

**Subagent mode**: Combine all subagent outputs into a working document.
**Direct mode**: Read key files on-demand as you write each section. Do NOT pre-read all files. For each section, read only the files relevant to that section's analysis.

Cross-validate:
- Core abstractions ↔ Architecture layers: each abstraction belongs to a layer
- Architecture data flow ↔ Usage interfaces: flows end at documented interfaces
- Design decisions ↔ Code evidence: decisions are backed by found patterns

### 4.2 Generate Mermaid Diagrams

Using Agent B's raw data (or direct file analysis in direct mode), create:

**Architecture Topology** (`graph TB`):
- Each node = actual module/directory
- Each edge = import/dependency relationship
- Label edges with relationship type
- Group nodes by layer using subgraph

**Data Flow** (`sequenceDiagram`):
- Each participant = actual module
- Each arrow = actual function call or event
- Cover the primary user-facing operation

### 4.3 Fill Output Template

Follow `references/output-template.md` exactly. Fill each section:

| Section | Primary Source | Secondary Source |
|---------|---------------|-----------------|
| 1. Project Identity | Scanner metadata + Phase 1 | Git metadata |
| 2. Architecture | Agent B | Agent A (abstractions per layer) |
| 3. Core Abstractions | Agent A | Agent B (layer context) |
| 4. Conditional | Phase 3 detection + relevant agents | — |
| 5. Usage Guide | Agent C | Scanner entry_points |
| 6. Performance & Cost | Agent C + Agent B | — |
| 7. Security & Privacy | Agent C | Agent D |
| 8. Design Decisions | Agent D | Agent B (architecture context) |
| 9. Recommendations | Agent D | Agents A/B/C (supporting evidence) |

### 4.4 Write Output

Write the profile to `docs/{project-name}.md` using the Write tool.

---

## Phase 5: Quality Gate

Read `references/quality-checklist.md` and verify the output.

### 5.1 Banned Language Scan

Search the written file for any word from the banned list:
```
well-designed, elegant, elegantly, robust, clean, impressive,
state-of-the-art, cutting-edge, best-in-class, beautifully,
carefully crafted, thoughtfully, well-thought-out, well-architected,
nicely, cleverly, sophisticated, powerful, seamless, seamlessly,
intuitive, intuitively
```

If found → replace with verifiable descriptions and re-write.

### 5.2 Number Audit

Scan for all numeric claims. Each must have a traceable source.
Remove or fix any "approximately", "around", "roughly", "several", "many", "numerous".

### 5.3 Structure Verification

- [ ] Every `##` section starts with `>` blockquote summary
- [ ] No directory tree duplicated from CODEBASE_MAP.md
- [ ] No file extension enumeration (use percentages)
- [ ] No generic concluding paragraph
- [ ] At least one Mermaid diagram in Architecture section
- [ ] All Mermaid nodes reference actual modules

### 5.4 Core Question Test

For each of the 4 core questions, locate the specific answer in the output:
1. Core abstractions → Section 3
2. Module to modify → Section 2 Layer Boundaries table
3. Biggest risk → Section 9 first recommendation
4. When to use/not use → Section 1 positioning line

### 5.5 Evidence Audit

- Section 3: every abstraction has `file:line`
- Section 8: every decision has `file:line` + alternative + tradeoff
- Section 9: every recommendation has `file_path` + specific problem + concrete fix

If any check fails → fix the issue in the file and re-verify.

---

## Output

After all phases complete, report to the user:

```
Profile generated: docs/{project-name}.md
- {total_files} files scanned ({total_tokens} tokens)
- {N} core abstractions identified
- {N} design decisions documented
- {N} recommendations
- Conditional sections: {list of included sections or "none"}
```
