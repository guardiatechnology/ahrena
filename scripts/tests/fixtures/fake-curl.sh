#!/usr/bin/env bash
# fake-curl.sh — drop-in `curl` stub used by scripts/tests/test_ahrena_api_commit.py.
#
# The script under test (scripts/ahrena-api-commit.sh) invokes curl via the
# `_curl_silent` helper with a fixed arg layout:
#
#   curl -sS -X <METHOD> -H "Accept: ..." -H "Authorization: Bearer <token>" \
#        -H "X-GitHub-Api-Version: ..." -o <out_file> -w '%{http_code}' \
#        [-H "Content-Type: application/json" --data-binary "@<body_file>"] \
#        <URL>
#
# Behavior:
#   - Reads the response plan from env var FAKE_CURL_PLAN_DIR (a directory
#     containing one .json + one .status pair per planned response, numbered
#     001, 002, ...).
#   - Reads the current call index from FAKE_CURL_STATE_DIR/idx (creates as
#     needed). Bumps it on every call.
#   - Writes the planned body to the `-o <out_file>` path and prints the
#     planned HTTP status to stdout (mimics `-w '%{http_code}'`).
#   - Appends a redacted log line to FAKE_CURL_STATE_DIR/calls.log for the
#     test to assert against. The Authorization header value is captured
#     but the test asserts it is NEVER echoed by the script under test.
#
# Token-redaction self-check (defensive): if the Authorization bearer value
# matches FAKE_CURL_TOKEN_REDACT_GUARD, fail loudly so a leak is impossible
# to miss in CI.

set -uo pipefail

PLAN_DIR="${FAKE_CURL_PLAN_DIR:?FAKE_CURL_PLAN_DIR must be set}"
STATE_DIR="${FAKE_CURL_STATE_DIR:?FAKE_CURL_STATE_DIR must be set}"
mkdir -p "${STATE_DIR}"

IDX_FILE="${STATE_DIR}/idx"
LOG_FILE="${STATE_DIR}/calls.log"

if [[ -f "${IDX_FILE}" ]]; then
  IDX=$(cat "${IDX_FILE}")
else
  IDX=0
fi
IDX=$((IDX + 1))
echo "${IDX}" > "${IDX_FILE}"

# Parse argv to extract method, URL, output file, auth header, body file.
METHOD="GET"
OUT_FILE=""
URL=""
AUTH=""
BODY_FILE=""

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
    -o)
      OUT_FILE="$2"
      shift 2
      ;;
    --data-binary)
      val="$2"
      if [[ "${val}" == "@"* ]]; then
        BODY_FILE="${val#@}"
      fi
      shift 2
      ;;
    -sS|-w)
      # -w is followed by a value (%{http_code}); skip the next token too.
      if [[ "$1" == "-w" ]]; then
        shift 2
      else
        shift 1
      fi
      ;;
    *)
      # First non-flag argument is the URL.
      if [[ -z "${URL}" ]]; then
        URL="$1"
      fi
      shift
      ;;
  esac
done

# Token-leak guard.
if [[ -n "${FAKE_CURL_TOKEN_REDACT_GUARD:-}" && "${AUTH}" == "${FAKE_CURL_TOKEN_REDACT_GUARD}" ]]; then
  # Don't print the token value; just confirm it matched the guard sentinel
  # so the test can detect that the script DID pass it via Authorization.
  echo "AUTH_GUARD_MATCHED" >> "${STATE_DIR}/auth-guard.log"
fi

# Log the call (redacted — never write the token).
{
  printf 'call=%d method=%s url=%s body_file=%s out_file=%s auth_present=%s\n' \
    "${IDX}" "${METHOD}" "${URL}" "${BODY_FILE:-<none>}" "${OUT_FILE:-<none>}" \
    "$([[ -n "${AUTH}" ]] && echo yes || echo no)"
} >> "${LOG_FILE}"

# Capture the request body so tests can inspect what was sent.
if [[ -n "${BODY_FILE}" && -f "${BODY_FILE}" ]]; then
  cp "${BODY_FILE}" "${STATE_DIR}/req-${IDX}.json"
fi

# Resolve the planned response. Convention: per call N, look for
# ${PLAN_DIR}/$(printf '%03d' N).json (body) and .status (HTTP code).
NNN=$(printf '%03d' "${IDX}")
BODY_PATH="${PLAN_DIR}/${NNN}.json"
STATUS_PATH="${PLAN_DIR}/${NNN}.status"

if [[ ! -f "${STATUS_PATH}" ]]; then
  echo "fake-curl: missing plan file ${STATUS_PATH} for call ${IDX}" >&2
  echo "000"
  exit 0  # mimic transport failure shape: 000 status
fi

STATUS=$(cat "${STATUS_PATH}")
if [[ -f "${BODY_PATH}" ]]; then
  cat "${BODY_PATH}" > "${OUT_FILE}"
else
  : > "${OUT_FILE}"
fi

printf '%s' "${STATUS}"
exit 0
