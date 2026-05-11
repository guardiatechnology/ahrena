#!/usr/bin/env bash
# bootstrap_status_labels.sh — idempotent creation of the 7 canonical
# status:* labels per lex-issue-status.
#
# Usage:
#   scripts/bootstrap_status_labels.sh                  # current repo (gh-detected)
#   scripts/bootstrap_status_labels.sh owner/repo       # explicit target
#
# Requires: gh CLI authenticated with write access to the repo.
# Re-runs are safe: existing labels are updated (idempotent via gh label create --force).

set -euo pipefail

REPO="${1:-}"
GH_ARGS=()
if [[ -n "$REPO" ]]; then
  GH_ARGS+=(--repo "$REPO")
fi

# Label tuples: name | color (hex, no #) | description
# Colors mirror lex-issue-status §1 "Conjunto canônico de 7 labels".
LABELS=(
  "status: todo|cccccc|Plan created, Issue opened, branch linked, worktree ready (lex-agent-planning todo)"
  "status: development|83d2ff|Implementation in progress — Athena Phase 4 (lex-agent-planning development)"
  "status: to review|fff3a3|PR opened, waiting for reviewer to pick up (lex-agent-planning to review)"
  "status: review|fbca04|Argos or human actively reviewing (lex-agent-planning review)"
  "status: to release|ffb178|Review approved, waiting for release to start (lex-agent-planning to release)"
  "status: release|e07400|Release in execution — Janus running tag/build/deploy (lex-agent-planning release)"
  "status: done|0e8a16|Release completed, PR merged, cycle closed (lex-agent-planning done)"
)

echo "Bootstrapping canonical status:* labels (lex-issue-status)..."
if [[ ${#GH_ARGS[@]} -gt 0 ]]; then
  echo "Target: $REPO"
else
  echo "Target: current repo (gh-detected)"
fi
echo

for tuple in "${LABELS[@]}"; do
  IFS='|' read -r NAME COLOR DESC <<<"$tuple"
  # --force makes the call idempotent: creates or updates color/description.
  if gh label create "$NAME" --color "$COLOR" --description "$DESC" --force "${GH_ARGS[@]}" >/dev/null 2>&1; then
    echo "  ✅ $NAME (#$COLOR)"
  else
    echo "  ❌ failed to create/update: $NAME" >&2
    exit 1
  fi
done

echo
echo "Done. 7 canonical status:* labels are present and idempotent."
echo
echo "Next: enforce mutex on transitions per lex-issue-status §2."
echo "      Eunomia applies status: todo on Issue creation;"
echo "      Athena/Argos/Janus transition per the owners table in"
echo "      lex-agent-planning."
