# Lexis: Reversible Migrations or With Rollback Plan

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Database schema migrations (relational or NoSQL) in any persistent environment

## Purpose

Migrations without rollback become time bombs: when the corresponding deploy fails or regresses, the schema has advanced but the previous code no longer understands it. The team gets stuck — it can only move forward, never backward. Worse: destructive migrations (DROP COLUMN, DROP TABLE) without backup or detailed plan can erase unrecoverable data in minutes.

This Lexis exists to ensure that **every migration is automatically reversible** (via `down` in Alembic, `migrate:rollback` in Django etc.) **OR has a documented manual rollback plan** with validated backup before any destructive change.

## Law

> **Every schema migration MUST be automatically reversible by the migrations framework OR have a documented and tested manual rollback plan. Destructive migrations (DROP, ALTER that loses data) MUST have a validated backup from the previous 24h and a declared maintenance window. Code deploys MUST be compatible with the previous AND new schema (expand-contract) in systems with rolling deploy.**

## Rules

### 1. Automatic reversibility by default

Additive migrations (CREATE TABLE, ADD COLUMN NULLABLE, CREATE INDEX CONCURRENTLY) **MUST** have `down` implemented:

```python
# Alembic
def upgrade():
    op.add_column("refund", sa.Column("notes", sa.String(500), nullable=True))

def downgrade():
    op.drop_column("refund", "notes")
```

If the migrations framework generates `down` automatically, accept; otherwise, write manually.

### 2. Destructive migrations: plan + backup

For `DROP TABLE`, `DROP COLUMN`, `ALTER TYPE` with loss of data, `RENAME` in production:

1. **Point-in-time backup** confirmed in the last 24h (via AWS Backup, pg_dump, etc.).
2. **Maintenance window** declared with stakeholders when tier-1.
3. **Manual rollback plan** written:
   - How to restore from backup.
   - How long it takes.
   - What is the point of no return (after this, rollback is only via restore-from-backup).
4. **Test in staging** with representative volume, measuring duration.

### 3. Expand-Contract for rolling deploys

When the system uses rolling deploy (N pods, gradual deploy):

- **Expand Phase**: migration adds new structure keeping the old one. Code deploy uses both.
- **Contract Phase**: migration removes old structure. Deploy uses only the new one.

E.g.: rename column `status` → `state`:

| Step | Migration | Code |
|---|---|---|
| 1 (expand) | `ADD COLUMN state` + trigger copies `status` → `state` | Reads from `state`, writes to `state` AND `status` |
| 2 | — | Reads and writes only to `state` |
| 3 (contract) | `DROP COLUMN status` + trigger | — |

An atomic deploy that changes schema + code simultaneously **breaks** in rolling deploy.

### 4. Long-duration migrations require strategy

Queries that scan large tables (> 1M rows) can block:

- `ADD COLUMN NOT NULL DEFAULT 'x'` in PostgreSQL locks the table → use `ADD COLUMN` nullable, backfill in batches, then `SET NOT NULL`.
- `CREATE INDEX` without `CONCURRENTLY` locks writes → always use `CONCURRENTLY` (outside transaction).
- `ALTER COLUMN TYPE` (with rewrite) in large table → evaluate pg_repack, shadow tables, or accept window.

Long migration **MUST** declare estimated duration and strategy in comment at the top.

### 5. No DDL in shared transaction with DML

Never put DDL (CREATE, ALTER) and massive DML (INSERT, UPDATE) in the same migration. DDL can be reversible; real data DML requires a separate plan.

### 6. Periodic restore test

Backup without restore test is useless backup. **Quarterly** (or by SOX/SOC 2):
- Execute restore in staging environment from production backup.
- Measure time; validate data.
- If fails → P0; backup strategy broken.

## Applicability

- **Applies to:** every migration in shared environment (staging, production). Personal sandbox is outside enforcement.
- **Linked agents:** `warrior-demeter`, `warrior-apollo` (when writing migration), `warrior-atlas` (when configuring backup).
- **Exceptions:** None. Migrations in sandbox should still follow the structure even without enforcement.

## Consequences of Violation

1. **Unexpected lock in production:** table locked 30min at peak time → customer-visible downtime.
2. **Data loss:** `DROP COLUMN` without backup or with old backup → unrecoverable data.
3. **Irreversible deploy:** feature deploy breaks, but schema advanced; no way back; emergency fix.
4. **Remediation:**
   - Audit trail: `pg_locks`, CloudTrail, migration tool logs.
   - Backup restore if data lost.
   - Blameless post-mortem (`kata-postmortem-write`).
   - Corrective action: checklist in migration PR; automated approval blocks until checklist filled.

## Automated Validation

- **Tool:**
  - Lint on migrations (e.g.: `squawk` for PostgreSQL): detects dangerous patterns (`ADD COLUMN NOT NULL DEFAULT`, `CREATE INDEX` without CONCURRENTLY).
  - Check on PR that `down` is implemented in every migration.
  - Test run in CI: `upgrade` + `downgrade` in test DB.
- **Timing:** on each PR containing migration; quarterly (restore test).
- **Metric:** 100% of migrations with `down` or documented plan; 0 `ADD COLUMN NOT NULL DEFAULT` on tables > 10k rows without multi-step strategy.

## References

- `codex-data-modeling` — prior design patterns
- `codex-migrations-strategy` — detailed playbooks
- `warrior-demeter` — leads complex migrations
- [Safer ActiveRecord Migrations](https://github.com/ankane/strong_migrations)
- [Alembic Best Practices](https://alembic.sqlalchemy.org/en/latest/tutorial.html#running-our-first-migration)
