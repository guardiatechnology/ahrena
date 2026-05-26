#!/usr/bin/env bash
# fake-security.sh — drop-in `security` stub used by
# scripts/tests/test_ahrena_auth_keychain.py.
#
# scripts/ahrena-auth.sh invokes the macOS `security` CLI in two shapes:
#
#   1. Existence probe:
#        security find-generic-password -s <service> -a <account> -w >/dev/null 2>&1
#      The script discards stdout/stderr and reads the exit code; a
#      successful probe means the entry exists in the Keychain.
#
#   2. Value extraction:
#        security find-generic-password -s <service> -a <account> -w 2>/dev/null
#      The `-w` flag asks `security` to print ONLY the password value
#      to stdout. The script captures it via command substitution.
#
# This stub serves both shapes from a per-test state directory:
#
#   ${FAKE_SECURITY_STATE_DIR}/entries/{service}
#
# When the file exists, exit 0 and (when `-w` is requested) print its
# content to stdout. When the file does not exist, exit 44 (the same
# exit code real `security` uses for "item not found") with no output.
#
# Every invocation is recorded to ${FAKE_SECURITY_STATE_DIR}/calls.log so
# the test can assert which lookups happened (and that the script did
# NOT query Keychain when a variable was already in env).
#
# Token-leak guard: when `xtrace` is inherited by the child invocation,
# the value printed by `-w` MUST stay below the xtrace defense at the
# script level — the stub itself does not toggle xtrace; the protection
# lives in the caller (`scripts/ahrena-auth.sh` activated path).

set -uo pipefail

STATE_DIR="${FAKE_SECURITY_STATE_DIR:?FAKE_SECURITY_STATE_DIR must be set}"
ENTRIES_DIR="${STATE_DIR}/entries"
LOG_FILE="${STATE_DIR}/calls.log"
mkdir -p "${ENTRIES_DIR}"

# Real `security` accepts arbitrary subcommand order. We support the
# single subcommand the auth script uses: `find-generic-password`.
SUBCOMMAND=""
SERVICE=""
ACCOUNT=""
WANT_VALUE=0

# Parse argv. Skip any leading flag the script may emit before the
# subcommand (none today, but the parser is defensive).
while [[ $# -gt 0 ]]; do
  case "$1" in
    find-generic-password)
      SUBCOMMAND="find-generic-password"
      shift
      ;;
    -s)
      SERVICE="$2"
      shift 2
      ;;
    -a)
      ACCOUNT="$2"
      shift 2
      ;;
    -w)
      WANT_VALUE=1
      shift
      ;;
    *)
      shift
      ;;
  esac
done

# Log the call (service + account; the value, if returned, is NOT logged
# — same redaction discipline as fake-curl-auth.sh).
{
  printf 'subcommand=%s service=%s account=%s want_value=%s\n' \
    "${SUBCOMMAND}" "${SERVICE}" "${ACCOUNT}" "${WANT_VALUE}"
} >> "${LOG_FILE}"

if [[ "${SUBCOMMAND}" != "find-generic-password" ]]; then
  echo "fake-security: unsupported subcommand '${SUBCOMMAND}'" >&2
  exit 50
fi

if [[ -z "${SERVICE}" ]]; then
  echo "fake-security: missing -s <service>" >&2
  exit 50
fi

ENTRY_FILE="${ENTRIES_DIR}/${SERVICE}"

if [[ ! -f "${ENTRY_FILE}" ]]; then
  # Real `security` exits 44 ("SecKeychainSearchCopyNext: The specified
  # item could not be found in the keychain") when the entry is absent.
  # Print nothing — the auth script reads stdout via command substitution
  # and tolerates an empty result.
  exit 44
fi

# Entry exists. The auth script's existence probe ignores stdout via
# `>/dev/null 2>&1` so we can unconditionally cat the value when `-w`
# is set; when `-w` is absent (defensive — the auth script always sets
# it), exit 0 silently.
if [[ "${WANT_VALUE}" == "1" ]]; then
  cat "${ENTRY_FILE}"
fi
exit 0
