# Codex: Data Modeling

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Data modeling patterns for persistence — entities, value objects, aggregates, normalization, schema evolution, choice between relational and NoSQL

## Content

### Entity vs. Value Object vs. Aggregate

**Entity**: has unique identity (`entity_id`), changes over time.
- E.g.: `User`, `Refund`, `Account`.
- Has primary key; participates in FKs.

**Value Object**: immutable, defined by its values.
- E.g.: `Money(amount, currency)`, `Address`, `Email`.
- Stored as embedded columns (`amount_cents` + `currency_code`) or JSON.

**Aggregate**: transactional consistency boundary.
- E.g.: `Order` (root) with `OrderItems`.
- Changes from aggregate root; invariants maintained together.
- Natural map to DB transaction.

Rule: prefer **small aggregates** — a large aggregate reduces concurrency.

### Base attributes in Ahrena entity

Every persistent entity follows `codex-entities`:

| Field | Type | Purpose |
|---|---|---|
| `entity_id` | UUID v4 | Stable identifier (never reuse) |
| `entity_type` | string | Polymorphism and auditing |
| `version` | int | Optimistic locking; increments on each update |
| `created_at` | timestamp | Immutable after create |
| `updated_at` | timestamp | Updated on each change |
| `created_by` | UUID (ref user) | Actor who created |
| `updated_by` | UUID (ref user) | Actor of last change |

Logical deletion: `discarded_at` field (nullable timestamp) instead of physical DELETE, except when compliance requires purge.

### Normalization — when and how much

- **3NF** as default for OLTP: avoids inconsistency, facilitates UPDATE.
- **Selective denormalization** for critical read paths:
  - Counters (`total_refunds`) materialized with trigger or job.
  - Materialized views for reports.
  - Cache (Redis) for frequent lookups.
- **OLAP**: snowflake/star schema; different from OLTP.
- **Avoid**: CSV fields in string, abusive arrays, JSON where explicit column would fit.

### Relational vs. NoSQL

**Relational (Postgres, Aurora) when:**
- ACID transactions over multiple entities.
- Ad-hoc queries with JOINs.
- Strong consistency is a requirement.
- Domain has complex relationships.

**DynamoDB when:**
- Known and stable access patterns.
- Massive and predictable scale.
- Sub-10ms latency required.
- Domain is key-value or simple hierarchical.

**DocumentDB / MongoDB when:**
- Schema evolves rapidly (flexible documents).
- Data aggregated by nature (one doc contains the aggregate).
- Flexible queries over documents.

**Time-series DB (Timestream, InfluxDB) when:**
- Append-heavy, queries by time window.
- Metrics, events, IoT.

Document the choice in ADR (`kata-adr-write`) when not trivial.

### Indexes

- **Every FK** has an index (unless proven it is never used in query).
- **Frequent queries** define composite indexes; analyze `EXPLAIN`.
- **Indexes on timestamps** for ranges (`created_at DESC`).
- **Partial indexes** for filtered queries (`WHERE status = 'active'`).
- **Limit**: 5-7 indexes per large table. Each index costs in writes.

Review indexes quarterly: `pg_stat_user_indexes` to detect unused.

### Migrations (expand-contract)

See `lex-migrations-reversible`. Typical pattern:

1. **Expand**: ADD COLUMN nullable + code writes in both (new + old).
2. **Backfill**: job migrates historical data in batches.
3. **Cut-over**: code starts reading only from the new one.
4. **Contract**: DROP old COLUMN.

Destructive migration without this pattern = downtime.

### Partitioning

When table reaches ~100M+ rows or contains long time series:

- **Range partitioning** by `created_at` (month/year): recent queries fast; old archive in separate partitions.
- **Hash partitioning** by `tenant_id`: multi-tenant isolation.
- **List partitioning** by closed category.

Postgres native Partitioning > application layer partitioning.

### Soft delete vs. hard delete

**Soft delete** (`discarded_at` timestamp):
- Preserves history.
- Allows undo.
- Complicates queries (every WHERE filters `discarded_at IS NULL`).

**Hard delete** (physical DELETE):
- Mandatory for data subject to LGPD with deletion request.
- Requires audit plan (CloudTrail, separate audit log).

Choose based on domain — document decision.

### Eventual consistency

In distributed systems (CQRS, event sourcing, multi-region):

- Accept that read model becomes eventually consistent.
- Declare **consistency guarantees** per use case (read-after-write on same account? or is it acceptable to read previous version for a few seconds?).
- Avoid unintentional mix: transaction writes and event is read sync → race risk.

### LGPD / GDPR from design

- **Classify data** when creating table: which column contains PII?
- **Minimize**: only persist what is needed.
- **Encrypt at rest** (default via KMS in RDS/Aurora).
- **Audited access**: queries on PII logged.
- **Retention**: declared in `docs/data-retention.yaml` (`lex-data-retention`).
- **Export and deletion**: endpoints ready from day 1.
