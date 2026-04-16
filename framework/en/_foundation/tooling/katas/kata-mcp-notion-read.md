# Kata: Query Notion content via MCP

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Reading pages, databases, and blocks from Notion via MCP server for local context use

## Objective

Fetch and read content from Notion (pages, databases, blocks) via MCP server, bringing the information into the session context for reference, analysis, or processing. This kata is strictly **read-only** — no pages or blocks are created or modified.

## When to Use

- When the user needs to look up documentation, notes, or decisions stored in Notion
- When entries from a Notion database are needed (e.g., backlog, ADRs, tasks)
- When a Notion page's content must be analyzed or referenced during the session

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Query or ID | Yes | Text search term, page ID, or page/database URL in Notion |
| Mode | No | `search` (text search), `page` (specific page by ID), `database` (database entries); default: `search` |
| Database filter | No | Property filters for `query_database` (e.g., status, date, tag) |
| Depth | No | `summary` (title + summary) or `full` (complete block content); default: `summary` |

## Workflow

```
Progress:
- [ ] 1. Verify MCP preconditions and directives
- [ ] 2. Identify what to fetch
- [ ] 3. Fetch and read the content
- [ ] 4. Present result to user
```

### Step 1: Verify MCP preconditions and directives

1. Consult `.ahrena/.directives` per `lex-directives`.
2. Verify that `notion` is listed in `mcp.servers` (per `lex-mcp`). If not, inform the user and stop.
3. Confirm that the `NOTION_API_KEY` environment variable is defined. If not, inform the user which variable to configure and stop.
4. Consult `codex-mcp-notion` to identify the correct tools and parameters.

### Step 2: Identify what to fetch

1. If the user provided a page ID or URL: use it in Step 3 with `get_page`.
2. If the user provided a database ID: use it in Step 3 with `query_database`.
3. If the user provided a search term: use it in Step 3 with `search`.
4. If no input was provided, ask the user: "Which page, database, or term would you like to look up in Notion?"

### Step 3: Fetch and read the content

**Mode `search`:**
1. Call `search(query="{term}")` to locate matching pages and databases.
2. Present the list of results (title, type, last edited) and confirm with the user which item to expand.
3. For the selected item, call `get_page(page_id="{id}")`.
4. If depth is `full`: call `get_block_children(block_id="{id}")` to retrieve the full content.

**Mode `page`:**
1. Call `get_page(page_id="{id}")` to retrieve metadata and properties.
2. If depth is `full`: call `get_block_children(block_id="{id}")` to retrieve the content blocks.

**Mode `database`:**
1. Call `query_database(database_id="{id}", filter={...})` with optional filters provided by the user.
2. For each returned entry, record: title, relevant properties, page ID.
3. If the user requests details of a specific entry, call `get_page` and `get_block_children` for that entry.

### Step 4: Present result to user

1. Present the retrieved content in a structured, readable format.
2. For databases: display entries as a table with the most relevant properties.
3. For pages: display title, metadata (last edited, creator), and content (summary or full per depth setting).
4. Include the ID and URL of each presented item for future reference.

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Page content | Structured text (title, metadata, blocks) | Response to user |
| Database entries | Table with relevant properties | Response to user |
| Search results | List of matching items with title and type | Response to user |

## Restrictions

- **Read-only:** this kata never creates, modifies, or deletes pages, blocks, or properties in Notion.
- **Use MCP only:** never use the Notion REST API directly; always use MCP server tools (per `lex-mcp`).
- **No hardcoded credentials:** authentication exclusively via `NOTION_API_KEY` environment variable.
- **Confirm before broad searches:** if the query could return many results, present a sample and confirm with the user before proceeding.

## References

- `lex-mcp` — MCP tool usage laws
- `codex-mcp-notion` — Notion MCP tools and parameters reference
- `lex-directives` — How to read `.ahrena/.directives`
