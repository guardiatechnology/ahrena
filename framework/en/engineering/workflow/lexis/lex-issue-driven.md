# Lexis: Issue-Driven Development

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Feature and bugfix development flow driven by GitHub issues in the Ahrena framework

## Purpose

In projects that adopt the Issue-Driven Development flow (orchestrated by `warrior-athena`), each feature or bugfix starts from a GitHub issue and goes through mandatory phases of analysis, design, implementation, and validation. Without firm rules, this flow loses integrity: gates are skipped, acceptance criteria become optional, architectural decisions are not recorded, and the produced documentation scatters across inconsistent locations.

This Lexis exists to ensure that **every implementation has traceability from the original issue to the final PR**, that **quality gates are not bypassed**, that **relevant architectural decisions are recorded as ADRs**, and that **all flow-produced documentation is structured under `docs/`**.

## Law

> **Every implementation conducted by `warrior-athena` MUST originate from an existing issue, pass through both Gates (Scope and Quality), respect bidirectional traceability between acceptance criteria and tests, record relevant architectural decisions as ADRs in `docs/adr/`, and produce all public flow documentation in `.ahrena/issues/{n}/`.**

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

### 5. Phase artifacts in `.ahrena/issues/`

The agent **MUST** structure the Issue-Driven flow Phase artifacts in `.ahrena/issues/{n}/`:

1. `.ahrena/issues/{n}/01-brief.md` — issue analysis (Phase 1)
2. `.ahrena/issues/{n}/02-requirements.md` — numbered ACs (Phase 2)
3. `.ahrena/issues/{n}/03-architecture.md` — design (Phase 3)
4. `.ahrena/issues/{n}/05-security-review.md` — security review (Phase 5)
5. `.ahrena/issues/{n}/06-quality-report.md` — Gate 2 report (Phase 6)
6. `docs/adr/ADR-{n}-*.md` — ADRs when applicable (ADRs remain in `docs/` because they are product documentation, not operational)

**Transition window:** during 1 release after  merges, the agent MUST accept **both** paths as valid — `.ahrena/issues/{n}/` (new, canonical) and `.ahrena/issues/issue-{n}/` (legacy). After the following release, Gate 2 (`kata-quality-gate`) fails finding files in `.ahrena/issues/issue-{n}/` — forcing migration via `git mv .ahrena/issues/issue-{n} .ahrena/issues/{n}`.

Ephemeral orchestration state (checkpoint between phases) may go to `.ahrena/workflow/issue-{n}/checkpoint.md`, **never** under `.ahrena/issues/` nor `docs/`. The checkpoint **MUST** use versioned YAML front-matter (see Rule 7).

### 7. Versioned checkpoint schema

The agent **MUST** keep the checkpoint at `.ahrena/workflow/issue-{n}/checkpoint.md` with **structured YAML front-matter** containing at minimum:

```yaml
---
schema_version: 1
issue: 42
repo: guardiatechnology/ahrena
phase_completed: 3
phase_next: 4
artifacts:
  brief: .ahrena/issues/42/01-brief.md
  requirements: .ahrena/issues/42/02-requirements.md
  architecture: .ahrena/issues/42/03-architecture.md
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
    layer: 1                          # optional; present only in flows with stack
# Optional block. Present only when Phase 3 proposed layered
# decomposition and the human approved at Gate 1. Absence = single PR
# flow (default behavior; preserves schema_version 1).
stack:
  approved: false                     # becomes true after Gate 1 approves the decomposition
  tool: vanilla                       # echo of .directives.stacked_prs.tool (vanilla | gs)
  decomposition:
    - layer: 1
      slug: schema
      covers_acs: [AC-1, AC-2]
      components: ["db/migrations/*", "models/*"]
      status: pending                 # pending | in-progress | submitted | merged
      pr: null                        # owner/repo#N when submitted
    - layer: 2
      slug: api
      covers_acs: [AC-3, AC-4]
      components: ["api/routers/*", "use_cases/*"]
      status: pending
      pr: null
updated_at: "2026-04-16T15:00:00Z"
---

# Narrative notes (optional, for human context)
```

Content after `---` may contain free-form prose for human consumption, but the operational state **MUST** live in the front-matter. Unknown fields are preserved; mandatory fields removed invalidate the checkpoint and force manual reconstruction.

### 8. Delegation protocol (state machine)

When `warrior-athena` delegates a phase to a specialist warrior (Apollo, Hephaestus, Daedalus, Kronos, Atlas, Hera, Hestia, Demeter, Iris), the handoff **MUST** follow a state machine captured in the checkpoint:

```
delegated → running → completed | failed | timed-out
```

Rules:

1. **`delegated`**: Athena writes the delegation entry in the `checkpoint.md` front-matter (warrior, kata, input refs, `started_at`). The specialist is invoked.
2. **`running`**: the specialist acknowledges by updating the entry to `status: running` at the first step. If the agent cannot acknowledge within 60 seconds of invocation, the delegation is treated as `timed-out`.
3. **`completed`**: the specialist finishes and writes `output_refs: [...]` + `completed_at`; status flips to `completed`. Athena resumes from the checkpoint.
4. **`failed`**: the specialist records an explicit reason + partial outputs (if any). Athena presents the failure to the human and asks for direction (retry, escalate, abandon).
5. **`timed-out`**: inferred by Athena when there is no status update within the configured deadline (default: 30 min for `kata-*-implement`; 10 min for short katas). Treated like `failed` — the human decides.

Athena **NEVER** silently re-invokes a delegation in `running` or `completed`. Re-invocation after `failed`/`timed-out` **MUST** create a new delegation entry (preserving the old one as an audit trail) — never mutate the history.

The delegation entry format is defined in Rule 7 (`delegations:` list); timestamps and statuses are the source of truth for orchestration state.

### 9. Checkpoint stays slim

The checkpoint file is re-read at every phase transition. To keep token consumption predictable, the checkpoint **MUST**:

- Contain only **active operational state** (current phase, last delegation, gate outcomes, artifact pointers).
- **Not duplicate content** from `.ahrena/issues/{n}/*.md` — those are the durable narrative; the checkpoint carries references (paths), not copies.
- **Not accumulate history beyond the last failed/timed-out delegation kept for audit** (older history belongs to the issue's narrative files, not the checkpoint).

Target size: under ~2 KB after the full flow. If the checkpoint exceeds 5 KB, the agent **MUST** prune historical entries before continuing; pruned content goes to a sibling `history.md` (optional) or is discarded if already captured in `.ahrena/issues/{n}/`.

### 6. Scope creep is a block, not a warning

Gate 2 **MUST** fail if:

1. Modified files are outside the scope declared in Phase 3.
2. New public functions or classes are not justified by any AC.

When detected, the agent **MUST** present two options to the user:
- Expand the ACs (new Gate 1 iteration) to cover the additional code.
- Remove the out-of-scope code from the current PR and open a new issue for it.

In flows with `stack.approved: true`, the scope of each scope-creep check is the **current layer**, not the entire stack (see Rule 11).

### 10. Decomposition into stacked PRs in Phase 3

During Phase 3 (Architecture), `warrior-athena` **MUST** consult the canonical Decision Checklist of [`codex-stacked-prs`](../../../_foundation/contributing/codex/codex-stacked-prs.md) (section 2) against the declared scope and the numbered ACs in Phase 2:

1. **Evaluate high signals and anti-signals** per the checklist (≥ 3 high signals AND 0 anti-signals → propose stack; otherwise, single PR).
2. **If the checklist approves:** record a `## Stacked PR Decomposition` section in `.ahrena/issues/{n}/03-architecture.md` containing:
   - Layer table with columns `Layer | Slug | Covered ACs | Touched components | Review-independence justification`
   - Selected tool (lookup in `.directives.stacked_prs.tool`; default `vanilla`)
   - Explicit AC ↔ layer mapping (each AC belongs to exactly one layer)
3. **If the checklist rejects:** record `Single PR — checklist not met` in the same section, citing the evaluated signals; follow the standard single-PR flow.

The proposed decomposition **MUST NOT** be applied before human approval at Gate 1. Athena presents the decomposition as part of the design and waits for review.

The tool choice (`vanilla` vs. `gs`) is the project's decision via `.directives` — Athena only reads the value; never modifies the directive. When `stacked_prs.tool: gs` is configured but `git-spice` is not available in the environment, `kata-stacked-pr-create` falls back to the `vanilla` path with a warning.

### 11. Gate 2 per layer when there is an approved stack

When the checkpoint contains `stack.approved: true`, `kata-quality-gate` **MUST** run **per layer** before each PR is submitted, not once at the end:

1. **AC ↔ test traceability** (Rule 3) is evaluated only against the subset of ACs covered by the layer (`stack.decomposition[i].covers_acs`), not against the full set.
2. **Scope creep** (Rule 6) is evaluated only against the components declared by the layer in Phase 3 (`stack.decomposition[i].components`).
3. Each `decomposition[i].status` only transitions from `in-progress` to `submitted` when the 7 checks of `kata-quality-gate` pass for the layer.
4. Final aggregate validation (after all layers reach status `submitted`) confirms that **every** AC was covered by some layer (no orphan AC) and that **every** touched component was declared in some layer (no orphan component).

In flows without a stack (no `stack` block), Gate 2 runs once over the full scope (current behavior preserved).

### 12. PR routing in Phase 7

Phase 7 picks the PR creation kata based on the `stack` state:

| Checkpoint state | Invoked kata |
|---|---|
| `stack` absent OR `stack.approved: false` | `kata-contributing-pr` (single PR — current behavior) |
| `stack.approved: true` | `kata-stacked-pr-create` |

`kata-stacked-pr-create` reads `.directives.stacked_prs.tool` and follows the corresponding variant (vanilla or gs). Each PR created by the chain updates the corresponding entry in `stack.decomposition[i].pr` in the checkpoint, in the format `owner/repo#N`.

The umbrella issue reference rule (Rule 5 of `codex-stacked-prs`, section 1.2) is applied by `kata-stacked-pr-create`: intermediate layers use `Refs #N`; the last uses `Closes #N` to automatically close the issue on merge.

### 13. Direct delegation to Python specialists by declared `component`

When `.ahrena/issues/{n}/03-architecture.md` explicitly declares the `component` in the component table (values: `api`, `jobs`, `agents`, `ui`, `deployment`), `warrior-athena` **MAY** invoke the matching specialist directly in Phase 4, skipping the indirection level through `warrior-apollo` (router).

Routing table:

| `component` declared in Phase 3 | Warrior invoked in Phase 4 |
|---|---|
| `api` | `warrior-apollo-api` |
| `jobs` | `warrior-apollo-jobs` |
| `agents` | `warrior-apollo-agents` |
| `ui` | `warrior-hephaestus` |
| `deployment` | `warrior-atlas` |
| **transversal** (more than one value) or `component` **missing/ambiguous** | `warrior-apollo` (router) — decides or asks |

Rules:

1. **Unambiguous component:** Athena delegates to the specialist directly and records the delegation entry in `checkpoint.md` with the canonical specialist name (e.g., `warrior: warrior-apollo-api`).
2. **Transversal component:** when Phase 3 declares more than one `component` for the same feature (e.g., `api` + `jobs`), Athena can either (a) decompose into stacked PRs per layer (Rule 10) with one specialist per layer, or (b) invoke `warrior-apollo` (router) to coordinate multiple specialists in a single PR when the `codex-stacked-prs` checklist does not justify a stack.
3. **Missing or ambiguous component:** Athena invokes `warrior-apollo` (router), which applies a heuristic (text, paths) and, as a last resort, asks the human before delegating — without guessing.
4. **Legacy cries preserved:** `cry-python-implement`, `cry-python-review`, `cry-python-refactor`, `cry-python-debug` keep invoking `warrior-apollo` (router); the direct delegation to a specialist applies to the Issue-Driven flow conducted by Athena, not to external invocations via cry.
5. **Lexis and Codex consumed by the specialist:** Apollo-API consumes `docs/{context}/oas/openapi.yaml`; Apollo-Jobs consumes `docs/{context}/events/events.md`; Apollo-Agents consumes all 13 Hub & Spoke files under `docs/{context}/agents/{agent}/` + `docs/{context}/dooc/{agent}.md` + `docs/{context}/feature-agent-map.md` per `codex-agent-design-docs`.

Direct delegation does not change any other flow rule (Gates 1 and 2, AC ↔ test traceability, ADRs, scope creep, delegation state machine) — it is only a routing shortcut in Phase 4 when the `component` is clear.

## Coverage

- **Applies to:** every invocation of `/cry-implement-issue` and any activity conducted by `warrior-athena`.
- **Bound agents:** `warrior-athena` (orchestrator) and all warriors/katas delegated during the flow.
- **Exceptions:** None. Lexis admit no exceptions.

## Violation Consequences

1. **Gate skipped:** PR created without Gate 2 equals unreviewed code in production; blocks merge and requires reopening the flow from Phase 5.
2. **Broken traceability:** AC without test or test without AC invalidates the PR; requires correction before reopening Gate 2.
3. **Missing ADR:** an architectural decision without an ADR leaves the organization without a rationale history; the ADR must be written retroactively before merge.
4. **Documentation outside `docs/`:** breaks the audit pattern; files must be moved to the correct structure before merge.
5. **Undeclared scope creep:** code beyond scope is reverted or justified in a new Gate 1 iteration.

## Examples

### Correct

```
# Flow driven from an existing issue:
/cry-implement-issue 42 guardiatechnology/ahrena

# Athena reads issue #42, produces:
# .ahrena/issues/42/01-brief.md
# .ahrena/issues/42/02-requirements.md   (AC-1, AC-2, AC-3)
# .ahrena/issues/42/03-architecture.md
# docs/adr/ADR-007-use-fastapi-routers.md   (relevant decision)

# Awaits Gate 1 → human approves
# Apollo implements: each test references AC-N
# Gate 2 runs 6 checks, all ✅
# .ahrena/issues/42/06-quality-report.md records the result
# PR created with body referencing the above artifacts
```

```
# Flow with stacked PR approved at Gate 1:
/cry-implement-issue 64 guardiatechnology/ahrena

# Athena reads issue #64 (5 ACs, ~900 lines predicted, schema+API+UI):
#   Decision Checklist: 4 high signals, 0 anti-signals → proposes stack
# .ahrena/issues/64/03-architecture.md includes:
#   ## Stacked PR Decomposition
#     Layer 1 (schema):  AC-1, AC-2  — db/migrations/*, models/*
#     Layer 2 (api):     AC-3, AC-4  — routers/*, use_cases/*
#     Layer 3 (ui):      AC-5       — frontend/components/*
# Gate 1 approved → checkpoint records stack.approved: true
# Apollo implements Layer 1; Gate 2 runs against AC-1, AC-2 and layer 1 components → ✅ submitted
# Apollo implements Layer 2; Gate 2 runs against AC-3, AC-4 → ✅ submitted
# Hephaestus implements Layer 3; Gate 2 runs against AC-5 → ✅ submitted
# kata-stacked-pr-create creates 3 stacked PRs; last layer uses Closes #64
```

### Incorrect

```
# ❌ Athena starts the flow without an issue:
/cry-implement-issue "add refund"

# ❌ Human asks "skip Gate 1, it's already ok":
# (Gate 1 is mandatory — Athena must refuse)

# ❌ New test without AC link:
# def test_random_helper(): ...   (no AC-N docstring)

# ❌ ADR saved in the wrong place:
# .ahrena/workflow/issue-42/adr.md
# (correct path is docs/adr/ADR-{n}-*.md)

# ❌ Modifying a file outside the declared scope:
# (Gate 2 blocks; user decides between expanding ACs or opening a new issue)

# ❌ Athena proposes stack decomposition but starts Phase 4 without Gate 1 approval:
# (Decomposition requires explicit human approval; checkpoint must record stack.approved: true)

# ❌ Layer 2 starts before layer 1 reaches `submitted`:
# (Layers have sequential dependency; Athena delegates layer N+1 only after N transitions to submitted)
```

## Automated Validation

- **Tool:** `kata-quality-gate` (Gate 2) runs traceability, scope creep, and best practices checks before the PR; `scripts/validate.py` verifies the mandatory presence of artifacts under `.ahrena/issues/{n}/` when the flow completes. When the checkpoint contains `stack.approved: true`, `kata-quality-gate` runs per layer and the aggregate validation confirms AC and component coverage.
- **Timing:** Gate 1 (before Phase 4), Gate 2 (before each submitted layer in flows with stack; before Phase 7 in single PR flow).
- **Metric:** 100% of issues pass both gates; 100% of ACs have at least one test; 0 tests without a corresponding AC; 100% of relevant architectural decisions have an ADR under `docs/adr/`; 0 flows with `stack.approved: true` advancing from Phase 3 to Phase 4 without human approval at Gate 1.
