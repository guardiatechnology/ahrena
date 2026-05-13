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
- [ ] 3. Compute tokens and cost via ccusage (or fallback) — Development bucket
- [ ] 4. Compute implementation time (active + calendar) — Development and Review buckets
- [ ] 5. Compute external reviewers via pr-cost-stamp-reviews.sh
- [ ] 6. Render markdown block with Development / Review / Total subsections
- [ ] 7. Upsert into the PR body
- [ ] 8. Final check
```

### Step 1: Verify preconditions and directives

1. Consult `.ahrena/.directives` per `lex-directives`.
2. Read `pr_cost_tracking.enabled`. If `false` or absent → exit silently with message `pr-cost-stamp: disabled in directives, skipping`.
3. Read `pr_cost_tracking.idle_gap_minutes` (default `10`). This value is the gap (in minutes) that splits active windows inside a Claude Code session for the active-time computation.
4. Read `pr_cost_tracking.attribution_mode` (default `hook`). Modes:
   - `hook` — `scripts/pr-cost-stamp.sh` is invoked with `--branch <HEAD_REF>` and `--purpose <dev|review>`, consuming the `~/.claude/projects/*/branches.jsonl` sidecar produced by the `pr-cost-attribution.sh` hook. Allows splitting Development from Review.
   - `project` (legacy) — previous behavior: project + since filter only, no branch or purpose distinction. Kept for projects that have not migrated. The block rendered in this mode omits the Claude Code (local) Review subsection and adds a `meta.warnings` advisory.
5. Read `pr_cost_tracking.known_ai_reviewers` (list, optional). Default ships with `gemini-code-assist[bot]`, `claude[bot]`, `coderabbitai[bot]`, `qodo-merge-pro[bot]`. Projects can extend it to recognize other review bots.
6. Verify availability of `gh` (authenticated), `git`, `scripts/pr-cost-stamp.sh`, and `scripts/pr-cost-stamp-reviews.sh`. Any absence → exit with warning, do not propagate the error.
7. Try `npx ccusage@latest --version` (timeout 30s). Success → `ccusage` is the token/USD backend for the Development bucket. Failure → `scripts/pr-cost-stamp.sh` covers tokens too (without cost). In both paths, the script is the single source of truth for the time aggregates (active + calendar) — `ccusage` does not expose per-turn `timestamp` in any subcommand.

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

### Step 3: Compute tokens and cost via ccusage (or fallback) — Development bucket

`ccusage` aggregates per project, with no branch or purpose distinction. For the **Development** subsection the raw result goes straight in; turns labeled `purpose=review` still count here in `project` mode. In `hook` mode, the filter is applied by `scripts/pr-cost-stamp.sh` in parallel (Step 4) and the Development numbers in the block refer **only** to dev turns (review turns land in the Review subsection).

**Preferred — `ccusage`:**

```bash
RAW_DEV=$(npx --yes ccusage@latest daily \
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
SESSIONS_DEV=$(npx --yes ccusage@latest session \
  --since "$SINCE_DATE" \
  --json --offline 2>/dev/null \
  | jq --arg pid "$PROJECT_ID" '[.sessions[] | select(.sessionId | startswith($pid))] | length')
```

`sessionId` in `ccusage session --json` is prefixed with the project id (same format as `--project=<id>`), which allows filtering via `startswith`. A session here is a Claude Code session (one continuous conversation), not an individual commit: 6 commits inside the same conversation count as 1 session.

**Fallback — `scripts/pr-cost-stamp.sh`:** when `ccusage` is unavailable, the script itself covers tokens (no USD). In `hook` mode, pass `--branch` and `--purpose` to isolate Development:

```bash
RAW_DEV=$(scripts/pr-cost-stamp.sh \
  --project "$PROJECT_BASENAME" \
  --since "$SINCE_DATE" \
  ${ATTR_MODE_HOOK:+--branch "$HEAD_REF" --purpose dev})
```

JSON output with schema equivalent to `ccusage` (keys `totals`, `breakdown`, `meta`).

### Step 4: Compute implementation time (active + calendar) — Development and Review buckets

Time always comes from `scripts/pr-cost-stamp.sh`, regardless of the token backend, because `ccusage` does not expose per-turn `timestamp` in any subcommand (validated against `docs/guide/json-output.md`).

**Mode `hook`** — script invoked **twice**, splitting dev and review by `--purpose`:

```bash
TIME_DEV=$(scripts/pr-cost-stamp.sh \
  --project "$PROJECT_BASENAME" \
  --since "$SINCE_DATE" \
  --branch "$HEAD_REF" \
  --purpose dev \
  --idle-gap-minutes "$IDLE_GAP_MINUTES" \
  --calendar-start "$BRANCH_FIRST_COMMIT_ISO" \
  --calendar-end   "$PR_END_ISO")

TIME_REVIEW=$(scripts/pr-cost-stamp.sh \
  --project "$PROJECT_BASENAME" \
  --since "$SINCE_DATE" \
  --branch "$HEAD_REF" \
  --purpose review \
  --idle-gap-minutes "$IDLE_GAP_MINUTES" \
  --calendar-start "$BRANCH_FIRST_COMMIT_ISO" \
  --calendar-end   "$PR_END_ISO")

ACTIVE_MIN_DEV=$(echo    "$TIME_DEV"    | jq -r '.totals.active_minutes')
ACTIVE_MIN_REVIEW=$(echo "$TIME_REVIEW" | jq -r '.totals.active_minutes')
CALENDAR_MIN=$(echo      "$TIME_DEV"    | jq -r '.totals.calendar_minutes')
WARNINGS=$(echo "$TIME_DEV" "$TIME_REVIEW" | jq -s '[.[].meta.warnings // []] | add | unique')
```

`--branch` filters turns by the PR branch via the sidecar; `--purpose` filters by bucket. The calendar comes from the dev bucket (both invocations share the window; taking one avoids duplication). When the sidecar is missing, the script populates `meta.warnings` automatically — propagate to the renderer.

**Mode `project` (legacy)** — single invocation, no purpose distinction:

```bash
TIME_DEV=$(scripts/pr-cost-stamp.sh \
  --project "$PROJECT_BASENAME" \
  --since "$SINCE_DATE" \
  --idle-gap-minutes "$IDLE_GAP_MINUTES" \
  --calendar-start "$BRANCH_FIRST_COMMIT_ISO" \
  --calendar-end   "$PR_END_ISO")
TIME_REVIEW=""  # Claude Code (local) subsection is omitted from the block
```

Computation model (encoded in the script, do not reimplement in the kata):

- **Active time:** sum, per `sessionId`, of windows with gap ≤ `idle_gap_minutes` between consecutive turns. Each session with at least one turn has a 60-second floor to keep short sessions from registering as zero. Windows with a larger gap contribute zero (reflects real idle time).
- **Calendar time:** `(calendar_end − calendar_start) / 60`, in minutes, with `floor`.

Both fields come back as **integer minutes**; the renderer (Step 6) converts them to `Xh Ymin`.

### Step 5: Compute external reviewers via pr-cost-stamp-reviews.sh

Detects external AI reviewers (Gemini, Claude bot, CodeRabbit, etc.) from PR reviews and comments. Formal reviews only by default (drive-by comments inflate the count).

```bash
KNOWN_AI=$(echo "$KNOWN_AI_REVIEWERS_LIST" | paste -sd, -)  # CSV from .directives
REVIEWS_RAW=$(scripts/pr-cost-stamp-reviews.sh \
  --repo "$OWNER_REPO" \
  --pr   "$PR_NUMBER" \
  ${KNOWN_AI:+--known-ai-reviewers "$KNOWN_AI"})

AI_REVIEWERS=$(echo "$REVIEWS_RAW" | jq -c '.ai_reviewers')
HUMAN_REVIEWERS=$(echo "$REVIEWS_RAW" | jq -c '.human_reviewers')
```

Output: `{ai_reviewers, human_reviewers, meta}`. Each reviewer carries `{login, count, first_at, last_at}`. **USD is not available** for external reviewers (Gemini/Ultrareview/Cursor do not expose per-PR usage); the renderer shows `n/a` in the USD column.

### Step 5: Render markdown block

From the JSON in `RAW` and the minutes derived in `TIME_RAW`, assemble:

```markdown
<!-- ahrena:cost-stamp:start v=2 -->
## AI Assistance Cost (Claude Code)

### Development

| Metric | Value |
|---|---|
| Sessions | <sessions_dev> |
| Input / output tokens | <input_tokens_dev> / <output_tokens_dev> |
| Cache reads / writes | <cache_read_dev> / <cache_create_dev> |
| Estimated cost | $<cost_usd_dev> USD |
| Active time | <active_time_dev_human> |
| Calendar time | <calendar_time_human> (<since_date> → <pr_end_date>) |
| Models | <model_breakdown_dev> |

### Review

| Source | Sessions / Occurrences | USD | Active time |
|--------|:---------------------:|:---:|:-----------:|
| Claude Code (local, `purpose=review`) | <sessions_review> sessions | $<cost_usd_review> | <active_time_review_human> |
<additional rows — one per external AI reviewer from `pr-cost-stamp-reviews.sh` `ai_reviewers`, USD = `n/a`>

### Total

**Tracked AI cost: $<cost_total> USD · <active_total_human> active · <calendar_time_human> calendar**
External AI activity (no public USD): <count_external_ai> (<comma-separated logins>)

_Computed by `kata-pr-cost-stamp` on <utc_now>. Window: <since_date> → <pr_end_date>. Source: ccusage <ccusage_version> + pr-cost-stamp.sh <stamp_version>. Idle gap: <idle_gap_minutes>min._
_Estimates based on Anthropic public pricing; the actual invoice comes from the console. External AI sources without public usage are listed for visibility only._
<!-- ahrena:cost-stamp:end -->
```

**Conditional omissions:**

- When `attribution_mode: project` or `TIME_REVIEW` is empty/zeroed, **omit the row** "Claude Code (local, `purpose=review`)" — keep the rest of the Review subsection if external reviewers exist.
- When `ai_reviewers` is empty AND there are no `purpose=review` sessions, **omit the entire Review subsection** ("Total" then references only Development).
- When `meta.warnings` is non-empty, append a line after the footer:
  `_Warnings: <warning1>; <warning2>._`

**Idempotency on `v=1` → `v=2` migration:** if the current body contains `<!-- ahrena:cost-stamp:start -->` (no `v=` attribute), treat as `v=1` and replace with the `v=2` block. Idempotency preserved: running twice with no new turns/reviews produces the same body.

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

### Step 7: Upsert into the PR body

1. Get the current body:
   ```bash
   CURRENT_BODY=$(gh pr view $PR_NUMBER --json body --jq .body)
   ```
2. Apply marker-based upsert via Python — safe literal substitution, no backreference interpolation (`$1`, `\1`, `\n`, etc.) inside the rendered block. The regex accepts both `v=1` and `v=2` to support in-place migration:
   ```bash
   echo "$CURRENT_BODY" > /tmp/pr-body.in
   echo "$RENDERED_BLOCK" > /tmp/pr-body.block

   python3 - <<'PY'
   import re, pathlib
   body = pathlib.Path("/tmp/pr-body.in").read_text()
   block = pathlib.Path("/tmp/pr-body.block").read_text().rstrip("\n")
   pattern = re.compile(
       r"<!-- ahrena:cost-stamp:start( v=\d+)? -->.*?<!-- ahrena:cost-stamp:end -->",
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

### Step 8: Final check

- [ ] `pr_cost_tracking.enabled: true` confirmed in `.directives`
- [ ] `pr_cost_tracking.attribution_mode` read (default `hook`)
- [ ] Token backend identified (`ccusage` or fallback) and version recorded in the block
- [ ] In `hook` mode: `scripts/pr-cost-stamp.sh` invoked **twice** (`--purpose dev` and `--purpose review`), with `--branch <HEAD_REF>`, `--idle-gap-minutes`, `--calendar-start`, and `--calendar-end` populated
- [ ] `scripts/pr-cost-stamp-reviews.sh` invoked, classifying `ai_reviewers` and `human_reviewers`
- [ ] Development, Review (when applicable), and Total subsections present in the rendered block
- [ ] `<!-- ahrena:cost-stamp:start v=2 -->` / `:end` markers on dedicated lines
- [ ] Updated body contains exactly one occurrence of the markers
- [ ] `meta.warnings` (if any) appended to the footer of the block
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
pr-cost-stamp: PR #{N} body updated (block upserted)
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
