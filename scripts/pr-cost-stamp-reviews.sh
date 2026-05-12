#!/usr/bin/env bash
# pr-cost-stamp-reviews.sh — Aggregator for PR review activity by author.
#
# Queries `gh pr view --json reviews,comments` for the target PR, classifies
# authors as AI bot vs. human via:
#   1. GitHub User type == "Bot" (authoritative).
#   2. Login matches a configured allow-list (--known-ai-reviewers, comma-sep).
#
# Counts FORMAL REVIEWS only (per the plan's risk note: "PRs grandes com muitos
# comentários ruidosos inflam contagem"; comments are out of scope by default).
# Pass --include-comments to additionally tally comment authors.
#
# Output: JSON on stdout with shape:
#   {
#     "ai_reviewers":    [ {login, count, first_at, last_at}, ... ],
#     "human_reviewers": [ {login, count, first_at, last_at}, ... ],
#     "meta": { tool, version, repo, pr, include_comments, generated_at }
#   }
#
# Requires: gh (authenticated), jq.

set -euo pipefail

VERSION="1.0.0"

usage() {
  cat <<USAGE
pr-cost-stamp-reviews.sh — Classify PR reviewers as AI vs. human

Usage:
  pr-cost-stamp-reviews.sh --repo <owner/name> --pr <number> [options]
  pr-cost-stamp-reviews.sh --version

Required:
  --repo <owner/name>            GitHub repository
  --pr <number>                  Pull request number

Optional:
  --known-ai-reviewers <csv>     Extra login allow-list (comma-separated).
                                 Built-ins always recognized as AI:
                                   gemini-code-assist[bot], claude[bot],
                                   coderabbitai[bot], qodo-merge-pro[bot],
                                   ahrena-warrior-argos[bot]
  --include-comments             Also tally comment authors. Default: reviews only.
  --version                      Print version and exit
  -h, --help                     Print this help and exit
USAGE
}

REPO=""
PR=""
KNOWN_AI=""
INCLUDE_COMMENTS=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO="${2:-}"
      shift 2
      ;;
    --pr)
      PR="${2:-}"
      shift 2
      ;;
    --known-ai-reviewers)
      KNOWN_AI="${2:-}"
      shift 2
      ;;
    --include-comments)
      INCLUDE_COMMENTS=1
      shift
      ;;
    --version)
      echo "pr-cost-stamp-reviews.sh ${VERSION}"
      exit 0
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "pr-cost-stamp-reviews.sh: unknown argument '$1'" >&2
      usage >&2
      exit 64
      ;;
  esac
done

if [[ -z "$REPO" || -z "$PR" ]]; then
  echo "pr-cost-stamp-reviews.sh: --repo and --pr are required" >&2
  usage >&2
  exit 64
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "pr-cost-stamp-reviews.sh: jq is required" >&2
  exit 69
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "pr-cost-stamp-reviews.sh: gh CLI is required" >&2
  exit 69
fi

# Built-in AI reviewer logins. Project-level overrides come via --known-ai-reviewers
# (typically populated from pr_cost_tracking.known_ai_reviewers in .directives).
BUILTIN_AI='[
  "gemini-code-assist[bot]",
  "claude[bot]",
  "coderabbitai[bot]",
  "qodo-merge-pro[bot]",
  "ahrena-warrior-argos[bot]"
]'

# Convert --known-ai-reviewers CSV to JSON array.
EXTRA_AI_JSON="[]"
if [[ -n "$KNOWN_AI" ]]; then
  EXTRA_AI_JSON=$(printf '%s' "$KNOWN_AI" | jq -R -c 'split(",") | map(. | gsub("^[[:space:]]+|[[:space:]]+$"; ""))' 2>/dev/null || echo "[]")
fi

# Fetch reviews + comments via gh REST API. The GitHub API paginates these
# endpoints (default 30 items per page); use `--paginate` and merge the
# resulting page array via `jq -s 'add // []'` so PRs with many reviews/comments
# are aggregated correctly. The trailing `|| echo "[]"` plus the `// []`
# default keep the JSON shape stable when the call fails or returns nothing.
REVIEW_JSON=$(gh api --paginate "/repos/${REPO}/pulls/${PR}/reviews" 2>/dev/null | jq -s 'add // []' 2>/dev/null || echo "[]")
COMMENT_JSON="[]"
if [[ "$INCLUDE_COMMENTS" -eq 1 ]]; then
  # Both inline review-comments and issue-level comments contribute.
  INLINE=$(gh api --paginate "/repos/${REPO}/pulls/${PR}/comments" 2>/dev/null | jq -s 'add // []' 2>/dev/null || echo "[]")
  ISSUE=$(gh api --paginate "/repos/${REPO}/issues/${PR}/comments" 2>/dev/null | jq -s 'add // []' 2>/dev/null || echo "[]")
  COMMENT_JSON=$(jq -n --argjson a "$INLINE" --argjson b "$ISSUE" '$a + $b')
fi

# Aggregate. Each item is normalized to { login, type, ts }.
GENERATED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)

jq -n \
  --argjson reviews "$REVIEW_JSON" \
  --argjson comments "$COMMENT_JSON" \
  --argjson builtin_ai "$BUILTIN_AI" \
  --argjson extra_ai "$EXTRA_AI_JSON" \
  --arg repo "$REPO" \
  --arg pr "$PR" \
  --arg include_comments "$INCLUDE_COMMENTS" \
  --arg version "$VERSION" \
  --arg generated_at "$GENERATED_AT" '
  ($builtin_ai + $extra_ai) as $ai_set
  | (
      ([$reviews[]?     | { login: (.user.login // ""), type: (.user.type // "User"), ts: (.submitted_at // .submittedAt // "") }])
      + ([$comments[]?  | { login: (.user.login // ""), type: (.user.type // "User"), ts: (.created_at  // .createdAt  // "") }])
    ) as $entries
  | [$entries[] | select(.login != "")]
  | group_by(.login)
  | map({
      login: .[0].login,
      type:  .[0].type,
      count: length,
      first_at: (map(.ts) | min),
      last_at:  (map(.ts) | max)
    })
  | map(. + { is_ai: ((.type == "Bot") or ([.login] | inside($ai_set))) })
  | {
      ai_reviewers:    (map(select(.is_ai))    | map(del(.is_ai, .type))),
      human_reviewers: (map(select(.is_ai | not)) | map(del(.is_ai, .type))),
      meta: {
        tool: "pr-cost-stamp-reviews.sh",
        version: $version,
        repo: $repo,
        pr: ($pr | tonumber),
        include_comments: ($include_comments == "1"),
        generated_at: $generated_at
      }
    }
  '
