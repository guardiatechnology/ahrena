# Kata: Requirements Elicitation (PO perspective)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Phase 2 of the Issue-Driven flow — transforming the Phase 1 brief into a numbered list of acceptance criteria, DoD, and out-of-scope items

## Objective

Adopting the Product Owner perspective, convert the brief produced in Phase 1 into a requirements document containing: a numbered list of acceptance criteria (ACs), Definition of Done (DoD), explicitly declared out-of-scope items, and pending questions for the user. The numbered ACs form the basis of the AC ↔ test traceability required by Gate 2 (per `lex-issue-driven`).

## When to Use

- Phase 2 of the flow orchestrated by `warrior-athena`, after Phase 1 (`kata-issue-analysis`) completes
- Whenever it is necessary to formalize measurable criteria from a generic feature/bugfix description

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Phase 1 brief | Yes | `.ahrena/issues/{n}/01-brief.md` |
| User confirmations | No | Responses to pending questions identified in the brief (via interaction) |

## Workflow

```
Progress:
- [ ] 1. Read the Phase 1 brief
- [ ] 2. Identify actors, entities, and behaviors
- [ ] 3. Formulate ACs in Given/When/Then format
- [ ] 4. Resolve unknowns with user questions
- [ ] 5. Define DoD and out-of-scope
- [ ] 6. Persist to .ahrena/issues/{n}/02-requirements.md
- [ ] 7. Update checkpoint
```

### Step 1: Read the Phase 1 brief

1. Read `.ahrena/issues/{n}/01-brief.md`.
2. If it does not exist, inform that Phase 1 was not executed and stop.
3. Focus on sections: Problem, Additional Context, Work Type, Risks and Unknowns.

### Step 2: Identify actors, entities, and behaviors

1. List the actors involved (e.g., customer, payment system, backoffice).
2. List the entities affected (e.g., Refund, Payment, AuditLog).
3. List the expected behaviors (e.g., "create refund", "audit attempt", "notify customer").
4. Record the three groups internally for use in Step 3.

### Step 3: Formulate ACs in Given/When/Then format

For each identified behavior, formulate one or more ACs in the format:

```
AC-{N}: {short title}
  Given {observable precondition}
  When {action or event}
  Then {observable, measurable result}
```

**Rules for ACs:**
- Each AC must be **testable** — if there is no way to write a test, rewrite it.
- Each AC covers **one behavior**, not multiple.
- ACs are numbered sequentially from `AC-1`, with no gaps.
- Cover happy paths, relevant error cases, and edges (e.g., idempotency, concurrency when applicable).

### Step 4: Resolve unknowns with user questions

1. For each item in "Risks and Unknowns" of the brief, formulate an objective question to the user.
2. Ask in batches (up to 5 per round) so as not to tire the user.
3. Record received responses; if the user cannot answer now, mark the corresponding AC as `PENDING` and include it in the "Pending Questions" section of the final document.
4. Do not invent answers — if something is pending, it is explicitly pending.

### Step 5: Define DoD and out-of-scope

1. **Definition of Done** — objective checklist:
   - All ACs have a corresponding test (traceability `AC-N`)
   - Gate 2 approved
   - Documentation in `.ahrena/issues/{n}/` complete
   - ADR(s) created if there was a relevant architectural decision
   - PR approved by at least 1 reviewer

2. **Out of scope** — explicit list of what will **not** be done in this iteration:
   - Extract from the brief and from interaction with the user
   - Each out-of-scope item should have a justification or a link to a future issue

### Step 6: Persist to `.ahrena/issues/{n}/02-requirements.md`

Document structure:

```markdown
# Requirements — Issue #{n}: {title}

- **Reference:** [Phase 1 brief](./01-brief.md)
- **Date:** {YYYY-MM-DD}

## Acceptance Criteria

### AC-1: {short title}

- **Given** {precondition}
- **When** {action}
- **Then** {result}

### AC-2: {short title}

...

## Definition of Done

- [ ] All ACs above have at least one test with `AC-N` marking
- [ ] Gate 2 (`kata-quality-gate`) approved
- [ ] Complete documentation in `.ahrena/issues/{n}/`
- [ ] ADR(s) created if applicable in `docs/adr/`
- [ ] PR approved by at least 1 reviewer

## Out of Scope

- **{Item 1}:** {justification or link to future issue}
- **{Item 2}:** {justification or link to future issue}

## Pending Questions

- [ ] {Question 1} — awaiting response from @{user}
- [ ] {Question 2} — awaiting response from @{user}

## Next Phase

Phase 3: architectural design (`kata-architecture-brief`).
```

### Step 7: Update checkpoint

1. Update `.ahrena/workflow/issue-{n}/checkpoint.md` with:
   - completed phase: 2
   - next phase: 3
   - reference: `.ahrena/issues/{n}/02-requirements.md`
   - total number of ACs
   - pending questions (if any)
2. Inform `warrior-athena`.

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Requirements document | Markdown with numbered ACs | `.ahrena/issues/{n}/02-requirements.md` |
| Updated checkpoint | Markdown | `.ahrena/workflow/issue-{n}/checkpoint.md` |
| User questions (if any) | Structured text | Response to the orchestrator |

## Restrictions

- **ACs must be testable:** do not accept vague ACs ("the system must be fast"); always with an observable metric.
- **Continuous numbering:** `AC-1`, `AC-2`, `AC-3`... with no gaps; removed ACs stay as `AC-N: (removed — see note)` to preserve numbering across iterations.
- **No inference of undocumented requirements:** if it is not in the brief nor confirmed by the user, it goes to "Pending Questions".
- **Fixed destination:** `.ahrena/issues/{n}/02-requirements.md` (per `lex-issue-driven`).

## References

- `lex-issue-driven` — laws of the flow
- `codex-issue-workflow` — flow structure and traceability convention
- `kata-issue-analysis` — predecessor kata (Phase 1)
- `kata-architecture-brief` — successor kata (Phase 3)
