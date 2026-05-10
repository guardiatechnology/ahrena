"""Smoke tests against the live framework/ in this repo."""

from pathlib import Path

import pytest

from ahrena_mcp.loader import FrameworkLoader
from ahrena_mcp.search import search as fw_search

# tools/ahrena-mcp/tests/test_smoke.py -> repo root is 3 parents up
REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module")
def loader() -> FrameworkLoader:
    return FrameworkLoader(REPO_ROOT)


def test_loader_finds_lex_directives_in_some_lang(loader: FrameworkLoader) -> None:
    found = False
    for lang in loader.available_languages():
        if loader.get("lex-directives", lang):
            found = True
            break
    assert found, "lex-directives must exist in at least one language"


def test_loader_classifies_pilar_correctly(loader: FrameworkLoader) -> None:
    for lang in loader.available_languages():
        artifact = loader.get("lex-directives", lang)
        if artifact:
            assert artifact.pilar == "lexis"
            assert artifact.clade == "_foundation"
            return
    pytest.fail("no lex-directives found anywhere")


def test_loader_returns_content(loader: FrameworkLoader) -> None:
    for lang in loader.available_languages():
        artifact = loader.get("lex-directives", lang)
        if artifact:
            content = loader.get_content(artifact)
            assert content
            assert ".directives" in content
            return
    pytest.fail("no lex-directives found anywhere")


def test_search_finds_idempotency(loader: FrameworkLoader) -> None:
    found_any = False
    for lang in loader.available_languages():
        hits = fw_search(loader, "idempotency", lang=lang, limit=10)
        if hits:
            found_any = True
            assert all(h.score > 0 for h in hits)
            assert all(h.lang == lang for h in hits)
            break
    assert found_any, "search must find at least one idempotency hit"


def test_search_filters_by_pilar(loader: FrameworkLoader) -> None:
    for lang in loader.available_languages():
        hits = fw_search(loader, "idempotency", pilar="lexis", lang=lang, limit=10)
        if hits:
            assert all(h.pilar == "lexis" for h in hits)
            return


def test_unknown_ref_returns_none(loader: FrameworkLoader) -> None:
    assert loader.get("lex-bogus-doesnt-exist-xyz", "pt-BR") is None


def test_iter_pilar_returns_only_pilar(loader: FrameworkLoader) -> None:
    for lang in loader.available_languages():
        items = list(loader.iter_pilar("lexis", lang=lang))
        if items:
            assert all(a.pilar == "lexis" for a in items)
            assert all(a.name.startswith("lex-") for a in items)
            return
    pytest.fail("no lexis found in any language")


def test_available_languages_nonempty(loader: FrameworkLoader) -> None:
    langs = loader.available_languages()
    assert langs, "framework must have at least one language"


def test_search_empty_query_returns_empty(loader: FrameworkLoader) -> None:
    assert fw_search(loader, "   ", limit=10) == []
