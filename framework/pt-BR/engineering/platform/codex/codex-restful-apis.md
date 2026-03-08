# Codex: APIs RESTful da Plataforma Guardia

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Plataforma Guardia — APIs REST

## Visão Geral

Este Codex consolida as diretrizes para construção, consumo e documentação de APIs RESTful na plataforma Guardia. Cobre status codes, payloads de resposta, headers, paginação e ordenação. Exceções à spec devem ser documentadas em ADR.

**Referências Hub:** [RESTful](https://hub.guardia.finance/docs/specifications/restful/) | [Status Codes](https://hub.guardia.finance/docs/specifications/restful/http-status-code/) | [Payload](https://hub.guardia.finance/docs/specifications/restful/http-response-payloads/) | [Headers](https://hub.guardia.finance/docs/specifications/restful/http-headers/) | [Paginação](https://hub.guardia.finance/docs/specifications/restful/http-pagination/) | [Ordenação](https://hub.guardia.finance/docs/specifications/restful/http-sorting/)

## Contexto

- **Domínio:** APIs HTTP da plataforma Guardia (respostas, headers, paginação, ordenação).
- **Público-alvo:** implementadores e consumidores de APIs.
- **Atualização:** quando as especificações RESTful no Hub forem alteradas.

---

## Módulo 1: Status Codes

Códigos de status permitidos e regras de uso. Códigos utilizados em cada endpoint DEVEM constar no contrato OAS. Padrão mínimo para qualquer API RESTful da Guardia.

### 2xx — Sucesso

| Código | Status | Métodos | Quando usar | Quando não usar |
|--------|--------|---------|-------------|-----------------|
| 200 | OK | GET, POST, PUT, PATCH | Operação bem-sucedida com dados; listagem vazia processada com sucesso | Novo recurso criado (use 201); processamento pendente (use 202); sem conteúdo (use 204) |
| 201 | Created | POST, PUT | Novo recurso criado | Recurso já existia/atualizado; criação ainda não concluída (use 202) |
| 202 | Accepted | POST, PUT, PATCH | Aceito; processamento assíncrono | Resultado já disponível |
| 204 | No Content | DELETE, PUT, PATCH | Sucesso sem corpo | Quando há conteúdo a retornar |

### 3xx — Redirecionamento

| Código | Status | Quando usar | Quando não usar |
|--------|--------|-------------|-----------------|
| 301 | Moved Permanently | Recurso movido permanentemente; descontinuação de rota | Mudança temporária (use 307) |
| 304 | Not Modified | Recurso inalterado (cache, If-Modified-Since/ETag) | Conteúdo alterado (use 200) |
| 307 | Temporary Redirect | Recurso temporariamente em outra URL; método e corpo preservados | Mudança permanente (use 301); nunca converter método para GET |

### 4xx — Erro do cliente

| Código | Status | Quando usar | Quando não usar |
|--------|--------|-------------|-----------------|
| 400 | Bad Request | Requisição malformada ou inválida | Dados corretos mas semântica inválida (use 422) |
| 401 | Unauthorized | Autenticação ausente ou token inválido | Autenticado sem permissão (use 403) |
| 402 | Payment Required | Acesso condicionado a pagamento/assinatura | Problema de permissão (use 403) |
| 403 | Forbidden | Autenticado mas sem autorização para o recurso | Não autenticado (use 401) |
| 404 | Not Found | Recurso inexistente | Recurso existe mas acesso restrito (use 403) |
| 408 | Request Timeout | Cliente demorou para completar a requisição | Timeout entre servidores (use 504) |
| 409 | Conflict | Conflito com estado atual (duplicidade, versão) | Erro de validação (use 400/422) |
| 422 | Unprocessable Entity | Dados sintaticamente corretos, semanticamente inválidos | Formatação ou propriedades faltando (use 400) |
| 429 | Too Many Requests | Limite de requisições excedido | Erro não relacionado a rate limit |

### 5xx — Erro do servidor

| Código | Status | Quando usar | Quando não usar |
|--------|--------|-------------|-----------------|
| 500 | Internal Server Error | Falha inesperada ou exceção não tratada | Erro previsível/tratável pelo cliente |
| 501 | Not Implemented | Método válido não suportado; funcionalidade não implementada | Falha ao processar (use 500) |
| 502 | Bad Gateway | Resposta inválida de outro servidor | Erro no próprio serviço (use 500) |
| 503 | Service Unavailable | Serviço temporariamente indisponível | Serviço ativo com falha interna (use 500) |
| 504 | Gateway Timeout | Sem resposta a tempo de outro servidor | Timeout cliente→servidor (use 408) |

**Referências:** RFC 9110; MDN.

---

## Módulo 2: Payload de Resposta

Estrutura unificada para sucesso e erro. Aplicável a todas as requisições HTTP da plataforma.

### Estrutura padrão

| Propriedade | Tipo | Descrição |
|-------------|------|-----------|
| data | object \| array | Dados quando 2xx; objeto para entidade única, array para lista; ausente em 4xx/5xx |
| pagination | object | Presente somente em recurso paginado (2xx); estrutura abaixo; ausente em erro |
| errors | array | Lista de erros quando 4xx/5xx; cada item: code, reason, message (conforme codex-error-handling); ausente em 2xx |
| debug | object | Somente se header X-Grd-Debug: true; trace_id, correlation_id, instance, timestamp, duration, memory, query, params, internal_ip, external_ip; nunca dados sensíveis |

### Sucesso

- `data` com entidade(s); incluir entity_id, external_entity_id, entity_type conforme codex-entities quando for entidade.
- Com paginação: `data` array + `pagination` (page_size, total_count, first_page_token, previous_page_token, next_page_token, last_page_token).

### Erro

- `errors`: array de { code, reason, message }; code conforme Tratamento de Erros; message orientada ao desenvolvedor, não ao usuário final.

### Debug

- Incluir somente com X-Grd-Debug: true; campos de rastreamento (trace_id, correlation_id, instance, timestamp, duration, memory, etc.).

**Referências:** codex-entities, codex-error-handling; RFC 7807.

---

## Módulo 3: Headers

### Headers padrão

| Header | Direção | Obrigatoriedade | Descrição |
|--------|---------|-----------------|-----------|
| Accept | Request | Opcional | Formato aceito (ex.: application/vnd.guardia.v1+json) |
| Accept-Language | Request | Opcional | Idioma preferido |
| Content-Type | Request/Response | Opcional | Formato do conteúdo |
| Content-Language | Response | Opcional | Idioma da resposta |
| Cache-Control | Response | Opcional | Diretivas de cache (public/private, max-age; no-store) |
| Link | Response | Opcional | Navegação (paginação rel first/previous/next/last; HATEOAS) |
| Idempotency-Key | Request/Response | Obrigatório em mutações | UUID; conforme codex-idempotency |
| Content-Digest | Response | Em respostas idempotentes | sha-256=&lt;hash&gt; 64 chars hex; conforme idempotência |
| Last-Modified | Response | Em idempotência | Data última modificação (RFC 7232) |
| Retry-After | Response | Em 429 | Segundos para retentar |

### Headers customizados (X-Grd-*)

| Header | Direção | Obrigatoriedade | Descrição |
|--------|---------|-----------------|-----------|
| X-Grd-Debug | Request | Opcional | true/false; habilita objeto debug na resposta; validação: 400 ERR400_MISSING_OR_MALFORMED_HEADER, INVALID_DEBUG_HEADER_VALUE se valor inválido; em produção: escopo, 10 min, 10 req/min, intervalo 1 min, auditoria |
| X-Grd-Trace-Id | Response | Obrigatório | UUID v7; em todas as respostas; rastreamento em todas as camadas |
| X-Grd-Correlation-Id | Request/Response | Opcional | UUID; propagar se presente na requisição |

**Segurança:** headers de rastreamento sem PII/segredos; validar por tenant e rate limit; sanitizar e limitar quantidade.

**Referências:** RFC 9110, 9111, 7232; codex-idempotency.

---

## Módulo 4: Paginação

### Requisição

| Parâmetro | Tipo | Default | Máximo | Regra |
|----------|------|---------|--------|-------|
| page_size | uint32 | 20 | 100 | Rejeitar acima do limite com 400 ERR400_INVALID_PARAMETER (PAGE_SIZE_TOO_LARGE, etc.) |
| page_token | string | — | — | Token opaco; retornado em chamadas anteriores |
| order_by | string | created_at | — | created_at, updated_at, reference_at; outro valor → 400 ORDER_BY_INVALID |
| sort | string | asc | — | asc, desc (case insensitive); outro → 400 SORT_INVALID |

### Resposta

- `data`: array da página atual.
- `pagination`: page_size, total_count, first_page_token, previous_page_token, next_page_token, last_page_token (todos presentes, nulos quando não aplicável).
- Headers: Cache-Control (ex.: max-age=900), Link com rel first, previous, next, last.

### Comportamentos

- Primeira página: sem page_token, page_size=20.
- Suporte a paginação reversa (previous_page_token, first_page_token).
- Ordenação estável e determinística.
- Tokens opacos (criptografados/assinados); expiração (ex.: 10 min); log com X-Grd-Trace-Id.
- Sem resultados: 200 OK, lista vazia, total_count=0.

### Erros conhecidos

| Cenário | HTTP | code | reason |
|---------|------|------|--------|
| page_token inválido/expirado | 400 | ERR400_INVALID_PARAMETER | PAGE_TOKEN_INVALID, PAGE_TOKEN_EXPIRED |
| page_size inválido/acima do limite | 400 | ERR400_INVALID_PARAMETER | PAGE_SIZE_INVALID, PAGE_SIZE_TOO_LARGE |
| order_by/sort inválido | 400 | ERR400_INVALID_PARAMETER | ORDER_BY_INVALID, SORT_INVALID |

**Referências:** Hub Paginação; HATEOAS.

---

## Módulo 5: Ordenação

- Ordenação limitada a propriedades temporais: created_at, updated_at, reference_at.
- Uso de índices; ordenação estável (critério secundário ex.: entity_id).
- Parâmetros: order_by (default created_at), sort (default asc). Ausência → created_at asc.
- Valores não permitidos em order_by ou sort → 400 Bad Request (ERR400_INVALID_PARAMETER, ORDER_BY_INVALID, SORT_INVALID).
- Exceção: ordenação fixa por regra de negócio pode omitir order_by se registrado em PDR.

**Referências:** Hub Ordenação; OAS.

---

## Referências gerais

- [RESTful APIs — Hub Guardia](https://hub.guardia.finance/docs/specifications/restful/)
- codex-entities, codex-idempotency, codex-error-handling
- RFC 9110 (HTTP Semantics), RFC 9111 (Caching), RFC 7232 (Conditional Requests), RFC 7807 (Problem Details)
