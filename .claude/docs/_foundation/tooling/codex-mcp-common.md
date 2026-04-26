# Codex: MCP — Common Patterns

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Cross-cutting patterns for any MCP (Model Context Protocol) server integration — preamble consumed by all `codex-mcp-{server}` references

## Content

### What is MCP, briefly

MCP (Model Context Protocol) exposes external system capabilities (API services) directly to AI agents through a standardized tool interface, with authentication managed by the platform (Cursor, Claude Code) and without manual API call construction. Every MCP tool appears to the agent as a typed function call.

### Shared configuration pattern

Each MCP server is defined by a JSON template in `framework/mcp/<name>.json` with two platform blocks — `cursor` and `claude-code` — merged by `scripts/install.py` into the respective platform config:

```
.cursor/mcp.json          ← populated from the "cursor" block
.claude/settings.json     ← populated from the "claude-code" block
```

The merge is **additive**: user-managed entries for other servers are preserved; only servers listed in `mcp.servers` in `.ahrena/.directives` are written/overwritten.

### Authentication — uniform rule

All MCP server credentials **MUST**:

1. Come exclusively from environment variables declared in the JSON template.
2. Use `${env:VAR_NAME}` in Cursor (MCP handles resolution) and `${VAR_NAME}` in Claude Code.
3. Never appear hardcoded in code, `.directives`, or any tracked artifact (see `lex-mcp`).

Standard variable names per server:

| Server | Env Var |
|---|---|
| GitHub | `GITHUB_PAT` |
| Notion | `NOTION_API_KEY` |
| Figma | `FIGMA_API_KEY` |

### Preference over CLI

Per `lex-mcp`, when an MCP server is **active** (listed in `mcp.servers`) AND the tool exists on that server, the agent **MUST** use the MCP tool in preference to any CLI equivalent (e.g., MCP `create_pull_request` over `gh pr create`). The server-specific codex lists available tools.

### Fallback behavior (common)

If the MCP server is unavailable mid-operation (network, auth expiration, tool missing):

1. Retry once after a brief backoff (the agent waits before retry; no busy loop).
2. If it still fails, the agent **MUST** inform the user: which server, which tool, observed error.
3. Offer explicit alternatives:
   - Use the CLI equivalent (if available) labelled as fallback.
   - Pause the flow until the user restores connectivity.
   - Abort the operation.
4. The agent **MUST NOT** silently fall back to CLI without surfacing the MCP unavailability.

See `lex-mcp` §4 for the full fallback law.

### Common failure signals

| Symptom | Likely cause | Action |
|---|---|---|
| 401 / 403 on first call | Missing / expired env var | Ask user to set/rotate the variable |
| 429 or explicit rate-limit | Too many calls | Back off, reduce batch size, re-queue |
| Timeout on every call | MCP server process not running | Restart the platform (Cursor/Claude Code) or check server startup logs |
| "Tool not found" | Server version mismatch or server not listed in `mcp.servers` | Confirm config; upgrade server package |

### When to add a new MCP server

1. Create `framework/mcp/<name>.json` with `cursor` and `claude-code` blocks.
2. Add `<name>` to `mcp.servers` in `.ahrena/.directives` when ready to use.
3. Create `codex-mcp-<name>.md` (server-specific: tool catalog + parameters + examples); reference **this codex** for common patterns.
4. Update `lex-mcp` examples if the new server introduces a novel authentication model.
5. If the server powers a new Kata, consider a read-only Kata first (`kata-mcp-<name>-read`) before any write pattern.
