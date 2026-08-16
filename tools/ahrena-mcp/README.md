# Ahrena MCP server

Local MCP server that exposes the Ahrena framework (Lexis, Codex, Katas, Warriors, Cries) as read-only queryable tools for any MCP client (Claude Code, Cursor, external agents).

**Default-on in every project that adopts Ahrena.** The framework's `scripts/install.py` copies this package source into `.ahrena/tools/ahrena-mcp/` and runs `pipx install --force <path>` so the `ahrena-mcp` console script lands on `PATH` as a self-contained install. The companion codex at [`framework/{lang}/_foundation/tooling/codex/codex-ahrena-mcp.md`](../../framework/pt-BR/_foundation/tooling/codex/codex-ahrena-mcp.md) is the canonical user-facing manual; this README is the package's technical entry point.

## Tools exposed

| Tool | Purpose |
|---|---|
| `ahrena_query_lex` | Read a Lexis by name (e.g., `lex-idempotency`) |
| `ahrena_get_codex` | Read a Codex by name |
| `ahrena_list_warriors` | List warriors, optional `clade` filter |
| `ahrena_list_cries` | List cries (slash commands) |
| `ahrena_search` | Ranked search; optional `pilar` filter (`lexis`/`codex`/`katas`/`warriors`/`cries`) |
| `ahrena_resolve_ref` | Check if a ref exists; cross-language fallback |
| `ahrena_get_directives` | Parsed `.ahrena/.directives` |

`ahrena_get_topology` is reserved for when `docs/internal/warrior-topology-2026.md` exists (per plan-011); not shipped in this iteration.

## Install

### Canonical path (adopter project)

Adopters do not install this package directly. Running the framework's installer is enough:

```bash
python3 scripts/install.py --target <project-dir> --platform claude-code
# or, after the framework is already in the project:
make -f .ahrena/Makefile install
```

`install.py` copies `tools/ahrena-mcp/` into `.ahrena/tools/ahrena-mcp/`, runs `pipx install --force <path>`, and merges `framework/mcp/ahrena.json` into the platform configs (`.cursor/mcp.json`, root `.mcp.json`, `.claude/settings.json` `enabledMcpjsonServers`). pipx copies the package into its managed environment, so removing or regenerating the project-local `.ahrena/` directory does not break the machine-wide command. Restart the MCP client; the 7 `ahrena_*` tools appear.

`pipx` is required for the canonical path. When `pipx` is missing, `install.py` prints a `WARNING` to `stderr` and continues — the rest of the framework install completes, and the user gets clear instructions to install pipx and re-run. See the codex for fallback paths (`pip install --user`, manual `PATH` adjustment).

### Development path (contributors)

When editing this package inside the Ahrena source repo:

```bash
pip install -e tools/ahrena-mcp
# or:
pipx install --force -e tools/ahrena-mcp
```

These editable commands are development-only. The adopter installer deliberately uses a non-editable pipx install so its machine-wide command never depends on a project-local source directory.

Optional but recommended: `brew install ripgrep` (or your OS equivalent). Without `rg`, search falls back to a slower Python regex sweep.

## Run standalone (stdio)

After install, the binary is on `PATH`:

```bash
ahrena-mcp --root <path-to-ahrena-repo-or-adopter-project>
# or rely on env / cwd walk-up:
AHRENA_ROOT=<path> ahrena-mcp
cd <project-with-.ahrena/> && ahrena-mcp
```

Root discovery order: `--root` flag → `AHRENA_ROOT` env var → walk up from `cwd` looking for `.ahrena/`. The loader accepts either source-repo layout (`<root>/framework/`) or adopter layout (`<root>/.ahrena/framework/`), preferring the adopter copy when both exist.

## Wire into Claude Code

`install.py` does this automatically. The output is equivalent to writing these two files manually:

**`.mcp.json` at the project root** — declares the server:

```json
{
  "mcpServers": {
    "ahrena": {
      "command": "ahrena-mcp",
      "args": ["--root", "${workspaceFolder}"]
    }
  }
}
```

**`.claude/settings.json`** — pre-approves the server so Claude Code does not prompt on first use:

```json
{
  "enabledMcpjsonServers": ["ahrena"]
}
```

If you need to wire manually outside `install.py` (e.g., a venv that is not on `PATH` for some reason), use placeholders — `<path-to-venv-python>` is the Python interpreter with `ahrena-mcp` installed, and `<path-to-ahrena-repo>` is the framework root to query:

```json
{
  "mcpServers": {
    "ahrena": {
      "command": "<path-to-venv-python>",
      "args": ["-m", "ahrena_mcp.server", "--root", "<path-to-ahrena-repo>"]
    }
  }
}
```

Restart Claude Code. The 7 tools listed above appear under `/mcp`.

## Run tests

```bash
cd tools/ahrena-mcp
pytest
```

The suite includes:

- `test_smoke.py` — loader, search, and pilar filtering against the live framework, plus adopter-layout discovery
- `test_install_mcp.py` — regression suite for the install_mcp merger (preservation, idempotency, `enabledMcpjsonServers: true`)
- `test_parse_directives.py` — regression suite for the YAML-like parser (nested lists, comments, multi-level dict nesting)

## Known limitations

- **Read-only.** No `ahrena_create_lex` / `ahrena_update_codex`. Mutation tools are deliberately out of scope in the first iteration.
- **Default language** is read from `.ahrena/.directives.language.default`; falls back to `pt-BR` when the directives are absent or unparseable (a `WARNING` is printed to `stderr` in the latter case).
- **No frontmatter parsing** — tools return raw markdown. Filtering by metadata (e.g., `alwaysApply: true`) is the consumer's responsibility.
- **Cache only by `mtime` on already-indexed files** — `loader.get()` re-scans when a file's `mtime` changes, but does not detect new files or deletions during a long server session. Restart the MCP client to recreate the index.
- **Single instance per project** — the server is started and torn down by the MCP client (stdio transport).

## What this server gives you

1. Token efficiency: surgical reads of specific Lexis/Codex without `@`-importing whole files into context.
2. External agent enablement: Strands, `apollo-agents`, CI scripts can consume the framework via standard MCP without a `.claude/` mirror.
3. Ranked cross-pilar search: `ahrena_search("circuit breaker")` returns hits across all pilars with snippet + score; grep can't.
4. Deterministic ref resolution: `ahrena_resolve_ref("lex-idempotency")` returns existence + path + pilar without textual fuzziness.

## See also

- Plan: [`.claude/plans/plan-021-ahrena-mcp-server.md`](../../.claude/plans/plan-021-ahrena-mcp-server.md) — full design, §Release & Distribution, §Architecture
- Codex (pt-BR canonical): [`framework/pt-BR/_foundation/tooling/codex/codex-ahrena-mcp.md`](../../framework/pt-BR/_foundation/tooling/codex/codex-ahrena-mcp.md)
- Translations: [`framework/es/`](../../framework/es/_foundation/tooling/codex/codex-ahrena-mcp.md) · [`framework/en/`](../../framework/en/_foundation/tooling/codex/codex-ahrena-mcp.md)
- MCP config template: [`framework/mcp/ahrena.json`](../../framework/mcp/ahrena.json)
- Changelog: [`CHANGELOG.md`](CHANGELOG.md)
