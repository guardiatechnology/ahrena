# Ahrena MCP server (spike)

Local MCP server that exposes the Ahrena framework as queryable tools for any MCP client (Claude Code, Cursor, custom agents).

> **Status: spike.** Not the final implementation described in `.claude/plans/plan-021-ahrena-mcp-server.md`. No issue, no branch, no PR — just enough to play. Read-only. No registration in `framework/platforms.yaml` or `scripts/install.py`.

## Tools exposed

| Tool | Purpose |
|---|---|
| `ahrena_query_lex` | Read a Lexis by name (e.g., `lex-idempotency`) |
| `ahrena_get_codex` | Read a Codex by name |
| `ahrena_list_warriors` | List warriors, optional `clade` filter |
| `ahrena_list_cries` | List cries (slash commands) |
| `ahrena_search` | Ranked search; optional `pilar` filter (`lexis`/`codex`/`katas`/`warriors`/`cries`) |
| `ahrena_resolve_ref` | Check if a ref exists; cross-lang fallback |
| `ahrena_get_directives` | Parsed `.ahrena/.directives` |

## Install

From the repo root (`tooling/ahrena/`):

```bash
pip install -e tools/ahrena-mcp
```

Optional but recommended: install ripgrep for fast search.

```bash
brew install ripgrep   # macOS
# Search falls back to a Python regex sweep if rg is missing.
```

## Run standalone (stdio)

```bash
python -m ahrena_mcp.server --root /Users/seguim/workspace/guardia/tooling/ahrena
```

Root discovery order: `--root` flag → `AHRENA_ROOT` env var → walk up from `cwd` looking for `.ahrena/`.

## Wire into Claude Code

Claude Code reads MCP servers from `.mcp.json` at the project root. Two files involved:

**1. `.mcp.json` at project root** — declares the server:

```json
{
  "mcpServers": {
    "ahrena": {
      "command": "/absolute/path/to/tools/ahrena-mcp/.venv/bin/python",
      "args": [
        "-m",
        "ahrena_mcp.server",
        "--root",
        "/absolute/path/to/ahrena/repo"
      ]
    }
  }
}
```

**2. `.claude/settings.json`** — pre-approves the server so Claude Code does not prompt on first use:

```json
{
  "enabledMcpjsonServers": ["ahrena"]
}
```

Restart Claude Code. The 7 tools listed above appear under `/mcp` and the agent can invoke them directly.

## Run tests

```bash
cd tools/ahrena-mcp
pytest
```

The smoke tests run against the actual `framework/` of this repo — no fixtures.

## Limits of this spike

- **Read-only.** No `ahrena_create_lex` / `ahrena_update_codex`.
- **Default language** read from `.ahrena/.directives.language.default`, falls back to `pt-BR`.
- **No registration** in `framework/platforms.yaml`, `framework/.directives.sample`, or `scripts/install.py`. Each consumer wires manually via `settings.json` (see above).
- **No frontmatter parsing** — tools return raw markdown.
- **Single instance.** Server is opt-in per project, started by the MCP client.
- **Cache:** in-memory only, invalidated on file `mtime` change.

## What this spike validates

1. The 8-tool surface from plan-021 is implementable in ~150 LOC of Python.
2. Search via `ripgrep` shell-out cumpre o budget de < 200ms folgado.
3. The wiring into Claude Code is purely an `.claude/settings.json` snippet — no kernel changes.
4. External agents (Strands, `apollo-agents`) can consume the same server without touching `.claude/`.

After validation, the formal flow (issue → branch → docs in 3 idiomas → `platforms.yaml` → `install.py` integration → PR) follows plan-021 step-by-step.
