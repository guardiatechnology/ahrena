# engineering/platform — Guardia Platform Specifications

This subclade contains Guardia platform specifications as Lexis (unbreakable laws) and Codex (reference manuals), for use by AI agents and implementers. These artifacts are the canonical reference in the Ahrena framework.

## Specifications

| Topic | Lexis | Codex |
|-------|--------|--------|
| Entities | [lex-entities](lexis/lex-entities.md) | [codex-entities](codex/codex-entities.md) |
| Idempotency | [lex-idempotency](lexis/lex-idempotency.md) | [codex-idempotency](codex/codex-idempotency.md) |
| Error Handling | [lex-error-handling](lexis/lex-error-handling.md) | [codex-error-handling](codex/codex-error-handling.md) |
| RESTful APIs | [lex-restful-apis](lexis/lex-restful-apis.md) | [codex-restful-apis](codex/codex-restful-apis.md) (index) + [status-codes](codex/codex-restful-status-codes.md), [payload](codex/codex-restful-payload.md), [headers](codex/codex-restful-headers.md), [pagination](codex/codex-restful-pagination.md), [sorting](codex/codex-restful-sorting.md) |
| CloudEvents | [lex-cloudevents](lexis/lex-cloudevents.md) | [codex-cloudevents](codex/codex-cloudevents.md) |
| Authentication and Authorization | [lex-auth](lexis/lex-auth.md) | [codex-auth](codex/codex-auth.md) |

## Structure

- **lexis/** — Unbreakable laws (one per specification).
- **codex/** — Reference manuals (one per specification; RESTful split across files: codex-restful-apis index + codex-restful-status-codes, codex-restful-payload, codex-restful-headers, codex-restful-pagination, codex-restful-sorting).

Artifacts exist in pt-BR, es, and en per `language.i18n` in `.ahrena/.directives`.
