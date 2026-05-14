# Lexis: No Silent Tech Debt

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Comments and sections left in code or documentation during an active Plan execution

## Purpose

Comments such as `# TODO`, `# FIXME`, `# XXX`, `# follow-up`, `# later`, `# revisit` and documentation sections like `## TODO`, `## Follow-up`, `## Out of scope (to revisit)` are markers of silent tech debt: they record that something was left for later, but do not connect that "later" to a trackable Issue or Plan. The result is entropy: the debt accumulates, no one is accountable, and the user discovers it weeks later when the debt becomes an incident.

The Ahrena framework treats every tangential finding as a **deliberate decision**: the agent PAUSES, surfaces it to the human, and offers three explicit paths — expand the current Plan, open a new Plan under the same parent Issue, or open a new parent capability Issue. None of these paths is "leave a TODO".

## Law

> **During the execution of an active Plan (status `development`), committing code with `# TODO`, `// TODO`, `# FIXME`, `# XXX`, `# follow-up`, `# later`, `# revisit` comments (or equivalent variants in other languages) OR committing documentation with `## TODO`, `## Follow-up`, `## Out of scope (to revisit)` sections, without those markers referencing a trackable Issue or Plan (format `# TODO(#NNN): ...` or equivalent), is FORBIDDEN. Tangential findings identified during execution MUST be surfaced to the human with three explicit options: (a) expand the current Plan scope, (b) open a new Plan sub-issue under the same parent Issue, (c) open a new parent capability Issue.**

## Coverage

- **Applies to:** every application code (Python, TypeScript/JavaScript, Go, Swift, Kotlin, Dart) and every documentation (Markdown under `docs/`, `README.md`, structured code comments) committed via a Plan in `status: development`
- **Bound agents:** `warrior-athena`, `warrior-apollo`, `warrior-hephaestus`, `warrior-iris`, `warrior-claudionor`, and any warrior that executes code during an active Plan
- **Declared exceptions:** (i) `# WHY: ...` comments explaining non-obvious decision (lineage, not debt); (ii) `pytest.mark.xfail(reason="bug:#N")` with trackable Issue number; (iii) `<!-- not-flushed -->` blocks in provider cache (`.claude/plans/`, `.cursor/plans/`) — transient scratch, not canonical

## Prospective Applicability

This Lex applies prospectively: existing `# TODO`/`# FIXME`/`# follow-up` comments in historical code of projects that adopted Ahrena before this Lex are **not** retroactively blocked. The lint detects only markers added or modified in the current PR diff. Migration of historical debt is the work of a dedicated Plan, surfaced when relevant to the current Plan's scope.

<HARD-GATE>
Every agent MUST NOT commit code or documentation containing
markers `# TODO`, `// TODO`, `# FIXME`, `# XXX`, `# follow-up`,
`# later`, `# revisit`, `## TODO`, `## Follow-up`, `## Out of scope`
without a reference to a trackable Issue or Plan.

Mandatory preconditions to commit such markers:
  (a) The marker references a trackable Issue/Plan (e.g., `# TODO(#NNN): description`)
  (b) Or the finding was surfaced to the human with 3 explicit options (expand Plan, open new Plan, open new Issue)
  (c) And the human confirmed the decision in writing (session response or Issue comment)

This rule applies to EVERY Plan in `status: development`, regardless of:
  - "it's just one line"
  - "the user didn't ask but will need it"
  - "it's tech debt, not feature"
  - "it's only a comment, nobody reads TODOs"

Declared exceptions (not silent):
  - `# WHY: ...` comments explaining a non-obvious decision (lineage)
  - `pytest.mark.xfail(reason="bug:#N")` with trackable Issue number
  - `<!-- not-flushed -->` blocks in plan provider cache
  - Pre-existing markers in historical code, outside the current PR diff
</HARD-GATE>

## Tangential Finding Protocol

When identifying a finding outside the current Plan's declared scope during execution, the agent MUST:

1. PAUSE the current implementation
2. Present to the human: finding description, affected scope, estimated cost of handling now vs. later
3. Offer three discrete options:
   - **(a) Expand the current Plan** — if trivial and directly related to the current scope; requires updating the Plan sub-issue body
   - **(b) Open a new Plan sub-issue** — if material but separable, still under the same parent Issue (User Story / Bug / Tech Task)
   - **(c) Open a new parent Issue** — if it constitutes a new capability, not derived from the current parent Issue
4. Record the human's decision in the corresponding Issue/Plan before resuming
5. Never implicitly accept a silent TODO

## Examples

### Correct

```python
# WHY: integer arithmetic on cents avoids floating-point error in money math
fee_cents = int(amount_cents * Decimal("0.015"))

# TODO(#172): switch to bank-specific fee table once spec arrives
return fee_cents
```

```python
@pytest.mark.xfail(reason="bug:#185 — race condition in retry path")
def test_concurrent_retries(): ...
```

### Incorrect

```python
# TODO: handle edge case later                    # FORBIDDEN — no #N reference
def parse_value(raw: str) -> int:
    return int(raw)

# FIXME: this is broken for negative numbers      # FORBIDDEN — silent
def calc(x): return x * 2

# XXX: refactor when we have time                 # FORBIDDEN — silent
```

```markdown
## Out of scope (to revisit)                      <!-- FORBIDDEN — no Issue/Plan -->
- Migration of legacy plans under docs/
- Cleanup of orphan worktrees
```

## Automated Validation

- **Tool:** ripgrep pre-commit hook running `rg -n '(^|\s)(# |// |## )(TODO|FIXME|XXX|follow-up|later|revisit)(?!\(#\d+\))'` on the staged diff; extension of `kata-quality-gate` (Check 4 or new check) applying the same pattern to the PR diff
- **When:** local pre-commit + Gate 2 of the Issue-Driven flow on every PR
- **Metric:** 0 silent debt markers added/modified in the PR diff; 100% of tangential findings during execution surfaced to the human with 3 explicit options
