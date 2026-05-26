#!/usr/bin/env bash
# ahrena-api-commit.sh — create a commit via the GitHub Git Data API.
#
# Builds a server-signed commit using the App installation token exported by
# scripts/ahrena-auth.sh (GH_TOKEN_AHRENA_BOT) and updates the branch ref to
# the new commit SHA. Designed to be invoked by `kata-commit` when the
# directive `bot_author.enabled=true` AND the calling warrior is in
# `bot_author.apply_to`. Soft-fails (returns non-zero) on any API/network
# error so the kata can fall back to local `git commit`.
#
# Sequence (each step uses curl + jq, auth via $GH_TOKEN_AHRENA_BOT):
#   1. Resolve repo + parent commit SHA (HEAD of the current branch on origin).
#   2. For each staged file (`git diff --cached --name-only`):
#      - For modifications/additions: read the staged content from the index
#        (`git show :path` for regular text, base64 for binary), POST a blob,
#        capture the blob SHA.
#      - For deletions: emit a tree entry with `sha: null` (no blob).
#   3. POST a new tree based on the parent commit's tree (`base_tree`).
#   4. POST a new commit (tree + parents). The App installation token signs it.
#   5. PATCH refs/heads/<branch> to point at the new commit.
#   6. `git fetch origin <branch>` + `git reset --hard origin/<branch>` so the
#      local working tree mirrors the server-side commit.
#
# Inputs:
#   --branch <name>      target branch (required)
#   --message <text>     commit message; supports multi-line (required)
#   --repo <owner/repo>  optional; auto-resolved from `git remote get-url origin`
#   --co-author "Name <email>"  optional Co-authored-by trailer
#
# Token handling:
#   - GH_TOKEN_AHRENA_BOT is consumed from the environment (exported by
#     ahrena-auth.sh). NEVER logged, NEVER printed to stdout/stderr, NEVER
#     interpolated into error messages.
#   - When the script is invoked with `set -x` (debug), the curl invocations
#     are wrapped in `set +x` / `set -x` so the bearer header does not leak.
#
# Exit codes:
#   0    success
#   1    invalid usage (missing required arg)
#   2    network/API failure (calling kata falls back to local commit)
#   3    git working-tree sync failed post-commit (commit landed on server
#        but `git reset --hard` did not; user must fetch/reset manually)
#
# Issue #275 (Plan P2). Pairs with scripts/ahrena-auth.sh (Plan P1).

set -uo pipefail
# NOTE: `set -e` is intentionally OFF — failure handling is explicit so we
# can emit a structured warning and return a documented exit code instead
# of dying mid-flight (the kata branches on the exit code to fall back).

umask 077

# ─── Token redaction guard ─────────────────────────────────────────────────
# Defensive: if BASH_XTRACEFD/PS4 are not set or the caller uses `set -x`,
# wrap curl invocations in a `_curl_silent` helper that toggles xtrace OFF
# for the duration of the call. The token is the only secret in this script
# and never appears outside curl Authorization headers.
_AHRENA_API_COMMIT_XTRACE_WAS_ON=0
if [[ "$-" == *x* ]]; then
  _AHRENA_API_COMMIT_XTRACE_WAS_ON=1
fi

_curl_silent() {
  # Run curl with xtrace forced OFF so the Authorization header (containing
  # the installation token) never lands in the trace stream. Restore the
  # caller's xtrace state after.
  local _was_x=0
  if [[ "$-" == *x* ]]; then _was_x=1; set +x; fi
  curl "$@"
  local rc=$?
  if [[ "${_was_x}" == "1" ]]; then set -x; fi
  return "${rc}"
}

# ─── Arg parsing ───────────────────────────────────────────────────────────
BRANCH=""
MESSAGE=""
REPO=""
CO_AUTHOR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --branch)
      BRANCH="${2:-}"
      shift 2
      ;;
    --message)
      MESSAGE="${2:-}"
      shift 2
      ;;
    --repo)
      REPO="${2:-}"
      shift 2
      ;;
    --co-author)
      CO_AUTHOR="${2:-}"
      shift 2
      ;;
    --help|-h)
      sed -n '1,/^set -uo pipefail$/p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "ERROR (ahrena-api-commit.sh): unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "${BRANCH}" ]]; then
  echo "ERROR (ahrena-api-commit.sh): --branch is required" >&2
  exit 1
fi
if [[ -z "${MESSAGE}" ]]; then
  echo "ERROR (ahrena-api-commit.sh): --message is required" >&2
  exit 1
fi

# ─── Activation gate ───────────────────────────────────────────────────────
# The kata only invokes this script when bot_author.enabled=true AND the
# calling warrior is in bot_author.apply_to. As a defensive second check,
# verify GH_TOKEN_AHRENA_BOT is exported (set by ahrena-auth.sh). When the
# directive is disabled, ahrena-auth.sh is a no-op and the var is absent —
# in that case this script exits 0 without acting (the kata then proceeds
# with the local `git commit` path).
if [[ -z "${GH_TOKEN_AHRENA_BOT:-}" ]]; then
  # Strict no-op: bot mode is off. Exit 0 so the kata's success-path branch
  # falls through to local commit without treating the absence as failure.
  exit 0
fi

# ─── Resolve repo ──────────────────────────────────────────────────────────
if [[ -z "${REPO}" ]]; then
  ORIGIN_URL="$(git remote get-url origin 2>/dev/null || true)"
  if [[ -z "${ORIGIN_URL}" ]]; then
    echo "WARN (ahrena-api-commit.sh): cannot resolve repo — no 'origin' remote." >&2
    exit 2
  fi
  # Strip protocol and .git suffix: handles both git@github.com:owner/repo.git
  # and https://github.com/owner/repo[.git] forms.
  REPO="$(printf '%s' "${ORIGIN_URL}" \
    | sed -E -e 's#^git@[^:]+:##' -e 's#^https?://[^/]+/##' -e 's#\.git$##')"
fi

if [[ ! "${REPO}" =~ ^[^/]+/[^/]+$ ]]; then
  echo "WARN (ahrena-api-commit.sh): resolved repo '${REPO}' is not in owner/repo form." >&2
  exit 2
fi

# ─── Tempfile cleanup ──────────────────────────────────────────────────────
_AHRENA_API_COMMIT_TMPDIR=""
# shellcheck disable=SC2329 # invoked indirectly via EXIT trap
_ahrena_api_commit_cleanup() {
  if [[ -n "${_AHRENA_API_COMMIT_TMPDIR}" && -d "${_AHRENA_API_COMMIT_TMPDIR}" ]]; then
    rm -rf "${_AHRENA_API_COMMIT_TMPDIR}"
  fi
  _AHRENA_API_COMMIT_TMPDIR=""
  return 0
}
trap _ahrena_api_commit_cleanup EXIT

_AHRENA_API_COMMIT_TMPDIR="$(mktemp -d -t ahrena-api-commit.XXXXXXXX)"

# ─── API helpers ───────────────────────────────────────────────────────────
# _api_call <method> <path> [<body_file>]
#   Prints JSON body on success (HTTP 2xx). Returns non-zero on transport
#   failure or non-2xx response (writes a redacted warning to stderr).
#   The token only appears in the Authorization header — never in error text.
_AHRENA_API_BASE="https://api.github.com"
_AHRENA_API_RETRIED_401=0

_api_call() {
  local method="$1"
  local path="$2"
  local body_file="${3:-}"
  local out_file
  out_file="$(mktemp "${_AHRENA_API_COMMIT_TMPDIR}/resp.XXXXXX")"

  local curl_args=(
    -sS
    -X "${method}"
    -H "Accept: application/vnd.github+json"
    -H "Authorization: Bearer ${GH_TOKEN_AHRENA_BOT}"
    -H "X-GitHub-Api-Version: 2022-11-28"
    -o "${out_file}"
    -w '%{http_code}'
  )
  if [[ -n "${body_file}" && -f "${body_file}" ]]; then
    curl_args+=(-H "Content-Type: application/json" --data-binary "@${body_file}")
  fi

  local http_code
  http_code="$(_curl_silent "${curl_args[@]}" "${_AHRENA_API_BASE}${path}")" || {
    echo "WARN (ahrena-api-commit.sh): curl transport failure on ${method} ${path}" >&2
    return 1
  }

  # 401 — try to refresh the token once via ahrena-auth.sh (in case the
  # cached installation token expired between mint and use).
  if [[ "${http_code}" == "401" && "${_AHRENA_API_RETRIED_401}" == "0" ]]; then
    _AHRENA_API_RETRIED_401=1
    echo "WARN (ahrena-api-commit.sh): HTTP 401; refreshing installation token via ahrena-auth.sh and retrying once." >&2
    local script_dir
    script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    if [[ -r "${script_dir}/ahrena-auth.sh" ]]; then
      # shellcheck disable=SC1091
      source "${script_dir}/ahrena-auth.sh" >/dev/null 2>&1 || true
      # Refresh curl_args[5] (the Authorization header) with the new token.
      # The Authorization header is at index 5 in curl_args (0=-sS, 1=-X,
      # 2=METHOD, 3=-H, 4=Accept, 5=-H, 6=Authorization). Rebuild for safety.
      curl_args=(
        -sS
        -X "${method}"
        -H "Accept: application/vnd.github+json"
        -H "Authorization: Bearer ${GH_TOKEN_AHRENA_BOT}"
        -H "X-GitHub-Api-Version: 2022-11-28"
        -o "${out_file}"
        -w '%{http_code}'
      )
      if [[ -n "${body_file}" && -f "${body_file}" ]]; then
        curl_args+=(-H "Content-Type: application/json" --data-binary "@${body_file}")
      fi
      http_code="$(_curl_silent "${curl_args[@]}" "${_AHRENA_API_BASE}${path}")" || {
        echo "WARN (ahrena-api-commit.sh): curl transport failure on retry of ${method} ${path}" >&2
        return 1
      }
    else
      echo "WARN (ahrena-api-commit.sh): cannot retry 401 — ahrena-auth.sh not readable at ${script_dir}." >&2
    fi
  fi

  if [[ ! "${http_code}" =~ ^2[0-9][0-9]$ ]]; then
    # Print a summary of the response body without the token. The response
    # body itself never contains the installation token (GitHub responses
    # do not echo bearer credentials).
    local body_summary
    body_summary="$(head -c 500 "${out_file}" 2>/dev/null || echo "")"
    echo "WARN (ahrena-api-commit.sh): HTTP ${http_code} on ${method} ${path}: ${body_summary}" >&2
    return 1
  fi

  cat "${out_file}"
  return 0
}

# ─── Step 1: parent commit SHA + tree SHA ──────────────────────────────────
# Use the local HEAD SHA (matches the branch tip that the user is committing
# from). The PATCH ref step at the end refuses non-fast-forward updates
# unless we pass force=true — we don't, so the local HEAD MUST already match
# origin/<branch>. Caller guarantees this via the standard kata flow
# (`git pull --ff-only` before staging).
PARENT_SHA="$(git rev-parse HEAD 2>/dev/null || true)"
if [[ -z "${PARENT_SHA}" ]]; then
  echo "WARN (ahrena-api-commit.sh): cannot resolve HEAD — not in a git working tree." >&2
  exit 2
fi

PARENT_TREE_SHA="$(git rev-parse "${PARENT_SHA}^{tree}" 2>/dev/null || true)"
if [[ -z "${PARENT_TREE_SHA}" ]]; then
  echo "WARN (ahrena-api-commit.sh): cannot resolve tree of parent commit ${PARENT_SHA}." >&2
  exit 2
fi

# ─── Step 2: collect staged paths ──────────────────────────────────────────
# `git diff --cached --name-status` emits: <STATUS><TAB><PATH>[<TAB><PATH>]
# Statuses: A (added), M (modified), D (deleted), R{score} (rename), C{score}
# (copy), T (type change). We treat A/M/T as blob upload, D as deletion,
# and R/C as "delete old + add new" (the new blob is the staged content of
# the new path; the old path is deleted in the tree entry).
STAGED_STATUS="$(git diff --cached --name-status 2>/dev/null || true)"
if [[ -z "${STAGED_STATUS}" ]]; then
  echo "WARN (ahrena-api-commit.sh): nothing staged — refusing to create an empty commit." >&2
  exit 2
fi

# Build tree entries as a JSON array in a tempfile (avoid argv length limits
# on large diffs).
TREE_ENTRIES_FILE="${_AHRENA_API_COMMIT_TMPDIR}/tree-entries.json"
echo '[]' > "${TREE_ENTRIES_FILE}"

_append_tree_entry() {
  local path="$1"
  local mode="$2"
  local sha_or_null="$3"  # blob SHA string, or "null" literal for deletion
  local tmp
  tmp="$(mktemp "${_AHRENA_API_COMMIT_TMPDIR}/tree-acc.XXXXXX")"
  if [[ "${sha_or_null}" == "null" ]]; then
    jq --arg p "${path}" --arg m "${mode}" \
      '. + [{path: $p, mode: $m, type: "blob", sha: null}]' \
      "${TREE_ENTRIES_FILE}" > "${tmp}"
  else
    jq --arg p "${path}" --arg m "${mode}" --arg s "${sha_or_null}" \
      '. + [{path: $p, mode: $m, type: "blob", sha: $s}]' \
      "${TREE_ENTRIES_FILE}" > "${tmp}"
  fi
  mv -f "${tmp}" "${TREE_ENTRIES_FILE}"
}

# Resolve the file mode (100644 normal, 100755 executable, 120000 symlink)
# from the index when staging an add/modify. Fall back to 100644 if the
# index lookup fails.
_resolve_mode() {
  local path="$1"
  local mode
  # `git ls-files --stage <path>` prints: <mode> <sha> <stage>\t<path>
  mode="$(git ls-files --stage -- "${path}" 2>/dev/null | awk '{print $1; exit}')"
  if [[ -z "${mode}" ]]; then
    # Path is staged-as-add but not yet in the index? Fall back to working-
    # tree mode via `stat`. Symlinks become 120000; executables 100755;
    # everything else 100644.
    if [[ -L "${path}" ]]; then
      mode="120000"
    elif [[ -x "${path}" ]]; then
      mode="100755"
    else
      mode="100644"
    fi
  fi
  printf '%s' "${mode}"
}

# Stream the status output line by line. Use `printf` + IFS rather than
# `<<< "${STAGED_STATUS}"` so paths with embedded spaces survive (the TAB
# separator from --name-status guarantees the path field is intact).
while IFS=$'\t' read -r status path1 path2; do
  [[ -z "${status}" ]] && continue
  case "${status}" in
    A|M|T)
      mode="$(_resolve_mode "${path1}")"
      # Build the blob payload. Use base64 for binary safety: every file
      # ships as `{content: "<base64>", encoding: "base64"}` so non-UTF-8
      # bytes (images, .pyc, etc.) round-trip cleanly. Text files also
      # work — GitHub stores the decoded bytes.
      blob_payload="${_AHRENA_API_COMMIT_TMPDIR}/blob-payload.json"
      content_b64="$(git show ":${path1}" 2>/dev/null | base64 | tr -d '\n')"
      if [[ -z "${content_b64}" ]]; then
        # Empty file — base64 of zero bytes is the empty string; emit an
        # explicit empty content blob.
        content_b64=""
      fi
      jq -n --arg c "${content_b64}" --arg e "base64" \
        '{content: $c, encoding: $e}' > "${blob_payload}"

      blob_response="$(_api_call POST "/repos/${REPO}/git/blobs" "${blob_payload}")" || {
        echo "WARN (ahrena-api-commit.sh): blob upload failed for ${path1}" >&2
        exit 2
      }
      blob_sha="$(printf '%s' "${blob_response}" | jq -r '.sha // empty')"
      if [[ -z "${blob_sha}" ]]; then
        echo "WARN (ahrena-api-commit.sh): blob response missing sha for ${path1}" >&2
        exit 2
      fi
      _append_tree_entry "${path1}" "${mode}" "${blob_sha}"
      ;;
    D)
      # Deletion — sha:null tells GitHub to remove the path from the tree.
      # Mode is still required; reuse 100644 (it's a marker, not enforced).
      _append_tree_entry "${path1}" "100644" "null"
      ;;
    R*|C*)
      # Rename or copy. Delete the old path (path1) and add the new path
      # (path2) with the staged content of the destination.
      if [[ -z "${path2:-}" ]]; then
        echo "WARN (ahrena-api-commit.sh): rename/copy status '${status}' missing destination path." >&2
        exit 2
      fi
      _append_tree_entry "${path1}" "100644" "null"
      mode="$(_resolve_mode "${path2}")"
      blob_payload="${_AHRENA_API_COMMIT_TMPDIR}/blob-payload.json"
      content_b64="$(git show ":${path2}" 2>/dev/null | base64 | tr -d '\n')"
      jq -n --arg c "${content_b64}" --arg e "base64" \
        '{content: $c, encoding: $e}' > "${blob_payload}"
      blob_response="$(_api_call POST "/repos/${REPO}/git/blobs" "${blob_payload}")" || {
        echo "WARN (ahrena-api-commit.sh): blob upload failed for ${path2}" >&2
        exit 2
      }
      blob_sha="$(printf '%s' "${blob_response}" | jq -r '.sha // empty')"
      if [[ -z "${blob_sha}" ]]; then
        echo "WARN (ahrena-api-commit.sh): blob response missing sha for ${path2}" >&2
        exit 2
      fi
      _append_tree_entry "${path2}" "${mode}" "${blob_sha}"
      ;;
    *)
      echo "WARN (ahrena-api-commit.sh): unsupported diff status '${status}' for path '${path1}'" >&2
      exit 2
      ;;
  esac
done < <(printf '%s\n' "${STAGED_STATUS}")

# ─── Step 3: create tree ───────────────────────────────────────────────────
TREE_PAYLOAD_FILE="${_AHRENA_API_COMMIT_TMPDIR}/tree-payload.json"
jq -n \
  --arg base_tree "${PARENT_TREE_SHA}" \
  --slurpfile tree "${TREE_ENTRIES_FILE}" \
  '{base_tree: $base_tree, tree: $tree[0]}' > "${TREE_PAYLOAD_FILE}"

TREE_RESPONSE="$(_api_call POST "/repos/${REPO}/git/trees" "${TREE_PAYLOAD_FILE}")" || {
  echo "WARN (ahrena-api-commit.sh): tree creation failed." >&2
  exit 2
}
NEW_TREE_SHA="$(printf '%s' "${TREE_RESPONSE}" | jq -r '.sha // empty')"
if [[ -z "${NEW_TREE_SHA}" ]]; then
  echo "WARN (ahrena-api-commit.sh): tree response missing sha." >&2
  exit 2
fi

# ─── Step 4: create commit ─────────────────────────────────────────────────
# Inject the Co-authored-by trailer when provided. The trailer goes at the
# end of the message body separated by a blank line (per `git interpret-
# trailers` convention).
FINAL_MESSAGE="${MESSAGE}"
if [[ -n "${CO_AUTHOR}" ]]; then
  # Ensure exactly one blank line between body and trailer block.
  case "${FINAL_MESSAGE}" in
    *$'\n\n') : ;;             # already ends with blank line
    *$'\n') FINAL_MESSAGE="${FINAL_MESSAGE}"$'\n' ;;
    *) FINAL_MESSAGE="${FINAL_MESSAGE}"$'\n\n' ;;
  esac
  FINAL_MESSAGE="${FINAL_MESSAGE}Co-authored-by: ${CO_AUTHOR}"
fi

COMMIT_PAYLOAD_FILE="${_AHRENA_API_COMMIT_TMPDIR}/commit-payload.json"
jq -n \
  --arg message "${FINAL_MESSAGE}" \
  --arg tree "${NEW_TREE_SHA}" \
  --arg parent "${PARENT_SHA}" \
  '{message: $message, tree: $tree, parents: [$parent]}' > "${COMMIT_PAYLOAD_FILE}"

COMMIT_RESPONSE="$(_api_call POST "/repos/${REPO}/git/commits" "${COMMIT_PAYLOAD_FILE}")" || {
  echo "WARN (ahrena-api-commit.sh): commit creation failed." >&2
  exit 2
}
NEW_COMMIT_SHA="$(printf '%s' "${COMMIT_RESPONSE}" | jq -r '.sha // empty')"
if [[ -z "${NEW_COMMIT_SHA}" ]]; then
  echo "WARN (ahrena-api-commit.sh): commit response missing sha." >&2
  exit 2
fi

# ─── Step 5: update branch ref ─────────────────────────────────────────────
REF_PAYLOAD_FILE="${_AHRENA_API_COMMIT_TMPDIR}/ref-payload.json"
jq -n --arg sha "${NEW_COMMIT_SHA}" '{sha: $sha, force: false}' > "${REF_PAYLOAD_FILE}"

# Body of the ref-update response is not consumed (the success-or-fail is
# what matters); discard via /dev/null but keep the failure branch.
if ! _api_call PATCH "/repos/${REPO}/git/refs/heads/${BRANCH}" "${REF_PAYLOAD_FILE}" >/dev/null; then
  echo "WARN (ahrena-api-commit.sh): ref update failed for refs/heads/${BRANCH}." >&2
  exit 2
fi

# ─── Step 6: sync local working tree ───────────────────────────────────────
# Fetch the server-side branch and reset the local checkout so subsequent
# git operations (push, log, status) see the bot-authored commit instead of
# diverging from the remote. Exit code 3 differentiates "commit landed but
# local sync failed" from "commit failed entirely" (exit 2).
if ! git fetch --quiet origin "${BRANCH}" 2>/dev/null; then
  echo "WARN (ahrena-api-commit.sh): commit ${NEW_COMMIT_SHA} created on remote but 'git fetch origin ${BRANCH}' failed; run it manually before pushing." >&2
  exit 3
fi
if ! git reset --quiet --hard "origin/${BRANCH}" 2>/dev/null; then
  echo "WARN (ahrena-api-commit.sh): commit ${NEW_COMMIT_SHA} created on remote but 'git reset --hard origin/${BRANCH}' failed; reset manually before pushing." >&2
  exit 3
fi

echo "${NEW_COMMIT_SHA}"
exit 0
