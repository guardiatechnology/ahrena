#!/usr/bin/env bash
# pr-cost-attribution.sh — Claude Code hook for branch + purpose attribution
#
# Purpose: write one JSON line to ~/.claude/projects/<hash>/branches.jsonl on
# every UserPromptSubmit (and best-effort on SessionStart), recording the git
# branch + cwd + session_id + purpose for the current turn. The companion
# pr-cost-stamp.sh consumes this sidecar to filter Claude Code turns to the
# branch that produced the PR — eliminating off-branch noise from the cost
# stamp.
#
# Wire-up: project-level .claude/settings.json — see scripts/install.py and
# codex-pr-cost-tracking.
#
# Cascade for `purpose` (first match wins, decided per turn):
#   1. $GUARDIA_PURPOSE  — literal value (e.g. dev, review, refactor, chore).
#   2. Heuristic on first line of `prompt` (canonical, frozen regex list):
#        ^/review\b                              — `/review` slash command
#        ^review[[:space:]]+pr\b                 — "review PR ..."
#        ^review[[:space:]]+#[0-9]+              — "review #N"
#        ^revise[[:space:]]+pr\b                 — "revise PR ..."
#        ^revise[[:space:]]+#[0-9]+              — "revise #N"
#        ^revisar[[:space:]]+pr\b                — pt-BR "revisar PR ..."
#        ^revisar[[:space:]]+#[0-9]+             — pt-BR "revisar #N"
#        ^revis(ã|a)o[[:space:]]+(de[[:space:]]+)?pr\b  — pt-BR "revisão de PR"
#        ^revisi(ó|o)n[[:space:]]+(de[[:space:]]+)?pr\b — es "revisión de PR"
#        pull[[:space:]]+request[[:space:]]+review      — anywhere on first line
#      Multi-byte UTF-8 characters use explicit alternation rather than
#      bracket classes — BSD grep on macOS does not handle UTF-8 inside [].
#      Match → purpose=review.
#   3. Default: purpose=dev.
#
# Contract: always exits 0; never blocks the turn. Failure modes (missing jq,
# missing git, unwritable sidecar) silently degrade — the hook is best-effort
# instrumentation, not a gate.

# Intentionally `set -u` only — we want best-effort completion, not -e.
set -u

# Read JSON payload from stdin. Claude Code passes session_id, transcript_path,
# cwd, hook_event_name, and (for UserPromptSubmit) prompt.
JSON_INPUT=""
if [[ -t 0 ]]; then
  # No stdin attached (e.g. manual invocation) — bail silently.
  exit 0
fi
JSON_INPUT=$(cat 2>/dev/null || echo "")

if [[ -z "$JSON_INPUT" ]]; then
  exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

EVENT_NAME=$(printf '%s' "$JSON_INPUT" | jq -r '.hook_event_name // ""' 2>/dev/null || echo "")
SESSION_ID=$(printf '%s' "$JSON_INPUT" | jq -r '.session_id // ""' 2>/dev/null || echo "")
PROMPT=$(printf '%s' "$JSON_INPUT" | jq -r '.prompt // ""' 2>/dev/null || echo "")
CWD=$(printf '%s' "$JSON_INPUT" | jq -r '.cwd // ""' 2>/dev/null || echo "")
TRANSCRIPT_PATH=$(printf '%s' "$JSON_INPUT" | jq -r '.transcript_path // ""' 2>/dev/null || echo "")

# Fallback for cwd: use $PWD when payload omits it.
if [[ -z "$CWD" ]]; then
  CWD="${PWD:-}"
fi

# Resolve git branch from cwd (best-effort).
BRANCH=""
if [[ -n "$CWD" && -d "$CWD" ]] && command -v git >/dev/null 2>&1; then
  BRANCH=$(git -C "$CWD" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
fi

# Resolve repo nameWithOwner (best-effort) from origin remote.
REPO=""
if [[ -n "$CWD" && -d "$CWD" ]] && command -v git >/dev/null 2>&1; then
  REMOTE_URL=$(git -C "$CWD" remote get-url origin 2>/dev/null || echo "")
  if [[ -n "$REMOTE_URL" ]]; then
    # Match git@host:owner/repo(.git) or https://host/owner/repo(.git)
    REPO=$(printf '%s' "$REMOTE_URL" | sed -E 's#^.*[:/]([^/:[:space:]]+/[^/[:space:]]+)$#\1#; s#\.git$##' | head -n 1)
  fi
fi

# Cascade for purpose: env var → prompt heuristic → default.
PURPOSE=""
if [[ -n "${GUARDIA_PURPOSE:-}" ]]; then
  PURPOSE="$GUARDIA_PURPOSE"
elif [[ -n "$PROMPT" ]]; then
  FIRST_LINE=$(printf '%s' "$PROMPT" | head -n 1 | sed -E 's/^[[:space:]]+//')
  # Frozen heuristic regex list — additions go through ADR.
  # Use `command grep` so the binary is invoked even if a shell function
  # named `grep` is in scope (some interactive shells alias to ripgrep/ugrep).
  if printf '%s' "$FIRST_LINE" | command grep -qiE '^/review\b|^review[[:space:]]+pr\b|^review[[:space:]]+#[0-9]+|^revise[[:space:]]+pr\b|^revise[[:space:]]+#[0-9]+|^revisar[[:space:]]+pr\b|^revisar[[:space:]]+#[0-9]+|^revis(ã|a)o[[:space:]]+(de[[:space:]]+)?pr\b|^revisi(ó|o)n[[:space:]]+(de[[:space:]]+)?pr\b|pull[[:space:]]+request[[:space:]]+review'; then
    PURPOSE="review"
  fi
fi
PURPOSE="${PURPOSE:-dev}"

# Resolve sidecar directory. Prefer the transcript directory (matches Claude Code's
# per-project hash dir), fallback to ~/.claude/projects/_unknown.
SIDECAR_DIR=""
if [[ -n "$TRANSCRIPT_PATH" ]]; then
  SIDECAR_DIR=$(dirname "$TRANSCRIPT_PATH" 2>/dev/null || echo "")
fi
if [[ -z "$SIDECAR_DIR" || ! -d "$SIDECAR_DIR" ]]; then
  SIDECAR_DIR="${HOME:-/tmp}/.claude/projects/_unknown"
  mkdir -p "$SIDECAR_DIR" 2>/dev/null || exit 0
fi
SIDECAR_FILE="${SIDECAR_DIR}/branches.jsonl"

# Build the JSON line via jq for proper escaping.
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "")
LINE=$(jq -n -c \
  --arg ts "$TS" \
  --arg session_id "$SESSION_ID" \
  --arg event "$EVENT_NAME" \
  --arg repo "$REPO" \
  --arg branch "$BRANCH" \
  --arg cwd "$CWD" \
  --arg purpose "$PURPOSE" \
  '{ts: $ts, session_id: $session_id, event: $event, repo: $repo, branch: $branch, cwd: $cwd, purpose: $purpose}' 2>/dev/null || echo "")

if [[ -z "$LINE" ]]; then
  exit 0
fi

# Atomic append — POSIX guarantees PIPE_BUF (≥ 512 bytes) atomicity for small
# writes. Each line is well below that threshold.
printf '%s\n' "$LINE" >> "$SIDECAR_FILE" 2>/dev/null || true

exit 0
