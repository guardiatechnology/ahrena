# Codex: Token cost and implementation time tracking in Pull Requests (Claude Code)

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Computing and stamping AI assistance cost (Claude Code) on Pull Requests — tokens, USD, and implementation time

## Content

### Principles

1. **Opt-in per project.** The capability is disabled by default. The project declares `pr_cost_tracking.enabled: true` in `.ahrena/.directives` to enable it. No Lexis enforces use — cost is internal data and each team decides whether to expose it.
2. **Single source of pricing.** The USD-per-model table is `ccusage`'s, which mirrors Anthropic's public pricing. The kata never hardcodes values; quarterly audits confirm `ccusage` remains current.
3. **Idempotency via HTML markers.** The block is delimited by `<!-- ahrena:cost-stamp:start -->` and `<!-- ahrena:cost-stamp:end -->`. Re-running the kata against the same PR replaces the content between markers; never duplicates.
4. **Non-blocking.** Stamp failure (network, tool unavailable, parsing) does not block the PR. The kata logs the error and continues.
5. **Estimate, not invoice.** The displayed value is an estimate based on public pricing; the actual invoice comes from the Anthropic console. The block states this explicitly.

### Data source

| Item | Detail |
|------|--------|
| Log location | `~/.claude/projects/<project-hash>/*.jsonl` |
| Granularity | one JSONL line per turn; each turn carries `usage.input_tokens`, `usage.output_tokens`, `usage.cache_read_input_tokens`, `usage.cache_creation_input_tokens`, `model`, `cwd`, `sessionId`, `timestamp` |
| Project hash | derived by Claude Code from the project's absolute path; `ccusage` translates the hash back to the project name via `--project` or `--instances` |
| Token time window | `[branch_creation_date, now]` by default (`--since` filter on `ccusage`/script) |
| Calendar time window | `[branch_creation_date, mergedAt or now]` — uses `mergedAt` when the PR is merged, current UTC time when still open |
| Idle gap | `pr_cost_tracking.idle_gap_minutes` (default `10`); splits active windows inside a session for the active-time computation |

### Supported tools

| Tool | When to use | Base command |
|------|-------------|--------------|
| `ccusage` (preferred) | Whenever `npx`/`node` are available | `npx ccusage@latest daily --project=<project-id> --since <YYYYMMDD> --json` |
| `scripts/pr-cost-stamp.sh` (fallback) | Environments without Node (e.g., minimal runners) | direct JSONL parsing with `jq` |

The kata tries `ccusage` first. Execution failure (not data failure) falls back to the secondary path. Fallback failure emits a warning and proceeds without a stamp.

### Project filter

`ccusage`'s `daily`, `weekly`, `monthly`, and `blocks` subcommands accept `--project <id>` and `--instances` (breakdown per project). The `<id>` is the identifier derived from the project's absolute path, with `/` replaced by `-` and a leading `-` (e.g., `/Users/foo/repo` → `-Users-foo-repo`). Use the `--project=<id>` form to preserve the leading `-` on the command line.

The `session` subcommand does not accept `--project` and is therefore not used by this Codex.

The kata uses `--project=<id>` as the primary filter; the `cwd` filter on the JSONL line remains as a documented complement, useful when the user works on multiple clones of the same repository with identical names.

### Attribution (`hook` vs `project` mode)

The `pr_cost_tracking.attribution_mode` directive controls how turns are bound to a specific PR.

| Mode | Mechanism | When to use |
|------|-----------|-------------|
| **`hook`** (default) | The `pr-cost-attribution.sh` hook writes `~/.claude/projects/<hash>/branches.jsonl` per turn; `pr-cost-stamp.sh --branch <head> --purpose <dev\|review>` filters | New projects or those wanting fine precision (off-branch turns are excluded; review goes to its own bucket) |
| **`project`** (legacy) | Project + since filter only (no sidecar) | Backward compatibility; PRs predating the hook |

In `hook` mode, the cascade for deciding a turn's `purpose` (first matching rule wins, decided per turn):

1. **Environment variable `GUARDIA_PURPOSE`** — literal value (e.g., `dev`, `review`, `refactor`). Official path via `cry-pr-review`.
2. **Heuristic on the first line of the prompt** — frozen canonical list (changes via ADR):
   ```
   ^/review\b
   ^review[[:space:]]+pr\b
   ^review[[:space:]]+#[0-9]+
   ^revise[[:space:]]+pr\b
   ^revise[[:space:]]+#[0-9]+
   ^revisar[[:space:]]+pr\b
   ^revisar[[:space:]]+#[0-9]+
   ^revis(ã|a)o[[:space:]]+(de[[:space:]]+)?pr\b
   ^revisi(ó|o)n[[:space:]]+(de[[:space:]]+)?pr\b
   pull[[:space:]]+request[[:space:]]+review
   ```
   Match → `purpose=review`. Multi-byte UTF-8 uses explicit alternation (BSD grep on macOS does not handle UTF-8 inside `[]`).
3. **Default**: `purpose=dev`.

Three recommended usage paths:

- **A — `cry-pr-review` (recommended):** the Cry calls `kata-pr-review`, which guides the user to set `GUARDIA_PURPOSE=review` before launching `claude`. Deterministic.
- **B — Heuristic:** safety net when the env var is not set. Start the review session with a prompt from the canonical list.
- **C — Textual convention:** simply start with `/review PR #<N>` in the prompt. Documented as a habit; identical effect to path B.

The `branches.jsonl` sidecar is append-only per turn; `pr-cost-stamp.sh` collapses to a `session_id → {branch, purpose}` map by taking the most recent entry per session. Sessions with no sidecar entry are excluded when `--branch`/`--purpose` is requested — that is the contract.

### Review cost

The block's **Review** subsection aggregates review effort by source. The cost is honest: USD is summed only for sources with public pricing; external reviewers appear as occurrences for visibility.

| Source | USD available? | Detection |
|--------|:--------------:|-----------|
| Claude Code local (`purpose=review`) | **Yes** (same `ccusage` backend or fallback) | `pr-cost-stamp.sh --purpose review` consuming the sidecar |
| Gemini Code Assist | Not public | `pr-cost-stamp-reviews.sh` via `gh pr view --json reviews` |
| Claude bot (`claude[bot]`) | Not public | idem |
| Other AI bots (CodeRabbit, qodo-merge, etc.) | Not public | idem; extra logins come from `pr_cost_tracking.known_ai_reviewers` |
| Human reviewer | Out of scope | Listed under `human_reviewers` in the script JSON, but omitted from the block |

`pr-cost-stamp-reviews.sh` classifies as AI via two signals (either suffices):
1. GitHub `User.type == "Bot"` (authoritative).
2. Login matches the allow-list (built-ins `gemini-code-assist[bot]`, `claude[bot]`, `coderabbitai[bot]`, `qodo-merge-pro[bot]` + the project's `pr_cost_tracking.known_ai_reviewers`).

By default, the script counts only formal reviews (no drive-by comments) — `--include-comments` opts in to also tally inline and issue-level comments. The "Total" line aggregates only available USD and lists the count of external AI reviewers without USD.

### Implementation time

The block carries **two time metrics**, always together when `pr_cost_tracking.enabled: true`:

| Metric | Definition | Data source |
|--------|------------|-------------|
| **Active time** | Sum, per `sessionId`, of windows with gap ≤ `idle_gap_minutes` between consecutive turns. Each session with at least one turn has a 60-second floor. Approximates hours of work engaged with the AI. | per-turn `timestamp` in JSONL; aggregated by `scripts/pr-cost-stamp.sh` |
| **Calendar time** | `(branch_creation_time, mergedAt or now)` in minutes. Approximates lead time / throughput. | `git log --reverse <base>..<head> --format=%cI`; `gh pr view --json mergedAt` |

#### Why two numbers?

- **Active time** answers "how much did this cost in hours of engaged work". It is the cost-in-hours metric, complementary to USD.
- **Calendar time** answers "how long did the feature stay in flight on the wall clock". It is a flow metric (lead time), not a cost metric.

Together they distinguish *concentration* (high active, low calendar — focused sprint) from *dilution* (low active, high calendar — feature waited on review, dependency, decision).

#### Active-time calculation

Canonical model: per `sessionId`, sort turns by `timestamp`; accumulate `delta` only when `delta ≤ idle_gap_minutes × 60`; windows with a larger gap contribute zero (real idle). Sessions with a single turn get a 60-second floor to avoid registering "zero work".

Example: session with turns at `t=0s, t=30s, t=65s, t=9000s, t=9020s` and `idle_gap_minutes=10` (= 600s):
- 30s ≤ 600 → add 30s
- 35s ≤ 600 → add 35s
- 8935s > 600 → add 0 (idle interval)
- 20s ≤ 600 → add 20s
- Total: 85s = 1min (after the script applies the floor).

Single-turn case: a session with a single turn yields an empty delta sum (range from 1 to 1 has no elements), and the floor lifts the result to the documented 60-second minimum.

#### Calendar-time calculation

`floor((calendar_end − calendar_start) / 60)` in minutes. `calendar_start` = first commit of the branch (`git log --reverse <base>..<head> --format=%cI | head -1`); `calendar_end` = PR `mergedAt` or current UTC time when still open.

#### Single backend for time

`ccusage` aggregates at the day level (`daily`), in 5-hour billing windows (`blocks`), or per session (`session` with `lastActivity`), but **does not expose per-turn `timestamp`** in any subcommand (validated against `docs/guide/json-output.md`). For that reason, time is always computed by `scripts/pr-cost-stamp.sh`, even when `ccusage` is the token/USD backend.

### Block format (schema `v=2`)

```markdown
<!-- ahrena:cost-stamp:start v=2 -->
## AI Assistance Cost (Claude Code)

### Development

| Metric | Value |
|---|---|
| Sessions | 3 |
| Input / output tokens | 245,892 / 18,432 |
| Cache reads / writes | 1,245,888 / 89,234 |
| Estimated cost | $4.32 USD |
| Active time | 2h 47min |
| Calendar time | 1d 4h (2026-05-04 → 2026-05-05) |
| Models | claude-opus-4-7 (78%), claude-sonnet-4-6 (22%) |

### Review

| Source | Sessions / Occurrences | USD | Active time |
|--------|:---------------------:|:---:|:-----------:|
| Claude Code (local, `purpose=review`) | 1 session | $1.10 | 18min |
| Gemini Code Assist | 1 review | n/a | n/a |

### Total

**Tracked AI cost: $5.42 USD · 3h 5min active · 1d 4h calendar**
External AI activity (no public USD): 1 (gemini-code-assist[bot])

_Computed by `kata-pr-cost-stamp` on 2026-05-09T01:30:00Z. Window: 2026-05-07 → 2026-05-09. Source: ccusage 1.x + pr-cost-stamp.sh 1.2.0. Idle gap: 10min._
_Estimates based on Anthropic public pricing; the actual invoice comes from the console. External AI sources without public usage are listed for visibility only._
<!-- ahrena:cost-stamp:end -->
```

Block rules:

- HTML markers on dedicated lines, no indentation; the upsert regex depends on this. The `v=2` attribute lets downstream parsers detect the version; upsert accepts both `v=1` (legacy) and `v=2`.
- Fixed heading `## AI Assistance Cost (Claude Code)` for discoverability.
- Subsections: **Development** (always present), **Review** (entire subsection omitted when there are no `purpose=review` sessions AND no external AI reviewers), **Total** (always present).
- "Active time" and "Calendar time" rows always present in Development; "Active time" in Review only when there are local `purpose=review` sessions.
- `attribution_mode: project` (legacy) mode: the Review subsection omits the "Claude Code (local, `purpose=review`)" row and the footer carries `_Warnings: no branch attribution data; counts may include off-branch sessions._`
- Provenance line (UTC timestamp, window, tool versions, idle gap) always present.
- Estimate disclaimer always present; external-reviewers-no-USD disclaimer present whenever at least one external source is listed.
- Time formatted from integer minutes: `< 60min` → `<n>min`; `< 24h` → `<h>h <m>min` (omit `<m>min` when zero); `≥ 24h` → `<d>d <h>h` (omit `<h>h` when zero); `0` → `0min`.

### Idempotency

The kata applies upsert through the HTML markers:

1. Reads the current PR body via `gh pr view --json body`.
2. Searches for the range `<!-- ahrena:cost-stamp:start( v=\d+)? --> ... <!-- ahrena:cost-stamp:end -->` (regex accepts both `v=1` and `v=2`).
3. If present → replaces the range with the freshly generated block (`v=1` → `v=2` migration is in-place).
4. If absent → appends the block to the end of the body, separated by a blank line.
5. Updates the PR via `gh pr edit --body`.

Running the kata twice in a row produces exactly the same body if no new sessions occurred in the interval.

### Privacy

- **Public repositories:** the PR body is public the moment the PR opens. Absolute USD cost can be sensitive; each team decides whether to expose. The kata respects the `.directives` opt-in; nothing is stamped by default.
- **Optional masking:** `pr_cost_tracking.mask_absolute_cost: true` replaces the absolute value with a qualitative band (`< $1`, `$1–$10`, `$10–$50`, `> $50`). Configuration not implemented in this first iteration — declared for a future iteration.
- **No PII:** no session content (messages, prompts, code) is stamped. Only numeric aggregates.

### Known limitations

| Limitation | Mitigation |
|------------|------------|
| Cross-machine sessions not captured (only the machine running the kata counts) | Codex documents this; cross-machine aggregation is out of scope for this iteration |
| `project` (legacy) mode includes off-branch sessions | Migrate to `hook` mode (new default); the sidecar excludes turns from other branches |
| `hook` mode requires the hook installed in `.claude/settings.json` | `scripts/install.py` installs it automatically when `pr_cost_tracking.enabled: true` and `attribution_mode: hook` |
| A session changes branch or purpose mid-session | Per-session classification uses the **most recent** sidecar entry; sessions that flip to `purpose=review` mid-flight are counted as review for the entire session. Accept as approximation; rare in dedicated worktrees |
| `branches.jsonl` grows without bound | `pr_cost_tracking.branches_sidecar_max_mb` directive (default 50MB) emits a warning when exceeded; automatic rotation in a future iteration |
| Prompt heuristic may produce false positives ("review" word in another context) | The trigger list is specific (frozen regex / prefixes, anchored on the first line). Path A (`cry-pr-review` with the env var) eliminates the risk |
| USD not available for external reviewers (Gemini, Ultrareview, Cursor) | Accept; the block shows count + `n/a`. Documented as "visibility only" |
| Stacked PRs with overlapping layers — sum of active time across layers > real active time | Each layer uses its window `[branch_checkout_time, mergedAt or now]`; accept imprecision; codex documents |
| Pricing variation across `ccusage` versions | Regression smoke test in CI; pin minimum tested version via `ccusage@<min-version>` |
| Mis-calibrated `idle_gap_minutes` distorts active time | Default 10min covers most flows; configurable per project; effective value is shown on the provenance line |
| Active time ≠ manual reading/editing time | Metric reflects turn cadence with the AI, not 100% human work before/after; document as "AI assistance hours", not "total feature hours" |
| `BRANCH_FIRST_COMMIT_ISO` falls back to `date -u` when the branch has no commits over the base yet | Intentional fallback in the kata (Step 2) so the script never receives an empty string. Result: calendar time appears as a tiny just-opened window, with no signal that the bound was synthetic. Accept until the branch accumulates commits and the stamp is re-run |

### Active decisions

| Aspect | Decision |
|--------|----------|
| Token/USD backend | `ccusage` via `npx ccusage@latest` (with fallback to `scripts/pr-cost-stamp.sh`) |
| Time backend (active + calendar) | `scripts/pr-cost-stamp.sh` always — `ccusage` does not expose per-turn `timestamp` |
| Project filter | native `--project=<id>` flag on `ccusage`; `cwd` basename in the fallback |
| Fine attribution (mode) | `pr_cost_tracking.attribution_mode`; default `hook` for new projects, `project` kept as backward-compatible legacy |
| `purpose` cascade | `GUARDIA_PURPOSE` env var → first-line heuristic (frozen canonical list) → default `dev` |
| Known AI reviewers | `pr_cost_tracking.known_ai_reviewers` in `.directives`; built-ins: gemini-code-assist, claude, coderabbitai, qodo-merge-pro |
| Review counting | formal reviews only by default (drive-by comments excluded); `--include-comments` opts in |
| Block schema | `v=2` with Development / Review / Total subsections; upsert accepts `v=1` for in-place migration |
| Adoption | opt-in via `pr_cost_tracking.enabled` in `.directives` |
| `idle_gap_minutes` | sub-flag in `.directives`; default `10` |
| Trigger | optional step in `kata-contributing-pr` |
| Idempotency | HTML markers `ahrena:cost-stamp:start[ v=N]/end` |
| Privacy | no masking in the first iteration; flag planned for later |
