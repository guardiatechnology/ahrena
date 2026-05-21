#!/usr/bin/env bash
# auth.sh — warrior-argos GitHub App authentication helper.
#
# Generates an installation access token for the `ahrena-warrior-argos`
# GitHub App so warrior-argos posts PR review comments under the
# `ahrena-warrior-argos[bot]` identity instead of the human user's PAT.
#
# Flow:
#   1. Load AHRENA_WARRIOR_ARGOS_GH_* credentials from .env.local (project root)
#      OR the current environment (env wins over .env.local for CI).
#   2. If cached installation token at .ahrena/argos/installation-token.json
#      is still fresh (>= 5 min before expiry), reuse it.
#   3. Otherwise:
#      a. Sign a JWT (RS256, 10-min expiry) with the App private key.
#      b. Exchange the JWT for an installation token via
#         POST /app/installations/{id}/access_tokens.
#      c. Cache the token + expiry timestamp.
#   4. Emit the installation token to stdout.
#
# Typical usage:
#   GH_TOKEN=$(scripts/argos/auth.sh) gh pr view 136 --comments
#   GH_TOKEN=$(scripts/argos/auth.sh) gh api repos/{owner}/{repo}/pulls/{n}/comments \
#     -f body="..."
#
# Requires: bash 3.2+, openssl (RS256 signing), jq (JSON parsing), curl.
# Issue #132. See `lex-pr-quality` Rule 7 and `pr_cost_tracking.known_ai_reviewers`.

set -euo pipefail

# Restrict default mode so any file/dir created below the cache root starts
# at owner-only (0600 file / 0700 dir). Complementary to the explicit chmod
# 600 on the cache file — closes the brief gap where the tempfile would
# otherwise inherit the parent shell's umask before chmod is reached.
umask 077

# ─── Unified tempfile cleanup ──────────────────────────────────────────────
# Single EXIT trap that removes any temp files created downstream. Callers
# populate KEYCHAIN_TMP_KEY (Keychain-sourced PEM) and TMP_CACHE (token
# cache write); the cleanup is idempotent so happy-path code that already
# consumed/moved the file just leaves the var empty.
KEYCHAIN_TMP_KEY=""
TMP_CACHE=""
cleanup() {
  [[ -n "${KEYCHAIN_TMP_KEY}" ]] && rm -f "${KEYCHAIN_TMP_KEY}"
  [[ -n "${TMP_CACHE}" ]] && rm -f "${TMP_CACHE}"
  return 0  # absorb the [[ -n "" ]] false return when vars are empty
}
trap cleanup EXIT

# ─── Paths ─────────────────────────────────────────────────────────────────
# Worktree-aware: when invoked from inside a git worktree, .env.local and the
# installation-token cache live at the main repo root, not at the worktree
# dir. `git rev-parse --git-common-dir` returns ".git" (relative) in the main
# repo and the absolute path to <main>/.git in a worktree — its parent is the
# main repo root in both cases, so a single resolution covers both modes.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "${SCRIPT_DIR}/../.." && pwd )"
GIT_COMMON_DIR_REL="$( cd "${REPO_ROOT}" && git rev-parse --git-common-dir 2>/dev/null || true )"
if [[ -n "${GIT_COMMON_DIR_REL}" ]]; then
  GIT_COMMON_DIR_ABS="$( cd "${REPO_ROOT}" && cd "${GIT_COMMON_DIR_REL}" && pwd )"
  MAIN_REPO_ROOT="$( dirname "${GIT_COMMON_DIR_ABS}" )"
else
  MAIN_REPO_ROOT="${REPO_ROOT}"
fi
ENV_FILE="${MAIN_REPO_ROOT}/.env.local"
CACHE_DIR="${MAIN_REPO_ROOT}/.ahrena/argos"
CACHE_FILE="${CACHE_DIR}/installation-token.json"

# ─── Load .env.local (env vars win) ────────────────────────────────────────
if [[ -f "${ENV_FILE}" ]]; then
  # Source non-comment, non-empty lines as KEY=VALUE assignments.
  # `set -a` exports each assignment; `set +a` restores default.
  set -a
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  set +a
fi

# ─── Validate required credentials ─────────────────────────────────────────
: "${AHRENA_WARRIOR_ARGOS_GH_APP_ID:?missing AHRENA_WARRIOR_ARGOS_GH_APP_ID (set in .env.local or env)}"
: "${AHRENA_WARRIOR_ARGOS_GH_INSTALLATION_ID:?missing AHRENA_WARRIOR_ARGOS_GH_INSTALLATION_ID}"

# ─── Resolve private key source (Keychain wins on macOS, else file path) ───
#
# Precedence:
#   1. macOS Keychain entry at service `ahrena.warrior-argos.github-app`
#      (preferred — PEM never at rest on disk; materialized to ephemeral
#      mktemp only during the openssl call below).
#   2. Fallback: AHRENA_WARRIOR_ARGOS_GH_PRIVATE_KEY_PATH env var (file path).
#      Required when not on macOS or no Keychain entry exists.
#
# Setup (one-shot on macOS):
#   security add-generic-password \
#     -a "warrior-argos" \
#     -s "ahrena.warrior-argos.github-app" \
#     -w "$(cat /path/to/warrior-argos.<date>.private-key.pem)"
#
KEYCHAIN_SERVICE="ahrena.warrior-argos.github-app"
PRIVATE_KEY_PATH=""
# KEYCHAIN_TMP_KEY initialized at script top; cleanup handled by EXIT trap

if [[ "$(uname -s)" == "Darwin" ]] && \
   security find-generic-password -s "${KEYCHAIN_SERVICE}" -w >/dev/null 2>&1; then
  # Keychain mode — materialize PEM to ephemeral tempfile (umask 077 → 0600)
  KEYCHAIN_TMP_KEY=$(mktemp -t "argos-key.XXXXXXXX")
  PEM_RAW=$(security find-generic-password -s "${KEYCHAIN_SERVICE}" -w 2>/dev/null) || {
    rm -f "${KEYCHAIN_TMP_KEY}"
    echo "ERROR: Keychain returned an entry at service '${KEYCHAIN_SERVICE}' but read failed." >&2
    exit 1
  }
  # `security` returns hex-encoded data when the password contains
  # non-printable bytes (PEM newlines trigger this). A valid PEM starts
  # with `-----BEGIN`; otherwise assume hex and decode via xxd.
  if [[ "${PEM_RAW}" == "-----BEGIN"* ]]; then
    printf '%s' "${PEM_RAW}" > "${KEYCHAIN_TMP_KEY}"
  else
    printf '%s' "${PEM_RAW}" | xxd -r -p > "${KEYCHAIN_TMP_KEY}"
  fi
  unset PEM_RAW
  PRIVATE_KEY_PATH="${KEYCHAIN_TMP_KEY}"
elif [[ -n "${AHRENA_WARRIOR_ARGOS_GH_PRIVATE_KEY_PATH:-}" ]]; then
  # File mode (fallback) — expand ~/ in the path
  PRIVATE_KEY_PATH="${AHRENA_WARRIOR_ARGOS_GH_PRIVATE_KEY_PATH/#\~/$HOME}"
else
  echo "ERROR: no private key source available." >&2
  echo "  Either populate the Keychain (macOS):" >&2
  echo "    security add-generic-password -a warrior-argos -s ${KEYCHAIN_SERVICE} -w \"\$(cat /path/to/key.pem)\"" >&2
  echo "  Or set AHRENA_WARRIOR_ARGOS_GH_PRIVATE_KEY_PATH in .env.local / env." >&2
  exit 1
fi

if [[ ! -r "${PRIVATE_KEY_PATH}" ]]; then
  echo "ERROR: private key not readable at ${PRIVATE_KEY_PATH}" >&2
  [[ -z "${KEYCHAIN_TMP_KEY}" ]] && \
    echo "  Check AHRENA_WARRIOR_ARGOS_GH_PRIVATE_KEY_PATH and chmod 600 the file." >&2
  exit 1
fi

# ─── Try cache (50min TTL, refresh when < 5min remaining) ──────────────────
NOW_EPOCH=$(date -u +%s)
REFRESH_THRESHOLD=$((5 * 60))  # refresh if < 5 min remaining

if [[ -f "${CACHE_FILE}" ]]; then
  CACHED_TOKEN=$(jq -r '.token // empty' "${CACHE_FILE}" 2>/dev/null || true)
  CACHED_EXPIRES_AT=$(jq -r '.expires_at_epoch // 0' "${CACHE_FILE}" 2>/dev/null || echo 0)
  CACHED_APP_ID=$(jq -r '.app_id // empty' "${CACHE_FILE}" 2>/dev/null || true)

  CACHED_INSTALLATION_ID=$(jq -r '.installation_id // empty' "${CACHE_FILE}" 2>/dev/null || true)

  if [[ -n "${CACHED_TOKEN}" && \
        "${CACHED_APP_ID}" == "${AHRENA_WARRIOR_ARGOS_GH_APP_ID}" && \
        "${CACHED_INSTALLATION_ID}" == "${AHRENA_WARRIOR_ARGOS_GH_INSTALLATION_ID}" && \
        $((CACHED_EXPIRES_AT - NOW_EPOCH)) -gt "${REFRESH_THRESHOLD}" ]]; then
    printf '%s' "${CACHED_TOKEN}"
    exit 0
  fi
fi

# ─── Generate JWT (RS256, 10-min expiry, 60s clock skew tolerance) ─────────
b64url() {
  # base64url encode (no padding) — portable across macOS/Linux.
  # `-A` keeps output on one line; `tr -d '\n'` guards against OpenSSL
  # builds/inputs that still emit newlines (would otherwise break the JWT).
  openssl base64 -A | tr -d '\n' | tr '+/' '-_' | tr -d '='
}

IAT=$((NOW_EPOCH - 60))   # 60s back to tolerate clock skew
EXP=$((NOW_EPOCH + 600))  # 10-min expiry (GitHub max)

HEADER=$(printf '{"alg":"RS256","typ":"JWT"}' | b64url)
PAYLOAD=$(printf '{"iat":%d,"exp":%d,"iss":"%s"}' \
  "${IAT}" "${EXP}" "${AHRENA_WARRIOR_ARGOS_GH_APP_ID}" | b64url)

SIGNATURE=$(printf '%s.%s' "${HEADER}" "${PAYLOAD}" | \
  openssl dgst -sha256 -sign "${PRIVATE_KEY_PATH}" | b64url)

# Erase the Keychain-sourced PEM tempfile immediately after signing. The
# JWT exchange below uses the resulting signature; the key material is no
# longer needed in this run.
if [[ -n "${KEYCHAIN_TMP_KEY}" ]]; then
  rm -f "${KEYCHAIN_TMP_KEY}"
  KEYCHAIN_TMP_KEY=""
fi

JWT="${HEADER}.${PAYLOAD}.${SIGNATURE}"

# ─── Exchange JWT for installation token ───────────────────────────────────
# Capture body + HTTP status so transport errors (4xx/5xx) are distinguished
# from a malformed-but-200 response.
HTTP_RESPONSE=$(curl -sS \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ${JWT}" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -w '\n%{http_code}' \
  "https://api.github.com/app/installations/${AHRENA_WARRIOR_ARGOS_GH_INSTALLATION_ID}/access_tokens")

HTTP_CODE=$(printf '%s' "${HTTP_RESPONSE}" | tail -n1)
RESPONSE=$(printf '%s' "${HTTP_RESPONSE}" | sed '$d')

if [[ "${HTTP_CODE}" != "201" ]]; then
  echo "ERROR: GitHub returned HTTP ${HTTP_CODE} when minting installation token:" >&2
  echo "${RESPONSE}" | jq . >&2 2>/dev/null || echo "${RESPONSE}" >&2
  exit 1
fi

TOKEN=$(echo "${RESPONSE}" | jq -r '.token // empty')
EXPIRES_AT=$(echo "${RESPONSE}" | jq -r '.expires_at // empty')

if [[ -z "${TOKEN}" || -z "${EXPIRES_AT}" ]]; then
  echo "ERROR: GitHub returned HTTP 201 but response missing token/expires_at:" >&2
  echo "${RESPONSE}" | jq . >&2 2>/dev/null || echo "${RESPONSE}" >&2
  exit 1
fi

# Convert ISO 8601 expires_at to epoch (portable: macOS BSD date + GNU date)
if date -u -d "${EXPIRES_AT}" +%s >/dev/null 2>&1; then
  EXPIRES_AT_EPOCH=$(date -u -d "${EXPIRES_AT}" +%s)
else
  # macOS BSD date
  EXPIRES_AT_EPOCH=$(date -u -j -f "%Y-%m-%dT%H:%M:%SZ" "${EXPIRES_AT}" +%s)
fi

# ─── Cache the token (atomic: write to tempfile with 0600, then rename) ────
# Avoids a window where the cache file briefly has default mode before chmod;
# also serializes concurrent invocations cleanly (mv is atomic on POSIX).
mkdir -p "${CACHE_DIR}"
TMP_CACHE=$(mktemp "${CACHE_DIR}/.installation-token.XXXXXX")
chmod 600 "${TMP_CACHE}"
# Cleanup of TMP_CACHE on abnormal exit is handled by the unified EXIT trap
# set at script top. On the happy path, mv -f below consumes the tempfile
# and TMP_CACHE is cleared so the trap becomes a no-op for it.

jq -n \
  --arg token "${TOKEN}" \
  --arg expires_at "${EXPIRES_AT}" \
  --argjson expires_at_epoch "${EXPIRES_AT_EPOCH}" \
  --arg app_id "${AHRENA_WARRIOR_ARGOS_GH_APP_ID}" \
  --arg installation_id "${AHRENA_WARRIOR_ARGOS_GH_INSTALLATION_ID}" \
  --argjson minted_at_epoch "${NOW_EPOCH}" \
  '{token: $token, expires_at: $expires_at, expires_at_epoch: $expires_at_epoch,
    app_id: $app_id, installation_id: $installation_id,
    minted_at_epoch: $minted_at_epoch}' \
  > "${TMP_CACHE}"

mv -f "${TMP_CACHE}" "${CACHE_FILE}"
TMP_CACHE=""  # consumed; EXIT trap becomes a no-op for this var

printf '%s' "${TOKEN}"
