# Codex: Token cost tracking in Pull Requests (Claude Code)

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Computing and stamping AI assistance cost (Claude Code) on Pull Requests

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
| Time window | `[branch_creation_date, now]` by default. The `pr_cost_tracking.window_override_days` subkey is reserved for a future iteration; the kata does not consume it in this version. |

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

### Block format

```markdown
<!-- ahrena:cost-stamp:start -->
## AI Assistance Cost (Claude Code)

| Metric | Value |
|---|---|
| Sessions | 3 |
| Input tokens | 245,892 |
| Output tokens | 18,432 |
| Cache reads | 1,245,888 |
| Cache writes | 89,234 |
| Estimated cost | $4.32 USD |
| Models | claude-opus-4-7 (78%), claude-sonnet-4-6 (22%) |

_Computed by `kata-pr-cost-stamp` on 2026-05-09T01:30:00Z. Window: 2026-05-07 → now. Source: ccusage 1.x._
_Estimate based on Anthropic public pricing; the actual invoice comes from the console._
<!-- ahrena:cost-stamp:end -->
```

Block rules:

- HTML markers on dedicated lines, no indentation; the upsert regex depends on this.
- Fixed heading `## AI Assistance Cost (Claude Code)` for discoverability.
- Table with identical columns across languages; labels translated.
- Provenance line (UTC timestamp, window, tool version) always present.
- Estimate disclaimer always present.

### Idempotency

The kata applies upsert through the HTML markers:

1. Reads the current PR body via `gh pr view --json body`.
2. Searches for the range `<!-- ahrena:cost-stamp:start --> ... <!-- ahrena:cost-stamp:end -->`.
3. If present → replaces the range with the freshly generated block.
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
| Heuristic window `[branch_creation_date, now]` includes off-topic sessions in the same project | `--project` filter narrows the scope; `cwd` complements; future iteration may use `sessionId` tracked by hooks |
| Stacked PRs with overlapping layers | Each layer uses its window `[branch_checkout_time, now]`; accept imprecision; codex documents |
| Pricing variation across `ccusage` versions | Regression smoke test in CI; pin minimum tested version via `ccusage@<min-version>` |

### Active decisions

| Aspect | Decision |
|--------|----------|
| Primary backend | `ccusage` via `npx ccusage@latest` |
| Project filter | native `--project <repo-name>` flag |
| Fallback | `scripts/pr-cost-stamp.sh` with `jq` |
| Adoption | opt-in via `pr_cost_tracking.enabled` in `.directives` |
| Trigger | optional step in `kata-contributing-pr` |
| Idempotency | HTML markers `ahrena:cost-stamp:start/end` |
| Privacy | no masking in the first iteration; flag planned for later |
