Review Pull Request. Shortcut to dispatch a multi-axis review on an open Pull Request via warrior-argos

# Cry: Review Pull Request

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to dispatch a multi-axis review on an open Pull Request via `warrior-argos`

## Usage

```
/cry-review-pr <PR#> [--repo owner/name]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `PR#` | Yes | Pull Request number to review | `142` |
| `--repo owner/name` | No | Repository name; if omitted, infers from current `git remote` | `--repo guardiatechnology/ahrena` |

## What the Command Does

1. Invokes `warrior-argos` with the PR number and optional repository
2. Argos runs Phases 0 → 4 (Collection → Worktree → Multi-axis Review → Consolidation → Cleanup)
3. The reviewer receives a single consolidated review-comment on the PR with findings classified as 🔴 BLOCKER or 🟡 WARNING
4. Re-running on the same commit edits the existing review-comment (idempotent); re-running on a new commit creates a new review (audit trail preserved)

## Prompt Template

```
Context:
- PR number: {{PR#}}
- Repository: {{repo}} (or inferred from `git remote`)

Task:
Act as `warrior-argos`. Run the full multi-axis Pull Request review per the warrior's defined flow:
- Phase 0: Collect PR, linked Issue, PRD/Capability Spec on Notion (when available), local .ahrena/issues/{N}/, and the referenced plan
- Phase 1: Create isolated worktree via `kata-git-worktree`
- Phase 2: Run review katas applicable to the diff (Python, frontend, AWS, API design, CloudEvents, security) plus axes B (spec alignment), C (local tests), D (backward compatibility), F (Lexis/Codex compliance)
- Phase 3: Consolidate findings into a single review-comment with idempotent marker `<!-- argos-review-id:sha256(pr_number+commit_sha) -->`; post via `gh pr review --request-changes` (≥1 finding) or `--comment` (0 findings); never `--approve`
- Phase 4: Remove the worktree

Output format:
- Phase summary (collected artifacts, detected stack, axes routed)
- Final review-comment body (also posted to the PR)
```

## Invocation Example

**Input:**

```
/cry-review-pr 142
```

**Expected output:**

```
Argos here. Reviewing PR #{N} on guardiatechnology/ahrena.

Phase 0 — Collection: Issue #138 ✅ | PRD on Notion ✅ | .ahrena/issues/138/ ✅
Phase 1 — Worktree: .worktrees/review-pr-142/ created
Phase 2 — Stack detected: Python + OpenAPI + CloudEvents + migrations
         Axes routed: A (python, api-design, events), B, C (pytest+mypy), D (oasdiff ✅, squawk ❌), E, F
Phase 3 — Findings: 🔴 2 BLOCKER, 🟡 4 WARNING → posted as `--request-changes` (review id: a1b2c3d4)
Phase 4 — Worktree removed

Review URL: https://github.com/guardiatechnology/ahrena/pull/142#pullrequestreview-...
```

## Constraints

- The Cry triggers a review only; it does not approve, modify the PR's source code, or push fix-up commits
- The reviewer running the cry MUST have authenticated `gh` and the configured MCP servers (`github`, optional `notion`) per `.ahrena/.directives`
- A new review is created per new head commit; subsequent dispatches on the same commit edit the existing review-comment
- The Cry does not run automatically on every opened PR — it requires explicit human dispatch (the human reviewer decides which PR to review and when)

## Associated Warrior and Katas

- **warrior-argos** — Multi-axis Pull Request reviewer (orchestrator)
- Katas executed by Argos: `kata-mcp-github-read`, `kata-mcp-notion-read`, `kata-git-worktree`, `kata-python-review`, `kata-frontend-review`, `kata-aws-review`, `kata-api-design-review`, `kata-events-review`, `kata-security-review`, `kata-quality-gate`
