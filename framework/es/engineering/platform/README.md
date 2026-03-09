# engineering/platform — Especificaciones de la Plataforma Guardia

Este subclade contiene las especificaciones de la plataforma Guardia como Lexis (leyes inquebrantables), Codex (manuales de referencia), Katas (procedimientos), Warriors (agentes especializados) y Cries (comandos recurrentes), para uso por agentes de IA e implementadores. Estos artefactos son la referencia canónica en el framework Ahrena.

## Especificaciones (Lexis y Codex)

| Tema | Lexis | Codex |
|------|--------|--------|
| Entidades | [lex-entities](lexis/lex-entities.md) | [codex-entities](codex/codex-entities.md) |
| Idempotencia | [lex-idempotency](lexis/lex-idempotency.md) | [codex-idempotency](codex/codex-idempotency.md) |
| Tratamiento de Errores | [lex-error-handling](lexis/lex-error-handling.md) | [codex-error-handling](codex/codex-error-handling.md) |
| RESTful APIs | [lex-restful-apis](lexis/lex-restful-apis.md) | [codex-restful-apis](codex/codex-restful-apis.md) (índice) + [status-codes](codex/codex-restful-status-codes.md), [payload](codex/codex-restful-payload.md), [headers](codex/codex-restful-headers.md), [pagination](codex/codex-restful-pagination.md), [sorting](codex/codex-restful-sorting.md) |
| CloudEvents | [lex-cloudevents](lexis/lex-cloudevents.md) | [codex-cloudevents](codex/codex-cloudevents.md) |
| Autenticación y Autorización | [lex-auth](lexis/lex-auth.md) | [codex-auth](codex/codex-auth.md) |

## Katas

| Kata | Descripción | Destino |
|------|-------------|---------|
| [kata-api-design-oas](katas/kata-api-design-oas.md) | Diseño de API y especificación OpenAPI 3.x | **paths.oas** (ej.: `docs/oas`) |
| [kata-api-design-doc](katas/kata-api-design-doc.md) | Diseño de API y documento Markdown de la API | **paths.oas** |
| [kata-events-doc](katas/kata-events-doc.md) | Documentación de eventos CloudEvents | **paths.events** (ej.: `docs/events`) |

## Warriors

| Warrior | Rol | Katas que ejecuta |
|---------|-----|-------------------|
| [warrior-daedalus](warriors/warrior-daedalus.md) | Especialista en Diseño de API | kata-api-design-oas, kata-api-design-doc |
| [warrior-kronos](warriors/warrior-kronos.md) | Especialista en Event Storm | kata-events-doc |

## Cries

| Cry | Descripción | Uso |
|-----|-------------|-----|
| [cry-api-design](cries/cry-api-design.md) | Diseño de API (OAS + doc) | `/cry-api-design <descripción> [base path]` |
| [cry-event-storm](cries/cry-event-storm.md) | Documentación de eventos CloudEvents | `/cry-event-storm <contexto> [source base]` |
| [cry-full-design](cries/cry-full-design.md) | Diseño completo (API + eventos) en secuencia | `/cry-full-design <descripción> [base path] [contexto eventos]` |

## Destinos (paths)

Los caminos canónicos se definen en `.ahrena/.directives`:

| Path | Predeterminado | Contenido |
|------|----------------|-----------|
| **paths.oas** | `docs/oas` | Especificación OpenAPI y documento Markdown de la API |
| **paths.events** | `docs/events` | Documentación de eventos CloudEvents (ej.: events.md) |

## Estructura

- **lexis/** — Leyes inquebrantables (una por especificación).
- **codex/** — Manuales de referencia (uno por especificación; RESTful en varios archivos).
- **katas/** — Procedimientos repetibles (diseño de API OAS, diseño de API doc, documentación de eventos).
- **warriors/** — Agentes especializados (Daedalus para API, Kronos para Event Storm).
- **cries/** — Comandos recurrentes (api-design, event-storm, full-design).

Los artefactos existen en los idiomas pt-BR, es y en conforme a `language.i18n` en `.ahrena/.directives`.
