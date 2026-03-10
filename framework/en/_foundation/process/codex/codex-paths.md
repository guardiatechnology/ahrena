# Codex: Canonical Framework Paths

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Use of paths in the Ahrena framework

## Overview

This Codex describes the canonical paths defined in the `paths` section of `.ahrena/.directives`. It explains when to use each path, when to create artifacts in `project_artifacts` instead of the framework, and how the install and update scripts use these paths. Consult `lex-directives` for the obligation to use canonical paths; consult `codex-directives` for the meaning of each key in `.directives`.

## Context

- **Domain:** Framework paths and project vs framework flow
- **Audience:** AI agents that create or reference artifacts; maintainers and integrators
- **Update:** When new paths are added to `.directives` or the project/framework flow changes

## Content

### Main paths

| Path | Where it exists | Use |
|------|-----------------|-----|
| `paths.root` | In every project that adopts Ahrena | Framework root in the project — `.ahrena/`. Scripts (install, update, uninstall) and Makefile are copied or referenced from here. |
| `paths.directives` | Inside `paths.root` | File `.ahrena/.directives`. Source of truth for paths, language, terminal, naming. |
| `paths.templates` | In the Ahrena repository (source repo) | Folder `templates/` with lex-sample.md, codex-sample.md, etc. Used by the installer and by agents when creating artifacts (via `paths.samples.*`). |
| `paths.framework` | In the Ahrena repository | Folder `framework/` with the tree by language (pt-BR, es, en) and by clade/subclade/pilar. In a consumer project, may be a copy in `.ahrena/framework/` after installation. |
| `paths.project_artifacts` | In the project that adopts Ahrena | `.ahrena/artifacts/`. Artifacts created here are project-specific and may be validated before being incorporated into the framework. |

### Destination paths (specifications and documentation)

| Path | Use |
|------|-----|
| `paths.oas` | Directory for OpenAPI specifications and API document (e.g. `docs/oas`). Created by the agent or installer if missing. API design Katas and Warriors write here. |
| `paths.events` | Directory for event documentation (CloudEvents) (e.g. `docs/events`). Created by the agent or installer if missing. |

### Template paths (samples)

| Path | Content |
|------|----------|
| `paths.samples.lexis` | Official Lexis template (e.g. `templates/lex-sample.md`) |
| `paths.samples.codex` | Official Codex template |
| `paths.samples.katas` | Official Katas template |
| `paths.samples.warriors` | Official Warriors template |
| `paths.samples.cries` | Official Cries template |

When creating a new artifact, the agent must load the corresponding template from the path defined in `.directives` (or the default value documented in `codex-directives`). Paths are typically relative to the framework repository (e.g. `templates/lex-sample.md`).

### When to use project_artifacts vs framework

| Situation | Where to create | Rationale |
|-----------|-----------------|-----------|
| Artifact under validation; may never go to framework | `paths.project_artifacts` | Local iteration without polluting the canonical framework |
| Stable artifact approved for the Ahrena repository | `paths.framework` (in the framework repo) | Part of the shared tree; must exist in all languages in `language.i18n` |
| Contributor working in the Ahrena repo | Directly in `framework/` in the repo | Does not use `project_artifacts`; edits the canonical tree |
| Consumer who wants to propose an artifact to the framework | Create in `project_artifacts`, then use `kata-push-to-framework` | Recommended flow in `codex-pilars` |

### Use by scripts

- **install.py / update.py:** Read `paths` (implicit when reading `.directives`) to know where to copy the framework, templates, and where to generate `.cursor/` when `--platform cursor` is used.
- **kata-push-to-framework:** Copies from `paths.project_artifacts` to `paths.framework` (local mode) or sends changes to the remote framework repository (remote mode).

## Glossary

| Term | Definition |
|------|------------|
| Canonical path | Path defined in `.ahrena/.directives` under the `paths` section; all agents must use it when referencing or creating artifacts |
| Consumer project | Repository that has installed Ahrena (via install.py or Makefile) and may have `.ahrena/framework/` and `.ahrena/artifacts/` |
| Framework repo | Repository that contains the canonical `framework/` and `templates/` tree |

## References

- `lex-directives` — Obligation to use canonical paths
- `codex-directives` — Manual for the `.directives` file (paths section)
- `codex-pilars` — Artifact flow in the project and Push to the framework
- `.ahrena/.directives` — Source of path values
