# Changelog

All notable changes to `ahrena-mcp` are documented here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [SemVer](https://semver.org).

## [Unreleased]

### Added
- Initial spike of the Ahrena MCP server (read-only, stdio transport, FastMCP-based).
- Loader that walks `framework/{lang}/` and indexes artifacts by `(lang, name)` with `mtime` cache invalidation.
- Search via ripgrep shell-out with Python regex fallback.
- Seven tools: `ahrena_query_lex`, `ahrena_get_codex`, `ahrena_list_warriors`, `ahrena_list_cries`, `ahrena_search`, `ahrena_resolve_ref`, `ahrena_get_directives`.
- Smoke tests (pytest) covering loader, search, and pilar filtering against the live framework.

### Notes
- Not yet released. First tag will be `v0.1.0a1` per `.claude/plans/plan-021-ahrena-mcp-server.md` §Release & Distribution.
- `ahrena_get_topology` deferred until `docs/internal/warrior-topology-2026.md` exists (plan-011 dependency).
