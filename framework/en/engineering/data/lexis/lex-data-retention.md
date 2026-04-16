# Lexis: Data Retention Policy

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Persistent storage of personal, transactional, logs, and artifacts data — retention policy defined by class and enforced

## Purpose

Data accumulates indefinitely when no one defines when to delete. S3 buckets grow to TBs, tables are left with years of orphan rows, access logs maintain history that violates regulation (LGPD right to be forgotten, GDPR storage limitation). Cost grows, performance degrades, legal risk rises silently.

This Lexis exists to ensure that **every class of data has a declared retention policy before first storage**, that **automatic purges are configured**, and that **legal compliance (LGPD, GDPR) is respected** — including the right to be forgotten of the data subject.

## Law

> **Every persistent data class MUST have a retention policy declared in `docs/data-retention.yaml` with value, legal/business justification, and enforcement mechanism. Personal data MUST be deletable upon request of the data subject (LGPD Art. 18 / GDPR Art. 17) within the legal deadline. Logs that contain PII MUST have specific retention, never `indefinite`.**

## Rules

### 1. Policy declared per class

Structure in `docs/data-retention.yaml`:

```yaml
classes:
  - name: transactional-core
    description: "Payment transactions, refunds, ledger"
    retention: "7 years"
    legal_basis: "Law 12.846/2013 (BR), SOX 17 CFR 240.17a-4 (if US)"
    storage: "Postgres primary; S3 Glacier after 1y for archive"
    enforcement: "postgres lifecycle job + S3 lifecycle policy"
    
  - name: pii-customer
    description: "Customer name, CPF, email, phone"
    retention: "while active + 5 years after last transaction"
    legal_basis: "LGPD Art. 16 — processing during necessity + defense of rights"
    deletion_policy: "upon user request OR auto after 5y inactivity"
    erasure_sla: "15 days from request (LGPD)"
    storage: "Postgres customer schema"
    
  - name: operational-logs
    description: "Application logs without PII"
    retention: "90 days"
    storage: "CloudWatch Logs"
    
  - name: audit-logs
    description: "CloudTrail, application audit logs"
    retention: "7 years (SOC 2 / SOX)"
    storage: "Immutable S3 bucket (Object Lock)"
    
  - name: cache
    description: "Redis / Memcached"
    retention: "ephemeral, TTL 24h default"
    storage: "ElastiCache"
```

### 2. Automated enforcement

For each class, an automatic expiration mechanism **MUST** exist:

- **Postgres**: `DELETE ... WHERE created_at < NOW() - INTERVAL 'X'` in cron/job.
- **S3**: Lifecycle policy with transition and expiration.
- **CloudWatch Logs**: `retentionInDays` on the log group.
- **Redis**: TTL per key.

Retention without enforcement is shelf policy.

### 3. Right to be forgotten (LGPD / GDPR)

The system **MUST** support, for personal data:

- **Export** (LGPD Art. 18 item VI): structured format (JSON) consumable.
- **Deletion** (LGPD Art. 18 item VI): anonymization or hard delete.
  - If deleting violates another requirement (e.g.: ledger needs to remain): anonymize PII keeping transactional structure.
- **SLA**: respected in all sources (DB, long-term backups, logs, analytics, caches).

Deletion in backups is complex: document policy (e.g.: "PII in backup is encrypted; keys destroyed on backup expiration") with legal.

### 4. PII retention in logs

Logs **MUST** not contain PII when possible (see `lex-observability-required`). If they do:
- Maximum retention: 90 days (or shorter applicable legal deadline).
- Redaction applied before persisting when feasible.

Logs in third-party systems (Datadog, Splunk) follow the same rule.

### 5. No `retention: indefinite` without justification

Valid category only for:
- **Audit logs required by law** (SOX 7 years is "indefinite" from the app's point of view).
- **System data** without PII and with controlled cost (config, feature flags history).

All other cases require explicit legal/business justification.

### 6. Quarterly audit

Quarterly:
- Verify that enforcement worked (samples deleted on time).
- Review growth of each class (storage = cost).
- Revalidate legal basis (changes in LGPD, contracts, internal policies).

## Applicability

- **Applies to:** every system that persists data beyond process memory.
- **Linked agents:** `warrior-demeter` (design), `warrior-atlas` (S3/RDS lifecycle), `warrior-apollo`/`warrior-hephaestus` (implementation of export/deletion endpoints).
- **Exceptions:** None. Sandbox may have shorter retention; legal compliance is universal.

## Consequences of Violation

1. **LGPD fine:** up to 2% of revenue for not respecting the right to be forgotten.
2. **Exploding cost:** TB accumulated in S3 Standard without lifecycle; monthly bill grows.
3. **Degraded performance:** tables with years of orphan rows make queries slow, backups heavy.
4. **Remediation:**
   - Inventory of data classes → `docs/data-retention.yaml`.
   - Configure enforcement (lifecycle policies, cron jobs).
   - Implement export/deletion endpoints.
   - Quarterly audit on calendar.

## Automated Validation

- **Tool:**
  - Linter validates that `docs/data-retention.yaml` exists and lists all classes declared in DB schema.
  - Monthly check: size of each class vs. expected growth.
  - End-to-end test: create synthetic user, request deletion, verify removal in all sources within SLA.
- **Timing:** pre-deploy of new data domain; monthly/quarterly.
- **Metric:** 100% of documented classes; 100% of deletion requests within SLA; monthly growth compatible with baseline.

## References

- `codex-data-modeling`
- `lex-aws-cost` — retention impacts AWS cost
- `warrior-demeter`
- [LGPD Art. 16 and 18](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [GDPR Art. 17 (right to erasure)](https://gdpr-info.eu/art-17-gdpr/)
