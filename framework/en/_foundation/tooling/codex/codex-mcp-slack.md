# Codex: Slack MCP Server

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Tools and authentication for the Slack MCP server in Cursor and Claude Code

## Overview

This Codex is the reference for using the **Slack MCP server** in Ahrena projects. See `codex-mcp-common` for shared MCP patterns (authentication, configuration, fallback) and `codex-notifications` for the provider-agnostic contract that maps `notifications.provider: slack` to the tools listed here. This document focuses on tools, parameters, and use cases specific to Slack: sending framework event notifications (PR timeout, release, plans digest) and reading channel context when relevant.

## Context

- **Domain:** message send/read, search, canvas, and user profiles on Slack via MCP.
- **Audience:** AI agents (Athena, Janus, Eunomia) that publish notifications; agents that need to read targeted channel discussion context.
- **Update:** when Slack adds new tools to the MCP server, or when the OAuth app scope changes.
- **Official source:** [https://docs.slack.dev/ai/slack-mcp-server/](https://docs.slack.dev/ai/slack-mcp-server/)

## Content

### Per-platform configuration

Both platforms consume the **official remote Slack server** at `https://mcp.slack.com/mcp` (tier 1 of the transport preference defined in `lex-mcp` §5 — zero local dependency). Auth is **confidential OAuth 2.0**: on the first call, the user authenticates via browser using the Slack app's `client_id` + `client_secret`; the token is managed by the platform.

> Source: "Slack supports JSON-RPC 2.0 over Streamable HTTP. All requests should be sent to: `https://mcp.slack.com/mcp`" and "Slack supports confidential OAuth for MCP clients. You'll need to use your app's `client_id` and `client_secret`."

**Cursor (`.cursor/mcp.json`):**
```json
"slack": {
  "url": "https://mcp.slack.com/mcp"
}
```

**Claude Code (`.mcp.json`):**
```json
"slack": {
  "type": "http",
  "url": "https://mcp.slack.com/mcp"
}
```

No environment variables in `.directives` or in the JSON. No npx or binary fallback exists because Slack exposes **only** HTTP at this time (official: "We do not support SSE-based connections or Dynamic Client Registration at this time"). If the team needs an alternative path (CI without browser, programmatic integration), open an ADR recording the exception.

### Activation

```bash
# 1. List mcp.servers in .ahrena/.directives and uncomment "slack"
# 2. Enable via make:
make mcp-enable SERVER=slack

# 3. Reopen Cursor / Claude Code; on the first invocation, the OAuth flow opens in the browser.
```

### Exposed tools

Categories documented in the official overview:

| Category | Tools (representative names) | Typical framework usage |
|---|---|---|
| **Search** | `slack_search_messages`, `slack_search_files`, `slack_search_channels`, `slack_search_users` | Search prior discussion of a topic before notifying |
| **Messages** | `slack_send_message`, `slack_send_message_draft`, `slack_read_channel`, `slack_read_thread`, `slack_schedule_message` | Athena, Janus, Eunomia publish notifications via `slack_send_message` |
| **Canvas** | `slack_create_canvas`, `slack_read_canvas`, `slack_update_canvas` | Eunomia publishes the periodic digest as an updated canvas |
| **Profiles** | `slack_read_user_profile` | Resolve `@login` to display name in alerts |

> Exact names may vary by client; the Slack MCP server exposes the list via `tools/list` on first connection. Always consult the official docs for the canonical name in use.

### `slack_send_message` — canonical invocation

Primary tool consumed by `codex-notifications`. Relevant parameters:

| Parameter | Source | Example |
|---|---|---|
| `channel` | `notifications.channels.{event}` from `.ahrena/.directives` | `"notifications-gh-pull-request"` (no `#`) |
| `text` | Built by the agent per the template in `codex-notifications` §5 | Multiline with PR/Release link |
| `thread_ts` | (optional) To reply to an existing thread | — |

The agent reads the logical value from `.directives` and passes it **directly** as `channel`. Workspace channel names must match the logical channels. If the channel does not exist, the MCP returns a structured error — per `lex-mcp` §4, single retry + log + proceed.

### Logical channel → real Slack channel resolution

Ahrena framework convention:

| Logical key in `.directives` | Expected Slack workspace name |
|---|---|
| `notifications.channels.pr_review_timeout` | `notifications-gh-pull-request` |
| `notifications.channels.release_notify` | `notifications-gh-releases` |
| `notifications.channels.plans_status` | `notifications-plans-status` |

Teams may rename logical channels to match their internal naming (e.g.: `eng-pr-alerts`), provided they update `.ahrena/.directives` in the same step.

### OAuth authentication — first run

1. Agent invokes a Slack tool for the first time (e.g.: `slack_send_message`).
2. Cursor / Claude Code opens the browser in the Slack OAuth flow.
3. User authorizes the app in the corresponding workspace (scopes: read messages, send in channels, read profiles — per registered app).
4. Token stored by the platform (does not touch `.directives`).
5. Subsequent calls use the token automatically.

Per `lex-mcp` §2, **no** token, `client_id`, or `client_secret` ever goes into `.ahrena/.directives` or a versioned file. Slack app configuration happens once in the workspace, by the admin.

### Fallback when MCP is unavailable

For notifications, `codex-notifications` §4 defines the behavior:

1. Single retry (5s).
2. If still failing, structured log + proceed. The main flow (Athena finishing the review loop, Janus finishing the release, etc.) MUST NOT fail because of it.

For Slack context reads (less common use), apply standard `lex-mcp` §4: surface the 3 options to the user (CLI fallback when applicable — does not exist for Slack today; pause; abort).

## Restrictions

- **No stdio/npx**: the Slack MCP is HTTP-only at this time. Do not invent an npx fallback without an ADR.
- **No credentials in code/.directives**: per `lex-mcp` §2.
- **Do not confuse logical channels with IDs**: the agent passes the channel **name** (without `#`), not a `C0123...` ID. Slack MCP resolves internally.

## References

- [https://docs.slack.dev/ai/slack-mcp-server/](https://docs.slack.dev/ai/slack-mcp-server/) — official source
- `lex-mcp` — MCP usage rules (§5 transport preference HTTP > binary > npx)
- `codex-mcp-common` — shared patterns
- `codex-notifications` — provider-agnostic contract (primary consumer)
- `framework/mcp/slack.json` — config consumed by install
- `lex-directives` — `notifications:` section in `.ahrena/.directives`
- `warrior-athena`, `warrior-janus`, `warrior-eunomia` — tool consumers
