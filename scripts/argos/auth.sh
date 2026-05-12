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

# ─── Paths ─────────────────────────────────────────────────────────────────
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "${SCRIPT_DIR}/../.." && pwd )"
ENV_FILE="${REPO_ROOT}/.env.local"
CACHE_DIR="${REPO_ROOT}/.ahrena/argos"
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
: "${AHRENA_WARRIOR_ARGOS_GH_PRIVATE_KEY_PATH:?missing AHRENA_WARRIOR_ARGOS_GH_PRIVATE_KEY_PATH}"

# Expand ~/ in private key path
PRIVATE_KEY_PATH="${AHRENA_WARRIOR_ARGOS_GH_PRIVATE_KEY_PATH/#\~/$HOME}"

if [[ ! -r "${PRIVATE_KEY_PATH}" ]]; then
  echo "ERROR: private key not readable at ${PRIVATE_KEY_PATH}" >&2
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

  if [[ -n "${CACHED_TOKEN}" && \
        "${CACHED_APP_ID}" == "${AHRENA_WARRIOR_ARGOS_GH_APP_ID}" && \
        $((CACHED_EXPIRES_AT - NOW_EPOCH)) -gt "${REFRESH_THRESHOLD}" ]]; then
    printf '%s' "${CACHED_TOKEN}"
    exit 0
  fi
fi

# ─── Generate JWT (RS256, 10-min expiry, 60s clock skew tolerance) ─────────
b64url() {
  # base64url encode (no padding) — portable across macOS/Linux
  openssl base64 -A | tr '+/' '-_' | tr -d '='
}

IAT=$((NOW_EPOCH - 60))   # 60s back to tolerate clock skew
EXP=$((NOW_EPOCH + 600))  # 10-min expiry (GitHub max)

HEADER=$(printf '{"alg":"RS256","typ":"JWT"}' | b64url)
PAYLOAD=$(printf '{"iat":%d,"exp":%d,"iss":"%s"}' \
  "${IAT}" "${EXP}" "${AHRENA_WARRIOR_ARGOS_GH_APP_ID}" | b64url)

SIGNATURE=$(printf '%s.%s' "${HEADER}" "${PAYLOAD}" | \
  openssl dgst -sha256 -sign "${PRIVATE_KEY_PATH}" | b64url)

JWT="${HEADER}.${PAYLOAD}.${SIGNATURE}"

# ─── Exchange JWT for installation token ───────────────────────────────────
RESPONSE=$(curl -sS \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ${JWT}" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/app/installations/${AHRENA_WARRIOR_ARGOS_GH_INSTALLATION_ID}/access_tokens")

TOKEN=$(echo "${RESPONSE}" | jq -r '.token // empty')
EXPIRES_AT=$(echo "${RESPONSE}" | jq -r '.expires_at // empty')

if [[ -z "${TOKEN}" || -z "${EXPIRES_AT}" ]]; then
  echo "ERROR: failed to mint installation token. GitHub response:" >&2
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

# ─── Cache the token ───────────────────────────────────────────────────────
mkdir -p "${CACHE_DIR}"
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
  > "${CACHE_FILE}"
chmod 600 "${CACHE_FILE}"

printf '%s' "${TOKEN}"
