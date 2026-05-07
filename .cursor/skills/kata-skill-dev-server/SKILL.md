---
name: kata-skill-dev-server
description: "Local skill dev server (widgets HMR + script runner + tools stub). Bring up the local development environment for a skill project at {paths.skills_root}/{slug}/, with widgets in HMR (Vite), HTTP/JSON script runner, and MCP tool stub, per codex-skill-build-pipeline"
---

# Kata: Local skill dev server (widgets HMR + script runner + tools stub)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Bring up the local development environment for a skill project at `{paths.skills_root}/{slug}/`, with widgets in HMR (Vite), HTTP/JSON script runner, and MCP tool stub, per `codex-skill-build-pipeline`

## Workflow

```
Progress:
- [ ] 1. Resolve project and config
- [ ] 2. Verify preconditions (paths, manifests, free ports)
- [ ] 3. Bring up widgets (Vite dev) when applicable
- [ ] 4. Bring up the script runner when applicable
- [ ] 5. Bring up the tool stub when applicable
- [ ] 6. Report URLs and instructions
- [ ] 7. Track until the user signals to stop
```

### Step 1: Resolve project and config

1. Read `.ahrena/.directives` to resolve `paths.skills_root` (default `skills`)
2. Confirm that `{paths.skills_root}/{slug}/` exists; abort if not
3. Read `{paths.skills_root}/{slug}/skill.config.json`; apply input overrides over the file values
4. Resolve subsets via `only` or by the presence of `widgets/`, `scripts/`, `tools/`

### Step 2: Verify preconditions

1. For widgets: confirm `widgets/package.json`, `widgets/manifest.json`, `widgets/src/`; check whether `node_modules/` exists (run `npm install` or `pnpm install` when absent)
2. For scripts (Python): confirm `scripts/pyproject.toml` or `scripts/uv.lock` (run `uv sync` when needed)
3. For scripts (JS): confirm `scripts/package.json`; run install if absent
4. For tools: confirm `tools/mcp.config.json` is valid (JSON Schema of each tool); confirm handler refs exist
5. Verify port availability (lsof / netstat per `lex-terminal-type`); if occupied, suggest an override

### Step 3: Bring up widgets (Vite dev) when `widgets/` exists and `only` allows

1. Command: `cd {paths.skills_root}/{slug}/widgets && vite --port {widgets_port} --host`
2. Vite loads `vite.config.ts` (if it exists) or uses defaults; React + TS detected automatically
3. HMR active; logs propagated to the user
4. Exposed URL: `http://localhost:{widgets_port}/`

### Step 4: Bring up the script runner when `scripts/` exists and `only` allows

The script runner is a minimal HTTP/JSON server that exposes each script as an endpoint:

| `runtimes.scripts` | Default implementation | Command |
|--------------------|------------------------|---------|
| `python` | `uv run` + lightweight server (FastAPI or stdlib http.server) | `cd {paths.skills_root}/{slug}/scripts && uv run python -m skill_runner --port {scripts_port}` (the `skill_runner` module is part of the scaffold when the author chooses Python; when absent, the kata points the author to `codex-skill-build-pipeline`) |
| `node` | Express/Fastify/server stdlib | `cd {paths.skills_root}/{slug}/scripts && npm run dev:server -- --port {scripts_port}` |

Routing:

- Each file in `scripts/src/` exports a named handler function
- Default endpoint: `POST /{filename-without-extension}`
- Body: JSON validated by the runner against the schema (when declared in `widgets/manifest.json`)

Exposed URL: `http://localhost:{scripts_port}/`

### Step 5: Bring up the tool stub when `tools/` exists and `only` allows

The tool stub is a locally mocked MCP server:

1. Reads `tools/mcp.config.json`
2. For each declared tool, exposes the endpoint `POST /tools/{tool_name}`
3. Default response: echo of the input with the `_stub: true` flag; the author overrides it in `tools/handlers/{tool_name}_stub.py` (or `.js`) when specific behavior is needed
4. Exposed URL: `http://localhost:{tools_stub_port}/`

The tool stub is exclusive to dev — `kata-build-skill` (Phase 4) validates the real handler, not the stub.

### Step 6: Report URLs and instructions

At the end of bring-up:

```
✅ Dev server active for {slug}:
   Widgets:      http://localhost:{widgets_port}/        (Vite HMR)
   Script runner: http://localhost:{scripts_port}/       (Python uv)
   Tool stub:    http://localhost:{tools_stub_port}/    (MCP mock)

Bindings from widgets/manifest.json:
   - TransferForm → tool: validate_amount    (stub at /tools/validate_amount)
   - TransferForm → script: scripts/src/format_currency.py (at /format-currency)

To stop: Ctrl-C in this terminal.
To build: /cry-skill-build {slug}
```

### Step 7: Track until the user stops

1. Keep the Vite process in the foreground (main HMR); script runner and tool stub in the background when supported by the terminal
2. Logs from each server are prefixed (`[widgets]`, `[scripts]`, `[tools]`) to ease diagnosis
3. On a crash of any subprocess, report and offer to restart
4. Ctrl-C cleanly terminates all subprocesses

## Outputs

| Output | Format |
|--------|--------|
| Success | Active URLs + foreground with logs until the user interrupts |
| Failure (project does not exist) | Message citing `lex-skill-project-structure` |
| Failure (port occupied) | Message instructing override via `--*_port` |
| Failure (invalid manifest) | Message citing `codex-skill-tools-and-widgets` with the violated rule |
| Failure (dependency not installed) | Message instructing `uv sync` / `npm install` in the corresponding directory |

## Execution Example

```
/cry-skill-dev hello-skill
```

```
✅ Dev server active for hello-skill:
   Widgets:      http://localhost:5173/
   Tool stub:    http://localhost:5175/
   (no scripts/ — skipped)

Press Ctrl-C to terminate.
```

## Restrictions

- Does not modify `skills/{slug}/` (read only)
- Does not write to `.build/` or `.dist/`
- Tool stub is a **mock**; never used in production
- Default ports are opinionated; an override is always allowed
- Logs respect `lex-logging-decorator` when integrated; the kata's CLI boot is a permitted exception (application boundary)
- `lex-terminal-type`: shell commands respect the terminal defined in `.directives` (bash | powershell)
