# Codex: Sorting in RESTful APIs

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guardia platform — REST APIs — sorting

## Content

- Sorting limited to temporal properties: **created_at**, **updated_at**, **reference_at** (other fields only if documented in the contract and indexed).
- Use indexes to avoid full scan; **stable** ordering (secondary criterion e.g. entity_id) so pagination does not duplicate or skip items.
- Parameters: **order_by** (default created_at), **sort** (default asc). Omission → created_at asc.
- Disallowed values for order_by or sort → 400 Bad Request (ERR400_INVALID_PARAMETER, ORDER_BY_INVALID, SORT_INVALID).
- In **partitioned** scenarios (e.g. by tenant), ordering MUST respect the partition scope.
- Exception: fixed ordering by business rule may omit order_by if justified and recorded in a PDR (Product Decision Record).
