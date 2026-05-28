#!/usr/bin/env bash
# session-tags-auto-suggest.sh — Claude Code hook for session tag auto-suggestion
#
# Purpose: on every UserPromptSubmit, detect "session has no tags yet" and
# inject a one-shot `<system-reminder>` instructing Claude to derive + write
# the tags per `lex-session-tags`, then emit the visibility note. Subsequent
# prompts in the same session are no-ops because the heartbeat now carries a
# `tags` object.
#
# Wire-up: project-level .claude/settings.json hooks.UserPromptSubmit[] — see
# scripts/install.py and codex-session-tracking §9.
#
# Gates (silent exit-0 on any miss):
#   1. jq + python3 + PyYAML available                              → else skip
#   2. .ahrena/.directives present                                  → else skip
#   3. session_tracking.enabled == true                             → else skip
#   4. session_tracking.tags.enabled == true                        → else skip
#   5. session_tracking.tags.auto_suggest == true                   → else skip
#   6. $session_id resolvable (from stdin payload or environment)   → else skip
#   7. heartbeat file exists at $heartbeat_dir/$id.json             → else skip
#      (per Plan B Q2 default — does NOT bootstrap heartbeat)
#   8. heartbeat .tags is null/missing/empty                        → else skip
#
# Contract: always exits 0; never blocks the turn. Emits the system-reminder
# block on stdout exactly once per session (next prompt finds .tags populated
# and skips at gate 8).

set -u

# No stdin attached (e.g. manual invocation) → bail silently.
if [[ -t 0 ]]; then
  exit 0
fi

JSON_INPUT=$(cat 2>/dev/null || echo "")
if [[ -z "$JSON_INPUT" ]]; then
  exit 0
fi

# Gate 1: required binaries.
if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi
if ! command -v python3 >/dev/null 2>&1; then
  exit 0
fi

# Resolve session_id from payload, fall back to env var.
SESSION_ID=$(printf '%s' "$JSON_INPUT" | jq -r '.session_id // ""' 2>/dev/null || echo "")
if [[ -z "$SESSION_ID" ]]; then
  SESSION_ID="${CLAUDE_CODE_SESSION_ID:-}"
fi
if [[ -z "$SESSION_ID" ]]; then
  # Gate 6 miss.
  exit 0
fi

# Resolve project root via CWD from payload (fallback $PWD).
CWD=$(printf '%s' "$JSON_INPUT" | jq -r '.cwd // ""' 2>/dev/null || echo "")
if [[ -z "$CWD" ]]; then
  CWD="${PWD:-}"
fi
if [[ -z "$CWD" || ! -d "$CWD" ]]; then
  exit 0
fi

DIRECTIVES="$CWD/.ahrena/.directives"
if [[ ! -f "$DIRECTIVES" ]]; then
  # Gate 2 miss.
  exit 0
fi

# Parse .directives via Python+YAML. Python 3 is already a hard dependency of
# the framework (install.py, update.py, validate.py), and PyYAML is universal
# in this codebase. Failure modes (missing PyYAML, malformed file) silently
# degrade to exit 0 — the hook is best-effort instrumentation.
CONFIG=$(python3 - "$DIRECTIVES" <<'PY' 2>/dev/null || echo ""
import json
import sys

try:
    import yaml
except ImportError:
    sys.exit(0)

try:
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
except Exception:
    sys.exit(0)

st = cfg.get("session_tracking") or {}
# Gate 3: session_tracking.enabled (default true when section exists).
if st.get("enabled", True) is not True:
    sys.exit(0)

tags = st.get("tags") or {}
# Gate 4 + 5: tags.enabled and tags.auto_suggest (default true).
if tags.get("enabled", True) is not True:
    sys.exit(0)
if tags.get("auto_suggest", True) is not True:
    sys.exit(0)

print(json.dumps({
    "kinds": tags.get("kinds") or [],
    "heartbeat_dir": st.get("heartbeat_dir") or ".ahrena/workflow/sessions",
}))
PY
)

if [[ -z "$CONFIG" ]]; then
  exit 0
fi

HEARTBEAT_DIR=$(printf '%s' "$CONFIG" | jq -r '.heartbeat_dir' 2>/dev/null || echo "")
if [[ -z "$HEARTBEAT_DIR" ]]; then
  exit 0
fi
HEARTBEAT_FILE="$CWD/$HEARTBEAT_DIR/${SESSION_ID}.json"

# Gate 7: heartbeat file exists. Per Plan B Q2 default the hook does not
# bootstrap; Eunomia/Athena create the heartbeat on first plan transition.
if [[ ! -f "$HEARTBEAT_FILE" ]]; then
  exit 0
fi

# Gate 8: heartbeat .tags is null/missing/empty.
HAS_TAGS=$(jq -r '(.tags // null) | if . == null or . == {} then "no" else "yes" end' "$HEARTBEAT_FILE" 2>/dev/null || echo "yes")
if [[ "$HAS_TAGS" != "no" ]]; then
  exit 0
fi

# All gates passed — emit the one-shot system-reminder. Include the configured
# kinds vocabulary so the agent sees the same list the user configured.
KINDS_LIST=$(printf '%s' "$CONFIG" | jq -r '.kinds | join(", ")' 2>/dev/null || echo "")
KINDS_LIST="${KINDS_LIST:-tech-task, bug, spike, user-story, epic, chore, design, review, exploration, release}"

cat <<REMINDER
<system-reminder>
Session auto-suggest (per lex-session-tags rule 5): this Claude Code session has no tags yet. Before responding to the user's prompt, do the following — silently, in one pass — and append the visibility note at the end of your response:

1. Derive a tags object per kata-session-tag-suggest:
   - Pick \`kind\` (1st slot) from the configured vocabulary: ${KINDS_LIST}.
   - Pick up to 2 free-form \`topics\` (lowercase, kebab-case, ≤ 20 chars each) from the user's prompt + active plan front-matter (\`.claude/plans/plan-*.md\` if any) + current branch name.
2. Write the tags into the session heartbeat by running:
   \`kata-session-heartbeat --set-tags <kind> [topic1] [topic2]\`
   (Or invoke the kata programmatically with \`tags='{"kind":"<kind>","topics":["<t1>","<t2>"]}'\`.)
3. End your response with the one-line visibility note:
   \`tagged: [<kind>] [<topic1>] [<topic2>]\`

Skip steps 1-3 only if the user explicitly says they do not want tags on this session. Do not invent a \`kind\` outside the configured vocabulary. This reminder fires exactly once per session — once the heartbeat has \`tags\`, the hook is a no-op.
</system-reminder>
REMINDER

exit 0
