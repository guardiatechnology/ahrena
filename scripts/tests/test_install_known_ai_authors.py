"""Unit tests for the `pr_cost_tracking.known_ai_authors` directive in scripts/install.py.

Covers Plan P3 acceptance criteria (Issue #276):

- AC-P3-4: `pr_cost_tracking.known_ai_authors` documented in the `lex-directives`
  table across 3 languages; built-ins listed.
- AC-P3-5: `install.py` `_render_pr_cost_tracking_section` emits the new key
  (uncommented when Full, commented when skipped); rendered output round-trips
  through `parse_directives` as a list with the 3 built-in entries.

Patterns mirror the existing test files in this folder (test_install_selection.py
and test_install_warriors_default_author.py).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from install import (  # noqa: E402
    PROFILE_FULL,
    PROFILE_MINIMAL,
    get_directive,
    parse_directives,
    render_directives,
)


# Resolve the framework root so the tests stay portable across worktrees.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_FRAMEWORK = _REPO_ROOT / "framework"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Render path — install.py emits the new key (AC-P3-5)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_render_full_includes_known_ai_authors_block() -> None:
    """PROFILE_FULL MUST render `known_ai_authors:` uncommented inside the
    `pr_cost_tracking:` section."""
    content = render_directives(PROFILE_FULL)
    assert "known_ai_authors:" in content, (
        "known_ai_authors key missing from rendered .directives"
    )
    # The section header MUST still appear so the schema is grouped.
    assert "pr_cost_tracking:" in content


def test_render_minimal_has_commented_known_ai_authors_skeleton() -> None:
    """PROFILE_MINIMAL drops `pr_cost_tracking` from optional_features, so the
    rendered `.directives` MUST contain the commented skeleton with the new key."""
    content = render_directives(PROFILE_MINIMAL)
    assert "#   known_ai_authors:" in content, (
        "commented known_ai_authors skeleton missing from minimal render"
    )


def test_parse_directives_returns_known_ai_authors_list() -> None:
    """When the section is uncommented, `parse_directives` MUST surface
    `pr_cost_tracking.known_ai_authors` as a list (same parse path used for
    `known_ai_reviewers` — see `lex-directives`)."""
    content = render_directives(PROFILE_FULL)
    parsed = parse_directives(content)
    authors = get_directive(parsed, "pr_cost_tracking", "known_ai_authors")
    assert isinstance(authors, list), (
        f"known_ai_authors should parse as a list; got {type(authors).__name__}: {authors!r}"
    )


def test_parse_directives_known_ai_authors_built_ins_present() -> None:
    """The three built-ins documented in `kata-pr-cost-stamp` § "Author identity"
    MUST be present in the rendered Full default: `ahrena-bot[bot]`,
    `claude[bot]`, `copilot[bot]`."""
    content = render_directives(PROFILE_FULL)
    parsed = parse_directives(content)
    authors = get_directive(parsed, "pr_cost_tracking", "known_ai_authors")
    assert isinstance(authors, list)
    assert "ahrena-bot[bot]" in authors, f"missing ahrena-bot[bot] in {authors!r}"
    assert "claude[bot]" in authors, f"missing claude[bot] in {authors!r}"
    assert "copilot[bot]" in authors, f"missing copilot[bot] in {authors!r}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Parity with framework/.directives.sample (AC-P3-5)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_directives_sample_includes_known_ai_authors_key() -> None:
    """`framework/.directives.sample` MUST mirror the install.py Full-default
    output and therefore MUST list `known_ai_authors:` with the 3 built-ins."""
    sample = (_FRAMEWORK / ".directives.sample").read_text(encoding="utf-8")
    assert "known_ai_authors:" in sample, (
        "framework/.directives.sample does not document the new key"
    )
    for login in ("ahrena-bot[bot]", "claude[bot]", "copilot[bot]"):
        assert login in sample, (
            f"framework/.directives.sample missing built-in {login!r}"
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Lexis documentation (AC-P3-4)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_lex_directives_table_documents_known_ai_authors() -> None:
    """`lex-directives` MUST document the new directive in every language
    declared in `language.i18n` (pt-BR, es, en). The table row MUST reference
    the kata it drives."""
    for lang in ("pt-BR", "es", "en"):
        path = (
            _FRAMEWORK
            / lang
            / "_foundation"
            / "process"
            / "lexis"
            / "lex-directives.md"
        )
        body = path.read_text(encoding="utf-8")
        assert "`pr_cost_tracking.known_ai_authors`" in body, (
            f"lex-directives ({lang}) missing row for pr_cost_tracking.known_ai_authors"
        )
        assert "kata-pr-cost-stamp" in body, (
            f"lex-directives ({lang}) row does not reference kata-pr-cost-stamp"
        )
