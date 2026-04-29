---
description: "BDD Validation (Phase 8). Engineering — Quality. Shortcut that invokes warrior-themis to run Phase 8 of the Issue-Driven flow (scenario design + validation against the implementation) and return the go"
---

# Cry: BDD Validation (Phase 8)

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Engineering — Quality. Shortcut that invokes `warrior-themis` to run Phase 8 of the Issue-Driven flow (scenario design + validation against the implementation) and return the `go | no-go` decision for Gate 3.

## Usage

```
/cry-bdd-validate <issue-number> [<owner>/<repo>]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `issue-number` | Yes | GitHub issue number | `42` |
| `<owner>/<repo>` | No | Target repository; defaults to the one detected via `git remote` | `guardiafinance/ahrena` |

## Prerequisites

- `github` listed in `mcp.servers` in `.ahrena/.directives` (per `lex-mcp`)
- `notion` in `mcp.servers` when the Issue references Notion pages
- Environment variables: `GITHUB_PAT` (required), `NOTION_API_KEY` (when applicable)
- Phases 1-3 of the Issue-Driven flow complete: `01-brief.md`, `02-requirements.md`, `03-architecture.md` in `docs/issues/issue-{n}/`
- **Recommended:** Gate 2 with `go` decision (`06-quality-report.md`); when missing or `no-go`, the Cry warns and asks for confirmation before proceeding

## What the Command Does

1. Reads `.ahrena/.directives`.
2. Verifies prerequisites (Phase 1-3 artifacts and Gate 2 status).
3. Invokes **warrior-themis** with the issue number and repository.
4. `warrior-themis` runs `kata-bdd-scenarios-design` (Phase 8.1) — blind to code:
   - Reads allowed sources (Issue, Notion, flow artifacts)
   - Produces `docs/issues/issue-{n}/07-bdd-scenarios.md`
5. `warrior-themis` runs `kata-bdd-validate-implementation` (Phase 8.2) — with test reading:
   - Maps each `SCN-{N}` to existing tests
   - Checks for BDD step-runner coupling in the manifests
   - Produces `docs/issues/issue-{n}/08-bdd-validation-report.md`
6. Reports the `go | no-go` decision for Gate 3 and, when `no-go`, lists next actions with owner and level.

## Prompt Template

```
Context:
- Issue: #{{issue-number}}
- Repository: {{<owner>/<repo>}} (or detected via git remote)

Task:
Act as warrior-themis and run Phase 8 of the Issue-Driven flow for issue
#{{issue-number}}, closing with the go | no-go decision for Gate 3.

Execute in strict order:

1. Verify preconditions: Phase 1-3 artifacts present in docs/issues/issue-{n}/.
2. Check Gate 2 status (06-quality-report.md). When missing or no-go, alert and ask whether to proceed.
3. Phase 8.1 — kata-bdd-scenarios-design:
   - Read only allowed sources (per lex-bdd-spec-only-sources).
   - Produce 07-bdd-scenarios.md with frontmatter declaring sources and AC coverage.
   - Apply declarative format (per lex-bdd-gherkin-format) and self-lint via codex-gherkin regex.
4. Phase 8.2 — kata-bdd-validate-implementation:
   - Index repository tests by SCN-{N} reference.
   - Check manifests against the forbidden step-runner list (lex-bdd-no-framework-coupling).
   - Produce 08-bdd-validation-report.md with classification (covered | partial | missing).
   - Emit go | no-go decision.
5. Update the checkpoint at .ahrena/workflow/issue-{n}/checkpoint.md.
6. Report to the user: decision, counts (covered/partial/missing), and next-actions table.

Strictly respect the BDD Lexis: blind to code in Phase 8.1, declarative Gherkin format,
no step-runner, mandatory SCN-{N} traceability.
```

## Sample Invocation

**Input:**

```
/cry-bdd-validate 42 guardiafinance/ahrena
```

**Expected output:**

```
Phase 8 — Issue #42

Phase 8.1 (scenarios design, blind to code):
✓ 07-bdd-scenarios.md produced (6 scenarios, 4 ACs covered)

Phase 8.2 (test mapping):
✓ 08-bdd-validation-report.md produced
  - covered: 4
  - partial: 1 (SCN-5 @nfr at unit level)
  - missing: 1 (SCN-6 @nfr idempotency)
  - framework coupling: clean

Gate 3 decision: NO-GO

Next actions:
| Gap   | Action                                  | Owner          | Level       |
| SCN-5 | Add integration test measuring latency  | warrior-apollo | integration |
| SCN-6 | Create idempotency test                 | warrior-apollo | integration |

Checkpoint updated.
```

## Constraints

- **Does not skip Gate 2:** if Gate 2 returned `no-go` or is missing, the Cry warns and asks for confirmation before proceeding (Phase 8 makes most sense after Gate 2 closes).
- **Does not implement tests:** when there is a gap, the Cry returns `no-go` with suggested actions — implementation of missing tests is delegated in a follow-up iteration.
- **Canonical output:** `07-bdd-scenarios.md` and `08-bdd-validation-report.md` in `docs/issues/issue-{n}/`; never in another path.
- **No invention:** if the Issue is incomplete for any AC, the Cry returns with ACs marked `BLOCKED` and routes back to source (it does not consult code to fill in).

## Difference from Kata

| Aspect | Cry `cry-bdd-validate` | Katas `kata-bdd-*` |
|---|---|---|
| **Nature** | Invocation shortcut | Detailed procedure |
| **Scope** | Triggers `warrior-themis` | Executed by the Warrior |
| **Complexity** | Low (one sentence) | High (dozens of steps) |

## Related Cries and Warriors

- **warrior-themis** — Warrior invoked by this Cry; orchestrates the Phase 8 Katas
- **warrior-athena** — When this Cry is part of the full Issue-Driven flow (`/cry-implement-issue`), Athena delegates Phase 8 and this Cry can be invoked standalone as a shortcut outside the flow
- **warrior-apollo / warrior-hephaestus / warrior-iris** — Receive gap actions when the result is `no-go`
