# Lexis: BDD Scenarios Authored from Business Sources

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Authoring of BDD scenarios for any feature, before implementation

## Law

> **BDD scenarios MUST be authored before implementation begins, derived exclusively from the GitHub issue and Notion (the business sources of truth), never from existing source code, tests, or implementation diffs. Scenarios MUST be expressed in Gherkin (Given/When/Then) using business language (domain actors, domain entities, observable business outcomes), never technical language (HTTP verbs, status codes, payload shapes, UI selectors). When the issue already contains API-focused or UI-focused Gherkin (typical of `user-story-for-api` or `user-story-for-frontend` templates), those scenarios MUST be duplicated and rewritten in business form, with the originals preserved unchanged. The final business scenarios MUST be persisted back into the GitHub issue body, inside a section delimited by `<!-- bdd:scenarios:start -->` and `<!-- bdd:scenarios:end -->` markers.**

## Coverage

- **Applies to:** any feature, bugfix, or behavior change for which BDD has been adopted (typically invoked through `/cry-bdd-create-scenarios`).
- **Bound agents:** any agent producing BDD scenarios; primarily `warrior-hera` and `kata-bdd-create-scenarios`.
- **Exceptions:** None. Lexis admit no exceptions.

## Rules

### 1. Source of truth

Allowed sources for authoring scenarios:

- The GitHub issue (title, body, comments, labels, assignees).
- Related Notion pages (when `notion` is in `mcp.servers`).

Forbidden sources during authoring:

- Application source code, tests, fixtures, ADRs, OpenAPI specs derived from the implementation, log lines.
- Pull request diffs.
- Engineer recall of "what the code does today".

The point is to describe what the business wants, not what the system already happens to do.

### 2. Business language only

Each scenario describes externally observable behavior in domain terms.

| Forbidden in `Given`, `When`, `Then` | Replace with |
|---|---|
| HTTP verbs (`POST`, `GET`, `PUT`, `PATCH`, `DELETE`) | a domain action ("the customer requests a refund") |
| HTTP paths (`/v1/refunds`) | the domain operation ("a refund request") |
| Status codes (`201`, `409`, `422`) | the business outcome ("the refund is recorded", "the refund is rejected") |
| Payload shape tokens (`{ "data": ... }`) | the observable effect ("an audit entry exists") |
| UI selectors (`.btn-submit`, `[data-testid=...]`) | the user action ("the operator approves the release") |
| Framework names (`fastapi`, `react`) | omit |

### 3. Duplicate, never replace

When the issue already contains Gherkin from `user-story-for-api` or `user-story-for-frontend`, those scenarios are kept intact (they remain useful for contract validation). The agent duplicates each into a business form inside the dedicated `bdd:scenarios` block. Both representations live in the issue.

### 4. Persisted in the issue body

Final scenarios live inside the issue body, in a delimited block:

```
<!-- bdd:scenarios:start -->
## BDD Scenarios (Business)

Scenario: ...
  Given ...
  When ...
  Then ...
<!-- bdd:scenarios:end -->
```

The block is the canonical, mutable record. The agent uses GitHub MCP `update_issue` (or equivalent) to write or refresh it. Re-running the authoring kata replaces only this block, never anything else in the body.

### 5. Authored before implementation

The cry/kata refuses to run if the working tree contains non-trivial implementation changes against the targeted issue, unless the user explicitly confirms a backfill. The default assumption is BDD-first.

### 6. No invented rules

If a rule is not present in the issue or Notion, it does not enter as a `Scenario:`. Pending rules are listed under a `## Pending Questions` sub-section inside the same `bdd:scenarios` block, awaiting the user.

## Examples

### Correct

(Issue body, before)

```gherkin
Scenario: Successful refund creation
  When I send POST /v1/refunds with body { "payment_id": "p_1", "amount": 1000 }
  Then the API returns 201 with { "id": ..., "status": "pending" }
```

(Issue body, after running `/cry-bdd-create-scenarios`)

```
<!-- bdd:scenarios:start -->
## BDD Scenarios (Business)

Scenario: Customer requests a refund for an eligible payment
  Given a captured payment of 1000 BRL made by the customer in the last 30 days
  When the customer requests a refund for that payment
  Then a refund is recorded against the payment in pending state
  And the audit trail records the refund attempt with the requesting customer
<!-- bdd:scenarios:end -->
```

The original API-focused scenario is left untouched above the block.

### Incorrect

```gherkin
Scenario: Customer requests a refund
  When the customer sends POST /v1/refunds with payload { ... }
  Then the response is 201
  And the JSON contains "id" and "status"
```

The scenario uses HTTP verbs, status codes, and payload shape (Rule 2 violation).

```
(no <!-- bdd:scenarios:start --> block in the issue body)
```

The block is missing (Rule 4 violation).

```
(scenarios derived by reading service.py and test_refund.py)
```

Code was used as a source (Rule 1 violation).

## Automated Validation

- **Tool:** `kata-bdd-create-scenarios` enforces the source restriction (only GitHub MCP and Notion MCP reads), runs a forbidden-token language check, and writes the block via GitHub MCP only after explicit user confirmation. `kata-bdd-validate-scenarios` confirms the presence and shape of the block.
- **Timing:** at scenario authoring (cry invocation); on PR review when scenarios accompany a change.
- **Metric:** 100% of features using BDD have a `bdd:scenarios` block in the issue; 0 scenarios containing forbidden technical tokens.
