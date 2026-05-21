# Cry: Design Completo — API e Eventos

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Processo único que combina design de API REST e documentação de eventos CloudEvents para uma nova feature

## Descrição

Este comando executa o **design completo** da superfície da feature: em uma única sequência, aciona o Warrior Daedalus para desenhar a API (OpenAPI + documento da API em **`docs/{context}/oas/`**) e em seguida o Warrior Kronos para documentar os eventos (Markdown em **`docs/{context}/events/`**). O agente executa as duas fases em sequência, usando a mesma descrição da feature como base. Equivale a combinar **cry-api-design** e **cry-event-storm** em um único fluxo.

## Uso

```
/cry-full-design <descrição da feature> [base path] [contexto de eventos]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `descrição da feature` | Sim | Descrição do domínio, entidades, operações de API e regras de negócio; serve de base tanto para a API quanto para o event storm | "Módulo de agendamento de transferências: criar, listar, atualizar e cancelar; listagem paginada; mutações idempotentes; eventos created, updated, cancelled" |
| `base path` | Não | Prefixo de URL para a API (ex.: /v1/scheduled-transfers). Se omitido, o Daedalus propõe | `/v1/scheduled-transfers` |
| `contexto de eventos` | Não | Complemento específico para eventos (ex.: módulo, entity type, source base). Se omitido, o Kronos infere do contexto da feature ou pergunta | "Módulo platform, entity type scheduled_transfer" |

## O que o Comando Faz

1. **Fase 1 — API:** Assume o papel do Warrior Daedalus; executa **kata-api-design-oas** e **kata-api-design-doc**; produz especificação OpenAPI e documento da API em **`docs/{context}/oas/`**
2. **Fase 2 — Eventos:** Assume o papel do Warrior Kronos; executa **kata-events-doc**; produz documentação de eventos em **`docs/{context}/events/`**
3. Usa a mesma descrição da feature como input para ambas as fases; na fase 2, pode usar o contexto de eventos explícito ou inferir a partir da API desenhada
4. Entrega resumo dos artefatos produzidos: OAS e doc da API em `docs/{context}/oas/`; doc de eventos em `docs/{context}/events/`

## Prompt Template

```
Contexto:
- Descrição da feature: {{descrição da feature}}
- Base path (opcional): {{base path}}
- Contexto de eventos (opcional): {{contexto de eventos}}

Tarefa:
Execute o processo de **design completo** em sequência:

1) **Fase API (Daedalus):** Atue como o Warrior Daedalus. Execute **kata-api-design-oas** e **kata-api-design-doc** com base na descrição da feature. Faça perguntas de clarificação se necessário (escopo, autenticação, paginação, base path). Produza especificação OpenAPI e documento da API em **`docs/{context}/oas/`**.

2) **Fase Event Storm (Kronos):** Atue como o Warrior Kronos. Com base na mesma feature (e no contexto de eventos, se informado), execute **kata-events-doc**. Identifique os eventos relevantes (ex.: created, updated, cancelled para as operações da API), faça perguntas de clarificação se necessário, e produza a documentação de eventos em **`docs/{context}/events/`**.

Entregue um resumo final: artefatos em `docs/{context}/oas/` (OAS + doc da API) e em `docs/{context}/events/` (doc de eventos).
```

## Exemplo de Invocação

**Input:**

```
/cry-full-design "Módulo de transferências agendadas: criar, listar, atualizar e cancelar; listagem paginada e ordenável; mutações idempotentes; eventos created, updated e cancelled" /v1/scheduled-transfers
```

**Output esperado:**

- **Fase 1:** Recursos e endpoints (POST, GET, GET/:id, PATCH, DELETE); especificação OpenAPI e doc da API criados/atualizados em **`docs/{context}/oas/`**
- **Fase 2:** Catálogo de eventos (event.guardia.financial.scheduled_transfer.created, .updated, .cancelled); doc de eventos criado/atualizado em **`docs/{context}/events/`**
- Resumo: três artefatos — OAS e doc da API em `docs/scheduled-payments/oas/`; doc de eventos em `docs/scheduled-payments/events/`

## Restrições

- O Cry não implementa código; apenas orquestra os dois Warriors
- A descrição da feature deve permitir tanto o design da API quanto a identificação dos eventos; se faltar informação para eventos, o Kronos fará perguntas na fase 2
- Exceções às Lexis devem ser documentadas em ADR

## Cries e Warriors Associados

- **cry-api-design** — Apenas design de API (Daedalus)
- **cry-event-storm** — Apenas documentação de eventos (Kronos)
- **warrior-daedalus** — Especialista em Design de API
- **warrior-kronos** — Especialista em Event Storm

## Referências

- `lex-feature-design-docs` — estrutura canônica `docs/{context}/{category}/`
- `cry-api-design`, `cry-event-storm` — Cries invocados (os Katas por eles executados consultam as Lexis e Codex aplicáveis; ver documentação dos Cries/Katas)
