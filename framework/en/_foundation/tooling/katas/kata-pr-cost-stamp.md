# Kata: Stamp token cost (Claude Code) on the PR

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Compute tokens consumed and USD cost of AI assistance during PR development and stamp the result in the PR body via `gh pr edit`

## Objective

Calculate tokens and estimated USD cost of the Claude Code sessions that produced a Pull Request and write an idempotent markdown block in the PR body. Supports financial visibility and a baseline of automation ROI per feature, bug, or refactor. It is invoked by `kata-contributing-pr` when `pr_cost_tracking.enabled: true` in `.ahrena/.directives` and may run standalone to update existing PRs.

## When to Use

- Right after creating or updating a PR via `kata-contributing-pr` in a project that enabled `pr_cost_tracking.enabled: true`.
- Manually on an existing PR to update the stamp with additional sessions (e.g., after new commits).
- In CI or post-merge hook for historical audit (future use).

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| PR number | Yes | `$PR_NUMBER` in the current repository |
| Repository | No | `owner/repo`; default: `gh repo view --json nameWithOwner` |
| Branch | No | PR branch name; default: `gh pr view <PR> --json headRefName` |
| Initial window | No | ISO date; default: date of the first commit on the branch (`git log --reverse <base>..<head> --format=%cI \| head -1`) |

## Workflow

```
Progress:
- [ ] 1. Verify preconditions and directives
- [ ] 2. Resolve PR context
- [ ] 3. Compute usage via ccusage (or fallback)
- [ ] 4. Render markdown block
- [ ] 5. Upsert into the PR body
- [ ] 6. Final check
```

### Step 1: Verify preconditions and directives

1. Consult `.ahrena/.directives` per `lex-directives`.
2. Read `pr_cost_tracking.enabled`. If `false` or absent → exit silently with message `pr-cost-stamp: disabled in directives, skipping`.
3. Verify availability of `gh` (authenticated) and `git`. If missing → exit with warning, do not propagate the error.
4. Try `npx ccusage@latest --version` (timeout 30s). Success → `ccusage` is the backend. Failure → try `scripts/pr-cost-stamp.sh --version`. Failure → exit with warning `pr-cost-stamp: no backend available, skipping`.

### Step 2: Resolve PR context

1. `OWNER_REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)`.
2. `PR_NUMBER` from input or from `gh pr view --json number --jq .number`.
3. `HEAD_REF=$(gh pr view $PR_NUMBER --json headRefName --jq .headRefName)`.
4. `BASE_REF=$(gh pr view $PR_NUMBER --json baseRefName --jq .baseRefName)`.
5. `SINCE_DATE`: date of the first commit on the branch in `YYYYMMDD`.
   ```bash
   SINCE_DATE=$(git log --reverse $BASE_REF..$HEAD_REF --format=%cd --date=format:%Y%m%d | head -1)
   ```
6. Resolve the main repository root directory (not the worktree, when applicable):
   ```bash
   MAIN_DIR=$(cd "$(dirname "$(git rev-parse --git-common-dir)")" && pwd)
   ```
   `git rev-parse --git-common-dir` points to the main repository's `.git/` even from worktrees, ensuring sessions recorded in main and in worktrees aggregate together.
7. `PROJECT_BASENAME=$(basename "$MAIN_DIR")` — used by the fallback (basename match against `cwd` in the JSONL).
8. `PROJECT_ID=$(echo "$MAIN_DIR" | tr / -)` — Claude Code-style id (path with `/` → `-`, leading `-`); used by `ccusage`'s `--project=<id>` filter.

### Step 3: Compute usage via ccusage (or fallback)

**Preferred — `ccusage`:**

```bash
RAW=$(npx --yes ccusage@latest daily \
  --project="$PROJECT_ID" \
  --since "$SINCE_DATE" \
  --json --offline 2>/dev/null)
```

Notes:
- Subcommand is `daily`. `session` does not accept `--project`. The `--project=<id>` form (with `=`) preserves the leading `-` of the id.
- `--offline` uses the pricing table embedded in `ccusage`; remove to force online fetch when online is available and current.
- JSON output contains `daily` (entries by date) and `totals` (aggregate), with `modelBreakdowns` per entry. For unique session count, make a complementary call `ccusage session --since "$SINCE_DATE" --json` and filter by `cwd` in the JSONL line.

**Fallback — `scripts/pr-cost-stamp.sh`:**

```bash
RAW=$(scripts/pr-cost-stamp.sh \
  --project "$PROJECT_BASENAME" \
  --since "$SINCE_DATE")
```

JSON output with schema equivalent to `ccusage` (keys `totals`, `breakdown`, `meta`).

### Step 4: Render markdown block

From the JSON in `RAW`, assemble:

```markdown
<!-- ahrena:cost-stamp:start -->
## AI Assistance Cost (Claude Code)

| Metric | Value |
|---|---|
| Sessions | <sessions> |
| Input tokens | <input_tokens> |
| Output tokens | <output_tokens> |
| Cache reads | <cache_read_tokens> |
| Cache writes | <cache_create_tokens> |
| Estimated cost | $<cost_usd> USD |
| Models | <model_breakdown> |

_Computed by `kata-pr-cost-stamp` on <utc_now>. Window: <since_date> → now. Source: <tool_name> <tool_version>._
_Estimate based on Anthropic public pricing; the actual invoice comes from the console._
<!-- ahrena:cost-stamp:end -->
```

Formatting rules:

- Numbers with thousands separator per locale (`en` uses comma). For `pt-BR` and `es` apply the appropriate separator.
- `cost_usd` with 2 decimals.
- `model_breakdown`: list of `<model_id> (<percent>%)` ordered by share descending, comma-separated.
- `<utc_now>` in ISO 8601 with `Z` suffix.

### Step 5: Upsert into the PR body

1. Get the current body:
   ```bash
   CURRENT_BODY=$(gh pr view $PR_NUMBER --json body --jq .body)
   ```
2. Apply marker-based upsert:
   ```bash
   START='<!-- ahrena:cost-stamp:start -->'
   END='<!-- ahrena:cost-stamp:end -->'

   if grep -q "$START" <<< "$CURRENT_BODY"; then
     # replace existing block
     NEW_BODY=$(awk -v start="$START" -v end="$END" -v block="$RENDERED_BLOCK" '
       BEGIN{p=1}
       $0 ~ start {print block; p=0}
       p {print}
       $0 ~ end {p=1; next}
     ' <<< "$CURRENT_BODY")
   else
     # append to end of body
     NEW_BODY="${CURRENT_BODY}"$'\n\n'"${RENDERED_BLOCK}"
   fi
   ```
3. Update the PR:
   ```bash
   gh pr edit $PR_NUMBER --body "$NEW_BODY"
   ```

### Step 6: Final check

- [ ] `pr_cost_tracking.enabled: true` confirmed in `.directives`
- [ ] Backend identified (`ccusage` or fallback) and version recorded in the block
- [ ] Usage JSON obtained without error
- [ ] Rendered block contains `start`/`end` markers on dedicated lines
- [ ] Updated body contains exactly one occurrence of the markers
- [ ] `gh pr view $PR_NUMBER --json body` shows the block visible and formatted

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Cost block | Markdown delimited by HTML markers | PR body |
| Status message | Text | Agent stdout |

## Execution Example

### Input

```bash
PR_NUMBER=67
# directives: pr_cost_tracking.enabled: true
```

### Expected output (stdout)

```
pr-cost-stamp: backend=ccusage version=1.x project=ahrena since=20260507
pr-cost-stamp: 3 sessions, 245892 input, 18432 output, $4.32 USD
pr-cost-stamp: PR #67 body updated (block upserted)
```

### Resulting block (in the PR body)

See `codex-pr-cost-tracking` → "Block format" section.

## Restrictions

- **Non-blocking:** any failure (network, parsing, tooling) emits a warning and exits with code 0. The kata never aborts `kata-contributing-pr`.
- **No pricing hardcode:** the kata never recomputes cost from its own table; it uses exclusively the `ccusage` or fallback result.
- **No PII in body:** no session content (messages, code, prompts) is stamped; only aggregates.
- **Idempotency required:** re-execution without new sessions produces the same body.
- **Respect directive:** `pr_cost_tracking.enabled: false` or absent → kata is a no-op.

## References

- `codex-pr-cost-tracking` — Reference manual (data source, format, idempotency, privacy)
- `lex-directives` — Mandatory reading of `.ahrena/.directives`
- `kata-contributing-pr` — Optional step that invokes this kata
- `scripts/pr-cost-stamp.sh` — Bash fallback when `ccusage` is unavailable
- `ccusage` — https://github.com/ryoppippi/ccusage
