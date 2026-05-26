"""Documentation-contract tests for the bot-author routing logic that
`kata-commit` and `kata-pr-prepare` instruct an agent to apply.

The katas are markdown (not executable code), so the "branching logic"
lives in the agent's interpretation of the instructions. These tests
verify two complementary surfaces:

1. The decision matrix the kata documents matches the directive shape
   that `scripts/install.py` renders (`bot_author.enabled` +
   `bot_author.apply_to`). If the rendered shape ever drifts from what
   the kata reads, these tests catch the mismatch.

2. The kata files (pt-BR / es / en) all reference the canonical
   `--warrior` arg, the `scripts/ahrena-auth.sh` source step, and the
   `scripts/ahrena-api-commit.sh` invocation when bot mode is active —
   so the three translations agree on the routing rules (per
   `lex-language` structural equivalence).

These tests treat the kata files as the source of truth and pin the
contract; they do NOT exercise the shell script (that is covered by
`test_ahrena_api_commit.py`).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from install import (  # noqa: E402
    Selection,
    parse_directives,
    render_directives,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
FRAMEWORK = REPO_ROOT / "framework"

KATA_COMMIT_PATHS = [
    FRAMEWORK / "pt-BR" / "_foundation" / "contributing" / "katas" / "kata-commit.md",
    FRAMEWORK / "es" / "_foundation" / "contributing" / "katas" / "kata-commit.md",
    FRAMEWORK / "en" / "_foundation" / "contributing" / "katas" / "kata-commit.md",
]

KATA_PR_PREPARE_PATHS = [
    FRAMEWORK / "pt-BR" / "engineering" / "workflow" / "katas" / "kata-pr-prepare.md",
    FRAMEWORK / "es" / "engineering" / "workflow" / "katas" / "kata-pr-prepare.md",
    FRAMEWORK / "en" / "engineering" / "workflow" / "katas" / "kata-pr-prepare.md",
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Decision-matrix contract (rendered directive ↔ kata expectation)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def _rendered_directives(*, with_bot_author: bool) -> dict:
    """Render .directives via install.py and parse the result back."""
    if with_bot_author:
        sel = Selection(optional_features=frozenset({"bot-author"}))
    else:
        sel = Selection()
    return parse_directives(render_directives(sel))


def test_bot_author_disabled_means_local_path_for_any_warrior() -> None:
    """AC-P2-1 / AC-P2-4 negative branch: when `bot_author.enabled=false`
    the kata MUST always take the local-commit path, regardless of
    `--warrior` or `apply_to`."""
    directives = _rendered_directives(with_bot_author=False)
    # When bot-author is not selected, render_directives emits the commented
    # skeleton — parse_directives sees no live `bot_author:` block.
    assert "bot_author" not in directives or not directives.get("bot_author", {}).get(
        "enabled"
    ), "with bot-author not selected, parsed enabled flag must be falsy"


def test_bot_author_enabled_and_warrior_in_apply_to_means_api_path() -> None:
    """AC-P2-2 / AC-P2-3: bot mode active + warrior listed → bot-author
    path (ahrena-api-commit.sh / GH_TOKEN_AHRENA_BOT)."""
    directives = _rendered_directives(with_bot_author=True)
    bot = directives.get("bot_author", {})
    assert bot.get("enabled") == "true"
    apply_to = bot.get("apply_to")
    assert isinstance(apply_to, list)
    # The 5 canonical warriors are listed (mirrors Plan #271 AC-6).
    for name in ("athena", "apollo", "hephaestus", "iris", "claudionor"):
        assert name in apply_to, f"warrior {name!r} missing from apply_to"


def test_bot_author_apply_to_is_authoritative_for_per_warrior_optout() -> None:
    """AC-P2-4: warriors NOT in `apply_to` keep the local-commit path
    even when the master switch is on. The list-membership check is the
    sole opt-out mechanism — there is no implicit per-warrior override."""
    directives = _rendered_directives(with_bot_author=True)
    apply_to = directives["bot_author"]["apply_to"]
    # Sanity: any warrior name NOT in the canonical list resolves to
    # human-author. This pins the contract; the kata documents it.
    assert "some-unlisted-warrior" not in apply_to
    assert "argos" not in apply_to, (
        "argos is a reviewer (not a committer) — must NOT appear in apply_to "
        "or `kata-commit` would route review comments through the bot identity."
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Kata file contents — pt-BR/es/en parity (lex-language structural)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_kata_commit_documents_warrior_arg_in_all_languages() -> None:
    """All 3 kata-commit translations document the `--warrior` arg."""
    for path in KATA_COMMIT_PATHS:
        content = path.read_text(encoding="utf-8")
        assert "--warrior" in content, f"--warrior arg missing in {path}"


def test_kata_commit_sources_ahrena_auth_in_all_languages() -> None:
    """All 3 kata-commit translations source ahrena-auth.sh as the gate."""
    for path in KATA_COMMIT_PATHS:
        content = path.read_text(encoding="utf-8")
        assert "scripts/ahrena-auth.sh" in content, (
            f"ahrena-auth.sh source step missing in {path}"
        )


def test_kata_commit_invokes_api_commit_script_in_all_languages() -> None:
    """All 3 kata-commit translations point to ahrena-api-commit.sh as
    the bot-author commit path."""
    for path in KATA_COMMIT_PATHS:
        content = path.read_text(encoding="utf-8")
        assert "scripts/ahrena-api-commit.sh" in content, (
            f"ahrena-api-commit.sh invocation missing in {path}"
        )


def test_kata_commit_declares_fallback_on_api_failure_in_all_languages() -> None:
    """The fallback contract (API failure → local commit path) is part of
    the kata's instructions, not an implementation detail."""
    for path in KATA_COMMIT_PATHS:
        content = path.read_text(encoding="utf-8")
        # Exit code 2 is the documented soft-fail signal.
        assert "exit code" in content.lower() and "2" in content, (
            f"exit-code 2 fallback contract missing in {path}"
        )


def test_kata_commit_references_co_authored_by_human_in_all_languages() -> None:
    """The `Co-authored-by: <human>` trailer is the auditability anchor
    on the bot-author path."""
    for path in KATA_COMMIT_PATHS:
        content = path.read_text(encoding="utf-8")
        assert "Co-authored-by" in content, (
            f"Co-authored-by trailer instruction missing in {path}"
        )


def test_kata_pr_prepare_documents_warrior_arg_in_all_languages() -> None:
    for path in KATA_PR_PREPARE_PATHS:
        content = path.read_text(encoding="utf-8")
        assert "--warrior" in content, f"--warrior arg missing in {path}"


def test_kata_pr_prepare_sources_ahrena_auth_in_all_languages() -> None:
    for path in KATA_PR_PREPARE_PATHS:
        content = path.read_text(encoding="utf-8")
        assert "scripts/ahrena-auth.sh" in content, (
            f"ahrena-auth.sh source step missing in {path}"
        )


def test_kata_pr_prepare_uses_gh_token_ahrena_bot_in_all_languages() -> None:
    """The PR-author path threads `GH_TOKEN_AHRENA_BOT` into the
    gh-create invocation."""
    for path in KATA_PR_PREPARE_PATHS:
        content = path.read_text(encoding="utf-8")
        assert "GH_TOKEN_AHRENA_BOT" in content, (
            f"GH_TOKEN_AHRENA_BOT env override missing in {path}"
        )


def test_kata_pr_prepare_documents_soft_fail_in_all_languages() -> None:
    """Soft-fail to the caller's default token is the documented behavior
    when the App lacks the right scope on the target repo."""
    for path in KATA_PR_PREPARE_PATHS:
        content = path.read_text(encoding="utf-8")
        assert "soft-fail" in content.lower() or "soft fail" in content.lower(), (
            f"soft-fail fallback contract missing in {path}"
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Cross-doc parity — same set of warriors appears in apply_to AND in
# the warrior docs that invoke the katas
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_warrior_athena_passes_warrior_arg_to_kata_pr_prepare() -> None:
    """The lone warrior that drives `kata-pr-prepare` is athena. Its doc
    MUST mention `--warrior athena` so the routing decision matches the
    `bot_author.apply_to` membership pinned above."""
    athena_paths = [
        FRAMEWORK / "pt-BR" / "engineering" / "workflow" / "warriors" / "warrior-athena.md",
        FRAMEWORK / "es" / "engineering" / "workflow" / "warriors" / "warrior-athena.md",
        FRAMEWORK / "en" / "engineering" / "workflow" / "warriors" / "warrior-athena.md",
    ]
    for path in athena_paths:
        content = path.read_text(encoding="utf-8")
        assert "--warrior athena" in content, (
            f"warrior-athena.md MUST document `--warrior athena` passthrough; missing in {path}"
        )
