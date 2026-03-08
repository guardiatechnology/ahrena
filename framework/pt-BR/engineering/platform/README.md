# engineering/platform — Especificações da Plataforma Guardia

Este subclade contém as especificações da plataforma Guardia como Lexis (leis inquebráveis) e Codex (manuais de referência), para uso por agentes de IA e implementadores. Estes artefatos são a referência canônica no framework Ahrena.

## Especificações

| Tema | Lexis | Codex |
|------|--------|--------|
| Entidades | [lex-entities](lexis/lex-entities.md) | [codex-entities](codex/codex-entities.md) |
| Idempotência | [lex-idempotency](lexis/lex-idempotency.md) | [codex-idempotency](codex/codex-idempotency.md) |
| Tratamento de Erros | [lex-error-handling](lexis/lex-error-handling.md) | [codex-error-handling](codex/codex-error-handling.md) |
| RESTful APIs | [lex-restful-apis](lexis/lex-restful-apis.md) | [codex-restful-apis](codex/codex-restful-apis.md) (índice) + [status-codes](codex/codex-restful-status-codes.md), [payload](codex/codex-restful-payload.md), [headers](codex/codex-restful-headers.md), [pagination](codex/codex-restful-pagination.md), [sorting](codex/codex-restful-sorting.md) |
| CloudEvents | [lex-cloudevents](lexis/lex-cloudevents.md) | [codex-cloudevents](codex/codex-cloudevents.md) |
| Autenticação e Autorização | [lex-auth](lexis/lex-auth.md) | [codex-auth](codex/codex-auth.md) |

## Estrutura

- **lexis/** — Leis inquebráveis (uma por especificação).
- **codex/** — Manuais de referência (um por especificação; RESTful em vários arquivos: codex-restful-apis índice + codex-restful-status-codes, codex-restful-payload, codex-restful-headers, codex-restful-pagination, codex-restful-sorting).

Artefatos existem nos idiomas pt-BR, es e en conforme `language.i18n` em `.ahrena/.directives`.
