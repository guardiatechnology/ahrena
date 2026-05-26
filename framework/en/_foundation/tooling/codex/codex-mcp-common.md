# Codex: MCP — Common Patterns

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Cross-cutting patterns for any MCP (Model Context Protocol) server integration — preamble consumed by all `codex-mcp-{server}` references

## Overview

This Codex centralizes the conceptual and operational patterns shared by every MCP server integration in Ahrena (GitHub, Notion, Figma, and any new server added). Individual `codex-mcp-{server}` documents now focus on server-specific tools, parameters, and examples, delegating the common preamble to this file. The goal is to reduce token consumption when multiple MCP codexes are referenced in a single operation and to keep authentication, configuration, and fallback rules in sync across servers.

## Context

- **Domain:** any MCP server integrated in Cursor or Claude Code.
- **Audience:** Warriors and Katas invoking MCP tools; consulted alongside the server-specific codex.
- **Updates:** when the framework adds a new MCP server, introduces a new platform (beyond Cursor/Claude Code), or changes the auth pattern.

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

### Transport preference — trade-off rationale

`lex-mcp` §5 establishes the mandatory order when declaring an MCP server: **remote HTTP → native binary → npx**. Each tier adds a distinct class of local dependency. Trade-offs per tier:

| Tier | Local dep. | Latency | Updates | Version control | When to prefer |
|---|---|---|---|---|---|
| Remote HTTP | none | network + hosted server | vendor (server-side) | vendor | default when the vendor offers an official endpoint |
| Native binary stdio | installed executable | local stdio | versioned releases | user (chooses installed version) | no HTTP; vendor publishes an official binary |
| npx | Node.js + npm cache | local stdio with Node overhead | per execution (`npx -y`) | npm package | no HTTP and no official binary |

**Why HTTP is the default:**
- Zero local dependency — the user installs no runtime or binary; the server evolves without manual releases.
- Standardized auth via header (`Authorization: Bearer ...`) or per-user OAuth, both supported by the platforms (Cursor and Claude Code).
- Failures surface in clear HTTP status (401/403/429/5xx) with automatic exponential retry in the official clients.

**Why binary is the second choice:**
- Works offline and has minimal latency (no network hop).
- Offers precise version control — useful when the vendor introduces breaking changes between releases.
- Cost: the user must install/update manually (or via a package manager).

**Why npx is the last resort:**
- Drags Node.js as a transitive dependency — heavy runtime for a single use case.
- `npx -y` downloads/caches on every cold execution, introducing initial latency.
- Third-party npm packages can be archived or compromised without notice (supply chain is more fragile than vendor-hosted).

Deviations from the order (e.g., using npx when HTTP is available) **MUST** be justified in a `_comment` inside the server JSON — see example below. Common acceptable reasons: need for shared configuration via env var (instead of per-user OAuth), air-gapped environment, dependency on a feature present only in the lower tier.

```json
{
  "_comment": "Override: team prefers shared NOTION_API_KEY over the official HTTP endpoint's per-user OAuth. Decision recorded in ADR-NN.",
  "cursor": {
    "command": "npx",
    "args": ["-y", "@notionhq/notion-mcp-server"],
    "env": { "NOTION_API_KEY": "${env:NOTION_API_KEY}" }
  }
}
```

Docker is not part of the hierarchy today. When an MCP server in Docker is adopted, its tier **MUST** be defined by ADR (decision about overhead vs. isolation).

### Authentication — uniform rule

All MCP server credentials **MUST**:

1. Come exclusively from environment variables declared in the JSON template.
2. Use `${env:VAR_NAME}` in Cursor (MCP handles resolution) and `${VAR_NAME}` in Claude Code.
3. Never appear hardcoded in code, `.directives`, or any tracked artifact (see `lex-mcp`).

Standard variable names per server:

| Server | Env Var |
|---|---|
| GitHub | `GH_TOKEN` |
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

## References

- `lex-mcp` — unbreakable laws on MCP tool usage
- `codex-mcp-github`, `codex-mcp-notion`, `codex-mcp-figma` — server-specific references
- [Model Context Protocol spec](https://modelcontextprotocol.io/)
