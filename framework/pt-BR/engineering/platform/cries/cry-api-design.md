# Cry: Design de API para Nova Feature

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para desenhar a API REST de uma nova feature conforme Lexis e Codex da Guardia

## Descrição

Este comando aciona o Warrior Daedalus (ou o agente assumindo seu papel) para desenhar a API REST de uma nova feature: consultar Lexis e Codex RESTful e produzir **especificação OpenAPI 3.x** (kata-api-design-oas) e **documento Markdown** estruturado da API (kata-api-design-doc), ambos em **`docs/{context}/oas/`**.

## Uso

```
/cry-api-design <descrição da feature> [base path]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `descrição da feature` | Sim | Descrição do domínio, entidades, operações e regras de negócio relevantes para a API | "Módulo de agendamento de transferências: criar, listar, atualizar e cancelar; listagem paginada e ordenável; mutações idempotentes" |
| `base path` | Não | Prefixo de URL desejado (ex.: /v1/transactions). Se omitido, o agente propõe com base na feature | `/v1/scheduled-transfers` |

## O que o Comando Faz

1. Interpreta a descrição da feature e o base path (se informado)
2. Assume o papel do Warrior Daedalus (especialista em design de API) ou delega ao agente que executa kata-api-design-oas ou kata-api-design-doc (conforme formato pedido)
3. O Warrior Daedalus (ou o agente no seu papel) consulta lex-directives e as Lexis/Codex RESTful, entidades, idempotência, erros e auth
4. Identifica recursos, operações, paginação, ordenação e necessidade de Idempotency-Key
5. Produz especificação (OpenAPI ou Markdown) com endpoints, métodos, status, headers, payloads e erros
6. Entrega o artefato no formato solicitado ou inline

## Prompt Template

```
Contexto:
- Descrição da feature: {{descrição da feature}}
- Base path (opcional): {{base path}}

Tarefa:
Atue como o Warrior Daedalus (Especialista em Design de API) e execute de forma iterativa o **kata-api-design-oas** e o **kata-api-design-doc** (os Katas consultam as Lexis e Codex RESTful conforme sua documentação). Com base na descrição da feature acima, faça perguntas de clarificação quando necessário e refine o design com base nas respostas. Produza a especificação OpenAPI e o documento da API em `docs/{context}/oas/`. Use o base path informado ou proponha um adequado.

Formato de saída:
- Salvar em `docs/{context}/oas/` conforme `lex-feature-design-docs`
- Criar o diretório se não existir no projeto
- Criar ou atualizar a especificação OpenAPI e o documento Markdown da API nesse path
- Lista ou tabela de endpoints (path, método, resumo); para cada endpoint: parâmetros, headers obrigatórios (ex.: Idempotency-Key em mutações), códigos de status, estrutura de request/response (data, pagination, errors conforme codex-restful-payload)
```

## Exemplo de Invocação

**Input:**

```
/cry-api-design "Módulo de agendamento de transferências: usuário pode criar, listar, atualizar e cancelar; listagem paginada e ordenável por data; criar/atualizar/cancelar idempotentes" /v1/scheduled-transfers
```

**Output esperado:**

Resposta estruturada do Warrior Daedalus com:
- Recursos identificados (ex.: scheduled-transfers)
- Endpoints: POST (criar), GET (listar com paginação/ordenação), GET por id, PATCH (atualizar), DELETE (cancelar)
- Uso de Idempotency-Key em POST e PATCH; status 200/201/204/400/409/422 etc.; payload com data/pagination/errors conforme codex-restful-payload
- Especificação criada ou atualizada em `docs/{context}/oas/` (diretório criado se não existir)

## Restrições

- O Cry não implementa código; apenas dispara o design de API
- A descrição da feature deve ser suficiente para identificar recursos e operações; se estiver vaga, o agente pode pedir complemento
- Exceções às Lexis devem ser documentadas em ADR; o agente pode sinalizar quando uma decisão exigir ADR

## Cry vs Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Natureza** | Invocação rápida com descrição da feature e base path | Procedimento completo em múltiplos passos |
| **Complexidade** | Baixa (1 comando) | Alta (7 passos: diretivas, consulta Lexis/Codex, recursos, endpoints, erros, especificação, validação) |
| **Configura agente?** | Sim (assume papel do Warrior Daedalus) | Sim (define todos os passos do design) |
| **Exemplo** | "/cry-api-design criar/listar/cancelar transferências agendadas" | Executar kata-api-design-oas ou kata-api-design-doc com inputs explícitos, conforme formato desejado |

## Kata e Warrior Associados

- **kata-api-design-oas** — Design de API e produção de especificação OpenAPI 3.x em `docs/{context}/oas/`
- **kata-api-design-doc** — Design de API e produção de documento Markdown estruturado em `docs/{context}/oas/`
- **warrior-daedalus** — Especialista em Design de API; executa kata-api-design-oas e kata-api-design-doc (ambos em `docs/{context}/oas/`)

## Referências

- `kata-api-design-oas`, `kata-api-design-doc` — Procedimentos executados pelo Warrior Daedalus (os Katas consultam as Lexis e Codex RESTful; ver documentação dos Katas)
