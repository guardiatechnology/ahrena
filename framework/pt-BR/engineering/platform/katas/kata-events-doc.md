# Kata: Documentação de Eventos CloudEvents

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Plataforma Guardia — documentação de eventos CloudEvents para uma feature ou módulo

## Objetivo

Este Kata define o procedimento para **produzir documentação em Markdown** dos eventos CloudEvents de uma feature ou módulo: consultar `lex-cloudevents`, `codex-cloudevents` e `codex-feature-design-docs`, identificar os tipos de evento (formato `event.guardia.{domain}.{entity_name}.{event_name}`), estruturar o conteúdo por entidade com `stateDiagram-v2` do ciclo de vida e payload CloudEvents por evento, e delegar a persistência ao `kata-feature-design-docs` em `docs/{context}/events/events.md`.

## Quando Usar

- Quando uma feature ou módulo publica ou consome eventos e é necessário catalogar e documentar esses eventos
- Quando invocado pelo Warrior especialista em Event Storm (ex.: Kronos) ou pelo cry-event-storm
- Quando é necessário gerar ou atualizar a doc de eventos em docs/{context}/events/events.md (ex.: `events.md`, `cloudevents.md`)

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Contexto da feature ou módulo | Sim | Nome do módulo, entidades envolvidas e operações que emitem eventos (ex.: transaction.created, transaction.updated) ou lista explícita de tipos de evento |
| Base path / source | Não | Base da URI `source` (ex.: `https://tenant.guardia.finance/platform/api/v1`). Se omitido, o agente propõe conforme codex-cloudevents |
| Documento existente | Não | Se houver doc de eventos em docs/{context}/events/events.md, atualizar em vez de criar do zero |

## Workflow

```
Progresso:
- [ ] 1. Ler diretivas e contexto
- [ ] 2. Consultar Lexis e Codex CloudEvents
- [ ] 3. Identificar tipos de evento e payloads
- [ ] 4. Documentar cada evento (type, source, subject, data, idempotencykey)
- [ ] 5. Produzir documento Markdown de eventos
- [ ] 6. Validação final
```

### Passo 1: Ler Diretivas e Contexto

1. Ler `.ahrena/.directives` para obter `language.default`. O destino é fixo: `docs/{context}/events/events.md` por `lex-feature-design-docs`. Confirmar com o usuário o nome do Bounded Context em PascalCase e o segmento `{module}` do CloudEvents
2. Carregar entidades existentes em `docs/{context}/entities/` para alinhar payloads e ciclo de vida
3. Confirmar o contexto da feature/módulo (entidades, operações que emitem eventos). Se insuficiente, fazer perguntas ao usuário (quais eventos? created/updated/deleted? entidades envolvidas?) e aguardar respostas
4. Verificar se já existe `docs/{context}/events/events.md` para atualizar em vez de criar novo

### Passo 2: Consultar Lexis e Codex CloudEvents

1. Consultar **lex-directives** (obrigatório)
2. Consultar **lex-cloudevents** — eventos devem seguir CloudEvents (estrutura, propriedades obrigatórias, idempotencykey, JSON, tamanho < 12KB)
3. Consultar **codex-cloudevents** — estrutura do evento (id, source, specversion, type, time, datacontenttype, subject, idempotencykey, data); formato de type `event.guardia.{domain}.{entity_name}.{event_name}`; shape de `data` conforme codex-entities
4. Consultar **lex-entities** e **codex-entities** — campos de entidade em `data` (entity_id, entity_type, version, created_at, updated_at, discarded_at; history omitido)
5. Consultar **lex-idempotency** e **codex-idempotency** — idempotencykey obrigatório; consumidores devem deduplicar

### Passo 3: Identificar Tipos de Evento e Payloads

1. Listar **tipos de evento** no formato `event.guardia.{domain}.{entity_name}.{event_name}` (ex.: `event.guardia.payments.transaction.created`, `event.guardia.payments.scheduled_transfer.cancelled`)
2. Para cada tipo, definir: **source** (URI base + entity_type + entity_id quando aplicável), **subject** (`{entity_type}/{entity_id}`), **data** (campos conforme codex-entities; sem history)
3. Garantir que cada evento tenha **idempotencykey** documentado e que o tamanho do evento seja inferior a 12KB
4. Mapear entidades referenciadas em `data` aos campos obrigatórios de codex-entities

### Passo 4: Documentar Cada Evento (type, source, subject, data, idempotencykey)

Para cada evento catalogado, documentar:

1. **type** — nome completo do tipo (event.guardia.{domain}.{entity_name}.{event_name})
2. **Descrição** — quando o evento é emitido (ex.: após criação de transferência agendada)
3. **source** — padrão da URI de origem (conforme codex-cloudevents)
4. **subject** — formato `{entity_type}/{entity_id}`
5. **idempotencykey** — obrigatório; consumidores devem registrar e deduplicar por chave e hash
6. **data** — estrutura do payload (entity_id, entity_type, e demais campos conforme codex-entities); indicar que history deve ser omitido
7. **Exemplo** (opcional) — snippet JSON do evento conforme codex-cloudevents

### Passo 5: Produzir Conteúdo do `events.md` na Estrutura Canônica

Estruturar o conteúdo conforme o template do `codex-feature-design-docs`:

1. **Cabeçalho** com Bounded Context e o segmento `{module}`
2. **Visão Geral** em 2-4 frases
3. **Catálogo** — tabela `entity_type | event_name | type completo | Publicador | Consumidores`
4. **Uma seção por entidade que emite eventos**:
   - Subseção **Ciclo de Vida** com bloco `mermaid` `stateDiagram-v2` cobrindo todos os estados e transições
   - Subseção **Eventos**: para cada evento, bloco JSON com payload CloudEvents completo (`specversion`, `id`, `source`, `type`, `subject`, `time`, `datacontenttype`, `idempotencykey`, `data`), tabela `Campo | Tipo | Obrigatório | Descrição` para `data`, e linhas finais **Idempotência** + **Trigger** (Use Case)
5. **Referências** para `lex-cloudevents`, `codex-cloudevents`, `lex-entity-naming`, `lex-idempotency`, e os arquivos em `docs/{context}/entities/`

Persistência: invocar **`kata-feature-design-docs`** com `Bounded Context`, `Categoria` = `events`, `Conteúdo` = Markdown gerado, `Operação` = `create` ou `update`. O kata grava em `docs/{context}/events/events.md`.

### Passo 6: Validação Final

Antes de entregar o output, verificar:

- [ ] Todos os eventos seguem lex-cloudevents (estrutura, type catalogado, idempotencykey, data conforme codex-entities)
- [ ] Tipo no formato event.guardia.{domain}.{entity_name}.{event_name}
- [ ] data sem history; campos obrigatórios de entidade documentados
- [ ] Documento está completo (tabela de eventos, detalhes por tipo) e sem contradição com as Lexis
- [ ] `stateDiagram-v2` presente para cada entidade que emite eventos
- [ ] Persistência delegada a `kata-feature-design-docs` com categoria `events` (path canônico `docs/{context}/events/events.md`)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Documento de eventos CloudEvents | Markdown (.md) | `docs/{context}/events/events.md` (persistido via `kata-feature-design-docs`) |

## Exemplo de Execução

### Input de Exemplo

```
Módulo: platform. Entidades: scheduled_transfer. Eventos: created (após POST), updated (após PATCH), cancelled (após DELETE).
```

### Output de Exemplo (resumido)

Arquivo `docs/{context}/events/events.md` com:
- event.guardia.payments.scheduled_transfer.created — após criação; source, subject, idempotencykey; data com entity_id, entity_type, created_at, updated_at, version, etc.
- event.guardia.payments.scheduled_transfer.updated
- event.guardia.payments.scheduled_transfer.cancelled

Cada um com descrição, source, subject, data e exemplo JSON conforme codex-cloudevents.

## Restrições

- Este Kata produz apenas documentação de eventos; não implementa publicadores nem consumidores
- Não altera documentação já publicada sem justificativa e ADR
- Exceções às Lexis devem ser documentadas em ADR
- O agente deve escalar para humano quando houver dúvida sobre fronteiras de módulo ou tipos de evento não catalogados

## Referências

- `lex-feature-design-docs` — estrutura `docs/{context}/events/`
- `codex-feature-design-docs` — template do `events.md`
- `kata-feature-design-docs` — persistência canônica
- `kata-events-review` — contrapartida de revisão para CloudEvents em momento de PR
- `lex-directives`, `lex-cloudevents`, `lex-entities`, `lex-entity-naming`, `lex-idempotency`
- `codex-cloudevents`, `codex-entities`, `codex-idempotency`
- [CloudEvents Specification](https://cloudevents.io/)
