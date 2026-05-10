# Codex: GitHub MCP Server

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Tools and authentication for the GitHub MCP server on Cursor and Claude Code

## Content

### Platform configuration

Both platforms consume the **official remote endpoint hosted by GitHub** at `https://api.githubcopilot.com/mcp/` (tier 1 of the transport preference declared in `lex-mcp` §5 — zero local dependency).

**Cursor (`.cursor/mcp.json`):**
```json
"github": {
  "url": "https://api.githubcopilot.com/mcp/",
  "headers": { "Authorization": "Bearer ${env:GITHUB_PAT}" }
}
```

**Claude Code (`.mcp.json`):**
```json
"github": {
  "type": "http",
  "url": "https://api.githubcopilot.com/mcp/",
  "headers": { "Authorization": "Bearer ${GITHUB_PAT}" }
}
```

> The `GITHUB_PAT` variable must be defined in the environment (classic or fine-grained PAT with repo scopes). Never hardcode tokens in tracked files (see `lex-mcp`).
>
> Intentional syntactic difference: Cursor uses `${env:VAR}` for environment variable interpolation; Claude Code uses `${VAR}`. Both forms resolve to the same runtime value.

#### Override for the legacy npx path

The npx package (`@modelcontextprotocol/server-github`) is deprecated but still functional. Teams that need it (air-gapped environments, tools coverage that has not landed in the hosted endpoint yet) can override the server JSON in `.ahrena/mcp/github.json` with a `_comment`-justified deviation per `lex-mcp` §5:

```json
{
  "_comment": "Override: using the npx @modelcontextprotocol/server-github package because <reason>. Decision recorded in ADR-NN.",
  "cursor": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${env:GITHUB_PAT}" }
  },
  "claude-code": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PAT}" }
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
