# Subagent Prompt Templates

> Phase 2 專用。Direct mode (≤80k tokens) 不會用到這個檔案。

## Shared Rules (inject into every agent prompt)

```
- Every number must come from actual code (count imports, count methods)
- No subjective language (no "well-designed", "elegant", "robust", "clean", "優雅", "完美", "強大")
- Every claim needs a `file:SymbolName` reference (NOT line numbers — they break on next commit)
```

---

## Agent A: Core Abstractions + Design Decisions

```
Task prompt for Agent A — subagent_type: "general-purpose", model: "sonnet"

## Mission
Identify the most architecturally significant abstractions AND key design decisions in this codebase.

## Files to Read
{LIST_OF_ASSIGNED_FILES}
Also read: README.md, CHANGELOG.md (if they exist and not already assigned)

## Output Format

### Part 1: Core Abstractions
Report the TOP 10-15 most architecturally significant abstractions, ranked by fan-in (how many other files reference them). If the project has fewer than 15 meaningful abstractions, report all.

For EACH abstraction:

#### {Name}
- **Purpose**: {≤15 words}
- **Defined in**: `{file_path}:ClassName` or `{file_path}:function_name`
- **Type**: {class / interface / type / trait / struct / protocol}
- **Public methods/fields**: {exact_count}
- **Adapters/implementations**: {count} — {names with file paths}
- **Imported by**: {count} files
- **Key pattern**: {factory / singleton / strategy / observer / none}

### Part 2: Design Decisions
For EACH decision (identify 3-5):

#### {Decision Title}
- **Problem**: {what needed solving}
- **Choice made**: {what was chosen}
- **Evidence**: `{file_path}:ClassName` or `{file_path}:function_name` — {relevant code pattern}
- **Alternatives NOT chosen**: {what else could have been done}
- **Why not**: {concrete reason — performance / complexity / ecosystem / team preference}
- **Tradeoff**: {what is gained} vs. {what is lost}

### Part 3: Architecture Risks
For EACH risk (identify 2-4):
- **Risk**: {specific description}
- **Location**: `{file_path}:SymbolName`
- **Impact**: {what breaks if this goes wrong}
- **Mitigation**: {how to fix or reduce risk}

### Part 4: Recommendations
For EACH recommendation (identify 2-4):
- **Current state**: `{file_path}` — {what exists now}
- **Problem**: {specific issue — not "could be better"}
- **Fix**: {concrete action — not "consider refactoring"}
- **Effect**: {measurable outcome}

## Rules
{SHARED_RULES}
- Each decision must have a "why NOT the alternative" answer
- Report the TOTAL count of abstractions found
```

---

## Agent B: Architecture + Code Quality Patterns

```
Task prompt for Agent B — subagent_type: "general-purpose", model: "sonnet"

## Mission
Map the system topology, layer boundaries, data flow paths, AND code quality patterns.

## Files to Read
{LIST_OF_ASSIGNED_FILES}

## Output Format

### Part 1: Topology
- **Architecture style**: {monolith / microservices / serverless / library / CLI tool / plugin system}
- **Entry points**: {list with file paths}
- **Layer count**: {N}

### Part 2: Layers (table)
| Layer | Modules | Files | Responsibility |
|-------|---------|-------|---------------|

### Part 3: Data Flow Paths
For each major user-facing operation:
1. **{Operation name}**: {step1_module} → {step2_module} → ... → {result}
   - Evidence: `{file:SymbolName}` for each step

### Part 4: Mermaid Diagram Elements
Provide raw data for Mermaid diagrams:
- Nodes: {module_name} — {file_path}
- Edges: {from} → {to} — {relationship_type: imports/calls/extends}

### Part 5: Module Dependencies (structured)
For each module:
- **{module_name}** (`{path}`): imports [{dep1}, {dep2}, ...]

### Part 6: Boundary Violations
List any cases where a lower layer imports from a higher layer.

### Part 7: Code Quality Patterns
- **Error handling**: {strategy and consistency — e.g., "try/catch at controller layer, custom AppError class"}
- **Logging**: {framework and coverage — e.g., "winston, structured JSON, covers all API routes"}
- **Testing**: {framework, coverage level, patterns — e.g., "vitest, 47 test files, unit + integration"}
- **Type safety**: {strict / partial / none — e.g., "strict TypeScript with no `any` casts"}

## Rules
{SHARED_RULES}
- Focus on HOW data moves, not WHAT the code does
```

---

## Agent C: Usage + Deployment + Security

```
Task prompt for Agent C — subagent_type: "general-purpose", model: "sonnet"

## Mission
Document all consumption interfaces, deployment modes, security surface, and AI agent integration points.

## Files to Read
{LIST_OF_ASSIGNED_FILES}

## Output Format

### Part 1: Consumption Interfaces
For each interface found:
- **Type**: {Python SDK / TS SDK / REST API / MCP / CLI / Vercel AI SDK / Library import}
- **Entry point**: `{file_path}:ClassName` or `{file_path}:function_name`
- **Public surface**: {N} exported functions/classes/endpoints
- **Example usage**: {minimal code snippet from docs/examples or inferred from exports}

### Part 2: Configuration
| Source | Path | Key Settings |
|--------|------|-------------|

### Part 3: Deployment Modes
| Mode | Evidence | Prerequisites |
|------|----------|--------------|

### Part 4: AI Agent Integration
- **MCP tools**: {count and names, if any}
- **Function calling schemas**: {count, if any}
- **Tool definitions**: {count, if any}
- **SDK integration**: {Vercel AI SDK / LangChain / LlamaIndex / custom}

### Part 5: Security Surface
- **API key handling**: {how and where}
- **Auth mechanism**: {type and file}
- **CORS config**: {if applicable}
- **Data at rest**: {encrypted / plaintext / N/A}
- **PII handling**: {anonymized / logged / none detected}

### Part 6: Performance & Cost Indicators
| Metric | Value | Source |
|--------|-------|--------|
| {LLM calls per request} | {N} | `{file:SymbolName}` |
| {Cache strategy} | {type} | `{file:SymbolName}` |
| {Rate limiting} | {config} | `{file:SymbolName}` |

## Rules
{SHARED_RULES}
- Include BOTH documented and undocumented interfaces
```
