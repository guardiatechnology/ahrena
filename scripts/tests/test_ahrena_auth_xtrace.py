"""Unit tests for scripts/ahrena-auth.sh xtrace-defense (Plan P7, Issue #283).

These tests close the security gap surfaced during the P5 smoke test on
2026-05-26: running `bash -x scripts/ahrena-auth.sh` printed the App
private key signature material, the JWT, and the resulting installation
token to stderr. P2 introduced the canonical xtrace-defense pattern
(`{ _SAVED=${-//[^x]/}; set +x; } 2>/dev/null` ... restore) for
`scripts/ahrena-api-commit.sh`; this test file enforces the equivalent
guarantees on `scripts/ahrena-auth.sh`.

Acceptance Criteria covered:

- AC-P7-1: `bash -x scripts/ahrena-auth.sh` (stubbed) emits zero stderr
  matches for `ghs_`, `ghp_`, `eyJ`, `BEGIN RSA PRIVATE KEY`,
  `-----BEGIN`.
- AC-P7-2: Inherited `set -x` from caller defends equivalently.
- AC-P7-3: Custom `PS4` override (`PS4='+ $LINENO: '`) does not bypass
  the defense.
- AC-P7-4: Functional behavior unchanged — under normal (no-xtrace)
  invocation the script exits 0 and exports the 5 expected env vars
  (GH_TOKEN_AHRENA_WARRIORS_DEFAULT, GIT_AUTHOR_NAME, GIT_AUTHOR_EMAIL,
  GIT_COMMITTER_NAME, GIT_COMMITTER_EMAIL).

Strategy:
- Each test materializes a tmp main repo with `.ahrena/.directives`
  (warriors_default_author.enabled=true), `.env.local`, and a freshly
  generated synthetic RSA key (so `openssl dgst -sha256 -sign` actually
  succeeds without depending on a static checked-in key).
- A stubbed `curl` (`scripts/tests/fixtures/fake-curl-auth.sh`) on PATH
  serves the two GitHub endpoints the script hits: POST
  `/app/installations/{id}/access_tokens` and GET
  `/users/{slug}%5Bbot%5D`.
- The leak assertion is a pure regex scan over the captured stderr,
  looking for the substrings any real leak would contain: GitHub
  installation-token prefix (`ghs_`), PAT prefix (`ghp_`), JWT prefix
  (`eyJ`), and the literal PEM header / generic `-----BEGIN` marker.
"""

from __future__ import annotations

import os
import subprocess
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_UNDER_TEST = REPO_ROOT / "scripts" / "ahrena-auth.sh"
FAKE_CURL = REPO_ROOT / "scripts" / "tests" / "fixtures" / "fake-curl-auth.sh"

# Patterns that, if found on stderr, prove the xtrace defense failed.
# Each is intentionally narrow to avoid false positives on incidental
# output (error messages, log file paths). Any match = leak.
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
    """Generate a real synthetic RSA key with openssl.

    A static checked-in key would be a magnet for accidental misuse;
    generating per-test ensures the key only ever exists in the test's
    tmp directory and never touches the working tree.
    """
    subprocess.run(
        ["openssl", "genrsa", "-out", str(target), "2048"],
        check=True,
        stderr=subprocess.DEVNULL,
    )
    target.chmod(0o600)


def _make_test_repo(tmp_path: Path) -> tuple[Path, Path]:
    """Materialize a tmp main repo with the directives + env wired for
    activation, plus a stubbed PEM. Also copies `scripts/ahrena-auth.sh`
    into the test repo so the script's worktree-aware path resolution
    (`git rev-parse --git-common-dir` from the script's own directory)
    lands in the TEST repo's `.git`, not in the real framework's `.git`.

    Returns a (repo_root, script_path_in_repo) tuple. Tests MUST use
    the returned script path — not `SCRIPT_UNDER_TEST` directly — so
    the activation gate consults the test repo's `.ahrena/.directives`.
    """
    repo = tmp_path / "main"
    repo.mkdir(parents=True, exist_ok=True)

    # Minimal git repo so `git rev-parse --git-common-dir` returns
    # `.git` (in-repo), which makes _AHRENA_MAIN_REPO_ROOT resolve to
    # `repo` itself instead of climbing into the framework's main repo.
    subprocess.run(["git", "init", "--quiet", "-b", "main"], cwd=repo, check=True)

    # .ahrena/.directives with warriors_default_author.enabled=true.
    # This is the file the script's activation gate reads — when the
    # real `.directives` lacks the section, the no-op path triggers
    # and the activated path is never exercised by the test (silent
    # vacuous pass). Materializing it here drives the script through
    # the protected codepath we actually want to assert on.
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

    # Synthetic PEM in a tmp location outside the repo (mirrors the
    # operator setup: key lives in $HOME/.ssh or similar, not in-repo).
    pem_path = tmp_path / "test-key.pem"
    _make_synthetic_pem(pem_path)

    # .env.local — required env for the activated path.
    (repo / ".env.local").write_text(
        textwrap.dedent(
            f"""\
            AHRENA_WARRIORS_DEFAULT_GH_APP_ID=999999
            AHRENA_WARRIORS_DEFAULT_GH_INSTALLATION_ID=88888888
            AHRENA_WARRIORS_DEFAULT_GH_PRIVATE_KEY_PATH={pem_path}
            AHRENA_WARRIORS_DEFAULT_GH_SLUG=ahrena-bot
            """
        ),
        encoding="utf-8",
    )

    # Copy the script under test into the repo. The script uses
    # `${BASH_SOURCE[0]}` to compute its own location and derives
    # `_AHRENA_MAIN_REPO_ROOT` from there + `git rev-parse
    # --git-common-dir`. Running from outside the repo would make
    # the script consult the framework's `.ahrena/.directives`
    # instead of the test repo's — the activation gate would
    # silently fall through to the no-op path and the test would
    # vacuously pass without ever exercising the defense.
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    script_in_repo = scripts_dir / "ahrena-auth.sh"
    script_in_repo.write_bytes(SCRIPT_UNDER_TEST.read_bytes())
    script_in_repo.chmod(0o755)

    return repo, script_in_repo


def _wire_fake_curl(tmp_path: Path) -> Path:
    """Symlink the fake-curl-auth stub as `curl` in a shim dir; return
    the shim dir (to be prepended to PATH)."""
    shim_dir = tmp_path / "shim"
    shim_dir.mkdir(parents=True, exist_ok=True)
    curl_link = shim_dir / "curl"
    if curl_link.exists() or curl_link.is_symlink():
        curl_link.unlink()
    curl_link.symlink_to(FAKE_CURL)
    return shim_dir


def _build_env(
    repo: Path, shim_dir: Path, state_dir: Path, *, redact_guard: str = ""
) -> dict[str, str]:
    """Build the environment for the script invocation."""
    env: dict[str, str] = {
        # Prepend the shim dir so the script's `curl` resolves to the
        # stub. Preserve the inherited PATH for real `openssl`, `jq`,
        # `mktemp`, `awk`, `sed`, `date`, `base64`, `tr`, `xxd`.
        "PATH": f"{shim_dir}:{os.environ.get('PATH', '')}",
        "HOME": str(repo / ".home"),
        "FAKE_CURL_STATE_DIR": str(state_dir),
        "FAKE_CURL_TOKEN_REDACT_GUARD": redact_guard,
    }
    # Carry locale + terminal hints so the inherited tools behave the
    # same way they would on a dev workstation.
    for k in ("LANG", "LC_ALL", "TERM"):
        if k in os.environ:
            env[k] = os.environ[k]
    # Force the macOS Keychain branch OFF: the script checks `uname -s
    # == Darwin` AND a Keychain lookup; the lookup will simply fail in
    # the test environment, dropping into the file-path branch. No
    # special handling needed beyond leaving the env var set.
    return env


def _run_script(
    repo: Path,
    script: Path,
    *,
    inherit_xtrace: bool = False,
    custom_ps4: str | None = None,
    explicit_xtrace_in_script: bool = False,
    capture_extra_env: dict[str, str] | None = None,
) -> tuple[subprocess.CompletedProcess, Path]:
    """Run the test-repo copy of ahrena-auth.sh under the test repo.

    - `explicit_xtrace_in_script=True` → invoke as `bash -x` (AC-P7-1).
    - `inherit_xtrace=True` → spawn bash, run `set -x` in the calling
      shell, then `source` the script (AC-P7-2).
    - `custom_ps4` → set PS4 in the environment to test trace-prefix
      overrides cannot bypass the defense (AC-P7-3).

    The caller MUST pass the script path returned by `_make_test_repo`
    (an in-repo copy), not the framework's source script — see the
    note in `_make_test_repo` for why.

    Returns (CompletedProcess, state_dir).
    """
    state_dir = repo / ".test-state"
    state_dir.mkdir(parents=True, exist_ok=True)
    shim_dir = _wire_fake_curl(repo.parent)

    env = _build_env(repo, shim_dir, state_dir)
    if custom_ps4 is not None:
        env["PS4"] = custom_ps4
    if capture_extra_env:
        env.update(capture_extra_env)

    if inherit_xtrace:
        # The caller has xtrace on and `source`s the script. We need
        # the calling shell to inherit -x BEFORE source-ing, so the
        # activated path runs under inherited xtrace and the script
        # must defend itself.
        cmd = [
            "bash",
            "-c",
            f"set -x; source {script}",
        ]
    elif explicit_xtrace_in_script:
        # Direct `bash -x scripts/ahrena-auth.sh`. The shell process
        # itself has xtrace on from the start.
        cmd = ["bash", "-x", str(script)]
    else:
        # Normal invocation (no xtrace) — used by AC-P7-4 to validate
        # functional behavior.
        cmd = ["bash", str(script)]

    proc = subprocess.run(
        cmd,
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
    )
    return proc, state_dir


def _assert_no_leak(stderr: str, label: str) -> None:
    """Scan stderr for any forbidden pattern. Surface a precise error
    when a leak is found so the diagnosis points directly at the
    offending substring + a window around the match."""
    leaks: list[tuple[str, str]] = []
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in stderr:
            # Capture a ±60 char window so the failure message is
            # actionable without dumping the entire trace.
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
# AC-P7-1: `bash -x scripts/ahrena-auth.sh` produces zero stderr matches
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_explicit_bash_x_does_not_leak_token_or_key(tmp_path: Path) -> None:
    """AC-P7-1: invoking the script as `bash -x scripts/ahrena-auth.sh`
    MUST NOT print the JWT, the installation token, or the private key
    material to stderr.

    Without the xtrace defense, `bash -x` would echo every command
    expansion (including `_AHRENA_JWT="..."`, `Authorization: Bearer
    ${_AHRENA_JWT}`, `_AHRENA_TOKEN="..."`) into the trace stream on
    stderr. The defense MUST suppress all of those."""
    repo, script = _make_test_repo(tmp_path)
    proc, _state = _run_script(repo, script, explicit_xtrace_in_script=True)

    assert proc.returncode == 0, (
        f"script exited {proc.returncode} under bash -x.\n"
        f"stderr (first 2000 chars): {proc.stderr[:2000]!r}\n"
        f"stdout: {proc.stdout!r}"
    )
    _assert_no_leak(proc.stderr, "bash -x")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-P7-2: inherited `set -x` from a caller defends equivalently
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_inherited_set_x_does_not_leak(tmp_path: Path) -> None:
    """AC-P7-2: when the calling shell already has `set -x` active and
    sources the script (e.g., `set -euxo pipefail; source
    scripts/ahrena-auth.sh` inside a CI wrapper), the script MUST
    detect inherited xtrace and disable it before touching any secret
    material.

    This is the in-the-wild scenario that triggered the 2026-05-26
    leak — the operator was running under `bash -x` interactively to
    debug the auth flow."""
    repo, script = _make_test_repo(tmp_path)
    proc, _state = _run_script(repo, script, inherit_xtrace=True)

    # Inherited-source path: exit code propagates from the sourced
    # script via `return`, which becomes the bash -c exit code.
    assert proc.returncode == 0, (
        f"sourced script with inherited set -x exited {proc.returncode}.\n"
        f"stderr (first 2000 chars): {proc.stderr[:2000]!r}\n"
        f"stdout: {proc.stdout!r}"
    )
    _assert_no_leak(proc.stderr, "inherited set -x")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-P7-3: custom PS4 override does not bypass the defense
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_custom_ps4_does_not_bypass_defense(tmp_path: Path) -> None:
    """AC-P7-3: changing the xtrace prefix via PS4 (a debugging
    convention to add line numbers, timestamps, or callsite hints to
    the trace) MUST NOT bypass the xtrace defense. The defense works
    by turning xtrace OFF entirely on sensitive lines, not by
    filtering or rewriting the prefix — PS4 changes are orthogonal
    and the protection holds."""
    repo, script = _make_test_repo(tmp_path)
    proc, _state = _run_script(
        repo,
        script,
        explicit_xtrace_in_script=True,
        custom_ps4="+ ${LINENO}: ",
    )

    assert proc.returncode == 0, (
        f"script exited {proc.returncode} under bash -x + custom PS4.\n"
        f"stderr (first 2000 chars): {proc.stderr[:2000]!r}\n"
        f"stdout: {proc.stdout!r}"
    )
    _assert_no_leak(proc.stderr, "custom PS4")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-P7-4: functional behavior unchanged under normal invocation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_normal_invocation_exports_expected_env_vars(tmp_path: Path) -> None:
    """AC-P7-4: under a no-xtrace invocation, the xtrace ceremony
    (`set +x` at entry, restore at exit) MUST NOT break the
    functional flow. The script MUST still:

    - exit 0,
    - export GH_TOKEN_AHRENA_WARRIORS_DEFAULT,
    - export GIT_AUTHOR_NAME, GIT_AUTHOR_EMAIL,
    - export GIT_COMMITTER_NAME, GIT_COMMITTER_EMAIL,
    - and write the installation-token cache to .ahrena/bot/.

    Because exported vars only persist when the script is `source`d
    by the test, we drive this end-to-end with `bash -c "source ...;
    env"` and inspect the captured env."""
    repo, script = _make_test_repo(tmp_path)
    state_dir = repo / ".test-state"
    state_dir.mkdir(parents=True, exist_ok=True)
    shim_dir = _wire_fake_curl(repo.parent)
    env = _build_env(repo, shim_dir, state_dir)

    # Source the script in a fresh bash, then dump the env so we can
    # assert on the exports. Quoting matters: the inner `env` runs
    # AFTER `source`, so it sees the exported vars; the outer Python
    # captures stdout = the env dump.
    cmd = [
        "bash",
        "-c",
        f"source {script} && env",
    ]
    proc = subprocess.run(
        cmd, cwd=repo, env=env, capture_output=True, text=True
    )

    assert proc.returncode == 0, (
        f"sourced script exited {proc.returncode} under normal invocation.\n"
        f"stderr: {proc.stderr!r}\n"
        f"stdout (first 500 chars): {proc.stdout[:500]!r}"
    )

    # Parse the env dump (KEY=VALUE per line) and verify each export.
    env_lines = proc.stdout.splitlines()
    env_dict: dict[str, str] = {}
    for line in env_lines:
        if "=" in line:
            k, _, v = line.partition("=")
            env_dict[k] = v

    expected_exports = (
        "GH_TOKEN_AHRENA_WARRIORS_DEFAULT",
        "GIT_AUTHOR_NAME",
        "GIT_AUTHOR_EMAIL",
        "GIT_COMMITTER_NAME",
        "GIT_COMMITTER_EMAIL",
    )
    missing = [k for k in expected_exports if k not in env_dict]
    assert not missing, (
        f"normal-invocation functional regression: missing exports {missing}.\n"
        f"present env keys: {sorted(env_dict.keys())}"
    )

    # Specifically: the token export holds the synthetic value from
    # fake-curl-auth.sh.
    assert env_dict["GH_TOKEN_AHRENA_WARRIORS_DEFAULT"] == "ghs_FAKE_FOR_TEST_DO_NOT_USE", (
        f"expected synthetic token, got {env_dict['GH_TOKEN_AHRENA_WARRIORS_DEFAULT']!r}"
    )
    # Author identity uses the slug + bot user id from fake-curl-auth.sh.
    assert env_dict["GIT_AUTHOR_NAME"] == "ahrena-bot[bot]", (
        f"unexpected GIT_AUTHOR_NAME: {env_dict['GIT_AUTHOR_NAME']!r}"
    )
    assert "99999999+ahrena-bot[bot]@users.noreply.github.com" in env_dict["GIT_AUTHOR_EMAIL"], (
        f"unexpected GIT_AUTHOR_EMAIL: {env_dict['GIT_AUTHOR_EMAIL']!r}"
    )

    # The cache file MUST exist after a successful mint.
    cache_file = repo / ".ahrena" / "bot" / "installation-token.json"
    assert cache_file.exists(), "installation-token cache was not written"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Defensive: confirm the synthetic token IS the one fake-curl returns.
# This sanity-check ensures the leak-pattern matches would catch a
# real leak — without it, a defense that silently swallowed the curl
# response would pass _assert_no_leak by accident.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_forbidden_pattern_scanner_catches_real_leak(tmp_path: Path) -> None:
    """Self-test of the scanner: feed it a string with a real GitHub
    installation-token prefix and verify _assert_no_leak fails.

    Without this guardrail, a refactor that accidentally narrows
    FORBIDDEN_PATTERNS could silently weaken the entire test file
    (the AC-P7-* assertions would still pass by vacuous absence)."""
    sample_leak = (
        "+ _AHRENA_TOKEN=ghs_FAKE_LEAK_SHOULD_BE_CAUGHT\n"
        "+ export GH_TOKEN_AHRENA_WARRIORS_DEFAULT=ghs_FAKE_LEAK_SHOULD_BE_CAUGHT\n"
    )
    # The scanner MUST flag this. We assert by catching the
    # AssertionError it raises.
    failed_as_expected = False
    try:
        _assert_no_leak(sample_leak, "self-test")
    except AssertionError:
        failed_as_expected = True
    assert failed_as_expected, (
        "leak-pattern scanner did not flag a sample with ghs_ prefix — "
        "the AC-P7-* assertions would pass by vacuous absence. "
        "Tighten FORBIDDEN_PATTERNS."
    )


