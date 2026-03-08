# engineering/platform — Especificaciones de la Plataforma Guardia

Este subclade contiene las especificaciones de la plataforma Guardia como Lexis (leyes inquebrantables) y Codex (manuales de referencia), para uso por agentes de IA e implementadores. Estos artefactos son la referencia canónica en el framework Ahrena.

## Especificaciones

| Tema | Lexis | Codex |
|------|--------|--------|
| Entidades | [lex-entities](lexis/lex-entities.md) | [codex-entities](codex/codex-entities.md) |
| Idempotencia | [lex-idempotency](lexis/lex-idempotency.md) | [codex-idempotency](codex/codex-idempotency.md) |
| Tratamiento de Errores | [lex-error-handling](lexis/lex-error-handling.md) | [codex-error-handling](codex/codex-error-handling.md) |
| RESTful APIs | [lex-restful-apis](lexis/lex-restful-apis.md) | [codex-restful-apis](codex/codex-restful-apis.md) (índice) + [status-codes](codex/codex-restful-status-codes.md), [payload](codex/codex-restful-payload.md), [headers](codex/codex-restful-headers.md), [pagination](codex/codex-restful-pagination.md), [sorting](codex/codex-restful-sorting.md) |
| CloudEvents | [lex-cloudevents](lexis/lex-cloudevents.md) | [codex-cloudevents](codex/codex-cloudevents.md) |
| Autenticación y Autorización | [lex-auth](lexis/lex-auth.md) | [codex-auth](codex/codex-auth.md) |

## Estructura

- **lexis/** — Leyes inquebrantables (una por especificación).
- **codex/** — Manuales de referencia (uno por especificación; RESTful en varios archivos: codex-restful-apis índice + codex-restful-status-codes, codex-restful-payload, codex-restful-headers, codex-restful-pagination, codex-restful-sorting).

Los artefactos existen en los idiomas pt-BR, es y en conforme a `language.i18n` en `.ahrena/.directives`.
