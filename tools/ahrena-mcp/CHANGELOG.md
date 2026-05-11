# Changelog

All notable changes to `ahrena-mcp` are documented here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [SemVer](https://semver.org).

## [Unreleased]

## [0.1.0a1] - 2026-05-10

### Added
- Initial alpha of the Ahrena MCP server (read-only, stdio transport, FastMCP-based).
- Loader that walks `framework/{lang}/` and indexes artifacts by `(lang, name)` with `mtime` cache invalidation.
- Search via ripgrep shell-out with Python regex fallback.
- Seven tools: `ahrena_query_lex`, `ahrena_get_codex`, `ahrena_list_warriors`, `ahrena_list_cries`, `ahrena_search`, `ahrena_resolve_ref`, `ahrena_get_directives`.
- Smoke tests (pytest) covering loader, search, and pilar filtering against the live framework.
- `.github/workflows/release.yml` extended: the same `v*` tag that releases the framework now also builds the `ahrena-mcp` wheel + sdist and attaches them to the same GitHub Release.

### Notes
- Distribution channel for v1: GitHub Releases only (wheel + sdist attached to the tag). PyPI publishing remains deferred per `.claude/plans/plan-021-ahrena-mcp-server.md` §Release & Distribution.
- `ahrena_get_topology` deferred until `docs/internal/warrior-topology-2026.md` exists (plan-011 dependency).
- Framework and `ahrena-mcp` ship in the **same** GitHub Release (single `v*` tag). The MCP keeps its own version inside the wheel filename (`ahrena_mcp-0.1.0a1-py3-none-any.whl`), so identities stay independent even when bundled.
