# Kata: Contribute Pilar to Framework

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Submitting Pilars to the Ahrena repository

## Objective

This Kata defines the standardized procedure for contributing a Pilar (or set of Pilars) to the Ahrena framework repository — including validation, commit, and submission via PR or direct commit depending on the contributor's role.

## When to Use

- When a new Pilar was created (via `kata-create-*`) and needs to be incorporated into the framework
- When the user requests to submit a contribution to the Ahrena repository
- When invoked by `cry-contribute`

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Pilar path | Yes | Path of the main artifact in the default language (e.g., `framework/pt-BR/.../lex-example.md`) |
| Message | No | Contribution description. If omitted, the agent composes it from the Pilar |

## Workflow

```
Progress:
- [ ] 1. Validate the Pilar
- [ ] 2. Verify i18n
- [ ] 3. Detect permission
- [ ] 4. Commit changes
- [ ] 5. Submit
- [ ] 6. Final verification
```

### Step 1: Validate the Pilar

1. Verify that the artifact follows the official template (`lex-template-usage`):
   - Identify the Pilar by the file prefix
   - Read the corresponding template (`templates/{pilar}-sample.md`)
   - Verify that all required sections are present
2. Verify that the artifact is in the correct taxonomy path:
   - Follows the addressing pattern `{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.md`
   - Uses kebab-case
   - Uses the correct Pilar prefix
3. Verify that it does not contradict existing Lexis
4. Verify that it does not duplicate existing artifacts

### Step 2: Verify i18n

1. Read `.ahrena/.directives` to obtain `language.i18n`
2. For each required language, verify that the translated version exists:
   - `framework/pt-BR/.../{artifact}.md`
   - `framework/es/.../{artifact}.md`
   - `framework/en/.../{artifact}.md`
3. If translations are missing, alert and suggest using `kata-translate` or `cry-translate`

### Step 3: Detect Permission

1. Check if the current repository is Ahrena:
   ```
   git remote get-url origin
   ```
2. Check if the user is a codeowner by consulting `.github/CODEOWNERS`
3. Optionally, verify via API:
   ```
   gh api repos/{owner}/{repo}/collaborators/{username}/permission
   ```
4. Determine the path:
   - **Codeowner:** direct commit + push
   - **External contributor:** branch + PR

### Step 4: Commit Changes

1. Run `git add` for the Pilar files (all i18n versions)
2. Invoke `kata-commit` with:
   - Type: `docs` (for framework artifacts)
   - Scope: Pilar name (e.g., `lex-conventional-commits`)
   - Description in English describing the contribution

### Step 5: Submit

**If codeowner:**
1. Push directly to the branch:
   ```
   git push origin HEAD
   ```

**If external contributor:**
1. Create branch:
   ```
   git checkout -b docs/{pilar-name}
   ```
2. Push to fork:
   ```
   git push -u origin docs/{pilar-name}
   ```
3. Open PR:
   ```
   gh pr create --title "docs({pilar}): add {name}" --body "..."
   ```
4. Fill the PR body with:
   - What: Pilar description
   - Why: justification
   - References: related issue or discussion

### Step 6: Final Verification

- [ ] The Pilar follows the official template (`lex-template-usage`)
- [ ] A version exists in all `language.i18n` languages
- [ ] The commit follows all 4 commit Lexis
- [ ] The commit is signed (GPG verified)
- [ ] The submission was made (push or PR created)
- [ ] CI is passing (if applicable)

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Signed commit(s) | Git commit | Local/remote repository |
| PR (if external contributor) | GitHub Pull Request | Ahrena repository |

## Constraints

- Never submit a Pilar without complete validation (template + i18n)
- Never skip the GPG signature
- If there is doubt about the correct Clade/Subclade, escalate to a human
- If the Pilar contradicts an existing Lexis, escalate to a human

## References

- `codex-contributing` — Guardia contribution flow
- `codex-commit-standards` — Commit message standards
- `kata-commit` — Procedure for creating compliant commits
- `lex-template-usage` — Mandatory template usage law
- `lex-framework-language` — Framework language structure law
- `warrior-framework-curator` — Agent that executes this Kata
- `cry-contribute` — Shortcut that invokes this Kata
