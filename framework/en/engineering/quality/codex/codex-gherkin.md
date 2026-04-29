# Codex: Gherkin at Guardia

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Engineering — Quality. Adopted Gherkin subset, file layout, tags, and concrete patterns for `07-bdd-scenarios.md` and `*.feature`.

## Overview

This Codex is the **operational Gherkin manual** at Guardia. It defines exactly which keywords we use, where files live, how they are tagged, and which patterns to apply for each scenario type. Together with `lex-bdd-gherkin-format`, it is what `warrior-themis` consults line by line when writing scenarios.

## Context

- **Domain:** Gherkin syntax applied to Phase 8 of the Issue-Driven flow.
- **Audience:** `warrior-themis`, authors and reviewers of `07-bdd-scenarios.md` or `*.feature`.
- **Update trigger:** when scenario patterns become repetitive (opportunity for a new template), when linters detect new frequent anti-patterns, when the test stack changes in ways that affect naming conventions.

## Content

### 1. Adopted subset

We use a tight subset. Anything outside this list **is not accepted** in review:

| Adopted | Use |
|---|---|
| `Feature:` | Block header; name as a noun phrase |
| `Background:` | Shared business precondition |
| `Scenario:` | Concrete behavior |
| `Scenario Outline:` + `Examples:` | Parametric scenario |
| `Given` / `When` / `Then` | Main steps |
| `And` / `But` | Continuation of the previous step |
| Doc strings `"""..."""` | Only when the step needs long text (e.g., the message the customer receives) |
| Data tables `| col | col |` | Only for parametric example data |
| Tags `@AC-{N}`, `@happy-path`, etc. | Traceability and taxonomy |
| Comments `# ...` | For the `SCN-{N}` id when not in the title |

| Excluded | Why |
|---|---|
| `Rule:` | Introduces hierarchy we don't need; group via Feature or tags |
| `*` as free-form step | Reduces clarity of the step's role (Given/When/Then) |
| Custom keywords / extensions | Each plugin would couple to a runner — forbidden by `lex-bdd-no-framework-coupling` |

### 2. File layout

**Default (preferred):** consolidated in `07-bdd-scenarios.md`.

```
docs/
└── issues/
    └── issue-42/
        ├── 01-brief.md
        ├── 02-requirements.md
        ├── 03-architecture.md
        ├── 07-bdd-scenarios.md      ← consolidated
        └── 08-bdd-validation-report.md
```

**Volume justifies a split:** when there are > 3 Features or > 30 scenarios in the same issue, split:

```
docs/issues/issue-42/
├── 07-bdd-scenarios.md              ← index + frontmatter
└── scenarios/
    ├── transfer-scheduling.feature
    ├── transfer-cancellation.feature
    └── transfer-execution.feature
```

In that case, `07-bdd-scenarios.md` contains only the frontmatter and the list of `.feature` files.

### 3. Frontmatter for `07-bdd-scenarios.md`

Mandatory YAML at the top of the file declaring origin and coverage:

```yaml
---
issue: 42
repo: guardiafinance/ahrena
generated_at: "2026-04-29T14:00:00Z"
generated_by: warrior-themis
sources:
  github_issue: "guardiafinance/ahrena#42"
  notion_pages:
    - "https://www.notion.so/page-id-1"
  flow_artifacts:
    - docs/issues/issue-42/01-brief.md
    - docs/issues/issue-42/02-requirements.md
    - docs/issues/issue-42/03-architecture.md
ac_coverage:
  - ac: AC-1
    scenarios: [SCN-1]
  - ac: AC-2
    scenarios: [SCN-2, SCN-3]
  - ac: AC-3
    scenarios: [SCN-4, SCN-5, SCN-6]
---
```

Paths under `src/`, `app/`, `lib/`, `tests/` in `sources` invalidate the artifact (per `lex-bdd-spec-only-sources`).

### 4. Gherkin block language

First line of the Gherkin block (after the frontmatter):

```gherkin
# language: en
```

Mandatory when the language is not `en`. Consistent within the same file. Supported languages: `pt-BR`, `es`, `en`. For multi-team projects, `en` is the pragmatic default.

### 5. Tag taxonomy

| Category | Tags | Count per scenario |
|---|---|---|
| AC | `@AC-1`, `@AC-2`, ... | **≥ 1** (mandatory) |
| Type | `@happy-path` \| `@alternative` \| `@edge` \| `@error` \| `@nfr` | **exactly 1** (mandatory) |
| Area (optional) | `@backend`, `@frontend`, `@mobile`, `@api`, `@worker` | 0..1 |
| Priority (optional) | `@critical`, `@regression`, `@smoke` | 0..1 |

Tags go on **a single line immediately above** the `Scenario:` or `Scenario Outline:`. Tags on the Feature apply to all scenarios in the file (e.g., `@backend` at the top of the Feature avoids repetition).

### 6. `SCN-{N}` id — where to place it

**Preferred:** in the scenario title.

```gherkin
@AC-1 @happy-path
Scenario: SCN-1 Customer schedules a valid transfer
```

**Accepted:** in a comment immediately above.

```gherkin
# SCN-1
@AC-1 @happy-path
Scenario: Customer schedules a valid transfer
```

Rules:

- Unique within the file.
- Stable: when the scenario text is edited, the id remains (preserves test traceability).
- Contiguous numbering not required; `SCN-1`, `SCN-2`, `SCN-4` is accepted (`SCN-3` was removed in review).

### 7. `Background` usage

`Background` declares a **business precondition** shared across all scenarios in the file.

**Good:**

```gherkin
Background:
  Given an active customer with a checking account in the "Operations" wallet
  And the customer has approver profile enabled
```

**Bad:**

```gherkin
Background:
  Given a clean Postgres database
  And the event queue was purged
  And the service was restarted
```

Technical setup lives in test code (fixture, container), not in the scenario. Per `lex-bdd-gherkin-format` Rule 6.

### 8. `Scenario Outline` — when to use

Use **only** when there are ≥ 3 parametric variations of the same Given/When/Then triple.

**Good:**

```gherkin
@AC-2 @edge
Scenario Outline: SCN-3 Balance limits at scheduling
  Given the available balance is $ <balance>
  When the customer requests a transfer of $ <amount>
  Then the system responds with <result>

  Examples:
    | balance | amount | result                  |
    | 100.00  | 50.00  | approved                |
    | 100.00  | 100.00 | approved                |
    | 100.00  | 100.01 | rejected for low balance |
    | 100.00  | 0.00   | rejected for invalid amount |
```

**Bad:** 1 or 2 examples in an outline (use separate scenarios; outline with 1-2 rows is overhead with no gain).

Examples table headers in short snake_case. Monetary values with consistent format ($ X.XX in en; R$ X,XX in pt-BR).

### 9. Naming conventions

| Element | Pattern | Example |
|---|---|---|
| Feature | Capitalized noun phrase | `Feature: Transfer scheduling` |
| Scenario | `SCN-{N} <verb phrase in third person>` | `Scenario: SCN-1 Customer schedules a valid transfer` |
| Steps | Third person, active voice, present tense | `When the customer schedules a transfer` (not "You schedule...") |
| Doc string | Triple quotes, consistent indentation | inside `Then` when literal message must be cited |
| Tag | `@kebab-case` or `@AC-{N}` | `@happy-path`, `@AC-3` |

### 10. Common patterns

#### 10.1 Negative scenario (`@error`)

Same `Given` as the happy-path, altered `When`, opposite `Then`:

```gherkin
@AC-3 @error
Scenario: SCN-4 Customer attempts to schedule without funds
  Given the available balance is $ 50.00
  When the customer attempts to schedule a transfer of $ 100.00
  Then the system rejects the scheduling for insufficient funds
  And no transfer is recorded
```

#### 10.2 Boundary scenario (`@edge`)

`Given` at the exact boundary value:

```gherkin
@AC-3 @edge
Scenario: SCN-5 Balance equal to amount plus fee
  Given the available balance is $ 100.00
  And the transfer fee is $ 1.00
  When the customer attempts to schedule a transfer of $ 100.00
  Then the system rejects the scheduling for insufficient funds
```

#### 10.3 NFR scenario (`@nfr`)

Observable budget, latency, idempotency behavior:

```gherkin
@AC-4 @nfr
Scenario: SCN-6 Response within latency budget
  Given an active customer
  When the customer requests the available balance
  Then the response is delivered within 1 second
```

#### 10.4 Idempotency (`@nfr`)

```gherkin
@AC-5 @nfr
Scenario: SCN-7 Resubmission of the same scheduling does not duplicate
  Given a customer who already scheduled transfer X
  When the customer resubmits exactly the same scheduling X
  Then the system returns the same previously recorded scheduling
  And no additional transfer is created
```

### 11. Anti-patterns (cross-reference)

Canonical list of forbidden patterns: `lex-bdd-gherkin-format` Rule 3. Summary of the most frequent:

- UI selectors: `#id`, `.class`, `input[name=...]`
- HTTP methods / status codes: `POST /api/...`, `status code 201`
- Function names: `calculate_fee()`, `processPayment(...)`
- Table names / SQL: `SELECT ...`, `INSERT INTO refunds`
- File paths: `src/`, `app/`, `.py`, `.ts`
- Literal JSON, HTTP headers, hashes

### 12. Lint — checker regex

Base set used by the lint (and by `warrior-themis` for self-review):

```
# forbidden
\b(POST|GET|PUT|DELETE|PATCH)\s+/        # HTTP method + path
\bstatus\s+code\s+\d+                    # numeric status code
\b\d{3}\b\s+(OK|Created|Bad Request)     # named status
\b[a-z_][a-z0-9_]*\([^)]*\)              # function/method names
SELECT\s+|INSERT\s+INTO|UPDATE\s+\w+\s+SET   # SQL
src/|app/|lib/|tests/|spec/              # implementation paths
#[a-zA-Z][\w-]+|\.[a-zA-Z][\w-]+         # CSS selectors
input\[[^\]]+\]                          # attribute selector
\.(py|ts|tsx|js|jsx|java|go)\b           # file extension

# required (per scenario)
@AC-\d+                                  # ≥ 1
@(happy-path|alternative|edge|error|nfr) # exactly 1
SCN-\d+                                  # unique in the file
```

`warrior-themis` applies this check before saving `07-bdd-scenarios.md`. A PR failing the lint is blocked by Gate 3 (`kata-quality-gate` Check 8).

### 13. Complete example

```yaml
---
issue: 42
repo: guardiafinance/ahrena
generated_at: "2026-04-29T14:00:00Z"
generated_by: warrior-themis
sources:
  github_issue: "guardiafinance/ahrena#42"
  notion_pages:
    - "https://www.notion.so/transfer-spec"
  flow_artifacts:
    - docs/issues/issue-42/01-brief.md
    - docs/issues/issue-42/02-requirements.md
    - docs/issues/issue-42/03-architecture.md
ac_coverage:
  - ac: AC-1
    scenarios: [SCN-1]
  - ac: AC-2
    scenarios: [SCN-2]
  - ac: AC-3
    scenarios: [SCN-3, SCN-4]
  - ac: AC-4
    scenarios: [SCN-5]
---
```

```gherkin
# language: en
@backend
Feature: Transfer scheduling

  Background:
    Given an active customer with a checking account in the "Operations" wallet

  @AC-1 @happy-path
  Scenario: SCN-1 Customer schedules a valid transfer
    Given the available balance is $ 1,000.00
    When the customer schedules a transfer of $ 100.00 for tomorrow
    Then the transfer is recorded as scheduled
    And the customer receives confirmation with the expected execution date

  @AC-2 @alternative
  Scenario: SCN-2 Customer schedules with approver profile
    Given the customer has approver profile enabled
    And the available balance is $ 1,000.00
    When the customer schedules a transfer of $ 100.00 with immediate approval
    Then the transfer is recorded as scheduled and pre-approved

  @AC-3 @error
  Scenario: SCN-3 Customer attempts to schedule without funds
    Given the available balance is $ 50.00
    When the customer attempts to schedule a transfer of $ 100.00
    Then the system rejects the scheduling for insufficient funds
    And no transfer is recorded

  @AC-3 @edge
  Scenario Outline: SCN-4 Balance limits at scheduling
    Given the available balance is $ <balance>
    When the customer requests a transfer of $ <amount>
    Then the system responds with <result>

    Examples:
      | balance  | amount   | result                       |
      | 100.00   | 100.00   | approved                     |
      | 100.00   | 100.01   | rejected for low balance     |
      | 0.00     | 1.00     | rejected for low balance     |

  @AC-4 @nfr
  Scenario: SCN-5 Response within latency budget
    Given an active customer
    When the customer requests the available balance
    Then the response is delivered within 1 second
```

## References

- `lex-bdd-spec-only-sources` — allowed sources
- `lex-bdd-gherkin-format` — declarative format (the law applied by this Codex)
- `lex-bdd-no-framework-coupling` — no step-runner
- `codex-bdd` — BDD principles at Guardia
- `kata-bdd-scenarios-design` — scenario production
- `kata-bdd-validate-implementation` — scenario↔test validation
- [Cucumber: Gherkin Reference](https://cucumber.io/docs/gherkin/reference/)
