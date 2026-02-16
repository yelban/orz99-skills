# Quality Gate Checklist

> Phase 5 verification rules. The orchestrator scans its own output against each rule.
> Any violation → fix before writing final output.

---

## 1. Banned Subjective Language

Scan the entire output for these words/phrases. **None may appear:**

```
well-designed
elegant
elegantly
robust
clean
impressive
state-of-the-art
cutting-edge
best-in-class
beautifully
carefully crafted
thoughtfully
well-thought-out
well-architected
nicely
cleverly
sophisticated
powerful
seamless
seamlessly
intuitive
intuitively
```

**Replacement strategy**: Replace with verifiable descriptions.
- "robust error handling" → "error handling covers N cases (`file:line`)"
- "elegant abstraction" → "abstraction with N implementations (`file:line`)"
- "well-designed API" → "API exposes N endpoints, N with type validation"

---

## 2. Number Verification

Every number in the output must:

- Be formatted as `(N files)`, `(N adapters)`, `(N methods)`, `(N lines)`, etc.
- Have a traceable source (scanner output, grep count, or `file:line` reference)
- NOT be rounded estimates — use exact counts

**Check**: Search for patterns like `\d+\s+(files?|adapters?|methods?|types?|modules?|implementations?)`. Each occurrence must have a source.

**Forbidden patterns**:
- "approximately N"
- "around N"
- "roughly N"
- "several" (replace with exact count)
- "many" (replace with exact count)
- "a few" (replace with exact count)
- "numerous" (replace with exact count)

---

## 3. Structure Checks

### 3.1 Section Summaries
Every section (## heading) must start with a `>` blockquote summary line (≤30 words).

### 3.2 No Directory Tree Duplication
If the project has `docs/CODEBASE_MAP.md`, the profile must NOT reproduce the full directory tree. Instead, reference it:
```markdown
> See [CODEBASE_MAP.md](docs/CODEBASE_MAP.md) for complete directory structure.
```

### 3.3 No Extension Enumeration
Do NOT list all file extensions found. Use language distribution percentages from the scanner instead:
- BAD: "The project contains .ts, .tsx, .js, .jsx, .json, .md, .yml files"
- GOOD: "TypeScript (72% by tokens), JavaScript (15%), Markdown (8%)"

### 3.4 No Generic Conclusions
The final section must NOT end with generic praise or vague statements like:
- "This is a well-structured project..."
- "The codebase follows good practices..."
- "Overall, the architecture is solid..."

Instead, end with a specific, actionable recommendation with file path reference.

### 3.5 Mermaid Diagrams
- Architecture section MUST contain at least one Mermaid diagram
- Each diagram node must correspond to an actual module/file
- No placeholder nodes like "Other" or "Misc"

---

## 4. LLM Readability — 4 Core Questions

The profile must directly answer these questions. Each must be answerable by reading a specific section:

| # | Question | Must Be Answered In |
|---|----------|-------------------|
| 1 | What are the core abstractions? | Section 3 (Core Abstractions) |
| 2 | Which modules to modify for feature X? | Section 2 (Architecture — Layer Boundaries table) |
| 3 | What is the biggest risk/debt? | Section 9 (Recommendations — first item) |
| 4 | When should/shouldn't you use this? | Section 1 (Project Identity — positioning line) |

**Check**: For each question, identify the exact section and verify it contains a concrete answer (not a vague one).

---

## 5. Evidence Requirements

### 5.1 Design Decisions (Section 8)
Each decision must have:
- `file:line` evidence pointing to actual code
- At least one alternative that was NOT chosen
- A concrete tradeoff (gain vs. loss)

### 5.2 Recommendations (Section 9)
Each recommendation must have:
- `file_path` pointing to actual current state
- A specific problem (not "could be improved")
- A concrete fix (not "consider refactoring")
- An expected measurable effect

### 5.3 Core Abstractions (Section 3)
Each abstraction must have:
- Exact file path with line number
- Exact method/field count (from code, not estimate)
- At least one adapter/implementation listed (or "0 — interface only")

---

## 6. Metadata Accuracy

- `profiled` timestamp must be current (ISO 8601)
- `total_files` and `total_tokens` must match scanner output exactly
- Language percentages must sum to ~100% (±2% for rounding)
- Dependencies count must match scanner's `dependencies_count`

---

## Verification Procedure

The orchestrator performs these checks in order:

1. **Grep own output** for banned words (Rule 1)
2. **Scan numbers** — verify each has a source (Rule 2)
3. **Check structure** — section summaries, no tree duplication, no extension lists, no generic endings (Rule 3)
4. **Answer test** — for each of the 4 core questions, locate the answer in the output (Rule 4)
5. **Evidence audit** — verify `file:line` references in Sections 3, 8, 9 (Rule 5)
6. **Metadata match** — compare frontmatter numbers with scanner output (Rule 6)

If any check fails → fix and re-verify before writing final file.
