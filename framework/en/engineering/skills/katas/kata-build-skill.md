# Kata: Skill build (source → `.build/{slug}/` + zip)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Operational implementation of the deterministic build pipeline described in `codex-skill-build-pipeline`. Reads `{paths.skills_root}/{slug}/`, validates manifests, builds widgets, freezes scripts, validates tools, and emits `{paths.skills_build}/{slug}/` + a testable zip

## Objective

Produce a byte-deterministic `.build/{slug}/` (same source → same output) and a `.build/{slug}.zip` that can be loaded into another Claude Code agent (or equivalent) for end-to-end manual testing before the final packaging in `.dist/` (PR 3).

## When to Use

- When the user invokes `/cry-skill-build <slug>`
- When continuous integration needs to generate a testable zip
- Before invoking `kata-package-skill` (PR 3) to produce the final delivery

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| `slug` | Yes | Project at `{paths.skills_root}/{slug}/` |
| `clean` | No | `true` deletes `.build/{slug}/` before starting; default `false` (incremental build leveraging the Vite cache) |
| `skip_zip` | No | `true` skips Phase 6 of the zip (useful when the consumer is only `kata-package-skill`); default `false` |

## Workflow

```
Progress:
- [ ] 1. Resolve paths and config
- [ ] 2. Phase 1 — Validate
- [ ] 3. Phase 2 — Build widgets
- [ ] 4. Phase 3 — Freeze scripts
- [ ] 5. Phase 4 — Resolve tools
- [ ] 6. Phase 5 — Rewrite bindings
- [ ] 7. Phase 6 — Emit (.build/ + zip)
- [ ] 8. Validate idempotency
- [ ] 9. Report
```

### Step 1: Resolve paths and config

1. Read `.ahrena/.directives` for `paths.skills_root`, `paths.skills_build`
2. Confirm `{paths.skills_root}/{slug}/` exists
3. Read `skill.config.json`; apply overrides
4. If `clean=true`, remove `{paths.skills_build}/{slug}/` before proceeding
5. Ensure `{paths.skills_build}/{slug}/` exists (create it)

### Step 2: Phase 1 — Validate

Per `codex-skill-build-pipeline` (Phase 1):

1. **`SKILL.md`**: parse frontmatter; validate `name` (spec regex), `description` (1-1024), `compatibility` (≤500 when present), `metadata.version` (semver), `metadata.language` (BCP 47)
2. **`skill.config.json`**: `schema_version: 1`, `runtimes.scripts` in `python|node`, ports present
3. **`tools/mcp.config.json`** (when `tools/` exists): `schema_version: 1`, each `tools[].name` in snake_case, `tools[].input_schema` is a valid JSON Schema, `tools[].handler` points to an existing file+function
4. **`widgets/manifest.json`** (when `widgets/` exists): `schema_version: 1`, each `components[].entry` points to an existing file, each `bindings[]` references an existing tool or script
5. **`description` in SKILL.md**: warn (do not abort) if < 30 chars (quality heuristic per spec — short descriptions reduce activation)

On any failure, abort with a specific error citing the rule (`codex-skill-anthropic-agent-skills` for frontmatter, `codex-skill-tools-and-widgets` for manifests).

### Step 3: Phase 2 — Build widgets

When `widgets/` exists:

1. `cd {paths.skills_root}/{slug}/widgets`
2. Ensure `node_modules/` (run `npm install` or `pnpm install` when absent)
3. Run `vite build --mode production` (default config; override via `vite.config.ts` if the author declared it)
4. Expected output: `widgets/dist/`
5. Copy `widgets/dist/` to `{paths.skills_build}/{slug}/widgets/`
6. Rewrite `widgets/manifest.json` in `.build/`:
   - `components[].entry` points to the corresponding compiled file in `dist/`
   - `bindings[]` preserved; rewrite occurs in Phase 5
7. Copy the rewritten `manifest.json` to `.build/{slug}/widgets/manifest.json`

### Step 4: Phase 3 — Freeze scripts

When `scripts/` exists:

1. For Python (`runtimes.scripts: python`):
   - Confirm `scripts/uv.lock` (generate with `uv lock` when absent, aborting if the author did not allow mutation)
   - Copy `scripts/src/`, `scripts/pyproject.toml`, `scripts/uv.lock` to `.build/{slug}/scripts/`
2. For Node (`runtimes.scripts: node`):
   - Confirm the lockfile (`package-lock.json` or `pnpm-lock.yaml`)
   - Copy `scripts/src/`, `scripts/package.json`, the lockfile to `.build/{slug}/scripts/`
3. Do not install dependencies in `.build/` (the consumer installs at load time)

### Step 5: Phase 4 — Resolve tools

When `tools/` exists:

1. Validate each `tools[].handler` (path:function exists and is callable)
2. Copy `tools/mcp.config.json` to `.build/{slug}/tools/`
3. Copy `tools/handlers/` to `.build/{slug}/tools/handlers/` (preserve structure)
4. When the handler is Python and `runtimes.scripts: python`, reuse the `uv.lock` from `scripts/` (handlers MAY import from `scripts/src/`)

### Step 6: Phase 5 — Rewrite bindings

In `widgets/manifest.json` (already in `.build/`):

1. For each `kind: script` binding:
   - Remove `called_via` (dev localhost URL)
   - Add `called_via_prod`: relative path to the consumer (default `./scripts/src/{filename}.{ext}`)
   - When `skill.config.json.build.prefer_tool_over_script: true`, mark as `via_tool: true` so the host invokes the equivalent MCP tool instead of executing the script directly

In `SKILL.md` (copy at `.build/{slug}/SKILL.md`):

1. Add a warning header (after the frontmatter, before the body) when `tools/` or `widgets/` is present:

   ```markdown
   > **Note:** This skill bundles `tools/` (MCP) and/or `widgets/` (React) as
   > Ahrena convention. Agents that only know the Anthropic Agent Skills spec
   > ignore those directories. See codex-skill-tools-and-widgets in the source
   > framework for binding semantics.
   ```

2. Validate that paths cited in the body (`scripts/...`, `tools/...`, `widgets/...`) exist in `.build/`

### Step 7: Phase 6 — Emit (.build/ + zip)

1. Write `.build/{slug}/.skill-manifest.json`:
   ```json
   {
     "schema_version": 1,
     "skill": { "name": "{slug}", "version": "...", "language": "..." },
     "framework": { "ahrena_commit": "{HEAD-of-source}" },
     "references": [],
     "files": [
       { "path": "SKILL.md", "sha256": "..." },
       { "path": "widgets/dist/index.js", "sha256": "..." },
       ...
     ]
   }
   ```
   `references[]` remains empty — populated by `kata-package-skill` (PR 3).
   `files[]` listed in **lexicographic** order of paths.
2. When `skip_zip=false`:
   - `mtime` of each file in the zip fixed at `1980-01-01T00:00:00Z` (format minimum)
   - Command: `cd .build/{slug} && find . -type f -exec touch -t 198001010000 {} + && find . -type f | LC_ALL=C sort | zip -X --no-extra -@ ../{slug}.zip` (or cross-platform equivalent). The `touch` fixes the `mtime` of each file at the ZIP format minimum before packaging
   - Output: `{paths.skills_build}/{slug}.zip`

### Step 8: Validate idempotency

1. Compute the sha256 of `.build/{slug}/{slug}.zip` (or of the entire tree when `skip_zip=true`)
2. Compare with the hash recorded in `.skill-manifest.json` (if any from a previous run)
3. On unexpected drift, alert — possible causes: timestamps not fixed, filesystem ordering, source maps with absolute paths

### Step 9: Report

```
✅ Build of {slug} completed.
   Output: {paths.skills_build}/{slug}/
   Zip:    {paths.skills_build}/{slug}.zip   (X.X MB)
   sha256: <hash>

Contents:
   - SKILL.md (warning header added)
   - widgets/dist/ (Vite production)
   - scripts/ (Python uv frozen)
   - tools/ (3 handlers validated)
   - .skill-manifest.json (8 files; references empty until PR 3)

Next steps:
   - Load the zip into another Claude Code agent for manual testing
   - kata-package-skill (PR 3) delivers an auditable .dist/{slug}.skill
```

## Outputs

| Output | Format |
|--------|--------|
| Success | `.build/{slug}/` populated + zip + manifest with hashes |
| Failure (Phase 1) | Specific validation error; nothing written to `.build/` |
| Failure (Phase 2) | Vite output propagated; build aborts |
| Failure (Phase 3) | Lockfile missing — instruction to generate |
| Failure (Phase 4) | Invalid handler ref — points to the missing handler |
| Failure (Phase 5) | Inconsistent bindings (point to a file that disappeared) |
| Idempotency failure | Alert with probable cause; the build survives but signals to investigate |

## Execution Example

```
/cry-skill-build hello-skill
```

```
✅ Build of hello-skill completed.
   Output: .build/hello-skill/
   Zip:    .build/hello-skill.zip   (124 KB)
   sha256: 7a8c…
```

## Restrictions

- The build is **read-only** over `{paths.skills_root}/{slug}/`
- Does not touch `.dist/`
- Aborts on the first failure; never emits partial output
- Determinism is a non-negotiable criterion (`codex-skill-build-pipeline` § "Determinism in the build"); full coverage in PR 3 (`lex-skill-export-determinism`)
- Application logs follow `lex-logging-decorator`; the kata's CLI output is an exception (boundary)
- `lex-terminal-type`: shell commands in the correct syntax

## References

- `codex-skill-build-pipeline` — pipeline contract (defaults, phases, determinism)
- `codex-skill-tools-and-widgets` — schemas validated in Phase 1
- `codex-skill-anthropic-agent-skills` — frontmatter validated in Phase 1
- `codex-skill-project-architecture` — dev → build → dist flow
- `codex-python-tooling` — uv as the Python runtime
- `lex-skill-project-structure` — source/build/dist separation
- `lex-skill-export-determinism` (PR 3) — determinism of the final delivery
- `cry-skill-build` — user shortcut
- `kata-skill-dev-server` — natural prior step; validates manually before the build
- `kata-package-skill` (PR 3) — consumer of `.build/` to produce `.dist/`
