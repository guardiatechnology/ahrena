# Kata: Issue Analysis

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Phase 1 of the Issue-Driven flow — reading the GitHub issue and fetching related context from Notion

## Objective

Read a GitHub issue (title, body, comments, labels, metadata) and fetch related context documents from Notion (product specs, prior ADRs, business rules), producing a structured brief at `.ahrena/issues/{n}/01-brief.md`. This brief is the basis for subsequent phases of the Issue-Driven flow.

## When to Use

- Phase 1 of the flow orchestrated by `warrior-athena` after invocation of `/cry-implement-issue`
- Whenever you need to consolidate context about an issue before starting design or implementation

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Issue number | Yes | GitHub issue number (e.g., `42`) |
| Repository | Yes | `owner/repo` (e.g., `guardiafinance/ahrena`) |
| Notion root | No | Context page/database; defaults to `knowledge.notion.root_page` in `.ahrena/.directives` |

## Workflow

```
Progress:
- [ ] 1. Verify MCP preconditions and directives
- [ ] 2. Read the GitHub issue
- [ ] 3. Fetch related context from Notion
- [ ] 4. Consolidate and structure the brief
- [ ] 5. Persist to .ahrena/issues/{n}/01-brief.md
- [ ] 6. Update handoff checkpoint
```

### Step 1: Verify MCP preconditions and directives

1. Consult `.ahrena/.directives` per `lex-directives`.
2. Confirm that `github` is in `mcp.servers` (per `lex-mcp`). If not, inform the user and stop.
3. Confirm that `notion` is in `mcp.servers`. If not, continue without Notion context (inform the user that enrichment will be skipped).
4. Confirm `GITHUB_PAT` and `NOTION_API_KEY` (if applicable) are defined in the environment.

### Step 2: Read the GitHub issue

1. Invoke `kata-mcp-github-read` with:
   - object: `issues`
   - `owner/repo` and `issue_number` received as input
2. Record: title, body, labels, assignees, author, creation date, state, milestone.
3. Invoke `kata-mcp-github-read` again to list the issue's comments (use `get_issue` if it already returns comments; otherwise fetch via the issue API).
4. If the issue does not exist or is empty, inform the user and stop.

### Step 3: Fetch related context from Notion

If `notion` is active:

1. Extract key terms from the issue title and body (feature proper names, domain entities, technical areas).
2. Invoke `kata-mcp-notion-read` in `search` mode for each relevant term (limit to 3-5 searches to avoid excessive cost).
3. For each promising result, invoke `kata-mcp-notion-read` in `page` mode with depth `full` to retrieve the content.
4. Filter out irrelevant results (outdated, tangential). If `knowledge.notion.root_page` is configured, prioritize results descending from that page.
5. Record: page title, URL, relevant snippet, relation to the issue.

### Step 4: Consolidate and structure the brief

Produce the brief following this structure:

```markdown
# Brief — Issue #{n}: {title}

- **Repository:** {owner/repo}
- **Author:** @{author}
- **Created:** {YYYY-MM-DD}
- **Labels:** {list}
- **Assignees:** {list}
- **Link:** {issue URL}

## Problem

{2-3 paragraph summary of what the issue describes — problem, motivation, symptoms}

## Additional Context

### From the issue (relevant comments)

- {comment 1, author, date}
- {comment 2, author, date}

### From Notion

- **[{Page title}]({URL}):** {relevant snippet, 1-3 lines}
- **[{Page title}]({URL}):** {relevant snippet, 1-3 lines}

## Work Type

{Feature | Bugfix | Refactor | Chore} — {brief justification}

## Identified Risks and Unknowns

- {List of points that require clarification before design}

## Next Phase

Phase 2: requirements elicitation (`kata-requirements-brief`).
```

### Step 5: Persist to `.ahrena/issues/{n}/01-brief.md`

1. Create the directory `.ahrena/issues/{n}/` if it does not exist.
2. Save the brief at `.ahrena/issues/{n}/01-brief.md`.
3. If the file already exists, compare with the new content: if it diverges, present the diff to the user before overwriting.

### Step 6: Update handoff checkpoint

1. Create/update `.ahrena/workflow/issue-{n}/checkpoint.md` with:
   - completed phase: 1
   - next phase: 2
   - reference: `.ahrena/issues/{n}/01-brief.md`
   - timestamp
2. Inform `warrior-athena` (or the user) that Phase 1 has completed.

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Structured brief | Markdown | `.ahrena/issues/{n}/01-brief.md` |
| Checkpoint | Markdown | `.ahrena/workflow/issue-{n}/checkpoint.md` |
| Summary to user | Structured text | Response to the orchestrator |

## Restrictions

- **Read-only on GitHub:** this kata does not create or modify issues, comments, or labels (per `kata-mcp-github-read`).
- **Read-only on Notion:** this kata does not create or modify pages (per `kata-mcp-notion-read`).
- **No scope inference:** the kata consolidates what is in the issue and Notion; it does not add undocumented information. Unknowns go in the "Risks and Unknowns" section.
- **Fixed destination:** the brief goes to `.ahrena/issues/{n}/01-brief.md`; never to another path (per `lex-issue-driven`).

## References

- `lex-issue-driven` — laws of the Issue-Driven flow
- `codex-issue-workflow` — full flow structure
- `kata-mcp-github-read` — issue reading via MCP
- `kata-mcp-notion-read` — Notion content reading via MCP
- `lex-mcp` — mandatory MCP usage
