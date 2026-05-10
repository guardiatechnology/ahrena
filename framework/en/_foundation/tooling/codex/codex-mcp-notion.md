# Codex: Notion MCP Server

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Tools and authentication for the Notion MCP server on Cursor and Claude Code

## Overview

This Codex is the reference for using the **Notion MCP server** in Ahrena projects. See `codex-mcp-common` for shared MCP patterns (authentication, configuration layout, fallback behavior). This document focuses on Notion-specific tools, parameters, and use cases: reading framework documentation, creating wikis, meeting notes, and project pages.

## Context

- **Domain:** Create, read, and update operations for content in Notion via MCP (pages, blocks, databases, searches).
- **Target audience:** AI agents that manage documentation or knowledge in Notion in Ahrena projects with the MCP server active.
- **Update:** When new tools are added to the Notion MCP server or when the database schema changes.

## Content

### Platform configuration

Both platforms consume the **official remote endpoint hosted by Notion** at `https://mcp.notion.com/mcp` (tier 1 of the transport preference declared in `lex-mcp` §5 — zero local dependency). Auth is via **per-user OAuth**: on the first call, each user authenticates through the browser; the token is managed by the platform.

**Cursor (`.cursor/mcp.json`):**
```json
"notion": {
  "url": "https://mcp.notion.com/mcp"
}
```

**Claude Code (`.mcp.json`):**
```json
"notion": {
  "type": "http",
  "url": "https://mcp.notion.com/mcp"
}
```

> UX change: the previous version (npx + shared `NOTION_API_KEY`) was replaced by the hosted endpoint with per-user OAuth. Each team member authenticates individually; there is no environment variable to configure anymore.

#### Override for the legacy npx path (shared NOTION_API_KEY)

Teams that depend on the shared env-var configuration (CI without browser access, integrations with fine-grained permissions) can override the server JSON in `.ahrena/mcp/notion.json` with a `_comment`-justified deviation per `lex-mcp` §5:

```json
{
  "_comment": "Override: using shared NOTION_API_KEY because <reason — e.g., headless CI>. Decision recorded in ADR-NN.",
  "cursor": {
    "command": "npx",
    "args": ["-y", "@notionhq/notion-mcp-server"],
    "env": { "NOTION_API_KEY": "${env:NOTION_API_KEY}" }
  },
  "claude-code": {
    "command": "npx",
    "args": ["-y", "@notionhq/notion-mcp-server"],
    "env": { "NOTION_API_KEY": "${NOTION_API_KEY}" }
  }
}
```

Obtain an integration key at [notion.so/my-integrations](https://www.notion.so/my-integrations). The integration MUST have access to the target pages/databases (explicit share in Notion). The override requires Node.js on the host; run `make mcp-enable SERVER=notion PLATFORM=...` and the preflight will offer to install it when missing. Never hardcode tokens in tracked files (see `lex-mcp`).

### Available tools

| Tool | Description |
|---|---|
| `search` | Searches pages and databases by title or content |
| `get_page` | Gets metadata and properties of a page |
| `create_page` | Creates a new page in a parent (page or database) |
| `update_page` | Updates properties of an existing page |
| `get_block_children` | Lists child blocks of a page or block |
| `append_block_children` | Appends blocks to the end of a page or block |
| `delete_block` | Removes a specific block |
| `list_databases` | Lists databases accessible by the integration |
| `query_database` | Queries a database with filters and sorting |
| `get_database` | Gets metadata and schema of a database |
| `create_database` | Creates a new database in a page |

### Parameters for most-used tools

**`create_page`**
```
parent        (object, required) — {"page_id": "..."} or {"database_id": "..."}
properties    (object, required) — page properties; for a simple page: {"title": [{"text": {"content": "Title"}}]}
children      (array, optional)  — list of initial content blocks
icon          (object, optional) — page icon (emoji or file)
cover         (object, optional) — cover image
```

**`append_block_children`**
```
block_id      (string, required) — ID of the parent page or block
children      (array, required)  — list of blocks to append
```

Common block types in `children`:
```json
{ "type": "paragraph", "paragraph": { "rich_text": [{"text": {"content": "Text"}}] } }
{ "type": "heading_2", "heading_2": { "rich_text": [{"text": {"content": "Section"}}] } }
{ "type": "bulleted_list_item", "bulleted_list_item": { "rich_text": [{"text": {"content": "Item"}}] } }
{ "type": "code", "code": { "language": "python", "rich_text": [{"text": {"content": "print('hello')"}}] } }
```

**`query_database`**
```
database_id   (string, required)  — database ID
filter        (object, optional)  — filter by property
sorts         (array, optional)   — sorting [{property, direction}]
page_size     (integer, optional) — maximum results (default: 100)
```

**`search`**
```
query         (string, optional) — text to search (empty returns all)
filter        (object, optional) — {"property": "object", "value": "page"} or "database"
sort          (object, optional) — {"direction": "descending", "timestamp": "last_edited_time"}
```

### Typical use cases

| Use case | Tools |
|---|---|
| Sync framework doc to Notion | `search` → `create_page` or `update_page` + `append_block_children` |
| Create structured meeting note | `create_page` with pre-formatted `children` |
| Update project wiki | `search` → `get_page` → `append_block_children` |
| Query task database | `query_database` with status filters |
| List available databases | `list_databases` |

### Usage example: create documentation page

```
# 1. Check if page already exists
search(query="Lexis: MCP Tools", filter={"property": "object", "value": "page"})

# 2. If not found, create in project wiki
create_page(
  parent={"page_id": "WIKI-PAGE-ID"},
  properties={"title": [{"text": {"content": "Lexis: MCP Tools"}}]},
  children=[
    {"type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Purpose"}}]}},
    {"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "This Lexis defines..."}}]}}
  ]
)
```

## References

- `lex-mcp` — MCP tool usage laws
- `kata-mcp-notion-read` — Kata for querying Notion content (read-only)
- [Notion MCP Server — official repository](https://github.com/makenotion/notion-mcp-server)
- [Notion API — Block types](https://developers.notion.com/reference/block)
