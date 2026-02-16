# Conditional Section Detection Rules

> Phase 3 uses these rules to determine which optional sections to include.
> Each rule combines: import/dependency grep patterns + file presence checks + subagent report signals.
> A section triggers when **any** detection method returns positive.

---

## 4.1 Storage Layer

**Trigger condition**: DB driver import OR migrations directory exists

### Grep Patterns (imports/requires)

```
# SQL databases
prisma|@prisma/client
sequelize
typeorm
drizzle-orm|drizzle-kit
knex
pg|postgres|postgresql
mysql2?|mariadb
better-sqlite3|sql\.js
sqlalchemy|alembic
django\.db|django\.models
tortoise-orm|tortoise\.models
peewee
diesel|sqlx|sea-orm|rusqlite
gorm|ent\.

# NoSQL databases
mongoose|mongodb|mongoclient
redis|ioredis|aioredis
dynamodb|@aws-sdk/client-dynamodb
firestore|firebase-admin
cassandra-driver
couchbase
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

### Subagent Signal
Agent B reports database connection setup or ORM model definitions.

---

## 4.2 Embedding Pipeline

**Trigger condition**: Embedding model import AND vector store import (both required)

### Grep Patterns — Embedding Models

```
openai\.embeddings|OpenAIEmbeddings
sentence.transformers|SentenceTransformer
cohere\.embed|CohereEmbeddings
HuggingFaceEmbeddings|HuggingFaceBgeEmbeddings
GoogleGenerativeAIEmbeddings
embed_model|embedding_model|embeddings_model
tiktoken\.encoding_for_model
text-embedding-ada|text-embedding-3
```

### Grep Patterns — Vector Stores

```
pinecone|PineconeClient
chromadb|Chroma
qdrant|QdrantClient
weaviate|WeaviateClient
milvus|MilvusClient
faiss|FAISS
pgvector|PGVector
lance|lancedb
```

### File Presence

```
embeddings/
vectorstore/
vector_store/
index/
```

### Subagent Signal
Agent A or C reports embedding generation or vector similarity search in core abstractions or usage interfaces.

---

## 4.3 Infrastructure Layer

**Trigger condition**: Any infrastructure-as-code or containerization file detected

### File Presence

```
Dockerfile
docker-compose.yml
docker-compose.yaml
compose.yml
compose.yaml
k8s/
kubernetes/
.k8s/
terraform/
*.tf
cdk.json
CDK/
pulumi/
Pulumi.yaml
serverless.yml
serverless.ts
vercel.json
netlify.toml
fly.toml
render.yaml
railway.json
```

### Grep Patterns

```
FROM\s+\w+  # Dockerfile FROM instruction
apiVersion:\s*apps/v1  # k8s manifest
resource\s+"aws_|resource\s+"google_|resource\s+"azurerm_  # terraform
```

### Subagent Signal
Agent C reports deployment configuration or container orchestration.

---

## 4.4 Knowledge Graph

**Trigger condition**: Graph database driver import detected

### Grep Patterns

```
neo4j|Neo4jDriver|neo4j-driver
dgraph|DgraphClient
arangodb|ArangoClient
neptune
rdf|rdflib
sparql|SPARQLWrapper
gremlin|tinkerpop
networkx  # only if used with persistent store
```

### File Presence

```
graph/
ontology/
*.rdf
*.ttl
*.owl
```

### Subagent Signal
Agent A reports graph traversal patterns or node/edge type definitions.

---

## 4.5 Scalability

**Trigger condition**: Queue/worker system OR sharding configuration detected

### Grep Patterns

```
# Message queues
bullmq|bull|BullModule
celery|Celery
rabbitmq|amqplib|amqp
kafka|KafkaJS|confluent.kafka
aws-sdk.*sqs|SQSClient
nats|NatsClient
redis.*queue|rq|RQ

# Workers
worker_threads|Worker\(
cluster\.fork|os\.fork
child_process\.fork

# Sharding
shard|sharding|partition
replica|replication
loadbalancer|load.balancer
```

### File Presence

```
workers/
queues/
jobs/
tasks/
celeryconfig.py
```

### Subagent Signal
Agent B reports message passing patterns, job queues, or horizontal scaling configuration.

---

## 4.6 Concurrency & Multi-Agent

**Trigger condition**: Concurrent execution patterns OR agent orchestration detected

### Grep Patterns

```
# Python async
asyncio\.gather|asyncio\.create_task
aiohttp|httpx\.AsyncClient
async\s+def\s+\w+.*gather

# Rust async
tokio::spawn|tokio::select
async\s+fn

# JavaScript/TypeScript concurrency
Promise\.all|Promise\.allSettled|Promise\.race
Worker\(|SharedWorker
new\s+Worker

# Threading
threading\.Thread|ThreadPoolExecutor
multiprocessing\.Process|ProcessPoolExecutor

# Agent orchestration
CrewAI|crew|Agent\(.*role
AutoGen|autogen
LangGraph|StateGraph
swarm|Swarm
agent.*orchestrat|orchestrat.*agent
multi.agent|multi_agent
```

### File Presence

```
agents/
agent/
crew/
workflows/
orchestrator/
```

### Subagent Signal
Agent A or B reports parallel execution patterns, agent definitions, or workflow orchestration in core abstractions or architecture.

---

## Detection Method

For each section, the orchestrator runs:

1. **Grep scan**: Run `Grep` with the patterns above against the codebase (skip node_modules, dist, build)
2. **File check**: Run `Glob` for the file presence patterns
3. **Subagent cross-reference**: Check if any subagent (A/B/C/D) reported related patterns

**Inclusion decision**: If **any** method returns positive → include the section.

**Important**: False positives are acceptable (section can be sparse). False negatives are not (missing a major subsystem is worse than including an empty one).
