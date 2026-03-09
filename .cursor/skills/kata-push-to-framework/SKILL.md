---
name: kata-push-to-framework
description: "Push Project Artifacts to Framework. Incorporate artifacts from .ahrena/artifacts/ into the canonical framework with full i18n"
---

# Kata: Push to Framework

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Incorporating project artifacts into the framework

## When to Use

- When the user wants to incorporate artifacts from `.ahrena/artifacts/` into the canonical `framework/`
- When invoked by `cry-push-to-framework` or when the user asks to "push to framework" or "incorporate project artifacts"

## Workflow

```
Progress:
- [ ] 1. Read directives
- [ ] 2. Identify artifacts to incorporate
- [ ] 3. Copy to framework and i18n
- [ ] 4. Optional removal from project
- [ ] 5. Final validation
```

### Step 1: Read Directives

1. Read `.ahrena/.directives` to obtain:
   - `paths.project_artifacts` — root of project artifacts (e.g. `.ahrena/artifacts/`)
   - `paths.framework` — framework root (e.g. `framework/`)
   - `language.default` — default language
   - `language.i18n` — required languages
2. Confirm that `paths.project_artifacts` exists; if not, report that there are no artifacts to incorporate and exit

### Step 2: Identify Artifacts to Incorporate

1. If **Target** was provided: if "all", list all `.md` files under `paths.project_artifacts`; if specific path(s), validate they exist and add to the list
2. If **Target** was not provided: list all `.md` files under `paths.project_artifacts`; if none, report and exit; otherwise process all (or ask the user)
3. For each artifact, extract the relative path: `{lang}/{clade}/{subclade}/{pilar}/{file}`
4. Validate structure (lang/clade/subclade/pilar); ignore or warn about invalid paths

### Step 3: Copy to Framework and i18n

For each artifact:

1. Source: `{paths.project_artifacts}/{lang}/{clade}/{subclade}/{pilar}/{file}`
2. Destination: `{paths.framework}/{lang}/{clade}/{subclade}/{pilar}/{file}`
3. Create destination directories if needed; copy file (overwrite if exists)
4. For each language in `language.i18n` missing in the framework: copy from project if present, or run `kata-translate` from the default-language file and save to `framework/{lang}/...`
5. Record copied files and created translations

### Step 4: Optional Removal from Project

- If **Remove from project** is "yes": delete the artifact file(s) from `paths.project_artifacts` (all languages for that artifact); remove empty directories
- If "no": leave project files unchanged

### Step 5: Final Validation

- [ ] All target artifacts were copied to `framework/`
- [ ] Each artifact has versions in all `language.i18n` languages in the framework
- [ ] Content preserved (no corruption)
- [ ] If remove was yes, files removed from `.ahrena/artifacts/`
- [ ] Report delivered to the user: list of incorporated files and generated translations

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Target | No | Relative path(s) under `paths.project_artifacts` or "all". If omitted, process all found artifacts |
| Remove from project | No | "yes" to delete from `.ahrena/artifacts/` after copy. Default: "no" |

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Artifacts in framework | Markdown (`.md`) | `framework/{lang}/{clade}/{subclade}/{pilar}/` |
| Translations (if missing) | Markdown (`.md`) | Same path in each `framework/{lang}/` |
| Report | Text | Response to user |

## Constraints

- Do not alter artifact content during copy (copy as-is; only generate new translations when missing)
- After Push, every artifact MUST exist in the framework in all `language.i18n` languages
- Overwrite existing framework file only when the project artifact is explicitly the one to promote

## References

- `codex-pilars` — Project artifacts (.ahrena) and Push flow
- `kata-translate` — For generating missing language versions
- Framework kata: `framework/{lang}/_foundation/authoring/katas/kata-push-to-framework.md`
