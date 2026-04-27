# Ahrena — Catálogo de Warriors

Todos los **14** agentes especializados del framework Ahrena (incluida la plantilla de ejemplo).

> **Los enlaces** apuntan a la versión en inglés en `framework/en/`. Todo Warrior también existe en `framework/pt-BR/` y `framework/es/`.

---

## `documentation / i18n`

| Artefacto | Papel | Orquesta | Framework |
|---|---|---|---|
| `warrior-translator` | Translates Ahrena artifacts to all required languages following `lex-language-*` rules | `kata-translate` | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/documentation/i18n/warriors/warrior-translator.md) |

---

## `engineering / backend`

| Artefacto | Papel | Orquesta | Framework |
|---|---|---|---|
| `warrior-apollo` | Senior Python Engineer — backend design, implementation, testing, and maintenance of Python services | `kata-python-implement`, `kata-python-review`, `kata-python-debug`, `kata-python-refactor` | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/backend/warriors/warrior-apollo.md) |

---

## `engineering / data`

| Artefacto | Papel | Orquesta | Framework |
|---|---|---|---|
| `warrior-demeter` | Senior Data / Database Architect — data modeling, schema design, migrations, and retention policies | `kata-schema-design` | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/data/warriors/warrior-demeter.md) |

---

## `engineering / devops`

| Artefacto | Papel | Orquesta | Framework |
|---|---|---|---|
| `warrior-atlas` | Senior AWS Solutions Architect — architecture design, IaC, security reviews, and cost optimization | `kata-aws-design`, `kata-aws-review` | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/devops/warriors/warrior-atlas.md) |

---

## `engineering / frontend`

| Artefacto | Papel | Orquesta | Framework |
|---|---|---|---|
| `warrior-hephaestus` | Senior Frontend Engineer — UI implementation, component development, accessibility, and performance | `kata-frontend-implement`, `kata-frontend-review` | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/frontend/warriors/warrior-hephaestus.md) |

---

## `engineering / mobile`

| Artefacto | Papel | Orquesta | Framework |
|---|---|---|---|
| `warrior-iris` | Senior Mobile Engineer — iOS and Android implementation with mandatory platform parity | `kata-mobile-implement` | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/mobile/warriors/warrior-iris.md) |

---

## `engineering / platform`

| Artefacto | Papel | Orquesta | Framework |
|---|---|---|---|
| `warrior-daedalus` | API Design Specialist — RESTful API design, OAS documentation, and design review | `kata-api-design-doc`, `kata-api-design-oas`, `kata-api-design-review` | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/platform/warriors/warrior-daedalus.md) |
| `warrior-kronos` | Event Storm Specialist — event storming sessions and CloudEvents documentation | `kata-event-storm`, `kata-events-doc` | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/platform/warriors/warrior-kronos.md) |
| `warrior-prometheus` | Technical Product Manager — orchestrates the complete feature design cycle | `kata-api-design-doc`, `kata-domain-model`, `kata-events-doc` (via Theseus, Daedalus, Kronos) | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/platform/warriors/warrior-prometheus.md) |
| `warrior-theseus` | Domain Modeling Specialist — DDD domain discovery, modeling, and documentation | `kata-domain-model` | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/platform/warriors/warrior-theseus.md) |

---

## `engineering / quality`

| Artefacto | Papel | Orquesta | Framework |
|---|---|---|---|
| `warrior-hera` | Senior QA / Test Strategy Engineer — test strategy, coverage plans, suite quality audits | `kata-test-plan-design` | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/quality/warriors/warrior-hera.md) |

---

## `engineering / sre`

| Artefacto | Papel | Orquesta | Framework |
|---|---|---|---|
| `warrior-hestia` | Senior SRE / On-Call — SLO design, monitoring, alerting, incident response, post-mortems | `kata-incident-triage` | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/sre/warriors/warrior-hestia.md) |

---

## `engineering / workflow`

| Artefacto | Papel | Orquesta | Framework |
|---|---|---|---|
| `warrior-athena` | Issue-Driven Flow Orchestrator — end-to-end development from GitHub issue to reviewed, merged PR | All workflow katas + delegates to Apollo, Hephaestus, Daedalus, Kronos, Atlas, Hera, Hestia, Demeter, Iris | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/workflow/warriors/warrior-athena.md) |

---

## Ejemplo

| Artefacto | Descripción | Framework |
|---|---|---|
| `warrior-sample` | Official template for creating new Warriors — structure, frontmatter, and authoring guidelines | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/workflow/warriors/warrior-sample.md) |

---

## Jerarquía de Warriors

```
warrior-athena (orquestador)
  ├── warrior-apollo        (implementación backend)
  ├── warrior-hephaestus    (implementación frontend)
  ├── warrior-iris          (implementación mobile)
  ├── warrior-daedalus      (diseño de API)
  ├── warrior-kronos        (documentación de eventos)
  ├── warrior-atlas         (infraestructura)
  ├── warrior-hera          (estrategia de pruebas)
  ├── warrior-hestia        (SRE)
  └── warrior-demeter       (datos)

warrior-prometheus (orquestador de diseño de producto)
  ├── warrior-theseus       (modelado de dominio)
  ├── warrior-daedalus      (diseño de API)
  └── warrior-kronos        (event storm)

warrior-translator (documentación)
```
