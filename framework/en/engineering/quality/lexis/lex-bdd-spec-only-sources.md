# Lexis: BDD Scenarios Derived Exclusively from Specification Sources

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Engineering — Quality. Behavioral validation of features delivered through the Issue-Driven Development flow.

## Purpose

BDD validation only catches "we built the wrong thing" when scenarios are independent of the implementation. A scenario derived from the code can only describe what was built — never what was asked. This Lexis ensures scenarios act as a black-box behavioral contract: if the specification does not allow them to be written, the requirement is incomplete and must return to source before validation continues.

This Lexis exists to make **BDD validation capable of detecting divergence between what was asked and what was delivered**, and to prevent the agent from "completing" ambiguous specifications by looking at the produced code.

## Law

> **Gherkin scenarios produced for behavioral validation MUST be derived exclusively from the GitHub Issue (title, body, acceptance criteria, comments) and from the linked Notion pages. Reading, opening, grepping, or otherwise consulting the implementation source code (files under `src/`, `app/`, `lib/`, `tests/`, etc.) to discover, refine, or complete scenarios is FORBIDDEN. If the specification sources do not allow scenarios to be written, the agent MUST stop and request that the Issue be amended — never resort to the code as a shortcut.**

## Rules

### 1. Allowed sources

The agent producing scenarios **MAY** consult:

- The linked GitHub Issue (title, body, comments, labels).
- Notion pages referenced by the Issue or by the Issue-Driven flow artifacts.
- The flow artifacts themselves: `docs/issues/issue-{n}/01-brief.md`, `02-requirements.md`, `03-architecture.md`.
- ADRs in `docs/adr/` when explicitly referenced by the architecture.

### 2. Forbidden sources

The agent producing scenarios **MUST NOT**:

- Open files under `src/`, `app/`, `lib/`, `pkg/`, `internal/`, `tests/`, `spec/`, `__tests__/`, `cypress/`, `e2e/`, or stack-equivalent directories.
- Run `grep`/`rg`/`find` against implementation code.
- Ask another agent to explain the code in order to infer behavior.
- Inspect PRs, diffs, or commits of the feature under validation.

### 3. Source declaration in the artifact

The file `docs/issues/issue-{n}/07-bdd-scenarios.md` **MUST** declare, in YAML frontmatter, the set of sources consulted:

```yaml
---
issue: 42
repo: guardiafinance/ahrena
sources:
  github_issue: "guardiafinance/ahrena#42"
  notion_pages:
    - "https://www.notion.so/page-id-1"
    - "https://www.notion.so/page-id-2"
  flow_artifacts:
    - docs/issues/issue-42/01-brief.md
    - docs/issues/issue-42/02-requirements.md
generated_at: "2026-04-29T10:00:00Z"
---
```

Paths under `src/`, `app/`, `tests/`, etc. in this block invalidate the artifact.

### 4. Insufficient specification

If the allowed sources do **not** support writing complete scenarios for some acceptance criterion:

1. The agent **MUST** stop producing the artifact.
2. **MUST** open a comment on the Issue or a blocker block in `07-bdd-scenarios.md` listing the ambiguities.
3. **MUST NOT** consult the code to resolve the ambiguity.
4. The Issue **MUST** be amended (by the PM, engineering, design) and the flow resumed.

### 5. Independent verification

Validating the scenarios against the implementation (executed by `kata-bdd-validate-implementation`) **MAY** read the code — this is the stage that maps scenario ↔ existing test. Producing the scenarios (`kata-bdd-scenarios-design`) **MUST NOT**.

The separation between "designing scenarios" (blind to code) and "validating implementation" (with code access) is the spine of this Lexis.

## Coverage

- **Applies to:** every feature or bugfix that completed the Issue-Driven flow and entered Phase 8 (BDD Validation).
- **Bound agents:** `warrior-themis` (Phase 8 executor), `warrior-athena` (orchestrator that delegates), and any Kata invoked inside Phase 8.
- **Exceptions:** None. Lexis admit no exceptions.

## Consequences of Violation

1. **PR blocked:** Gate 3 (Behavioral) in `kata-quality-gate` fails when the frontmatter of `07-bdd-scenarios.md` references implementation paths or when the agent records code reads during Phase 8 design.
2. **Scenarios discarded:** scenarios produced with a detected violation are discarded; the artifact is regenerated from the allowed sources.
3. **Incomplete Issue becomes a process event:** repeated ambiguities trigger a Phase 2 review (`kata-requirements-brief`) — the problem is in the requirement, not in the validator.

## Examples

### Correct

```
warrior-themis is asked to validate issue #42.
1. Reads: docs/issues/issue-42/01-brief.md, 02-requirements.md.
2. Reads: GitHub Issue #42 (body + comments).
3. Reads: Notion pages referenced by the Issue.
4. Produces docs/issues/issue-42/07-bdd-scenarios.md with:
   - frontmatter declaring those 4 sources;
   - scenarios covering every numbered AC.
5. Does not open any file under src/.
```

### Incorrect

```
warrior-themis is asked to validate issue #42.
1. Reads the Phase 1-3 artifacts.
2. "To understand the refund flow", opens src/refund_service.py.
3. Writes scenarios based on the behavior observed in the code.

→ Violation. The scenarios now describe what was built, not what was
asked — they lose the ability to detect "we built the wrong thing".
```

## Automated Validation

- **Tool:** frontmatter lint on `07-bdd-scenarios.md` rejecting paths under `src/`, `app/`, `lib/`, `tests/`; `kata-bdd-scenarios-design` checklist requiring an explicit source declaration; review via `kata-quality-gate` Check 8 (BDD coverage).
- **When:** Phase 8 of the Issue-Driven flow (pre-PR), before `kata-pr-prepare`.
- **Metric:** 0 `07-bdd-scenarios.md` files referencing implementation paths; 100% of scenarios traceable to a declared specification source.

## References

- `lex-bdd-gherkin-format` — mandatory Gherkin format for scenarios
- `lex-bdd-no-framework-coupling` — test implementation without a BDD framework
- `lex-issue-driven` — Issue-Driven flow that precedes BDD validation
- `kata-bdd-scenarios-design` — scenario production procedure
- `kata-bdd-validate-implementation` — validation procedure against implementation
- `warrior-themis` — specialized BDD validation agent
