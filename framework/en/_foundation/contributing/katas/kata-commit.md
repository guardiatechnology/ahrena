# Kata: Create Standardized Commit

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Creating commits compliant with Guardia Lexis

## Objective

This Kata defines the standardized procedure for creating a commit that respects all Guardia commit Lexis — Conventional Commits format, atomicity, GPG signature, and language.

## When to Use

- When committing changes following Guardia standards
- When the user requests help committing changes
- When invoked by `cry-commit`
- When invoked internally by `kata-contribute`

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Changes | Yes | Staged files or indication of what to commit |
| Type | No | Conventional Commits type (feat, fix, docs, etc.). If omitted, the agent infers from the diff |
| Scope | No | Affected module or domain. If omitted, the agent infers from the diff |
| Description | No | Subject text. If omitted, the agent composes it from the diff |

## Workflow

```
Progress:
- [ ] 1. Analyze changes
- [ ] 2. Classify and compose message
- [ ] 3. Validate against Lexis
- [ ] 4. Execute commit
- [ ] 5. Final verification
```

### Step 1: Analyze Changes

1. Run `git status` to check staged files
2. If no files are staged, analyze the diff and suggest what to include with `git add`
3. Run `git diff --staged` to understand the content of the changes
4. Verify that changes are atomic (`lex-small-commits`):
   - Do all changes belong to a single purpose?
   - If not, guide the user to split into separate commits

### Step 2: Classify and Compose Message

1. Consult `codex-commit-standards` for reference
2. **Identify the type:** feat, fix, docs, build, chore, ci, style, refactor, perf, test
3. **Identify the scope:** main affected module or domain (optional)
4. **Compose the subject:**
   - Imperative present tense in English (`lex-commit-language`)
   - Maximum 72 characters
   - No trailing period
   - Format: `type(scope): description`
5. **Compose the body (if needed):**
   - English version with `[en]` tag
   - Local language version with `[pt-BR]` or `[es]` tag (if requested)
   - Detail the "why" of the change
6. **Add footers (if applicable):**
   - `Closes #N` to close issues
   - `BREAKING CHANGE:` for incompatible changes
   - `Co-authored-by:` for pair programming

### Step 3: Validate Against Lexis

Verify compliance with each Lexis before executing:

- [ ] `lex-conventional-commits`: correct `type(scope): description` format?
- [ ] `lex-small-commits`: atomic changes (single purpose)?
- [ ] `lex-commit-language`: subject in English? Language tag in the body?
- [ ] `lex-signed-commits`: GPG configured? (`git config --get commit.gpgsign` = true)

If any validation fails, fix it before proceeding.

### Step 4: Execute Commit

1. Run the commit with GPG signature:
   ```
   git commit -S -m "<message>"
   ```
2. For multiline messages (with body), use:
   ```
   git commit -S -m "$(cat <<'EOF'
   type(scope): description

   [en]
   Detailed description in English.

   [pt-BR]
   Descrição detalhada em português.

   Closes #123
   EOF
   )"
   ```

### Step 5: Final Verification

- [ ] `git log -1 --format='%s'` shows the correct subject
- [ ] `git log -1 --show-signature` shows a valid GPG signature
- [ ] The commit contains only the intended changes
- [ ] The subject is in English and follows Conventional Commits
- [ ] The commit is atomic (single logical change)

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Signed and formatted commit | Git commit | Local repository |

## Constraints

- Never commit without verifying compliance with all 4 Lexis
- Never mix unrelated changes in a single commit
- Never commit without GPG signature configured
- If GPG is not configured, alert the user and guide the setup

## References

- `lex-conventional-commits` — Mandatory format
- `lex-signed-commits` — Mandatory GPG signature
- `lex-small-commits` — Mandatory atomicity
- `lex-commit-language` — Mandatory language
- `codex-commit-standards` — Complete standards guide
- `cry-commit` — Shortcut that invokes this Kata
