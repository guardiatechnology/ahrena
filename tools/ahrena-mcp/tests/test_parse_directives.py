"""Regression tests for scripts/install.py parse_directives().

The custom YAML-like parser must handle the nested-list shape used by
.directives.sample:

    mcp:
      servers:
        - ahrena

The previous implementation returned `{"servers": {}}` for `mcp` (empty
dict instead of list), which silently disabled the install_mcp_package
default-on flow.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
INSTALL_PY = REPO_ROOT / "scripts" / "install.py"


@pytest.fixture(scope="module")
def parse():
    spec = importlib.util.spec_from_file_location("ahrena_install_parse", INSTALL_PY)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["ahrena_install_parse"] = module
    spec.loader.exec_module(module)
    return module.parse_directives


def test_nested_list_under_two_levels(parse) -> None:
    """`mcp.servers: [ahrena]` — the exact shape that broke default-on."""
    content = (
        "mcp:\n"
        "  servers:\n"
        "    - ahrena\n"
    )
    parsed = parse(content)
    assert parsed == {"mcp": {"servers": ["ahrena"]}}


def test_nested_list_with_comments_interleaved(parse) -> None:
    """Comments inside the list body must not break parsing."""
    content = (
        "mcp:\n"
        "  servers:\n"
        "    - ahrena\n"
        "    # - github\n"
        "    # - notion\n"
    )
    parsed = parse(content)
    assert parsed["mcp"]["servers"] == ["ahrena"]


def test_multiple_list_items(parse) -> None:
    content = (
        "mcp:\n"
        "  servers:\n"
        "    - ahrena\n"
        "    - github\n"
        "    - notion\n"
    )
    parsed = parse(content)
    assert parsed["mcp"]["servers"] == ["ahrena", "github", "notion"]


def test_list_does_not_pollute_following_dict_section(parse) -> None:
    content = (
        "mcp:\n"
        "  servers:\n"
        "    - ahrena\n"
        "language:\n"
        "  default: pt-BR\n"
    )
    parsed = parse(content)
    assert parsed["mcp"]["servers"] == ["ahrena"]
    assert parsed["language"]["default"] == "pt-BR"


def test_quoted_list_items_lose_quotes(parse) -> None:
    content = (
        "mcp:\n"
        "  servers:\n"
        '    - "ahrena"\n'
        "    - 'github'\n"
    )
    parsed = parse(content)
    assert parsed["mcp"]["servers"] == ["ahrena", "github"]


def test_flat_scalar_keys_still_parse(parse) -> None:
    """Regression: don't break the simpler scalar case the old parser handled."""
    content = (
        "paths:\n"
        '  root: ".ahrena/"\n'
        '  framework: "framework/"\n'
    )
    parsed = parse(content)
    assert parsed["paths"]["root"] == ".ahrena/"
    assert parsed["paths"]["framework"] == "framework/"


def test_three_level_nesting_still_works(parse) -> None:
    content = (
        "naming:\n"
        "  prefixes:\n"
        "    lexis: lex-\n"
        "    codex: codex-\n"
    )
    parsed = parse(content)
    assert parsed["naming"]["prefixes"]["lexis"] == "lex-"
    assert parsed["naming"]["prefixes"]["codex"] == "codex-"


def test_empty_input_returns_empty_dict(parse) -> None:
    assert parse("") == {}
    assert parse("# just a comment\n# nothing else\n") == {}
