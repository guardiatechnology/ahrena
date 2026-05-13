# Codex: Issue-Driven Development Workflow

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Structure, phases, gates, and artifacts of the issue-driven development flow orchestrated by `warrior-athena`

## Content

### The 7 phases of the flow

| # | Phase | Main kata | Output |
|:-:|---|---|---|
| 1 | Issue analysis | `kata-issue-analysis` | `.ahrena/issues/{n}/01-brief.md` |
| 2 | Requirements elicitation | `kata-requirements-brief` | `.ahrena/issues/{n}/02-requirements.md` |
| 3 | Architectural design | `kata-architecture-brief` (+ `kata-adr-write` if applicable) | `.ahrena/issues/{n}/03-architecture.md` + `docs/adr/ADR-*` |
| 4 | Implementation | delegates to `warrior-apollo` → `kata-python-implement` (Python) | code + tests with `AC-N` marker |
| 5 | Security review | `kata-security-review` | `.ahrena/issues/{n}/05-security-review.md` |
| 6 | Quality gate | `kata-quality-gate` | `.ahrena/issues/{n}/06-quality-report.md` |
| 7 | PR preparation | `kata-pr-prepare` | PR URL on GitHub |

### The 2 gates

**Gate 1 — Scope Approval** (between Phase 3 and Phase 4)

- Executed by: `warrior-athena`
- Presents to the human: brief + ACs + architecture + proposed ADRs
- Pass criterion: explicit human approval
- If it fails: flow ends or returns to Phase 1/2/3 with feedback

**Gate 2 — Implementation Quality** (between Phase 6 and Phase 7)

- Executed by: `kata-quality-gate`
- 7 checks; result is `go` (all ✅ or `unverifiable` where not applicable), `no-go` (any ❌), or `go-with-caveats` (>2 `unverifiable`, human decides):

| # | Check | How |
|:-:|---|---|
| 1 | AC ↔ test traceability (bidirectional) | Canonical markers per stack (pytest marker, JS `@ac` tag); regex only as fallback |
| 2 | Scope creep check | `git diff` vs. components declared in Phase 3 |
| 3 | Best practices (Lexis applicable per stack) | Python/Frontend/IaC Lexis; cross-stack conventions |
| 4 | Executed tests | `pytest` / `yarn test` / stack-specific command |
| 5 | Coverage | `pytest --cov` ≥ `quality.coverage_threshold` in `.directives` |
| 6 | Types | `mypy --strict` / `tsc --noEmit` without new errors |
| 7 | Performance budget | Lighthouse/bundle (Frontend); benchmark p99 (Backend); Infracost (IaC) |

- If it fails: returns to Phase 4 (Apollo) with detailed report; the human may choose to expand ACs (new Gate 1 iteration) if the issue is justifiable scope creep.

### Best practices checked at Gate 2

| Lexis | Check |
|---|---|
| `lex-python-typing` | `mypy --strict` without errors |
| `lex-python-testing` | All public functions have a test |
| `lex-python-security` | No hardcoded credentials; validated inputs |
| `lex-python-immutability` | No mutation in shared structures |
| `lex-python-error-handling` | No `except: pass` or silent swallowing |
| `lex-conventional-commits` | Commits in `type(scope): message` format |

### Documentation structure in `docs/`

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

### Ephemeral state in `.ahrena/workflow/`

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

`kata-quality-gate` uses regex to extract the references and cross-checks them with the AC list. There is no automatic coercion — it is the implementer's (Apollo or another warrior) responsibility to mark correctly.

### ADR format (simplified MADR)

```markdown
# ADR-{n}: {Short title}

- **Status:** proposed | accepted | deprecated | superseded by ADR-XXX
- **Date:** {YYYY-MM-DD}
- **Issue:** #{issue-number}

## Decision

{the decision taken, in active voice}

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

**Numbering:** `ADR-{n}` is global sequential in `docs/adr/`. `kata-adr-write` detects the next number by listing existing files.

### When to generate an ADR (checklist)

| Situation | Generate ADR? |
|---|:-:|
| New technology choice (framework, library) | ✅ Yes |
| Deviation from an existing pattern in the codebase | ✅ Yes |
| Significant trade-off between alternatives | ✅ Yes |
| Decision that affects multiple components | ✅ Yes |
| Decision that affects external contract (API, event) | ✅ Yes |
| Point bug fix without pattern change | ❌ No |
| Localized refactor following existing pattern | ❌ No |
| Endpoint addition following codebase pattern | ❌ No |

### Delegation to specialist warriors

`warrior-athena` **does not implement** phases 4 (code) nor 3 (when it involves API/events). Instead, it delegates:

| Situation | Delegates to | Via |
|---|---|---|
| Feature involves REST API | `warrior-daedalus` | `kata-api-design-oas` |
| Feature involves events (CloudEvents) | `warrior-kronos` | `kata-events-doc` |
| Feature involves AWS infrastructure | `warrior-atlas` | `kata-aws-design` |
| Python implementation | `warrior-apollo` | `kata-python-implement` |
| Frontend implementation | `warrior-hephaestus` | `kata-frontend-implement` |

The handoff happens via `.ahrena/workflow/issue-{n}/checkpoint.md` — Athena writes the necessary context, invokes the specialist warrior, and resumes orchestration after completion.

### Cry input mapping

The `/cry-implement-issue` accepts the following arguments:

```
/cry-implement-issue <issue-number> [<owner>/<repo>]
```

- `<issue-number>` (required): GitHub issue number.
- `<owner>/<repo>` (optional): target repository; default is the current project repo (detected via git remote).
