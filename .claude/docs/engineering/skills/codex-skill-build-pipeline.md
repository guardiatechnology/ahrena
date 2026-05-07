# Codex: Skill Build Pipeline (Ahrena)

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Deterministic pipeline that reads `skills/{slug}/`, validates manifests, builds widgets, freezes scripts, validates tools, and emits `.build/{slug}/` + `.build/{slug}.zip`

## Content

### Tooling defaults

| Layer | Tool | Target version | Justification |
|-------|------|----------------|---------------|
| Widgets bundler | **Vite** | 5.x | Speed, zero-config for React + TS, multi-format output, dev server with HMR |
| JS runtime for scripts | **Node** | 20 LTS | Stable, native ESM support |
| Python runtime for scripts and handlers | **uv** + **Python 3.12** | uv ≥ 0.4 | Aligned with `codex-python-tooling`; reproducible and fast install |
| Final packager | POSIX `zip` (BSD/Info-ZIP) | any | Testable zip delivery; `kata-package-skill` (PR 3) defines the final `.skill` format |

`skill.config.json` allows per-project override (`build.bundler`, `runtimes.scripts`); the pipeline rejects inconsistent combinations (e.g., `widgets/` present without a supported bundler).

### Default ports on the dev server

| Server | Default port | Override | Function |
|--------|-------------:|----------|----------|
| Widgets HMR (Vite) | `5173` | `dev_server.widgets_port` | Rendering and hot reload |
| Script runner | `5174` | `dev_server.scripts_port` | HTTP/JSON endpoints exposing `scripts/` to widgets |
| MCP tool stub | `5175` | `dev_server.tools_stub_port` | Local mock of tools declared in `tools/mcp.config.json` |

`kata-skill-dev-server` brings up the three on demand (only those needed by the skill under development).

### Pipeline — phases

```
skills/{slug}/                                    .build/{slug}/
   │
   ├─ Phase 1: Validate
   │     ├─ SKILL.md frontmatter (codex-skill-anthropic-agent-skills)
   │     ├─ skill.config.json (schema_version, runtimes, ports)
   │     ├─ tools/mcp.config.json (handler refs exist, valid JSON Schema)
   │     └─ widgets/manifest.json (entries exist, consistent bindings)
   │
   ├─ Phase 2: Build widgets (when widgets/ exists)
   │     ├─ vite build --mode production
   │     ├─ output in .build/{slug}/widgets/
   │     └─ manifest.json rewritten to point to compiled entries
   │
   ├─ Phase 3: Freeze scripts (when scripts/ exists)
   │     ├─ Python: uv lock → copy src + uv.lock to .build/{slug}/scripts/
   │     ├─ JS: npm/pnpm lock + copy src + lockfile
   │     └─ paths in scripts preserved (not compiled)
   │
   ├─ Phase 4: Resolve tools (when tools/ exists)
   │     ├─ validates each handler ref (path:function exists)
   │     ├─ copies mcp.config.json + handlers/ to .build/{slug}/tools/
   │     └─ rewrites handler refs to post-build paths (when needed)
   │
   ├─ Phase 5: Rewrite bindings
   │     ├─ widgets/manifest.json: bindings with kind: script lose called_via
   │     │   localhost (dev only) and gain called_via_prod (path resolved by
   │     │   the host) or are marked as "via_tool" when the build suggests
   │     │   migration from script→tool
   │     └─ SKILL.md: paths cited in ./scripts/, ./tools/, ./widgets/
   │       are checked against files actually emitted
   │
   ├─ Phase 6: Emit
   │     ├─ SKILL.md (copy + convention warning header when there are tools/widgets)
   │     ├─ .skill-manifest.json (skeleton filled with hashes — only fields
   │     │   determinable in the build; references[] with framework
   │     │   snapshots is the responsibility of PR 3)
   │     └─ {slug}.zip (lexicographically ordered zip; no timestamps)
   │
   └─ Done
```

### Determinism in the build (intermediate)

The same inputs MUST produce the same `.build/{slug}/` and the same `{slug}.zip`. Rules:

- **Lexicographic ordering** when listing files for the zip (`zip -X`, `find . | sort`); avoids filesystem-dependent order
- **No volatile timestamps**: file `mtime` in the zip is fixed at `1980-01-01` (format minimum) or at the commit hash of `skills/{slug}/` (epoch of the last versioned modification)
- **No source maps with absolute paths**: `source_maps: false` by default in `skill.config.json`; when `true`, paths are rewritten to be relative to the project root
- **Vite always with `production` mode**; dev mode (with HMR) is exclusive to `kata-skill-dev-server`
- **Locks copied, not regenerated**: `uv.lock` / `package-lock.json` from the source are preserved (not re-resolved at build), guaranteeing reproducibility

Full coverage of determinism (including snapshot of external refs with commit hash) lives in `lex-skill-export-determinism` (PR 3).

### Cache

`.build/{slug}/` is gitignored. `kata-build-skill` accepts a `--clean` flag to delete and regenerate; without the flag, an incremental build occurs when possible (Vite manages its own cache in `node_modules/.vite/`). Hashes recorded in `.skill-manifest.json` allow drift to be checked later.

### Hashes in `.skill-manifest.json`

At the end of Phase 6, the build writes `files[]` with:

```json
{
  "files": [
    { "path": "SKILL.md", "sha256": "..." },
    { "path": "widgets/dist/index.js", "sha256": "..." },
    { "path": "tools/mcp.config.json", "sha256": "..." }
  ]
}
```

`references[]` (snapshots of external framework refs) is **not** populated at this stage — it is the responsibility of `kata-package-skill` (PR 3) when consolidating `.dist/`. PR 2 delivers `references[]: []` in the manifest.

### Failures — common modes

| Failure | Cause | Expected output |
|---------|-------|-----------------|
| Invalid `SKILL.md` frontmatter | name/description outside the limits | Error citing the rules of `codex-skill-anthropic-agent-skills`; build aborts before Phase 2 |
| Invalid handler ref in `tools/mcp.config.json` | path:function does not exist | Error listing the ref and location; aborts in Phase 1 |
| Invalid widget entry in `widgets/manifest.json` | Entry path does not exist | Error with a correction suggestion; aborts in Phase 1 |
| `uv.lock` missing when `runtimes.scripts: python` | Lockfile was not generated by the author | Error instructing `uv lock` in the `scripts/` folder; aborts in Phase 3 |
| Vite build fails | TS strict error, broken import, etc. | Vite output propagated; aborts in Phase 2 |
| `kind: script` binding without `called_via` in dev | Incomplete manifest | Error instructing to declare `called_via`; aborts in Phase 5 |

### Integration with Storybook / Playwright (optional)

Skills that adopt Storybook or Playwright in `widgets/` keep these tools as **dev dependencies**; the build does not include them in `.build/{slug}/`. Stories and specs are part of the source (versioned), not of the delivery.

## Restrictions

- The build is **idempotent**: running it twice in a row with unchanged source produces a byte-identical `.build/{slug}/`
- The build **does not modify** `skills/{slug}/` (only reads)
- The build **does not touch** `.dist/` (responsibility of PR 3)
- The pipeline aborts on the first failure; it does not try to proceed partially
- Pipeline logs follow `lex-logging-decorator` when emitted by Ahrena handlers (CLI boot stays in `kata-build-skill`)
