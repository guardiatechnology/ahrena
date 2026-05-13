# Kata: Architecture Brief

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Phase 3 of the Issue-Driven flow — mapping affected components, design decisions, and delegation to specialist warriors when applicable

## Objective

From the brief (Phase 1) and requirements (Phase 2), produce an architectural design document containing: the map of affected components, the proposed technical approach, decisions to be made, delegation to specialist warriors (Daedalus for API, Kronos for events), and invocation of `kata-adr-write` when there is a relevant architectural decision. The final document at `.ahrena/issues/{n}/03-architecture.md` is the basis for Gate 1 and delimits the scope against which Gate 2 will perform the scope creep check.

## When to Use

- Phase 3 of the flow orchestrated by `warrior-athena`, after Phase 2 (`kata-requirements-brief`)
- Whenever it is necessary to technically define how to implement the ACs before coding

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Phase 1 brief | Yes | `.ahrena/issues/{n}/01-brief.md` |
| Phase 2 requirements | Yes | `.ahrena/issues/{n}/02-requirements.md` |
| Project stack | Yes | Language, frameworks, existing patterns (detected by reading the repo) |

## Workflow

```
Progress:
- [ ] 1. Read brief + requirements
- [ ] 2. Map affected components
- [ ] 3. Propose technical approach
- [ ] 4. Identify relevant architectural decisions
- [ ] 5. Delegate to specialists if applicable (Daedalus/Kronos)
- [ ] 6. Invoke kata-adr-write for each relevant decision
- [ ] 7. Persist to .ahrena/issues/{n}/03-architecture.md
- [ ] 8. Update checkpoint
```

### Step 1: Read brief + requirements

1. Read `01-brief.md` and `02-requirements.md` under `.ahrena/issues/{n}/`.
2. If any is missing, inform and stop — predecessor phases must be complete.
3. Identify ACs that require special architectural attention (e.g., performance, consistency, idempotency).

### Step 2: Map affected components

For each AC:

1. Identify existing files/modules that will be modified.
2. Identify new files/modules to be created.
3. Identify affected external contracts (APIs, events, databases, queues).
4. Consolidate in a table:

| Component | Type | Action | ACs covered |
|---|---|---|---|
| `src/refunds/service.py` | module | create | AC-1, AC-2 |
| `src/payments/repository.py` | module | modify (add method) | AC-3 |
| `openapi/refunds.yaml` | spec | modify | AC-1 |
| `events/refund.created` | event | create | AC-2 |

This table is the **scope boundary** used by `kata-quality-gate` in the scope creep check.

### Step 3: Propose the technical approach

Describe in structured prose:

1. **Main flow:** sequence of calls/events for the happy path.
2. **Alternative flows:** errors, idempotency, retry.
3. **Persistence:** affected entities, required migrations.
4. **External integrations:** contracts, authentication, rate limits.
5. **Observability:** relevant logs, metrics, traces.

### Step 4: Identify relevant architectural decisions

For each design point, ask: is it a **decision** or a **follow-through of an existing pattern**?

Use the `codex-issue-workflow` checklist (section "When to generate ADR"):

| Generate ADR? | Examples |
|:-:|---|
| ✅ | New tech choice; deviation from pattern; significant trade-off; affects multiple components; affects external contract |
| ❌ | Localized bugfix; local refactor following pattern; new endpoint following existing structure |

Record each candidate decision with: title, motivation, alternatives considered.

### Step 5: Delegate to specialists if applicable

**If the issue involves REST API design:**
1. Invoke `warrior-daedalus` → `kata-api-design-oas`
2. Pass as context: the brief, the requirements, and the affected components.
3. Daedalus produces OAS + Markdown under `paths.oas`.
4. Reference those files in the architecture document of this phase.

**If the issue involves event design (CloudEvents):**
1. Invoke `warrior-kronos` → `kata-events-doc`
2. Pass the same artifacts as context.
3. Kronos produces an event catalog under `paths.events`.
4. Reference those files in the architecture document.

Record in the checkpoint which warrior was delegated and where the output is.

### Step 6: Invoke `kata-adr-write` for each relevant decision

For each decision identified in Step 4 that deserves an ADR:

1. Invoke `kata-adr-write` with: decision title, context, proposed decision, alternatives.
2. `kata-adr-write` creates `docs/adr/ADR-{n}-{title}.md` with status `proposed`.
3. The ADR transitions to `accepted` after approval at Gate 1.
4. Reference each created ADR in the architecture document.

### Step 7: Persist to `.ahrena/issues/{n}/03-architecture.md`

Structure:

```markdown
# Architecture — Issue #{n}: {title}

- **References:** [Brief](./01-brief.md) · [Requirements](./02-requirements.md)
- **Date:** {YYYY-MM-DD}

## Affected Components

| Component | Type | Action | ACs covered |
|---|---|---|---|
| ... | ... | ... | ... |

> This table defines the exact scope of files to modify.
> Modifications outside this table are blocked by Gate 2 as scope creep.

## Technical Approach

### Main flow

{prose description, optional Mermaid sequence diagram}

### Alternative flows

- **Error {X}:** {how it is handled}
- **Idempotency:** {how it is guaranteed}
- **Retry:** {policy}

### Persistence

{affected entities, required migrations}

### External integrations

{contracts, auth, rate limits}

### Observability

{logs, metrics, traces}

## Specialist Delegations

- **Daedalus (API):** see `{OAS path}`, `{doc path}`
- **Kronos (Events):** see `{catalog path}`

(omit sections that do not apply)

## Architectural Decisions (ADRs)

- [ADR-{n}: {title}](../../adr/ADR-{n}-{slug}.md) — status: proposed
- [ADR-{m}: {title}](../../adr/ADR-{m}-{slug}.md) — status: proposed

(section absent if no relevant decision was made)

## Technical Risks

- {Risk 1 and mitigation}
- {Risk 2 and mitigation}

## Next Phase

Gate 1 — Scope Approval (awaiting human approval).
```

### Step 8: Update checkpoint

1. Update `.ahrena/workflow/issue-{n}/checkpoint.md`:
   - completed phase: 3
   - next: Gate 1 (human approval)
   - references: `03-architecture.md`, created ADRs
   - delegations: invoked specialist warriors and their outputs
2. `warrior-athena` requests human approval before advancing to Phase 4.

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Architecture document | Markdown | `.ahrena/issues/{n}/03-architecture.md` |
| ADRs (0 or more) | Markdown MADR | `docs/adr/ADR-{n}-*.md` |
| OAS/doc/events (if applicable) | per Daedalus/Kronos | `paths.oas`, `paths.events` |
| Updated checkpoint | Markdown | `.ahrena/workflow/issue-{n}/checkpoint.md` |

## Restrictions

- **The component table is binding:** it defines the exact scope that Gate 2 will use for the scope creep check. Anything outside that table will be blocked.
- **ADRs in `proposed` status:** until Gate 1, all ADRs produced in this phase stay with status `proposed`. Transition to `accepted` only occurs after human approval.
- **Delegation does not replace the phase document:** even when delegating to Daedalus/Kronos, the kata must produce `03-architecture.md` with overall context and references to the specialists' outputs.
- **No coding:** this kata describes **what** and **where**, not **how** (Apollo will do the how in Phase 4).
- **Fixed destination:** `.ahrena/issues/{n}/03-architecture.md` and `docs/adr/ADR-*` (per `lex-issue-driven`).

## References

- `lex-issue-driven` — laws of the flow
- `codex-issue-workflow` — checklist for when to generate ADR
- `kata-adr-write` — ADR writing in MADR format
- `warrior-daedalus`, `kata-api-design-oas` — API delegation
- `warrior-kronos`, `kata-events-doc` — events delegation
- `codex-codex`, `codex-lexis` — artifact conventions
