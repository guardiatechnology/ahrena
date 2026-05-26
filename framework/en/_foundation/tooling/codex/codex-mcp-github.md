# Codex: GitHub MCP Server

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Tools and authentication for the GitHub MCP server on Cursor and Claude Code

## Overview

This Codex is the reference for using the **GitHub MCP server** in Ahrena projects. See `codex-mcp-common` for shared MCP patterns (authentication model, configuration layout, fallback behavior, when-to-prefer-MCP rule). This document focuses on GitHub-specific tools, parameters, and examples. Consulted by Warriors and Katas that perform repository operations (issues, pull requests, branches, files, searches).

## Context

- **Domain:** GitHub repository operations via MCP (issues, PRs, branches, commits, files, searches, discussions).
- **Target audience:** AI agents that perform GitHub operations in Ahrena projects with the MCP server active.
- **Update:** When new tools are added to the GitHub MCP server or when parameters change.

## Content

### Platform configuration

Both platforms consume the **official remote endpoint hosted by GitHub** at `https://api.githubcopilot.com/mcp/` (tier 1 of the transport preference declared in `lex-mcp` §5 — zero local dependency).

**Cursor (`.cursor/mcp.json`):**
```json
"github": {
  "url": "https://api.githubcopilot.com/mcp/",
  "headers": { "Authorization": "Bearer ${env:GH_TOKEN}" }
}
```

**Claude Code (`.mcp.json`):**
```json
"github": {
  "type": "http",
  "url": "https://api.githubcopilot.com/mcp/",
  "headers": { "Authorization": "Bearer ${GH_TOKEN}" }
}
```

> The `GH_TOKEN` variable must be defined in the environment (classic or fine-grained PAT). The name matches the `gh` CLI convention and the GitHub MCP server's documented variable. Never hardcode tokens in tracked files (see `lex-mcp`).
>
> Intentional syntactic difference: Cursor uses `${env:VAR}` for environment variable interpolation; Claude Code uses `${VAR}`. Both forms resolve to the same runtime value.

#### Required OAuth scopes

A classic PAT used with the GitHub MCP must grant the following scopes for the full tool surface (issues, PRs, branches, workflows, user lookups):

| Scope | Why |
|---|---|
| `repo` | Read/write on issues, PRs, branches, files, commits |
| `read:org` | List organization teams, members, code owners |
| `workflow` | Read workflow runs, dispatch reruns (used by release/CI katas) |
| `read:user` | Resolve `@me` and assignee identities |

`scripts/install.py` verifies these scopes at install time when `GH_TOKEN` is set and emits one warn-only line per missing scope with a copy-paste hint: `gh auth refresh -s <scope>`. The check never blocks the install; network failures or fine-grained PATs (which do not expose the `X-OAuth-Scopes` header) fall back to a single advisory line.

#### Override for the legacy npx path

The npx package (`@modelcontextprotocol/server-github`) is deprecated but still functional. Teams that need it (air-gapped environments, tools coverage that has not landed in the hosted endpoint yet) can override the server JSON in `.ahrena/mcp/github.json` with a `_comment`-justified deviation per `lex-mcp` §5:

```json
{
  "_comment": "Override: using the npx @modelcontextprotocol/server-github package because <reason>. Decision recorded in ADR-NN.",
  "cursor": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${env:GH_TOKEN}" }
  },
  "claude-code": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GH_TOKEN}" }
  }
}
```

The override requires Node.js on the host; run `make mcp-enable SERVER=github PLATFORM=...` and the preflight will offer to install it when missing.

### Available tools

| Tool | Description |
|---|---|
| `create_issue` | Creates an issue in the repository |
| `list_issues` | Lists issues with filters (state, labels, assignee) |
| `get_issue` | Gets details of a specific issue |
| `add_issue_comment` | Adds a comment to an issue |
| `create_pull_request` | Creates a pull request |
| `list_pull_requests` | Lists PRs with filters (state, head, base) |
| `get_pull_request` | Gets details of a specific PR |
| `merge_pull_request` | Merges a PR |
| `create_branch` | Creates a new branch in the repository |
| `push_files` | Pushes one or more files to a branch |
| `get_file_contents` | Gets the content of a file or directory |
| `list_commits` | Lists commits from a branch |
| `search_repositories` | Searches repositories on GitHub |
| `search_code` | Searches code in repositories |
| `fork_repository` | Forks a repository |
| `create_repository` | Creates a new repository |

### Parameters for most-used tools

**`create_pull_request`**
```
owner         (string, required) — repository owner
repo          (string, required) — repository name
title         (string, required) — PR title
head          (string, required) — source branch
base          (string, required) — target branch (e.g., "main")
body          (string, optional) — PR description (Markdown)
draft         (boolean, optional) — create as draft
```

**`create_issue`**
```
owner         (string, required) — repository owner
repo          (string, required) — repository name
title         (string, required) — issue title
body          (string, optional) — description (Markdown)
labels        (array, optional)  — list of labels
assignees     (array, optional)  — list of assignees
```

**`push_files`**
```
owner         (string, required) — repository owner
repo          (string, required) — repository name
branch        (string, required) — target branch
message       (string, required) — commit message
files         (array, required)  — [{path, content}] — content as string
```

**`get_file_contents`**
```
owner         (string, required) — repository owner
repo          (string, required) — repository name
path          (string, required) — file or directory path
branch        (string, optional) — branch (default: default branch)
```

### When to use MCP vs `gh` CLI

See `codex-mcp-common` §"Preference over CLI" and §"Fallback behavior" for the general rule. Summary:

- Listed in `mcp.servers` + tool exists → MCP (mandatory per `lex-mcp`).
- MCP unavailable → surface to user + offer `gh` CLI as explicit fallback.
- Operation not covered by any MCP tool above → `gh` CLI or REST API directly.

### Usage example: create PR with structured body

```
create_pull_request(
  owner="acme",
  repo="my-project",
  title="feat(auth): implement OAuth2",
  head="feat/oauth2",
  base="main",
  body="## Summary\n\n- Adds OAuth2 flow with PKCE\n- Integrates with provider configured in `.env`\n\n## How to test\n\n1. Set `OAUTH_CLIENT_ID` and `OAUTH_CLIENT_SECRET`\n2. Run `make dev` and navigate to `/auth/login`",
  draft=False
)
```

## References

- `lex-mcp` — MCP tool usage laws
- `kata-mcp-notion-read` — Kata for querying Notion content (analogous pattern)
- `kata-mcp-github-read` — Kata for querying GitHub repositories and code (read-only)
- [GitHub MCP Server — official Go repository](https://github.com/github/github-mcp-server) (binary/HTTP server maintained by GitHub)
- [Claude Code — MCP documentation](https://code.claude.com/docs/en/mcp)
- `_foundation/contributing/katas/kata-contribute` — Contribution kata that uses GitHub MCP
