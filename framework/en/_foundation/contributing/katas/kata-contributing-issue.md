# Kata: Open issue in the repository (template by type)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Create issue in the origin repository via GitHub MCP

## Objective

This Kata defines the standardized procedure for opening an issue in the project's origin repository using one of the 5 issue templates (feature-request, epic, user-story-for-api, user-story-for-frontend, tech-task). The agent resolves the template in `.ahrena/contributing_templates/`, fills the sections with the user, applies required labels per `lex-issue-quality`, sets the GitHub Issue Type, creates the issue **via GitHub MCP** (fallback to `gh` CLI when unavailable), and applies the `status: todo` label as the final step per `lex-agent-planning` (Gate 1).

The kata does **NOT** apply an assignee. The assignee is an execution commitment, applied at `todo → development` by warrior-athena per `lex-agent-planning` Gate 2 — when the human or AI agent commits to executing.

## When to Use

- When the user requests to open a feature request, epic, user story (API or frontend), or simple task
- When invoked by one of the cries: cry-new-feature-request, cry-new-epic, cry-new-user-story-api, cry-new-user-story-frontend, cry-new-tech-task
- When invoked by cry-contribute with issue action (and type indicated or inferred)

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Type | Yes* | `feature-request` \| `epic` \| `user-story-for-api` \| `user-story-for-frontend` \| `tech-task`. *Inferred from the invoking cry if not provided.* |
| Title (summary) | No | Brief issue summary. If omitted, the agent composes it from context. |
| User context | No | Additional information to fill template placeholders. |

### Table: type → template → required labels → Issue Type

| Type | Template file | Required labels | GitHub Issue Type |
|------|---------------|----------------|-------------------|
| feature-request | `feature-request.md` | `feature request ➕` | Feature |
| epic | `epic.md` | `epic` | Feature |
| user-story-for-api | `user-story-for-api.md` | `api`, `user story 🎯` | Feature |
| user-story-for-frontend | `user-story-for-frontend.md` | `frontend`, `user story 🎯` | Feature |
| tech-task | `tech-task.md` | At least one of: `documentation 📃`, `ci 🏗️`, `enhancement 🔝`, `evolvability ♻️` | Task |

## Workflow

```
Progress:
- [ ] 1. Resolve issue type
- [ ] 2. Load template .md
- [ ] 3. Fill sections/placeholders with the user
- [ ] 4. Create issue via GitHub MCP (or gh)
- [ ] 5. Set GitHub Issue Type via GraphQL
- [ ] 6. Apply `status: todo` label (lex-agent-planning Gate 1)
- [ ] 7. Final verification
```

### Step 1: Resolve issue type

1. If the type was passed explicitly (e.g., by the cry), use it.
2. Otherwise, ask the user which type they want: feature request, epic, user story (API), user story (frontend), or simple task.
3. Map to the template file name, required labels, and GitHub Issue Type per the table above.

### Step 2: Load template .md

1. Canonical path: `.ahrena/contributing_templates/<file>.md` (e.g., `feature-request.md`).
2. If it does not exist in `.ahrena/`, use fallback: `framework/templates/contributing_templates/<file>.md` or `.github/ISSUE_TEMPLATE/` when applicable.
3. Read the content and identify sections and placeholders (e.g., `{user_role}`, `{specific_objective}`).

### Step 3: Fill sections/placeholders with the user

1. For each required section of the template, obtain the needed information from the user or context.
2. Replace placeholders and fill checkboxes when applicable.
3. Compose the issue title (e.g., "feat/ summary" for feature request; brief summary for epic/user story).
4. Build the body in Markdown with the filled template.

### Step 4: Create issue via GitHub MCP (or gh)

1. Determine the required labels from the table above. For `tech-task`, ask the user which label applies if not clear from context.
2. **Preferred:** Use GitHub MCP (server that exposes issue creation). E.g., server `project-0-ahrena-github`, tool `issue_write` with: `method`: `create`; `owner`; `repo`; `title`; `body`; `labels` — **mandatory**, per `lex-issue-quality`. **Do not** set `assignees` — the assignee is applied at `todo → development` per `lex-agent-planning` Gate 2.
3. **Fallback:** If MCP is unavailable, use:
   ```bash
   gh issue create \
     --title "..." \
     --body "..." \
     --label "label-name"
   ```
4. Record the issue number and node ID returned by the API — needed for Step 5.

### Step 5: Set GitHub Issue Type via GraphQL

The `gh issue create` CLI does not support `--type`. Set the Issue Type immediately after creation using the GraphQL API.

```bash
# Get the issue node ID (if not returned by Step 4)
ISSUE_ID=$(gh issue view $ISSUE_NUMBER --repo $OWNER/$REPO --json id -q .id)

# Set Issue Type (replace ISSUE_TYPE_ID with value from table below)
gh api graphql -f query="
  mutation {
    updateIssue(input: {id: \"$ISSUE_ID\", issueTypeId: \"$ISSUE_TYPE_ID\"}) {
      issue { number }
    }
  }
"
```

**Issue Type IDs** (repository-specific — verify via `codex-labels`):

| GitHub Issue Type | ID |
|-------------------|----|
| Task | `IT_kwDOED9Qy84B7pBh` |
| Bug | `IT_kwDOED9Qy84B7pBi` |
| Feature | `IT_kwDOED9Qy84B7pBj` |

### Step 6: Apply `status: todo` label (lex-agent-planning Gate 1)

Per `lex-agent-planning`, every newly created Issue MUST receive the `status: todo` label as the final step of the creation gate. Apply via `gh`:

```bash
gh issue edit $ISSUE_NUMBER --repo $OWNER/$REPO --add-label "status: todo"
```

Confirm the label was applied:

```bash
gh issue view $ISSUE_NUMBER --repo $OWNER/$REPO --json labels --jq '[.labels[].name] | join(", ")'
```

This step is the **procedural path** of the auto-apply invariant. The kata is the canonical path for Issue creation; without this step, the Issue is born without `status: todo` and falls outside the unified lifecycle of `lex-agent-planning`.

### Step 7: Final verification

- [ ] The issue was created successfully
- [ ] Title and body reflect the filled template
- [ ] Required labels were applied per `lex-issue-quality`
- [ ] The GitHub Issue Type is set (Task or Feature per template)
- [ ] The `status: todo` label was applied per `lex-agent-planning` (Gate 1)
- [ ] **No** assignee was applied (the assignee is the `todo → development` commitment, owned by Athena)
- [ ] The issue link was presented to the user

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Issue | GitHub Issue | Origin repository |
| Issue URL | Link | Presented to the user |

## Constraints

- Always use one of the 5 types and the corresponding template; do not create an issue without the template or without the required labels.
- **Never apply an assignee in this kata.** The assignee is an execution commitment, applied at `todo → development` by warrior-athena per `lex-agent-planning` Gate 2.
- Always set the GitHub Issue Type in Step 5 immediately after creation.
- Always apply `status: todo` in Step 6 as the procedural path of the auto-apply invariant per `lex-agent-planning`.
- If neither `.ahrena/contributing_templates/` nor the fallback exists, inform the user and suggest running the Ahrena install or creating the template manually.
- On MCP failure, present the error and suggest manual creation via `gh issue create` or the GitHub UI.

## References

- `lex-issue-quality` — Law governing templates, labels, and Why/What/How content
- `lex-agent-planning` — Law governing the unified Issue → Plan → PR lifecycle; `status: todo` applied in Step 6 (Gate 1)
- `codex-labels` — Full label taxonomy and GitHub Issue Type definitions
- `codex-contributing` — Guardia contribution flow
- `.ahrena/contributing_templates/` — Issue templates (feature-request.md, epic.md, user-story-for-api.md, user-story-for-frontend.md, tech-task.md)
- GitHub MCP (e.g., issue_write for issue creation)
- `warrior-athena` — owner of the `todo → development` gate (applies the assignee)
- Cries: cry-new-feature-request, cry-new-epic, cry-new-user-story-api, cry-new-user-story-frontend, cry-new-tech-task
