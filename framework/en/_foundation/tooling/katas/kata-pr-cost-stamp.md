# Kata: Stamp token cost and implementation time (Claude Code) on the PR

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Compute tokens, USD cost, and implementation time of AI assistance during PR development and stamp the result in the PR body via `gh pr edit`

## Objective

Calculate tokens, estimated USD cost, and implementation time (active + calendar) of the Claude Code sessions that produced a Pull Request and write an idempotent markdown block in the PR body. Supports financial visibility, automation ROI, and throughput reading per feature, bug, or refactor. It is invoked by `kata-contributing-pr` when `pr_cost_tracking.enabled: true` in `.ahrena/.directives` and may run standalone to update existing PRs.

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
- [ ] 3. Compute tokens and cost via ccusage (or fallback)
- [ ] 4. Compute implementation time (active + calendar)
- [ ] 5. Render markdown block
- [ ] 6. Upsert into the PR body
- [ ] 7. Final check
```

### Step 1: Verify preconditions and directives

1. Consult `.ahrena/.directives` per `lex-directives`.
2. Read `pr_cost_tracking.enabled`. If `false` or absent → exit silently with message `pr-cost-stamp: disabled in directives, skipping`.
3. Read `pr_cost_tracking.idle_gap_minutes` (default `10`). This value is the gap (in minutes) that splits active windows inside a Claude Code session for the active-time computation.
4. Verify availability of `gh` (authenticated), `git`, and `scripts/pr-cost-stamp.sh` (present and executable; required to compute time). Any absence → exit with warning, do not propagate the error.
5. Try `npx ccusage@latest --version` (timeout 30s). Success → `ccusage` is the token/USD backend. Failure → `scripts/pr-cost-stamp.sh` covers tokens too (without cost). In both paths, the script is the single source of truth for the time aggregates (active + calendar) — `ccusage` does not expose per-turn `timestamp` in any subcommand.

### Step 2: Resolve PR context

1. `OWNER_REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)`.
2. `PR_NUMBER` from input or from `gh pr view --json number --jq .number`.
3. `HEAD_REF=$(gh pr view $PR_NUMBER --json headRefName --jq .headRefName)`.
4. `BASE_REF=$(gh pr view $PR_NUMBER --json baseRefName --jq .baseRefName)`.
5. `SINCE_DATE` (`YYYYMMDD` for `--since`) and `BRANCH_FIRST_COMMIT_ISO` (ISO 8601 for `--calendar-start`). If the branch has no commits over the base (fresh branch or resolution error), fall back to today's date:
   ```bash
   SINCE_DATE=$(git log --reverse $BASE_REF..$HEAD_REF --format=%cd --date=format:%Y%m%d | head -1)
   BRANCH_FIRST_COMMIT_ISO=$(git log --reverse $BASE_REF..$HEAD_REF --format=%cI | head -1)
   [ -z "$SINCE_DATE" ] && SINCE_DATE=$(date -u +%Y%m%d)
   [ -z "$BRANCH_FIRST_COMMIT_ISO" ] && BRANCH_FIRST_COMMIT_ISO=$(date -u +%Y-%m-%dT%H:%M:%SZ)
   ```
6. `PR_END_ISO`: upper bound of the calendar window. If the PR is already merged, use `mergedAt`; otherwise current UTC time:
   ```bash
   MERGED_AT=$(gh pr view $PR_NUMBER --json mergedAt --jq .mergedAt)
   if [ -n "$MERGED_AT" ] && [ "$MERGED_AT" != "null" ]; then
     PR_END_ISO="$MERGED_AT"
   else
     PR_END_ISO=$(date -u +%Y-%m-%dT%H:%M:%SZ)
   fi
   ```
7. Resolve the main repository root directory (not the worktree, when applicable):
   ```bash
   MAIN_DIR=$(cd "$(dirname "$(git rev-parse --git-common-dir)")" && pwd)
   ```
   `git rev-parse --git-common-dir` points to the main repository's `.git/` even from worktrees, ensuring sessions recorded in main and in worktrees aggregate together.
8. `PROJECT_BASENAME=$(basename "$MAIN_DIR")` — used by the fallback and by the time computation (basename match against `cwd` in the JSONL).
9. `PROJECT_ID=$(echo "$MAIN_DIR" | tr / -)` — Claude Code-style id (path with `/` → `-`, leading `-`); used by `ccusage`'s `--project=<id>` filter.

### Step 3: Compute tokens and cost via ccusage (or fallback)

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
- JSON output contains `daily` (entries by date) and `totals` (aggregate), with `modelBreakdowns` per entry.

**Unique session count** (complementary call; `daily` does not expose it):

```bash
SESSIONS=$(npx --yes ccusage@latest session \
  --since "$SINCE_DATE" \
  --json --offline 2>/dev/null \
  | jq --arg pid "$PROJECT_ID" '[.sessions[] | select(.sessionId | startswith($pid))] | length')
```

`sessionId` in `ccusage session --json` is prefixed with the project id (same format as `--project=<id>`), which allows filtering via `startswith`. A session here is a Claude Code session (one continuous conversation), not an individual commit: 6 commits inside the same conversation count as 1 session.

**Fallback — `scripts/pr-cost-stamp.sh`:**

```bash
RAW=$(scripts/pr-cost-stamp.sh \
  --project "$PROJECT_BASENAME" \
  --since "$SINCE_DATE")
```

JSON output with schema equivalent to `ccusage` (keys `totals`, `breakdown`, `meta`).

### Step 4: Compute implementation time (active + calendar)

Time always comes from `scripts/pr-cost-stamp.sh`, regardless of the token backend, because `ccusage` does not expose per-turn `timestamp` in any subcommand (validated against `docs/guide/json-output.md`).

```bash
TIME_RAW=$(scripts/pr-cost-stamp.sh \
  --project "$PROJECT_BASENAME" \
  --since "$SINCE_DATE" \
  --idle-gap-minutes "$IDLE_GAP_MINUTES" \
  --calendar-start "$BRANCH_FIRST_COMMIT_ISO" \
  --calendar-end   "$PR_END_ISO")

ACTIVE_MIN=$(echo "$TIME_RAW" | jq -r '.totals.active_minutes')
CALENDAR_MIN=$(echo "$TIME_RAW" | jq -r '.totals.calendar_minutes')
```

When the token backend is already the script itself (fallback path), a single invocation covers everything — pass `--idle-gap-minutes`, `--calendar-start`, and `--calendar-end` on the Step 3 call and reuse `totals.active_minutes` and `totals.calendar_minutes`.

Computation model (encoded in the script, do not reimplement in the kata):

- **Active time:** sum, per `sessionId`, of windows with gap ≤ `idle_gap_minutes` between consecutive turns. Each session with at least one turn has a 60-second floor to keep short sessions from registering as zero. Windows with a larger gap contribute zero (reflects real idle time).
- **Calendar time:** `(calendar_end − calendar_start) / 60`, in minutes, with `floor`.

Both fields come back as **integer minutes**; the renderer (Step 5) converts them to `Xh Ymin`.

### Step 5: Render markdown block

From the JSON in `RAW` and the minutes derived in `TIME_RAW`, assemble:

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
| Active time | <active_time_human> |
| Calendar time | <calendar_time_human> (<since_date> → <pr_end_date>) |
| Models | <model_breakdown> |

_Computed by `kata-pr-cost-stamp` on <utc_now>. Window: <since_date> → <pr_end_date>. Source: <tool_name> <tool_version>. Idle gap: <idle_gap_minutes>min._
_Estimates based on Anthropic public pricing; the actual invoice comes from the console._
<!-- ahrena:cost-stamp:end -->
```

Formatting rules:

- Numbers with thousands separator per locale (`en` uses comma). For `pt-BR` and `es` apply the appropriate separator.
- `cost_usd` with 2 decimals.
- `model_breakdown`: list of `<model_id> (<percent>%)` ordered by share descending, comma-separated.
- `<utc_now>`, `<since_date>`, and `<pr_end_date>` in ISO 8601 with `Z` suffix (or plain date for `since_date`/`pr_end_date` when time-of-day adds no context).
- **Humanized time** from integer minutes:
  - `< 60min` → `"<n>min"` (e.g., `47min`)
  - `< 24h`  → `"<h>h <m>min"` (e.g., `2h 47min`); omit `<m>min` when zero (`3h`)
  - `≥ 24h` → `"<d>d <h>h"` (e.g., `1d 4h`); omit `<h>h` when zero (`2d`)
- If `active_minutes` or `calendar_minutes` is `0`, render `0min`.

### Step 6: Upsert into the PR body

1. Get the current body:
   ```bash
   CURRENT_BODY=$(gh pr view $PR_NUMBER --json body --jq .body)
   ```
2. Apply marker-based upsert via Python — safe literal substitution, no backreference interpolation (`$1`, `\1`, `\n`, etc.) inside the rendered block:
   ```bash
   echo "$CURRENT_BODY" > /tmp/pr-body.in
   echo "$RENDERED_BLOCK" > /tmp/pr-body.block

   python3 - <<'PY'
   import re, pathlib
   body = pathlib.Path("/tmp/pr-body.in").read_text()
   block = pathlib.Path("/tmp/pr-body.block").read_text().rstrip("\n")
   pattern = re.compile(
       r"<!-- ahrena:cost-stamp:start -->.*?<!-- ahrena:cost-stamp:end -->",
       re.DOTALL,
   )
   if pattern.search(body):
       # replace existing block; lambda forces literal replacement
       new_body = pattern.sub(lambda _: block, body)
   else:
       # append to end of body separated by a blank line
       new_body = body.rstrip("\n") + "\n\n" + block + "\n"
   pathlib.Path("/tmp/pr-body.in").write_text(new_body)
   PY

   NEW_BODY=$(cat /tmp/pr-body.in)
   ```

   Why Python and not `awk`/`perl`/`sed`: macOS BWK `awk` does not pass multi-line variables; `perl`'s `s///` (without `e`) interprets sequences like `\n` in the replacement; `sed` requires heavy escaping of special characters. Python with `lambda _: block` in `re.sub` substitutes the block literally, without re-interpreting backreferences. Python 3 is present by default on macOS, Linux, and most CI runners.
3. Update the PR:
   ```bash
   gh pr edit $PR_NUMBER --body "$NEW_BODY"
   ```

### Step 7: Final check

- [ ] `pr_cost_tracking.enabled: true` confirmed in `.directives`
- [ ] Token backend identified (`ccusage` or fallback) and version recorded in the block
- [ ] `scripts/pr-cost-stamp.sh` invoked for time, with `--idle-gap-minutes`, `--calendar-start`, and `--calendar-end` populated
- [ ] Token JSON and time JSON obtained without error
- [ ] "Active time" and "Calendar time" rows present in the rendered block
- [ ] Block contains `start`/`end` markers on dedicated lines
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
pr-cost-stamp: time backend=pr-cost-stamp.sh 1.1.0 idle_gap=10min
pr-cost-stamp: active 167min (2h 47min), calendar 1680min (1d 4h)
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
- **Active time is heuristic:** depends on `idle_gap_minutes` to separate engaged work from idle gaps; cross-machine does not capture sessions on other machines; in stacked PRs the windows of layers overlap. Limitations documented in `codex-pr-cost-tracking`.

## References

- `codex-pr-cost-tracking` — Reference manual (data source, format, idempotency, privacy)
- `lex-directives` — Mandatory reading of `.ahrena/.directives`
- `kata-contributing-pr` — Optional step that invokes this kata
- `scripts/pr-cost-stamp.sh` — Bash fallback when `ccusage` is unavailable
- `ccusage` — https://github.com/ryoppippi/ccusage
