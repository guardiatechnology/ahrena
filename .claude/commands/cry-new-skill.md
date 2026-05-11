New Skill Project. Initialization of a new skill project in the repository, in Anthropic Agent Skills format, with the Ahrena layout

# Cry: New Skill Project

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Initialization of a new skill project in the repository, in Anthropic Agent Skills format, with the Ahrena layout

## Usage

```
/cry-new-skill <slug> [options]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `slug` | Yes | Project name in kebab-case (1-64 chars, `a-z`/`0-9`/hyphen, no leading/trailing hyphen, no `--`) | `scheduled-payments-skill` |
| `description=` | Yes | Single sentence for the frontmatter (1-1024 chars), with **what it does** + **when to use** | `description="Schedules bank transfers when the user requests payment for a future date"` |
| `language=` | No | BCP 47; default = `language.default` in `.directives` | `language=en` |
| `license=` | No | Identifier (`Apache-2.0`, `MIT`) or reference | `license=Apache-2.0` |
| `human_title=` | No | Human-readable title for the `# H1` of `SKILL.md` | `human_title="Scheduled Payments"` |
| `with_widgets=` | No | `true` (default) or `false` | `with_widgets=false` |
| `with_tools=` | No | `true` (default) or `false` | `with_tools=false` |
| `with_scripts=` | No | `python` (default), `js`, or `false` | `with_scripts=js` |

## What the Command Does

1. Validates slug and description against the Anthropic Agent Skills spec (regex and limits)
2. Resolves `paths.skills_root` from `.ahrena/.directives` (default `skills`)
3. Confirms the destination `{paths.skills_root}/{slug}/` does not exist
4. Invokes `kata-init-skill` with the received parameters
5. Reports the created path, applied opt-outs, and next steps

## Prompt Template

```
Context:
- slug: {{slug}}
- description: {{description}}
- language: {{language}} (optional)
- license: {{license}} (optional)
- human_title: {{human_title}} (optional)
- with_widgets: {{with_widgets}} (default true)
- with_tools: {{with_tools}} (default true)
- with_scripts: {{with_scripts}} (default python)

Task:
Invoke kata-init-skill with the parameters above. The kata:
1. Validates slug and description per codex-skill-anthropic-agent-skills
2. Copies framework/templates/skill-project-sample/ to
   {paths.skills_root}/{slug}/, replacing placeholders
3. Applies opt-outs (with_widgets, with_tools, with_scripts)
4. Ensures .gitignore contains .build/
5. Reports the result

Abort if: invalid slug, destination already exists, or template missing.

Output format:
Confirmation of the created project, list of subdirectories, next steps
for authoring. On error, specific message and suggested correction.
```

## Invocation Example

```
/cry-new-skill scheduled-payments-skill \
  description="Schedules and approves bank transfers using widgets connected to Python tools. Use when the user wants to create or approve a scheduled transfer." \
  license=Apache-2.0
```

**Expected output:**

```
✅ Project created: skills/scheduled-payments-skill/
   SKILL.md, skill.config.json, .skill-manifest.json
   widgets/ (React + TS)
   scripts/ (Python)
   tools/ (MCP placeholder)
   references/REFERENCE.md

.gitignore: .build/ added.

Next steps:
- Edit SKILL.md (body)
- Add components in widgets/src/
- Add handlers in tools/handlers/
- Suggested next cry: `/cry-skill --mode implement --slug <slug>` to orchestrate authoring + validation + packaging via warrior-claudionor
```

## Restrictions

- The Cry does not modify `.ahrena/.directives` (per `lex-directives`)
- The Cry does not create the project if the destination already exists; the user decides whether to remove or pick another slug
- User messages in the `language.default` language; technical identifiers (slug, frontmatter, placeholder) preserved

## Difference from Kata

| Aspect | Cry | Kata |
|--------|-----|------|
| **Nature** | 1:1 shortcut that gathers parameters and dispatches | Full scaffold procedure (8 steps) |
| **Validation** | Parameter shape | Anthropic spec compliance + filesystem |
| **Effect** | Invokes the Kata | Writes files, updates `.gitignore` |
