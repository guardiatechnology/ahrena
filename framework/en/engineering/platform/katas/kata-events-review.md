# Kata: CloudEvents Review

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Guardia platform — compliance review of CloudEvents documentation, publishers, and consumers against Guardia Lexis and Codex

## Objective

This Kata defines the procedure to **review CloudEvents-related changes** (documentation at `docs/{context}/events/events.md`, publisher and consumer code, schema and payload definitions) against Guardia's CloudEvents Lexis and Codex, identifying compliance violations, gaps, breaking changes, and producing a structured review report with severity-classified findings. It is the symmetric pair of `kata-api-design-review` for the events surface.

## When to Use

- When a PR modifies `events.md` or any file under `docs/{context}/events/`
- When a PR modifies code that publishes or consumes CloudEvents (publishers, consumer handlers, event-schema definitions)
- When invoked by `warrior-argos` during a multi-axis Pull Request review
- When `cry-review-pr` is triggered and the diff touches event surfaces

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Diff or path to events.md | Yes | Path to the modified `events.md` file or unified diff containing event-surface changes |
| Old version of events.md (for breaking-change check) | No | If omitted, the kata fetches `git show HEAD~1:<path>` from the base branch when reviewing a PR |
| Bounded Context name | No | If omitted, infers from path `docs/{context}/events/events.md` |
| Fix mode | No | `report` (default) — findings only; `fix` — propose inline corrections alongside findings |

## Workflow

```
Progress:
- [ ] 1. Read directives and locate event surface
- [ ] 2. Consult Lexis and Codex
- [ ] 3. Validate type format and naming
- [ ] 4. Validate idempotencykey presence
- [ ] 5. Validate payload (data) against entities catalog
- [ ] 6. Validate size and serialization
- [ ] 7. Detect breaking changes against the base version
- [ ] 8. Validate publishers and consumers (when in diff)
- [ ] 9. Produce review report
```

### Step 1: Read Directives and Locate Event Surface

1. Read `.ahrena/.directives` to obtain `language.default`
2. Identify the event surface in the diff:
   - Documentation: files matching `docs/*/events/events.md`
   - Code: files importing or emitting CloudEvents (heuristic: grep for `event.guardia.`, `idempotencykey`, `cloudevents`)
3. If neither documentation nor code touches the event surface, exit early with `not applicable: no event surface in diff`
4. Record the Bounded Context inferred from the path

### Step 2: Consult Lexis and Codex

1. Consult **lex-cloudevents** — events MUST follow CloudEvents (structure, required properties, idempotencykey, JSON, size < 12KB)
2. Consult **codex-cloudevents** — event structure, type format `event.guardia.{module}.{entity_type}.{event_name}`, `data` shape per codex-entities
3. Consult **lex-entities** and **codex-entities** — entity fields in `data` (entity_id, entity_type, version, created_at, updated_at, discarded_at; history omitted)
4. Consult **lex-entity-naming** — `entity_type`, JSON field names, and CloudEvents type segments MUST be in snake_case
5. Consult **lex-idempotency** and **codex-idempotency** — idempotencykey required on every published event; consumers MUST deduplicate
6. Consult **lex-feature-design-docs** — canonical structure under `docs/{context}/events/events.md`

### Step 3: Validate Type Format and Naming

For each event documented or emitted in the diff:

1. **type regex** — MUST match `^event\.guardia\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$`. Flag any deviation as 🔴 BLOCKER.
2. **module segment** — declared and stable; renaming an existing module is a breaking change
3. **entity_type segment** — snake_case singular (e.g., `scheduled_transfer`, not `scheduledTransfer` or `scheduled_transfers`)
4. **event_name segment** — snake_case verb in past participle (e.g., `created`, `approved`, `executed`, `cancelled`)
5. **Catalog presence** — every documented type MUST appear in the events catalog table at the top of `events.md`

### Step 4: Validate idempotencykey Presence

For each event documented or emitted:

1. **In documentation** — every JSON example in `events.md` MUST include `idempotencykey` at the envelope level
2. **In publisher code** — every call site building a CloudEvent MUST set `idempotencykey` (typically equal to `entity_id` of the originating request)
3. **In consumer code** — handlers MUST persist `(type, idempotencykey)` and short-circuit on duplicate
4. Flag any event missing `idempotencykey` as 🔴 BLOCKER citing `lex-idempotency`

### Step 5: Validate Payload (data) Against Entities Catalog

For each event whose `data` represents a persistent entity:

1. **entity_id** — present, typed as UUID v7
2. **entity_type** — present, snake_case, matches the type segment
3. **created_at, updated_at** — present as ISO 8601 timestamps
4. **version** — present when optimistic locking is documented for the entity
5. **history** — MUST be omitted from `data` (per lex-entities)
6. **Field naming** — all `data` fields MUST be snake_case (per lex-entity-naming)
7. **Cross-reference** — fields in `data` MUST exist in the corresponding `docs/{context}/entities/{entity}.md` catalog. Flag any field present in `data` but absent from the entity catalog as 🟡 WARNING (catalog out of sync) or 🔴 BLOCKER (silent leak of internal field)

### Step 6: Validate Size and Serialization

1. **Serialization** — JSON UTF-8 (per lex-cloudevents)
2. **Size** — payload < 12KB. When the diff includes a representative example, compute byte length and flag if ≥ 12KB
3. **Content-Type** — `datacontenttype: application/json` declared

### Step 7: Detect Breaking Changes Against the Base Version

For each event present in **both** the base and the new version of `events.md` (or schema):

| Change | Severity | Reason |
|--------|----------|--------|
| `type` renamed (any segment changed) | 🔴 BLOCKER | Consumers subscribed to the old type silently stop receiving |
| Required field removed from `data` | 🔴 BLOCKER | Consumers reading the field break |
| Field type narrowed (e.g., `string` → `enum<a,b>`) | 🔴 BLOCKER | Existing values become invalid |
| Required field added without backfill plan | 🔴 BLOCKER | Old consumers unaware; emitters publishing without it break the contract |
| Field renamed | 🔴 BLOCKER | Same as removed + added |
| Optional field added with default | 🟡 WARNING | Consumers SHOULD ignore unknown fields, but flag for awareness |
| `module` segment of an existing entity changed | 🔴 BLOCKER | Topic routing breaks |

Detection method: compare the events catalog table (entity_type × event_name × type) and per-event `data` field list. Use git: `git show <base-sha>:<path>` vs current.

For events **only in the new version** (added): no breaking change — record as 🟡 WARNING only when the corresponding entity exists in the base but lacks the new state in its lifecycle diagram.

### Step 8: Validate Publishers and Consumers (when in diff)

When publisher or consumer code is in the diff:

1. **Publisher** — confirm the call site:
   - sets the `type` segment per the catalog
   - includes `idempotencykey`
   - serializes `data` with snake_case fields
   - propagates trace context per `lex-observability-required`
2. **Consumer** — confirm the handler:
   - subscribes to the cataloged `type` (no typos)
   - checks idempotency before processing
   - returns ACK after persistence (not before)
   - logs failures with correlation_id without exposing PII

### Step 9: Produce Review Report

Generate a structured Markdown review report:

1. **Header** — events surface reviewed (file paths, total events count, total publishers/consumers in diff), overall verdict:
   - ✅ **Compliant** — zero BLOCKERs and zero WARNINGs
   - 🟡 **Warnings** — zero BLOCKERs, one or more WARNINGs
   - 🔴 **Violations** — one or more BLOCKERs
2. **Findings table** — one row per finding:

   | Severity | Event / File | Lexis / Codex | Finding | Suggestion |
   |----------|--------------|---------------|---------|------------|

   Severity levels:
   - `🔴 BLOCKER` — Lexis violation or breaking change; MUST be fixed before merge
   - `🟡 WARNING` — Codex deviation or non-blocking concern; SHOULD be fixed in this PR or a follow-up

3. **Summary counts** — total BLOCKER / WARNING
4. **Breaking-change matrix** — when Step 7 finds anything, list old → new with the change type
5. **Next steps** — in `fix` mode, append inline correction for each BLOCKER and WARNING; in `report` mode, list the events requiring attention

If no findings, state: "Event surface fully compliant with Guardia Lexis and Codex; no breaking changes detected."

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Review report | Markdown | Returned to the caller (typically `warrior-argos`) for inclusion in the consolidated PR review-comment |

## Execution Example

### Example Input

```
Diff path: docs/scheduled-payments/events/events.md
Base SHA: 12bf878 (main)
Fix mode: report
```

### Example Output (summary)

```markdown
## CloudEvents Review — docs/scheduled-payments/events/events.md

**Events reviewed:** 6 | **Verdict:** 🔴 1 BLOCKER, 2 WARNINGs

| Severity | Event / File | Rule | Finding | Suggestion |
|----------|--------------|------|---------|------------|
| 🔴 BLOCKER | event.guardia.platform.scheduledTransfer.approved | lex-entity-naming | entity_type segment in camelCase | Rename to `scheduled_transfer` (snake_case) |
| 🟡 WARNING | event.guardia.platform.scheduled_transfer.executed | lex-cloudevents | data.failure_reason marked optional but absent from entity catalog | Add `failure_reason` to docs/scheduled-payments/entities/scheduled-transfer.md |
| 🟡 WARNING | events.md catalog table | codex-feature-design-docs | Missing Consumers column | Populate Consumers column for all rows |

**Breaking-change matrix:** none.

**Next steps:** fix 1 BLOCKER before merge; address 2 WARNINGs in this PR or open a follow-up Issue.
```

## Constraints

- This Kata produces only a review report; it does not modify documentation or code unless `fix` mode is explicitly requested
- Every deviation MUST be classified as 🔴 BLOCKER (Lexis violation or breaking change) or 🟡 WARNING (Codex deviation or non-blocking) — never silently accept
- Escalate to a human when a deviation may be an intentional exception requiring an ADR
- Do not flag deviations in events explicitly excluded from the review scope
- The breaking-change check requires a base version; if unavailable, skip Step 7 and report `breaking-change check skipped: base version unavailable` as 🟡 WARNING

## References

- `lex-cloudevents`, `codex-cloudevents`
- `lex-entities`, `codex-entities`, `lex-entity-naming`
- `lex-idempotency`, `codex-idempotency`
- `lex-feature-design-docs`, `codex-feature-design-docs`
- `lex-observability-required`
- `kata-api-design-review` — symmetric pair for HTTP API contracts
- `kata-events-doc` — authorship counterpart
- [CloudEvents Specification](https://cloudevents.io/)
