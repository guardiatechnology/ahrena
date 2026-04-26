# Ahrena — Warriors Catalog

All **14** specialized agents in the Ahrena framework (including the sample template).

> **Links** point to the English version in `framework/en/`. Every Warrior also exists in `framework/pt-BR/` and `framework/es/`.

---

## `documentation / i18n`

| Artifact | Role | Orchestrates | Framework |
|---|---|---|---|
| `warrior-translator` | Translates Ahrena artifacts to all required languages following `lex-language-*` rules | `kata-translate` | [en](../../framework/en/documentation/i18n/warriors/warrior-translator.md) |

---

## `engineering / backend`

| Artifact | Role | Orchestrates | Framework |
|---|---|---|---|
| `warrior-apollo` | Senior Python Engineer — backend design, implementation, testing, and maintenance of Python services | `kata-python-implement`, `kata-python-review`, `kata-python-debug`, `kata-python-refactor` | [en](../../framework/en/engineering/backend/warriors/warrior-apollo.md) |

---

## `engineering / data`

| Artifact | Role | Orchestrates | Framework |
|---|---|---|---|
| `warrior-demeter` | Senior Data / Database Architect — data modeling, schema design, migrations, and retention policies | `kata-schema-design` | [en](../../framework/en/engineering/data/warriors/warrior-demeter.md) |

---

## `engineering / devops`

| Artifact | Role | Orchestrates | Framework |
|---|---|---|---|
| `warrior-atlas` | Senior AWS Solutions Architect — architecture design, IaC, security reviews, and cost optimization | `kata-aws-design`, `kata-aws-review` | [en](../../framework/en/engineering/devops/warriors/warrior-atlas.md) |

---

## `engineering / frontend`

| Artifact | Role | Orchestrates | Framework |
|---|---|---|---|
| `warrior-hephaestus` | Senior Frontend Engineer — UI implementation, component development, accessibility, and performance | `kata-frontend-implement`, `kata-frontend-review` | [en](../../framework/en/engineering/frontend/warriors/warrior-hephaestus.md) |

---

## `engineering / mobile`

| Artifact | Role | Orchestrates | Framework |
|---|---|---|---|
| `warrior-iris` | Senior Mobile Engineer — iOS and Android implementation with mandatory platform parity | `kata-mobile-implement` | [en](../../framework/en/engineering/mobile/warriors/warrior-iris.md) |

---

## `engineering / platform`

| Artifact | Role | Orchestrates | Framework |
|---|---|---|---|
| `warrior-daedalus` | API Design Specialist — RESTful API design, OAS documentation, and design review | `kata-api-design-doc`, `kata-api-design-oas`, `kata-api-design-review` | [en](../../framework/en/engineering/platform/warriors/warrior-daedalus.md) |
| `warrior-kronos` | Event Storm Specialist — event storming sessions and CloudEvents documentation | `kata-event-storm`, `kata-events-doc` | [en](../../framework/en/engineering/platform/warriors/warrior-kronos.md) |
| `warrior-prometheus` | Technical Product Manager — orchestrates the complete feature design cycle | `kata-api-design-doc`, `kata-domain-model`, `kata-events-doc` (via Theseus, Daedalus, Kronos) | [en](../../framework/en/engineering/platform/warriors/warrior-prometheus.md) |
| `warrior-theseus` | Domain Modeling Specialist — DDD domain discovery, modeling, and documentation | `kata-domain-model` | [en](../../framework/en/engineering/platform/warriors/warrior-theseus.md) |

---

## `engineering / quality`

| Artifact | Role | Orchestrates | Framework |
|---|---|---|---|
| `warrior-hera` | Senior QA / Test Strategy Engineer — test strategy, coverage plans, suite quality audits | `kata-test-plan-design` | [en](../../framework/en/engineering/quality/warriors/warrior-hera.md) |

---

## `engineering / sre`

| Artifact | Role | Orchestrates | Framework |
|---|---|---|---|
| `warrior-hestia` | Senior SRE / On-Call — SLO design, monitoring, alerting, incident response, post-mortems | `kata-incident-triage` | [en](../../framework/en/engineering/sre/warriors/warrior-hestia.md) |

---

## `engineering / workflow`

| Artifact | Role | Orchestrates | Framework |
|---|---|---|---|
| `warrior-athena` | Issue-Driven Flow Orchestrator — end-to-end development from GitHub issue to reviewed, merged PR | All workflow katas + delegates to Apollo, Hephaestus, Daedalus, Kronos, Atlas, Hera, Hestia, Demeter, Iris | [en](../../framework/en/engineering/workflow/warriors/warrior-athena.md) |

---

## Sample

| Artifact | Description | Framework |
|---|---|---|
| `warrior-sample` | Official template for creating new Warriors — structure, frontmatter, and authoring guidelines | [en](../../framework/en/engineering/workflow/warriors/warrior-sample.md) |

---

## Warrior Hierarchy

```
warrior-athena (orchestrator)
  ├── warrior-apollo        (backend implementation)
  ├── warrior-hephaestus    (frontend implementation)
  ├── warrior-iris          (mobile implementation)
  ├── warrior-daedalus      (API design)
  ├── warrior-kronos        (event documentation)
  ├── warrior-atlas         (infrastructure)
  ├── warrior-hera          (test strategy)
  ├── warrior-hestia        (SRE)
  └── warrior-demeter       (data)

warrior-prometheus (product design orchestrator)
  ├── warrior-theseus       (domain modeling)
  ├── warrior-daedalus      (API design)
  └── warrior-kronos        (event storm)

warrior-translator (documentation)
```
