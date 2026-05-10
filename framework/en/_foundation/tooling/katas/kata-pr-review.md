# Kata: Start a PR Review Session (with `purpose=review` on the cost stamp)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Start a Claude Code session to review a Pull Request, ensuring the turns are counted in the `Review` subsection of the cost stamp (`kata-pr-cost-stamp`)

## Objective

Ensure every Claude Code session dedicated to reviewing a PR is explicitly marked with `purpose=review`, so the aggregator (`scripts/pr-cost-stamp.sh --purpose review`) can split **development** cost from **review** cost when `kata-pr-cost-stamp` stamps the PR. Without that mark, review turns end up in the `dev` bucket and pollute the reading of the effort that produced the PR.

This Kata is a thin instructional wrapper: the actual review work is done by `/review` (or an equivalent prompt). The Kata exists to make the `purpose=review` etiquette discoverable and consistent.

## When to Use

- The user wants to review a PR with Claude Code and the project has `pr_cost_tracking.enabled: true`.
- The user wants to dogfood the stamp: measure the review cost on the PR itself before merge.
- Invoked by `cry-pr-review`.

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| PR number | Yes | `$PR_NUMBER` in the current repository |
| Repository | No | `owner/repo`; default: `gh repo view --json nameWithOwner` |

## Workflow

```
Progress:
- [ ] 1. Check preconditions
- [ ] 2. Mark the session as purpose=review
- [ ] 3. Trigger the review
- [ ] 4. Final verification
```

### Step 1: Check preconditions

1. Read `.ahrena/.directives` (`lex-directives`).
2. Confirm `pr_cost_tracking.enabled: true`. If disabled, the Kata informs the user that the stamp will not split dev vs. review and proceeds anyway (the review still works; it just is not counted).
3. Confirm `pr_cost_tracking.attribution_mode: hook` (default when omitted). If `project`, the Kata warns that legacy mode does not bucket by `purpose` and proceeds.
4. Verify the `pr-cost-attribution.sh` hook is installed under `.claude/hooks/` and wired into `.claude/settings.json` (installed by `scripts/install.py` when the stamp is enabled).

### Step 2: Mark the session as purpose=review

Three supported paths — pick whichever fits. Path A (env var) is the official one and removes the dependency on the heuristic:

**A) Environment variable — recommended.** Start the Claude Code session with the env var set:

```bash
GUARDIA_PURPOSE=review claude
```

or, if Claude Code is already open, export before the next turn:

```bash
export GUARDIA_PURPOSE=review
```

The hook reads this variable and writes `purpose=review` to the sidecar for every subsequent turn.

**B) Textual convention (hook heuristic).** When the env var is not set, the hook inspects the first line of the prompt. Start the review session with a prompt that matches the canonical list:

| Pattern (case-insensitive) | Language | Example |
|---|---|---|
| `^/review` | en | `/review PR #72` |
| `^review pr` | en | `review PR #72` |
| `^review #N` | en | `review #72` |
| `^revise pr` | en | `revise PR #72` |
| `^revisar pr` | pt-BR | `revisar PR #72` |
| `^revisão de pr` | pt-BR | `revisão de PR #72` |
| `^revisión de pr` | es | `revisión de PR #72` |
| `pull request review` (anywhere on first line) | en | `let's do a pull request review` |

The heuristic decides per-turn — it does not persist between turns. When in doubt, prefer path A.

**C) Combined.** Use both: the env var as a contract and the prompt starting with `/review` as a habit. The first matching rule wins (env var always wins when present).

### Step 3: Trigger the review

1. With the session properly marked, invoke the official Claude Code slash command:
   ```
   /review #<PR_NUMBER>
   ```
   or conduct the review via a normal prompt — what matters for the stamp is the `purpose` mark, not the form of the review.
2. Conduct the review cycle (read the diff, comments, suggestions, follow-ups) as usual.

### Step 4: Final verification

- [ ] Session started with `GUARDIA_PURPOSE=review` exported **or** first prompt on the canonical list
- [ ] Hook recorded at least one line in `~/.claude/projects/<hash>/branches.jsonl` with `purpose: "review"` (verify with `tail -1` on the file)
- [ ] When `kata-pr-cost-stamp` runs, the PR block will show the **Review → Claude Code (local, `purpose=review`)** subsection with the matching session count.

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Marked sidecar | JSONL lines with `purpose: "review"` | `~/.claude/projects/<hash>/branches.jsonl` |
| PR review | Comments, suggestions, conversations | Target PR |

## Execution Example

```bash
# Recommended: set the env var before the session
$ GUARDIA_PURPOSE=review claude
# Inside the session:
> /review PR #72

# Verify (in another shell):
$ tail -1 ~/.claude/projects/-Users-someone-projects-ahrena/branches.jsonl
{"ts":"...","session_id":"...","purpose":"review", ...}
```

## Constraints

- **No effect when the stamp is disabled:** if `pr_cost_tracking.enabled: false`, the Kata still teaches the marking (zero cost), but no stamp will exist to report it.
- **Does not replace the human reviewer:** agent-driven review is a complementary layer; CODEOWNERS and PR policies still apply (`lex-pr-quality`).
- **No public cost for external reviewers:** if the review is by another AI agent (Gemini, Cursor, Ultrareview), `kata-pr-review` does not cover it — that path is detected automatically by `pr-cost-stamp-reviews.sh` from PR comments.

## References

- `codex-pr-cost-tracking` — Manual with the `purpose` detection cascade and the block layout with the `Review` subsection
- `kata-pr-cost-stamp` — Stamps the result on the PR, consuming the sidecar
- `cry-pr-review` — Shortcut that invokes this Kata
- `framework/templates/claude-code-hooks/pr-cost-attribution.sh` — Hook implementation
- `lex-pr-quality` — PR quality policy
