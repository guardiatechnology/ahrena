# Kata: Push to Framework

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Incorporating project artifacts into the framework

## Objective

This Kata defines the procedure to incorporate into the canonical framework the artifacts created in the project space (`.ahrena/artifacts/`). It supports two modes: **local** (copy to `framework/` in the current repo, with i18n) and **remote** (sync with the framework repository on GitHub via GitHub MCP). It optionally removes the copies from the project after incorporation.

## When to Use

- When artifacts in `.ahrena/artifacts/` have been validated and are ready to become part of the framework
- When the user explicitly requests incorporating project artifacts into the framework
- When invoked by `cry-push-to-framework`

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Mode | Yes* | `local` or `remote`. Local: destination = `paths.framework` in the current repo. Remote: destination = framework repository on GitHub (PR/push via GitHub MCP). *Default may be `local` if `paths.framework` exists in the repo. |
| Target | No | Relative path(s) under `paths.project_artifacts` (e.g. `pt-BR/engineering/quality/lexis/lex-foo.md`) or "all". If omitted, the agent lists existing artifacts and asks or processes all |
| Remove from project | No | If "yes", removes files from `.ahrena/artifacts/` after copying to the framework (local) or after successful send (remote). Default: "no" |

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
   - In **remote** mode: `paths.framework_repo` or `repo.framework` (URL or slug of the framework repository on GitHub), if present
2. Confirm that the `paths.project_artifacts` directory exists; if it does not, report that there are no artifacts to incorporate and exit

### Step 2: Identify Artifacts to Incorporate

1. If **Target** input was provided:
   - If "all", list recursively all `.md` files under `paths.project_artifacts`
   - If one or more relative paths, validate that each exists under `paths.project_artifacts` and add to the list
2. If **Target** input was not provided:
   - List all `.md` files under `paths.project_artifacts`
   - If there are none, report and exit
   - If there are any, process all (or ask the user which to incorporate)
3. For each artifact, extract: `{lang}/{clade}/{subclade}/{pilar}/{file}` (the path relative to project_artifacts)
4. Validate that the structure follows the addressing pattern (lang/clade/subclade/pilar); ignore or warn about files that do not

### Step 3: Copy to Framework and i18n (local mode) or Send to Remote (remote mode)

**If --local:**

For each artifact in the list:

1. Source path: `{paths.project_artifacts}/{lang}/{clade}/{subclade}/{pilar}/{file}`
2. Destination path in framework: `{paths.framework}/{lang}/{clade}/{subclade}/{pilar}/{file}`
3. Create destination directories in the framework if they do not exist
4. Copy the file from the project to the framework (overwrite if it already exists)
5. Check languages: for each language in `language.i18n` that does not yet have the file in the framework:
   - If it exists in the project in another language, copy it
   - If it does not exist, run `kata-translate` from the file in the default language and save to `framework/{lang}/...`
6. Record which files were copied and which translations were created

**If --remote:**

1. Do not write to `paths.framework` on local disk.
2. Prepare the set of files to incorporate in the same layout as `framework/{lang}/{clade}/{subclade}/{pilar}/` (including missing translations via `kata-translate` in memory or a temporary area).
3. **Required:** run the sync flow with the framework repository **using the GitHub MCP only**. The agent **MUST** use the available GitHub MCP tools (e.g. server `project-0-ahrena-github` or equivalent) to: create a branch for the changes, apply the prepared files (commit), push, open a PR. All operations on the remote framework repository must be done via the GitHub MCP.
4. Record prepared files, branch created, and PR link returned by the GitHub MCP.

### Step 4: Optional Removal from Project

1. If **Remove from project** input is "yes":
   - In **local** mode: after copying to `framework/`; in **remote** mode: after successful send (e.g. after the PR is opened via the MCP).
   - For each processed artifact, remove the file(s) in `paths.project_artifacts` (all languages of the same artifact)
   - Remove empty directories under `paths.project_artifacts` if applicable
2. If "no", leave the files in the project unchanged

### Step 5: Final Validation

- [ ] All target artifacts were copied to `framework/`
- [ ] For each artifact, versions exist in all languages in `language.i18n` in the framework
- [ ] No file was corrupted (content preserved)
- [ ] If "Remove from project" was yes, files were removed from `.ahrena/artifacts/`
- [ ] Report delivered to the user with list of incorporated files and generated translations

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Artifacts in framework (local mode) | Markdown (`.md`) | `framework/{lang}/{clade}/{subclade}/{pilar}/` |
| Translations (if missing, local mode) | Markdown (`.md`) | Same path in each `framework/{lang}/` |
| Remote mode | — | Report with prepared files, branch, PR link (returned by the GitHub MCP) |
| Report | Text | Response to user |

## Constraints

- Do not alter artifact content during copy or when preparing for send (copy as-is, except when generating translations)
- Always ensure that after the Push, each artifact exists in the framework in all languages in `language.i18n` (at the destination: local or remote)
- In **remote** mode, **the GitHub MCP must be used**; do not use only git on the command line for push or opening a PR
- If a file already exists in the framework and is newer or different, consider overwriting only if the project artifact is explicitly the one to promote

## References

- `codex-pilars` — Project artifacts (.ahrena) and Push flow
- `kata-translate` — Translation procedure for generating missing languages
- `.ahrena/.directives` — paths.project_artifacts, paths.framework, language.i18n
