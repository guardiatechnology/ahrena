# Kata: Design de API RESTful para Nova Feature — Especificação OpenAPI (OAS)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Plataforma Guardia — design de APIs REST e produção de especificação OpenAPI 3.x

## Objetivo

Este Kata define o procedimento para desenhar a API REST de uma nova feature e **produzir especificação em formato OpenAPI 3.x** (YAML ou JSON): consultar Lexis e Codex, identificar recursos e operações, definir endpoints e persistir o contrato em **paths.oas** em conformidade com as regras da Guardia.

## Quando Usar

- Quando o formato de saída desejado é **OpenAPI 3.x** (YAML ou JSON)
- Quando uma nova feature exige exposição via API HTTP e ainda não existe contrato definido
- Quando invocado pelo `cry-api-design` ou pelo Warrior Daedalus com output OAS
- Quando é necessário gerar ou atualizar um arquivo OAS em `docs/oas` (ou path definido em paths.oas)

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Descrição da feature | Sim | Descrição textual do domínio, entidades, operações e regras de negócio relevantes para a API |
| Contexto ou escopo | Não | Restrições (ex.: apenas leitura, apenas um recurso), base path desejado ou convenção existente |
| Base path | Não | Prefixo de URL (ex.: `/v1/transactions`). Se omitido, o agente propõe com base na feature |
| Formato OAS | Não | YAML ou JSON. Se omitido, usar YAML como padrão |

## Workflow

```
Progresso:
- [ ] 1. Ler diretivas e contexto
- [ ] 2. Consultar Lexis e Codex RESTful
- [ ] 3. Identificar recursos e operações
- [ ] 4. Desenhar endpoints (paths, métodos, status, headers, payloads)
- [ ] 5. Documentar erros e idempotência
- [ ] 6. Produzir especificação OpenAPI 3.x
- [ ] 7. Validação final
```

### Passo 1: Ler Diretivas e Contexto

1. Ler `.ahrena/.directives` para obter `language.default`, caminhos canônicos e **paths.oas** (destino da especificação; padrão `docs/oas`)
2. Confirmar que a descrição da feature foi fornecida. **Trabalhar de forma iterativa:** se incompleta ou ambígua, **fazer perguntas ao usuário** (ex.: API pública ou privada? Paginação e ordenação? Base path? Soft delete ou discarded_at? Filtros?) e aguardar respostas; repetir até os critérios ficarem claros
3. Registrar o base path informado ou propor um (ex.: `/v1/<recurso-principal>`) em kebab-case e versão na URL quando aplicável
4. Identificar se a API é pública (Client Credentials, FAPI 2.0) ou privada (JWT, RBAC) para alinhar com lex-auth

### Passo 2: Consultar Lexis e Codex RESTful

1. Consultar **lex-directives** (obrigatório)
2. Consultar **lex-restful-apis** — conformidade geral em endpoints HTTP
3. Consultar **codex-restful-apis** e módulos referenciados: codex-restful-status-codes, codex-restful-payload, codex-restful-headers, codex-restful-pagination, codex-restful-sorting
4. Consultar **lex-entities** e **codex-entities** — estrutura base de entidades (entity_id, entity_type, version, created_at, updated_at, discarded_at)
5. Consultar **lex-idempotency** e **codex-idempotency** — Idempotency-Key em mutações
6. Consultar **lex-error-handling** e **codex-error-handling** — estrutura de erros (code, reason, message)
7. Consultar **lex-auth** e **codex-auth** — autenticação e autorização (OAuth 2.0, JWT, RBAC)
8. Consultar **codex-oas-structure** — ordem das operações em paths (POST, GET, PUT, PATCH, DELETE)

### Passo 3: Identificar Recursos e Operações

1. Extrair **recursos** (substantivos) da descrição da feature — ex.: transação, usuário, contrato
2. Para cada recurso, listar **operações** necessárias: criar, ler, atualizar, excluir (soft delete quando aplicável), listar (com paginação)
3. Identificar operações que **modificam estado** (POST, PATCH, PUT) e marcar como obrigatório Idempotency-Key
4. Identificar listagens que exigem **paginação** (page_size, page_token) e **ordenação** (order_by, sort)
5. Mapear entidades persistentes que devem seguir a estrutura base (entity_id, entity_type, version, timestamps)

### Passo 4: Desenhar Endpoints (paths, métodos, status, headers, payloads)

1. Definir **paths** no formato RESTful: recurso em plural ou singular conforme convenção do projeto; identificador por path (ex.: `/v1/transactions/{entity_id}`)
2. Atribuir **métodos HTTP**: GET (leitura), POST (criação), PATCH ou PUT (atualização), DELETE (exclusão lógica quando aplicável). Ordenar métodos HTTP por path conforme **codex-oas-structure**: POST, GET, PUT, PATCH, DELETE (omitir os não utilizados no path, mantendo a ordem)
3. Para cada endpoint, definir **códigos de status** conforme codex-restful-status-codes (ex.: 200, 201, 204, 400, 401, 403, 404, 409, 422, 429, 500)
4. Definir **headers** obrigatórios: Idempotency-Key em mutações; X-Grd-Trace-Id quando aplicável; Content-Type, Accept
5. Definir **payload de request**: corpo para POST/PATCH/PUT; parâmetros de query para listagem (page_size, page_token, order_by, sort)
6. Definir **payload de response**: estrutura `data` (objeto ou array), `pagination` quando listagem paginada, conforme codex-restful-payload
7. Garantir que entidades em resposta incluam campos obrigatórios de codex-entities (entity_id, entity_type, created_at, updated_at, version quando aplicável)

### Passo 5: Documentar Erros e Idempotência

1. Para cada endpoint de mutação, documentar que **Idempotency-Key** é obrigatório; respostas 400 (ausente), 409 (mesma chave, payload diferente)
2. Listar **erros conhecidos** por endpoint: códigos ERR4xx/ERR5xx, reason (conforme codex-error-handling), message orientada ao desenvolvedor
3. Garantir que respostas de erro usem apenas a estrutura `errors` (array de code, reason, message); sem expor dados sensíveis em mensagens de autenticação (lex-error-handling)
4. Documentar **paginação** em listagens: parâmetros de request (page_size, page_token), estrutura de resposta (pagination com first_page_token, next_page_token, etc.)

### Passo 6: Produzir Especificação OpenAPI 3.x

1. Obter o path canônico **paths.oas** em `.ahrena/.directives`. Garantir que o diretório exista na raiz do projeto; se não existir, criá-lo
2. Gerar **fragmento ou documento OpenAPI 3.x** em YAML ou JSON (conforme input ou padrão YAML), contendo:
   - `openapi: 3.x`
   - `paths` com cada endpoint; em cada path, listar as operações na ordem **codex-oas-structure**: post, get, put, patch, delete; em cada operação: `parameters` (path, query, header), `requestBody` quando aplicável, `responses` (200, 201, 204, 400, 401, 403, 404, 409, 422, 429, 500)
   - Componentes de headers globais (Idempotency-Key, X-Grd-Trace-Id, Content-Type, Authorization) conforme codex-restful-headers
   - Schemas de request/response alinhados a codex-restful-payload e codex-entities
3. Nomear o arquivo de forma consistente (ex.: `openapi.yaml`, `api-spec.yaml` ou nome do recurso principal). Salvar em **paths.oas** (criar ou atualizar). Se o usuário solicitar entrega inline além do arquivo, entregar também no chat

### Passo 7: Validação Final

Antes de entregar o output, verificar:

- [ ] Todos os endpoints seguem lex-restful-apis (status, payload, headers, paginação, ordenação conforme spec)
- [ ] Operações de mutação exigem Idempotency-Key (lex-idempotency)
- [ ] Entidades persistentes seguem estrutura base (lex-entities)
- [ ] Erros seguem estrutura padronizada e códigos conhecidos (lex-error-handling)
- [ ] Autenticação/autorização documentadas conforme lex-auth quando a API for protegida
- [ ] Listagens paginadas têm page_size, page_token e estrutura pagination na resposta
- [ ] Arquivo OpenAPI 3.x está completo (paths, methods, parameters, responses) e sem contradição com as Lexis
- [ ] Ordem das operações em cada path segue codex-oas-structure (POST, GET, PUT, PATCH, DELETE)
- [ ] Arquivo foi salvo no path **paths.oas** (diretório criado se não existia)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Especificação OpenAPI 3.x | YAML ou JSON | Diretório **paths.oas** em `.ahrena/.directives` (criar diretório se não existir; criar ou atualizar o arquivo) |

## Exemplo de Execução

### Input de Exemplo

```
Feature: Módulo de agendamento de transferências. Criar, listar, atualizar e cancelar; listagem paginada e ordenável por data; mutações idempotentes.
Base path: /v1/scheduled-transfers
Formato: YAML
```

### Output de Exemplo (resumido)

Arquivo `openapi.yaml` (ou similar) em **paths.oas** com `paths` incluindo:
- `POST /v1/scheduled-transfers` — 201, Idempotency-Key obrigatório
- `GET /v1/scheduled-transfers` — 200, query page_size, page_token, order_by, sort; response com data e pagination
- `GET /v1/scheduled-transfers/{entity_id}` — 200, 404
- `PATCH /v1/scheduled-transfers/{entity_id}` — 200, 409 (Idempotency-Key)
- `DELETE /v1/scheduled-transfers/{entity_id}` — 204, 404

Payloads e erros conforme codex-restful-payload e codex-entities.

## Restrições

- Este Kata produz apenas especificação OpenAPI 3.x; não implementa código
- Não altera contratos OAS já publicados sem justificativa e ADR
- Exceções às Lexis devem ser documentadas em ADR e refletidas no OAS
- O agente deve escalar para humano quando houver conflito entre Lexis e requisito de negócio ou quando a feature envolver múltiplos bounded contexts com fronteiras de API não claras

## Referências

- lex-directives, lex-restful-apis, lex-entities, lex-idempotency, lex-error-handling, lex-auth
- codex-restful-apis, codex-restful-status-codes, codex-restful-payload, codex-restful-headers, codex-restful-pagination, codex-restful-sorting, codex-entities, codex-idempotency, codex-error-handling, codex-auth, codex-oas-structure
- [OpenAPI Specification 3.x](https://spec.openapis.org/oas/v3.0.3)
