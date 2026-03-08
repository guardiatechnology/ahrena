# engineering/platform — Especificações da Plataforma Guardia

Este subclade contém as especificações da plataforma Guardia espelhadas do [Hub Guardia](https://hub.guardia.finance/docs/specifications/), como Lexis (leis inquebráveis) e Codex (manuais de referência), para uso por agentes de IA e implementadores.

O Hub permanece a **fonte da verdade**; estes artefatos são referência canônica no framework Ahrena.

## Especificações

| Tema | Lexis | Codex | Hub |
|------|--------|--------|-----|
| Entidades | [lex-entities](lexis/lex-entities.md) | [codex-entities](codex/codex-entities.md) | [Entidades](https://hub.guardia.finance/docs/specifications/entities/) |
| Idempotência | [lex-idempotency](lexis/lex-idempotency.md) | [codex-idempotency](codex/codex-idempotency.md) | [Idempotência](https://hub.guardia.finance/docs/specifications/idempotency/) |
| Tratamento de Erros | [lex-error-handling](lexis/lex-error-handling.md) | [codex-error-handling](codex/codex-error-handling.md) | [Tratamento de Erros](https://hub.guardia.finance/docs/specifications/error-handling/) |
| RESTful APIs | [lex-restful-apis](lexis/lex-restful-apis.md) | [codex-restful-apis](codex/codex-restful-apis.md) | [RESTful](https://hub.guardia.finance/docs/specifications/restful/) |
| CloudEvents | [lex-cloudevents](lexis/lex-cloudevents.md) | [codex-cloudevents](codex/codex-cloudevents.md) | [CloudEvents](https://hub.guardia.finance/docs/specifications/cloud-events/) |
| Autenticação e Autorização | [lex-auth](lexis/lex-auth.md) | [codex-auth](codex/codex-auth.md) | [Auth](https://hub.guardia.finance/docs/specifications/auth/) |

## Estrutura

- **lexis/** — Leis inquebráveis (uma por especificação).
- **codex/** — Manuais de referência (um por especificação; codex-restful-apis inclui cinco módulos: Status Codes, Payload, Headers, Paginação, Ordenação).

Artefatos existem nos idiomas pt-BR, es e en conforme `language.i18n` em `.ahrena/.directives`.
