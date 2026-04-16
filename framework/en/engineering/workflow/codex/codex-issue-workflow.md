# Codex: Issue-Driven Development Workflow

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Structure, phases, gates, and artifacts of the issue-driven development flow orchestrated by `warrior-athena`

## Overview

This Codex is the operational reference for the Ahrena **Issue-Driven Development** flow. It defines the 7 process phases, the 2 quality gates, the format of intermediate artifacts, the traceability convention between acceptance criteria and tests, the ADR (Architecture Decision Record) format, and the documentation structure under `docs/`. Consulted by `warrior-athena` and by all katas in the `engineering/workflow/` clade.

## Context

- **Domain:** feature and bugfix delivery flow starting from GitHub issues, orchestrated via `warrior-athena`.
- **Audience:** `warrior-athena`, katas in the `engineering/workflow/` clade, and delegated specialist warriors (Apollo, Daedalus, Kronos).
- **Updates:** when phases are added/removed, when Gate 2 criteria change, or when the `docs/` structure evolves.

## Content

### The 7 phases of the flow

| # | Phase | Main kata | Output |
|:-:|---|---|---|
| 1 | Issue analysis | `kata-issue-analysis` | `docs/issues/issue-{n}/01-brief.md` |
| 2 | Requirements elicitation | `kata-requirements-brief` | `docs/issues/issue-{n}/02-requirements.md` |
| 3 | Architectural design | `kata-architecture-brief` (+ `kata-adr-write` if applicable) | `docs/issues/issue-{n}/03-architecture.md` + `docs/adr/ADR-*` |
| 4 | Implementation | delegates to `warrior-apollo` → `kata-python-implement` (Python) | code + tests marked with `AC-N` |
| 5 | Security review | `kata-security-review` | `docs/issues/issue-{n}/05-security-review.md` |
| 6 | Quality gate | `kata-quality-gate` | `docs/issues/issue-{n}/06-quality-report.md` |
| 7 | PR preparation | `kata-pr-prepare` | GitHub PR URL |

### The 2 gates

**Gate 1 — Scope Approval** (between Phase 3 and Phase 4)

- Executed by: `warrior-athena`
- Presents to the human: brief + ACs + architecture + proposed ADRs
- Pass criterion: explicit human approval
- On failure: flow stopped or returns to Phase 1/2/3 with feedback

**Gate 2 — Implementation Quality** (between Phase 6 and Phase 7)

- Executed by: `kata-quality-gate`
- 6 verifications (all ✅ to pass):

| # | Verification | How |
|:-:|---|---|
| 1 | Bidirectional AC → test traceability | Parse tests for `AC-N` + cross-check with Phase 2 ACs |
| 2 | Scope creep check | `git diff` vs. components declared in Phase 3 |
| 3 | Best practices (applicable Lexis) | Checklist per Lexis (see table below) |
| 4 | Tests executed | `pytest` (or equivalent) without failures |
| 5 | Coverage | `pytest --cov` ≥ `quality.coverage_threshold` in `.directives` |
| 6 | Types | `mypy --strict` without new errors |

- On failure: returns to Phase 4 (Apollo) with a detailed report; the human may choose to expand ACs (new Gate 1 iteration) if the issue is justifiable scope creep.

### Best practices verified at Gate 2

| Lexis | Verification |
|---|---|
| `lex-python-typing` | `mypy --strict` without errors |
| `lex-python-testing` | All public functions have tests |
| `lex-python-security` | No hardcoded credentials; inputs validated |
| `lex-python-immutability` | No mutation of shared structures |
| `lex-python-error-handling` | No `except: pass` or silent swallowing |
| `lex-conventional-commits` | Commits in `type(scope): message` format |

### Documentation structure under `docs/`

```
docs/
├── adr/
│   ├── ADR-001-use-event-sourcing-for-ledger.md
│   ├── ADR-002-migrate-to-fastapi.md
│   └── ...
└── issues/
    └── issue-{n}/
        ├── 01-brief.md
        ├── 02-requirements.md
        ├── 03-architecture.md
        ├── 05-security-review.md
        └── 06-quality-report.md
```

### Ephemeral state under `.ahrena/workflow/`

```
.ahrena/workflow/issue-{n}/
└── checkpoint.md       # Handoff context between phases
```

### AC ↔ test traceability convention

Each AC in Phase 2 is numbered (`AC-1`, `AC-2`, ...). Each new test in Phase 4 **must** reference the AC(s) it covers, in one of these forms:

**Form 1 — test name:**
```python
def test_create_refund_returns_201_AC_1():
    ...
```

**Form 2 — docstring:**
```python
def test_refund_idempotency():
    """AC-2: repeated calls with the same Idempotency-Key return the same result."""
    ...
```

**Form 3 — pytest marker:**
```python
@pytest.mark.ac("AC-3")
def test_refund_audit_log():
    ...
```

`kata-quality-gate` uses a regex to extract the references and cross-checks against the AC list. There is no automatic coercion — it is the implementer's responsibility (Apollo or other warrior) to mark tests correctly.

### ADR format (simplified MADR)

```markdown
# ADR-{n}: {Short title}

- **Status:** proposed | accepted | deprecated | superseded by ADR-XXX
- **Date:** {YYYY-MM-DD}
- **Issue:** #{issue-number}

## Context

{problem or force that motivated the decision}

## Decision

{the decision made, in active voice}

## Consequences

### Positive
- ...

### Negative
- ...

### Neutral
- ...

## Alternatives Considered

- **{Alternative A}:** rejected because ...
- **{Alternative B}:** rejected because ...
```

**Numbering:** `ADR-{n}` is globally sequential under `docs/adr/`. `kata-adr-write` detects the next number by listing existing files.

### When to generate ADR (checklist)

| Situation | Generate ADR? |
|---|:-:|
| New technology choice (framework, library) | ✅ Yes |
| Deviation from an existing pattern in the codebase | ✅ Yes |
| Significant trade-off between alternatives | ✅ Yes |
| Decision affecting multiple components | ✅ Yes |
| Decision affecting an external contract (API, event) | ✅ Yes |
| Localized bug fix without pattern change | ❌ No |
| Localized refactor following the existing pattern | ❌ No |
| Adding an endpoint following the codebase pattern | ❌ No |

### Delegation to specialist warriors

`warrior-athena` **does not implement** Phase 4 (code) nor Phase 3 when it involves APIs/events. Instead, it delegates:

| Situation | Delegates to | Via |
|---|---|---|
| Feature involves REST API | `warrior-daedalus` | `kata-api-design-oas` |
| Feature involves events (CloudEvents) | `warrior-kronos` | `kata-events-doc` |
| Feature involves AWS infrastructure | `warrior-atlas` | `kata-aws-design` |
| Python implementation | `warrior-apollo` | `kata-python-implement` |
| Frontend implementation | `warrior-hephaestus` | `kata-frontend-implement` |

Handoff happens via `.ahrena/workflow/issue-{n}/checkpoint.md` — Athena writes the necessary context, invokes the specialist warrior, and resumes orchestration after completion.

### Cry input mapping

`/cry-implement-issue` accepts as arguments:

```
/cry-implement-issue <issue-number> [<owner>/<repo>]
```

- `<issue-number>` (required): GitHub issue number.
- `<owner>/<repo>` (optional): target repository; defaults to the current project repo (detected via git remote).

## References

- `lex-issue-driven` — unbreakable laws of the Issue-Driven flow
- `warrior-athena` — flow orchestrator
- `cry-implement-issue` — entry point
- `kata-issue-analysis`, `kata-requirements-brief`, `kata-architecture-brief`, `kata-adr-write`, `kata-security-review`, `kata-quality-gate`, `kata-pr-prepare` — flow katas
- `kata-mcp-github-read`, `kata-mcp-notion-read` — external context reading
- `lex-mcp`, `codex-mcp-github`, `codex-mcp-notion` — MCP usage
- `warrior-apollo`, `warrior-daedalus`, `warrior-kronos`, `warrior-hephaestus`, `warrior-atlas` — delegated specialists
- [MADR — Markdown Architectural Decision Records](https://adr.github.io/madr/)
