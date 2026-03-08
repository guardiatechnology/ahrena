# engineering/platform — Especificaciones de la Plataforma Guardia

Este subclade contiene las especificaciones de la plataforma Guardia reflejadas del [Hub Guardia](https://hub.guardia.finance/docs/specifications/), como Lexis (leyes inquebrantables) y Codex (manuales de referencia), para uso por agentes de IA e implementadores.

El Hub sigue siendo la **fuente de la verdad**; estos artefactos son la referencia canónica en el framework Ahrena.

## Especificaciones

| Tema | Lexis | Codex | Hub |
|------|--------|--------|-----|
| Entidades | [lex-entities](lexis/lex-entities.md) | [codex-entities](codex/codex-entities.md) | [Entidades](https://hub.guardia.finance/docs/specifications/entities/) |
| Idempotencia | [lex-idempotency](lexis/lex-idempotency.md) | [codex-idempotency](codex/codex-idempotency.md) | [Idempotencia](https://hub.guardia.finance/docs/specifications/idempotency/) |
| Tratamiento de Errores | [lex-error-handling](lexis/lex-error-handling.md) | [codex-error-handling](codex/codex-error-handling.md) | [Tratamiento de Errores](https://hub.guardia.finance/docs/specifications/error-handling/) |
| RESTful APIs | [lex-restful-apis](lexis/lex-restful-apis.md) | [codex-restful-apis](codex/codex-restful-apis.md) | [RESTful](https://hub.guardia.finance/docs/specifications/restful/) |
| CloudEvents | [lex-cloudevents](lexis/lex-cloudevents.md) | [codex-cloudevents](codex/codex-cloudevents.md) | [CloudEvents](https://hub.guardia.finance/docs/specifications/cloud-events/) |
| Autenticación y Autorización | [lex-auth](lexis/lex-auth.md) | [codex-auth](codex/codex-auth.md) | [Auth](https://hub.guardia.finance/docs/specifications/auth/) |

## Estructura

- **lexis/** — Leyes inquebrantables (una por especificación).
- **codex/** — Manuales de referencia (uno por especificación; codex-restful-apis incluye cinco módulos: Status Codes, Payload, Headers, Paginación, Ordenación).

Los artefactos existen en los idiomas pt-BR, es y en conforme a `language.i18n` en `.ahrena/.directives`.
