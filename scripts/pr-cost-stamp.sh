#!/usr/bin/env bash
# pr-cost-stamp.sh — Fallback for kata-pr-cost-stamp when ccusage is unavailable.
#
# Parses Claude Code JSONL logs in ~/.claude/projects/<hash>/*.jsonl, filters by
# project basename and date, and emits a JSON aggregate compatible with the schema
# the kata expects (totals + breakdown + meta).
#
# Cost estimation is intentionally OUT OF SCOPE for this fallback to honor
# `lex-` no-hardcode-pricing principle. Output declares meta.cost_unavailable=true,
# and the kata renders cost as "N/A (fallback mode — install Node.js for ccusage)".
#
# Requires: bash 3.2+, jq, find, date.

set -euo pipefail

VERSION="1.0.0"

usage() {
  cat <<USAGE
pr-cost-stamp.sh — Fallback aggregator for Claude Code JSONL logs

Usage:
  pr-cost-stamp.sh --project <name> --since <YYYYMMDD>
  pr-cost-stamp.sh --version

Options:
  --project <name>   Project basename to filter (matches cwd basename in JSONL)
  --since <date>     YYYYMMDD lower bound (inclusive) for line timestamp
  --version          Print version and exit
  -h, --help         Print this help and exit

Output: JSON on stdout with keys totals, breakdown, meta.
USAGE
}

PROJECT=""
SINCE=""

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
  echo "pr-cost-stamp.sh: jq is required for the fallback path" >&2
  exit 69
fi

CLAUDE_ROOT="${HOME}/.claude/projects"
if [[ ! -d "$CLAUDE_ROOT" ]]; then
  # No logs at all — emit empty aggregate so the kata can still render the block.
  jq -n \
    --arg project "$PROJECT" \
    --arg since "$SINCE" \
    --arg version "$VERSION" \
    '{
      totals: {
        sessions: 0,
        input_tokens: 0,
        output_tokens: 0,
        cache_read_tokens: 0,
        cache_creation_tokens: 0,
        cost_usd: null
      },
      breakdown: [],
      meta: {
        tool: "pr-cost-stamp.sh",
        version: $version,
        project: $project,
        since: $since,
        cost_unavailable: true,
        reason: "no claude code logs found"
      }
    }'
  exit 0
fi

# Convert YYYYMMDD into ISO8601 boundary for string comparison against `timestamp`.
SINCE_ISO="${SINCE:0:4}-${SINCE:4:2}-${SINCE:6:2}T00:00:00.000Z"

# Build aggregation across matching JSONL files.
# `cwd` field in each line is the absolute project path; we match its basename.
# Optimization: Claude Code stores logs at `~/.claude/projects/<project-id>/<session>.jsonl`,
# so we limit depth to 2 and scope to directories whose name contains $PROJECT (the basename).
# A worktree directory under the same repo carries the project name in its hash directory too,
# so this scope covers both the main checkout and worktrees.
# Portable file collection (no `mapfile` — bash 3.2 on macOS lacks it).
JSONL_FILE_LIST=$(find "$CLAUDE_ROOT" -maxdepth 2 -type f -name "*.jsonl" -path "*/*${PROJECT}*/*" 2>/dev/null)

if [[ -z "$JSONL_FILE_LIST" ]]; then
  jq -n \
    --arg project "$PROJECT" \
    --arg since "$SINCE" \
    --arg version "$VERSION" \
    '{
      totals: {
        sessions: 0,
        input_tokens: 0,
        output_tokens: 0,
        cache_read_tokens: 0,
        cache_creation_tokens: 0,
        cost_usd: null
      },
      breakdown: [],
      meta: {
        tool: "pr-cost-stamp.sh",
        version: $version,
        project: $project,
        since: $since,
        cost_unavailable: true,
        reason: "no jsonl files in claude code projects directory"
      }
    }'
  exit 0
fi

# Aggregate using a single jq invocation that consumes all JSONL files
# concatenated through stdin (`find ... -exec cat`). `jq -s` slurps the
# resulting stream into an array.
# Each line either has shape {sessionId, cwd, timestamp, message:{usage:{...}, model}}
# or is a non-message event we skip.
AGGREGATE=$(find "$CLAUDE_ROOT" -maxdepth 2 -type f -name "*.jsonl" -path "*/*${PROJECT}*/*" -exec cat {} + 2>/dev/null | \
  jq -s --arg project "$PROJECT" --arg since "$SINCE_ISO" '
  [
    .[]
    | select(type == "object")
    | select((.cwd // "") | tostring | split("/") | last == $project)
    | select((.timestamp // "") >= $since)
    | select(.message.usage != null)
    | {
        session: .sessionId,
        model: (.message.model // "unknown"),
        input: (.message.usage.input_tokens // 0),
        output: (.message.usage.output_tokens // 0),
        cache_read: (.message.usage.cache_read_input_tokens // 0),
        cache_create: (.message.usage.cache_creation_input_tokens // 0)
      }
  ]
  | {
      totals: {
        sessions: ([.[].session] | unique | length),
        input_tokens: ([.[].input] | add // 0),
        output_tokens: ([.[].output] | add // 0),
        cache_read_tokens: ([.[].cache_read] | add // 0),
        cache_creation_tokens: ([.[].cache_create] | add // 0),
        cost_usd: null
      },
      breakdown: (
        group_by(.model)
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
' 2>/dev/null || echo '{"totals":{"sessions":0,"input_tokens":0,"output_tokens":0,"cache_read_tokens":0,"cache_creation_tokens":0,"cost_usd":null},"breakdown":[]}')

# Add meta block.
echo "$AGGREGATE" | jq \
  --arg project "$PROJECT" \
  --arg since "$SINCE" \
  --arg version "$VERSION" \
  '. + {
    meta: {
      tool: "pr-cost-stamp.sh",
      version: $version,
      project: $project,
      since: $since,
      cost_unavailable: true,
      reason: "fallback mode does not compute USD cost; install Node.js to use ccusage"
    }
  }'
