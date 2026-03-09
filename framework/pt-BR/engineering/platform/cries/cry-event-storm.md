# Cry: Event Storm — Documentação de Eventos CloudEvents

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para documentar eventos CloudEvents de uma feature ou módulo conforme Lexis e Codex da Guardia

## Descrição

Este comando aciona o Warrior Kronos (ou o agente assumindo seu papel) para realizar event storm e documentar os eventos CloudEvents de uma feature ou módulo: consultar lex-cloudevents e codex-cloudevents, catalogar tipos de evento e produzir documentação em Markdown em **paths.events** (docs/events).

## Uso

```
/cry-event-storm <contexto da feature ou módulo> [source base]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `contexto da feature ou módulo` | Sim | Nome do módulo, entidades envolvidas e operações que emitem eventos (ex.: created, updated, cancelled) ou lista explícita de tipos de evento | "Módulo platform, entidade scheduled_transfer: eventos created (após POST), updated (após PATCH), cancelled (após DELETE)" |
| `source base` | Não | Base da URI `source` (ex.: https://tenant.guardia.finance/platform/api/v1). Se omitido, o agente propõe conforme codex-cloudevents | `https://tenant.guardia.finance/platform/api/v1` |

## O que o Comando Faz

1. Interpreta o contexto da feature/módulo e o source base (se informado)
2. Assume o papel do Warrior Kronos (especialista em Event Storm) ou delega ao agente que executa **kata-events-doc**
3. Consulta lex-directives, lex-cloudevents, codex-cloudevents, lex-entities, codex-entities, lex-idempotency e codex-idempotency
4. Identifica tipos de evento (formato event.guardia.{module}.{entity_type}.{event_name}), source, subject, data e idempotencykey
5. Produz documento Markdown de eventos (ex.: events.md, cloudevents.md) com catálogo e detalhes por tipo
6. Persiste em **paths.events** (`.ahrena/.directives`; padrão `docs/events`) e entrega resumo ou inline

## Prompt Template

```
Contexto:
- Contexto da feature/módulo: {{contexto da feature ou módulo}}
- Source base (opcional): {{source base}}

Tarefa:
Atue como o Warrior Kronos (Especialista em Event Storm) e execute de forma iterativa o **kata-events-doc**.
Com base no contexto acima, faça perguntas de clarificação quando necessário (módulo, entity type, eventos a catalogar, source base, payload) e refine o catálogo com base nas respostas. Consulte lex-cloudevents e codex-cloudevents e produza a documentação de eventos em paths.events.

Formato de saída:
- Consultar **paths.events** em `.ahrena/.directives` para o destino (padrão docs/events)
- Criar o diretório (paths.events) se não existir no projeto
- Criar ou atualizar o documento de eventos (ex.: events.md) nesse path
- Tabela de eventos (type, descrição, quando é emitido); para cada evento: type, source, subject, idempotencykey, estrutura de data conforme codex-entities
```

## Exemplo de Invocação

**Input:**

```
/cry-event-storm "Módulo platform, entidade scheduled_transfer: eventos created, updated e cancelled"
```

**Output esperado:**

Resposta estruturada do Warrior Kronos com:
- Catálogo de tipos (ex.: event.guardia.platform.scheduled_transfer.created, .updated, .cancelled)
- Para cada tipo: descrição, source, subject, idempotencykey, estrutura de data
- Documento criado ou atualizado no path **paths.events** (`.ahrena/.directives`; diretório criado se não existir)

## Restrições

- O Cry não implementa código; apenas dispara a documentação de eventos
- O contexto deve permitir identificar módulo, entidades e eventos; se estiver vago, o agente pode pedir complemento
- Exceções às Lexis devem ser documentadas em ADR

## Kata e Warrior Associados

- **kata-events-doc** — Documentação de eventos CloudEvents (Markdown) em paths.events
- **warrior-kronos** — Especialista em Event Storm; executa kata-events-doc

## Referências

- lex-cloudevents, lex-entities, lex-idempotency
- codex-cloudevents, codex-entities, codex-idempotency
