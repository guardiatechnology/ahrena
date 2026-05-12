# Lexis: Estrutura Obrigatória dos Documentos de Design de Feature

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Plataforma Guardia — documentos produzidos durante o ciclo de design de feature orquestrado pelo warrior-prometheus

## Propósito

A modelagem de domínio, o desenho de API e a documentação de eventos produzem artefatos que precisam ser encontrados rapidamente, lidos por humanos e por agentes, e atualizados sem ambiguidade entre fases. Sem uma estrutura única e nominal, cada feature acaba salvando documentos em locais diferentes, com nomes diferentes, e a consistência cruzada entre domínio, API e eventos se perde. Esta Lexis fixa o local, o nome e a forma de organização desses documentos.

## Lei

> **Todo documento produzido nas fases de design de feature (modelagem de domínio, design de API, documentação de eventos, agentes e métricas) DEVE ser persistido em `docs/{context}/{categoria}/`, onde `{context}` é o Bounded Context em kebab-case e `{categoria}` é uma das categorias canônicas: `entities`, `oas`, `events`, `agents`, `metrics`. Cada categoria DEVE seguir o template definido em `codex-feature-design-docs`. Salvar documentos de design fora dessa estrutura, em paths configuráveis (`paths.oas`, `paths.events`, `paths.domain`) ou em qualquer outro local FORA de `docs/{context}/{categoria}/` é PROIBIDO.**

## Abrangência

- **Aplica-se a:** todos os documentos produzidos pelos warriors de design (`warrior-prometheus`, `warrior-theseus`, `warrior-daedalus`, `warrior-kronos`) e por qualquer agente que crie ou atualize artefatos de design de feature na plataforma Guardia.
- **Agentes vinculados:** `warrior-prometheus`, `warrior-theseus`, `warrior-daedalus`, `warrior-kronos`, `warrior-athena` quando orquestra design, e qualquer Kata invocado por eles (`kata-domain-model`, `kata-api-design-oas`, `kata-api-design-doc`, `kata-event-storm`, `kata-events-doc`, `kata-feature-design-docs`).
- **Exceções:** Nenhuma. Lexis não admitem exceções. Documentos transitórios de orquestração (checkpoints, scratchpads de fase) não são alvo desta Lexis e permanecem em `.ahrena/workflow/`.

## Estrutura Canônica

```
docs/
└── {context}/                  # Bounded Context em kebab-case (ex.: scheduled-payments)
    ├── entities/
    │   └── {entity-name}.md    # 1 arquivo por entidade (kebab-case)
    ├── oas/
    │   └── openapi.yaml        # OpenAPI 3.x da API do contexto
    ├── events/
    │   └── events.md           # Eventos do contexto, organizados por entidade
    ├── agents/                 # (reservado — definição posterior)
    └── metrics/                # (reservado — definição posterior)
```

### Regras de nomeação

| Item | Regra |
|------|-------|
| `{context}` | kebab-case do nome do Bounded Context. Ex.: `ScheduledPayments` → `scheduled-payments` |
| Arquivos de `entities/` | `{entity-name}.md` em kebab-case do nome em PascalCase. Ex.: `ScheduledTransfer` → `scheduled-transfer.md` |
| Arquivo de `oas/` | `openapi.yaml`. Quando houver mais de uma API no mesmo contexto, sufixar: `openapi-{slug}.yaml` |
| Arquivo de `events/` | `events.md` |
| Categorias reservadas | `entities`, `oas`, `events`, `agents`, `metrics`. Criar outra categoria sem ADR aprovado é PROIBIDO |

### Conformidade de conteúdo

Cada categoria DEVE seguir o template definido em `codex-feature-design-docs`:

- `entities/{entity}.md` — cabeçalho com **Classificação DDD** (Entity, Aggregate Root ou Value Object), seção **Por que existe**, tabela **Campos** (Campo, Tipo, Tamanho, Obrigatório, Descrição), e seções **Regras de Negócio**, **Invariantes**, **Relações**, **Erros** e **Referências**.
- `oas/openapi.yaml` — OpenAPI 3.x em YAML legível, conforme `codex-oas-structure`.
- `events/events.md` — agrupado por entidade, com `stateDiagram-v2` Mermaid do ciclo de vida, e para cada evento o payload em CloudEvents conforme `codex-cloudevents`.

## Consequências de Violação

1. **Bloqueio automático:** PRs com documentos de design fora de `docs/{context}/{categoria}/` são rejeitados.
2. **Inconsistência cruzada:** Prometheus não conclui o pacote final quando algum artefato está fora da estrutura.
3. **Remediação:** mover o documento para o path canônico, atualizar referências e atualizar o resumo final do warrior-prometheus.

## Exemplos

### Correto

```
docs/
└── scheduled-payments/
    ├── entities/
    │   ├── scheduled-transfer.md
    │   └── transfer-approval.md
    ├── oas/
    │   └── openapi.yaml
    └── events/
        └── events.md
```

### Incorreto

```
docs/
├── domain/platform-domain-model.md     # ❌ não existe paths.domain
├── oas/scheduled-transfers-api.yaml    # ❌ fora de docs/{context}/oas/
└── events/scheduled-transfers.md       # ❌ fora de docs/{context}/events/
```

```
docs/
└── scheduled-payments/
    └── domain-model.md                 # ❌ categoria "domain-model" não existe; modelo de domínio se distribui entre entities/, events/ e oas/
```

## Validação Automatizada

- **Ferramenta:** verificação por agente ao persistir; lint de PR que valida o regex `^docs/[a-z][a-z0-9-]*/(entities|oas|events|agents|metrics)/[^/]+$` para todo arquivo novo em `docs/`.
- **Momento:** ao final de cada fase do design, no Gate 1 do fluxo Issue-Driven (escopo) e no PR.
- **Métrica:** 0 documentos de design fora da estrutura canônica em `main`; 100% das features com Bounded Contexts identificados produzem subdiretórios coerentes em `docs/`.

## Referências

- `codex-feature-design-docs` — manual com templates de cada categoria
- `codex-component-architecture` — `docs/{context}/` é parte do layout físico do bounded context (component-architecture). Esta Lexis governa o conteúdo de `docs/`; `codex-component-architecture` governa a estrutura física (`components/`, `deployment/`)
- `kata-feature-design-docs` — procedimento para criar e atualizar os documentos
- `lex-entities`, `lex-entity-naming` — estrutura e nomeação de entidades
- `lex-cloudevents`, `codex-cloudevents` — formato de eventos
- `codex-oas-structure` — estrutura do OpenAPI
- `warrior-prometheus` — orquestrador do ciclo de design que enforce esta Lexis
