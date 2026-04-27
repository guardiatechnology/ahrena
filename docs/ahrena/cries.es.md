# Ahrena — Catálogo de Cries

Todos los **31** comandos de alto nivel del framework Ahrena (incluida la plantilla de ejemplo).

> Los Cries son los puntos de entrada orientados al usuario — el `/comando` que se escribe para activar una capacidad. Cada Cry invoca un Kata (uno a uno) o un Warrior (que orquesta múltiples Katas).
>
> **Los enlaces** apuntan a la versión en inglés en `framework/en/`. Todo Cry también existe en `framework/pt-BR/` y `framework/es/`.

---

## `_foundation / authoring`

| Artefacto | Invoca | Descripción | Framework |
|---|---|---|---|
| `cry-diff-artifacts` | `kata-diff-artifacts` | Compare two framework artifact versions and produce a diff report | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/authoring/cries/cry-diff-artifacts.md) |
| `cry-new-codex` | `kata-create-codex` | Create a new Codex artifact from the official template | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/authoring/cries/cry-new-codex.md) |
| `cry-new-cry` | `kata-create-cry` | Create a new Cry artifact from the official template | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/authoring/cries/cry-new-cry.md) |
| `cry-new-kata` | `kata-create-kata` | Create a new Kata artifact from the official template | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/authoring/cries/cry-new-kata.md) |
| `cry-new-lex` | `kata-create-lexis` | Create a new Lexis artifact from the official template | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/authoring/cries/cry-new-lex.md) |
| `cry-new-warrior` | `kata-create-warrior` | Create a new Warrior artifact from the official template | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/authoring/cries/cry-new-warrior.md) |
| `cry-push-to-framework` | `kata-push-to-framework` | Push a local artifact to the canonical framework repository | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/authoring/cries/cry-push-to-framework.md) |

---

## `_foundation / contributing`

| Artefacto | Invoca | Descripción | Framework |
|---|---|---|---|
| `cry-commit` | `kata-commit` | Create a Conventional Commits-compliant, GPG-signed commit | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/contributing/cries/cry-commit.md) |
| `cry-contribute` | `kata-contribute` | Run the full contribution flow for an open-source contribution | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/contributing/cries/cry-contribute.md) |
| `cry-new-discuss` | `kata-contributing-discuss` | Open a discussion issue in a Guardia repository | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/contributing/cries/cry-new-discuss.md) |
| `cry-new-epic` | `kata-contributing-issue` | Create a new epic issue using the approved epic template | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/contributing/cries/cry-new-epic.md) |
| `cry-new-feature-request` | `kata-contributing-issue` | Create a new feature request issue using the approved template | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/contributing/cries/cry-new-feature-request.md) |
| `cry-new-pr` | `kata-contributing-pr` | Open a pull request following Guardia conventions | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/contributing/cries/cry-new-pr.md) |
| `cry-new-simple-task` | `kata-contributing-issue` | Create a simple task issue (chore, refactoring, docs, CI) | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/contributing/cries/cry-new-simple-task.md) |
| `cry-new-user-story-api` | `kata-contributing-issue` | Create an API-focused user story issue with acceptance criteria | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/contributing/cries/cry-new-user-story-api.md) |
| `cry-new-user-story-frontend` | `kata-contributing-issue` | Create a frontend user story issue with acceptance criteria | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/contributing/cries/cry-new-user-story-frontend.md) |
| `cry-rebase` | `kata-contribute` | Rebase the current branch on `main` | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/contributing/cries/cry-rebase.md) |
| `cry-sync` | `kata-contribute` | Sync the current branch with the upstream remote | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/contributing/cries/cry-sync.md) |
| `cry-tag` | `kata-tag` | Create a SemVer-compliant, GPG-signed release tag | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/contributing/cries/cry-tag.md) |

---

## `_foundation / tooling`

| Artefacto | Invoca | Descripción | Framework |
|---|---|---|---|
| `cry-make` | `kata-make-*` | Run Makefile commands for framework operations (install, update, sync, clean) | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/tooling/cries/cry-make.md) |

---

## `documentation / i18n`

| Artefacto | Invoca | Descripción | Framework |
|---|---|---|---|
| `cry-translate` | `warrior-translator` | Translate an Ahrena artifact to all required languages | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/documentation/i18n/cries/cry-translate.md) |

---

## `engineering / backend`

| Artefacto | Invoca | Descripción | Framework |
|---|---|---|---|
| `cry-python-implement` | `warrior-apollo` | Implement a Python feature following all platform standards | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/backend/cries/cry-python-implement.md) |
| `cry-python-review` | `warrior-apollo` | Review Python code for quality, security, typing, and compliance | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/backend/cries/cry-python-review.md) |

---

## `engineering / platform`

| Artefacto | Invoca | Descripción | Framework |
|---|---|---|---|
| `cry-api-design` | `warrior-daedalus` | Run the API design flow: brief → requirements → OAS → review | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/platform/cries/cry-api-design.md) |
| `cry-event-storm` | `warrior-kronos` | Run an event storming session and document domain events and CloudEvents | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/platform/cries/cry-event-storm.md) |
| `cry-feature-design` | `warrior-prometheus` | Run the feature design cycle: domain model → API design → event documentation | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/platform/cries/cry-feature-design.md) |
| `cry-full-design` | `warrior-prometheus` | Run the complete platform design cycle from discovery to full documentation | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/platform/cries/cry-full-design.md) |

---

## `engineering / workflow`

| Artefacto | Invoca | Descripción | Framework |
|---|---|---|---|
| `cry-docs-serve` | `kata-docs-serve` | Serve project documentation locally for review | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/workflow/cries/cry-docs-serve.md) |
| `cry-implement-issue` | `warrior-athena` | Run the full Issue-Driven Development flow for a GitHub issue (all 7 phases, 2 gates) | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/workflow/cries/cry-implement-issue.md) |

---

## Ejemplo

| Artefacto | Descripción | Framework |
|---|---|---|
| `cry-sample` | Official template for creating new Cries — structure, frontmatter, invocation target | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/workflow/cries/cry-sample.md) |

---

## Referencia Rápida

| Objetivo | Cry |
|---|---|
| Implementar una feature completa de extremo a extremo | `/cry-implement-issue {owner/repo}#{n}` |
| Diseñar una nueva feature de plataforma | `/cry-full-design` o `/cry-feature-design` |
| Diseñar una nueva API | `/cry-api-design` |
| Ejecutar event storming | `/cry-event-storm` |
| Implementar un servicio Python | `/cry-python-implement` |
| Revisar código Python | `/cry-python-review` |
| Traducir un artefacto | `/cry-translate` |
| Crear una nueva issue | `/cry-new-feature-request`, `/cry-new-user-story-api`, `/cry-new-epic` |
| Abrir un PR | `/cry-new-pr` |
| Crear una tag de release | `/cry-tag` |
| Crear una nueva Lexis | `/cry-new-lex` |
| Crear un nuevo Kata | `/cry-new-kata` |
