"""Documentation-contract tests for the warriors-default-author routing
logic that `kata-commit` and `kata-pr-prepare` instruct an agent to apply.

The katas are markdown (not executable code), so the "branching logic"
lives in the agent's interpretation of the instructions. These tests
verify two complementary surfaces:

1. The decision matrix the kata documents matches the directive shape
   that `scripts/install.py` renders (`warriors_default_author.enabled` +
   `warriors_default_author.apply_to`). If the rendered shape ever
   drifts from what the kata reads, these tests catch the mismatch.

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


def _rendered_directives(*, with_warriors_default_author: bool) -> dict:
    """Render .directives via install.py and parse the result back."""
    if with_warriors_default_author:
        sel = Selection(optional_features=frozenset({"warriors-default-author"}))
    else:
        sel = Selection()
    return parse_directives(render_directives(sel))


def test_warriors_default_author_disabled_means_local_path_for_any_warrior() -> None:
    """AC-P2-1 / AC-P2-4 negative branch: when
    `warriors_default_author.enabled=false` the kata MUST always take the
    local-commit path, regardless of `--warrior` or `apply_to`."""
    directives = _rendered_directives(with_warriors_default_author=False)
    # When warriors-default-author is not selected, render_directives
    # emits the commented skeleton — parse_directives sees no live
    # `warriors_default_author:` block.
    assert "warriors_default_author" not in directives or not directives.get(
        "warriors_default_author", {}
    ).get(
        "enabled"
    ), "with warriors-default-author not selected, parsed enabled flag must be falsy"


def test_warriors_default_author_enabled_and_warrior_in_apply_to_means_api_path() -> None:
    """AC-P2-2 / AC-P2-3: warriors-default mode active + warrior listed →
    warriors-default-author path (ahrena-api-commit.sh /
    GH_TOKEN_AHRENA_WARRIORS_DEFAULT)."""
    directives = _rendered_directives(with_warriors_default_author=True)
    section = directives.get("warriors_default_author", {})
    assert section.get("enabled") == "true"
    apply_to = section.get("apply_to")
    assert isinstance(apply_to, list)
    # The 5 canonical warriors are listed (mirrors Plan #271 AC-6).
    for name in ("athena", "apollo", "hephaestus", "iris", "claudionor"):
        assert name in apply_to, f"warrior {name!r} missing from apply_to"


def test_warriors_default_author_apply_to_is_authoritative_for_per_warrior_optout() -> None:
    """AC-P2-4: warriors NOT in `apply_to` keep the local-commit path
    even when the master switch is on. The list-membership check is the
    sole opt-out mechanism — there is no implicit per-warrior override."""
    directives = _rendered_directives(with_warriors_default_author=True)
    apply_to = directives["warriors_default_author"]["apply_to"]
    # Sanity: any warrior name NOT in the canonical list resolves to
    # human-author. This pins the contract; the kata documents it.
    assert "some-unlisted-warrior" not in apply_to
    assert "argos" not in apply_to, (
        "argos is a reviewer (not a committer) — must NOT appear in apply_to "
        "or `kata-commit` would route review comments through the warriors-default identity."
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
    the warriors-default-author commit path."""
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
    on the warriors-default-author path."""
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


def test_kata_pr_prepare_uses_gh_token_ahrena_warriors_default_in_all_languages() -> None:
    """The PR-author path threads `GH_TOKEN_AHRENA_WARRIORS_DEFAULT` into
    the gh-create invocation."""
    for path in KATA_PR_PREPARE_PATHS:
        content = path.read_text(encoding="utf-8")
        assert "GH_TOKEN_AHRENA_WARRIORS_DEFAULT" in content, (
            f"GH_TOKEN_AHRENA_WARRIORS_DEFAULT env override missing in {path}"
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
    `warriors_default_author.apply_to` membership pinned above."""
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
