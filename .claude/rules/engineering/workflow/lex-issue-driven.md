---
paths:
  - "docs/issues/**"
  - ".ahrena/workflow/**"
---

# Lexis: Issue-Driven Development

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Feature and bugfix development flow driven by GitHub issues in the Ahrena framework

## Law

> **Every implementation conducted by `warrior-athena` MUST originate from an existing issue, pass through both Gates (Scope and Quality), respect bidirectional traceability between acceptance criteria and tests, record relevant architectural decisions as ADRs in `docs/adr/`, and produce all public flow documentation in `docs/issues/issue-{n}/`.**

## Rules

### 1. Issue as mandatory starting point

The agent **MUST**:

1. Require a reference to an existing issue (`owner/repo#number` or equivalent) before starting any phase of the flow.
2. Read the issue via `kata-mcp-github-read` in Phase 1.
3. If the issue does not exist or is empty, inform the user and stop — do not create the issue automatically nor infer the scope.

### 2. Gates cannot be skipped

The agent **MUST NOT**:

1. Advance from Phase 3 to Phase 4 without explicit human approval at Gate 1 (scope).
2. Create the PR in Phase 7 if Gate 2 (quality) did not result in `go`.
3. Mark Gate 2 items as met without actually running the verification (e.g., cannot claim "tests pass" without running `pytest`).

### 3. Bidirectional AC ↔ test traceability

For Gate 2 to pass:

1. **Each numbered acceptance criterion** from Phase 2 **MUST** have at least one test that covers it.
2. **Each new test** introduced in Phase 4 **MUST** be linked to at least one AC via the convention `AC-{N}` in the test name or docstring.
3. New tests without a corresponding AC are treated as **scope creep** and block the gate.

### 4. Mandatory ADRs for relevant architectural decisions

The agent **MUST** invoke `kata-adr-write` when Phase 3 identifies:

1. A new technology choice (framework, library, architectural pattern).
2. A deviation from an existing pattern in the codebase.
3. A significant trade-off between alternatives.
4. A decision that affects multiple components or external contracts.

The ADR **MUST** be saved at `docs/adr/ADR-{n}-{kebab-title}.md` in the simplified MADR format.

### 5. Documentation under `docs/`

The agent **MUST** structure all public flow documentation under `docs/`:

1. `docs/issues/issue-{n}/01-brief.md` — issue analysis (Phase 1)
2. `docs/issues/issue-{n}/02-requirements.md` — numbered ACs (Phase 2)
3. `docs/issues/issue-{n}/03-architecture.md` — design (Phase 3)
4. `docs/issues/issue-{n}/05-security-review.md` — security review (Phase 5)
5. `docs/issues/issue-{n}/06-quality-report.md` — Gate 2 report (Phase 6)
6. `docs/adr/ADR-{n}-*.md` — ADRs when applicable

Ephemeral orchestration state (checkpoint between phases) may go to `.ahrena/workflow/issue-{n}/checkpoint.md`, **never** under `docs/`. The checkpoint **MUST** use versioned YAML front-matter (see Rule 7).

### 7. Versioned checkpoint schema

The agent **MUST** keep the checkpoint at `.ahrena/workflow/issue-{n}/checkpoint.md` with **structured YAML front-matter** containing at minimum:

```yaml
---
schema_version: 1
issue: 42
repo: guardiafinance/ahrena
phase_completed: 3
phase_next: 4
artifacts:
  brief: docs/issues/issue-42/01-brief.md
  requirements: docs/issues/issue-42/02-requirements.md
  architecture: docs/issues/issue-42/03-architecture.md
adrs:
  - ADR-008-use-event-sourcing-for-refund-audit-trail.md
gate_1:
  status: approved | pending | rejected
  approved_at: "2026-04-16T14:30:00Z"
  approver: "@user"
gate_2:
  status: go | no-go | pending
  last_run_at: "..."
delegations:
  - warrior: warrior-daedalus
    kata: kata-api-design-oas
    status: completed | running | failed | timed-out
    started_at: "..."
    completed_at: "..."
    output_refs: ["docs/..."]
updated_at: "2026-04-16T15:00:00Z"
---

# Narrative notes (optional, for human context)
```

Content after `---` may contain free-form prose for human consumption, but operational state **MUST** live in the front-matter. Unknown fields are preserved; removing required fields invalidates the checkpoint and forces manual reconstruction.

### 8. Delegation protocol (status machine)

When `warrior-athena` delegates a phase to a specialist warrior (Apollo, Hephaestus, Daedalus, Kronos, Atlas, Hera, Hestia, Demeter, Iris), the handoff **MUST** follow a status machine captured in the checkpoint:

```
delegated → running → completed | failed | timed-out
```

Rules:

1. **`delegated`**: Athena writes the delegation entry in `checkpoint.md` front-matter (warrior, kata, input refs, `started_at`). Specialist is invoked.
2. **`running`**: specialist acknowledges by updating entry `status: running` at the earliest step. If the agent cannot acknowledge within 60 seconds of invocation, the delegation is considered `timed-out`.
3. **`completed`**: specialist finishes and writes `output_refs: [...]` + `completed_at` to the entry; status flips to `completed`. Athena resumes from checkpoint.
4. **`failed`**: specialist records explicit failure reason + partial outputs (if any). Athena presents the failure to the human and asks for direction (retry, escalate, abandon).
5. **`timed-out`**: inferred by Athena when no status update appears within the configured deadline (default: 30 minutes for `kata-*-implement`; 10 minutes for short katas). Treated like `failed` — human decides.

Athena **NEVER** silently re-invokes a delegation that is `running` or `completed`. Re-invocation after `failed`/`timed-out` **MUST** create a new delegation entry (preserving the old one as audit trail) — never mutate history.

The delegation entry format is defined in Rule 7 (`delegations:` list); timestamps and statuses are source of truth for orchestration state.

### 9. Checkpoint stays slim

The checkpoint file is re-read at every phase transition. To keep token consumption predictable, the checkpoint **MUST**:

- Contain only **active operational state** (current phase, last delegation, gate outcomes, artifact pointers).
- **Not duplicate content** from `docs/issues/issue-{n}/*.md` — those are the durable narrative; checkpoint carries references (paths), not copies.
- **Not accumulate history beyond the last failed/timed-out delegation kept for audit** (older history belongs in the issue narrative files, not the checkpoint).

Target size: under ~2 KB after the full flow. If the checkpoint exceeds 5 KB, the agent **MUST** prune historical entries before continuing; pruned content goes to a sibling `history.md` (optional) or is discarded if already captured in `docs/issues/issue-{n}/`.

### 6. Scope creep is a block, not a warning

Gate 2 **MUST** fail if:

1. Modified files are outside the scope declared in Phase 3.
2. New public functions or classes are not justified by any AC.

When detected, the agent **MUST** present two options to the user:
- Expand the ACs (new Gate 1 iteration) to cover the additional code.
- Remove the out-of-scope code from the current PR and open a new issue for it.

## Applicability

- **Applies to:** every invocation of `/cry-implement-issue` and any activity conducted by `warrior-athena`.
- **Bound agents:** `warrior-athena` (orchestrator) and all warriors/katas delegated during the flow.
- **Exceptions:** None. Lexis admit no exceptions.

## Examples

### Correct

```
# Flow driven from an existing issue:
/cry-implement-issue 42 guardiafinance/ahrena

# Athena reads issue #42, produces:
# docs/issues/issue-42/01-brief.md
# docs/issues/issue-42/02-requirements.md   (AC-1, AC-2, AC-3)
# docs/issues/issue-42/03-architecture.md
# docs/adr/ADR-007-use-fastapi-routers.md   (relevant decision)

# Awaits Gate 1 → human approves
# Apollo implements: each test references AC-N
# Gate 2 runs 6 checks, all ✅
# docs/issues/issue-42/06-quality-report.md records the result
# PR created with body referencing the above artifacts
```

### Incorrect

```
# ❌ Athena starts the flow without an issue:
/cry-implement-issue "add refund"

# ❌ Human asks "skip Gate 1, it's ok":
# (Gate 1 is mandatory — Athena must refuse)

# ❌ New test without AC link:
# def test_random_helper(): ...   (no AC-N docstring)

# ❌ ADR saved in the wrong place:
# .ahrena/workflow/issue-42/adr.md
# (correct path is docs/adr/ADR-{n}-*.md)

# ❌ Modifying a file outside the declared scope:
# (Gate 2 blocks; user decides between expanding ACs or opening a new issue)
```

## Automated Validation

- **Tool:** `kata-quality-gate` (Gate 2) runs traceability, scope creep, and best practices checks before the PR; `scripts/validate.py` verifies the mandatory presence of artifacts under `docs/issues/issue-{n}/` when the flow completes.
- **Timing:** Gate 1 (before Phase 4), Gate 2 (before Phase 7).
- **Metric:** 100% of issues pass both gates; 100% of ACs have at least one test; 0 tests without a corresponding AC; 100% of relevant architectural decisions have an ADR under `docs/adr/`.
