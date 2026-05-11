---
paths:
  - 'package.json'
  - '**/__version__.py'
  - '**/version.txt'
  - 'CHANGELOG*'
  - '.bumpversion*'
  - 'pyproject.toml'
---

# Lexis: Mandatory Semantic Versioning

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Versions and release tags in Guardia repositories

## Law

> **Every release version identifier and every release tag MUST follow Semantic Versioning 2.0 (MAJOR.MINOR.PATCH). No exception.**

## Rules

### 1. Mandatory format

The version identifier MUST be in the form `X.Y.Z`, where:

- **MAJOR (X):** non-negative integer; incremented when there are incompatible API changes
- **MINOR (Y):** non-negative integer; incremented when new backward-compatible functionality is added
- **PATCH (Z):** non-negative integer; incremented when backward-compatible fixes are made

### 2. Tags in Git

Tags used to mark releases MUST use the SemVer format. The `v` prefix is recommended for tool compatibility (e.g. `v1.2.3`). The variants `v1.2.3` and `1.2.3` are accepted; the project MUST adopt one convention and keep it consistent.

### 3. Signed and annotated release tags

Release tags MUST also be signed with GPG, as per `lex-signed-commits`, and annotated (`git tag -a -s`), as per `lex-annotated-tags`. Lightweight tags cannot carry a signature — only annotated tags support GPG.

### 4. Pre-release and metadata

Pre-release identifiers (e.g. `v1.2.3-alpha.1`) and build metadata (e.g. `v1.2.3+build.42`) follow the SemVer 2.0 specification and are allowed when documented in `codex-semantic-version`.

## Examples

### Correct

```
v1.0.0
v2.1.3
1.0.0
v1.2.3-alpha.1
v1.2.3+build.42
```

### Incorrect

```
release-1.2      # not MAJOR.MINOR.PATCH
1.2              # PATCH missing
v1.2.3.4         # more than three numeric segments (unless pre-release/metadata per SemVer)
latest           # non-numeric identifier for release
```

## Automated Validation

- **Tool:** regex or SemVer parser validation (e.g. in CI or pre-push hook)
- **When:** before tag push or in the release pipeline
- **Metric:** 0 release tags in invalid format tolerated
