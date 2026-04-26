# Ahrena — Cries Catalog

All **31** high-level commands in the Ahrena framework (including the sample template).

> Cries are user-facing entry points — the `/command` you type to trigger a capability. Each Cry invokes either a Kata (one-to-one) or a Warrior (which orchestrates multiple Katas).
>
> **Links** point to the English version in `framework/en/`. Every Cry also exists in `framework/pt-BR/` and `framework/es/`.

---

## `_foundation / authoring`

| Artifact | Invokes | Description | Framework |
|---|---|---|---|
| `cry-diff-artifacts` | `kata-diff-artifacts` | Compare two framework artifact versions and produce a diff report | [en](../../framework/en/_foundation/authoring/cries/cry-diff-artifacts.md) |
| `cry-new-codex` | `kata-create-codex` | Create a new Codex artifact from the official template | [en](../../framework/en/_foundation/authoring/cries/cry-new-codex.md) |
| `cry-new-cry` | `kata-create-cry` | Create a new Cry artifact from the official template | [en](../../framework/en/_foundation/authoring/cries/cry-new-cry.md) |
| `cry-new-kata` | `kata-create-kata` | Create a new Kata artifact from the official template | [en](../../framework/en/_foundation/authoring/cries/cry-new-kata.md) |
| `cry-new-lex` | `kata-create-lexis` | Create a new Lexis artifact from the official template | [en](../../framework/en/_foundation/authoring/cries/cry-new-lex.md) |
| `cry-new-warrior` | `kata-create-warrior` | Create a new Warrior artifact from the official template | [en](../../framework/en/_foundation/authoring/cries/cry-new-warrior.md) |
| `cry-push-to-framework` | `kata-push-to-framework` | Push a local artifact to the canonical framework repository | [en](../../framework/en/_foundation/authoring/cries/cry-push-to-framework.md) |

---

## `_foundation / contributing`

| Artifact | Invokes | Description | Framework |
|---|---|---|---|
| `cry-commit` | `kata-commit` | Create a Conventional Commits-compliant, GPG-signed commit | [en](../../framework/en/_foundation/contributing/cries/cry-commit.md) |
| `cry-contribute` | `kata-contribute` | Run the full contribution flow for an open-source contribution | [en](../../framework/en/_foundation/contributing/cries/cry-contribute.md) |
| `cry-new-discuss` | `kata-contributing-discuss` | Open a discussion issue in a Guardia repository | [en](../../framework/en/_foundation/contributing/cries/cry-new-discuss.md) |
| `cry-new-epic` | `kata-contributing-issue` | Create a new epic issue using the approved epic template | [en](../../framework/en/_foundation/contributing/cries/cry-new-epic.md) |
| `cry-new-feature-request` | `kata-contributing-issue` | Create a new feature request issue using the approved template | [en](../../framework/en/_foundation/contributing/cries/cry-new-feature-request.md) |
| `cry-new-pr` | `kata-contributing-pr` | Open a pull request following Guardia conventions | [en](../../framework/en/_foundation/contributing/cries/cry-new-pr.md) |
| `cry-new-simple-task` | `kata-contributing-issue` | Create a simple task issue (chore, refactoring, docs, CI) | [en](../../framework/en/_foundation/contributing/cries/cry-new-simple-task.md) |
| `cry-new-user-story-api` | `kata-contributing-issue` | Create an API-focused user story issue with acceptance criteria | [en](../../framework/en/_foundation/contributing/cries/cry-new-user-story-api.md) |
| `cry-new-user-story-frontend` | `kata-contributing-issue` | Create a frontend user story issue with acceptance criteria | [en](../../framework/en/_foundation/contributing/cries/cry-new-user-story-frontend.md) |
| `cry-rebase` | `kata-contribute` | Rebase the current branch on `main` | [en](../../framework/en/_foundation/contributing/cries/cry-rebase.md) |
| `cry-sync` | `kata-contribute` | Sync the current branch with the upstream remote | [en](../../framework/en/_foundation/contributing/cries/cry-sync.md) |
| `cry-tag` | `kata-tag` | Create a SemVer-compliant, GPG-signed release tag | [en](../../framework/en/_foundation/contributing/cries/cry-tag.md) |

---

## `_foundation / tooling`

| Artifact | Invokes | Description | Framework |
|---|---|---|---|
| `cry-make` | `kata-make-*` | Run Makefile commands for framework operations (install, update, sync, clean) | [en](../../framework/en/_foundation/tooling/cries/cry-make.md) |

---

## `documentation / i18n`

| Artifact | Invokes | Description | Framework |
|---|---|---|---|
| `cry-translate` | `warrior-translator` | Translate an Ahrena artifact to all required languages | [en](../../framework/en/documentation/i18n/cries/cry-translate.md) |

---

## `engineering / backend`

| Artifact | Invokes | Description | Framework |
|---|---|---|---|
| `cry-python-implement` | `warrior-apollo` | Implement a Python feature following all platform standards | [en](../../framework/en/engineering/backend/cries/cry-python-implement.md) |
| `cry-python-review` | `warrior-apollo` | Review Python code for quality, security, typing, and compliance | [en](../../framework/en/engineering/backend/cries/cry-python-review.md) |

---

## `engineering / platform`

| Artifact | Invokes | Description | Framework |
|---|---|---|---|
| `cry-api-design` | `warrior-daedalus` | Run the API design flow: brief → requirements → OAS → review | [en](../../framework/en/engineering/platform/cries/cry-api-design.md) |
| `cry-event-storm` | `warrior-kronos` | Run an event storming session and document domain events and CloudEvents | [en](../../framework/en/engineering/platform/cries/cry-event-storm.md) |
| `cry-feature-design` | `warrior-prometheus` | Run the feature design cycle: domain model → API design → event documentation | [en](../../framework/en/engineering/platform/cries/cry-feature-design.md) |
| `cry-full-design` | `warrior-prometheus` | Run the complete platform design cycle from discovery to full documentation | [en](../../framework/en/engineering/platform/cries/cry-full-design.md) |

---

## `engineering / workflow`

| Artifact | Invokes | Description | Framework |
|---|---|---|---|
| `cry-docs-serve` | `kata-docs-serve` | Serve project documentation locally for review | [en](../../framework/en/engineering/workflow/cries/cry-docs-serve.md) |
| `cry-implement-issue` | `warrior-athena` | Run the full Issue-Driven Development flow for a GitHub issue (all 7 phases, 2 gates) | [en](../../framework/en/engineering/workflow/cries/cry-implement-issue.md) |

---

## Sample

| Artifact | Description | Framework |
|---|---|---|
| `cry-sample` | Official template for creating new Cries — structure, frontmatter, invocation target | [en](../../framework/en/engineering/workflow/cries/cry-sample.md) |

---

## Quick Reference

| Goal | Cry |
|---|---|
| Implement a full feature end-to-end | `/cry-implement-issue {owner/repo}#{n}` |
| Design a new platform feature | `/cry-full-design` or `/cry-feature-design` |
| Design a new API | `/cry-api-design` |
| Run event storming | `/cry-event-storm` |
| Implement a Python service | `/cry-python-implement` |
| Review Python code | `/cry-python-review` |
| Translate an artifact | `/cry-translate` |
| Create a new issue | `/cry-new-feature-request`, `/cry-new-user-story-api`, `/cry-new-epic` |
| Open a PR | `/cry-new-pr` |
| Create a release tag | `/cry-tag` |
| Create a new Lexis | `/cry-new-lex` |
| Create a new Kata | `/cry-new-kata` |
