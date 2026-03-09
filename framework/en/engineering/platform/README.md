# engineering/platform — Guardia Platform Specifications

This subclade contains Guardia platform specifications as Lexis (unbreakable laws), Codex (reference manuals), Katas (procedures), Warriors (specialized agents), and Cries (recurring commands), for use by AI agents and implementers. These artifacts are the canonical reference in the Ahrena framework.

## Specifications (Lexis and Codex)

| Topic | Lexis | Codex |
|-------|--------|--------|
| Entities | [lex-entities](lexis/lex-entities.md) | [codex-entities](codex/codex-entities.md) |
| Idempotency | [lex-idempotency](lexis/lex-idempotency.md) | [codex-idempotency](codex/codex-idempotency.md) |
| Error Handling | [lex-error-handling](lexis/lex-error-handling.md) | [codex-error-handling](codex/codex-error-handling.md) |
| RESTful APIs | [lex-restful-apis](lexis/lex-restful-apis.md) | [codex-restful-apis](codex/codex-restful-apis.md) (index) + [status-codes](codex/codex-restful-status-codes.md), [payload](codex/codex-restful-payload.md), [headers](codex/codex-restful-headers.md), [pagination](codex/codex-restful-pagination.md), [sorting](codex/codex-restful-sorting.md) |
| CloudEvents | [lex-cloudevents](lexis/lex-cloudevents.md) | [codex-cloudevents](codex/codex-cloudevents.md) |
| Authentication and Authorization | [lex-auth](lexis/lex-auth.md) | [codex-auth](codex/codex-auth.md) |

## Katas

| Kata | Description | Destination |
|------|-------------|-------------|
| [kata-api-design-oas](katas/kata-api-design-oas.md) | API design and OpenAPI 3.x specification | **paths.oas** (e.g. `docs/oas`) |
| [kata-api-design-doc](katas/kata-api-design-doc.md) | API design and API Markdown document | **paths.oas** |
| [kata-events-doc](katas/kata-events-doc.md) | CloudEvents documentation | **paths.events** (e.g. `docs/events`) |

## Warriors

| Warrior | Role | Katas executed |
|---------|------|----------------|
| [warrior-daedalus](warriors/warrior-daedalus.md) | API Design specialist | kata-api-design-oas, kata-api-design-doc |
| [warrior-kronos](warriors/warrior-kronos.md) | Event Storm specialist | kata-events-doc |

## Cries

| Cry | Description | Usage |
|-----|-------------|-------|
| [cry-api-design](cries/cry-api-design.md) | API design (OAS + doc) | `/cry-api-design <description> [base path]` |
| [cry-event-storm](cries/cry-event-storm.md) | CloudEvents documentation | `/cry-event-storm <context> [source base]` |
| [cry-full-design](cries/cry-full-design.md) | Full design (API + events) in sequence | `/cry-full-design <description> [base path] [events context]` |

## Destinations (paths)

Canonical paths are defined in `.ahrena/.directives`:

| Path | Default | Content |
|------|---------|---------|
| **paths.oas** | `docs/oas` | OpenAPI specification and API Markdown document |
| **paths.events** | `docs/events` | CloudEvents documentation (e.g. events.md) |

## Structure

- **lexis/** — Unbreakable laws (one per specification).
- **codex/** — Reference manuals (one per specification; RESTful split across files).
- **katas/** — Repeatable procedures (API design OAS, API design doc, events documentation).
- **warriors/** — Specialized agents (Daedalus for API, Kronos for Event Storm).
- **cries/** — Recurring commands (api-design, event-storm, full-design).

Artifacts exist in pt-BR, es, and en per `language.i18n` in `.ahrena/.directives`.
