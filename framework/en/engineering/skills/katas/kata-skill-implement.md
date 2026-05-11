# Kata: Implement Skill

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Orchestration of the authoring phase of a skill project at `{paths.skills_root}/{slug}/`, delegating widgets to `warrior-hephaestus` and Python tools/scripts to `warrior-apollo`, while authoring `SKILL.md` + `references/` directly

## Objective

Run the `implement` phase of the skill cycle: given a project already scaffolded by `kata-init-skill`, identify the gaps (widgets without implementation, tools without handlers, scripts without an entry, `SKILL.md` still with placeholders) and delegate each gap to the right specialist, with `warrior-claudionor` consolidating the result. This kata does **not** implement its own widget or Python code — its discipline is to orchestrate.

## When to Use

- Right after `cry-new-skill` when the scaffold still holds placeholders and empty directories
- When the user asks to "implement" an existing skill whose widgets/tools/scripts are incomplete
- As Step 2 of the `cry-skill --mode all` flow (between initial validate and final package)

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| `slug` | Yes | Project name (identical to the directory name in `{paths.skills_root}/`) |
| `gaps` | No | Pre-identified gap list; when absent, the kata performs the scan |

## Workflow

```
Progress:
- [ ] 1. Load project context (SKILL.md, skill.config.json)
- [ ] 2. Scan for gaps (widgets, tools, scripts, SKILL.md, references)
- [ ] 3. Delegation plan (who does what)
- [ ] 4. Delegate widgets → warrior-hephaestus
- [ ] 5. Delegate tools + Python scripts → warrior-apollo
- [ ] 6. Author/update SKILL.md (body) and references/ in-house
- [ ] 7. Reconcile (verify SKILL.md ↔ real files)
- [ ] 8. Report progress to the caller
```

### Step 1: Load context

1. Read `{skills_root}/{slug}/SKILL.md` and `{skills_root}/{slug}/skill.config.json`
2. Identify the declared language in `metadata.language` (used for human messages; technical identifiers remain in English)
3. Identify present subdirectories (`widgets/`, `tools/`, `scripts/`, `references/`)

### Step 2: Scan for gaps

A gap, by convention:

| Location | Gap signal |
|----------|-----------|
| `SKILL.md` | leftover `__...__` placeholders; body with only headings and no content; tool/widget list out of sync with filesystem |
| `widgets/` | `package.json` present but `src/` empty or missing `index.tsx`; no tests; components without typed props |
| `tools/` | directory present but no `mcp.config.json` or no handler for each declared tool |
| `scripts/` (Python) | no `pyproject.toml`; no module under `src/`; no test for any public function |
| `scripts/` (JS/TS) | same criterion translated to the JS stack |
| `references/` | listed in `SKILL.md` but file missing, or file present but empty |

The kata can receive the list via `gaps`; when absent, it performs the scan. When the ambiguity is unrecoverable, ask the user before delegating.

### Step 3: Delegation plan

For every gap, compose the pair (gap, responsible agent):

| Gap | Agent | Relevant Lexis |
|-----|-------|----------------|
| React/TS widget | `warrior-hephaestus` | `lex-frontend-typing`, `lex-frontend-accessibility`, `lex-frontend-security`, `lex-frontend-testing` |
| MCP tool (Python handler) | `warrior-apollo` | `lex-mcp`, `lex-python-typing`, `lex-python-testing`, `lex-python-error-handling`, `lex-python-result-type`, `lex-python-error-object` |
| MCP tool (JS/TS handler) | `warrior-hephaestus` (frontend lead owns TS) | `lex-frontend-typing`, `lex-mcp` |
| Python script | `warrior-apollo` | `lex-python-typing`, `lex-python-testing`, `lex-python-security`, `lex-python-immutability` |
| JS/TS script | `warrior-hephaestus` | `lex-frontend-typing` |
| `SKILL.md` body + `references/` | **this kata** (Claudionor authors) | `lex-tone`, `codex-skill-anthropic-agent-skills` |

Present the plan to the user in a compact format and wait for confirmation when the scope is substantive (≥3 delegations). For trivial gaps (a single widget), proceed without a gate.

### Step 4: Delegate widgets

Invoke `warrior-hephaestus` via the agent subsystem with a minimal prompt:

1. `skills_root/{slug}/widgets/` is the target directory (do not touch outside)
2. List of components to create/complete (from Step 2)
3. Explicit applicable Lexis
4. Return contract: list of produced files + status (created, modified, still pending)
5. Constraint: use `@guardia/design-system` when the skill renders on a Guardia surface (`lex-design-system-library`)

Collect the return; **do not infer** success — only the agent's explicit return counts.

### Step 5: Delegate tools/Python scripts

Invoke `warrior-apollo` analogously, with:

1. `skills_root/{slug}/tools/` and/or `skills_root/{slug}/scripts/` as target directories
2. List of handlers/scripts to create
3. Applicable Python Lexis (`lex-python-*`, `lex-mcp`)
4. Return contract identical to Step 4

### Step 6: Author SKILL.md and references in-house

This kata writes directly:

1. **`SKILL.md` body:**
   - Resolve remaining `__...__` placeholders
   - Sync the "Tools, scripts, and widgets" section with the actual filesystem after Steps 4-5
   - Make usage descriptions concrete (intent + keywords) per `codex-skill-anthropic-agent-skills`
   - Apply `lex-tone` (direct, strategic, no buzzwords)
2. **`references/`:**
   - For each reference cited in `SKILL.md`, ensure existence and coherent content
   - Snapshots of cited Lexis/Codex may be pulled from the `framework/` tree when applicable; document `source_commit` for later use by `kata-skill-package`

### Step 7: Reconcile

1. Re-read `SKILL.md` and compare with the filesystem:
   - Every declared widget has a matching file in `widgets/src/`
   - Every declared tool has a handler in `tools/handlers/` (or equivalent declared in `mcp.config.json`)
   - Every reference has a file under `references/`
2. Invoke `kata-skill-validate` as the closing check
3. If validation still fails, generate a sub-plan (remaining gaps) and return to Step 3 — maximum 3 iterations before escalating to a human

### Step 8: Report

1. List of gaps addressed in this run
2. List of files produced by each delegation
3. Final state of `kata-skill-validate`
4. Suggested next step (`cry-skill --mode package` when ready, or another round of `--mode implement` if any gap remains)

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Widget implementation | Files under `widgets/` | filesystem (produced by Hephaestus) |
| Tools/scripts implementation | Files under `tools/` and `scripts/` | filesystem (produced by Apollo) |
| Consolidated `SKILL.md` + `references/` | Markdown | filesystem (produced by this kata) |
| Progress report | Human text | `stdout` |

## Example Execution

### Input

```
kata-skill-implement slug=scheduled-payments-skill
```

### Expected output (summary)

```
Gaps identified (5):
  - SKILL.md: 3 remaining __...__ placeholders
  - widgets/: TransferForm not implemented
  - widgets/: ApprovalReview not implemented
  - tools/: handler validate_amount missing code
  - scripts/: validate_amount.py without tests

Plan:
  - Hephaestus → widgets/TransferForm, widgets/ApprovalReview
  - Apollo → tools/handlers/validate_amount.py, scripts/tests/test_validate_amount.py
  - Claudionor (this kata) → resolve placeholders + sync SKILL.md

Result:
  - 4 files produced by Hephaestus
  - 2 files produced by Apollo
  - SKILL.md consolidated, placeholders resolved
  - kata-skill-validate: ✅ no violations

Suggested next step: cry-skill --mode package --slug scheduled-payments-skill
```

## Restrictions

- The kata does **not** implement its own widgets, tools, or scripts — it delegates; crossing that boundary breaks the division of responsibility between `warrior-claudionor`, `warrior-hephaestus`, `warrior-apollo`
- The kata writes **directly** only to `SKILL.md` and `references/`; nothing else
- The kata does **not** modify `.directives`, `.gitignore`, `framework/`, or any file outside `{skills_root}/{slug}/`
- Each delegation must return the explicit list of produced files; the kata does **not** infer completion without that return
- After 3 iterations without closing every gap, the kata escalates to a human rather than loops indefinitely

## References

- `kata-skill-validate` — closing check at the end
- `kata-skill-package` — successor invoked when implementation is ready
- `warrior-claudionor` — orchestrator that invokes this kata
- `warrior-hephaestus` — widget delegation
- `warrior-apollo` — Python tools/scripts delegation
- `codex-skill-anthropic-agent-skills` — frontmatter and progressive disclosure
- `codex-skill-project-architecture` — project layout
- `codex-skill-tools-and-widgets` — `tools/` + `widgets/` convention
- `lex-skill-project-structure` — layout law
- `lex-tone` — tone applied to `SKILL.md` and `references/`
