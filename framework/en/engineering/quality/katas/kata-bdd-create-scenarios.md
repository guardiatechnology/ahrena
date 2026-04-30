# Kata: Author BDD Business Scenarios from Issue and Notion

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Standalone — produces business-focused BDD scenarios from a GitHub issue and Notion, then writes them back into the issue body

## Objective

Read a GitHub issue (and related Notion pages when MCP is configured), produce a list of business-focused Gherkin scenarios, and persist them into the issue body inside the `<!-- bdd:scenarios:start -->` / `<!-- bdd:scenarios:end -->` markers. The kata never reads application source or test code; the scenarios encode business intent, not a description of what the implementation already does.

## When to Use

- Before implementation begins, on a feature where BDD adds value (tier-1, regulated domain, complex business rules).
- Invoked through `/cry-bdd-create-scenarios <issue>`.
- Optional and standalone — independent of `/cry-implement-issue` and Gate 2.

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Issue number | Yes | GitHub issue number (e.g., `42`) |
| Repository | Yes | `owner/repo` (default: detected via git remote) |
| Notion root | No | Notion context page; defaults to `knowledge.notion.root_page` in `.directives` |
| User confirmation | Yes | Explicit confirmation before the kata writes to the issue via MCP |

## Workflow

```
Progress:
- [ ] 1. Verify MCP and directives
- [ ] 2. Read the issue (title, body, comments)
- [ ] 3. Pull Notion context if available
- [ ] 4. Detect existing API/UI scenarios in the issue body
- [ ] 5. Draft business-focused scenarios (duplicate, do not replace)
- [ ] 6. Run language validation (no HTTP verbs, status codes, payload shapes)
- [ ] 7. Present the proposed bdd:scenarios block to the user
- [ ] 8. On confirmation, update the issue body via GitHub MCP
- [ ] 9. Report scenario titles and slugs to the user
```

### Step 1: Verify MCP and directives

1. Read `.ahrena/.directives` per `lex-directives`.
2. Confirm `github` is in `mcp.servers` (per `lex-mcp`); without it, stop and inform the user.
3. Confirm `notion` is in `mcp.servers` (optional). When missing, continue without Notion enrichment and inform the user that context will come only from the issue.
4. Confirm env vars: `GITHUB_PAT` (required); `NOTION_API_KEY` (when Notion is in scope).

### Step 2: Read the issue

1. Use `kata-mcp-github-read` to fetch the issue: title, body, labels, assignees, comments.
2. Stop if the issue does not exist or has an empty body.
3. If the body already contains a `<!-- bdd:scenarios:start -->` block, capture the current contents for diff purposes (re-runs are merges, not blind overwrites).
4. **Source code is forbidden.** No `git show`, no Read against `src/`, `tests/`, `app/`, `domain/`, etc. The kata's perspective is what the business wants; code answers a different question.

### Step 3: Pull Notion context (optional)

When `notion` is active:

1. Extract domain terms from the issue title and body (entity names, operations, roles).
2. Use `kata-mcp-notion-read` in `search` mode for 3-5 high-signal terms (avoid excessive cost).
3. For relevant hits, fetch in `page` mode at `full` depth.
4. Filter for product strategy, business rules, and prior product decisions. Skip irrelevant pages.
5. Record: page title, URL, relevant snippet.

### Step 4: Detect existing API/UI scenarios

1. Search the issue body for fenced ```gherkin blocks and `Scenario:` markers.
2. Capture them as **API/UI scenarios** (the original templates' output). Keep them.
3. They become the seed for duplication into business form (Step 5).
4. The agent does not modify or remove the originals.

### Step 5: Draft business scenarios

For each behavior implied by the issue and Notion context:

1. Identify the actor in domain terms (customer, operator, system on its own behalf — never "the API" or "the user agent").
2. Identify the action in domain terms (request a refund, schedule a transfer, approve a release — never an HTTP verb).
3. Identify the observable outcome (a record is created, a notification is dispatched, a state transition occurs — never a status code or payload shape).
4. Write the scenario in Gherkin:

```gherkin
Scenario: <Title in product language>
  Given <precondition stated in domain terms>
  When <action stated in domain terms>
  Then <observable business outcome>
  And <additional outcome, if any>
```

5. Cover happy path, key error/edge cases, and idempotency or replay when relevant.
6. Do not invent rules absent from the issue or Notion; instead, list them under a `## Pending Questions` sub-section inside the same block.

### Step 6: Language validation

Reject any drafted line that contains:

- HTTP verbs in caps (`POST`, `GET`, `PUT`, `PATCH`, `DELETE`).
- Status codes when adjacent to "status", "code", or "returns" (regex `\b[1-5]\d{2}\b`).
- Payload shape tokens (`{` / `}` enclosing field-like keys; `Content-Type`, `Accept`, `Idempotency-Key`).
- DOM/UI selectors (`#`, `.`, `[data-`).
- Implementation framework names (`fastapi`, `react`, `redis`, `kafka` when used as a `Then` element).

For each rejection: rewrite the line in business terms, or escalate the conflict to the user.

### Step 7: Present the proposed block

Show the user the proposed `bdd:scenarios` block, alongside any existing API/UI scenarios that will remain unchanged. Wait for explicit confirmation ("yes, update the issue") before proceeding.

### Step 8: Update the issue body

1. If the issue body already has a `<!-- bdd:scenarios:start -->` ... `<!-- bdd:scenarios:end -->` block, replace its contents in place.
2. Otherwise, append the block at the end of the body, preceded by one blank line.
3. Use GitHub MCP `update_issue` (or equivalent) with the new body. Do not change title, labels, assignees, or any other field.
4. Block format:

```
<!-- bdd:scenarios:start -->
## BDD Scenarios (Business)

Scenario: ...
  Given ...
  When ...
  Then ...

Scenario: ...
  Given ...
  When ...
  Then ...

## Pending Questions (optional)
- ...
<!-- bdd:scenarios:end -->
```

### Step 9: Report

Print to the user: list of scenario titles, their slugs (for use as test markers), the URL to the updated issue, and any pending questions captured.

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Scenario list with slugs | Markdown response | User-facing |
| Updated issue body | GitHub issue | Remote repository (via MCP) |

## Restrictions

- **Code is forbidden as a source.** The kata cannot run any tool that reads source code or test code.
- **Originals are preserved.** API/UI scenarios already in the issue are duplicated into business form, never modified or removed.
- **Idempotent block update.** Re-running the kata replaces only the `bdd:scenarios` block; the rest of the body stays intact.
- **Confirmation gate.** No issue update without explicit user confirmation; this action is visible to others.
- **No invented business rules.** Anything not in the issue or Notion goes into `Pending Questions`, not into a `Scenario:`.

## References

- `lex-bdd-scenarios` — authoring law (sources, language, persistence)
- `lex-bdd-coverage` — coverage law (used downstream by the validation kata)
- `codex-bdd` — methodology, marker conventions, anti-patterns
- `lex-mcp`, `kata-mcp-github-read`, `kata-mcp-notion-read` — MCP tooling rules
- `kata-bdd-validate-scenarios` — successor procedure (after implementation)
