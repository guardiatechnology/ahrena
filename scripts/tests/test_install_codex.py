"""Tests for the native OpenAI Codex platform projection."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from install import (  # noqa: E402
    AHRENA_CODEX_MARKER_END,
    AHRENA_CODEX_MARKER_START,
    _process_lang_dir_to_codex,
    clean,
    generate_codex_agents_md,
    install_codex_mcp,
    transform_md_to_codex_agent,
    transform_md_to_codex_skill,
)


def test_codex_agent_is_valid_toml() -> None:
    rendered = transform_md_to_codex_agent(
        "# Warrior Test\n\n> Scope: Review safely.\n\n## Instructions\n\nBe precise.\n",
        "warrior",
        "warrior-test.md",
    )
    parsed = tomllib.loads(rendered)
    assert parsed["name"] == "warrior-test"
    assert "Be precise" in parsed["developer_instructions"]


def test_codex_skill_has_discovery_frontmatter() -> None:
    rendered = transform_md_to_codex_skill(
        "# Kata Test\n\n> Scope: Run the test.\n\n## Steps\n\n1. Execute.\n",
        "kata",
        "kata-test.md",
    )
    assert rendered.startswith("---\nname: kata-test\ndescription:")
    assert "## Steps" in rendered


def test_agents_md_preserves_user_content_and_is_idempotent(tmp_path: Path) -> None:
    path = tmp_path / "AGENTS.md"
    path.write_text("# Project rules\n\nKeep this.\n", encoding="utf-8")
    generate_codex_agents_md(tmp_path)
    generate_codex_agents_md(tmp_path)
    content = path.read_text(encoding="utf-8")
    assert "Keep this." in content
    assert content.count(AHRENA_CODEX_MARKER_START) == 1
    assert content.count(AHRENA_CODEX_MARKER_END) == 1


def test_projection_writes_docs_skills_and_agents(tmp_path: Path) -> None:
    base = tmp_path / "framework"
    lang = base / "en" / "engineering" / "test"
    fixtures = {
        "lexis/lex-law.md": "# Law\n\nMandatory.\n",
        "codex/codex-manual.md": "# Manual\n\nReference.\n",
        "katas/kata-run.md": "# Run\n\nRun it.\n",
        "warriors/warrior-reviewer.md": "# Reviewer\n\nReview it.\n",
        "cries/cry-check.md": "# Check\n\nCheck it.\n",
    }
    for relative, content in fixtures.items():
        path = lang / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    config = {"transposition": {
        "lex": "docs", "codex": "docs", "kata": "skills",
        "warrior": "agents", "cry": "skills",
    }}
    counts = _process_lang_dir_to_codex(base / "en", base, tmp_path, False, config)
    assert counts == (2, 2, 1)
    assert (tmp_path / ".codex/docs/lex/engineering/test/lex-law.md").exists()
    assert (tmp_path / ".agents/skills/kata-run/SKILL.md").exists()
    agent = tmp_path / ".codex/agents/warrior-reviewer.toml"
    with agent.open("rb") as stream:
        assert tomllib.load(stream)["name"] == "warrior-reviewer"


def test_codex_mcp_config_is_valid_and_preserves_project_config(tmp_path: Path) -> None:
    ahrena = tmp_path / ".ahrena"
    mcp_dir = ahrena / "framework" / "mcp"
    mcp_dir.mkdir(parents=True)
    (mcp_dir / "local.json").write_text(
        '{"claude-code":{"command":"tool","args":["--root","${workspaceFolder}"],'
        '"env":{"TOKEN":"${TOKEN}"}}}',
        encoding="utf-8",
    )
    config = tmp_path / ".codex" / "config.toml"
    config.parent.mkdir(parents=True)
    config.write_text('model = "project-choice"\n', encoding="utf-8")
    directives = {"mcp": {"servers": ["local"]}}
    install_codex_mcp(ahrena, tmp_path, directives)
    install_codex_mcp(ahrena, tmp_path, directives)
    parsed = tomllib.loads(config.read_text(encoding="utf-8"))
    assert parsed["model"] == "project-choice"
    assert parsed["mcp_servers"]["local"]["args"] == ["--root", "."]
    assert parsed["mcp_servers"]["local"]["env_vars"] == ["TOKEN"]


def test_clean_removes_only_ahrena_codex_docs(tmp_path: Path) -> None:
    docs = tmp_path / ".codex" / "docs"
    generated = docs / "lex" / "engineering" / "lex-law.md"
    project_owned = docs / "project-notes.md"
    generated.parent.mkdir(parents=True)
    generated.write_text("generated\n", encoding="utf-8")
    project_owned.write_text("owned\n", encoding="utf-8")
    clean(tmp_path)
    assert not generated.exists()
    assert project_owned.read_text(encoding="utf-8") == "owned\n"
