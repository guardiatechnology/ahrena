#!/usr/bin/env bash
# bootstrap_labels.sh — idempotent seed of the full framework label catalog.
#
# Seeds every label the framework expects to exist in a consumer repository:
#   - 7 workflow status labels (lex-issue-status)
#   - 10 type labels (feature request, epic, user story, bug report, plan, etc.)
#   - 14 cross-cutting and lifecycle labels (security, breaking change, blocked, ...)
#   - 5 platform / tool labels (api, frontend, codex, copilot, cursor)
#   - 6 size labels (size/XS ... size/XXL)
#
# Usage:
#   scripts/bootstrap_labels.sh                  # current repo (gh-detected)
#   scripts/bootstrap_labels.sh owner/repo       # explicit target
#
# Requirements:
#   - gh CLI installed and on PATH
#   - gh CLI authenticated with write access to the target repository
#
# Behavior:
#   - Idempotent: uses `gh label create --force` so re-runs update color and
#     description without failing on existing labels.
#   - Graceful: if gh is missing or unauthenticated, prints a clear warning
#     with the manual command and exits 0 so it never aborts an install.
#   - Per-label failures (e.g., color conflict, transient error) are reported
#     but do not stop the run; a summary is printed at the end.

set -uo pipefail

REPO="${1:-}"
GH_ARGS=()
if [[ -n "$REPO" ]]; then
  GH_ARGS+=(--repo "$REPO")
fi

# --- Preflight: gh availability and auth --------------------------------------

if ! command -v gh >/dev/null 2>&1; then
  cat >&2 <<'EOF'
warning: gh CLI not found on PATH — skipping label bootstrap.

Install the GitHub CLI (https://cli.github.com/) and re-run:
  bash .ahrena/bootstrap_labels.sh
EOF
  exit 0
fi

if ! gh auth status >/dev/null 2>&1; then
  cat >&2 <<'EOF'
warning: gh CLI is not authenticated — skipping label bootstrap.

Authenticate with:
  gh auth login
Then re-run:
  bash .ahrena/bootstrap_labels.sh
EOF
  exit 0
fi

# --- Canonical label catalog --------------------------------------------------
# Format: name|color (hex, no #)|description
# Source of truth: the live label catalog of the framework upstream repository.

LABELS=(
  # Workflow status labels (lex-issue-status — 7 canonical states)
  "status: todo|cccccc|Plan created, Issue opened, branch linked, worktree ready (lex-agent-planning todo)"
  "status: development|83d2ff|Implementation in progress — Athena Phase 4 (lex-agent-planning development)"
  "status: to review|fff3a3|PR opened, waiting for reviewer to pick up (lex-agent-planning to review)"
  "status: review|fbca04|Argos or human actively reviewing (lex-agent-planning review)"
  "status: to release|ffb178|Review approved, waiting for release to start (lex-agent-planning to release)"
  "status: release|e07400|Release in execution — Janus running tag/build/deploy (lex-agent-planning release)"
  "status: done|0e8a16|Release completed, PR merged, cycle closed (lex-agent-planning done)"

  # Issue Type labels (required by lex-issue-quality Rule 2)
  "feature request ➕|5319E7|Issue about a new feature request"
  "feature ➕|7828E5|New features added. Use only after approve feature request"
  "epic|5319E7|Large initiative grouping multiple stories or features"
  "user story 🎯|6A42EB|A new user story"
  "bug report 🐞|fc2803|Report a new bug"
  "plan 📋|7c4dff|Sub-issue: executable unit under a parent Issue (User Story / Bug / Tech Task)"
  "evolvability ♻️|008672|Issue or PR launched to ensure the project's evolvability. Aka refactoring, clean code, etc."
  "documentation 📃|0075ca|Issue or PR releated to improvements or additions to documentation"
  "ci 🏗️|ff7a0e|Issue or PR releated to Continuous Integration (CI) pipeline enhancements"
  "enhancement 🔝|D5BBED|Issue or PR releated to a enhancement to an existing feature"

  # Cross-cutting / lifecycle / state labels
  "bugfix 🔧|fc4e03|Issue or PR related to something isn't working"
  "compliance 📜|ae6b09|Issue or PR releated to enhancement to be compliant with something"
  "security 🛡️|D93F0B|This PR resolves some security issue"
  "vulnerability 🚨|B60205|Vulnerability detected"
  "breaking change 💥|925845|Issue or PR adding a breaking change. Major version bump required"
  "release ↗️|81A5DC|To be set only on release PR"
  "deprecate 🪦|5f6a70|Issue to deprecate some existing feature"
  "blocked 🚧|e99695|Issue or PR have some block to advance"
  "hold|fbca04|Paused / not actively pursued"
  "question ✋|d876e3|Further information is requested"
  "rejected ❌|b52816|Issue or pull request rejected"
  "wontfix 🤷‍♀️|ffffff|This issue will not be worked on"
  "duplicate !!|cfd3d7|This issue or pull request already exists"
  "good first issue 🧠|CA3AC2|Issue good for newcomers"

  # Platform / scope labels
  "api|0075ca|Issue or PR related to API design or implementation"
  "frontend|D5BBED|Issue or PR related to frontend (UI/UX) implementation"

  # Tool-assigned labels (auto-applied by integrations)
  "codex ✨|111112|PR opened by Codex"
  "copilot ✨|111112|PR opened by Copilot"
  "cursor ✨|111112|PR opened by Cursor"

  # PR size labels (auto-applied by GitHub Actions)
  "size/XS|9b770a|This PR changes 0-9 lines, ignoring generated files. Setted automatically"
  "size/S|e1b207|This PR changes 10-29 lines, ignoring generated files. Setted automatically"
  "size/M|f3c511|This PR changes 30-99 lines, ignoring generated files. Setted automatically"
  "size/L|ffdb4d|This PR changes 100-499 lines, ignoring generated files. Setted automatically"
  "size/XL|cb9e0a|This PR changes 500-999 lines, ignoring generated files. Setted automatically"
  "size/XXL|7a6600|This PR changes over 1,000 lines, ignoring the generated files. Setted automatically"
)

# --- Apply --------------------------------------------------------------------

echo "Bootstrapping framework labels..."
if [[ ${#GH_ARGS[@]} -gt 0 ]]; then
  echo "Target: $REPO"
else
  echo "Target: current repo (gh-detected)"
fi
echo

success=0
failed=0
failed_names=()

for tuple in "${LABELS[@]}"; do
  IFS='|' read -r NAME COLOR DESC <<<"$tuple"
  # --force creates or updates; idempotent across re-runs.
  if gh label create "$NAME" --color "$COLOR" --description "$DESC" --force "${GH_ARGS[@]}" >/dev/null 2>&1; then
    echo "  ok    $NAME (#$COLOR)"
    success=$((success + 1))
  else
    echo "  fail  $NAME (#$COLOR)" >&2
    failed=$((failed + 1))
    failed_names+=("$NAME")
  fi
done

total=${#LABELS[@]}
echo
echo "Summary: $success of $total labels created/updated."
if [[ $failed -gt 0 ]]; then
  echo "Failed labels:" >&2
  for name in "${failed_names[@]}"; do
    echo "  - $name" >&2
  done
  echo
  echo "warning: some labels failed to create. Inspect with: gh label list" >&2
  # Do not exit non-zero — keep install/update flows from aborting.
fi
