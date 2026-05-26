#!/usr/bin/env bash
# ahrena-auth.sh — Warriors default GitHub App authentication helper.
#
# Generates an installation access token for the fleet-default warrior
# GitHub App so warrior-driven commits and PRs are attributed to the App's
# `[bot]` identity instead of the human contributor's PAT/GPG key. Designed
# to be `source`'d, not executed: the script EXPORTS environment variables
# for downstream `git`/`gh` invocations in the same shell.
#
# Activation gate:
#   warriors_default_author.enabled in .ahrena/.directives is the master
#   switch. When false (or the directive is absent), this script is a
#   strict no-op: it returns 0 immediately, exports nothing, prints
#   nothing. Existing human-author behavior is preserved bit-for-bit.
#
# When enabled, the resolution flow mirrors scripts/argos/auth.sh:
#   1. Load AHRENA_WARRIORS_DEFAULT_GH_* credentials from .env.local
#      (project root) OR the current environment (env wins for CI). When
#      a variable is still missing AND the host is macOS with the
#      `security` CLI on PATH, fill it from the Keychain entry of the
#      same name family:
#        ahrena-warriors-default-gh-app-id
#        ahrena-warriors-default-gh-installation-id
#        ahrena-warriors-default-gh-private-key  (PEM content)
#      Missing on Linux / Windows → the require checks below surface the
#      specific variable that needs to be set.
#   2. If cached installation token at .ahrena/bot/installation-token.json
#      is still fresh (>= 5 min before expiry), reuse it.
#   3. Otherwise:
#      a. Sign a JWT (RS256, 10-min expiry) with the App private key.
#         When the PEM came from the Keychain, it is materialized into a
#         chmod-600 tempfile that the cleanup trap removes on exit.
#      b. Exchange the JWT for an installation token via
#         POST /app/installations/{id}/access_tokens.
#      c. Cache the token + expiry timestamp (chmod 0600).
#   4. Resolve the App's numeric `[bot]` user id via
#      GET /users/{slug}[bot] to build the noreply GitHub email.
#   5. Export GH_TOKEN_AHRENA_WARRIORS_DEFAULT, GIT_AUTHOR_NAME,
#      GIT_AUTHOR_EMAIL, GIT_COMMITTER_NAME, GIT_COMMITTER_EMAIL for the
#      calling shell.
#
# Typical usage (P2 wiring; P1 only ships the script + no-op behavior):
#   source scripts/ahrena-auth.sh
#   GH_TOKEN="${GH_TOKEN_AHRENA_WARRIORS_DEFAULT:-${GH_TOKEN}}" git commit -m "..."
#
# Requires (only when warriors_default_author.enabled=true): bash 3.2+,
# openssl, jq, curl, base64. None are required when disabled — the no-op
# exits first.
#
# IMPORTANT — designed to be sourced:
#   This script does NOT use `set -euo pipefail` at the top because a
#   sourced script inherits the calling shell. Errors are handled
#   defensively with explicit checks + `return` (when sourced) or `exit`
#   (when executed directly). Token values are NEVER echoed to stdout
#   or to logs — they are exported and consumed by downstream tools.
#
# xtrace-defense pattern (Plan P7 — Issue #283):
#   The activated path of this script touches secret material on every
#   non-trivial line: it reads the App private key, base64-encodes the JWT
#   header/payload, signs the JWT with `openssl dgst`, POSTs the JWT to
#   /app/installations/{id}/access_tokens, and exports the resulting
#   installation token to the calling shell. If the calling shell has
#   `set -x` (xtrace) active — directly or inherited from `set -euxo
#   pipefail` in a caller — every one of those operations would land in
#   the trace stream on stderr in plain text, leaking the private key,
#   the JWT, and the installation token to terminal history, scrollback,
#   and CI logs.
#
#   This script defends against that leak by capturing the caller's
#   xtrace state at the entry of the activated path, forcing `set +x`
#   for the duration, and restoring the caller's state at every exit
#   point (success and error paths). The guard ceremony lives at the
#   boundary, not inside individual lines, so the entire sensitive flow
#   runs with xtrace OFF regardless of how it was enabled upstream.
#
#   The no-op path (when warriors_default_author.enabled=false or
#   absent) deliberately leaves xtrace alone: it touches no secrets,
#   so legitimate debugging of the activation gate stays observable.
#
#   The guard pattern (canonical, mirrored from scripts/ahrena-api-commit.sh):
#     { _SAVED_XTRACE=${-//[^x]/}; set +x; } 2>/dev/null
#     # ... sensitive code ...
#     { [ "${_SAVED_XTRACE}" = "x" ] && set -x; } 2>/dev/null
#
#   The redirect to /dev/null on each toggle hides the `set +x` and
#   `set -x` commands themselves from the trace stream — without it,
#   the guard would announce its own activation and obscure the trace
#   immediately around the protected region.

# ─── Source vs. exec detection ─────────────────────────────────────────────
# When sourced: ${BASH_SOURCE[0]} != $0; use `return` to exit early without
# killing the calling shell. When executed directly: use `exit`.
if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
  _AHRENA_AUTH_SOURCED=1
else
  _AHRENA_AUTH_SOURCED=0
fi

_ahrena_auth_exit() {
  local code="${1:-0}"
  # Restore the caller's xtrace state BEFORE handing control back.
  # Sourced path: the EXIT trap does not fire (it would belong to the
  # calling shell), so we MUST restore here or the caller observes a
  # silently-disabled xtrace after the script returns. Executed path:
  # the trap also runs `_ahrena_auth_finalize`, but calling restore
  # here first is idempotent and keeps the contract uniform across
  # both invocation modes. The function is declared before the
  # activated path's helpers, so guard against the variable/helper
  # being undefined when the no-op path returns 0 without ever
  # touching xtrace state.
  if declare -F _ahrena_auth_restore_xtrace >/dev/null 2>&1; then
    _ahrena_auth_restore_xtrace
  fi
  if [[ "${_AHRENA_AUTH_SOURCED}" == "1" ]]; then
    return "${code}"
  else
    exit "${code}"
  fi
}

# ─── Paths ─────────────────────────────────────────────────────────────────
# Worktree-aware (mirrors scripts/argos/auth.sh): when invoked from inside
# a git worktree, .env.local and the installation-token cache live at the
# main repo root, not at the worktree dir.
_AHRENA_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
_AHRENA_REPO_ROOT="$( cd "${_AHRENA_SCRIPT_DIR}/.." && pwd )"
_AHRENA_GIT_COMMON_DIR_REL="$( cd "${_AHRENA_REPO_ROOT}" && git rev-parse --git-common-dir 2>/dev/null || true )"
if [[ -n "${_AHRENA_GIT_COMMON_DIR_REL}" ]]; then
  _AHRENA_GIT_COMMON_DIR_ABS="$( cd "${_AHRENA_REPO_ROOT}" && cd "${_AHRENA_GIT_COMMON_DIR_REL}" && pwd )"
  _AHRENA_MAIN_REPO_ROOT="$( dirname "${_AHRENA_GIT_COMMON_DIR_ABS}" )"
else
  _AHRENA_MAIN_REPO_ROOT="${_AHRENA_REPO_ROOT}"
fi
_AHRENA_DIRECTIVES_FILE="${_AHRENA_MAIN_REPO_ROOT}/.ahrena/.directives"
_AHRENA_ENV_FILE="${_AHRENA_MAIN_REPO_ROOT}/.env.local"
_AHRENA_CACHE_DIR="${_AHRENA_MAIN_REPO_ROOT}/.ahrena/bot"
_AHRENA_CACHE_FILE="${_AHRENA_CACHE_DIR}/installation-token.json"

# ─── Gate: warriors_default_author.enabled in .directives ──────────────────
# Strict no-op when the directive is absent OR `enabled` is anything other
# than `true`. Parses the minimal YAML shape:
#   warriors_default_author:
#     enabled: true|false
# Uses awk (no Python dependency, portable across macOS BSD + GNU). The
# parser scans for the `warriors_default_author:` block start, then reads
# `enabled: VAL` at the first indent level beneath it. Anything else
# (comments, missing section, malformed value) defaults to disabled.
_ahrena_auth_is_enabled() {
  local file="$1"
  [[ -f "${file}" ]] || return 1
  local value
  value="$(awk '
    /^warriors_default_author:[[:space:]]*$/ { in_section = 1; next }
    in_section && /^[^[:space:]#]/ { in_section = 0 }
    in_section && /^[[:space:]]+enabled:/ {
      sub(/^[[:space:]]+enabled:[[:space:]]*/, "")
      sub(/[[:space:]]*#.*$/, "")
      sub(/[[:space:]]+$/, "")
      gsub(/["'\'']/, "")
      print tolower($0)
      exit
    }
  ' "${file}")"
  [[ "${value}" == "true" ]]
}

if ! _ahrena_auth_is_enabled "${_AHRENA_DIRECTIVES_FILE}"; then
  # Strict no-op: directive absent or disabled. Preserve existing
  # human-author behavior bit-for-bit by exporting nothing.
  #
  # IMPORTANT: when sourced, `return` from a top-level statement exits
  # the sourced script cleanly without affecting the calling shell.
  # When executed, `exit 0` ends the process. The condition mirrors the
  # _ahrena_auth_exit helper but lives inline so a stray fall-through
  # into the activated path is impossible.
  if [[ "${_AHRENA_AUTH_SOURCED}" == "1" ]]; then
    return 0
  else
    exit 0
  fi
fi

# ─── Activated path ────────────────────────────────────────────────────────
# From this point on the directive opted in. Use defensive checks instead
# of `set -euo pipefail` to avoid killing the calling shell when sourced.
#
# xtrace-defense entry point (Plan P7 — Issue #283):
#   Capture the caller's xtrace state BEFORE doing anything that could
#   leak. `${-//[^x]/}` collapses the current shell flag set to either
#   the literal "x" (xtrace on) or the empty string (xtrace off). The
#   `set +x` then disables xtrace for the rest of the activated path,
#   and `_ahrena_auth_restore_xtrace` restores the caller's original
#   state at every exit point. The redirect `2>/dev/null` on each
#   toggle hides the toggle command itself from any in-flight trace.
{ _AHRENA_SAVED_XTRACE=${-//[^x]/}; set +x; } 2>/dev/null

umask 077

# Unified tempfile cleanup (idempotent). Internal helper — the public
# cleanup-and-restore wrapper is `_ahrena_auth_finalize` below.
_AHRENA_KEYCHAIN_TMP_KEY=""
_AHRENA_TMP_CACHE=""
_ahrena_auth_cleanup() {
  [[ -n "${_AHRENA_KEYCHAIN_TMP_KEY}" ]] && rm -f "${_AHRENA_KEYCHAIN_TMP_KEY}"
  [[ -n "${_AHRENA_TMP_CACHE}" ]] && rm -f "${_AHRENA_TMP_CACHE}"
  _AHRENA_KEYCHAIN_TMP_KEY=""
  _AHRENA_TMP_CACHE=""
  return 0
}

# Restore the caller's xtrace state. Idempotent — safe to call multiple
# times along an error path. The inner brace block + 2>/dev/null mirrors
# the entry-point guard so the restore command itself never lands in
# the trace stream.
_ahrena_auth_restore_xtrace() {
  { [ "${_AHRENA_SAVED_XTRACE:-}" = "x" ] && set -x; } 2>/dev/null
  return 0
}

# Combined finalizer: clean up tempfiles, then restore xtrace. Every
# exit path in the activated section calls this (directly or via the
# trap) so the caller never observes a leak window between cleanup
# and xtrace restoration.
_ahrena_auth_finalize() {
  _ahrena_auth_cleanup
  _ahrena_auth_restore_xtrace
  return 0
}

# Only register the trap when executed (not sourced) — a sourced script
# must not steal the calling shell's EXIT handler. The trap also covers
# unexpected exits (signals, errors that bypass the explicit cleanup).
if [[ "${_AHRENA_AUTH_SOURCED}" == "0" ]]; then
  trap _ahrena_auth_finalize EXIT
fi

# Load .env.local (env wins)
if [[ -f "${_AHRENA_ENV_FILE}" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${_AHRENA_ENV_FILE}"
  set +a
fi

# ─── macOS Keychain resolution (Plan P8 — Issue #284) ──────────────────────
# After .env.local + inherited env, fill missing values from the macOS
# Keychain. The activated path is already running with xtrace OFF (see the
# master guard at the top of this section), so the `security` invocations
# below do NOT leak under `bash -x`. Each lookup is independent:
# the operator can store any subset in Keychain and the rest in env / .env.local.
#
# Cross-platform contract:
#   - On Linux / Windows (no `security` on PATH) the entire block is
#     skipped via the `command -v security` guard. Missing variables
#     then surface through `_ahrena_auth_require` with the established
#     env-only error message. AC-P8-3.
#   - On macOS, an empty Keychain falls through cleanly: each `security
#     find-generic-password` call ends with `|| true` so the script
#     never trips on a missing entry; the assignment guard
#     (`[[ -n ... ]]`) skips when the lookup returned nothing.
#
# Service-name convention (Plan P8 scope item 4):
#   ahrena-warriors-default-gh-app-id          → APP_ID (plain value)
#   ahrena-warriors-default-gh-installation-id → INSTALLATION_ID (plain value)
#   ahrena-warriors-default-gh-private-key     → PEM content (multiline)
#
# The private-key Keychain entry stores the PEM CONTENT verbatim
# (option (b) of the scope: tempfile materialized at runtime; the key
# never lives on disk under the operator's $HOME). The existing
# `_ahrena_auth_cleanup` trap removes the tempfile on every exit path.
if command -v security >/dev/null 2>&1 && [[ "$(uname -s)" == "Darwin" ]]; then
  if [[ -z "${AHRENA_WARRIORS_DEFAULT_GH_APP_ID:-}" ]]; then
    _AHRENA_KEYCHAIN_APP_ID="$(security find-generic-password \
      -s ahrena-warriors-default-gh-app-id -a "${USER}" -w 2>/dev/null || true)"
    if [[ -n "${_AHRENA_KEYCHAIN_APP_ID}" ]]; then
      AHRENA_WARRIORS_DEFAULT_GH_APP_ID="${_AHRENA_KEYCHAIN_APP_ID}"
    fi
    unset _AHRENA_KEYCHAIN_APP_ID
  fi

  if [[ -z "${AHRENA_WARRIORS_DEFAULT_GH_INSTALLATION_ID:-}" ]]; then
    _AHRENA_KEYCHAIN_INSTALLATION_ID="$(security find-generic-password \
      -s ahrena-warriors-default-gh-installation-id -a "${USER}" -w 2>/dev/null || true)"
    if [[ -n "${_AHRENA_KEYCHAIN_INSTALLATION_ID}" ]]; then
      AHRENA_WARRIORS_DEFAULT_GH_INSTALLATION_ID="${_AHRENA_KEYCHAIN_INSTALLATION_ID}"
    fi
    unset _AHRENA_KEYCHAIN_INSTALLATION_ID
  fi
fi

# Validate required credentials (defensive: emit error + return non-zero)
_ahrena_auth_require() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    echo "ERROR (ahrena-auth.sh): missing ${name} (set in .env.local, env, or macOS Keychain)." >&2
    _ahrena_auth_cleanup
    _ahrena_auth_exit 1
    return 1
  fi
  return 0
}

_ahrena_auth_require "AHRENA_WARRIORS_DEFAULT_GH_APP_ID" || return 1 2>/dev/null || exit 1
_ahrena_auth_require "AHRENA_WARRIORS_DEFAULT_GH_INSTALLATION_ID" || return 1 2>/dev/null || exit 1

# Resolve the GitHub App slug (defaults to ahrena-bot; overridable via env)
_AHRENA_APP_SLUG="${AHRENA_WARRIORS_DEFAULT_GH_SLUG:-ahrena-bot}"

# Resolve private key source.
#
# Resolution order:
#   1. macOS Keychain entry `ahrena-warriors-default-gh-private-key`
#      (PEM content stored verbatim) — materialized to a chmod-600 tempfile
#      and removed by the cleanup trap (AC-P8-4).
#   2. Env / .env.local `AHRENA_WARRIORS_DEFAULT_GH_PRIVATE_KEY_PATH` —
#      file path to an existing PEM on disk.
#
# The Keychain branch only fires when `security` exists AND the entry is
# present. Empty entries fall through to the file-path branch. This
# preserves the established behavior for operators on Linux/Windows and
# for macOS operators who prefer the env-vars-only setup.
_AHRENA_PRIVATE_KEY_PATH=""

if command -v security >/dev/null 2>&1 && [[ "$(uname -s)" == "Darwin" ]]; then
  if security find-generic-password \
       -s ahrena-warriors-default-gh-private-key -a "${USER}" -w >/dev/null 2>&1; then
    _AHRENA_KEYCHAIN_TMP_KEY="$(mktemp -t "ahrena-warriors-default-key.XXXXXXXX")" || {
      echo "ERROR (ahrena-auth.sh): failed to create temporary file for private key." >&2
      _ahrena_auth_exit 1
      return 1 2>/dev/null
    }
    chmod 600 "${_AHRENA_KEYCHAIN_TMP_KEY}"
    _AHRENA_PEM_RAW="$(security find-generic-password \
      -s ahrena-warriors-default-gh-private-key -a "${USER}" -w 2>/dev/null)" || {
      rm -f "${_AHRENA_KEYCHAIN_TMP_KEY}"
      _AHRENA_KEYCHAIN_TMP_KEY=""
      echo "ERROR (ahrena-auth.sh): Keychain entry 'ahrena-warriors-default-gh-private-key' present but read failed." >&2
      _ahrena_auth_exit 1
      return 1 2>/dev/null
    }
    if [[ "${_AHRENA_PEM_RAW}" == "-----BEGIN"* ]]; then
      printf '%s' "${_AHRENA_PEM_RAW}" > "${_AHRENA_KEYCHAIN_TMP_KEY}"
    else
      # Legacy fallback: some operators stored the PEM hex-encoded.
      printf '%s' "${_AHRENA_PEM_RAW}" | xxd -r -p > "${_AHRENA_KEYCHAIN_TMP_KEY}"
    fi
    unset _AHRENA_PEM_RAW
    _AHRENA_PRIVATE_KEY_PATH="${_AHRENA_KEYCHAIN_TMP_KEY}"
  fi
fi

if [[ -z "${_AHRENA_PRIVATE_KEY_PATH}" ]]; then
  if [[ -n "${AHRENA_WARRIORS_DEFAULT_GH_PRIVATE_KEY_PATH:-}" ]]; then
    _AHRENA_PRIVATE_KEY_PATH="${AHRENA_WARRIORS_DEFAULT_GH_PRIVATE_KEY_PATH/#\~/$HOME}"
  else
    echo "ERROR (ahrena-auth.sh): no private key source available." >&2
    echo "  Either populate the Keychain (macOS):" >&2
    echo "    security add-generic-password -s ahrena-warriors-default-gh-private-key -a \"\$USER\" -w \"\$(cat /path/to/key.pem)\"" >&2
    echo "  Or set AHRENA_WARRIORS_DEFAULT_GH_PRIVATE_KEY_PATH in .env.local / env." >&2
    _ahrena_auth_exit 1
    return 1 2>/dev/null
  fi
fi

if [[ ! -r "${_AHRENA_PRIVATE_KEY_PATH}" ]]; then
  echo "ERROR (ahrena-auth.sh): private key not readable at ${_AHRENA_PRIVATE_KEY_PATH}" >&2
  _ahrena_auth_cleanup
  _ahrena_auth_exit 1
  return 1 2>/dev/null
fi

# ─── Try cache (refresh when < 5min remaining) ─────────────────────────────
_AHRENA_NOW_EPOCH="$(date -u +%s)"
_AHRENA_REFRESH_THRESHOLD=$((5 * 60))
_AHRENA_TOKEN=""
_AHRENA_APP_USER_ID=""

if [[ -f "${_AHRENA_CACHE_FILE}" ]]; then
  _AHRENA_CACHED_TOKEN="$(jq -r '.token // empty' "${_AHRENA_CACHE_FILE}" 2>/dev/null || true)"
  _AHRENA_CACHED_EXPIRES_AT="$(jq -r '.expires_at_epoch // 0' "${_AHRENA_CACHE_FILE}" 2>/dev/null || echo 0)"
  _AHRENA_CACHED_APP_ID="$(jq -r '.app_id // empty' "${_AHRENA_CACHE_FILE}" 2>/dev/null || true)"
  _AHRENA_CACHED_INSTALLATION_ID="$(jq -r '.installation_id // empty' "${_AHRENA_CACHE_FILE}" 2>/dev/null || true)"
  _AHRENA_CACHED_BOT_USER_ID="$(jq -r '.bot_user_id // empty' "${_AHRENA_CACHE_FILE}" 2>/dev/null || true)"

  if [[ -n "${_AHRENA_CACHED_TOKEN}" && \
        "${_AHRENA_CACHED_APP_ID}" == "${AHRENA_WARRIORS_DEFAULT_GH_APP_ID}" && \
        "${_AHRENA_CACHED_INSTALLATION_ID}" == "${AHRENA_WARRIORS_DEFAULT_GH_INSTALLATION_ID}" && \
        $((_AHRENA_CACHED_EXPIRES_AT - _AHRENA_NOW_EPOCH)) -gt "${_AHRENA_REFRESH_THRESHOLD}" ]]; then
    _AHRENA_TOKEN="${_AHRENA_CACHED_TOKEN}"
    _AHRENA_APP_USER_ID="${_AHRENA_CACHED_BOT_USER_ID}"
  fi
fi

# ─── Mint a fresh token when cache miss ────────────────────────────────────
if [[ -z "${_AHRENA_TOKEN}" ]]; then
  _ahrena_b64url() {
    openssl base64 -A | tr -d '\n' | tr '+/' '-_' | tr -d '='
  }

  _AHRENA_IAT=$((_AHRENA_NOW_EPOCH - 60))
  _AHRENA_EXP=$((_AHRENA_NOW_EPOCH + 600))
  _AHRENA_HEADER="$(printf '{"alg":"RS256","typ":"JWT"}' | _ahrena_b64url)"
  _AHRENA_PAYLOAD="$(printf '{"iat":%d,"exp":%d,"iss":"%s"}' \
    "${_AHRENA_IAT}" "${_AHRENA_EXP}" "${AHRENA_WARRIORS_DEFAULT_GH_APP_ID}" | _ahrena_b64url)"
  _AHRENA_SIGNATURE="$(printf '%s.%s' "${_AHRENA_HEADER}" "${_AHRENA_PAYLOAD}" | \
    openssl dgst -sha256 -sign "${_AHRENA_PRIVATE_KEY_PATH}" | _ahrena_b64url)"

  # Erase the Keychain-sourced PEM tempfile right after signing.
  if [[ -n "${_AHRENA_KEYCHAIN_TMP_KEY}" ]]; then
    rm -f "${_AHRENA_KEYCHAIN_TMP_KEY}"
    _AHRENA_KEYCHAIN_TMP_KEY=""
  fi

  _AHRENA_JWT="${_AHRENA_HEADER}.${_AHRENA_PAYLOAD}.${_AHRENA_SIGNATURE}"

  _AHRENA_HTTP_RESPONSE="$(curl -sS \
    -X POST \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${_AHRENA_JWT}" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    -w '\n%{http_code}' \
    "https://api.github.com/app/installations/${AHRENA_WARRIORS_DEFAULT_GH_INSTALLATION_ID}/access_tokens")"

  _AHRENA_HTTP_CODE="$(printf '%s' "${_AHRENA_HTTP_RESPONSE}" | tail -n1)"
  _AHRENA_RESPONSE="$(printf '%s' "${_AHRENA_HTTP_RESPONSE}" | sed '$d')"

  if [[ "${_AHRENA_HTTP_CODE}" != "201" ]]; then
    echo "ERROR (ahrena-auth.sh): GitHub returned HTTP ${_AHRENA_HTTP_CODE} when minting installation token." >&2
    _ahrena_auth_cleanup
    _ahrena_auth_exit 1
    return 1 2>/dev/null
  fi

  _AHRENA_TOKEN="$(echo "${_AHRENA_RESPONSE}" | jq -r '.token // empty')"
  _AHRENA_EXPIRES_AT="$(echo "${_AHRENA_RESPONSE}" | jq -r '.expires_at // empty')"

  if [[ -z "${_AHRENA_TOKEN}" || -z "${_AHRENA_EXPIRES_AT}" ]]; then
    echo "ERROR (ahrena-auth.sh): mint succeeded (HTTP 201) but response missing token/expires_at." >&2
    _ahrena_auth_cleanup
    _ahrena_auth_exit 1
    return 1 2>/dev/null
  fi

  # ISO 8601 → epoch (portable between BSD and GNU date)
  if date -u -d "${_AHRENA_EXPIRES_AT}" +%s >/dev/null 2>&1; then
    _AHRENA_EXPIRES_AT_EPOCH="$(date -u -d "${_AHRENA_EXPIRES_AT}" +%s)"
  else
    _AHRENA_EXPIRES_AT_EPOCH="$(date -u -j -f "%Y-%m-%dT%H:%M:%SZ" "${_AHRENA_EXPIRES_AT}" +%s)"
  fi

  # Resolve the bot's numeric user id once (immutable per App identity);
  # cache alongside the token to avoid repeating the lookup on every call.
  _AHRENA_APP_USER_RESPONSE="$(curl -sS \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${_AHRENA_TOKEN}" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    -w '\n%{http_code}' \
    "https://api.github.com/users/${_AHRENA_APP_SLUG}%5Bbot%5D")"
  _AHRENA_APP_USER_CODE="$(printf '%s' "${_AHRENA_APP_USER_RESPONSE}" | tail -n1)"
  _AHRENA_APP_USER_BODY="$(printf '%s' "${_AHRENA_APP_USER_RESPONSE}" | sed '$d')"
  if [[ "${_AHRENA_APP_USER_CODE}" == "200" ]]; then
    _AHRENA_APP_USER_ID="$(echo "${_AHRENA_APP_USER_BODY}" | jq -r '.id // empty')"
  else
    # Non-fatal: the email becomes slightly less canonical but the
    # author identity still resolves via slug. P2 may tighten this.
    _AHRENA_APP_USER_ID=""
  fi

  # Cache atomically (tempfile + rename)
  mkdir -p "${_AHRENA_CACHE_DIR}"
  _AHRENA_TMP_CACHE="$(mktemp "${_AHRENA_CACHE_DIR}/.installation-token.XXXXXX")" || {
    echo "ERROR (ahrena-auth.sh): failed to create temporary file for installation-token cache." >&2
    _ahrena_auth_exit 1
    return 1 2>/dev/null
  }
  chmod 600 "${_AHRENA_TMP_CACHE}"

  jq -n \
    --arg token "${_AHRENA_TOKEN}" \
    --arg expires_at "${_AHRENA_EXPIRES_AT}" \
    --argjson expires_at_epoch "${_AHRENA_EXPIRES_AT_EPOCH}" \
    --arg app_id "${AHRENA_WARRIORS_DEFAULT_GH_APP_ID}" \
    --arg installation_id "${AHRENA_WARRIORS_DEFAULT_GH_INSTALLATION_ID}" \
    --arg bot_user_id "${_AHRENA_APP_USER_ID}" \
    --argjson minted_at_epoch "${_AHRENA_NOW_EPOCH}" \
    '{token: $token, expires_at: $expires_at, expires_at_epoch: $expires_at_epoch,
      app_id: $app_id, installation_id: $installation_id,
      bot_user_id: $bot_user_id, minted_at_epoch: $minted_at_epoch}' \
    > "${_AHRENA_TMP_CACHE}"

  mv -f "${_AHRENA_TMP_CACHE}" "${_AHRENA_CACHE_FILE}"
  _AHRENA_TMP_CACHE=""
fi

# ─── Export to calling shell ───────────────────────────────────────────────
# Author / committer identity follows GitHub's bot noreply convention:
#   <numeric_user_id>+<slug>[bot]@users.noreply.github.com
# When the user-id lookup failed (rare), fall back to the slug-only form;
# GitHub still recognizes it for attribution, just without the canonical id.
if [[ -n "${_AHRENA_APP_USER_ID}" ]]; then
  _AHRENA_APP_EMAIL="${_AHRENA_APP_USER_ID}+${_AHRENA_APP_SLUG}[bot]@users.noreply.github.com"
else
  _AHRENA_APP_EMAIL="${_AHRENA_APP_SLUG}[bot]@users.noreply.github.com"
fi

export GH_TOKEN_AHRENA_WARRIORS_DEFAULT="${_AHRENA_TOKEN}"
export GIT_AUTHOR_NAME="${_AHRENA_APP_SLUG}[bot]"
export GIT_AUTHOR_EMAIL="${_AHRENA_APP_EMAIL}"
export GIT_COMMITTER_NAME="${_AHRENA_APP_SLUG}[bot]"
export GIT_COMMITTER_EMAIL="${_AHRENA_APP_EMAIL}"

# Clean up internal state without affecting the exports above.
_ahrena_auth_cleanup
_ahrena_auth_exit 0
