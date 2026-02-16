# Conditional Section Detection Rules

> Phase 3 uses these rules to determine which optional sections to include.
> **Primary detection**: Scanner parses dependency manifests and checks file presence (automatic, in `detected_sections`).
> **Fallback**: Subagent reports may flag patterns not caught by the scanner (e.g., raw concurrency without library deps).
> A section triggers when **any** detection method returns positive.

---

## Detection Method

1. **Scanner primary path** (automatic): Read `detected_sections` from scanner output. The scanner checks:
   - Dependency names from `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`, `composer.json`, `*.csproj`
   - File/directory presence checks
2. **Subagent cross-reference**: Check if any subagent (A/B/C) reported related patterns not caught by the scanner
3. **Manual grep fallback** (only if subagent reports are ambiguous): Use the import grep patterns below as reference

**Inclusion decision**: If **any** method returns positive → include the section.
**False positive tolerance**: False positives are acceptable (section can be sparse). False negatives are not (missing a major subsystem is worse than including an empty one).

---

## 4.1 Storage Layer

**Trigger condition**: DB driver in dependencies OR migrations directory exists

### Dependency Name Patterns (scanner primary)
```
prisma, @prisma/client, sequelize, typeorm, drizzle-orm, drizzle-kit,
knex, pg, postgres, mysql2, mariadb, better-sqlite3,
sqlalchemy, alembic, django, tortoise-orm, peewee,
diesel, sqlx, sea-orm, rusqlite, gorm,
mongoose, mongodb, redis, ioredis, aioredis,
dynamodb, firestore, firebase-admin, cassandra-driver, couchbase
```

### File Presence
```
migrations/
prisma/schema.prisma
alembic/
db/migrate/
src/database/
drizzle/
```

### Import Grep Patterns (fallback reference)
```
prisma|@prisma/client
sequelize
typeorm
drizzle-orm
sqlalchemy|alembic
django\.db|django\.models
mongoose|mongodb|mongoclient
redis|ioredis|aioredis
```

### Subagent Signal
Agent A or B reports database connection setup or ORM model definitions.

---

## 4.2 Embedding Pipeline

**Trigger condition**: Embedding model dependency AND vector store dependency (both required)

### Dependency Name Patterns — Embedding Models (scanner primary)
```
openai, sentence-transformers, cohere, tiktoken,
langchain, @langchain/core
```

### Dependency Name Patterns — Vector Stores (scanner primary)
```
pinecone, chromadb, qdrant-client, weaviate-client,
pymilvus, faiss-cpu, faiss-gpu, pgvector, lancedb
```

### File Presence
```
embeddings/
vectorstore/
vector_store/
```

### Import Grep Patterns (fallback reference)
```
openai\.embeddings|OpenAIEmbeddings
sentence.transformers|SentenceTransformer
cohere\.embed|CohereEmbeddings
pinecone|PineconeClient
chromadb|Chroma
qdrant|QdrantClient
weaviate|WeaviateClient
faiss|FAISS
```

### Subagent Signal
Agent A or C reports embedding generation or vector similarity search in core abstractions or usage interfaces.

---

## 4.3 Infrastructure Layer

**Trigger condition**: Any infrastructure-as-code or containerization file detected

### File Presence (scanner primary)
```
Dockerfile
docker-compose.yml / docker-compose.yaml / compose.yml / compose.yaml
k8s/ / kubernetes/ / .k8s/
terraform/ / *.tf
cdk.json / CDK/ / pulumi/ / Pulumi.yaml
serverless.yml / serverless.ts
vercel.json / netlify.toml / fly.toml / render.yaml / railway.json
```

### Subagent Signal
Agent C reports deployment configuration or container orchestration.

---

## 4.4 Knowledge Graph

**Trigger condition**: Graph database driver in dependencies

### Dependency Name Patterns (scanner primary)
```
neo4j, neo4j-driver, dgraph, arangodb,
rdflib, sparqlwrapper, gremlin, tinkerpop
```

### File Presence
```
graph/
ontology/
*.rdf / *.ttl / *.owl
```

### Import Grep Patterns (fallback reference)
```
neo4j|Neo4jDriver|neo4j-driver
dgraph|DgraphClient
rdf|rdflib
sparql|SPARQLWrapper
gremlin|tinkerpop
```

### Subagent Signal
Agent A reports graph traversal patterns or node/edge type definitions.

---

## 4.5 Scalability

**Trigger condition**: Queue/worker system dependency detected

### Dependency Name Patterns (scanner primary)
```
bullmq, bull, celery, amqplib, amqp,
kafkajs, confluent-kafka, nats, rq
```

### File Presence
```
workers/
queues/
jobs/
tasks/
celeryconfig.py
```

### Import Grep Patterns (fallback reference)
```
bullmq|bull|BullModule
celery|Celery
rabbitmq|amqplib
kafka|KafkaJS
```

### Subagent Signal
Agent B reports message passing patterns, job queues, or horizontal scaling configuration.

---

## 4.6 Concurrency & Multi-Agent

**Trigger condition**: Concurrent execution dependency OR agent orchestration dependency detected

### Dependency Name Patterns (scanner primary)
```
aiohttp, httpx, crewai, autogen, langgraph
```

### File Presence
```
agents/
agent/
crew/
workflows/
orchestrator/
```

### Import Grep Patterns (fallback reference — for patterns without library deps)
```
# Python async
asyncio\.gather|asyncio\.create_task

# Rust async
tokio::spawn|tokio::select

# JavaScript/TypeScript concurrency
Promise\.all|Promise\.allSettled|Promise\.race

# Threading
threading\.Thread|ThreadPoolExecutor
multiprocessing\.Process|ProcessPoolExecutor

# Agent orchestration
CrewAI|crew|Agent\(.*role
AutoGen|autogen
LangGraph|StateGraph
```

### Subagent Signal
Agent A or B reports parallel execution patterns, agent definitions, or workflow orchestration in core abstractions or architecture.
