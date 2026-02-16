# Project Profile Output Template

> This template defines the section structure for the generated profile document.
> Sections marked [CONDITIONAL] are only included when Phase 3 detection triggers them.
> All numbers must come from actual code. No subjective language.
> Evidence uses `file:SymbolName` format (NOT line numbers — they break on next commit).

---

## Template

```markdown
---
profiled: {ISO_TIMESTAMP}
scanner_version: 2.0.0
total_files: {N}
total_tokens: {N}
---

# {PROJECT_NAME}

> {ONE_LINE_POSITIONING: what it is NOT → what it IS, in ≤30 words}

| Field | Value |
|-------|-------|
| **Language** | {primary_lang} ({N}% by tokens), {secondary_lang} ({N}%) |
| **Framework** | {frameworks, comma-separated} |
| **Package Manager** | {pkg_manager} |
| **Version** | {version} |
| **License** | {license} |
| **Dependencies** | {N} direct |
| **First Commit** | {date} |
| **Contributors** | {N} |
| **Releases** | {N} |
| **Maturity** | {experimental / growing / stable / mature} |
| **Stars / Forks** | {N} / {N} |
| **Monthly Downloads** | {N} |
| **CI** | {ci_system or "None detected"} |
| **Tests** | {Yes/No} |
| **Docker** | {Yes/No} |

---

## 2. Architecture

> {ONE_SENTENCE_SUMMARY: topology type + primary data flow direction}

### 2.1 System Topology

```mermaid
graph TB
    %% Generated from actual module dependencies
    {MERMAID_TOPOLOGY}
```

### 2.1b Module Dependencies (structured)

> Machine-parseable dependency list for LLM readers.

- **{module_name}** (`{path}`): imports [{dep1}, {dep2}, ...]

### 2.2 Layer Boundaries

| Layer | Modules | Responsibility |
|-------|---------|---------------|
| {layer_name} | {module_paths} | {one_line_purpose} |

### 2.3 Data Flow

```mermaid
sequenceDiagram
    %% Generated from actual call chains
    {MERMAID_SEQUENCE}
```

### 2.3b Data Flow (structured)

> Machine-parseable data flow for LLM readers.

1. **{Operation name}**: {step1_module} → {step2_module} → ... → {result}

---

## 3. Core Abstractions

> {N} core types/interfaces identified (top 10-15 by architectural significance). Each drives a distinct responsibility boundary.

### {AbstractionName}

| Field | Value |
|-------|-------|
| **Purpose** | {what_it_does, ≤15 words} |
| **Defined in** | `{file_path}:ClassName` or `{file_path}:function_name` |
| **Methods/Fields** | {N} public |
| **Adapters/Implementations** | {N} ({names, comma-separated}) |
| **Used by** | {N} files |

{REPEAT FOR EACH CORE ABSTRACTION — 10-15, ranked by architectural significance}

---

## 4. [CONDITIONAL SECTIONS]

{Include ONLY sections triggered by Phase 3 detection. Order:}

### 4.1 Storage Layer
{Only if DB driver in dependencies or migrations/ detected}

> {db_type}: {N} models, {N} migrations

| Component | Detail |
|-----------|--------|
| **Driver** | {driver_name} — `{import_path}` |
| **Models** | {N} ({file_paths}) |
| **Migrations** | {N} files in `{migrations_dir}` |
| **Connection** | {connection_pattern — pool/singleton/per-request} |

### 4.2 Embedding Pipeline
{Only if embedding model + vector store detected}

> {embedding_model} → {vector_store}

| Component | Detail |
|-----------|--------|
| **Embedding Model** | {model_name} — `{file_path}:ClassName` |
| **Vector Store** | {store_name} — `{file_path}:ClassName` |
| **Chunking** | {strategy} — chunk size: {N}, overlap: {N} |
| **Index** | {index_type} |

### 4.3 Infrastructure Layer
{Only if Dockerfile/docker-compose/k8s/terraform/CDK detected}

> {infra_type}: {N} services

| Component | Detail |
|-----------|--------|
| **Container** | {Dockerfile path, base image} |
| **Orchestration** | {compose/k8s/terraform — file path} |
| **Services** | {N} ({service_names}) |
| **Ports** | {exposed_ports} |

### 4.4 Knowledge Graph
{Only if neo4j/dgraph/rdf/sparql import detected}

| Component | Detail |
|-----------|--------|
| **Store** | {graph_db} — `{import_path}` |
| **Schema** | {N} node types, {N} edge types |
| **Query Pattern** | {cypher/sparql/gremlin} |

### 4.5 Scalability
{Only if queue/worker/sharding detected}

| Component | Detail |
|-----------|--------|
| **Queue** | {queue_system} — `{import_path}` |
| **Workers** | {N} worker types |
| **Sharding** | {strategy or "N/A"} |

### 4.6 Concurrency & Multi-Agent
{Only if asyncio.gather/tokio::spawn/threading/agent orchestration detected}

| Component | Detail |
|-----------|--------|
| **Pattern** | {async/threading/multiprocessing/agent-orchestration} |
| **Concurrency primitives** | {gather/spawn/pool/channel} — `{file_path}:SymbolName` |
| **Agent count** | {N} agent types (if applicable) |

---

## 5. Usage Guide

> {N} consumption interfaces identified.

### 5.1 Consumption Interfaces

| Interface | Entry Point | Example |
|-----------|------------|---------|
| {Python SDK / TS SDK / REST / MCP / CLI / Vercel AI SDK / Library} | `{entry_path}:ClassName` | {one_line_usage} |

### 5.2 Configuration

| Config Source | Path | Key Settings |
|--------------|------|-------------|
| {env/yaml/toml/json} | `{path}` | {key_names} |

### 5.3 Deployment Modes

| Mode | How | Prerequisites |
|------|-----|--------------|
| {local/docker/cloud/serverless} | {command_or_steps} | {deps} |

### 5.4 AI Agent Integration
{Only if MCP/tool-use/function-calling patterns detected}

| Pattern | Detail |
|---------|--------|
| **Protocol** | {MCP / OpenAI function calling / LangChain tool / custom} |
| **Tools exposed** | {N} ({tool_names}) |
| **Entry point** | `{file_path}` |

---

## 6. Performance & Cost

> Key performance characteristics and cost drivers.

| Metric | Value | Source |
|--------|-------|--------|
| {LLM calls per request} | {N} | `{file_path}:SymbolName` |
| {Embedding dimensions} | {N} | `{file_path}:SymbolName` |
| {Cache strategy} | {type} | `{file_path}:SymbolName` |
| {Rate limiting} | {config} | `{file_path}:SymbolName` |

---

## 7. Security & Privacy

| Aspect | Detail |
|--------|--------|
| **API Key Management** | {env var / vault / config file} — `{file_path}` |
| **Auth Pattern** | {JWT / session / API key / OAuth / none} |
| **Data at Rest** | {encrypted / plaintext / N/A} |
| **PII Handling** | {anonymized / logged / none detected} |
| **CORS** | {configured / open / N/A} |

---

## 8. Design Decisions

> {N} key architectural decisions identified. Each shaped the system's current form.

### 8.1 {DECISION_TITLE}

| Aspect | Detail |
|--------|--------|
| **Problem** | {what_needed_solving} |
| **Choice** | {what_was_chosen} |
| **Alternatives** | {what_was_NOT_chosen, and why} |
| **Tradeoffs** | {what_you_gain vs. what_you_lose} |
| **Evidence** | `{file_path}:ClassName` — {code_snippet_or_pattern} |

{REPEAT for 3-5 decisions}

---

## 8.5 Code Quality & Patterns

> Cross-cutting code quality observations from codebase analysis.

| Aspect | Detail |
|--------|--------|
| **Error Handling** | {strategy — e.g., "try/catch at controller layer, custom AppError class in `src/errors.ts:AppError`"} |
| **Logging** | {framework + coverage — e.g., "winston structured JSON, covers all API routes"} |
| **Testing** | {framework + coverage + patterns — e.g., "vitest, 47 test files, unit + integration, `tests/`"} |
| **Type Safety** | {level — e.g., "strict TypeScript, no `any` casts, `tsconfig.json` strict: true"} |

---

## 9. Recommendations

> {N} actionable improvements identified from code analysis.

### 9.1 {RECOMMENDATION_TITLE}

| Aspect | Detail |
|--------|--------|
| **Current State** | `{file_path}` — {what_exists_now} |
| **Problem** | {specific_issue} |
| **Suggested Fix** | {concrete_action} |
| **Expected Effect** | {measurable_outcome} |

{REPEAT — each must reference actual file paths}
```

---

## Section Inclusion Rules

| Section | Always Include | Condition |
|---------|---------------|-----------|
| 1. Project Identity | Yes | — |
| 2. Architecture | Yes | — |
| 3. Core Abstractions | Yes | — |
| 4.x Conditional | No | Phase 3 detection triggers |
| 5. Usage Guide | Yes | — |
| 6. Performance & Cost | Yes | May be minimal for non-AI projects |
| 7. Security & Privacy | Yes | May be minimal for libraries |
| 8. Design Decisions | Yes | Minimum 3 |
| 8.5 Code Quality & Patterns | Yes | — |
| 9. Recommendations | Yes | Minimum 2 |
