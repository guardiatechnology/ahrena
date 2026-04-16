# Lexis: Mandatory Use of MCP Tools

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** MCP server tool usage by AI agents in Ahrena projects

## Purpose

MCP (Model Context Protocol) servers expose capabilities of external systems — such as GitHub, Notion, and Figma — directly to AI agents, with managed authentication and without the need to manually construct API calls. When an MCP server is active for an operation, using it is safer, more consistent, and more traceable than executing the equivalent CLI command.

This Lexis exists to ensure that **every agent prefers available MCP tools over CLI equivalents**, that **credentials are never exposed in tracked files**, and that **only servers declared in `.ahrena/.directives` are used**.

## Law

> **Every agent MUST use the available MCP tool when an active MCP server provides a capability for the current operation. Authentication credentials MUST be provided exclusively via environment variables. The agent MUST NOT use MCP servers not listed in `mcp.servers` in `.ahrena/.directives`.**

## Rules

### 1. Preference for MCP tools

When executing an operation supported by an active MCP server, the agent **MUST**:

1. Check whether the corresponding MCP server is listed in `mcp.servers` in `.ahrena/.directives`.
2. Use the MCP tool instead of the CLI equivalent (e.g., use GitHub MCP `create_pull_request` instead of `gh pr create`).
3. Consult the Codex for the corresponding MCP server (`codex-mcp-github`, `codex-mcp-notion`, `codex-mcp-figma`) to identify the correct tool and parameters.

### 2. Authentication exclusively via environment variables

The agent **MUST** ensure that:

1. Credentials (tokens, API keys) are provided only via environment variables referenced in MCP config files (`mcp.json`, `settings.json`).
2. No token, API key, or secret is written to `.ahrena/.directives`, to git-tracked files, or to any generated artifact.
3. If the required environment variable is not defined, the agent informs the user which variable to configure before proceeding.

### 3. Use restricted to declared servers

The agent **MUST NOT**:

1. Activate or use an MCP server not declared in `mcp.servers` in `.ahrena/.directives`.
2. Add MCP servers to platform configuration (`.cursor/mcp.json`, `.claude/settings.json`) without explicit user instruction.
3. Modify the `mcp.servers` section in `.ahrena/.directives` without explicit user request.

### 4. Fallback behavior when MCP is unavailable

If the required MCP server is unavailable mid-operation (server down, missing environment variable, unsupported tool, rate-limit, timeout):

1. **Retry once** with brief backoff (default: 5 seconds). Transient failures happen; a single retry avoids spurious escalation.
2. If the retry still fails, the agent **MUST** inform the user with structured context:
   - Which server (`github`, `notion`, `figma`).
   - Which tool was attempted.
   - Observed error (HTTP status, message).
3. The agent **MUST** then offer explicit choices — not pick silently:
   - **(a)** Use the CLI equivalent as fallback (when one exists and is safe), clearly labelled as fallback.
   - **(b)** Pause the flow until the user restores connectivity (credentials, server restart).
   - **(c)** Abort the operation with clear message.
4. The agent **MUST NOT** silently fall back to CLI without the choice surfaced in Step 3.
5. The agent **MUST NOT** enter a retry loop beyond Step 1 — persistent failure requires human decision.

Common failure signals and their typical cause are listed in `codex-mcp-common` — consult before surfacing to the user.

## Scope

- **Applies to:** all operations where an active MCP server provides a tool equivalent to the requested operation.
- **Bound agents:** all Warriors and generic agents.
- **Exceptions:** None. Lexis admit no exceptions.

## Consequences of Violation

1. **Exposed credentials:** hardcoding tokens in tracked files is a serious security violation; requires immediate rotation of the affected credential.
2. **Unauthorized servers:** using servers not declared violates the principle of least privilege and may expose project data to unapproved systems.
3. **Inconsistency:** mixing MCP and CLI for the same operation without criteria creates unpredictable results and hinders auditing.
4. **Remediation:** the agent must re-read the directives, identify the active MCP servers and the corresponding Codex, and repeat the operation using the correct MCP tool.

## Examples

### Correct

```
# mcp.servers in .ahrena/.directives lists "github"
# Agent creates PR via MCP:
create_pull_request(
  owner="acme",
  repo="my-project",
  title="feat: new feature",
  head="feat/new",
  base="main"
)
```

```
# Environment variable configured externally:
# export NOTION_API_KEY="secret_..."
# Agent creates Notion page via MCP:
create_page(parent={"database_id": "..."}, properties={...})
```

### Incorrect

```
# ❌ Hardcoding token in .directives or any tracked file:
# mcp_token: "ghp_abc123..."

# ❌ Using gh CLI when GitHub MCP is available and listed:
# gh pr create --title "feat: new" --base main

# ❌ Using an MCP server not listed in mcp.servers:
# (using an MCP server from a system not declared in the directives)
```

## Automated Validation

- **Tool:** verification by the agent itself before executing operations covered by MCP; `validate.py` checks that `mcp.servers` is present in `.directives` when MCP config files exist.
- **Timing:** when starting any operation involving GitHub, Notion, or Figma.
- **Metric:** 100% of operations covered by active MCP must use the MCP tool; 0 credentials in tracked files.
