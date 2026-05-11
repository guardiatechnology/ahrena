# Kata: Initialize a Skill Project (Scaffold)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Scaffolding a new skill project under `{paths.skills_root}/{slug}/` from the `framework/templates/skill-project-sample/` template

## Objective

Create a new skill project in the repository from the official template, validating the slug against the Anthropic Agent Skills spec, replacing placeholders, ensuring `.gitignore` contains `.build/`, and leaving the project ready for authoring per `lex-skill-project-structure` and `codex-skill-project-architecture`.

## When to Use

- When the user invokes `/cry-new-skill <slug>`
- When an agent (human or AI) needs to start a new skill project before producing widgets, scripts, or tools

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| `slug` | Yes | Project name in kebab-case; identical to the `name` to be written in `SKILL.md` (1-64 chars, `a-z`/`0-9`/hyphen, no leading/trailing hyphen, no consecutive `--`) |
| `description` | Yes | Single sentence for the frontmatter (1-1024 chars); includes **what it does** and **when to use** |
| `language` | No | BCP 47; default = `language.default` in `.ahrena/.directives` |
| `license` | No | Identifier (e.g., `Apache-2.0`); default empty (field omitted) |
| `human_title` | No | Human-readable title for the `# H1` in the `SKILL.md` body; default = readable capitalization of the slug |
| `with_widgets` | No | `true` (default) or `false` (controls whether `widgets/` stays in the scaffold) |
| `with_tools` | No | `true` (default) or `false` |
| `with_scripts` | No | `true` (default), `false`, `python` (default when true), or `js` |

## Workflow

```
Progress:
- [ ] 1. Validate slug and description
- [ ] 2. Resolve paths and destination
- [ ] 3. Check preconditions (template exists, destination free)
- [ ] 4. Copy template and replace placeholders
- [ ] 5. Apply opt-outs (with_widgets/tools/scripts)
- [ ] 6. Ensure .gitignore contains .build/
- [ ] 7. Validate the result
- [ ] 8. Report
```

### Step 1: Validate slug and description

1. Apply the regex `^[a-z0-9](?:(?:[a-z0-9]|-(?!-)){0,62}[a-z0-9])?$` to the slug (1-64 chars, no leading/trailing hyphen, no `--`)
2. Reject slugs with reserved words (`anthropic`, `claude`) per Anthropic documentation
3. Confirm `description` is 1-1024 chars; reject empty
4. On violation, abort with a message naming the rule (cite `codex-skill-anthropic-agent-skills`)

### Step 2: Resolve paths and destination

1. Read `.ahrena/.directives` (per `lex-directives`); use `paths.skills_root` (default `skills`), `paths.skills_build` (default `.build`), `paths.skills_dist` (default `.dist`)
2. Resolve missing `language` to `language.default`
3. Compute destination: `{paths.skills_root}/{slug}/`

### Step 3: Check preconditions

1. Confirm `framework/templates/skill-project-sample/` exists (source)
2. Confirm the destination **does not exist** — if it does, abort with instructions to remove it or pick another slug; never overwrite
3. Ensure `paths.skills_root` exists (create directory if missing)

### Step 4: Copy template and replace placeholders

1. Copy the tree from `framework/templates/skill-project-sample/` to `{paths.skills_root}/{slug}/`, **omitting** the template root `README.md` (internal framework documentation)
2. Replace placeholders in the copied files:

| Placeholder | Value |
|-------------|-------|
| `__SLUG__` | `slug` |
| `__BCP47__` | resolved `language` |
| `__HUMAN_TITLE__` | `human_title` (default: readable capitalization of the slug) |
| `__ONE_SENTENCE_DESCRIPTION_INCLUDING_WHEN_TO_USE__` | `description` |
| `__LICENSE_OR_REFERENCE__` | `license` when provided; when absent, **remove the `license:` line** from the frontmatter |

3. Replacement is literal (string-match), across every text file (`.md`, `.json`, `.tsx`, `.ts`, `.py`, `package.json`, etc.)

### Step 5: Apply opt-outs

1. `with_widgets=false`: remove the `widgets/` directory; remove the widgets mention in `SKILL.md` ("Tools, scripts, and widgets" section)
2. `with_tools=false`: remove the `tools/` directory
3. `with_scripts=false`: remove the `scripts/` directory
4. `with_scripts=js`: switch `runtimes.scripts` in `skill.config.json` to `node`; adjust `scripts/README.md` removing the Python section; keep `scripts/` empty with `.gitkeep`
5. `with_scripts=python`: keep as in the template (default)

### Step 6: Ensure `.gitignore`

1. Inspect the repository-root `.gitignore`
2. If the `{paths.skills_build}/` (or `.build/` when default) entry is missing, **add it** with a comment header:

```
# External skill projects — build intermediates (per lex-skill-project-structure)
.build/
```

3. If already present, do not duplicate

### Step 7: Validate the result

1. Confirm `{paths.skills_root}/{slug}/SKILL.md` exists
2. Confirm `{paths.skills_root}/{slug}/skill.config.json` exists
3. Confirm the frontmatter of `SKILL.md` has `name: {slug}` (validate equality)
4. Confirm **no** `__...__` placeholder remains in the created project files

### Step 8: Report

1. Show the user:
   - Path of the created project
   - Slug, description, language, license applied
   - Subdirectories included (widgets/scripts/tools, per opt-outs)
   - Next steps: edit `SKILL.md` body, add components in `widgets/src/`, etc.
   - Orchestration suggestion: `cry-skill --mode implement --slug <slug>` to hand the authoring phase to `warrior-claudionor`
2. Point to `codex-skill-project-architecture` for authoring.

## Outputs

| Output | Format |
|--------|--------|
| Success | Directory `{paths.skills_root}/{slug}/` populated; `.gitignore` updated when needed |
| Failure (invalid slug) | Message citing `codex-skill-anthropic-agent-skills`; no file created |
| Failure (destination exists) | Message instructing to remove or pick another slug; no file modified |
| Failure (template missing) | Message indicating that `framework/templates/skill-project-sample/` is missing — possible installation corruption |

## Execution Example

### Input

```
/cry-new-skill scheduled-payments-skill \
  description="Schedules and approves bank transfers using widgets connected to Python tools. Use when the user wants to create or approve a scheduled transfer." \
  license=Apache-2.0
```

### Expected Output

```
✅ Project created: skills/scheduled-payments-skill/
   ├── SKILL.md                 (name: scheduled-payments-skill, language: en, license: Apache-2.0)
   ├── skill.config.json
   ├── .skill-manifest.json
   ├── references/REFERENCE.md
   ├── scripts/                 (Python — pyproject.toml to be added when starting)
   ├── tools/                   (mcp.config.json placeholder)
   └── widgets/                 (React — package.json + tsconfig.json ready)

.gitignore updated: .build/ added.

Next steps:
- Edit skills/scheduled-payments-skill/SKILL.md (body)
- Add components in widgets/src/
- Add handlers in tools/handlers/
- To orchestrate authoring + validation + packaging, invoke:
    /cry-skill --mode implement --slug scheduled-payments-skill
```

## Restrictions

- Do not overwrite existing project
- Do not modify `.directives`
- Do not touch `.build/` or `.dist/` (those belong to build and packaging in future PRs)
- All user messages in pt-BR, es, or en per `language.default`; technical names (slug, frontmatter, placeholder) preserved
- An invalid slug aborts the kata with no side effect

## References

- `codex-skill-anthropic-agent-skills` — naming, frontmatter, and layout rules
- `codex-skill-project-architecture` — source project architecture and spec ↔ Ahrena mapping
- `lex-skill-project-structure` — law for the layout and source/build/dist separation
- `lex-template-usage` — mandatory template usage
- `lex-directives` — reading of `paths.skills_*`
- `lex-terminal-type` — shell command syntax when the kata needs to touch the filesystem in PowerShell vs. bash
- `cry-new-skill` — user entry point
- `framework/templates/skill-project-sample/` — scaffold source
- `warrior-claudionor`, `cry-skill --mode implement` — recommended successor after the scaffold
