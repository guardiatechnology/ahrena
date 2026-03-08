# engineering/platform — Guardia Platform Specifications

This subclade contains Guardia platform specifications mirrored from the [Guardia Hub](https://hub.guardia.finance/docs/specifications/), as Lexis (unbreakable laws) and Codex (reference manuals), for use by AI agents and implementers.

The Hub remains the **source of truth**; these artifacts are the canonical reference in the Ahrena framework.

## Specifications

| Topic | Lexis | Codex | Hub |
|-------|--------|--------|-----|
| Entities | [lex-entities](lexis/lex-entities.md) | [codex-entities](codex/codex-entities.md) | [Entities](https://hub.guardia.finance/docs/specifications/entities/) |
| Idempotency | [lex-idempotency](lexis/lex-idempotency.md) | [codex-idempotency](codex/codex-idempotency.md) | [Idempotency](https://hub.guardia.finance/docs/specifications/idempotency/) |
| Error Handling | [lex-error-handling](lexis/lex-error-handling.md) | [codex-error-handling](codex/codex-error-handling.md) | [Error Handling](https://hub.guardia.finance/docs/specifications/error-handling/) |
| RESTful APIs | [lex-restful-apis](lexis/lex-restful-apis.md) | [codex-restful-apis](codex/codex-restful-apis.md) | [RESTful](https://hub.guardia.finance/docs/specifications/restful/) |
| CloudEvents | [lex-cloudevents](lexis/lex-cloudevents.md) | [codex-cloudevents](codex/codex-cloudevents.md) | [CloudEvents](https://hub.guardia.finance/docs/specifications/cloud-events/) |
| Authentication and Authorization | [lex-auth](lexis/lex-auth.md) | [codex-auth](codex/codex-auth.md) | [Auth](https://hub.guardia.finance/docs/specifications/auth/) |

## Structure

- **lexis/** — Unbreakable laws (one per specification).
- **codex/** — Reference manuals (one per specification; codex-restful-apis includes five modules: Status Codes, Payload, Headers, Pagination, Sorting).

Artifacts exist in pt-BR, es, and en per `language.i18n` in `.ahrena/.directives`.
