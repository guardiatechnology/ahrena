# Codex: Ahrena MCP Server

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Internal MCP server of the Ahrena framework for Cursor and Claude Code

## Content

### Platform configuration

The canonical configuration lives in `framework/mcp/ahrena.json`. `install.py` merges it into:

**Cursor (`.cursor/mcp.json`):**
```json
"ahrena": {
  "command": "ahrena-mcp",
  "args": ["--root", "${workspaceFolder}"]
}
```

**Claude Code (`.mcp.json` at the project root + `enabledMcpjsonServers` in `.claude/settings.json`):**
```json
"ahrena": {
  "command": "ahrena-mcp",
  "args": ["--root", "${workspaceFolder}"]
}
```

> The `ahrena-mcp` command is the console script declared in `tools/ahrena-mcp/pyproject.toml` (`[project.scripts]`). It becomes available on `PATH` after `install.py` runs `pipx install -e .ahrena/tools/ahrena-mcp` (see §Installation). The default-on path requires no dependency on PyPI or on `uv`/`uvx`.

### Available tools

| Tool | Description |
|---|---|
| `ahrena_query_lex` | Returns the full markdown of a Lexis (e.g., `lex-idempotency`) |
| `ahrena_get_codex` | Returns the full markdown of a Codex (e.g., `codex-restful-apis`) |
| `ahrena_list_warriors` | Lists warriors; optional `clade` filter (e.g., `engineering`) |
| `ahrena_list_cries` | Lists cries (slash commands) registered in the framework |
| `ahrena_search` | Ranked search across the entire framework; `pilar` and `lang` filters |
| `ahrena_resolve_ref` | Checks whether a ref exists (e.g., `lex-idempotency`); cross-language fallback |
| `ahrena_get_directives` | Returns the parsed `.ahrena/.directives` |

### Tool parameters

**`ahrena_query_lex`**
```
name (string, required) — short name of the Lex (e.g., "lex-idempotency")
lang (string, optional) — BCP 47 code; default: language.default from .directives
```

**`ahrena_get_codex`**
```
name (string, required) — short name of the Codex
lang (string, optional) — default: language.default from .directives
```

**`ahrena_list_warriors`**
```
clade (string, optional) — filter by clade (e.g., "engineering"); empty = no filter
lang  (string, optional) — default: language.default
```

**`ahrena_list_cries`**
```
lang (string, optional) — default: language.default
```

**`ahrena_search`**
```
query (string, required)  — search term
pilar (string, optional)  — "lexis" \| "codex" \| "katas" \| "warriors" \| "cries"; empty = all
lang  (string, optional)  — default: language.default
limit (integer, optional) — default: 30
```

Output: ranked list by number of matches in the file, with `artifact`, `pilar`, `lang`, `path`, `line`, `snippet`, `score`.

**`ahrena_resolve_ref`**
```
ref  (string, required) — short name (e.g., "lex-idempotency")
lang (string, optional) — default: language.default
```

Output: `{exists, name, pilar, lang, path}`. When the ref exists in another language but not in the requested one, the result includes a `warning` key indicating the fallback.

**`ahrena_get_directives`**
No parameters. Returns the parsed YAML of `.ahrena/.directives`.

### When to use (and when not)

**Use the `ahrena` tools when:**
- The agent must consult **one** specific Lexis or Codex mid-session (without inflating context via `@` import of the entire file).
- The agent must run a cross-pilar search (`circuit breaker` across any artifact; ranking by score).
- The agent is external to Cursor/Claude Code and has no access to the mirrors in `.cursor/`/`.claude/` (e.g., Strands, CI scripts, `apollo-agents`).
- The agent must resolve a ref deterministically (does `lex-idempotency` exist? at which path?).

**Do NOT use `ahrena` for:**
- Loading **many** artifacts at once — reading the filesystem directly is more efficient.
- Mutating framework artifacts. The server is read-only by design (write tools such as `ahrena_create_lex` are out of scope in the first iteration).
- Replacing the Lexis with `alwaysApply: true` that Cursor/Claude Code load at boot — those remain the native eager-governance mechanism.

### Installation

#### Standard adoption (default-on, via `install.py`)

Every adoption of the Ahrena framework activates `ahrena` automatically. `scripts/install.py` handles everything:

1. **Copies the package source** — `tools/ahrena-mcp/` (from the Ahrena source repo) is copied to `.ahrena/tools/ahrena-mcp/` in the adopter project, excluding `.venv` and caches.
2. **Installs via `pipx`** — `pipx install -e .ahrena/tools/ahrena-mcp`. The `ahrena-mcp` console script (declared in `pyproject.toml`) becomes available on `PATH`.
3. **Merges MCP configs** — `framework/mcp/ahrena.json` is merged into `.cursor/mcp.json` (Cursor) and `.mcp.json` at the root + `enabledMcpjsonServers: ["ahrena"]` in `.claude/settings.json` (Claude Code).
4. **Activation prerequisite** — `framework/.directives.sample` lists `mcp.servers: [ahrena]` uncommented by default; when `ahrena` is in `mcp.servers`, the steps above run.

The adopter runs `make install` (or the equivalent `python3 .ahrena/install.py`) — done. After restarting the MCP client (Claude Code/Cursor), the 7 `ahrena_*` tools appear.

**Re-install / update behavior:**
- First time (not installed): silent `pipx install`.
- Already installed + interactive session: prompt `[y/N]` to reinstall (default-no, preserves).
- Already installed + non-TTY (CI): preserves without prompt.

**Opt-out:** comment the `- ahrena` line in `.ahrena/.directives` before the install. To deactivate post-install: run `scripts/uninstall.py` (which calls `pipx uninstall ahrena-mcp` best-effort) or remove `ahrena` from `enabledMcpjsonServers` in `.claude/settings.json` + from `mcpServers` in `.cursor/mcp.json` and `.mcp.json`.

#### When `pipx` is unavailable

`install.py` detects the absence of `pipx` on `PATH`, prints `WARNING` to `stderr` with the installation link ([pipx.pypa.io](https://pipx.pypa.io/stable/installation/)), and continues (non-fatal). Paths to unblock:

1. **Install pipx and re-run `install.py`** (recommended): `brew install pipx` (macOS), `python3 -m pip install --user pipx` + `python3 -m pipx ensurepath` (Linux/Windows).
2. **Install manually without pipx**: `pip install --user .ahrena/tools/ahrena-mcp` and adjust `PATH` to include `~/.local/bin` (Linux/macOS) or `%APPDATA%\Python\Scripts` (Windows). The `command: ahrena-mcp` in `.mcp.json` remains valid.

#### External adopter without framework installed (post-release)

For agents or scripts that do **not** run `install.py` (Strands in a non-Ahrena project, ad-hoc CI), see `.claude/plans/plan-021-ahrena-mcp-server.md` §Release & Distribution. After release v1 (PyPI), the recommended path is `uvx ahrena-mcp --root <ahrena-repo>` (zero-install) or `pipx install ahrena-mcp` (persistent). Pre-release, `pipx install --spec <github-release-url> ahrena-mcp`.

### Performance

Measurements from the spike (759 artifacts × 3 languages):

| Operation | Typical latency |
|---|---|
| Server boot (cold) | ~1.0 s (Python + imports + initial scan) |
| Subsequent boot in session (warm cache) | < 50 ms |
| `ahrena_query_lex` (cache hit) | < 1 ms |
| `ahrena_search` (with `ripgrep`) | 80–100 ms |
| `ahrena_search` (Python regex fallback) | 200–500 ms |

Recommendation: install `ripgrep` on the host (`brew install ripgrep`) for the fast path. Without ripgrep, the server falls back to the Python implementation — it works, but slower on large frameworks.

### `--root` discovery

The server discovers the Ahrena framework root in this order:

1. `--root <path>` flag on invocation.
2. Environment variable `AHRENA_ROOT`.
3. Walk-up from `cwd` looking for the `.ahrena/` directory.

When the server starts inside an Ahrena project, the walk-up finds `.ahrena/` automatically. Adopters running the server from outside the project must use `--root` or `AHRENA_ROOT`.

### Known limitations (initial spike)

- **No `ahrena_get_topology`** until `docs/internal/warrior-topology-2026.md` exists (depends on plan-011).
- **Cache only by `mtime` on already-indexed files** — `loader.get()` re-scans when the `mtime` changes, but **does not detect new files or deletions** during a long server session (the index is built at boot and updated per individual file). In practice this rarely matters (framework artifacts change little intra-session); when it does, restarting the MCP client recreates the index.
- **No frontmatter parsing** — tools return raw markdown. Filtering by metadata (e.g., `alwaysApply: true`) is the consumer's responsibility.
- **Cross-language search may have partial dedup** — a term present in pt-BR and English appears twice in the hits list (once per language) when `lang` is not specified.

## Restrictions

- **Read-only.** Mutation of Lexis/Codex/Katas/Warriors/Cries via MCP is out of scope. To create artifacts, use the framework's cries (`/cry-new-lex`, `/cry-new-codex`, etc.).
- **Does not replace `lex-mcp`.** The server is subject to `lex-mcp` rule 3 (declared in `mcp.servers`) — `.directives.sample` already complies.
- **A pinned absolute path breaks when the repo moves.** When using a local override with `command: python -m ahrena_mcp.server`, the venv where the package is installed must stay at the agreed-upon path.
