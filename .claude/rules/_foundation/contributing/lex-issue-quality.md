# Lexis: Issue Quality Requirements

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** All issues in Guardia repositories

## Law

> **Every issue in a Guardia repository MUST use one of the approved templates (feature-request, epic, user-story-for-api, user-story-for-frontend, simple-task), MUST have at least one label from the approved list that corresponds to its type, and MUST explicitly answer: why (motivation and impact), what (objective and scope), and how (implementation approach or definition of done). No branch MAY be created and no PR MAY be opened for an issue that does not comply with these requirements.**

## Coverage

- **Applies to:** all issues in all Guardia repositories.
- **Bound agents:** developers, AI agents (warrior-athena, warrior-apollo, warrior-hephaestus) that create or validate issues.
- **Exceptions:** auto-generated issues by Dependabot or security scanning tools, which follow their own format. Every other exception requires explicit justification recorded in the issue itself.

## Rules

### 1. Approved templates

Every issue MUST use one of the following templates (located in `.ahrena/contributing_templates/`):

| Template | When to use |
|----------|-------------|
| `feature-request` | New functionality, new behavior, new user-facing capability |
| `epic` | Large initiative grouping multiple stories or features |
| `user-story-for-api` | API-focused backend feature with acceptance criteria and API spec |
| `user-story-for-frontend` | UI/UX feature for the platform or app |
| `simple-task` | Well-defined small task: chore, refactoring, maintenance, documentation fix, CI change |

Issues without a template are incomplete and MUST be updated before any branch or PR can reference them.

### 2. Mandatory labels

Every issue MUST have at least one label applied. The label MUST correspond to the issue type:

| Template | Required labels |
|----------|----------------|
| `feature-request` | `feature request ➕` |
| `epic` | `epic` |
| `user-story-for-api` | `api`, `user story 🎯` |
| `user-story-for-frontend` | `frontend`, `user story 🎯` |
| `simple-task` | At least one of: `documentation 📃`, `ci 🏗️`, `enhancement 🔝`, `evolvability ♻️` |

### 3. Mandatory content: Why / What / How

Every issue MUST answer three questions, explicitly or through the template sections:

| Question | What it covers | Template mapping |
|----------|----------------|-----------------|
| **Why** | Motivation, impact, problem being solved | "Why is this important?" / "Why" section |
| **What** | Objective, scope, what changes | "Objective" / "What" section |
| **How** | Implementation approach, expected outcome, definition of done | "How should it work?" / "How" section |

For `simple-task`: the three questions are the direct sections of the template.

For other templates: the sections map to these questions — the **Objective** (user story) answers What, **Why is this important** answers Why, and **How can it be implemented** / acceptance criteria answers How.

### 4. Branch and PR blocked until issue complies

Per `lex-issue-first` and `lex-git-branches`, no branch MAY be created and no PR MAY be opened if the associated issue:

- Does not use one of the approved templates
- Does not have at least one required label
- Does not answer Why, What, and How

### 5. Agents must comply

AI agents that create issues (via MCP or CLI) MUST:

1. Use the appropriate template via `kata-contributing-issue`
2. Apply the required labels during creation
3. Fill all mandatory sections (Why / What / How) before submitting

## Examples

### Correct

```
Issue: "Add kata-setup-gpg-signing to the contributing framework"
Template: simple-task
Labels: documentation 📃
Why: Contributors need to configure GPG signing to satisfy lex-signed-commits; no step-by-step guide exists yet.
What: Create kata-setup-gpg-signing covering GPG installation, key generation, git configuration, and GitHub export.
How: Follow the GPG key generation flow; cover macOS, Linux, and Windows; add verification step.
```

### Incorrect

```
Issue: "fix the auth bug"
Template: none
Labels: none
Content: single line, no Why / What / How

→ ❌ Branch creation blocked per lex-git-branches
→ ❌ PR rejected per lex-issue-first
```

## Automated Validation

- **Tool:** `kata-contributing-issue` enforces template selection and label application on creation; PR review checklist verifies that the associated issue is complete.
- **When:** on issue creation (via kata); on PR creation (via lex-issue-first check).
- **Metric:** 0 open PRs referencing an issue without template and labels; 100% of issues created via kata comply on first submission.
