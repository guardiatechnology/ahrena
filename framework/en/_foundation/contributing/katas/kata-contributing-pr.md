# Kata: Contribute via Pull Request

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Create Pull Request in the origin repository via MCP

## Objective

This Kata defines the standardized procedure for opening a Pull Request in the project's origin repository using GitKraken MCP tools and the template at `.ahrena/contributing_templates/pull_request_template.md` (or `.github/pull_request_template.md`). It ensures that every contribution follows the unified flow defined in `codex-contributing`. It aligns with the existing `kata-contribute`.

## When to Use

- When changes are ready for submission to the repository
- When the user requests to create a PR
- When invoked by cry-new-pr or by cry-contribute with pr action

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Committed changes | Yes | Commits ready on the local branch (already validated by `kata-commit`) |
| Title | No | PR title in Conventional Commits format. If omitted, the agent infers from the commits |
| Related issue | No | Issue number that the PR resolves. If omitted, the agent asks |

## Workflow

```
Progress:
- [ ] 1. Analyze changes
- [ ] 2. Prepare branch
- [ ] 3. Push to remote
- [ ] 4. Compose PR (template in .ahrena/contributing_templates/)
- [ ] 5. Create PR via MCP (GitKraken: pull_request_create)
- [ ] 6. Final verification
```

### Step 1: Analyze changes

1. Run `git status` to verify the repository state
2. Run `git log main..HEAD --oneline` to list commits to be included
3. Verify that all commits follow the Lexis (`lex-conventional-commits`, `lex-signed-commits`, `lex-small-commits`, `lex-commit-language`)
4. If there are uncommitted changes, invoke `kata-commit` first

### Step 2: Prepare branch

1. Verify the current branch name: `git branch --show-current`
2. If on `main`, create a branch following the convention: `feat/{name}`, `fix/{name}`, `docs/{name}` (name inferred from commit scope)
3. Use MCP `git_branch` with `action: create` and `branch_name`; MCP `git_checkout` to switch to the new branch

### Step 3: Push to remote

1. Run push via MCP `git_push` with `directory` pointing to the repository
2. If push fails because the branch does not exist on the remote, git will create it

### Step 4: Compose PR (template)

1. Extract `repository_organization` and `repository_name` from the remote (e.g., `git remote get-url origin`)
2. Compose the title in Conventional Commits (English): single commit → commit subject; multiple commits → title that summarizes the change
3. **Template:** Read `.ahrena/contributing_templates/pull_request_template.md`; if it does not exist, use `.github/pull_request_template.md`
4. Fill the body: Description, Type of Change, Prerequisites, How Has This Been Tested, Checklist, Related Issues (`Closes #N` or `Related to #N`); Breaking Changes, Security, Performance when applicable

### Step 5: Create PR via MCP

Invoke MCP `pull_request_create` (server: `user-GitKraken`) with: `provider`: `github`; `repository_name`; `repository_organization`; `title`; `source_branch`; `target_branch`: `main`; `body`; `is_draft` as needed.

### Step 6: Final verification

- [ ] The PR was created successfully
- [ ] The title follows Conventional Commits in English
- [ ] The body is filled with the repository template
- [ ] The issue is referenced in the PR
- [ ] All commits are signed (GPG verified)
- [ ] The source branch is correct

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Pull Request | GitHub PR | Origin repository |
| PR URL | Link | Presented to the user |

## Constraints

- Do not create a PR unless commits comply with the 4 commit Lexis
- Do not create a PR directly on `main` (always use a branch)
- If there is no template in `.ahrena/` or `.github/`, use the default format (Description + Related Issues)
- If MCP `pull_request_create` fails, present the error and suggest manual creation via `gh pr create`

## References

- `codex-contributing` — Guardia contribution flow
- `codex-commit-standards` — Commit message standards
- `kata-commit` — Procedure for making compliant commits
- `kata-contribute` — Canonical PR procedure (this kata aligns with or reuses it)
- cry-new-pr, cry-contribute — Shortcuts that invoke this Kata
- `.ahrena/contributing_templates/pull_request_template.md` — PR template (canonical source after install)
