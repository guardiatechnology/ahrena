# Kata: Open issue in the repository (template by type)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Create issue in the origin repository via GitHub MCP

## Objective

This Kata defines the standardized procedure for opening an issue in the project's origin repository using one of the 5 issue templates (feature-request, epic, user-story-for-api, user-story-for-frontend, simple-task). The agent resolves the template in `.ahrena/contributing_templates/`, fills the sections with the user, applies the required labels per `lex-issue-quality`, and creates the issue **via GitHub MCP** (fallback to `gh` CLI when unavailable). It follows the flow in `codex-contributing`.

## When to Use

- When the user requests to open a feature request, epic, user story (API or frontend), or simple task
- When invoked by one of the cries: cry-new-feature-request, cry-new-epic, cry-new-user-story-api, cry-new-user-story-frontend, cry-new-simple-task
- When invoked by cry-contribute with issue action (and type indicated or inferred)

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Type | Yes* | `feature-request` \| `epic` \| `user-story-for-api` \| `user-story-for-frontend` \| `simple-task`. *Inferred from the invoking cry if not provided.* |
| Title (summary) | No | Brief issue summary. If omitted, the agent composes it from context. |
| User context | No | Additional information to fill template placeholders. |

### Table: type → template → required labels

| Type | Template file | Required labels |
|------|---------------|----------------|
| feature-request | `feature-request.md` | `feature request ➕` |
| epic | `epic.md` | `epic` |
| user-story-for-api | `user-story-for-api.md` | `api`, `user story 🎯` |
| user-story-for-frontend | `user-story-for-frontend.md` | `frontend`, `user story 🎯` |
| simple-task | `simple-task.md` | At least one of: `documentation 📃`, `ci 🏗️`, `enhancement 🔝`, `evolvability ♻️` |

## Workflow

```
Progress:
- [ ] 1. Resolve issue type
- [ ] 2. Load template .md
- [ ] 3. Fill sections/placeholders with the user
- [ ] 4. Create issue via GitHub MCP (or gh)
- [ ] 5. Final verification
```

### Step 1: Resolve issue type

1. If the type was passed explicitly (e.g., by the cry), use it.
2. Otherwise, ask the user which type they want: feature request, epic, user story (API), user story (frontend), or simple task.
3. Map to the template file name and required labels per the table above.

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

1. Determine the required labels from the table above. For `simple-task`, ask the user which label applies if not clear from context.
2. **Preferred:** Use GitHub MCP (server that exposes issue creation). E.g., server `project-0-ahrena-github`, tool `issue_write` with: `method`: `create`; `owner`; `repo`; `title`; `body`; `labels` — **mandatory**, per `lex-issue-quality`.
3. **Fallback:** If MCP is unavailable, use `gh issue create --title "..." --body "..." --label "label-name"` (or body via temp file).

### Step 5: Final verification

- [ ] The issue was created successfully
- [ ] Title and body reflect the filled template
- [ ] Required labels were applied per `lex-issue-quality`
- [ ] The issue link was presented to the user

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Issue | GitHub Issue | Origin repository |
| Issue URL | Link | Presented to the user |

## Constraints

- Always use one of the 5 types and the corresponding template; do not create an issue without the template or without the required labels.
- If neither `.ahrena/contributing_templates/` nor the fallback exists, inform the user and suggest running the Ahrena install or creating the template manually.
- On MCP failure, present the error and suggest manual creation via `gh issue create` or the GitHub UI.

## References

- `lex-issue-quality` — Law governing templates, labels, and Why/What/How content
- `codex-contributing` — Guardia contribution flow
- `.ahrena/contributing_templates/` — Issue templates (feature-request.md, epic.md, user-story-for-api.md, user-story-for-frontend.md, simple-task.md)
- GitHub MCP (e.g., issue_write for issue creation)
- Cries: cry-new-feature-request, cry-new-epic, cry-new-user-story-api, cry-new-user-story-frontend, cry-new-simple-task
