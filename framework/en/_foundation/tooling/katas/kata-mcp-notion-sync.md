# Kata: Sync documentation to Notion via MCP

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Synchronization of Ahrena framework documents to Notion pages or databases via MCP server

## Objective

Sync Ahrena framework documents (Lexis, Codex, Katas, Warriors, Cries) to Notion via MCP server, creating new pages for missing documents and updating existing pages for modified documents. The result is a navigable mirror of the framework documentation in Notion.

## When to Use

- When the user requests syncing framework documentation to Notion
- After adding or updating significant artifacts in the framework
- When a new clade or subclade is created and needs to be documented in Notion

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Target Notion page or database | Yes | ID or URL of the root page/database in Notion where documents will be created |
| Scope | No | Specific clade or subclade (e.g., `engineering/platform`); default: all |
| Language | No | Language of documents to sync; default: `language.default` in `.ahrena/.directives` |

## Workflow

```
Progress:
- [ ] 1. Verify MCP preconditions and directives
- [ ] 2. Determine scope and collect documents
- [ ] 3. Locate destination in Notion
- [ ] 4. For each document: create or update page
- [ ] 5. Report result
```

### Step 1: Verify MCP preconditions and directives

1. Consult `.ahrena/.directives` per `lex-directives`.
2. Verify that `notion` is listed in `mcp.servers` (per `lex-mcp`). If not, inform the user and stop.
3. Confirm that the `NOTION_API_KEY` environment variable is defined. If not, inform the user which variable to configure and stop.
4. Consult `codex-mcp-notion` to identify the correct tools and parameters.

### Step 2: Determine scope and collect documents

1. Identify the language: read `language.default` from `.ahrena/.directives`.
2. Determine the source directory: `.ahrena/framework/{lang}/{scope}/` (or `.ahrena/framework/{lang}/` for all).
3. Recursively list `.md` files with Pilar prefix (`lex-`, `codex-`, `kata-`, `warrior-`, `cry-`).
4. For each file, record: relative path, title (first H1 line), Pilar type, modification date.

### Step 3: Locate destination in Notion

1. Use Notion MCP `search` to verify the destination page or database exists and is accessible.
2. If the destination is a database, confirm it has a `title` property for the page name.
3. If the destination is not found or not accessible, inform the user and stop.

### Step 4: For each document — create or update page

For each document collected in Step 2:

1. Use `search` with the document title to check if a corresponding page already exists in Notion.
2. **If not found:** use `create_page` with the title and initial content. Convert Markdown to Notion blocks (paragraphs, headings, code blocks, lists).
3. **If found:**
   - Compare the file modification date with the Notion page `last_edited_time`.
   - If the file is newer: use `append_block_children` to add a section with updated content and record sync date.
   - If the Notion page is newer: **do not overwrite**. Record as a conflict and inform the user.
4. Record the result for each document (created, updated, conflict, skipped).

### Step 5: Report result

1. Present summary: total documents processed, created, updated, conflicts (Notion pages are newer), skipped.
2. List identified conflicts with page name and Notion URL, so the user can decide the action.
3. In case of partial failure, list which documents failed and why.

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Created pages | Notion pages with document content | Notion — specified parent |
| Updated pages | Blocks appended to existing Notion page | Notion — existing page |
| Sync report | Structured text (created, updated, conflicts, skipped) | Response to user |

## Restrictions

- **Do not overwrite newer pages:** if the Notion page was edited after the last file modification, record as a conflict and await user decision.
- **Use MCP only:** never use the Notion REST API directly; always use MCP server tools (per `lex-mcp`).
- **No hardcoded credentials:** authentication exclusively via `NOTION_API_KEY` environment variable.
- **Respect declared scope:** do not sync clades or subclades outside the scope specified by the user.

## References

- `lex-mcp` — MCP tool usage laws
- `codex-mcp-notion` — Notion MCP tools and parameters reference
- `lex-directives` — How to read `.ahrena/.directives`
