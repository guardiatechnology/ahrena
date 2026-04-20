# Kata: Query projects and code on GitHub via MCP

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Reading repositories, issues, pull requests, commits, and code on GitHub via MCP server

## Objective

Fetch and read information from GitHub repositories (code, issues, PRs, commits, branches) via MCP server, bringing the data into the session context for reference, analysis, or review. This kata is strictly **read-only** — no files, issues, PRs, or branches are created or modified.

## When to Use

- When the user needs to inspect code from a GitHub repository without cloning it locally
- When open issues or PRs need to be consulted for context on a task
- When reviewing commit history or the branch structure of a repository
- When searching code across repositories for reference or comparison

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Repository | Yes | `owner/repo` (e.g., `guardiafinance/ahrena`) |
| Object | Yes | What to query: `code`, `issues`, `prs`, `commits`, `branches`, `file` |
| Query or path | Depends | Search term (for `code`), path (for `file`), filters (for `issues`/`prs`) |
| Branch | No | Reference branch; default: repository's default branch |

## Workflow

```
Progress:
- [ ] 1. Verify MCP preconditions and directives
- [ ] 2. Identify repository and query object
- [ ] 3. Fetch and read the content
- [ ] 4. Present result to user
```

### Step 1: Verify MCP preconditions and directives

1. Consult `.ahrena/.directives` per `lex-directives`.
2. Verify that `github` is listed in `mcp.servers` (per `lex-mcp`). If not, inform the user and stop.
3. Confirm that the `GITHUB_PAT` environment variable is defined. If not, inform the user which variable to configure and stop.
4. Consult `codex-mcp-github` to identify the correct tools and parameters.

### Step 2: Identify repository and query object

1. Confirm the repository (`owner/repo`) with the user — ask if not provided.
2. Identify the query object:
   - **`file`** — content of a file or directory listing
   - **`code`** — code search by term or pattern
   - **`issues`** — list or details of issues
   - **`prs`** — list or details of pull requests
   - **`commits`** — commit history for a branch
   - **`branches`** — available branches in the repository
3. If the object was not specified, ask the user which aspect of the repository they want to query.

### Step 3: Fetch and read the content

**Object `file`:**
1. Call `get_file_contents(owner, repo, path, branch)`.
2. If `path` is a directory, list the returned items and ask the user which file to expand.
3. If `path` is a file, present the full content with language highlighting.

**Object `code`:**
1. Call `search_code(query="{term} repo:{owner}/{repo}")`.
2. Present the matching files with relevant snippets.
3. For files of interest, call `get_file_contents` to retrieve the full content if the user requests it.

**Object `issues`:**
1. Call `list_issues(owner, repo, state, labels, assignee)` with filters provided by the user.
2. Present the list (number, title, state, labels, assignee, opened date).
3. If the user wants details on a specific issue, call `get_issue(owner, repo, issue_number)`.

**Object `prs`:**
1. Call `list_pull_requests(owner, repo, state, head, base)` with provided filters.
2. Present the list (number, title, state, head/base branch, author, date).
3. If the user wants details on a specific PR, call `get_pull_request(owner, repo, pull_number)`.

**Object `commits`:**
1. Call `list_commits(owner, repo, branch)`.
2. Present the history (abbreviated hash, message, author, date).
3. Default to the 20 most recent commits; ask the user if they want more.

### Step 4: Present result to user

1. Present the retrieved content in a structured, readable format.
2. For lists (issues, PRs, commits): use a table with the most relevant fields.
3. For files and code: preserve the original formatting with a code block and identified language.
4. Include the direct GitHub URL for each item when available in the tool response.

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| File content | Code block with identified language | Response to user |
| Code search results | List of files with relevant snippets | Response to user |
| Issues / PRs list | Table with relevant fields | Response to user |
| Commit history | Table (hash, message, author, date) | Response to user |

## Restrictions

- **Read-only:** this kata never creates branches, issues, PRs, comments, or pushes files.
- **Use MCP only:** never use the `gh` CLI or the GitHub REST API directly when the MCP server is active (per `lex-mcp`).
- **No hardcoded credentials:** authentication exclusively via `GITHUB_PAT` environment variable.
- **Confirm repository:** always confirm `owner/repo` with the user before starting the query.

## References

- `lex-mcp` — MCP tool usage laws
- `codex-mcp-github` — GitHub MCP tools and parameters reference
- `lex-directives` — How to read `.ahrena/.directives`
