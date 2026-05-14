# Lexis: Issue Quality Requirements

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** All issues in Guardia repositories

## Law

> **Every issue in a Guardia repository MUST use one of the approved templates (feature-request, epic, user-story-for-api, user-story-for-frontend, tech-task, bug, plan), MUST have at least one label from the approved list that corresponds to its type, MUST have a defined GitHub Issue Type (Feature, Task, Bug, Epic) compatible with the template used, MUST explicitly answer: why (motivation and impact), what (objective and scope), and how (implementation approach or definition of done), and — for every non-Epic issue — MUST carry the `status: todo` label immediately after creation. The assignee is captured at the `todo → development` transition by `warrior-athena` (per `lex-agent-planning`), NOT at creation time: issues in `status: todo` MAY remain without an assignee. No branch MAY be created and no PR MAY be opened for an issue that does not comply with these requirements.**

## Coverage

- **Applies to:** all issues in all Guardia repositories.
- **Bound agents:** developers, AI agents (warrior-athena, warrior-apollo, warrior-hephaestus, warrior-eunomia) that create or validate issues.
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
| `bug` | Defect report on existing behavior; reproduction + impact + expected fix |
| `tech-task` | Well-defined small task: chore, refactoring, maintenance, documentation fix, CI change |
| `plan` | Executable Plan sub-issue under a parent Issue (User Story / Bug / Tech Task), per `lex-agent-planning` |

Issues without a template are incomplete and MUST be updated before any branch or PR can reference them.

### 2. Mandatory labels

Every issue MUST have at least one label applied. The label MUST correspond to the issue type:

| Template | Required labels |
|----------|----------------|
| `feature-request` | `feature request ➕` |
| `epic` | `epic` |
| `user-story-for-api` | `api`, `user story 🎯` |
| `user-story-for-frontend` | `frontend`, `user story 🎯` |
| `bug` | `bug 🐛` |
| `tech-task` | At least one of: `documentation 📃`, `ci 🏗️`, `enhancement 🔝`, `evolvability ♻️` |
| `plan` | `plan 📋` (plus labels inherited from the parent Issue context when applicable) |

### 3. Mandatory GitHub Issue Type

Every issue MUST have a defined **GitHub Issue Type** (a native GitHub field, distinct from labels). The type MUST match the template used:

| Template | Issue Type |
|----------|------------|
| `feature-request` | `Feature` |
| `epic` | `Epic` |
| `user-story-for-api` | `Feature` |
| `user-story-for-frontend` | `Feature` |
| `bug` | `Bug` |
| `tech-task` | `Task` |
| `plan` | `Task` |

> Orgs that customize Issue Types (e.g., `Tech Task` instead of `Task`, `Plan` as its own type) MUST preserve semantic equivalence. The canonical mapping in this Lex uses the native GitHub names.

When the issue is created via a template form (`.github/ISSUE_TEMPLATE/*.yml`), the type is auto-applied by the template's `type:` field. When the issue is created via CLI (`gh issue create`), the agent MUST apply the type after creation:

```bash
# After creating the issue, apply the type via REST API
gh api -X PATCH "repos/$OWNER/$REPO/issues/$ISSUE_NUMBER" -f type=Task
```

Issues without a defined Issue Type do not satisfy this Lex and block branch/PR creation.

### 4. Assignee is NOT a creation requirement

An issue in `status: todo` MAY remain without an assignee. The assignee captures **who takes on the execution** of the work and is applied at the `todo → development` transition by `warrior-athena` (per `lex-agent-planning` execution HARD-GATE):

```bash
# Whoever picks up the work applies the assignee on the transition:
gh issue edit $ISSUE_NUMBER \
  --add-assignee "@me" \
  --remove-label "status: todo" \
  --add-label "status: development"
```

Cases where the assignee MAY be applied already at creation:
- Issue created with declared intent of immediate execution by the author themselves.
- Issue derived from an incident whose on-call is already designated.

In all other cases, leaving the issue without an assignee until `todo → development` is the canonical path — it avoids "ghost ownership" noise on issues that sit in the backlog for days with no one truly committed.

### 5. Mandatory content: Why / What / How

Every issue MUST answer three questions, explicitly or through the template sections:

| Question | What it covers | Template mapping |
|----------|----------------|-----------------|
| **Why** | Motivation, impact, problem being solved | "Why is this important?" / "Why" section |
| **What** | Objective, scope, what changes | "Objective" / "What" section |
| **How** | Implementation approach, expected outcome, definition of done | "How should it work?" / "How" section |

For `tech-task`, `bug`, and `plan`: the three questions are the direct sections of the template.

For other templates: the sections map to these questions — the **Objective** (user story) answers What, **Why is this important** answers Why, and **How can it be implemented** / acceptance criteria answers How.

### 6. `status: todo` is a creation invariant (non-Epic)

Every **non-Epic** issue MUST carry the `status: todo` label immediately after creation. An Epic is decomposed into child Issues and does not participate in Axis A of `lex-issue-status` — see `lex-issue-status` Rule 7.

The label is applied in one of three ways:

1. **Via the `.github/ISSUE_TEMPLATE/*.yml` template**: the `labels:` field of the template declares `status: todo` and GitHub applies it on submission. Canonical path for creation via UI.
2. **Via `kata-contributing-issue` (CLI/MCP)**: the kata applies `status: todo` as the final step, after applying the type and the template labels.
3. **Manually after `gh issue create`**:
   ```bash
   gh issue edit $ISSUE_NUMBER --add-label "status: todo"
   ```

Issues in the Issue-Driven flow without `status: todo` (excluding Epic) violate this Lex and block any subsequent transition — there is no "limbo" between creation and `todo`.

### 7. Agents follow the same rules

AI agents that create issues (via MCP or CLI) MUST:

1. Use the appropriate template via `kata-contributing-issue`
2. Apply the required labels during creation
3. Apply the Issue Type matching the template
4. For non-Epic issues, apply the `status: todo` label as the final creation step
5. Fill all mandatory sections (Why / What / How) before submitting

The assignee is deliberately omitted from this list — it is the responsibility of the `todo → development` transition, executed by `warrior-athena` per `lex-agent-planning`.

### 8. Branch and PR blocked until issue complies

Per `lex-issue-first` and `lex-git-branches`, no branch MAY be created and no PR MAY be opened if the associated issue:

- Does not use one of the approved templates
- Does not have at least one required label
- Does not have a defined Issue Type
- Does not carry `status: todo` (excluding Epic)
- Does not answer Why, What, and How

Note that **the assignee is not in this list** — it is enforced at the `todo → development` transition, not at creation.

## HARD-GATE (creation)

Per [`lex-hard-gate-pattern`](framework/en/_foundation/quality/lexis/lex-hard-gate-pattern.md), the textual creation block of this Lex is canonically expressed as:

```
<HARD-GATE>
warrior-athena, warrior-apollo, warrior-hephaestus, warrior-eunomia and
any other agent MUST NOT create a branch or open a PR for an issue
without it satisfying ALL canonical criteria:

  (a) Uses one of the approved templates (feature-request, epic,
      user-story-for-api, user-story-for-frontend, tech-task, bug, plan)
  (b) Has at least one required label matching the template
  (c) Has a defined GitHub Issue Type (Feature, Task, Bug, Epic)
      compatible with the template
  (d) Carries the `status: todo` label (non-Epic) immediately after
      creation
  (e) Explicitly answers Why, What, and How

This rule applies to EVERY issue, regardless of:
  - perceived size ("it is a trivial change")
  - urgency ("production fire")
  - who requested ("the CEO asked")
  - team confidence ("we already tested")

Single declared exception: issues generated automatically by
Dependabot or security scanning tools follow their own format
and are exempt. Every other exception requires explicit
justification recorded in the issue itself.
</HARD-GATE>
```

## HARD-GATE (`todo → development` transition)

The assignee capture — previously required at the creation gate — is now enforced at the transition that signals real execution commitment. This Lex declares the gate; `lex-agent-planning` invokes it operationally.

```
<HARD-GATE>
warrior-athena and any other agent MUST NOT transition a non-Epic
issue from `status: todo` to `status: development` without applying
at least one assignee in the same operation.

Mandatory preconditions to apply the transition:
  (a) Origin state is `status: todo`
  (b) Destination state is `status: development`
  (c) At least one assignee is added in the same operation
      (`gh issue edit --add-assignee` or equivalent MCP)
  (d) Issue is not an Epic (Epic does not participate in Axis A — see
      `lex-issue-status` Rule 7)

This rule applies to EVERY `todo → development` transition,
regardless of:
  - perceived size ("it is a trivial change")
  - urgency ("production fire")
  - who requested ("the CEO asked")
  - team confidence ("we already tested")

Declared exception: None. The assignee is an invariant on entry
into `development`.
</HARD-GATE>
```

## Examples

### Correct

```
Issue: "Add kata-setup-gpg-signing to the contributing framework"
Template: tech-task
Labels: documentation 📃, status: todo
Issue Type: Task
Assignee: (empty — will be applied at todo → development)
Why: Contributors need to configure GPG signing to satisfy lex-signed-commits; no step-by-step guide exists yet.
What: Create kata-setup-gpg-signing covering GPG installation, key generation, git configuration, and GitHub export.
How: Follow the GPG key generation flow; cover macOS, Linux, and Windows; add verification step.
```

```
# Transition todo → development (assignee applied in the same operation)
gh issue edit 42 \
  --add-assignee "@me" \
  --remove-label "status: todo" \
  --add-label "status: development"
```

### Incorrect

```
Issue: "fix the auth bug"
Template: none
Labels: none
Content: single line, no Why / What / How

→ ❌ Branch creation blocked per lex-git-branches
→ ❌ PR rejected per lex-issue-first
→ ❌ Fails precondition (a), (b), (c), (d), (e) of the creation HARD-GATE
```

```
# ❌ Transition todo → development without applying an assignee
gh issue edit 42 --remove-label "status: todo" --add-label "status: development"
# Fails precondition (c) of the transition HARD-GATE — execution without a declared owner
```

```
# ❌ Issue created without status: todo
gh issue create --title "feat: ..." --label "feature request ➕"
# Issue sits in limbo between creation and the flow — fails precondition (d) of the creation gate
```

## Automated Validation

- **Tool:** `kata-contributing-issue` applies template, labels, Issue Type, and `status: todo` on creation; `.github/ISSUE_TEMPLATE/*.yml` templates declare `type:` and `labels:` to auto-apply Issue Type + `status: todo`; PR review checklist verifies that the associated issue is complete on every required field; `kata-quality-gate` at Gate 2 verifies the presence of an assignee on the `todo → development` transition recorded in the issue history.
- **When:** on issue creation (via kata or template); on the `todo → development` transition (assignee enforcement); on PR creation (via lex-issue-first check).
- **Metric:** 0 open PRs referencing an issue without template, labels, Issue Type, or `status: todo`; 0 `todo → development` transitions without an assignee; 100% of issues created via kata comply on first submission.
