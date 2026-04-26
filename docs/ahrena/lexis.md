# Ahrena — Catálogo de Lexis

Todas as **39** leis invioláveis do framework Ahrena.

> **Os links** apontam para a versão em inglês em `framework/en/`. Toda Lexis também existe em `framework/pt-BR/` e `framework/es/`.

---

## `_foundation / authoring`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-pilars` | Defines the 5 Pilars, their canonical rules, and the invocation hierarchy (Lexis → Codex → Katas → Warriors → Cries) | [en](../../framework/en/_foundation/authoring/lexis/lex-pilars.md) |

---

## `_foundation / contributing`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-commit-language` | Commit subject must be in English; body may include other languages with `[lang]` tag | [en](../../framework/en/_foundation/contributing/lexis/lex-commit-language.md) |
| `lex-conventional-commits` | Every commit must follow Conventional Commits format `<type>[scope]: <description>` | [en](../../framework/en/_foundation/contributing/lexis/lex-conventional-commits.md) |
| `lex-git-branches` | Branch names must follow `{type}/{issue-number}-{kebab-slug}` format | [en](../../framework/en/_foundation/contributing/lexis/lex-git-branches.md) |
| `lex-issue-first` | Every code change must originate from an existing GitHub Issue | [en](../../framework/en/_foundation/contributing/lexis/lex-issue-first.md) |
| `lex-issue-quality` | Every issue must use an approved template and explicitly answer Why / What / How | [en](../../framework/en/_foundation/contributing/lexis/lex-issue-quality.md) |
| `lex-semantic-version` | Every release version must follow SemVer 2.0 (MAJOR.MINOR.PATCH) | [en](../../framework/en/_foundation/contributing/lexis/lex-semantic-version.md) |
| `lex-signed-commits` | Every commit must be signed with a GPG key and verified by GitHub | [en](../../framework/en/_foundation/contributing/lexis/lex-signed-commits.md) |
| `lex-small-commits` | Every commit must be atomic — one logical change per commit | [en](../../framework/en/_foundation/contributing/lexis/lex-small-commits.md) |

---

## `_foundation / i18n`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-framework-language` | Language is the first navigation level within `framework/`; every artifact must exist in all required languages | [en](../../framework/en/_foundation/i18n/lexis/lex-framework-language.md) |

---

## `_foundation / process`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-checkpoint` | Agents check `.checkpoint` before starting any activity and save it when concluding | [en](../../framework/en/_foundation/process/lexis/lex-checkpoint.md) |
| `lex-directives` | Agents must read `.ahrena/.directives` before any artifact-producing activity | [en](../../framework/en/_foundation/process/lexis/lex-directives.md) |
| `lex-naming` | Artifacts follow the naming conventions defined in `.ahrena/.directives` (prefix, casing, addressing) | [en](../../framework/en/_foundation/process/lexis/lex-naming.md) |
| `lex-platforms-rules` | Every Lexis and Codex must have an entry with `description` in `framework/platforms.yaml` | [en](../../framework/en/_foundation/process/lexis/lex-platforms-rules.md) |

---

## `_foundation / quality`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-observability-required` | Every new endpoint, consumer, or job must emit a distributed trace, latency metric, and structured log with correlation ID | [en](../../framework/en/_foundation/quality/lexis/lex-observability-required.md) |
| `lex-template-usage` | Agents use the official Pilar template as structural base when creating any new artifact | [en](../../framework/en/_foundation/quality/lexis/lex-template-usage.md) |
| `lex-tone` | Agents apply the tone and writing style defined in `.ahrena/.directives` in all artifacts and communication | [en](../../framework/en/_foundation/quality/lexis/lex-tone.md) |

---

## `_foundation / tooling`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-mcp` | Use the available MCP tool when an active server provides the capability; credentials exclusively via environment variables | [en](../../framework/en/_foundation/tooling/lexis/lex-mcp.md) |
| `lex-terminal-type` | Use the terminal type (bash or PowerShell) defined in `.ahrena/.directives`; infer from OS if not set | [en](../../framework/en/_foundation/tooling/lexis/lex-terminal-type.md) |

---

## `design / brand`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-brand-colors` | Official Guardia palette only; WCAG 2.1 AA required; Yellow 500 + White combination is forbidden | [en](../../framework/en/design/brand/lexis/lex-brand-colors.md) |
| `lex-brand-logo` | Use only official logo files; select correct variant (primary/secondary/mono) based on background | [en](../../framework/en/design/brand/lexis/lex-brand-logo.md) |
| `lex-brand-typography` | Poppins as everyday typeface; Lastica exclusive to the logo; Roboto as CSS fallback only | [en](../../framework/en/design/brand/lexis/lex-brand-typography.md) |
| `lex-brand-voice` | Direct, strategic, affirmative, clear voice; no buzzwords; positioning is "agentic accounting" | [en](../../framework/en/design/brand/lexis/lex-brand-voice.md) |

---

## `design / system`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-ai-first-experience` | Every human-facing Guardia interface uses AI-First pattern: Isac conversation as primary surface | [en](../../framework/en/design/system/lexis/lex-ai-first-experience.md) |
| `lex-design-system-library` | All interfaces consume components from `@guardia/design-system`; reimplementing primitives is forbidden | [en](../../framework/en/design/system/lexis/lex-design-system-library.md) |

---

## `documentation / i18n`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-language` | Cross-language translation rules: structural equivalence, semantic fidelity, preservation of technical elements | [en](../../framework/en/documentation/i18n/lexis/lex-language.md) |
| `lex-language-en` | Specific rules for translating to American English — voice, conciseness, modal verbs, false cognates | [en](../../framework/en/documentation/i18n/lexis/lex-language-en.md) |
| `lex-language-es` | Specific rules for translating to neutral Spanish — formality, false cognates with pt-BR | [en](../../framework/en/documentation/i18n/lexis/lex-language-es.md) |
| `lex-language-ptbr` | Specific rules for translating to Brazilian Portuguese — form of address, anglicisms, tone | [en](../../framework/en/documentation/i18n/lexis/lex-language-ptbr.md) |

---

## `engineering / backend`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-python-error-handling` | No bare `except`; exceptions must be specific; no sensitive data in error messages | [en](../../framework/en/engineering/backend/lexis/lex-python-error-handling.md) |
| `lex-python-immutability` | Dataclasses use `frozen=True` by default; no mutable default function arguments | [en](../../framework/en/engineering/backend/lexis/lex-python-immutability.md) |
| `lex-python-security` | No hardcoded secrets; SQL must be parameterized; all input validated via Pydantic at system boundaries | [en](../../framework/en/engineering/backend/lexis/lex-python-security.md) |
| `lex-python-testing` | Every behavior change has tests; mocks only at system boundaries (HTTP, DB, filesystem) | [en](../../framework/en/engineering/backend/lexis/lex-python-testing.md) |
| `lex-python-typing` | Complete type hints everywhere; mypy strict passes with zero errors; no `Any` without a justifying comment | [en](../../framework/en/engineering/backend/lexis/lex-python-typing.md) |

---

## `engineering / data`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-data-retention` | Every data class has a retention policy declared in `docs/data-retention.yaml` with automated enforcement | [en](../../framework/en/engineering/data/lexis/lex-data-retention.md) |
| `lex-migrations-reversible` | Every schema migration is automatically reversible or has a documented and tested rollback plan | [en](../../framework/en/engineering/data/lexis/lex-migrations-reversible.md) |

---

## `engineering / devops`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-aws-cost` | Cost allocation tags required on all AWS resources; budgets with alerts per environment; choices >$100/mo documented | [en](../../framework/en/engineering/devops/lexis/lex-aws-cost.md) |
| `lex-aws-iac` | All AWS resources must be provisioned via Git-versioned IaC applied through a CI/CD pipeline | [en](../../framework/en/engineering/devops/lexis/lex-aws-iac.md) |
| `lex-aws-security` | Least privilege IAM; TLS 1.2+ in transit; encryption at rest; CloudTrail multi-region enabled | [en](../../framework/en/engineering/devops/lexis/lex-aws-security.md) |

---

## `engineering / frontend`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-frontend-accessibility` | WCAG 2.1 AA minimum; keyboard navigation; ARIA states; accessible contrast; no color as sole state indicator | [en](../../framework/en/engineering/frontend/lexis/lex-frontend-accessibility.md) |
| `lex-frontend-security` | No unsanitized `innerHTML`; no secrets in client bundle; CSP configured; `rel="noopener"` on external links | [en](../../framework/en/engineering/frontend/lexis/lex-frontend-security.md) |
| `lex-frontend-testing` | Behavioral tests from user POV; accessible queries preferred (`getByRole`); mocks only at boundaries | [en](../../framework/en/engineering/frontend/lexis/lex-frontend-testing.md) |
| `lex-frontend-typing` | TypeScript `strict: true`; no implicit or unjustified `any`; API contracts typed from OAS or Zod schemas | [en](../../framework/en/engineering/frontend/lexis/lex-frontend-typing.md) |

---

## `engineering / mobile`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-mobile-offline-first` | App operates in 3 network states; UI never blocks >5s without cancel/cache alternative; sync conflicts have declared strategy | [en](../../framework/en/engineering/mobile/lexis/lex-mobile-offline-first.md) |
| `lex-mobile-platform-parity` | Every new mobile feature ships on iOS and Android in the same release (±3 business days) | [en](../../framework/en/engineering/mobile/lexis/lex-mobile-platform-parity.md) |

---

## `engineering / platform`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-auth` | API access controlled by OAuth 2.0: Client Credentials + FAPI 2.0 (public); JWT from trusted IdP (private) | [en](../../framework/en/engineering/platform/lexis/lex-auth.md) |
| `lex-cloudevents` | Distributed events follow CloudEvents spec; JSON UTF-8; size < 12KB; `idempotencykey` required | [en](../../framework/en/engineering/platform/lexis/lex-cloudevents.md) |
| `lex-entities` | Persistent entities follow base structure: `entity_id` (UUIDv7), `entity_type`, timestamps, `version` | [en](../../framework/en/engineering/platform/lexis/lex-entities.md) |
| `lex-entity-naming` | `entity_type` values, JSON field names, and DB column names use snake_case; camelCase is forbidden | [en](../../framework/en/engineering/platform/lexis/lex-entity-naming.md) |
| `lex-error-handling` | Error responses use standardized structure: `errors` array with `code`, `reason`, `message` | [en](../../framework/en/engineering/platform/lexis/lex-error-handling.md) |
| `lex-idempotency` | State-modifying operations are idempotent; `Idempotency-Key` header required on POST/PATCH | [en](../../framework/en/engineering/platform/lexis/lex-idempotency.md) |
| `lex-restful-apis` | HTTP endpoints follow platform RESTful spec: status codes, payload, headers, pagination, sorting | [en](../../framework/en/engineering/platform/lexis/lex-restful-apis.md) |

---

## `engineering / quality`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-test-isolation` | Tests start from known state; order-independent; parallelizable; flaky tests are treated as critical bugs | [en](../../framework/en/engineering/quality/lexis/lex-test-isolation.md) |
| `lex-test-pyramid` | Test distribution ~70% unit / 20% integration / 10% E2E; E2E only for declared critical journeys | [en](../../framework/en/engineering/quality/lexis/lex-test-pyramid.md) |

---

## `engineering / sre`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-runbook-for-every-alert` | Every human-triggering alert has a versioned runbook in `docs/runbooks/` linked in the alert annotation | [en](../../framework/en/engineering/sre/lexis/lex-runbook-for-every-alert.md) |
| `lex-slo-required` | Tier-1/2 services have a declared SLO before first production deploy; error budget tracked in real time | [en](../../framework/en/engineering/sre/lexis/lex-slo-required.md) |

---

## `engineering / workflow`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-issue-driven` | Every implementation originates from an issue; passes Gate 1 (Scope) and Gate 2 (Quality); full AC↔test traceability | [en](../../framework/en/engineering/workflow/lexis/lex-issue-driven.md) |
