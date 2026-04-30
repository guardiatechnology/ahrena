# Codex: Behavior-Driven Development at Guardia

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** BDD methodology used in Guardia projects — when, why, and how scenarios are authored from business sources, mapped to tests, and maintained over time

## Overview

This Codex is the operational reference for **BDD scenario authoring and coverage** at Guardia. Consulted by `warrior-hera` when designing test plans, by agents executing `kata-bdd-create-scenarios` and `kata-bdd-validate-scenarios`, and by code reviewers checking that scenarios and tests stay aligned.

BDD here is **optional and standalone**. It is not a phase of the Issue-Driven flow. Teams adopt it for features where the business intent benefits from being captured in domain language before implementation begins. When adopted, `lex-bdd-scenarios` and `lex-bdd-coverage` apply.

## Context

- **Domain:** behavior specification through Gherkin scenarios derived from business sources (issue + Notion), with mapping to tests at any level via canonical markers.
- **Audience:** `warrior-hera`, agents authoring or validating scenarios, code reviewers.
- **Update:** when the test stack changes (new framework adopted), when the canonical marker convention evolves, when a project elects to adopt a Gherkin runner (project-level addendum, not framework default).

## Content

### Why BDD here, why standalone

The Issue-Driven flow already enforces numbered acceptance criteria with AC↔test traceability. BDD adds a **business-language layer** between the issue and the tests. It is useful when the gap between technical ACs and business intent is wide enough that scenarios capture intent more clearly than Given/When/Then ACs. For most issues this is overhead. For tier-1 features, complex domain rules, and regulated processes (payment, refund, ledger), it pays off.

Standalone, because it does not block teams that do not use it. `/cry-bdd-create-scenarios` and `/cry-bdd-validate-scenarios` are independent entry points that run before, after, or fully outside the Issue-Driven flow.

### Business-focused vs API/UI-focused — the difference

The contributing templates `user-story-for-api.md` and `user-story-for-frontend.md` already carry Gherkin scenarios, but those scenarios encode the **contract** (HTTP, UI surface). They are useful for contract testing and they stay in the issue. Business-focused scenarios encode the **intent** behind the contract.

| Aspect | API/UI scenario (template) | Business scenario (BDD) |
|---|---|---|
| Subject | The API/UI surface | The domain operation |
| Vocabulary | HTTP verb/path, status code, payload field, DOM selector | Actor, entity, business outcome |
| Audience | Backend/frontend reviewers, integrators | Product, domain experts, all engineers |
| Stability | Changes when the contract changes | Changes when the business rule changes |
| Test target | Contract test (E2E API, UI E2E) | Any level, wherever the rule lives |

Both forms coexist. The cry duplicates the API/UI scenario into a business form; it does not replace it.

### Gherkin conventions used here

Use only `Scenario`, `Given`, `When`, `Then`, `And`. Do not use `Background`, `Scenario Outline`, or `Examples` tables — they encourage technical drift and harder mappings. One observable behavior per scenario. Title each scenario with a sentence the product team would recognize.

```gherkin
Scenario: Customer requests a refund for an eligible payment
  Given a captured payment of 1000 BRL made by the customer in the last 30 days
  When the customer requests a refund for that payment
  Then a refund is recorded against the payment in pending state
  And the audit trail records the refund attempt with the requesting customer
```

Scenarios live in the issue body, between dedicated markers:

```
<!-- bdd:scenarios:start -->
## BDD Scenarios (Business)

Scenario: ...

Scenario: ...
<!-- bdd:scenarios:end -->
```

Re-runs of the authoring kata replace only this block, never anything else in the body.

### Source of truth

| Source | Role |
|---|---|
| GitHub issue body (`bdd:scenarios` block) | The canonical, mutable record. |
| Notion pages | Enrichment context (product strategy, prior decisions). Not where scenarios live. |
| Code (services, tests, OAS) | Forbidden source. Code reflects what was built; scenarios reflect what is wanted. |

### Test mapping conventions (full table)

`<scenario-slug>` is the kebab-case form of `Scenario: <title>`. Example: `Customer requests a refund for an eligible payment` → `customer-requests-a-refund-for-an-eligible-payment`.

| Stack | Canonical marker | Fallback (test name or docstring) |
|---|---|---|
| Python / pytest | `@bdd_scenario("scenario-slug")` decorator | `BDD: <title>` in docstring |
| JS/TS (Jest, Vitest) | `// @bdd_scenario scenario-slug` JSDoc tag, or `bddScenario("scenario-slug", () => { ... })` wrapper | `BDD: <title>` in test name |
| Go | `// bdd_scenario: scenario-slug` above `func TestXxx` | `BDD<Slug>` in func name |
| Generic | docstring or test name matching `BDD:\s*<title-or-slug>` | — |

A test may map to more than one scenario when it legitimately exercises multiple behaviors at once (rare; prefer one scenario per test).

### The `bdd_scenario` identifier

`bdd_scenario` is the canonical, grep-stable token across stacks. The framework does not ship the Python decorator or the JS/TS wrapper. Projects that adopt BDD define a small local helper so the call site stays clean.

Reference Python helper:

```python
# project/tests/conftest.py (or a small bdd.py utility)
import pytest

def bdd_scenario(slug: str):
    """Mark a test as covering a BDD scenario by its kebab-case slug."""
    return pytest.mark.bdd_scenario(slug)
```

Reference JS/TS helper:

```typescript
// tests/_helpers/bdd.ts
export function bddScenario(slug: string, body: () => void): void {
  // The slug surfaces in test reporting via the test name and via the
  // `// @bdd_scenario <slug>` JSDoc tag; either is sufficient for the
  // validation kata to pick the mapping up.
  body();
}
```

The validation kata recognizes the canonical token regardless of how the helper is implemented, as long as the scenario slug travels with it.

### What makes a good scenario

| Property | Detail |
|---|---|
| Single behavior | One Given/When/Then triple per scenario; multiple `And` lines for context are fine, but the assertion is single. |
| Observable outcome | `Then` describes something a stakeholder can verify (a record exists, a notification was sent, a balance changed). Internal state ("the cache was invalidated") is implementation detail and does not belong here. |
| Stable wording | Scenario titles are stable enough to map by slug. Renaming is a breaking change to traceability (Rule 6 of `lex-bdd-coverage`). |
| Domain vocabulary | A product manager understands every word. If parsing requires reading the API spec, rewrite. |

### Anti-patterns

| Anti-pattern | Why it's bad |
|---|---|
| Copying the API scenario verbatim into the business block | Defeats the purpose; both versions become noise. |
| Multiple `Then` outcomes per scenario | The scenario becomes a checklist; covering tests become unfocused; mapping becomes ambiguous. |
| Casual scenario renames | Breaks the slug mapping. Rename = treat as breaking change to traceability and update the markers in the same change. |
| Authoring scenarios from the codebase | Encodes what the system does, not what the business wants. Defeats BDD entirely. |
| Mandating a Gherkin runner | Adds tool weight without adding signal. Tests are the executable artifact; mapping is the contract. |
| Asserting on internal state | Scenarios talk about externally observable outcomes only. Internal state is an implementation choice. |

### Lifecycle of a scenario

1. Authored from the issue and Notion (`/cry-bdd-create-scenarios`).
2. Persisted into the issue body inside the `bdd:scenarios` markers.
3. Mapped from the test code during implementation (canonical marker added).
4. Validated for coverage on demand (`/cry-bdd-validate-scenarios`) and on PR review.
5. When the business rule changes: rewrite the scenario in the issue first, then update the covering tests in the same change. The mapping is a contract; both ends move together.

### Relationship with the Issue-Driven flow

| Flow event | BDD interaction |
|---|---|
| Phase 2 (`kata-requirements-brief`) produces numbered ACs | Scenarios may complement the ACs; both can coexist in the issue. |
| Phase 4 (implementation) | Tests carry both `@ac("AC-N")` and `@bdd_scenario("...")` markers when both layers exist. |
| Gate 2 (`kata-quality-gate`) | Validates AC↔test mapping. BDD coverage is checked separately by `kata-bdd-validate-scenarios`. |

The two surfaces remain orthogonal. Neither blocks the other.

## Glossary

| Term | Definition |
|---|---|
| BDD scenario | Gherkin Given/When/Then triple authored in business language and persisted in the GitHub issue. |
| Scenario slug | kebab-case derivation of the scenario title, used as the canonical mapping key. |
| Canonical marker | Stack-specific test annotation that explicitly references a scenario slug. |
| Fallback marker | Test name or docstring containing `BDD: <title-or-slug>`, accepted when the canonical marker is unavailable. |
| `bdd:scenarios` block | The HTML-marker-delimited section in the issue body that holds the business scenarios. |
| Gap | Scenario in the issue with no covering test. |
| Drift | Test marker pointing to a scenario absent from the issue. |

## References

- `lex-bdd-scenarios` — authoring law (sources, language, persistence)
- `lex-bdd-coverage` — coverage law (mapping, drift, level neutrality)
- `kata-bdd-create-scenarios`, `kata-bdd-validate-scenarios` — procedures
- `cry-bdd-create-scenarios`, `cry-bdd-validate-scenarios` — entry points
- `lex-test-pyramid`, `lex-test-isolation`, `codex-test-strategy` — test-level decisions
- `framework/templates/contributing_templates/user-story-for-api.md`, `user-story-for-frontend.md` — origin of API/UI scenarios that get duplicated
