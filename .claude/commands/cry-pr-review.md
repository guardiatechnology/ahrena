Start PR review with `purpose=review`. Shortcut to start a Claude Code PR-review session already tagged for the Review subsection of the cost stamp

# Cry: Start PR review with `purpose=review`

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to start a Claude Code PR-review session already tagged for the `Review` subsection of the cost stamp

## Usage

```
/cry-pr-review <PR_NUMBER> [repository]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `PR_NUMBER` | Yes | PR number to review | `72` |
| `repository` | No | `owner/repo`; default: `gh repo view --json nameWithOwner` | `guardiatechnology/ahrena` |

## What the Command Does

1. Resolves `PR_NUMBER` and repository from parameters or context.
2. Invokes `kata-pr-review` with those inputs.
3. The Kata verifies `pr_cost_tracking.enabled` and `attribution_mode` in `.ahrena/.directives`, guides the user on how to mark the session as `purpose=review` (paths A/B/C documented in the Kata), and triggers `/review` on the PR.

## Prompt Template

```
Context:
- Target PR: #{{PR_NUMBER}}
- Repository: {{repository}} (optional; resolve via `gh repo view` if absent)

Task:
Invoke kata-pr-review with PR_NUMBER and repository resolved. Before
triggering /review, guide the user to set `GUARDIA_PURPOSE=review`
(or start the review session with `GUARDIA_PURPOSE=review claude`) so
turns are counted in the Review subsection of the stamp.

Output format:
Marking status (env var set / heuristic prompt) followed by the
conduct of the review as you would normally with /review.
```

## Invocation Example

```
/cry-pr-review 72
```

**Expected output:** the agent reminds the user to set `GUARDIA_PURPOSE=review` (or recommends starting the session with `/review PR #72`), confirms the hook wrote `purpose=review` to the sidecar, and proceeds with the review.
