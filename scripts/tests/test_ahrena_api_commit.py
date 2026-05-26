"""Unit tests for scripts/ahrena-api-commit.sh (Plan P2).

The shell script under test:

- Exits 0 (no-op) when `GH_TOKEN_AHRENA_BOT` is absent (AC-P2-1, AC-P2-4
  branch when bot mode is off).
- Drives a 4-step GitHub Git Data API flow (blob → tree → commit → ref)
  using `curl` + `jq`, returning the new commit SHA on stdout (AC-P2-2/3).
- Soft-fails (exit 2) on any API/network error so the calling kata can
  fall back to local `git commit` (AC-P2-6).
- Refreshes the installation token once on HTTP 401 by re-sourcing
  `scripts/ahrena-auth.sh` (AC-P2-6 retry path).
- Never echoes the installation token to stdout or stderr (AC-P2-7).

Strategy: a `fake-curl.sh` shim (under `scripts/tests/fixtures/`) replaces
the real curl on PATH. The shim reads its planned responses from a
per-test `plan_dir` populated by the test, and writes a redacted call log
that the assertions inspect.

Mirrors the test-conventions baseline established by `test_install_*`
files (same pytest patterns, no fixture sharing across tests).
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_UNDER_TEST = REPO_ROOT / "scripts" / "ahrena-api-commit.sh"
FAKE_CURL = REPO_ROOT / "scripts" / "tests" / "fixtures" / "fake-curl.sh"

# Sentinel token value used across tests; intentionally distinctive so any
# leak would be impossible to miss in captured output.
TEST_TOKEN = "ghs_TEST_TOKEN_REDACTION_GUARD_4747"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def _init_repo(repo: Path) -> None:
    """Initialize a throw-away git repo with one initial commit so the
    script has a parent SHA + tree to base the new commit on."""
    repo.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "--quiet", "-b", "main"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    # Avoid the global signing config dragging us in.
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=repo, check=True)
    (repo / "README.md").write_text("initial\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
    subprocess.run(
        ["git", "commit", "--quiet", "-m", "initial"],
        cwd=repo,
        check=True,
        env={**os.environ, "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z"},
    )
    # Fake origin remote so the script can resolve `owner/repo`.
    subprocess.run(
        ["git", "remote", "add", "origin", "https://github.com/test-org/test-repo.git"],
        cwd=repo,
        check=True,
    )


def _write_plan(plan_dir: Path, calls: list[tuple[int, dict]]) -> None:
    """Materialize a per-call response plan in plan_dir.

    Each entry is (http_status, json_body_dict). The fake-curl stub reads
    plan_dir/NNN.status + plan_dir/NNN.json on call N (1-indexed).
    """
    import json

    plan_dir.mkdir(parents=True, exist_ok=True)
    for i, (status, body) in enumerate(calls, start=1):
        nnn = f"{i:03d}"
        (plan_dir / f"{nnn}.status").write_text(str(status), encoding="utf-8")
        (plan_dir / f"{nnn}.json").write_text(json.dumps(body), encoding="utf-8")


def _env_with_fake_curl(state_dir: Path, plan_dir: Path, token: str | None) -> dict:
    """Build the env that runs the script with the fake curl on PATH."""
    fixtures_dir = FAKE_CURL.parent
    # Use a symlink-named `curl` so the script's `_curl_silent` (which
    # invokes plain `curl`) resolves to the stub.
    shim_dir = state_dir / "shim"
    shim_dir.mkdir(parents=True, exist_ok=True)
    curl_link = shim_dir / "curl"
    if curl_link.exists() or curl_link.is_symlink():
        curl_link.unlink()
    curl_link.symlink_to(FAKE_CURL)

    env = {
        # Preserve the inherited PATH for the real `git`, `jq`, `base64`,
        # `mktemp`, `awk`, `sed`. Prepend the shim dir so `curl` resolves
        # to the stub.
        "PATH": f"{shim_dir}:{os.environ.get('PATH', '')}",
        "HOME": os.environ.get("HOME", ""),
        "FAKE_CURL_PLAN_DIR": str(plan_dir),
        "FAKE_CURL_STATE_DIR": str(state_dir),
        "FAKE_CURL_TOKEN_REDACT_GUARD": token or "",
    }
    if token is not None:
        env["GH_TOKEN_AHRENA_BOT"] = token
    # Carry GIT_* config-free environment.
    for k in ("LANG", "LC_ALL", "TERM"):
        if k in os.environ:
            env[k] = os.environ[k]
    return env


def _stage_file(repo: Path, path: str, content: str) -> None:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", path], cwd=repo, check=True)


def _run_script(
    repo: Path,
    *,
    token: str | None,
    branch: str = "main",
    message: str = "feat: test commit",
    co_author: str | None = None,
    plan: list[tuple[int, dict]] | None = None,
    extra_env: dict | None = None,
) -> tuple[subprocess.CompletedProcess, Path, Path]:
    """Invoke the script with the fake curl wired up; return (proc, plan_dir, state_dir)."""
    state_dir = repo / ".test-state"
    plan_dir = repo / ".test-plan"
    state_dir.mkdir(parents=True, exist_ok=True)
    if plan is not None:
        _write_plan(plan_dir, plan)
    else:
        plan_dir.mkdir(parents=True, exist_ok=True)

    env = _env_with_fake_curl(state_dir, plan_dir, token)
    if extra_env:
        env.update(extra_env)

    args = [
        str(SCRIPT_UNDER_TEST),
        "--branch",
        branch,
        "--message",
        message,
    ]
    if co_author:
        args.extend(["--co-author", co_author])

    proc = subprocess.run(
        args,
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
    )
    return proc, plan_dir, state_dir


def _read_call_log(state_dir: Path) -> list[str]:
    log = state_dir / "calls.log"
    if not log.exists():
        return []
    return log.read_text(encoding="utf-8").splitlines()


def _read_request_body(state_dir: Path, call_index: int) -> dict | None:
    """Return the JSON body sent on the Nth call (1-indexed), or None."""
    import json

    p = state_dir / f"req-{call_index}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-P2-1: no-op when GH_TOKEN_AHRENA_BOT is absent
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_no_op_when_token_absent(tmp_path: Path) -> None:
    """bot_author.enabled=false → ahrena-auth.sh exports nothing →
    GH_TOKEN_AHRENA_BOT absent → this script MUST exit 0 silently
    without invoking curl."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    _stage_file(repo, "foo.txt", "hello\n")

    proc, _plan_dir, state_dir = _run_script(repo, token=None)

    assert proc.returncode == 0, f"unexpected exit: stdout={proc.stdout!r} stderr={proc.stderr!r}"
    # No curl calls should have been made.
    assert _read_call_log(state_dir) == [], (
        "no-op path made an HTTP call — should have exited before any curl invocation"
    )
    # Local commit was NOT created (the kata's local commit path takes over).
    log = subprocess.run(
        ["git", "log", "--oneline"], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip().splitlines()
    assert len(log) == 1, "no-op path must not create a commit on its own"


def test_no_op_emits_nothing_on_stdout(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    _stage_file(repo, "foo.txt", "hello\n")
    proc, _plan_dir, _state_dir = _run_script(repo, token=None)
    assert proc.stdout == "", f"no-op path leaked to stdout: {proc.stdout!r}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Required-arg validation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_missing_branch_arg_returns_1(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    state_dir = repo / ".test-state"
    state_dir.mkdir(parents=True, exist_ok=True)
    env = _env_with_fake_curl(state_dir, repo / ".test-plan", TEST_TOKEN)
    proc = subprocess.run(
        [str(SCRIPT_UNDER_TEST), "--message", "x"],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert "--branch is required" in proc.stderr


def test_missing_message_arg_returns_1(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    state_dir = repo / ".test-state"
    state_dir.mkdir(parents=True, exist_ok=True)
    env = _env_with_fake_curl(state_dir, repo / ".test-plan", TEST_TOKEN)
    proc = subprocess.run(
        [str(SCRIPT_UNDER_TEST), "--branch", "main"],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert "--message is required" in proc.stderr


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-P2-2: happy path (4-step blob/tree/commit/ref)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_happy_path_blob_tree_commit_ref(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    _stage_file(repo, "foo.txt", "bar\n")

    plan = [
        (201, {"sha": "blob_sha_xxxxxxxxxxxxxxxxxxxx"}),
        (201, {"sha": "tree_sha_xxxxxxxxxxxxxxxxxxxx"}),
        (201, {"sha": "commit_sha_xxxxxxxxxxxxxxxxxxxx"}),
        (200, {"ref": "refs/heads/main", "object": {"sha": "commit_sha_xxxxxxxxxxxxxxxxxxxx"}}),
    ]
    # Bypass step 6 (fetch+reset) by stubbing git fetch via PATH? We can't
    # easily mock git inside the same shell. Workaround: invoke the script
    # but expect exit 3 (commit landed, local sync failed because origin is
    # a fake URL). Verify the 4 API calls + the new commit SHA on stdout
    # AND that the warning message references the new commit SHA.
    proc, _plan_dir, state_dir = _run_script(
        repo, token=TEST_TOKEN, plan=plan, co_author="Human Dev <human@example.com>"
    )

    # Exit 3 = commit landed remotely but local fetch/reset failed (expected
    # in test because origin is a fake https URL).
    assert proc.returncode == 3, (
        f"expected exit 3 (commit OK, local sync failed); got {proc.returncode}\n"
        f"stdout={proc.stdout!r}\nstderr={proc.stderr!r}"
    )
    # The new commit SHA must appear in the warning line that flags the
    # local-sync failure.
    assert "commit_sha_xxxxxxxxxxxxxxxxxxxx" in proc.stderr
    assert "created on remote but" in proc.stderr

    # Exactly 4 API calls were issued.
    calls = _read_call_log(state_dir)
    assert len(calls) == 4, f"expected 4 API calls; got {len(calls)}:\n{calls}"
    assert "method=POST" in calls[0] and "/git/blobs" in calls[0]
    assert "method=POST" in calls[1] and "/git/trees" in calls[1]
    assert "method=POST" in calls[2] and "/git/commits" in calls[2]
    assert "method=PATCH" in calls[3] and "/git/refs/heads/main" in calls[3]

    # Every call carried the Authorization header.
    assert all("auth_present=yes" in c for c in calls), calls

    # The commit body MUST contain the Co-authored-by trailer.
    commit_req = _read_request_body(state_dir, 3)
    assert commit_req is not None
    assert "Co-authored-by: Human Dev <human@example.com>" in commit_req["message"], (
        f"missing Co-authored-by trailer in commit message: {commit_req['message']!r}"
    )
    assert commit_req["tree"] == "tree_sha_xxxxxxxxxxxxxxxxxxxx"
    assert commit_req["parents"] == [
        subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True
        ).stdout.strip()
    ]


def test_happy_path_without_co_author_emits_no_trailer(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    _stage_file(repo, "foo.txt", "bar\n")
    plan = [
        (201, {"sha": "blob_sha"}),
        (201, {"sha": "tree_sha"}),
        (201, {"sha": "commit_sha"}),
        (200, {"ref": "refs/heads/main"}),
    ]
    proc, _plan_dir, state_dir = _run_script(repo, token=TEST_TOKEN, plan=plan, co_author=None)
    # Exit 3 (commit OK, local sync fails) — same as the happy-path test.
    assert proc.returncode == 3, f"stderr={proc.stderr!r}"
    commit_req = _read_request_body(state_dir, 3)
    assert commit_req is not None
    assert "Co-authored-by" not in commit_req["message"], (
        f"unexpected Co-authored-by trailer: {commit_req['message']!r}"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-P2-6: soft-fail on API errors (returns 2)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_blob_creation_500_returns_2(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    _stage_file(repo, "foo.txt", "bar\n")
    plan = [(500, {"message": "Server error"})]
    proc, _plan_dir, _state_dir = _run_script(repo, token=TEST_TOKEN, plan=plan)
    assert proc.returncode == 2
    assert "blob upload failed" in proc.stderr or "HTTP 500" in proc.stderr


def test_no_staged_changes_returns_2(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    # NOTHING staged.
    proc, _plan_dir, _state_dir = _run_script(repo, token=TEST_TOKEN, plan=[])
    assert proc.returncode == 2
    assert "nothing staged" in proc.stderr


def test_tree_creation_failure_returns_2(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    _stage_file(repo, "foo.txt", "bar\n")
    plan = [
        (201, {"sha": "blob_sha"}),
        (422, {"message": "tree validation failed"}),
    ]
    proc, _plan_dir, _state_dir = _run_script(repo, token=TEST_TOKEN, plan=plan)
    assert proc.returncode == 2
    assert "tree creation failed" in proc.stderr or "HTTP 422" in proc.stderr


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-P2-7: token redaction (token NEVER appears in stdout/stderr)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_token_never_in_stdout_or_stderr_happy_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    _stage_file(repo, "foo.txt", "bar\n")
    plan = [
        (201, {"sha": "blob_sha"}),
        (201, {"sha": "tree_sha"}),
        (201, {"sha": "commit_sha"}),
        (200, {}),
    ]
    proc, _plan_dir, state_dir = _run_script(repo, token=TEST_TOKEN, plan=plan)
    combined = proc.stdout + proc.stderr
    assert TEST_TOKEN not in combined, (
        f"installation token leaked into captured output:\nstdout={proc.stdout!r}\n"
        f"stderr={proc.stderr!r}"
    )
    # Sanity: the stub did receive the token via the Authorization header
    # (so the test is meaningful — not a vacuously-passing assertion).
    auth_guard = state_dir / "auth-guard.log"
    assert auth_guard.exists(), "fake-curl did not see the Authorization bearer at all"


def test_token_never_in_stderr_on_500(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    _stage_file(repo, "foo.txt", "bar\n")
    plan = [(500, {"message": "boom"})]
    proc, _plan_dir, _state_dir = _run_script(repo, token=TEST_TOKEN, plan=plan)
    combined = proc.stdout + proc.stderr
    assert TEST_TOKEN not in combined, (
        f"installation token leaked into 500 error output:\nstdout={proc.stdout!r}\n"
        f"stderr={proc.stderr!r}"
    )


def test_token_never_in_stderr_on_missing_args(tmp_path: Path) -> None:
    """Even when failing the most obvious way (missing args), the token
    must not appear in any error message."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    state_dir = repo / ".test-state"
    state_dir.mkdir(parents=True, exist_ok=True)
    env = _env_with_fake_curl(state_dir, repo / ".test-plan", TEST_TOKEN)
    proc = subprocess.run(
        [str(SCRIPT_UNDER_TEST)],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
    )
    assert TEST_TOKEN not in (proc.stdout + proc.stderr)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-P2-6 retry path: 401 → re-source ahrena-auth.sh → retry once
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_401_retries_once_after_re_sourcing_auth(tmp_path: Path) -> None:
    """First blob upload returns 401; the script MUST re-source
    ahrena-auth.sh (no-op when bot_author.enabled is missing, but still
    invoked) and retry the call once with the refreshed token. The second
    call returns 201 and the flow proceeds normally."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    _stage_file(repo, "foo.txt", "bar\n")
    plan = [
        (401, {"message": "Bad credentials"}),
        (201, {"sha": "blob_sha"}),
        (201, {"sha": "tree_sha"}),
        (201, {"sha": "commit_sha"}),
        (200, {}),
    ]
    proc, _plan_dir, state_dir = _run_script(repo, token=TEST_TOKEN, plan=plan)
    # Exit 3 (commit OK, local sync failed) is the expected end-state.
    assert proc.returncode == 3, (
        f"expected exit 3; got {proc.returncode}\nstderr={proc.stderr!r}"
    )
    assert "HTTP 401" in proc.stderr or "refreshing installation token" in proc.stderr
    calls = _read_call_log(state_dir)
    # 5 calls total: 401 + retry-201 + tree + commit + ref.
    assert len(calls) == 5, f"expected 5 API calls (401 retried once + 4 happy-path); got {calls}"


def test_401_twice_returns_2(tmp_path: Path) -> None:
    """If the retry also returns 401, the script must give up with exit 2
    (no infinite retry loop)."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    _stage_file(repo, "foo.txt", "bar\n")
    plan = [
        (401, {"message": "Bad credentials"}),
        (401, {"message": "Bad credentials again"}),
    ]
    proc, _plan_dir, state_dir = _run_script(repo, token=TEST_TOKEN, plan=plan)
    assert proc.returncode == 2, (
        f"expected exit 2 on double-401; got {proc.returncode}\nstderr={proc.stderr!r}"
    )
    calls = _read_call_log(state_dir)
    assert len(calls) == 2, f"must retry exactly once on 401; got {len(calls)} calls"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Deletion handling (status D → tree entry with sha:null)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_staged_deletion_emits_null_blob_entry(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    # Add + commit a file, then stage its deletion.
    (repo / "delete-me.txt").write_text("bye\n", encoding="utf-8")
    subprocess.run(["git", "add", "delete-me.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "--quiet", "-m", "add"], cwd=repo, check=True)
    subprocess.run(["git", "rm", "--quiet", "delete-me.txt"], cwd=repo, check=True)

    # Only 2 calls: tree, commit. NOT blobs (deletions don't post blobs).
    # Then the ref PATCH. Total 3.
    plan = [
        (201, {"sha": "tree_sha"}),
        (201, {"sha": "commit_sha"}),
        (200, {}),
    ]
    proc, _plan_dir, state_dir = _run_script(repo, token=TEST_TOKEN, plan=plan)
    assert proc.returncode == 3, f"stderr={proc.stderr!r}"
    calls = _read_call_log(state_dir)
    assert len(calls) == 3, f"deletion should skip blob upload; got {calls}"
    assert "/git/trees" in calls[0]
    # Tree entry must mark deletion via sha:null.
    tree_req = _read_request_body(state_dir, 1)
    assert tree_req is not None
    entry = tree_req["tree"][0]
    assert entry["path"] == "delete-me.txt"
    assert entry["sha"] is None, f"deletion entry sha must be null; got {entry}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Repo resolution
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_repo_resolved_from_https_origin(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    _stage_file(repo, "foo.txt", "bar\n")
    plan = [
        (201, {"sha": "blob_sha"}),
        (201, {"sha": "tree_sha"}),
        (201, {"sha": "commit_sha"}),
        (200, {}),
    ]
    proc, _plan_dir, state_dir = _run_script(repo, token=TEST_TOKEN, plan=plan)
    assert proc.returncode == 3, f"stderr={proc.stderr!r}"
    calls = _read_call_log(state_dir)
    # All API URLs must include `test-org/test-repo`.
    for c in calls:
        assert "test-org/test-repo" in c, f"call missing resolved repo: {c}"


def test_repo_resolved_from_ssh_origin(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    # Replace origin URL with the ssh form.
    subprocess.run(
        ["git", "remote", "set-url", "origin", "git@github.com:another-org/another-repo.git"],
        cwd=repo,
        check=True,
    )
    _stage_file(repo, "foo.txt", "bar\n")
    plan = [(201, {"sha": "blob_sha"})]
    proc, _plan_dir, state_dir = _run_script(repo, token=TEST_TOKEN, plan=plan)
    # We only need the first call to verify URL resolution.
    calls = _read_call_log(state_dir)
    assert calls, "no calls captured"
    assert "another-org/another-repo" in calls[0]
    # Cleanup expectation: subsequent steps not planned → script will exit
    # non-zero (which is fine for this assertion-focused test).
    assert proc.returncode != 0  # may be 2 (tree call missing) or 3


@pytest.mark.parametrize(
    "origin_url",
    [
        "https://github.com/o/r.git",
        "https://github.com/o/r",
        "http://github.com/o/r.git",
        "git@github.com:o/r.git",
        "ssh://git@github.com/o/r.git",
        "ssh://github.com/o/r",
        "git://github.com/o/r.git",
    ],
)
def test_repo_resolution_across_url_schemes(tmp_path: Path, origin_url: str) -> None:
    """Every origin URL form GitHub publishes MUST resolve to `o/r`.

    Addresses gemini-code-assist comment #3301245358 on PR #279: the
    pre-fix-up sed only handled https://, http:// and scp-style. The
    parametric matrix below pins ssh:// and git:// (plus existing
    schemes as regression guards).
    """
    repo = tmp_path / "repo"
    _init_repo(repo)
    subprocess.run(
        ["git", "remote", "set-url", "origin", origin_url],
        cwd=repo,
        check=True,
    )
    _stage_file(repo, "foo.txt", "bar\n")
    plan = [(201, {"sha": "blob_sha"})]
    proc, _plan_dir, state_dir = _run_script(repo, token=TEST_TOKEN, plan=plan)
    calls = _read_call_log(state_dir)
    assert calls, f"no curl calls captured for origin {origin_url!r}"
    # Every API URL produced by the script must include the resolved
    # `o/r` slug — never the original scheme prefix.
    assert "/repos/o/r/" in calls[0], (
        f"repo not resolved correctly for origin {origin_url!r}; first call: {calls[0]!r}"
    )
    # The script will exit non-zero because we only planned the first
    # call; we are only asserting URL parsing here.
    assert proc.returncode != 0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-P2-2 first-commit on a brand-new branch: PATCH 404 → POST /git/refs
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_patch_404_falls_back_to_post_create_ref(tmp_path: Path) -> None:
    """First commit on a brand-new feature branch: `PATCH /git/refs/heads/<branch>`
    returns 404 (the ref does not exist yet). The script MUST fall back
    to `POST /git/refs` with `{ref, sha}` so the branch is created and
    the bot-author commit lands.

    Addresses gemini-code-assist comment #3301245348 on PR #279:
    without the fallback, AC-P2-2 was silently broken on the first
    commit of every new branch — the kata would drop to the human-
    author fallback path even though the API token was valid.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)
    _stage_file(repo, "foo.txt", "bar\n")
    plan = [
        # Steps 1-4: happy-path blob + tree + commit.
        (201, {"sha": "blob_sha_xxxxxxxxxxxxxxxxxxxx"}),
        (201, {"sha": "tree_sha_xxxxxxxxxxxxxxxxxxxx"}),
        (201, {"sha": "commit_sha_xxxxxxxxxxxxxxxxxxxx"}),
        # Step 5: PATCH ref → 404 (branch does not exist on remote yet).
        (404, {"message": "Reference does not exist"}),
        # Step 6: POST /git/refs → 201 (ref created).
        (201, {"ref": "refs/heads/main", "object": {"sha": "commit_sha_xxxxxxxxxxxxxxxxxxxx"}}),
    ]
    proc, _plan_dir, state_dir = _run_script(repo, token=TEST_TOKEN, plan=plan)
    # Exit 3 = commit landed remotely (PATCH 404 + POST 201) but local
    # `git fetch origin <branch>` fails because origin is a fake URL.
    # That is exactly the same end-state as the existing happy-path test.
    assert proc.returncode == 3, (
        f"expected exit 3 after POST fallback; got {proc.returncode}\n"
        f"stdout={proc.stdout!r}\nstderr={proc.stderr!r}"
    )
    calls = _read_call_log(state_dir)
    # 5 API calls total: blob + tree + commit + PATCH(404) + POST(201).
    assert len(calls) == 5, f"expected 5 API calls; got {len(calls)}:\n{calls}"
    # Verify the PATCH was attempted first and the POST followed as the
    # 5th call against `/git/refs` (not `/git/refs/heads/<branch>`).
    assert "method=PATCH" in calls[3] and "/git/refs/heads/main" in calls[3]
    assert "method=POST" in calls[4] and "/git/refs" in calls[4]
    assert "/git/refs/heads/" not in calls[4], (
        f"POST fallback must target /git/refs (no branch path); got {calls[4]!r}"
    )
    # POST body must carry the canonical {ref, sha} pair.
    post_req = _read_request_body(state_dir, 5)
    assert post_req is not None
    assert post_req == {
        "ref": "refs/heads/main",
        "sha": "commit_sha_xxxxxxxxxxxxxxxxxxxx",
    }, f"unexpected POST /git/refs body: {post_req!r}"


def test_patch_and_post_both_fail_returns_2(tmp_path: Path) -> None:
    """When PATCH 404s and the POST fallback also fails (5xx, 422, etc.),
    the script MUST exit 2 so the kata falls back to local commit.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)
    _stage_file(repo, "foo.txt", "bar\n")
    plan = [
        (201, {"sha": "blob_sha"}),
        (201, {"sha": "tree_sha"}),
        (201, {"sha": "commit_sha"}),
        (404, {"message": "Reference does not exist"}),
        (422, {"message": "Validation Failed"}),
    ]
    proc, _plan_dir, state_dir = _run_script(repo, token=TEST_TOKEN, plan=plan)
    assert proc.returncode == 2, f"stderr={proc.stderr!r}"
    assert "ref update/creation failed" in proc.stderr
    calls = _read_call_log(state_dir)
    assert len(calls) == 5
