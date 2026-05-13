# Codex: Label Taxonomy

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Labels and GitHub Issue Types in Guardia repositories

## Content

### GitHub Issue Types

The Guardia organization configures three Issue Types at the repository level. Every issue MUST have one Issue Type set at creation time via the GraphQL API (the `gh issue create` CLI does not expose `--type`).

| Issue Type | ID | Templates that map to it |
|------------|----|--------------------------|
| **Task** | `IT_kwDOED9Qy84B7pBh` | `tech-task`, `plan` |
| **Bug** | `IT_kwDOED9Qy84B7pBi` | `bug` |
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
| `api` | `user-story-for-api` | API design or implementation scope |
| `user story 🎯` | `user-story-for-api`, `user-story-for-frontend` | Scoped user-facing story |
| `frontend` | `user-story-for-frontend` | Frontend (UI/UX) implementation scope |
| `documentation 📃` | `tech-task`, `plan` | Documentation improvements or additions |
| `ci 🏗️` | `tech-task`, `plan` | CI/CD or pipeline changes |
| `enhancement 🔝` | `tech-task`, `plan` | Enhancement to an existing feature |
| `evolvability ♻️` | `tech-task`, `plan` | Refactoring, clean code, maintenance |

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

### Full Label Catalog

The complete catalog seeded by `scripts/bootstrap_labels.sh` and by `make bootstrap-labels`. The script is idempotent (uses `gh label create --force`) and skips gracefully when the `gh` CLI is missing or unauthenticated. Colors are hex without the leading `#`.

#### Workflow status (7 labels)

Track Issue and PR lifecycle. See `lex-issue-status`.

| Label | Color | Description | Dependent artifact |
|-------|-------|-------------|--------------------|
| `status: todo` | `cccccc` | Plan created, Issue opened, branch linked, worktree ready | `lex-issue-status`, `lex-agent-planning` |
| `status: development` | `83d2ff` | Implementation in progress — Athena Phase 4 | `lex-issue-status`, `warrior-athena` |
| `status: to review` | `fff3a3` | PR opened, waiting for reviewer to pick up | `lex-issue-status`, `warrior-athena` |
| `status: review` | `fbca04` | Argos or human actively reviewing | `lex-issue-status`, `warrior-argos` |
| `status: to release` | `ffb178` | Review approved, waiting for release to start | `lex-issue-status`, `warrior-janus` |
| `status: release` | `e07400` | Release in execution — Janus running tag/build/deploy | `lex-issue-status`, `warrior-janus` |
| `status: done` | `0e8a16` | Release completed, PR merged, cycle closed | `lex-issue-status` |

#### Issue Types (10 labels)

Required by `lex-issue-quality` Rule 2. Map to issue templates in `.github/ISSUE_TEMPLATE/`.

| Label | Color | Description | Dependent artifact |
|-------|-------|-------------|--------------------|
| `feature request ➕` | `5319E7` | Issue about a new feature request | `feature-request.yml` |
| `feature ➕` | `7828E5` | New features added. Use only after approving a feature request | PR scope |
| `epic` | `5319E7` | Large initiative grouping multiple stories or features | `epic.yml` |
| `user story 🎯` | `6A42EB` | A new user story | `user-story-for-api.yml`, `user-story-for-frontend.yml` |
| `bug report 🐞` | `fc2803` | Report a new bug | `bug.yml` |
| `plan 📋` | `7c4dff` | Sub-issue: executable unit under a parent Issue (User Story / Bug / Tech Task) | `plan.yml`, `kata-plan-task` |
| `evolvability ♻️` | `008672` | Issue or PR launched to ensure the project's evolvability (refactoring, clean code) | `tech-task.yml` |
| `documentation 📃` | `0075ca` | Issue or PR related to improvements or additions to documentation | `tech-task.yml` |
| `ci 🏗️` | `ff7a0e` | Issue or PR related to CI/CD pipeline enhancements | `tech-task.yml` |
| `enhancement 🔝` | `D5BBED` | Issue or PR related to an enhancement to an existing feature | `tech-task.yml` |

#### Cross-cutting and lifecycle (14 labels)

Describe nature of work or state outside the development flow.

| Label | Color | Description | Dependent artifact |
|-------|-------|-------------|--------------------|
| `bugfix 🔧` | `fc4e03` | Issue or PR related to something isn't working | PR scope |
| `compliance 📜` | `ae6b09` | Issue or PR related to enhancement to be compliant with something | PR scope |
| `security 🛡️` | `D93F0B` | This PR resolves some security issue | `lex-pr-quality` |
| `vulnerability 🚨` | `B60205` | Vulnerability detected | Security workflow |
| `breaking change 💥` | `925845` | Issue or PR adding a breaking change. Major version bump required | `lex-pr-quality`, `lex-semantic-version` |
| `release ↗️` | `81A5DC` | To be set only on release PR | `lex-pr-quality`, `warrior-janus` |
| `deprecate 🪦` | `5f6a70` | Issue to deprecate some existing feature | Deprecation workflow |
| `blocked 🚧` | `e99695` | Issue or PR has some block to advance | Manual triage |
| `hold` | `fbca04` | Paused / not actively pursued | Manual triage |
| `question ✋` | `d876e3` | Further information is requested | Manual triage |
| `rejected ❌` | `b52816` | Issue or pull request rejected | Manual triage |
| `wontfix 🤷‍♀️` | `ffffff` | This issue will not be worked on | Manual triage |
| `duplicate !!` | `cfd3d7` | This issue or pull request already exists | Manual triage |
| `good first issue 🧠` | `CA3AC2` | Issue good for newcomers | Open source onboarding |

#### Platform / scope (2 labels)

Indicate the technical surface affected.

| Label | Color | Description | Dependent artifact |
|-------|-------|-------------|--------------------|
| `api` | `0075ca` | Issue or PR related to API design or implementation | `user-story-for-api.yml` |
| `frontend` | `D5BBED` | Issue or PR related to frontend (UI/UX) implementation | `user-story-for-frontend.yml` |

#### Tool-assigned (3 labels)

Auto-applied by integrations when a PR is opened by an AI tool.

| Label | Color | Description | Dependent artifact |
|-------|-------|-------------|--------------------|
| `codex ✨` | `111112` | PR opened by Codex | Integration |
| `copilot ✨` | `111112` | PR opened by Copilot | Integration |
| `cursor ✨` | `111112` | PR opened by Cursor | Integration |

#### PR size (6 labels)

Auto-applied by the GitHub Actions PR size labeler. Required by `lex-pr-quality` Rule 2.

| Label | Color | Description | Dependent artifact |
|-------|-------|-------------|--------------------|
| `size/XS` | `9b770a` | This PR changes 0-9 lines, ignoring generated files. Set automatically | `lex-pr-quality` |
| `size/S` | `e1b207` | This PR changes 10-29 lines, ignoring generated files. Set automatically | `lex-pr-quality` |
| `size/M` | `f3c511` | This PR changes 30-99 lines, ignoring generated files. Set automatically | `lex-pr-quality` |
| `size/L` | `ffdb4d` | This PR changes 100-499 lines, ignoring generated files. Set automatically | `lex-pr-quality` |
| `size/XL` | `cb9e0a` | This PR changes 500-999 lines, ignoring generated files. Set automatically | `lex-pr-quality` |
| `size/XXL` | `7a6600` | This PR changes over 1,000 lines, ignoring generated files. Set automatically | `lex-pr-quality` |

#### Bootstrap procedure

Run once per consumer repository. The catalog is also seeded automatically by `make install` and `make update` when the target has a GitHub remote.

```bash
# Manual run against the current repo
make bootstrap-labels

# Manual run against an explicit repo
bash scripts/bootstrap_labels.sh owner/repo
```

The script requires the `gh` CLI authenticated with write access to the target repository. It is idempotent — re-running updates color and description without errors.
