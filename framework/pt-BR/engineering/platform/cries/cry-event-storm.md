# Cry: Event Storm — Descoberta e Documentação de CloudEvents

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para descobrir e documentar eventos CloudEvents de uma feature ou módulo conforme Lexis e Codex da Guardia

## Descrição

Este comando aciona o Warrior Kronos (especialista em Event Storm) para descobrir e documentar eventos CloudEvents de uma feature ou módulo em duas fases. Quando o panorama de eventos é desconhecido, Kronos executa primeiro o **kata-event-storm** (Descoberta) para mapear eventos de domínio, comandos, agregados, políticas, hotspots e bounded contexts, e então prossegue para o **kata-events-doc** (Documentação). Quando os eventos já estão identificados, Kronos vai diretamente para a Documentação.

## Uso

```
/cry-event-storm <contexto da feature ou módulo> [source base]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `contexto da feature ou módulo` | Sim | Nome do módulo e descrição do domínio (para Descoberta) ou lista explícita de tipos de evento (apenas para Documentação) | `"Módulo platform, transferências agendadas — eventos desconhecidos"` ou `"event.guardia.financial.scheduled_transfer.created, .updated, .cancelled"` |
| `source base` | Não | Base da URI `source` (ex.: `https://tenant.guardia.finance/platform/api/v1`). Se omitido, o agente propõe conforme codex-cloudevents | `https://tenant.guardia.finance/platform/api/v1` |

## O que o Comando Faz

1. Assume o papel do Warrior Kronos e **determina o ponto de entrada**:
   - Contexto descreve um domínio sem eventos conhecidos → **Fase 1: Descoberta** (kata-event-storm) depois **Fase 2: Documentação** (kata-events-doc)
   - Contexto fornece lista explícita de tipos de evento → **Fase 2: Documentação apenas** (kata-events-doc)
2. **Fase 1 — Descoberta** (quando aplicável): executa kata-event-storm iterativamente — mapeia eventos de domínio (timeline), comandos, atores, agregados, políticas, sistemas externos, read models, hotspots e bounded contexts; produz catálogo CloudEvents; apresenta ao usuário para confirmação; resolve hotspots P1 antes de avançar
3. **Fase 2 — Documentação**: executa kata-events-doc — documenta estrutura do evento, payload (data), idempotência; gera ou atualiza o documento formal de eventos em **`docs/{context}/events/`**
4. Persiste ambos os artefatos (documento de descoberta quando a Fase 1 foi executada; documento de eventos sempre) em **`docs/{context}/events/`**; cria o diretório se não existir

## Prompt Template

```
Contexto:
- Contexto da feature/módulo: {{contexto da feature ou módulo}}
- Source base (opcional): {{source base}}

Tarefa:
Atue como o Warrior Kronos (Especialista em Event Storm) e determine o ponto de entrada:
- Se o panorama de eventos for desconhecido ou o domínio ainda não foi mapeado →
  execute kata-event-storm primeiro (Fase 1 — Descoberta), depois kata-events-doc
  (Fase 2 — Documentação).
- Se uma lista explícita de tipos de evento for fornecida → execute kata-events-doc
  diretamente (Fase 2 — Documentação apenas).

Trabalhe de forma iterativa: faça perguntas de clarificação quando necessário e
aguarde respostas antes de avançar. Não prossiga da Fase 1 para a Fase 2 se
houver hotspots P1 não resolvidos.

Formato de saída:
- Salvar em `docs/{context}/events/` conforme `lex-feature-design-docs`
- Criar o diretório se não existir
- Fase 1 (quando executada): salvar documento de descoberta de event storm (ex.: event-storm-{modulo}.md)
- Fase 2: criar ou atualizar o documento formal de eventos (events.md)
- Confirmar os paths de todos os artefatos persistidos
```

## Exemplos de Invocação

**Cenário A — Panorama de eventos desconhecido (Fase 1 → Fase 2):**

```
/cry-event-storm "Módulo platform, transferências agendadas — contadores agendam transferências bancarias para execução futura; aprovação do supervisor obrigatória antes da execução"
```

Output esperado:
- Kronos executa kata-event-storm: mapeia timeline, comandos, atores, agregados, hotspots
- Apresenta catálogo CloudEvents para confirmação; resolve hotspots P1
- Executa kata-events-doc e produz documento formal de eventos
- Ambos os artefatos salvos em `docs/{context}/events/`

**Cenário B — Eventos já conhecidos (Fase 2 apenas):**

```
/cry-event-storm "event.guardia.financial.scheduled_transfer.created, .updated, .cancelled"
```

Output esperado:
- Kronos executa kata-events-doc diretamente
- Faz perguntas sobre source base e payload se necessário
- Documento de eventos criado ou atualizado em `docs/{context}/events/`

## Restrições

- O Cry não implementa código (publicadores ou consumidores); apenas dispara descoberta e documentação
- Hotspots P1 identificados na Fase 1 bloqueiam a transição para a Fase 2 — devem ser resolvidos antes da documentação
- O contexto deve ser suficiente para identificar o módulo e o domínio ou os tipos de evento; se estiver vago, Kronos solicita complemento
- Exceções às Lexis devem ser documentadas em ADR

## Katas e Warrior Associados

| Artefato | Fase | Descrição |
|----------|------|-----------|
| `kata-event-storm` | 1 — Descoberta | Eventos de domínio, comandos, agregados, políticas, bounded contexts, catálogo CloudEvents |
| `kata-events-doc` | 2 — Documentação | Documento formal de CloudEvents (Markdown) em `docs/{context}/events/` |
| `warrior-kronos` | Orquestrador | Determina o ponto de entrada e orquestra as duas fases |

## Referências

- `warrior-kronos` — Especialista em Event Storm; roteia entre Descoberta e Documentação conforme o contexto
- `kata-event-storm` — Procedimento de Descoberta (Fase 1)
- `kata-events-doc` — Procedimento de Documentação (Fase 2)
