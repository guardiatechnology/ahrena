---
name: kata-skill-validate
description: "Validate Skill Project. Deterministic validation of a skill project at {paths.skills_root}/{slug}/ against lex-skill-project-structure and the frontmatter requirements from codex-skill-anthropic-agent-skills"
---

# Kata: Validate Skill Project

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Deterministic validation of a skill project at `{paths.skills_root}/{slug}/` against `lex-skill-project-structure` and the frontmatter requirements from `codex-skill-anthropic-agent-skills`

## Workflow

```
Progress:
- [ ] 1. Resolve the path and confirm existence
- [ ] 2. Invoke scripts/skills/validate.py
- [ ] 3. Collect violations (rule, severity, file, message)
- [ ] 4. Classify the result (ok / with warnings / with errors)
- [ ] 5. Report to the caller
```

### Step 1: Resolve the path and confirm existence

1. Accept the path as an absolute or repository-relative argument
2. Verify `skill_path` exists and is a directory; otherwise report `lex-skill-project-structure#location` and stop

### Step 2: Invoke `scripts/skills/validate.py`

1. Run `python3 scripts/skills/validate.py <skill_path> --format json`
2. Capture stdout and exit code
3. Do not filter the output — the validator is the source of truth; the kata only orchestrates

The validator covers, in a single pass:

| Rule | Severity | Check |
|------|:--------:|-------|
| `lex-skill-project-structure#slug-regex` | error | Directory name matches the Anthropic slug regex |
| `lex-skill-project-structure#slug-reserved` | error | Slug does not contain `anthropic` or `claude` |
| `lex-skill-project-structure#required-files` | error | `SKILL.md` and `skill.config.json` are present |
| `lex-skill-project-structure#frontmatter` | error | `SKILL.md` has a `---` YAML block |
| `lex-skill-project-structure#frontmatter-name` | error | Frontmatter has a non-empty `name` |
| `lex-skill-project-structure#name-matches-slug` | error | Frontmatter `name` equals the directory name |
| `codex-skill-anthropic-agent-skills#description` | error | `description` is present |
| `codex-skill-anthropic-agent-skills#description-length` | error | `description` is within `[1, 1024]` chars |
| `lex-semantic-version` | error | `metadata.version` is SemVer (when declared) |
| `lex-skill-project-structure#cross-references` | error | Relative Markdown links in `SKILL.md` resolve inside the project |
| `lex-skill-project-structure#optional-subdirs` | warning | Subdirectories outside the allow-list (`references/`, `scripts/`, `tools/`, `widgets/`, `assets/`) |

### Step 3: Collect violations

1. Each item in the JSON output has the shape `{rule, severity, file, message}`
2. Separate errors (severity `error`) from warnings (severity `warning`)
3. Do not infer anything beyond the reported items — the kata is "thin": the rule logic belongs to the validator

### Step 4: Classify the result

| Result | Criterion |
|--------|-----------|
| ✅ `ok` | Zero violations |
| ⚠️ `ok-with-warnings` | Warnings only |
| ❌ `failed` | One or more `error` violations |

`warrior-claudionor` only proceeds to `kata-skill-package` when the result is `ok` or `ok-with-warnings` (warnings do not block packaging but must be reported).

### Step 5: Report to the caller

1. **Format `text` (default):** print the human-readable report (header plus one line per violation)
2. **Format `json`:** return the raw violations array for programmatic consumption
3. In either format, return exit code `0` when every item is `warning`, and `1` when at least one `error` exists

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Human report | Multiline text | `stdout` |
| Agent report | JSON `[{rule, severity, file, message}, ...]` | `stdout` |
| Exit code | `0` (ok or warnings) / `1` (errors) | shell |

## Example Execution

### Input

```
kata-skill-validate skills/scheduled-payments-skill --format text
```

### Output (success)

```
✅ no violations
```

### Output (with errors)

```
❌ 2 violation(s):
  [error] lex-skill-project-structure#name-matches-slug
      file:    skills/scheduled-payments-skill/SKILL.md
      message: frontmatter name 'scheduled-payments' does not match directory slug 'scheduled-payments-skill'
  [error] lex-skill-project-structure#cross-references
      file:    skills/scheduled-payments-skill/SKILL.md
      message: reference 'references/missing.md' does not exist at ...
```

## Restrictions

- The kata **does not modify** files — it reports violations only
- The kata **does not interpret** results beyond what the validator returns; new rules are born in the Lex and propagated down to the script, never the other way around
- The kata invokes the validator as a subprocess to preserve isolation (the session's Python drift does not affect the result)
- All messages in pt-BR, es, or en per `language.default`; technical identifiers (paths, rule names) are preserved
