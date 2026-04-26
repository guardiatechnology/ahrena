# Codex: Label Taxonomy

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Labels and GitHub Issue Types in Guardia repositories

## Content

### GitHub Issue Types

The Guardia organization configures three Issue Types at the repository level. Every issue MUST have one Issue Type set at creation time via the GraphQL API (the `gh issue create` CLI does not expose `--type`).

| Issue Type | ID | Templates that map to it |
|------------|----|--------------------------|
| **Task** | `IT_kwDOED9Qy84B7pBh` | `simple-task` |
| **Bug** | `IT_kwDOED9Qy84B7pBi` | `bug-report` *(future)* |
| **Feature** | `IT_kwDOED9Qy84B7pBj` | `feature-request`, `epic`, `user-story-for-api`, `user-story-for-frontend` |

**Setting Issue Type after creation:**

```bash
# Get the issue node ID
ISSUE_ID=$(gh issue view $NUMBER --repo $OWNER/$REPO --json id -q .id)

# Set issue type (example: Task)
gh api graphql -f query="
  mutation {
    updateIssue(input: {id: \"$ISSUE_ID\", issueTypeId: \"IT_kwDOED9Qy84B7pBh\"}) {
      issue { number }
    }
  }
"
```

### Label Categories

#### 1. Issue Type Labels (Required — applied at creation)

Required per `lex-issue-quality`. Applied manually at issue creation by the contributing agent.

| Label | Template | Description |
|-------|----------|-------------|
| `feature request ➕` | `feature-request` | New feature request (before approval) |
| `epic` | `epic` | Large initiative grouping multiple stories |
| `user story 🎯` | `user-story-for-api`, `user-story-for-frontend` | Scoped user-facing story |
| `documentation 📃` | `simple-task` | Documentation improvements or additions |
| `ci 🏗️` | `simple-task` | CI/CD or pipeline changes |
| `enhancement 🔝` | `simple-task` | Enhancement to an existing feature |
| `evolvability ♻️` | `simple-task` | Refactoring, clean code, maintenance |

> **Known gap:** The labels `api`, `frontend`, and `epic` are referenced in `lex-issue-quality` as required for some templates but are not yet defined in `labels.yml`. They MUST be added to the canonical label set before those templates can be fully enforced. Track via `lex-issue-quality` amendment.

#### 2. Content and Nature Labels

Applied manually to describe the nature of the change. Can apply to issues or PRs.

| Label | When to use |
|-------|-------------|
| `bug report 🐞` | Reporting a new bug (issue only) |
| `bugfix 🔧` | PR or issue that fixes a bug |
| `compliance 📜` | Change required for regulatory or standards compliance |
| `deprecate 🪦` | Marking a feature for deprecation |
| `feature ➕` | Implementation PR after a `feature request ➕` is approved |
| `security 🛡️` | PR resolves a security vulnerability |
| `vulnerability 🚨` | Detected security vulnerability (issue) |
| `breaking change 💥` | Change introduces an incompatible API change; major version bump required |
| `question ✋` | Issue requesting further information |
| `good first issue 🧠` | Issue suitable for newcomers |

#### 3. Status Labels

Applied to track issue or PR lifecycle state.

| Label | When to apply |
|-------|---------------|
| `blocked 🚧` | Issue or PR is blocked and cannot advance |
| `duplicate !!` | Issue or PR duplicates an existing one |
| `rejected ❌` | Issue or PR has been rejected (closed without merge) |
| `wontfix 🤷‍♀️` | Issue acknowledged but will not be addressed |
| `triage 🔍` | Issue requires triage before work can begin |

#### 4. PR-Only Labels

Apply exclusively to Pull Requests.

| Label | When to apply |
|-------|---------------|
| `release ↗️` | Release PR (version bump + changelog) — maintainer only |
| `breaking change 💥` | PR introduces a breaking change requiring major version bump |
| `security 🛡️` | PR resolves a security issue |

#### 5. Size Labels (Auto-applied by GitHub Actions)

Applied automatically by the PR size labeler action. **Never apply manually.** Size is calculated by counting net lines changed (additions + deletions), ignoring generated files (lock files, migrations, build artifacts).

| Label | Lines changed | Description |
|-------|:-------------:|-------------|
| `size/XS` | 0–9 | Tiny change |
| `size/S` | 10–29 | Small change |
| `size/M` | 30–99 | Medium change |
| `size/L` | 100–499 | Large change |
| `size/XL` | 500–999 | Extra-large change |
| `size/XXL` | 1,000+ | Massive change — consider splitting |

**PR size guidance:**

| Size | Guidance |
|------|----------|
| XS / S | Ideal. Fast review cycle. |
| M | Acceptable. Keep scope focused. |
| L | Acceptable for feature branches. Add context in PR description. |
| XL | Requires justification. Consider splitting. |
| XXL | Should be split into smaller PRs whenever possible. |

#### 6. Tool-Assigned Labels (Auto-applied)

Applied automatically based on who or what opened the PR.

| Label | Applied when |
|-------|-------------|
| `codex ✨` | PR opened by GitHub Copilot (legacy Codex) |
| `copilot ✨` | PR opened by GitHub Copilot |
| `cursor ✨` | PR opened by Cursor AI |
| `dependabot 🤖` | PR opened by Dependabot |

### PR Label Rules

When creating a PR, the agent MUST:

1. **Mirror all labels from the associated issue** — if the issue has `documentation 📃` and `evolvability ♻️`, the PR receives the same labels.
2. **Do NOT apply size labels manually** — the GitHub Actions labeler applies them automatically on PR creation and update.
3. **Apply PR-specific labels when applicable** — `breaking change 💥`, `security 🛡️`, `release ↗️`.
4. **Assignee** — always set `--assignee "@me"` so the PR is assigned to the contributor who created it.

**Applying labels to a PR via CLI:**

```bash
# Get labels from the associated issue
LABELS=$(gh issue view $ISSUE_NUMBER --repo $OWNER/$REPO --json labels --jq '[.labels[].name] | join(",")')

# Mirror to PR (repeat --label for each)
gh pr edit $PR_NUMBER --repo $OWNER/$REPO --add-label "$LABELS"
```
