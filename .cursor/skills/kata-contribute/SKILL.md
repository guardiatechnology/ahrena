---
name: kata-contribute
description: "Contribute via Pull Request. Create Pull Request in the origin repository via MCP"
---

# Kata: Contribute via Pull Request

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Create Pull Request in the origin repository via MCP

## Workflow

```
Progress:
- [ ] 1. Analyze changes
- [ ] 2. Prepare branch
- [ ] 3. Push to remote
- [ ] 4. Compose PR
- [ ] 5. Create PR via MCP
- [ ] 6. Final verification
```

### Step 1: Analyze Changes

1. Run `git status` to verify the repository state
2. Run `git log main..HEAD --oneline` to list commits to be included
3. Verify that all commits follow the Lexis (`lex-conventional-commits`, `lex-signed-commits`, `lex-small-commits`, `lex-commit-language`)
4. If there are uncommitted changes, invoke `kata-commit` first

### Step 2: Prepare Branch

1. Verify the current branch name:
   ```
   git branch --show-current
   ```
2. If on `main`, create a branch following the convention:
   - `feat/{name}` for features
   - `fix/{name}` for fixes
   - `docs/{name}` for documentation
   - The name is inferred from the scope of the commits
3. Use MCP `git_branch` with `action: create` and `branch_name` to create
4. Use MCP `git_checkout` to switch to the new branch

### Step 3: Push to Remote

1. Run push via MCP `git_push` with `directory` pointing to the repository
2. If the push fails because the branch does not exist on the remote, git creates it automatically

### Step 4: Compose PR

1. Extract information from the remote:
   ```
   git remote get-url origin
   ```
   Parse `repository_organization` and `repository_name` from the URL
2. Compose the title in Conventional Commits format (in English):
   - If there is a single commit: use the commit subject as the title
   - If there are multiple commits: compose a title that summarizes the change
3. Read `.github/pull_request_template.md` and fill the body:
   - **Description:** summary of the change and resolved issue
   - **Type of Change:** check relevant checkboxes
   - **Prerequisites:** associate issue, milestone, and labels
   - **How Has This Been Tested:** describe tests
   - **Checklist:** validate applicable items
   - **Related Issues:** reference with `Closes #N` or `Related to #N`
   - Fill optional sections (Breaking Changes, Security, Performance) when applicable

### Step 5: Create PR via MCP

Invoke MCP `pull_request_create` (server: `user-GitKraken`) with:

| Parameter | Value |
|-----------|-------|
| `provider` | `github` |
| `repository_name` | Extracted from remote (e.g., `ahrena`) |
| `repository_organization` | Extracted from remote (e.g., `guardiatechnology`) |
| `title` | Title in Conventional Commits format |
| `source_branch` | Current branch |
| `target_branch` | `main` |
| `body` | Filled template |
| `is_draft` | `false` (or `true` if the user requests) |

### Step 6: Final Verification

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

- Never create a PR without commits conforming to the 4 commit Lexis
- Never create a PR directly on `main` (always use a branch)
- If `.github/pull_request_template.md` does not exist, use the default format (Description + Related Issues)
- If MCP `pull_request_create` fails, present the error and suggest manual creation via `gh pr create`
