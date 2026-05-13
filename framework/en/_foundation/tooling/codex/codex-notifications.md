# Codex: Provider-Agnostic Notifications via MCP

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Notification delivery by agents (Athena, Argos, Janus, Eunomia) via the notification MCP server configured in `.ahrena/.directives`

## Overview

This Codex is the canonical manual for notifications in the Ahrena framework. It defines the contract between agents that publish alerts (Athena on PR review timeout, Janus on release publish, Eunomia on plans status digest) and the concrete provider (Slack, Discord, Teams) — without tying Lexis, Codex, or Warriors to a specific vendor.

The rule is simple: agents reference **abstract keys** (`notifications.provider` + `notifications.channels.{event}`) read from `.ahrena/.directives`; this Codex translates those keys into the corresponding MCP tool at runtime.

## Context

- **Domain:** notification delivery to corporate communication channels (Slack/Discord/Teams) by framework AI agents.
- **Audience:** Athena, Argos, Janus, Eunomia, and any agent that has a notification trigger in the Issue-Driven flow.
- **Update:** when a new provider is added to the framework, or when a new logical channel key (`notifications.channels.*`) is defined.

## Content

### 1. Abstract keys in `.ahrena/.directives`

The `notifications:` section in `.directives` (per `lex-directives`) declares:

```yaml
notifications:
  provider: slack                # slack | discord | teams | none
  channels:
    pr_review_timeout: "notifications-gh-pull-request"
    release_notify:    "notifications-gh-releases"
    plans_status:      "notifications-plans-status"
  working_hours:
    start: "07:00"
    end:   "22:00"
    timezone: "America/Sao_Paulo"
```

| Key | Consumer | When it fires |
|---|---|---|
| `notifications.channels.pr_review_timeout` | `warrior-athena` | The 3×15min wait cycles elapse without human approval on a PR in `to review` |
| `notifications.channels.release_notify` | `warrior-janus` | Release published (tag pushed, `validate-tag.yml` passed, GitHub Release created) |
| `notifications.channels.plans_status` | `warrior-eunomia` | Periodic active-plans digest from the PM loop |

### 2. Provider → MCP tool mapping

Each provider exposes its own MCP toolset. The agent reads `notifications.provider` and selects the corresponding tool:

| `provider` | MCP tool used | Provider manual |
|---|---|---|
| `slack` | `slack_send_message` | `codex-mcp-slack` |
| `discord` | (future — `discord_post_message`) | (future `codex-mcp-discord`) |
| `teams` | (future — `teams_post_message`) | (future `codex-mcp-teams`) |
| `none` | none — agent logs warning and proceeds | — |

When a new provider enters the framework, this Codex gains a row; no Lex/Warrior/Kata changes.

### 3. Logical channel → real channel resolution

The key `notifications.channels.pr_review_timeout` carries the **logical name** ("notifications-gh-pull-request" in the example). The agent passes that value directly to the `channel` parameter of the corresponding MCP tool. Provider-specific mappings (e.g.: Slack accepts the channel name without `#`; Discord uses numeric ID) are documented in `codex-mcp-{provider}`.

### 4. Canonical publication flow

```
1. Agent decides to notify (Athena after 3rd cycle, Janus on release, etc.)
2. Agent reads notifications.provider from .ahrena/.directives
3. If provider == "none" → log warning + proceed (do not fail)
4. Verify provider is in mcp.servers and MCP is active
5. Read notifications.channels.{event} (logical channel)
6. Invoke provider's MCP tool with (channel=<logical>, text=<msg>)
7. On MCP error: single retry (5s), then log + proceed
```

Principles:

- **provider == none**: the agent MUST NOT fail the main flow because of the notification. Log a structured warning and continue.
- **MCP unavailable**: per `lex-mcp` §4, single retry; if it still fails, surface the 3 options (CLI fallback when applicable, pause, abort). For notifications, the default is "log + proceed" because the main flow already completed.
- **Working window**: `notifications.working_hours` applies to non-critical digests (Eunomia). Event notifications (PR timeout, release) ignore the window.

### 5. Message content

The minimum payload includes enough context for the channel to act without opening GitHub:

**PR review timeout (Athena):**

```
🟡 PR waiting for review for 45min with no human approval
Repo: {owner/repo}  •  PR: #{N}  •  Author: @{login}
Reviewers requested: @{a}, @{b}
Status: {gh pr view --json reviewDecision}
Link: https://github.com/{owner/repo}/pull/{N}
```

**Release published (Janus):**

```
🚀 Release {tag} published in {repo}
Type: {patch|minor|major}
Highlights: {top 3 CHANGELOG entries}
Link: https://github.com/{owner/repo}/releases/tag/{tag}
```

**Plans status digest (Eunomia):**

```
📋 Active plans digest — {date}
 stalled  ⚠️  3 plans with no heartbeat for >4h
 healthy 🟢 12 plans in motion (last_activity < 30min)
 blocked 🚫 1 plan in changes-requested for >24h
[see details in the attachment / link]
```

Messages must be **direct**, **actionable**, and **self-contained** — per `lex-brand-voice`.

### 6. Switching providers

Switching provider is **3 steps** (zero edit to Lex/Codex/Warrior/Kata):

1. Add `framework/mcp/{new}.json` per `lex-mcp` §5 (prefer HTTP > binary > npx).
2. Enable via `make mcp-enable SERVER={new}`.
3. Edit `notifications.provider` in `.ahrena/.directives` to the new value.

Logical channels (`notifications.channels.*`) can be kept or renamed to match the new provider's convention.

## Restrictions

- **Do not name the concrete provider in Lexis/Warriors/Katas.** Only `notifications.provider` and `notifications.channels.{key}`.
- **Do not store credentials in `.directives`.** Per `lex-mcp` §2, credentials go in environment variables.
- **Do not attempt notifications before the MCP is listed in `mcp.servers`.** Per `lex-mcp` §3.

## References

- `lex-mcp` — MCP usage rules (transport preference, fallback, authentication)
- `lex-directives` — schema of the `notifications:` section in `.ahrena/.directives`
- `codex-mcp-common` — shared MCP patterns
- `codex-mcp-slack` — initial provider (Slack)
- `lex-agent-planning` — owners of the transitions that fire notifications
- `lex-brand-voice` — message tone
- `warrior-athena`, `warrior-janus`, `warrior-eunomia` — consumers of this Codex
