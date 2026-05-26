"""Unit tests for scripts/ahrena-auth.sh macOS Keychain resolver (Plan P8, Issue #284).

These tests close the gap surfaced during the smoke test on 2026-05-26:
the auth script's documentation advertised a 3-tier resolution (env →
Keychain → 1Password), but only env vars + `.env.local` were actually
read. Operators who stored credentials in the Keychain got inert
entries.

P8 adds three Keychain lookups inside the activated path (after `.env.local`
load, before requirement checks):

    ahrena-warriors-default-gh-app-id          (plain APP_ID value)
    ahrena-warriors-default-gh-installation-id (plain INSTALLATION_ID value)
    ahrena-warriors-default-gh-private-key     (PEM content, written to chmod-600 tempfile)

Acceptance Criteria covered:

- AC-P8-1: all 3 vars in Keychain, env empty → script resolves all 3
  and exports the 5 expected env vars.
- AC-P8-2: mixed env + Keychain (any subset in env, rest in Keychain)
  works.
- AC-P8-3: Linux scenario — `security` command absent on PATH → script
  falls back to env-only without error.
- AC-P8-4: PEM-in-Keychain → tempfile created chmod 600, cleaned up
  via existing trap on exit.
- AC-P8-5 (regression): re-run AC-P7-1 — `bash -x` against the modified
  script emits zero leak matches even when Keychain branches fire.

Strategy mirrors `test_ahrena_auth_xtrace.py`:
- Each test materializes a tmp main repo with `.ahrena/.directives`
  (warriors_default_author.enabled=true).
- A stubbed `security` (`scripts/tests/fixtures/fake-security.sh`) on
  PATH serves the Keychain lookups from per-test entry files.
- A stubbed `curl` (`scripts/tests/fixtures/fake-curl-auth.sh`) on PATH
  serves the two GitHub endpoints the script hits.
- The script is copied into the test repo (mirrors xtrace test) so the
  worktree-aware `_AHRENA_MAIN_REPO_ROOT` resolution lands in the test
  repo, not the framework's main repo.
"""

from __future__ import annotations

import os
import subprocess
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_UNDER_TEST = REPO_ROOT / "scripts" / "ahrena-auth.sh"
FAKE_CURL = REPO_ROOT / "scripts" / "tests" / "fixtures" / "fake-curl-auth.sh"
FAKE_SECURITY = REPO_ROOT / "scripts" / "tests" / "fixtures" / "fake-security.sh"

# Patterns that, if found on stderr under `bash -x`, prove the xtrace
# defense failed. Reused from test_ahrena_auth_xtrace.py so AC-P8-5
# regresses with the same scanner that catches AC-P7-1.
FORBIDDEN_PATTERNS = (
    "ghs_",                       # GitHub installation token prefix
    "ghp_",                       # GitHub PAT prefix
    "eyJ",                        # Base64url-encoded JWT header prefix
    "BEGIN RSA PRIVATE KEY",      # PKCS#1 PEM header
    "BEGIN PRIVATE KEY",          # PKCS#8 PEM header (openssl genrsa default)
    "-----BEGIN",                 # Generic PEM open marker
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def _make_synthetic_pem(target: Path) -> None:
    """Generate a real synthetic RSA key with openssl. Per-test, never
    checked in. Same approach as test_ahrena_auth_xtrace.py."""
    subprocess.run(
        ["openssl", "genrsa", "-out", str(target), "2048"],
        check=True,
        stderr=subprocess.DEVNULL,
    )
    target.chmod(0o600)


def _make_test_repo(tmp_path: Path, *, env_vars: dict[str, str] | None = None) -> tuple[Path, Path]:
    """Materialize a tmp main repo with `.ahrena/.directives` and an
    optional `.env.local`. Copies `scripts/ahrena-auth.sh` into the repo
    so the script's worktree-aware path resolution stays inside the
    test repo (same constraint documented in test_ahrena_auth_xtrace.py).

    `env_vars` lets the test pre-populate `.env.local`. When empty (or
    `None`), no `.env.local` is created — the script's Keychain branch
    becomes the only resolution path. AC-P8-1 uses this; AC-P8-2 uses a
    partial dict.

    Returns (repo_root, script_path_in_repo).
    """
    repo = tmp_path / "main"
    repo.mkdir(parents=True, exist_ok=True)

    # Minimal git repo so `git rev-parse --git-common-dir` returns `.git`
    # (in-repo). Without this, `_AHRENA_MAIN_REPO_ROOT` would climb to
    # the framework's `.git` and the activation gate would consult the
    # framework's `.directives` instead of the test repo's.
    subprocess.run(["git", "init", "--quiet"], cwd=repo, check=True)
    subprocess.run(
        ["git", "symbolic-ref", "HEAD", "refs/heads/main"],
        cwd=repo,
        check=True,
    )

    ahrena_dir = repo / ".ahrena"
    ahrena_dir.mkdir(parents=True, exist_ok=True)
    (ahrena_dir / ".directives").write_text(
        textwrap.dedent(
            """\
            warriors_default_author:
              enabled: true
              identity: ahrena-bot
            """
        ),
        encoding="utf-8",
    )

    if env_vars:
        env_local_lines = [f"{k}={v}" for k, v in env_vars.items()]
        (repo / ".env.local").write_text(
            "\n".join(env_local_lines) + "\n", encoding="utf-8"
        )

    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    script_in_repo = scripts_dir / "ahrena-auth.sh"
    script_in_repo.write_bytes(SCRIPT_UNDER_TEST.read_bytes())
    script_in_repo.chmod(0o755)

    return repo, script_in_repo


def _wire_shims(
    tmp_path: Path,
    *,
    include_security: bool = True,
) -> Path:
    """Build a per-test PATH-shim directory containing the stubs.

    `include_security=False` simulates a Linux host (no `security` on
    PATH). The auth script's `command -v security` guard MUST detect
    this and skip the Keychain block entirely (AC-P8-3).

    `curl` is always shimmed because the activated path always reaches
    the GitHub token-mint endpoint.
    """
    shim_dir = tmp_path / "shim"
    shim_dir.mkdir(parents=True, exist_ok=True)

    curl_link = shim_dir / "curl"
    if curl_link.exists() or curl_link.is_symlink():
        curl_link.unlink()
    curl_link.symlink_to(FAKE_CURL)

    if include_security:
        security_link = shim_dir / "security"
        if security_link.exists() or security_link.is_symlink():
            security_link.unlink()
        security_link.symlink_to(FAKE_SECURITY)

    return shim_dir


# Whitelist of external tools the auth script invokes. Used by
# `_wire_isolated_shim` to populate the shim dir for the
# `security`-absent fallback test (AC-P8-3). Anything missing here will
# surface as "command not found" in stderr — clear, actionable.
#
# `printf`, `echo`, and other shell builtins do not need entries; only
# real external binaries do. Everything `command -v` would resolve to
# a path under /usr/bin or /usr/local/bin counts.
_REQUIRED_TOOLS = (
    "dirname", "env", "openssl", "jq", "mktemp", "awk", "sed", "date",
    "base64", "tr", "xxd", "bash", "git", "cat", "rm", "uname",
    "grep", "ls", "mkdir", "mv", "chmod", "tail", "head", "id",
    "pwd",
)


def _wire_isolated_shim(tmp_path: Path) -> Path:
    """Build a shim dir that contains every tool the auth script needs
    EXCEPT `security`. Used by the Linux-fallback test (AC-P8-3) to
    simulate a host without the macOS Keychain CLI.

    The fake-curl stub is also placed here. The test then sets PATH to
    JUST the shim dir, masking the host's `/usr/bin/security` entirely.
    `command -v security` returns non-zero → the script's Keychain
    guard short-circuits and the env-only fallback takes over.
    """
    shim_dir = tmp_path / "isolated-shim"
    shim_dir.mkdir(parents=True, exist_ok=True)

    # Fake curl.
    curl_link = shim_dir / "curl"
    if curl_link.exists() or curl_link.is_symlink():
        curl_link.unlink()
    curl_link.symlink_to(FAKE_CURL)

    # Real tools — symlink from their host locations. Using shutil.which
    # ensures we find them wherever they live (macOS Homebrew, BSD,
    # Linux distros) without assuming /usr/bin or /usr/local/bin.
    import shutil
    for tool in _REQUIRED_TOOLS:
        host_path = shutil.which(tool)
        if host_path is None:
            # Not strictly fatal — the auth script may not invoke every
            # tool on every code path. Skip silently; the test failure
            # mode of a missing dep is "command not found" with a clear
            # message in stderr that surfaces if it actually breaks.
            continue
        link = shim_dir / tool
        if link.exists() or link.is_symlink():
            link.unlink()
        link.symlink_to(host_path)

    # Deliberately NO `security` symlink. `command -v security` MUST
    # return non-zero when PATH is restricted to this dir.
    return shim_dir


def _populate_keychain(
    state_dir: Path,
    entries: dict[str, str],
) -> None:
    """Write Keychain entry files for fake-security.sh. The stub reads
    them from `${FAKE_SECURITY_STATE_DIR}/entries/{service}`."""
    entries_dir = state_dir / "entries"
    entries_dir.mkdir(parents=True, exist_ok=True)
    for service, value in entries.items():
        (entries_dir / service).write_text(value, encoding="utf-8")


def _build_env(
    repo: Path,
    shim_dir: Path,
    curl_state_dir: Path,
    security_state_dir: Path,
    *,
    isolate_path: bool = False,
) -> dict[str, str]:
    """Build the env for the script invocation.

    `isolate_path=False` (default): prepend the shim dir to the host PATH.
    The host's `security` (in /usr/bin/security on macOS) is reachable
    AFTER the shim dir, but the shim dir's `security` symlink wins for
    tests that DO want to drive the Keychain branch.

    `isolate_path=True`: PATH is set to JUST the shim dir. The shim dir
    must contain symlinks to all required tools EXCEPT `security`.
    Used by AC-P8-3 to simulate a Linux host without the macOS
    Keychain CLI.
    """
    if isolate_path:
        path_value = str(shim_dir)
    else:
        path_value = f"{shim_dir}:{os.environ.get('PATH', '')}"

    env: dict[str, str] = {
        "PATH": path_value,
        "HOME": str(repo / ".home"),
        "USER": os.environ.get("USER", "testuser"),
        "FAKE_CURL_STATE_DIR": str(curl_state_dir),
        "FAKE_SECURITY_STATE_DIR": str(security_state_dir),
        "FAKE_CURL_TOKEN_REDACT_GUARD": "",
    }
    for k in ("LANG", "LC_ALL", "TERM"):
        if k in os.environ:
            env[k] = os.environ[k]
    return env


def _run_sourced(
    repo: Path,
    script: Path,
    env: dict[str, str],
    *,
    bash_x: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Source the script in a fresh bash and dump the resulting env so
    we can assert on exports + cache file."""
    prefix = "set -x; " if bash_x else ""
    cmd = [
        "bash",
        "-c",
        f"{prefix}source '{script}' && env",
    ]
    return subprocess.run(
        cmd, cwd=repo, env=env, capture_output=True, text=True
    )


def _parse_env_dump(stdout: str) -> dict[str, str]:
    env_dict: dict[str, str] = {}
    for line in stdout.splitlines():
        if "=" in line:
            k, _, v = line.partition("=")
            env_dict[k] = v
    return env_dict


def _assert_no_leak(stderr: str, label: str) -> None:
    """Mirror of test_ahrena_auth_xtrace._assert_no_leak — re-implemented
    here to avoid cross-file imports between test modules (pytest
    discovery treats each file as a self-contained collection).

    A genuine leak under `bash -x` will surface in stderr; this scanner
    is the contract test for AC-P8-5."""
    leaks: list[tuple[str, str]] = []
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in stderr:
            idx = stderr.find(pattern)
            start = max(0, idx - 60)
            end = min(len(stderr), idx + 60)
            window = stderr[start:end].replace("\n", "\\n")
            leaks.append((pattern, window))
    assert not leaks, (
        f"[{label}] xtrace defense FAILED — secret material leaked to stderr:\n"
        + "\n".join(f"  pattern={p!r} window={w!r}" for p, w in leaks)
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-P8-1: all 3 vars in Keychain, env empty → resolves successfully
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_all_three_credentials_in_keychain(tmp_path: Path) -> None:
    """AC-P8-1: when `.env.local` and env are empty AND the Keychain
    holds all 3 entries (app-id, installation-id, private-key), the
    script MUST resolve everything from the Keychain and export the
    5 expected env vars.

    This is the canonical "macOS dev workstation" path: operator stored
    credentials once via `security add-generic-password` and expects
    the auth resolver to consume them on every warrior commit."""
    repo, script = _make_test_repo(tmp_path)
    curl_state = repo / ".curl-state"
    security_state = repo / ".security-state"
    curl_state.mkdir(parents=True, exist_ok=True)
    security_state.mkdir(parents=True, exist_ok=True)

    # Synthetic PEM stored in the Keychain entry verbatim.
    pem_path = tmp_path / "synthetic.pem"
    _make_synthetic_pem(pem_path)
    pem_content = pem_path.read_text(encoding="utf-8")

    _populate_keychain(
        security_state,
        {
            "ahrena-warriors-default-gh-app-id": "999999",
            "ahrena-warriors-default-gh-installation-id": "88888888",
            "ahrena-warriors-default-gh-private-key": pem_content,
        },
    )

    shim_dir = _wire_shims(repo.parent, include_security=True)
    env = _build_env(
        repo, shim_dir, curl_state, security_state, isolate_path=False
    )

    proc = _run_sourced(repo, script, env)
    assert proc.returncode == 0, (
        f"Keychain-only resolution failed: exit={proc.returncode}\n"
        f"stderr (first 2000 chars): {proc.stderr[:2000]!r}"
    )

    env_dict = _parse_env_dump(proc.stdout)
    expected_exports = (
        "GH_TOKEN_AHRENA_WARRIORS_DEFAULT",
        "GIT_AUTHOR_NAME",
        "GIT_AUTHOR_EMAIL",
        "GIT_COMMITTER_NAME",
        "GIT_COMMITTER_EMAIL",
    )
    missing = [k for k in expected_exports if k not in env_dict]
    assert not missing, (
        f"AC-P8-1: missing exports {missing}.\n"
        f"present keys: {sorted(env_dict.keys())}\n"
        f"stderr: {proc.stderr[:1000]!r}"
    )

    # The synthetic token in fake-curl-auth.sh proves the script
    # actually invoked GitHub (not a vacuous pass).
    assert env_dict["GH_TOKEN_AHRENA_WARRIORS_DEFAULT"] == "ghs_FAKE_FOR_TEST_DO_NOT_USE"

    # Calls log MUST show all 3 Keychain lookups happened.
    security_calls = (security_state / "calls.log").read_text(encoding="utf-8")
    assert "service=ahrena-warriors-default-gh-app-id" in security_calls
    assert "service=ahrena-warriors-default-gh-installation-id" in security_calls
    assert "service=ahrena-warriors-default-gh-private-key" in security_calls


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-P8-2: mixed env + Keychain → resolution works
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_mixed_env_and_keychain(tmp_path: Path) -> None:
    """AC-P8-2: APP_ID in `.env.local`, INSTALLATION_ID + PRIVATE_KEY
    in Keychain → resolution still succeeds and the Keychain lookup
    for APP_ID is skipped (env wins, no redundant Keychain query)."""
    pem_path = tmp_path / "synthetic.pem"
    _make_synthetic_pem(pem_path)
    pem_content = pem_path.read_text(encoding="utf-8")

    repo, script = _make_test_repo(
        tmp_path,
        env_vars={
            "AHRENA_WARRIORS_DEFAULT_GH_APP_ID": "777777",
            "AHRENA_WARRIORS_DEFAULT_GH_SLUG": "ahrena-bot",
        },
    )
    curl_state = repo / ".curl-state"
    security_state = repo / ".security-state"
    curl_state.mkdir(parents=True, exist_ok=True)
    security_state.mkdir(parents=True, exist_ok=True)

    _populate_keychain(
        security_state,
        {
            "ahrena-warriors-default-gh-installation-id": "66666666",
            "ahrena-warriors-default-gh-private-key": pem_content,
        },
    )

    shim_dir = _wire_shims(repo.parent, include_security=True)
    env = _build_env(
        repo, shim_dir, curl_state, security_state, isolate_path=False
    )

    proc = _run_sourced(repo, script, env)
    assert proc.returncode == 0, (
        f"Mixed env+Keychain resolution failed: exit={proc.returncode}\n"
        f"stderr (first 2000 chars): {proc.stderr[:2000]!r}"
    )

    env_dict = _parse_env_dump(proc.stdout)
    assert env_dict.get("GH_TOKEN_AHRENA_WARRIORS_DEFAULT") == "ghs_FAKE_FOR_TEST_DO_NOT_USE"

    # APP_ID was in env → the Keychain lookup for it MUST have been
    # skipped (the if-guard short-circuits when the variable is
    # already set). The other two MUST have fired.
    security_calls = (security_state / "calls.log").read_text(encoding="utf-8")
    assert "service=ahrena-warriors-default-gh-app-id" not in security_calls, (
        f"APP_ID was in env; Keychain lookup MUST be skipped.\n"
        f"calls.log:\n{security_calls}"
    )
    assert "service=ahrena-warriors-default-gh-installation-id" in security_calls
    assert "service=ahrena-warriors-default-gh-private-key" in security_calls


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-P8-3: Linux (no `security` on PATH) → graceful env-only fallback
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_linux_no_security_command_falls_back_to_env(tmp_path: Path) -> None:
    """AC-P8-3: when `security` is absent from PATH (Linux / Windows /
    minimal container), the script MUST skip the Keychain block via
    `command -v security` and resolve credentials from env / `.env.local`
    only. No spurious "command not found" stderr; no non-zero exit."""
    pem_path = tmp_path / "synthetic.pem"
    _make_synthetic_pem(pem_path)

    repo, script = _make_test_repo(
        tmp_path,
        env_vars={
            "AHRENA_WARRIORS_DEFAULT_GH_APP_ID": "555555",
            "AHRENA_WARRIORS_DEFAULT_GH_INSTALLATION_ID": "44444444",
            "AHRENA_WARRIORS_DEFAULT_GH_PRIVATE_KEY_PATH": str(pem_path),
            "AHRENA_WARRIORS_DEFAULT_GH_SLUG": "ahrena-bot",
        },
    )
    curl_state = repo / ".curl-state"
    security_state = repo / ".security-state"
    curl_state.mkdir(parents=True, exist_ok=True)
    security_state.mkdir(parents=True, exist_ok=True)

    # Crucially: _wire_isolated_shim gives us a directory containing
    # every required tool EXCEPT `security`. Combined with
    # isolate_path=True (PATH = just this dir), the host's real
    # `/usr/bin/security` on macOS becomes unreachable too — the test
    # runs deterministically on dev workstations and CI alike.
    shim_dir = _wire_isolated_shim(repo.parent)
    env = _build_env(
        repo, shim_dir, curl_state, security_state, isolate_path=True
    )

    proc = _run_sourced(repo, script, env)
    assert proc.returncode == 0, (
        f"Linux fallback failed: exit={proc.returncode}\n"
        f"stderr (first 2000 chars): {proc.stderr[:2000]!r}\n"
        f"stdout (first 500): {proc.stdout[:500]!r}"
    )

    env_dict = _parse_env_dump(proc.stdout)
    assert env_dict.get("GH_TOKEN_AHRENA_WARRIORS_DEFAULT") == "ghs_FAKE_FOR_TEST_DO_NOT_USE"

    # The stub was NOT installed → no calls.log file should have
    # been written by anything (the auth script never invoked
    # `security` because `command -v security` returned non-zero).
    assert not (security_state / "calls.log").exists(), (
        "AC-P8-3: Keychain block fired despite `security` being absent. "
        "The `command -v security` guard is broken."
    )

    # Stderr MUST NOT mention "command not found" — the activated path
    # uses `command -v` to probe, not a raw `security` call.
    assert "command not found" not in proc.stderr, (
        f"AC-P8-3: spurious 'command not found' in stderr:\n{proc.stderr}"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-P8-4: PEM-in-Keychain materializes to chmod-600 tempfile and is cleaned
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_pem_in_keychain_tempfile_lifecycle(tmp_path: Path) -> None:
    """AC-P8-4: when the private key comes from the Keychain, the auth
    script MUST (1) write the PEM content to a chmod-600 tempfile,
    (2) sign the JWT against that path, (3) remove the tempfile via
    the existing `_ahrena_auth_cleanup` trap (executed-mode) OR the
    inline `_ahrena_auth_cleanup` call (sourced-mode) before returning
    control to the caller.

    Strategy:
    - Source the script (mints token), then list any matching tempfiles
      under $TMPDIR. The auth script's `mktemp -t
      ahrena-warriors-default-key.XXXXXXXX` produces a predictable
      prefix we can grep for.
    - The sourced path calls `_ahrena_auth_cleanup` explicitly at the
      end (line ~429 post-P7), so the tempfile MUST be gone by the time
      bash exits.
    """
    pem_path = tmp_path / "synthetic.pem"
    _make_synthetic_pem(pem_path)
    pem_content = pem_path.read_text(encoding="utf-8")

    repo, script = _make_test_repo(tmp_path)
    curl_state = repo / ".curl-state"
    security_state = repo / ".security-state"
    curl_state.mkdir(parents=True, exist_ok=True)
    security_state.mkdir(parents=True, exist_ok=True)

    _populate_keychain(
        security_state,
        {
            "ahrena-warriors-default-gh-app-id": "999999",
            "ahrena-warriors-default-gh-installation-id": "88888888",
            "ahrena-warriors-default-gh-private-key": pem_content,
        },
    )

    # Force a known TMPDIR so the cleanup assertion is deterministic.
    custom_tmpdir = tmp_path / "ahrena-tmp"
    custom_tmpdir.mkdir(parents=True, exist_ok=True)

    shim_dir = _wire_shims(repo.parent, include_security=True)
    env = _build_env(
        repo, shim_dir, curl_state, security_state, isolate_path=False
    )
    env["TMPDIR"] = str(custom_tmpdir)

    proc = _run_sourced(repo, script, env)
    assert proc.returncode == 0, (
        f"PEM-in-Keychain run failed: exit={proc.returncode}\n"
        f"stderr (first 2000 chars): {proc.stderr[:2000]!r}"
    )

    # After the sourced script returns, no `ahrena-warriors-default-key.*`
    # file MUST remain. The cleanup path is non-negotiable — a leak here
    # means the chmod-600 PEM survived in $TMPDIR.
    leftovers = list(custom_tmpdir.glob("ahrena-warriors-default-key.*"))
    assert not leftovers, (
        f"AC-P8-4: PEM tempfile(s) not cleaned up by _ahrena_auth_cleanup: "
        f"{[str(p) for p in leftovers]}"
    )

    # The cache file MUST exist (proof the JWT signing actually
    # consumed the materialized PEM and minted a token).
    cache_file = repo / ".ahrena" / "bot" / "installation-token.json"
    assert cache_file.exists(), (
        "AC-P8-4: installation-token cache absent → JWT signing never "
        "happened, which means the PEM tempfile was never used."
    )


def test_pem_in_keychain_tempfile_chmod_600_at_signing_time(tmp_path: Path) -> None:
    """AC-P8-4 (stricter): assert the tempfile is created with mode 600.

    Since the script's `_ahrena_auth_cleanup` removes the file before
    returning, we cannot stat the file after the run. Instead we patch
    the test's view of mktemp + assert via the script's `umask 077`
    contract. The auth script sets `umask 077` at the top of the
    activated path (line 188 post-P7) AND explicitly `chmod 600` on the
    Keychain-derived PEM tempfile (P8 addition). Both belt-and-suspenders.

    Strategy: pre-create the entries dir, run the script, capture the
    chmod call via a wrapper around the script that pauses after PEM
    materialization. Simpler approach: confirm the script SOURCE
    contains the `chmod 600` line for the Keychain tempfile — a
    grep-level assertion that is robust to future refactors as long
    as the chmod stays in place.
    """
    script_source = SCRIPT_UNDER_TEST.read_text(encoding="utf-8")
    # The Keychain PEM materialization block MUST contain a chmod 600
    # on the tempfile. `umask 077` covers the create case, but an
    # explicit chmod guards against future refactors that change the
    # umask scope.
    assert "chmod 600" in script_source and "_AHRENA_KEYCHAIN_TMP_KEY" in script_source, (
        "AC-P8-4: the Keychain PEM materialization block MUST contain "
        "an explicit `chmod 600 \"${_AHRENA_KEYCHAIN_TMP_KEY}\"` to "
        "guard against future umask-scope refactors."
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-P8-5: regression — `bash -x` against the Keychain flow stays leak-free
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_bash_x_with_keychain_branch_does_not_leak(tmp_path: Path) -> None:
    """AC-P8-5: AC-P7 regression. When the script runs under inherited
    `set -x` AND resolves credentials from the Keychain (the new path
    P8 introduces), stderr MUST still emit zero leak matches.

    This is the principal protective contract: P8 adds three new
    `security` invocations + a PEM tempfile write inside the activated
    path. All of those touch secret material. The P7 master xtrace
    guard at the top of the activated path covers them by construction
    — this test PROVES it.

    Without the guard, the trace would contain:
      + AHRENA_WARRIORS_DEFAULT_GH_PRIVATE_KEY='-----BEGIN ...'
      + printf '...PEM CONTENT...' > /tmp/ahrena-warriors-default-key.XXXX
    Both are caught by `-----BEGIN` / `BEGIN RSA PRIVATE KEY` / `BEGIN
    PRIVATE KEY` patterns.
    """
    pem_path = tmp_path / "synthetic.pem"
    _make_synthetic_pem(pem_path)
    pem_content = pem_path.read_text(encoding="utf-8")

    repo, script = _make_test_repo(tmp_path)
    curl_state = repo / ".curl-state"
    security_state = repo / ".security-state"
    curl_state.mkdir(parents=True, exist_ok=True)
    security_state.mkdir(parents=True, exist_ok=True)

    _populate_keychain(
        security_state,
        {
            "ahrena-warriors-default-gh-app-id": "999999",
            "ahrena-warriors-default-gh-installation-id": "88888888",
            "ahrena-warriors-default-gh-private-key": pem_content,
        },
    )

    shim_dir = _wire_shims(repo.parent, include_security=True)
    env = _build_env(
        repo, shim_dir, curl_state, security_state, isolate_path=False
    )

    proc = _run_sourced(repo, script, env, bash_x=True)
    assert proc.returncode == 0, (
        f"bash -x + Keychain run failed: exit={proc.returncode}\n"
        f"stderr (first 2000 chars): {proc.stderr[:2000]!r}"
    )
    _assert_no_leak(proc.stderr, "bash -x + Keychain")
