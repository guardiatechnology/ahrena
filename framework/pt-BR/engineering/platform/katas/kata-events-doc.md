# Kata: Documentação de Eventos CloudEvents

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Plataforma Guardia — documentação de eventos CloudEvents para uma feature ou módulo

## Objetivo

Este Kata define o procedimento para **produzir documentação em Markdown** dos eventos CloudEvents de uma feature ou módulo: consultar lex-cloudevents e codex-cloudevents, identificar os tipos de evento (formato `event.guardia.{module}.{entity_type}.{event_name}`), documentar estrutura, payload (data), idempotência e persistir o documento em **paths.events** (`.ahrena/.directives`; padrão `docs/events`) em conformidade com as regras da Guardia.

## Quando Usar

- Quando uma feature ou módulo publica ou consome eventos e é necessário catalogar e documentar esses eventos
- Quando invocado pelo Warrior especialista em Event Storm (ex.: Kronos) ou pelo cry-event-storm
- Quando é necessário gerar ou atualizar a doc de eventos em paths.events (ex.: `events.md`, `cloudevents.md`)

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Contexto da feature ou módulo | Sim | Nome do módulo, entidades envolvidas e operações que emitem eventos (ex.: transaction.created, transaction.updated) ou lista explícita de tipos de evento |
| Base path / source | Não | Base da URI `source` (ex.: `https://tenant.guardia.finance/platform/api/v1`). Se omitido, o agente propõe conforme codex-cloudevents |
| Documento existente | Não | Se houver doc de eventos em paths.events, atualizar em vez de criar do zero |

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

1. Ler `.ahrena/.directives` para obter **paths.events** (destino da doc de eventos; padrão `docs/events`)
2. Confirmar o contexto da feature/módulo (entidades, operações que emitem eventos). Se insuficiente, fazer perguntas ao usuário (quais eventos? created/updated/deleted? entidades envolvidas?) e aguardar respostas
3. Verificar se já existe documento de eventos em paths.events (ex.: `events.md`, `cloudevents.md`) para atualizar ou criar novo

### Passo 2: Consultar Lexis e Codex CloudEvents

1. Consultar **lex-directives** (obrigatório)
2. Consultar **lex-cloudevents** — eventos devem seguir CloudEvents (estrutura, propriedades obrigatórias, idempotencykey, JSON, tamanho < 12KB)
3. Consultar **codex-cloudevents** — estrutura do evento (id, source, specversion, type, time, datacontenttype, subject, idempotencykey, data); formato de type `event.guardia.{module}.{entity_type}.{event_name}`; shape de `data` conforme codex-entities
4. Consultar **lex-entities** e **codex-entities** — campos de entidade em `data` (entity_id, entity_type, version, created_at, updated_at, discarded_at; history omitido)
5. Consultar **lex-idempotency** e **codex-idempotency** — idempotencykey obrigatório; consumidores devem deduplicar

### Passo 3: Identificar Tipos de Evento e Payloads

1. Listar **tipos de evento** no formato `event.guardia.{module}.{entity_type}.{event_name}` (ex.: `event.guardia.platform.transaction.created`, `event.guardia.platform.scheduled_transfer.cancelled`)
2. Para cada tipo, definir: **source** (URI base + entity_type + entity_id quando aplicável), **subject** (`{entity_type}/{entity_id}`), **data** (campos conforme codex-entities; sem history)
3. Garantir que cada evento tenha **idempotencykey** documentado e que o tamanho do evento seja inferior a 12KB
4. Mapear entidades referenciadas em `data` aos campos obrigatórios de codex-entities

### Passo 4: Documentar Cada Evento (type, source, subject, data, idempotencykey)

Para cada evento catalogado, documentar:

1. **type** — nome completo do tipo (event.guardia.{module}.{entity_type}.{event_name})
2. **Descrição** — quando o evento é emitido (ex.: após criação de transferência agendada)
3. **source** — padrão da URI de origem (conforme codex-cloudevents)
4. **subject** — formato `{entity_type}/{entity_id}`
5. **idempotencykey** — obrigatório; consumidores devem registrar e deduplicar por chave e hash
6. **data** — estrutura do payload (entity_id, entity_type, e demais campos conforme codex-entities); indicar que history deve ser omitido
7. **Exemplo** (opcional) — snippet JSON do evento conforme codex-cloudevents

### Passo 5: Produzir Documento Markdown de Eventos

1. Obter **paths.events** em `.ahrena/.directives`. Garantir que o diretório exista; se não existir, criá-lo
2. Gerar ou atualizar **documento Markdown** (ex.: `events.md`, `cloudevents.md`) em paths.events contendo:
   - Título e resumo (módulo/feature)
   - Tabela de eventos (type, descrição, quando é emitido)
   - Para cada evento: type, descrição, source, subject, idempotencykey, estrutura de `data`, exemplo quando útil
   - Notas: serialização JSON UTF-8, tamanho < 12KB, consumidores idempotentes (conforme lex-idempotency)
3. Se já existir doc de eventos no path, **mesclar** os novos eventos na estrutura existente (por módulo ou por entity_type) em vez de sobrescrever
4. Salvar em **paths.events**. Se o usuário solicitar entrega inline, entregar também no chat

### Passo 6: Validação Final

Antes de entregar o output, verificar:

- [ ] Todos os eventos seguem lex-cloudevents (estrutura, type catalogado, idempotencykey, data conforme codex-entities)
- [ ] Tipo no formato event.guardia.{module}.{entity_type}.{event_name}
- [ ] data sem history; campos obrigatórios de entidade documentados
- [ ] Documento está completo (tabela de eventos, detalhes por tipo) e sem contradição com as Lexis
- [ ] Documento foi salvo no path **paths.events** (diretório criado se não existia)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Documento de eventos CloudEvents | Markdown (.md) | Diretório **paths.events** em `.ahrena/.directives` (padrão `docs/events`; criar diretório se não existir; criar ou atualizar o arquivo, ex.: events.md) |

## Exemplo de Execução

### Input de Exemplo

```
Módulo: platform. Entidades: scheduled_transfer. Eventos: created (após POST), updated (após PATCH), cancelled (após DELETE).
```

### Output de Exemplo (resumido)

Arquivo `events.md` (ou `cloudevents.md`) em **paths.events** com:
- event.guardia.platform.scheduled_transfer.created — após criação; source, subject, idempotencykey; data com entity_id, entity_type, created_at, updated_at, version, etc.
- event.guardia.platform.scheduled_transfer.updated
- event.guardia.platform.scheduled_transfer.cancelled

Cada um com descrição, source, subject, data e exemplo JSON conforme codex-cloudevents.

## Restrições

- Este Kata produz apenas documentação de eventos; não implementa publicadores nem consumidores
- Não altera documentação já publicada sem justificativa e ADR
- Exceções às Lexis devem ser documentadas em ADR
- O agente deve escalar para humano quando houver dúvida sobre fronteiras de módulo ou tipos de evento não catalogados

## Referências

- lex-directives, lex-cloudevents, lex-entities, lex-idempotency
- codex-cloudevents, codex-entities, codex-idempotency
- [CloudEvents Specification](https://cloudevents.io/)
