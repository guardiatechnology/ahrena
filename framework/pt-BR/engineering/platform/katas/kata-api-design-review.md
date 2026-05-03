# Kata: Revisão de Design de API RESTful

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Plataforma Guardia — revisão de contratos de API HTTP existentes contra as Lexis e Codex da Guardia

## Objetivo

Este Kata define o procedimento para **revisar um contrato de API existente** (especificação OpenAPI 3.x ou documento Markdown) contra as Lexis e Codex RESTful da Guardia, identificando violações de conformidade, lacunas e melhorias, e produzindo um relatório de revisão estruturado com findings classificados por severidade.

## Quando Usar

- Quando um arquivo OAS ou documento Markdown de API existente precisa ser validado contra as regras da Guardia antes ou depois da implementação
- Quando um PR inclui alterações em um contrato de API que deve passar no Gate 2 (kata-quality-gate)
- Quando invocado pelo Warrior Daedalus como parte de um ciclo de design-revisão
- Quando `cry-api-review` é acionado pelo usuário

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Caminho do contrato | Sim | Caminho para o arquivo OAS (YAML/JSON) ou documento Markdown de API a ser revisado |
| Escopo da revisão | Não | Endpoints ou regras específicos para focar. Se omitido, revisa o contrato completo |
| Modo | Não | `report` (padrão) — apenas findings; `fix` — propõe correções inline junto com os findings |

## Workflow

```
Progresso:
- [ ] 1. Ler diretivas e localizar contrato
- [ ] 2. Consultar Lexis e Codex
- [ ] 3. Validar endpoints (paths, métodos, status codes)
- [ ] 4. Validar estrutura de entidades
- [ ] 5. Validar idempotência
- [ ] 6. Validar estrutura de erros
- [ ] 7. Validar autenticação
- [ ] 8. Validar paginação e ordenação
- [ ] 9. Produzir relatório de revisão
```

### Passo 1: Ler Diretivas e Localizar Contrato

1. Identificar o `language.default` em `.ahrena/.directives`
2. Localizar o contrato no caminho fornecido. Se o caminho não existir ou não puder ser parseado, alertar o usuário e parar
3. Identificar se o contrato é OpenAPI 3.x (YAML/JSON) ou Markdown. Se não estiver claro, perguntar ao usuário
4. Registrar o escopo da revisão: todos os endpoints ou um subconjunto específico

### Passo 2: Consultar Lexis e Codex

1. Consultar **lex-restful-apis** — conformidade geral para endpoints HTTP
2. Consultar **codex-restful-apis**, codex-restful-status-codes, codex-restful-payload, codex-restful-headers, codex-restful-pagination, codex-restful-sorting
3. Consultar **lex-entities** e **codex-entities** — estrutura base de entidade (entity_id, entity_type, version, timestamps)
4. Consultar **lex-idempotency** e **codex-idempotency** — Idempotency-Key para mutações
5. Consultar **lex-error-handling** e **codex-error-handling** — estrutura de erro (code, reason, message)
6. Consultar **lex-auth** e **codex-auth** — autenticação e autorização
7. Consultar **codex-oas-structure** — ordenação de operações dentro de paths (POST, GET, PUT, PATCH, DELETE)

### Passo 3: Validar Endpoints (paths, métodos, status codes)

Para cada endpoint no contrato:

1. **Formato do path** — nomenclatura RESTful: substantivos no plural, kebab-case, prefixo de versão `/v1/`; identificador no path (ex: `/{entity_id}`)
2. **Métodos HTTP** — semântica correta: POST = criar, GET = ler, PATCH ou PUT = atualizar, DELETE = remover
3. **Status codes** — apenas códigos permitidos por codex-restful-status-codes: 200, 201, 204, 400, 401, 403, 404, 409, 422, 429, 500; sinalizar qualquer código fora do conjunto permitido
4. **Ordenação de operações** (apenas OAS) — POST, GET, PUT, PATCH, DELETE por path conforme codex-oas-structure; sinalizar desvios
5. **Headers obrigatórios** — X-Grd-Trace-Id quando aplicável; Content-Type, Accept

### Passo 4: Validar Estrutura de Entidades

Para cada payload de resposta que representa uma entidade persistente:

1. **entity_id** — presente e tipado como UUID
2. **entity_type** — presente e string não vazia
3. **created_at**, **updated_at** — presentes como timestamps ISO 8601
4. **discarded_at** — presente quando o endpoint suporta soft delete; sinalizar ausência apenas quando DELETE está implementado
5. **version** — presente quando locking otimista está documentado
6. Sinalizar qualquer entidade com campos obrigatórios ausentes conforme lex-entities

### Passo 5: Validar Idempotência

Para cada operação que modifica estado (POST, PATCH, PUT):

1. **Header Idempotency-Key** — declarado como obrigatório na definição do endpoint
2. **Resposta 400** — documentada para Idempotency-Key ausente (`ERR400_MISSING_IDEMPOTENCY_KEY`)
3. **Resposta 409** — documentada para mesma chave com payload diferente
4. Sinalizar qualquer endpoint de mutação sem Idempotency-Key conforme lex-idempotency

### Passo 6: Validar Estrutura de Erros

Para cada resposta de erro:

1. **Array `errors`** — body usa `{ "errors": [{ "code": "...", "reason": "...", "message": "..." }] }`
2. **Formato do `code`** — segue o padrão `ERR{HTTP_CODE}_{NOME}` (ex: `ERR400_MISSING_FIELD`, `ERR404_NOT_FOUND`)
3. **`reason`** — deve ser um valor catalogado conforme codex-known-errors
4. **Mensagens de autenticação** — respostas 401/403 não devem revelar se o usuário ou recurso existe conforme lex-error-handling
5. Sinalizar qualquer resposta de erro que desvia da estrutura padrão

### Passo 7: Validar Autenticação

1. **Endpoints protegidos** — esquema de autenticação declarado (OAuth 2.0 / Bearer JWT)
2. **APIs públicas** — Client Credentials + extensões FAPI 2.0 documentadas quando aplicável
3. **APIs privadas** — JWT de IdP confiável + escopo RBAC documentado
4. Sinalizar qualquer endpoint protegido sem documentação de autenticação conforme lex-auth

### Passo 8: Validar Paginação e Ordenação

Para cada endpoint de listagem (GET retornando coleção):

1. **Parâmetros de request** — `page_size` e `page_token` declarados como query parameters
2. **Estrutura da resposta** — objeto `pagination` com `first_page_token`, `next_page_token`, `prev_page_token`, `page_size` conforme codex-restful-pagination
3. **Ordenação** — parâmetros `order_by` e `sort` declarados quando ordenação é suportada
4. Sinalizar qualquer endpoint de coleção sem paginação conforme codex-restful-pagination

### Passo 9: Produzir Relatório de Revisão

Gerar um relatório Markdown estruturado:

1. **Cabeçalho** — contrato revisado (caminho, formato, total de endpoints), veredicto geral:
   - ✅ **Conforme** — zero ERRORs e zero WARNINGs
   - ⚠️ **Avisos** — zero ERRORs, um ou mais WARNINGs
   - ❌ **Violações** — um ou mais ERRORs
2. **Tabela de findings** — uma linha por finding:

   | Severidade | Endpoint | Lexis / Codex | Finding | Sugestão |
   |------------|----------|---------------|---------|----------|

   Níveis de severidade:
   - `ERROR` — violação de Lexis; DEVE ser corrigido antes do merge
   - `WARNING` — desvio de Codex; DEVERIA ser corrigido
   - `INFO` — oportunidade de melhoria; PODE ser endereçado

3. **Contagem resumida** — total ERROR / WARNING / INFO
4. **Próximos passos** — no modo `fix`, acrescentar correção inline para cada ERROR e WARNING; no modo `report`, listar os endpoints que necessitam atenção

Se não houver findings, afirmar: "Contrato totalmente conforme com as Lexis e Codex da Guardia."

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Relatório de revisão | Markdown | Entregue no chat; opcionalmente salvo em `docs/reviews/api-review-{nome-contrato}.md` |

## Exemplo de Execução

### Input de Exemplo

```
Caminho do contrato: docs/oas/openapi.yaml
Escopo da revisão: todos os endpoints
Modo: report
```

### Output de Exemplo (resumo)

```markdown
## Revisão de Design de API — openapi.yaml

**Endpoints revisados:** 5 | **Veredicto:** ❌ 2 ERRORs, 3 WARNINGs

| Severidade | Endpoint | Regra | Finding | Sugestão |
|------------|----------|-------|---------|----------|
| ERROR | POST /v1/transfers | lex-idempotency | Header Idempotency-Key não declarado | Adicionar header obrigatório Idempotency-Key; documentar respostas 400 e 409 |
| ERROR | GET /v1/transfers/{entity_id} | lex-entities | entity_type ausente do schema de resposta | Adicionar entity_type: string (não vazio) ao schema TransferResponse |
| WARNING | DELETE /v1/transfers/{entity_id} | codex-restful-status-codes | Status 200 usado em vez de 204 para resposta sem body | Alterar para 204 No Content |
| WARNING | GET /v1/transfers | codex-restful-pagination | page_token ausente do objeto pagination na resposta | Adicionar page_token ao schema de pagination |
| WARNING | POST /v1/transfers | codex-oas-structure | GET declarado antes de POST na definição do path | Reordenar: POST, depois GET |

**Próximos passos:** corrigir 2 ERRORs antes do merge; 3 WARNINGs devem ser endereçados no mesmo PR.
```

## Restrições

- Este Kata produz apenas um relatório de revisão; não modifica o contrato a menos que o modo `fix` seja explicitamente solicitado
- Todo desvio DEVE ser classificado como ERROR (Lexis) ou WARNING (Codex) — nunca aceitar violações silenciosamente
- Escalar para um humano quando um desvio pode ser uma exceção intencional que requer um ADR
- Não sinalizar desvios em endpoints explicitamente excluídos do escopo da revisão

## Referências

- lex-restful-apis, lex-entities, lex-idempotency, lex-error-handling, lex-auth
- codex-restful-apis, codex-restful-status-codes, codex-restful-payload, codex-restful-headers, codex-restful-pagination, codex-restful-sorting, codex-entities, codex-idempotency, codex-error-handling, codex-auth, codex-oas-structure
