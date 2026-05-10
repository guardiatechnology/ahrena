#!/usr/bin/env bash
# pr-cost-stamp.sh — Aggregator for kata-pr-cost-stamp.
#
# Parses Claude Code JSONL logs in ~/.claude/projects/<hash>/*.jsonl, filters by
# project basename and date, and emits a JSON aggregate compatible with the
# schema the kata expects (totals + breakdown + meta).
#
# Two roles:
#   1. Token / model fallback when ccusage is unavailable
#      (cost_usd remains null; meta.cost_unavailable=true).
#   2. Single source of truth for implementation-time aggregates
#      (totals.active_minutes from JSONL timestamps; totals.calendar_minutes
#      when --calendar-start/--calendar-end are provided). The kata invokes
#      this path even when ccusage is the token backend, because ccusage does
#      not expose per-turn timestamps in any subcommand.
#
# Cost estimation is intentionally OUT OF SCOPE for this script to honor the
# no-hardcode-pricing principle.
#
# Requires: bash 3.2+, jq, find, date.

set -euo pipefail

VERSION="1.2.0"

usage() {
  cat <<USAGE
pr-cost-stamp.sh — Aggregator for Claude Code JSONL logs

Usage:
  pr-cost-stamp.sh --project <name> --since <YYYYMMDD> [options]
  pr-cost-stamp.sh --version

Required:
  --project <name>           Project basename to filter (matches cwd basename in JSONL)
  --since <date>             YYYYMMDD lower bound (inclusive) for line timestamp

Time aggregates (optional):
  --idle-gap-minutes <N>     Gap (minutes) that splits active windows. Default: 10.
  --calendar-start <ISO8601> Lower bound for calendar duration (e.g. branch first commit).
  --calendar-end   <ISO8601> Upper bound for calendar duration. Default: current UTC time.

Branch / purpose attribution (optional, requires pr-cost-attribution.sh hook):
  --branch <name>            Restrict to turns whose sidecar entry shows branch == <name>.
  --purpose <dev|review>     Restrict to turns whose sidecar entry shows purpose == <value>.
  --branches-sidecar <glob>  Override sidecar discovery (default: ~/.claude/projects/*/branches.jsonl).

Other:
  --version                  Print version and exit
  -h, --help                 Print this help and exit

Output: JSON on stdout with keys totals, breakdown, meta.
totals.active_minutes is always present (0 when no matching turns).
totals.calendar_minutes is present only when --calendar-start is provided.
meta.warnings carries advisories (e.g. when --branch/--purpose are passed but
no branches.jsonl sidecar is available, the script falls back to project+since
filtering and emits "no branch attribution data; counts may include off-branch
sessions").
USAGE
}

PROJECT=""
SINCE=""
IDLE_GAP_MIN="10"
CAL_START=""
CAL_END=""
BRANCH=""
PURPOSE=""
BRANCHES_SIDECAR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project)
      PROJECT="${2:-}"
      shift 2
      ;;
    --since)
      SINCE="${2:-}"
      shift 2
      ;;
    --idle-gap-minutes)
      IDLE_GAP_MIN="${2:-}"
      shift 2
      ;;
    --calendar-start)
      CAL_START="${2:-}"
      shift 2
      ;;
    --calendar-end)
      CAL_END="${2:-}"
      shift 2
      ;;
    --branch)
      BRANCH="${2:-}"
      shift 2
      ;;
    --purpose)
      PURPOSE="${2:-}"
      shift 2
      ;;
    --branches-sidecar)
      BRANCHES_SIDECAR="${2:-}"
      shift 2
      ;;
    --version)
      echo "pr-cost-stamp.sh ${VERSION}"
      exit 0
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "pr-cost-stamp.sh: unknown argument '$1'" >&2
      usage >&2
      exit 64
      ;;
  esac
done

if [[ -z "$PROJECT" || -z "$SINCE" ]]; then
  echo "pr-cost-stamp.sh: --project and --since are required" >&2
  usage >&2
  exit 64
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "pr-cost-stamp.sh: jq is required" >&2
  exit 69
fi

# Validate idle-gap-minutes is a non-negative integer.
if ! [[ "$IDLE_GAP_MIN" =~ ^[0-9]+$ ]]; then
  echo "pr-cost-stamp.sh: --idle-gap-minutes must be a non-negative integer (got '$IDLE_GAP_MIN')" >&2
  exit 64
fi
IDLE_GAP_SEC=$(( IDLE_GAP_MIN * 60 ))

# Normalize an ISO 8601 timestamp to canonical UTC form `YYYY-MM-DDTHH:MM:SSZ`.
# jq's fromdateiso8601 is strict ("%Y-%m-%dT%H:%M:%SZ" only) — it rejects both
# fractional seconds and explicit ±HH:MM offsets. We pre-process here so:
#   (a) the bash-level calendar computation succeeds on either form;
#   (b) string comparisons against JSONL `timestamp` (which Claude Code emits
#       as fractional-Z) stay coherent — the JSONL side is normalized inline
#       in the same jq filter.
normalize_iso() {
  jq -n --arg t "$1" -r '
    def to_epoch:
      . as $orig
      | sub("\\.[0-9]+(?=$|Z|[+-])"; "")
      | if test("[+-][0-9]{2}:[0-9]{2}$") then
          capture("^(?<dt>.+)(?<sign>[+-])(?<oh>[0-9]{2}):(?<om>[0-9]{2})$") as $m
          | (($m.dt + "Z") | fromdateiso8601)
            - (if $m.sign == "+" then 1 else -1 end)
              * (($m.oh | tonumber) * 3600 + ($m.om | tonumber) * 60)
        elif test("Z$") then
          fromdateiso8601
        else
          ((. + "Z") | fromdateiso8601)
        end;
    if $t == "" then "" else ($t | to_epoch | strftime("%Y-%m-%dT%H:%M:%SZ")) end
  ' 2>/dev/null || echo ""
}

# Resolve calendar window (jq does the parsing so we stay portable).
CALENDAR_MINUTES_JSON="null"
if [[ -n "$CAL_START" ]]; then
  if [[ -z "$CAL_END" ]]; then
    CAL_END=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  fi
  CAL_START=$(normalize_iso "$CAL_START")
  CAL_END=$(normalize_iso "$CAL_END")
  if [[ -z "$CAL_START" || -z "$CAL_END" ]]; then
    echo "pr-cost-stamp.sh: failed to normalize --calendar-start/--calendar-end" >&2
    CAL_START=""
    CAL_END=""
  else
    CALENDAR_MINUTES_JSON=$(jq -n --arg s "$CAL_START" --arg e "$CAL_END" '
      (($e | fromdateiso8601) - ($s | fromdateiso8601)) / 60 | floor
    ' 2>/dev/null || echo "null")
  fi
fi

CLAUDE_ROOT="${HOME}/.claude/projects"

# ── Build session_id → (branch, purpose) map from branches.jsonl sidecars ──
# When the consumer asks for --branch or --purpose, we need to know which
# session_id correspond to which branch/purpose. The pr-cost-attribution.sh
# hook records one entry per turn; here we collapse to per-session by taking
# the LAST entry for each session_id (so a session that ended on a given
# branch/purpose is classified that way). The hook is best-effort, so the
# absence of a sidecar entry for a given session is expected and handled
# downstream as "unattributed" (see WARNINGS below).
SESSION_ATTRS_JSON="{}"
WARNINGS_JSON="[]"

if [[ -n "$BRANCH" || -n "$PURPOSE" ]]; then
  if [[ -z "$BRANCHES_SIDECAR" ]]; then
    BRANCHES_SIDECAR="${CLAUDE_ROOT}/*/branches.jsonl"
  fi
  # Use shell glob to expand the pattern; tolerate misses.
  SIDECAR_FILES=()
  # shellcheck disable=SC2206
  shopt -s nullglob
  SIDECAR_FILES=( $BRANCHES_SIDECAR )
  shopt -u nullglob

  if [[ ${#SIDECAR_FILES[@]} -eq 0 ]]; then
    WARNINGS_JSON='["no branch attribution data; counts may include off-branch sessions"]'
  else
    # Concat all sidecars and reduce to map session_id → {branch, purpose, ts}
    # keeping the entry with the LATEST ts per session_id.
    SESSION_ATTRS_JSON=$(cat "${SIDECAR_FILES[@]}" 2>/dev/null | jq -s '
      [
        .[]
        | select(type == "object")
        | select((.session_id // "") != "")
      ]
      | group_by(.session_id)
      | map(
          sort_by(.ts // "") | last
          | { (.session_id): { branch: (.branch // ""), purpose: (.purpose // "") } }
        )
      | add // {}
    ' 2>/dev/null || echo "{}")
  fi
fi

# Empty-result emitter (no logs / no matches). Keeps schema stable so the kata
# always finds the keys it expects.
emit_empty() {
  local reason="$1"
  jq -n \
    --arg project "$PROJECT" \
    --arg since "$SINCE" \
    --arg version "$VERSION" \
    --arg cal_start "$CAL_START" \
    --arg cal_end "$CAL_END" \
    --arg idle_gap_min "$IDLE_GAP_MIN" \
    --arg branch "$BRANCH" \
    --arg purpose "$PURPOSE" \
    --argjson calendar_minutes "$CALENDAR_MINUTES_JSON" \
    --argjson warnings "$WARNINGS_JSON" \
    --arg reason "$reason" \
    '{
      totals: {
        sessions: 0,
        input_tokens: 0,
        output_tokens: 0,
        cache_read_tokens: 0,
        cache_creation_tokens: 0,
        cost_usd: null,
        active_minutes: 0,
        calendar_minutes: $calendar_minutes
      },
      breakdown: [],
      meta: {
        tool: "pr-cost-stamp.sh",
        version: $version,
        project: $project,
        since: $since,
        idle_gap_minutes: ($idle_gap_min | tonumber),
        calendar_start: (if $cal_start == "" then null else $cal_start end),
        calendar_end:   (if $cal_end   == "" then null else $cal_end   end),
        branch:  (if $branch  == "" then null else $branch  end),
        purpose: (if $purpose == "" then null else $purpose end),
        warnings: $warnings,
        cost_unavailable: true,
        reason: $reason
      }
    }'
}

if [[ ! -d "$CLAUDE_ROOT" ]]; then
  emit_empty "no claude code logs found"
  exit 0
fi

# Claude Code stores logs at ~/.claude/projects/<project-id>/<session>.jsonl.
# We narrow to directories whose name contains $PROJECT (basename match), which
# covers both the main checkout and worktrees of the same repo.
JSONL_FILE_LIST=$(find "$CLAUDE_ROOT" -maxdepth 2 -type f -name "*.jsonl" -path "*/*${PROJECT}*/*" 2>/dev/null)

if [[ -z "$JSONL_FILE_LIST" ]]; then
  emit_empty "no jsonl files in claude code projects directory"
  exit 0
fi

# Convert YYYYMMDD into ISO8601 boundary for string comparison against `timestamp`.
SINCE_ISO="${SINCE:0:4}-${SINCE:4:2}-${SINCE:6:2}T00:00:00.000Z"

# Single-pass aggregation: token totals, model breakdown, and active-time
# computed from per-turn timestamps within each sessionId.
#
# Token totals use the `--since` lower bound only (matches `ccusage --since`
# semantics). Active-time additionally honors `--calendar-start`/`--calendar-end`
# when provided, so that `active_minutes` is always bounded by the calendar
# window — otherwise the script could report `active > calendar`, which is
# nonsensical.
#
# Active-time model:
#   - Sort turns by timestamp within each sessionId.
#   - For each consecutive pair, contribute (delta) when delta <= idle_gap_sec,
#     else contribute 0. This is the canonical "active intervals" formulation.
#   - Floor each session that produced any turn at 60 seconds, so a single-turn
#     session does not register as zero work.
AGGREGATE=$(find "$CLAUDE_ROOT" -maxdepth 2 -type f -name "*.jsonl" -path "*/*${PROJECT}*/*" -exec cat {} + 2>/dev/null | \
  jq -s \
    --arg project "$PROJECT" \
    --arg since "$SINCE_ISO" \
    --arg cal_start "$CAL_START" \
    --arg cal_end "$CAL_END" \
    --arg branch "$BRANCH" \
    --arg purpose "$PURPOSE" \
    --argjson session_attrs "$SESSION_ATTRS_JSON" \
    --argjson gap "$IDLE_GAP_SEC" '
  [
    .[]
    | select(type == "object")
    | select((.cwd // "") | tostring | split("/") | last == $project)
    | select((.timestamp // "") >= $since)
    | select(.message.usage != null)
    | . as $row
    | ($session_attrs[($row.sessionId // "")] // null) as $attr
    # When --branch is requested, accept the turn only if its session_id maps
    # to that branch in the sidecar. Sessions with no sidecar entry are
    # excluded (matches the contract: "branch attribution requested → only
    # attributed turns count"). The legacy mode without --branch keeps all
    # sessions.
    | select(
        ($branch == "")
        or (($attr // {}) | (.branch // "") == $branch)
      )
    | select(
        ($purpose == "")
        or (($attr // {}) | (.purpose // "") == $purpose)
      )
    | {
        session: .sessionId,
        model: (.message.model // "unknown"),
        timestamp: (.timestamp // ""),
        input: (.message.usage.input_tokens // 0),
        output: (.message.usage.output_tokens // 0),
        cache_read: (.message.usage.cache_read_input_tokens // 0),
        cache_create: (.message.usage.cache_creation_input_tokens // 0)
      }
  ] as $turns
  | (
      # Normalize JSONL timestamps (which Claude Code emits with fractional
      # seconds, e.g. "2026-05-09T22:29:33.123Z") to the canonical no-fractional
      # form, so lexicographic comparisons against the already-normalized
      # calendar bounds are coherent.
      $turns
      | map(. + { ts_norm: (.timestamp | sub("\\.[0-9]+(?=$|Z|[+-])"; "")) })
      | if $cal_start != "" then map(select(.ts_norm >= $cal_start)) else . end
      | if $cal_end   != "" then map(select(.ts_norm <= $cal_end))   else . end
    ) as $time_turns
  | {
      totals: {
        sessions: ([$turns[].session] | unique | length),
        input_tokens: ([$turns[].input] | add // 0),
        output_tokens: ([$turns[].output] | add // 0),
        cache_read_tokens: ([$turns[].cache_read] | add // 0),
        cache_creation_tokens: ([$turns[].cache_create] | add // 0),
        cost_usd: null,
        active_minutes: (
          # Per-session active duration. JSONL timestamps follow the
          # Claude Code contract YYYY-MM-DDTHH:MM:SS.fffZ -- trailing Z
          # required, fractional part stripped before fromdateiso8601
          # (which is strict). If a future log format ever emits a non-Z
          # offset, the outer 2>/dev/null fallback would silently zero
          # everything; that risk is acceptable while the contract is
          # fixed.
          #
          # For each group, sum the deltas between consecutive turns when
          # the gap is <= idle_gap; gaps larger than idle_gap contribute 0
          # (real idle). The outer if . < 60 then 60 floors single-turn
          # sessions to one minute (range(1;1) is empty, so the inner sum
          # is 0 and the floor lifts it to 60s).
          $time_turns
          | group_by(.session)
          | map(
              sort_by(.timestamp)
              | [.[].timestamp | sub("\\.[0-9]+Z$"; "Z") | fromdateiso8601]
              | ([range(1; length) as $i | (.[$i] - .[$i-1])
                  | if . <= $gap then . else 0 end] | add // 0)
              | if . < 60 then 60 else . end
            )
          | add // 0
          | . / 60
          | floor
        )
      },
      breakdown: (
        $turns
        | group_by(.model)
        | map({
            model: .[0].model,
            input_tokens: ([.[].input] | add // 0),
            output_tokens: ([.[].output] | add // 0),
            cache_read_tokens: ([.[].cache_read] | add // 0),
            cache_creation_tokens: ([.[].cache_create] | add // 0)
          })
        | sort_by(-(.input_tokens + .output_tokens))
      )
    }
' 2>/dev/null || echo '{"totals":{"sessions":0,"input_tokens":0,"output_tokens":0,"cache_read_tokens":0,"cache_creation_tokens":0,"cost_usd":null,"active_minutes":0},"breakdown":[]}')

# Add calendar_minutes (from --calendar-start/--calendar-end) and meta block.
# `cost_unavailable` and `reason` describe a property of this script itself
# (it never computes USD cost), not a runtime fallback decision. The kata
# pairs this output with `ccusage`'s totalCost when ccusage is available;
# the reason text is intentionally neutral so downstream consumers do not
# infer "ccusage is missing" from this field.
echo "$AGGREGATE" | jq \
  --arg project "$PROJECT" \
  --arg since "$SINCE" \
  --arg version "$VERSION" \
  --arg cal_start "$CAL_START" \
  --arg cal_end "$CAL_END" \
  --arg idle_gap_min "$IDLE_GAP_MIN" \
  --arg branch "$BRANCH" \
  --arg purpose "$PURPOSE" \
  --argjson calendar_minutes "$CALENDAR_MINUTES_JSON" \
  --argjson warnings "$WARNINGS_JSON" \
  '. + {
    totals: (.totals + { calendar_minutes: $calendar_minutes }),
    meta: {
      tool: "pr-cost-stamp.sh",
      version: $version,
      project: $project,
      since: $since,
      idle_gap_minutes: ($idle_gap_min | tonumber),
      calendar_start: (if $cal_start == "" then null else $cal_start end),
      calendar_end:   (if $cal_end   == "" then null else $cal_end   end),
      branch:  (if $branch  == "" then null else $branch  end),
      purpose: (if $purpose == "" then null else $purpose end),
      warnings: $warnings,
      cost_unavailable: true,
      reason: "this script does not compute USD cost; pair with ccusage when available"
    }
  }'
