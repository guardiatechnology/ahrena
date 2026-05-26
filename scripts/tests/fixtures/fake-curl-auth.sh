#!/usr/bin/env bash
# fake-curl-auth.sh — drop-in `curl` stub used by scripts/tests/test_ahrena_auth_xtrace.py.
#
# scripts/ahrena-auth.sh invokes curl in a different shape than
# scripts/ahrena-api-commit.sh:
#
#   curl -sS -X POST -H "Accept: ..." -H "Authorization: Bearer <JWT>" \
#        -H "X-GitHub-Api-Version: ..." -w '\n%{http_code}' <URL>
#
# Note: NO `-o <out_file>`. The body is written to stdout, followed by a
# newline, followed by the HTTP status code. The script under test
# captures the whole thing with command substitution and parses via
# `tail -n1` (status) + `sed '$d'` (body).
#
# Behavior:
#   - Read URL from argv (first non-flag token).
#   - Dispatch on URL:
#       * /app/installations/*/access_tokens → return synthetic token JSON
#         + HTTP 201
#       * /users/*%5Bbot%5D → return synthetic user JSON + HTTP 200
#   - Body goes to stdout, then a literal newline, then the status code,
#     mimicking `-w '\n%{http_code}'`.
#   - Log every call (redacted) to FAKE_CURL_STATE_DIR/calls.log so the
#     test can assert the script reached the expected endpoints.
#
# Token-redaction self-check: if the Authorization bearer matches
# FAKE_CURL_TOKEN_REDACT_GUARD, append a sentinel to auth-guard.log.

set -uo pipefail

STATE_DIR="${FAKE_CURL_STATE_DIR:?FAKE_CURL_STATE_DIR must be set}"
mkdir -p "${STATE_DIR}"

LOG_FILE="${STATE_DIR}/calls.log"
IDX_FILE="${STATE_DIR}/idx"

if [[ -f "${IDX_FILE}" ]]; then
  IDX=$(cat "${IDX_FILE}")
else
  IDX=0
fi
IDX=$((IDX + 1))
echo "${IDX}" > "${IDX_FILE}"

# Parse argv to extract method, URL, auth header.
METHOD="GET"
URL=""
AUTH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -X)
      METHOD="$2"
      shift 2
      ;;
    -H)
      header="$2"
      case "${header}" in
        "Authorization: Bearer "*) AUTH="${header#Authorization: Bearer }" ;;
      esac
      shift 2
      ;;
    -w)
      shift 2
      ;;
    -sS)
      shift 1
      ;;
    *)
      if [[ -z "${URL}" ]]; then
        URL="$1"
      fi
      shift
      ;;
  esac
done

# Token-leak guard.
if [[ -n "${FAKE_CURL_TOKEN_REDACT_GUARD:-}" && "${AUTH}" == "${FAKE_CURL_TOKEN_REDACT_GUARD}" ]]; then
  echo "AUTH_GUARD_MATCHED" >> "${STATE_DIR}/auth-guard.log"
fi

# Log the call (redacted — token never written).
{
  printf 'call=%d method=%s url=%s auth_present=%s\n' \
    "${IDX}" "${METHOD}" "${URL}" \
    "$([[ -n "${AUTH}" ]] && echo yes || echo no)"
} >> "${LOG_FILE}"

# Dispatch on URL pattern, mimic the GitHub responses ahrena-auth.sh
# expects. Body to stdout, then `\n%{http_code}`.
case "${URL}" in
  *"/app/installations/"*"/access_tokens"*)
    # Mint installation token response. Token value MUST be obviously
    # synthetic so any leak is impossible to confuse with a real token.
    BODY='{"token":"ghs_FAKE_FOR_TEST_DO_NOT_USE","expires_at":"2099-12-31T23:59:59Z"}'
    STATUS="201"
    ;;
  *"/users/"*"%5Bbot%5D"*)
    # Resolve the bot user id. Synthetic numeric id.
    BODY='{"id":99999999,"login":"ahrena-bot[bot]"}'
    STATUS="200"
    ;;
  *)
    BODY='{"message":"unexpected URL in fake-curl-auth"}'
    STATUS="404"
    ;;
esac

printf '%s\n%s' "${BODY}" "${STATUS}"
exit 0
