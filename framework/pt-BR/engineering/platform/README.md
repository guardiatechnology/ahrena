# engineering/platform — Especificações da Plataforma Guardia

Este subclade contém as especificações da plataforma Guardia como Lexis (leis inquebráveis), Codex (manuais de referência), Katas (procedimentos), Warriors (agentes especializados) e Cries (comandos recorrentes), para uso por agentes de IA e implementadores. Estes artefatos são a referência canônica no framework Ahrena.

## Especificações (Lexis e Codex)

| Tema | Lexis | Codex |
|------|--------|--------|
| Entidades | [lex-entities](lexis/lex-entities.md) | [codex-entities](codex/codex-entities.md) |
| Idempotência | [lex-idempotency](lexis/lex-idempotency.md) | [codex-idempotency](codex/codex-idempotency.md) |
| Tratamento de Erros | [lex-error-handling](lexis/lex-error-handling.md) | [codex-error-handling](codex/codex-error-handling.md) |
| RESTful APIs | [lex-restful-apis](lexis/lex-restful-apis.md) | [codex-restful-apis](codex/codex-restful-apis.md) (índice) + [status-codes](codex/codex-restful-status-codes.md), [payload](codex/codex-restful-payload.md), [headers](codex/codex-restful-headers.md), [pagination](codex/codex-restful-pagination.md), [sorting](codex/codex-restful-sorting.md) |
| CloudEvents | [lex-cloudevents](lexis/lex-cloudevents.md) | [codex-cloudevents](codex/codex-cloudevents.md) |
| Autenticação e Autorização | [lex-auth](lexis/lex-auth.md) | [codex-auth](codex/codex-auth.md) |

## Katas

| Kata | Descrição | Destino |
|------|-----------|---------|
| [kata-api-design-oas](katas/kata-api-design-oas.md) | Design de API e especificação OpenAPI 3.x | **paths.oas** (ex.: `docs/oas`) |
| [kata-api-design-doc](katas/kata-api-design-doc.md) | Design de API e documento Markdown da API | **paths.oas** |
| [kata-events-doc](katas/kata-events-doc.md) | Documentação de eventos CloudEvents | **paths.events** (ex.: `docs/events`) |

## Warriors

| Warrior | Papel | Katas que executa |
|---------|--------|-------------------|
| [warrior-daedalus](warriors/warrior-daedalus.md) | Especialista em Design de API | kata-api-design-oas, kata-api-design-doc |
| [warrior-kronos](warriors/warrior-kronos.md) | Especialista em Event Storm | kata-events-doc |

## Cries

| Cry | Descrição | Uso |
|-----|-----------|-----|
| [cry-api-design](cries/cry-api-design.md) | Design de API (OAS + doc) | `/cry-api-design <descrição> [base path]` |
| [cry-event-storm](cries/cry-event-storm.md) | Documentação de eventos CloudEvents | `/cry-event-storm <contexto> [source base]` |
| [cry-full-design](cries/cry-full-design.md) | Design completo (API + eventos) em sequência | `/cry-full-design <descrição> [base path] [contexto eventos]` |

## Destinos (paths)

Os caminhos canônicos são definidos em `.ahrena/.directives`:

| Path | Padrão | Conteúdo |
|------|--------|----------|
| **paths.oas** | `docs/oas` | Especificação OpenAPI e documento Markdown da API |
| **paths.events** | `docs/events` | Documentação de eventos CloudEvents (ex.: events.md) |

## Estrutura

- **lexis/** — Leis inquebráveis (uma por especificação).
- **codex/** — Manuais de referência (um por especificação; RESTful em vários arquivos).
- **katas/** — Procedimentos repetíveis (design de API OAS, design de API doc, documentação de eventos).
- **warriors/** — Agentes especializados (Daedalus para API, Kronos para Event Storm).
- **cries/** — Comandos recorrentes (api-design, event-storm, full-design).

Artefatos existem nos idiomas pt-BR, es e en conforme `language.i18n` em `.ahrena/.directives`.
