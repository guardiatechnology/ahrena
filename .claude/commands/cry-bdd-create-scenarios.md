Author BDD Business Scenarios from Issue + Notion. Standalone — produces business-focused BDD scenarios for a GitHub issue and writes them back to the issue body

# Cry: Author BDD Business Scenarios from Issue + Notion

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Standalone — produces business-focused BDD scenarios for a GitHub issue and writes them back to the issue body

## Usage

```
/cry-bdd-create-scenarios <issue-number> [<owner>/<repo>]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `issue-number` | Yes | GitHub issue number | `42` |
| `<owner>/<repo>` | No | Default: current repo via git remote | `guardiafinance/ahrena` |

## Prerequisites

- `github` listed in `mcp.servers` in `.ahrena/.directives`
- `notion` listed in `mcp.servers` (optional, enriches context)
- Env: `GITHUB_PAT` required; `NOTION_API_KEY` optional
- Existing GitHub issue

## What the Command Does

1. Invokes `kata-bdd-create-scenarios`.
2. The kata reads the issue and Notion (never code) and drafts business-focused scenarios in Gherkin.
3. The kata duplicates any API/UI scenarios already in the issue, leaving the originals untouched.
4. The kata presents the proposed `bdd:scenarios` block to the user for confirmation.
5. On confirmation, the kata updates the issue body via GitHub MCP.

## Prompt Template

```
Context:
- Issue: #{{issue-number}}
- Repository: {{<owner>/<repo>}} (or detected via git remote)

Task:
Run kata-bdd-create-scenarios for issue #{{issue-number}}. Author business-focused BDD scenarios sourced exclusively from the GitHub issue body, comments, and related Notion pages. Do not read source code. Duplicate any existing API/UI Gherkin into a separate business-language form (preserve the originals). Wait for explicit user confirmation before updating the issue. Persist the final scenarios into the issue body inside the markers <!-- bdd:scenarios:start --> ... <!-- bdd:scenarios:end -->. Report scenario titles and slugs.

Strictly respect lex-bdd-scenarios (sources, language, persistence) and lex-mcp (no destructive write without explicit user confirmation).
```

## Invocation Example

**Input:**

```
/cry-bdd-create-scenarios 42 guardiafinance/ahrena
```

**Expected output:**

- Kata fetches issue #42 (and Notion if configured).
- Detects 2 API-focused scenarios from the user-story-for-api template.
- Drafts 3 business-focused scenarios.
- Presents the proposed `bdd:scenarios` block to the user.
- On confirmation, updates the issue body. Original API scenarios are unchanged.
- Reports the scenario slugs:
  - `customer-requests-a-refund-for-an-eligible-payment`
  - `customer-cannot-refund-after-30-days`
  - `concurrent-refunds-deduplicate-by-idempotency-key`

## Restrictions

- **Code is never a source.** Source files and tests are out of scope for this command.
- **Issue must exist.** No issue → command refuses (no auto-creation).
- **Confirmation required.** No write to the issue without explicit "yes".
- **Standalone.** Does not enter the Issue-Driven flow, does not block any phase or gate.

## Associated Cries and Katas

- `kata-bdd-create-scenarios` — invoked by this cry
- `cry-bdd-validate-scenarios` — coverage check after implementation
- `cry-implement-issue` — orthogonal flow; this cry can run alongside it without coupling
