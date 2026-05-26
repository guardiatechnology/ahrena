"""Unit tests for check_github_token_scopes() and the github scope-check
extension of check_env_vars() in scripts/install.py.

The function exercises a single boundary (`urllib.request.urlopen`) and is
stubbed end-to-end via unittest.mock — no real HTTP traffic ever leaves the
test process. The contract under test:

  - All scopes granted             → []
  - One missing scope              → [scope]
  - Multiple missing scopes        → ordered list per `required`
  - Empty X-OAuth-Scopes header    → [GITHUB_FINE_GRAINED_SENTINEL]
  - Missing X-OAuth-Scopes header  → [GITHUB_FINE_GRAINED_SENTINEL]
  - Network error / timeout        → [] (soft-fail, no traceback)
  - Token is passed in the Authorization header as `Bearer <token>`

The check_env_vars() extension is exercised in a second group with the same
stub so the warning lines are asserted verbatim.
"""

from __future__ import annotations

import socket
import sys
import urllib.error
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from install import (  # noqa: E402
    GITHUB_FINE_GRAINED_SENTINEL,
    GITHUB_MCP_REQUIRED_SCOPES,
    PROFILE_FULL,
    Selection,
    check_env_vars,
    check_github_token_scopes,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helpers — stub urlopen to return a fake response with controlled headers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _fake_response(scopes_header: str | None) -> MagicMock:
    """Build a MagicMock that mimics urllib's HTTPResponse context manager.

    `scopes_header` is the literal value returned by `resp.headers.get(
    "X-OAuth-Scopes")`. Passing `None` simulates a header absent from the
    response (the common fine-grained PAT case).
    """
    resp = MagicMock()
    resp.headers.get.return_value = scopes_header
    cm = MagicMock()
    cm.__enter__.return_value = resp
    cm.__exit__.return_value = False
    return cm


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# check_github_token_scopes — happy paths
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_all_scopes_granted_returns_empty_list() -> None:
    granted = ", ".join(GITHUB_MCP_REQUIRED_SCOPES)
    with patch("install.urllib.request.urlopen", return_value=_fake_response(granted)):
        missing = check_github_token_scopes("ghp_dummy", GITHUB_MCP_REQUIRED_SCOPES)
    assert missing == []


def test_one_missing_scope_returns_that_scope() -> None:
    granted = "repo, workflow, read:user"  # missing read:org
    with patch("install.urllib.request.urlopen", return_value=_fake_response(granted)):
        missing = check_github_token_scopes("ghp_dummy", GITHUB_MCP_REQUIRED_SCOPES)
    assert missing == ["read:org"]


def test_multiple_missing_scopes_preserves_required_order() -> None:
    granted = "repo"  # missing read:org, workflow, read:user
    with patch("install.urllib.request.urlopen", return_value=_fake_response(granted)):
        missing = check_github_token_scopes("ghp_dummy", GITHUB_MCP_REQUIRED_SCOPES)
    # Order MUST follow the declared `required` list, not header order.
    assert missing == ["read:org", "workflow", "read:user"]


def test_all_missing_returns_full_required_list_in_order() -> None:
    with patch("install.urllib.request.urlopen", return_value=_fake_response("")):
        # Empty string header is treated as fine-grained — covered below.
        # Use a header with an unrelated scope to test the empty-granted set path.
        pass
    with patch(
        "install.urllib.request.urlopen",
        return_value=_fake_response("public_repo"),
    ):
        missing = check_github_token_scopes("ghp_dummy", GITHUB_MCP_REQUIRED_SCOPES)
    assert missing == GITHUB_MCP_REQUIRED_SCOPES


def test_granted_scopes_with_extra_whitespace_are_normalized() -> None:
    granted = "  repo  ,  read:org , workflow ,read:user"
    with patch("install.urllib.request.urlopen", return_value=_fake_response(granted)):
        missing = check_github_token_scopes("ghp_dummy", GITHUB_MCP_REQUIRED_SCOPES)
    assert missing == []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# check_github_token_scopes — fine-grained PAT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_empty_x_oauth_scopes_header_signals_fine_grained() -> None:
    with patch("install.urllib.request.urlopen", return_value=_fake_response("")):
        missing = check_github_token_scopes("github_pat_xxx", GITHUB_MCP_REQUIRED_SCOPES)
    assert missing == [GITHUB_FINE_GRAINED_SENTINEL]


def test_missing_x_oauth_scopes_header_signals_fine_grained() -> None:
    with patch("install.urllib.request.urlopen", return_value=_fake_response(None)):
        missing = check_github_token_scopes("github_pat_xxx", GITHUB_MCP_REQUIRED_SCOPES)
    assert missing == [GITHUB_FINE_GRAINED_SENTINEL]


def test_whitespace_only_x_oauth_scopes_header_signals_fine_grained() -> None:
    with patch("install.urllib.request.urlopen", return_value=_fake_response("   ")):
        missing = check_github_token_scopes("github_pat_xxx", GITHUB_MCP_REQUIRED_SCOPES)
    assert missing == [GITHUB_FINE_GRAINED_SENTINEL]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# check_github_token_scopes — soft-fail on network errors
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_url_error_returns_empty_no_traceback() -> None:
    with patch("install.urllib.request.urlopen", side_effect=urllib.error.URLError("dns")):
        missing = check_github_token_scopes("ghp_dummy", GITHUB_MCP_REQUIRED_SCOPES)
    assert missing == []


def test_http_error_returns_empty_no_traceback() -> None:
    err = urllib.error.HTTPError(
        url="https://api.github.com/",
        code=401,
        msg="Unauthorized",
        hdrs=None,  # type: ignore[arg-type]
        fp=None,
    )
    with patch("install.urllib.request.urlopen", side_effect=err):
        missing = check_github_token_scopes("ghp_dummy", GITHUB_MCP_REQUIRED_SCOPES)
    assert missing == []


def test_timeout_returns_empty_no_traceback() -> None:
    with patch("install.urllib.request.urlopen", side_effect=socket.timeout("read timed out")):
        missing = check_github_token_scopes("ghp_dummy", GITHUB_MCP_REQUIRED_SCOPES)
    assert missing == []


def test_unexpected_exception_returns_empty_no_traceback() -> None:
    with patch("install.urllib.request.urlopen", side_effect=RuntimeError("boom")):
        missing = check_github_token_scopes("ghp_dummy", GITHUB_MCP_REQUIRED_SCOPES)
    assert missing == []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# check_github_token_scopes — request shape
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_token_is_sent_as_bearer_authorization_header() -> None:
    captured: dict[str, Any] = {}

    def _spy(req: Any, timeout: float = 0) -> MagicMock:  # noqa: ARG001
        captured["url"] = req.full_url
        captured["headers"] = {k.lower(): v for k, v in req.header_items()}
        captured["timeout"] = timeout
        return _fake_response(", ".join(GITHUB_MCP_REQUIRED_SCOPES))

    with patch("install.urllib.request.urlopen", side_effect=_spy):
        check_github_token_scopes("ghp_abc123", GITHUB_MCP_REQUIRED_SCOPES)

    assert captured["url"] == "https://api.github.com/"
    # urllib normalizes header keys to capitalized; lowercase-compare for safety.
    assert captured["headers"]["authorization"] == "Bearer ghp_abc123"
    assert captured["headers"]["user-agent"] == "ahrena-install"
    assert captured["timeout"] == 5


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# check_env_vars — integration with the github scope check
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _github_only_selection() -> Selection:
    return Selection(mcps=frozenset({"ahrena", "github"}))


def test_check_env_vars_warns_when_gh_token_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GH_TOKEN", raising=False)
    warnings = check_env_vars(_github_only_selection())
    assert any("GH_TOKEN" in w and "currently unset" in w for w in warnings)
    # When the var is unset, the scope check must NOT fire.
    assert not any("scope" in w for w in warnings)


def test_check_env_vars_emits_no_warning_when_all_scopes_granted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GH_TOKEN", "ghp_dummy")
    granted = ", ".join(GITHUB_MCP_REQUIRED_SCOPES)
    with patch("install.urllib.request.urlopen", return_value=_fake_response(granted)):
        warnings = check_env_vars(_github_only_selection())
    # No github-related warning when scopes are complete.
    assert not any("github" in w for w in warnings)


def test_check_env_vars_emits_one_line_per_missing_scope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GH_TOKEN", "ghp_dummy")
    granted = "repo, workflow"  # missing read:org and read:user
    with patch("install.urllib.request.urlopen", return_value=_fake_response(granted)):
        warnings = check_env_vars(_github_only_selection())
    assert (
        "WARNING: MCP 'github' GH_TOKEN missing scope: read:org. "
        "Run: gh auth refresh -s read:org"
        in warnings
    )
    assert (
        "WARNING: MCP 'github' GH_TOKEN missing scope: read:user. "
        "Run: gh auth refresh -s read:user"
        in warnings
    )


def test_check_env_vars_emits_fine_grained_advisory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GH_TOKEN", "github_pat_xxx")
    with patch("install.urllib.request.urlopen", return_value=_fake_response(None)):
        warnings = check_env_vars(_github_only_selection())
    fine_grained = [w for w in warnings if "fine-grained" in w]
    assert len(fine_grained) == 1
    msg = fine_grained[0]
    assert "MCP 'github'" in msg
    assert "GH_TOKEN" in msg
    # Confirm all required scope names are listed in the advisory.
    for scope in GITHUB_MCP_REQUIRED_SCOPES:
        assert scope in msg


def test_check_env_vars_is_silent_on_network_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GH_TOKEN", "ghp_dummy")
    with patch("install.urllib.request.urlopen", side_effect=urllib.error.URLError("dns")):
        warnings = check_env_vars(_github_only_selection())
    # Soft-fail: no github warning at all when the network check fails.
    assert not any("github" in w for w in warnings)


def test_check_env_vars_full_profile_scope_check_does_not_fire_without_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Ensure GH_TOKEN is unset; the scope check must be skipped entirely
    # (no urlopen call), and the legacy "unset" warning must still appear.
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("FIGMA_API_KEY", raising=False)
    with patch("install.urllib.request.urlopen") as urlopen_mock:
        warnings = check_env_vars(PROFILE_FULL)
    urlopen_mock.assert_not_called()
    joined = "\n".join(warnings)
    assert "GH_TOKEN" in joined
    assert "FIGMA_API_KEY" in joined
