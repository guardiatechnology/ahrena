# Kata: Write content to Notion via MCP

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Creating and updating pages, blocks, and properties in Notion via MCP server

## Objective

Create or update content in Notion (pages, blocks, database properties) via MCP server. Covers four operations: creating a new page, appending blocks to an existing page, updating page properties, and deleting a specific block. Always verifies that the target exists before writing and confirms destructive actions with the user.

## When to Use

- When the user needs to create a new page or document in Notion
- When content must be appended to an existing page (e.g., meeting notes, artifact sync)
- When properties of a database entry must be updated (e.g., status, date, assignee)
- When a specific block must be removed from a page
- When invoked by a Warrior that produces output destined for Notion (e.g., documentation sync, event catalog, ADR)

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Operation | Yes | `create` (new page) \| `append` (add blocks) \| `update-props` (page/entry properties) \| `delete-block` (remove a block) |
| Target | Conditional | Parent page or database ID/URL for `create`; page ID/URL for `append` and `update-props`; block ID for `delete-block` |
| Content | Conditional | Block content for `create` and `append`; property map for `update-props` |
| Title | Conditional | Page title — required for `create` |
| Duplicate handling | No | `skip` (do nothing if page with same title exists), `update` (append to existing), `create-new` (always create); default: `skip` |

## Workflow

```
Progress:
- [ ] 1. Verify MCP preconditions and directives
- [ ] 2. Identify operation and target
- [ ] 3. Check for existing content (create / append)
- [ ] 4. Execute write operation
- [ ] 5. Confirm and return result
```

### Step 1: Verify MCP Preconditions and Directives

1. Consult `.ahrena/.directives` per `lex-directives`
2. Verify that `notion` is listed in `mcp.servers` per `lex-mcp`. If not, inform the user and stop
3. Confirm that `NOTION_API_KEY` is defined in the environment. If not, inform the user which variable to configure and stop
4. Consult `codex-mcp-notion` to identify the correct tools and parameters for the requested operation

### Step 2: Identify Operation and Target

1. Confirm the operation: `create`, `append`, `update-props`, or `delete-block`
2. If target is a URL, extract the ID (last 32 characters of the Notion URL, formatted as UUID)
3. If target was not provided:
   - For `create`: ask the user for the parent page or database where the new page should be created
   - For `append` and `update-props`: ask the user for the page ID or URL
   - For `delete-block`: ask the user for the block ID to delete
4. If content was not provided for `create` or `append`, ask the user what to write

### Step 3: Check for Existing Content (create / append only)

For `create`:
1. Call `search(query="{title}", filter={"property": "object", "value": "page"})` to check whether a page with the same title exists in Notion
2. Apply duplicate handling:
   - `skip` — if a matching page is found, inform the user and stop; return the existing page URL
   - `update` — if a matching page is found, switch to `append` mode using the found page ID
   - `create-new` — proceed regardless of existing pages

For `append`:
1. Call `get_page(page_id="{id}")` to confirm the page exists and retrieve its current title
2. If the page does not exist, alert the user and stop

For `update-props` and `delete-block`: proceed directly to Step 4 (target is explicit).

### Step 4: Execute Write Operation

**Operation `create`:**
1. Build the `properties` object with the page title:
   ```json
   {"title": [{"text": {"content": "{title}"}}]}
   ```
2. Build the `children` array with the initial content blocks (see block formats in `codex-mcp-notion`)
3. Call `create_page(parent={...}, properties={...}, children=[...])`
4. Record the returned `id` and `url` of the new page

**Operation `append`:**
1. Build the `children` array with the blocks to add
2. Call `append_block_children(block_id="{page_id}", children=[...])`
3. For large content (more than 20 blocks), split into multiple `append_block_children` calls to stay within API limits

**Operation `update-props`:**
1. Build the `properties` object with only the fields to update (do not include unchanged properties)
2. Call `update_page(page_id="{id}", properties={...})`

**Operation `delete-block`:**
1. **Confirm with the user** before deleting — state clearly which block will be removed (include block ID and any visible text if retrievable)
2. After confirmation, call `delete_block(block_id="{id}")`

### Step 5: Confirm and Return Result

1. Report the outcome to the user:
   - `create`: "Page '{title}' created at {url}"
   - `append`: "Content appended to '{page title}' ({url})"
   - `update-props`: "Properties updated on '{page title}' ({url})"
   - `delete-block`: "Block {id} deleted from '{page title}'"
2. Include the page URL in every confirmation so the user can navigate directly
3. If the operation failed, report the error clearly and suggest next steps (check access, verify ID, confirm integration has access to the target page/database)

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| New page | Notion page | Parent page or database specified by user |
| Appended content | Blocks on existing page | Page specified by user |
| Updated properties | Database entry fields | Page/entry specified by user |
| Confirmation | Text with page URL | Response to user |

## Execution Example

### Example — Create a structured page

```
Operation: create
Parent: https://notion.so/WIKI-PAGE-ID
Title: Event Storm — Platform Module
Content: heading "Scheduled Transfers", event table with 5 events
Duplicate handling: skip
```

Steps executed:
1. `search(query="Event Storm — Platform Module", filter={"property": "object", "value": "page"})` — no existing page found
2. `create_page(parent={"page_id": "WIKI-PAGE-ID"}, properties={title...}, children=[heading_2, table...])`
3. Result: "Page 'Event Storm — Platform Module' created at https://notion.so/..."

### Example — Append to existing page

```
Operation: append
Target: https://notion.so/EXISTING-PAGE-ID
Content: paragraph "Updated 2026-04-26 — added cancelled event"
```

Steps executed:
1. `get_page(page_id="EXISTING-PAGE-ID")` — page confirmed
2. `append_block_children(block_id="EXISTING-PAGE-ID", children=[paragraph...])`
3. Result: "Content appended to 'Event Storm — Platform Module' (https://notion.so/...)"

## Constraints

- **Use MCP only:** never call the Notion REST API directly; always use MCP server tools per `lex-mcp`
- **No hardcoded credentials:** authentication exclusively via `NOTION_API_KEY` environment variable
- **Check before creating:** always run `search` to detect duplicates before `create`, unless `create-new` is explicitly set
- **Confirm before deleting:** always ask the user to confirm before executing `delete-block`
- **Do not overwrite without instruction:** `append` adds to existing content; to replace content, the user must explicitly request block deletion first
- **Integration access:** if Notion returns a 403 or "object not found" error, it means the integration was not granted access to the target page or database — instruct the user to share it with the integration in Notion

## References

- `lex-mcp` — MCP tool usage laws
- `codex-mcp-notion` — Notion MCP tools and parameters reference
- `kata-mcp-notion-read` — Kata for reading Notion content before writing
- `lex-directives` — How to read `.ahrena/.directives`
