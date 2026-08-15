"""Tests for preserving optional stack subpaths in platform projections."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from install import (  # noqa: E402
    build_claude_code_path,
    build_cursor_path,
)


def test_rule_projection_preserves_stack_subpath() -> None:
    source = Path(
        "en/engineering/backend/dotnet/lexis/lex-dotnet-runtime-safety.md"
    )

    assert build_cursor_path(source, "lex", "rules") == Path(
        ".cursor/rules/engineering/backend/dotnet/lex-dotnet-runtime-safety.mdc"
    )
    assert build_claude_code_path(source, "lex", "rules") == Path(
        ".claude/rules/engineering/backend/dotnet/lex-dotnet-runtime-safety.md"
    )


def test_command_projection_preserves_stack_when_platform_is_hierarchical() -> None:
    source = Path("en/engineering/backend/python/cries/cry-python-review.md")

    assert build_cursor_path(source, "cry", "commands") == Path(
        ".cursor/commands/engineering/backend/python/cry-python-review.md"
    )
    assert build_claude_code_path(source, "cry", "commands") == Path(
        ".claude/commands/cry-python-review.md"
    )


def test_transversal_artifact_stays_directly_under_subclade() -> None:
    source = Path(
        "en/engineering/frontend/lexis/lex-frontend-accessibility.md"
    )

    assert build_cursor_path(source, "lex", "rules") == Path(
        ".cursor/rules/engineering/frontend/lex-frontend-accessibility.mdc"
    )
