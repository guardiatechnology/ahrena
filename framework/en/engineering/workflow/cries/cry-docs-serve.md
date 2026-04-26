# Cry: cry-docs-serve

> **Prefix:** `cry-` | **Type:** Execution Command | **Scope:** Local MkDocs documentation server for any Markdown directory

## Description

Starts a local MkDocs documentation server to browse `.md` files as a navigable site at `http://127.0.0.1:8000`. Accepts an optional `docs-path` to serve any directory instead of the one derived from `.directives` — useful for projects where the documentation directory is not `docs/` (e.g., in the Ahrena repository the framework directory itself is the documentation).

## When to Use

- After running `cry-feature-design`, `cry-api-design`, or `cry-event-storm`, to review the generated documents as a unified site
- When you want to browse domain models, API specs, and event documents locally before committing
- When the project documentation lives outside `docs/` (e.g., `framework/` in Ahrena)

## Syntax

```
/cry-docs-serve [docs-path] [port]
```

## Parameters

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `docs-path` | No | Path to the directory to serve (e.g., `framework/`, `docs/`). If omitted, the path is derived from `.directives` (`paths.domain`, `paths.oas`, `paths.events`). |
| `port` | No | Port to bind the server. Default: `8000`. |

## Invokes

| Kata | Description |
|------|-------------|
| `kata-docs-serve` | Verifies MkDocs installation, resolves `docs_dir`, generates `mkdocs.yml` if absent, and starts the server |

## Examples

```
/cry-docs-serve
```
Derives the documentation directory from `.directives` and serves it at `http://127.0.0.1:8000`.

---

```
/cry-docs-serve framework/
```
Serves the `framework/` directory at `http://127.0.0.1:8000`. Use this in the Ahrena repository, where the framework itself is the documentation.

---

```
/cry-docs-serve docs/
```
Explicitly serves `docs/` at `http://127.0.0.1:8000`.

---

```
/cry-docs-serve framework/ 8080
```
Serves `framework/` at `http://127.0.0.1:8080`.

## Deliverable

A running MkDocs server accessible at `http://127.0.0.1:{port}` serving all `.md` files in the specified or derived directory, with hot-reload on file changes.

## Notes

- The server runs in the foreground; stop it with `Ctrl+C`.
- When `docs-path` is omitted, the common parent of `paths.domain`, `paths.oas`, and `paths.events` in `.directives` is used.
- If `mkdocs.yml` does not exist at the project root, a minimal one is generated automatically (never overwrites an existing file).
- The Material theme (`mkdocs-material`) is used when available; falls back to the default MkDocs theme.

## References

- `kata-docs-serve` — procedure this cry delegates to
- `lex-directives` — canonical paths read when `docs-path` is omitted
