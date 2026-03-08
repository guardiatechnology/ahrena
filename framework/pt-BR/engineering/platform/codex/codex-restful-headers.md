# Codex: Headers HTTP em APIs RESTful

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Plataforma Guardia — APIs REST — headers

## Visão Geral

Headers padrão e customizados (X-Grd-*) para requisições e respostas HTTP da plataforma Guardia. Inclui regras para Idempotency-Key, Content-Digest, X-Grd-Debug e rastreamento.

## Contexto

- **Domínio:** headers HTTP em APIs da plataforma Guardia.
- **Público-alvo:** implementadores e consumidores de APIs.
- **Atualização:** quando a especificação de headers no Hub for alterada.

## Conteúdo

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
| Content-Digest | Response | Em respostas idempotentes | sha-256=&lt;hash&gt;; DEVE ser SHA-256 em hexadecimal com 64 caracteres; corpo da requisição DEVE ser normalizado em JSON antes do cálculo; valor inválido → 400 ERR400_MISSING_OR_MALFORMED_HEADER, reason INVALID_CONTENT_DIGEST |
| Last-Modified | Response | Em idempotência | Data última modificação (RFC 7232) |
| Retry-After | Response | Em 429 | Segundos para retentar |

### Headers customizados (X-Grd-*)

| Header | Direção | Obrigatoriedade | Descrição |
|--------|---------|-----------------|-----------|
| X-Grd-Debug | Request | Opcional | Valores permitidos: **true** ou **false** (qualquer outro valor → 400 ERR400_MISSING_OR_MALFORMED_HEADER, reason INVALID_DEBUG_HEADER_VALUE); habilita objeto debug na resposta; em produção: restringir por escopo (ex.: usuário/tenant), janela máx. 10 min, 10 req/min por cliente, intervalo mínimo 1 min entre ativações, uso auditado |
| X-Grd-Trace-Id | Response | Obrigatório | UUID v7; em todas as respostas; rastreamento em todas as camadas |
| X-Grd-Correlation-Id | Request/Response | Opcional | UUID; propagar se presente na requisição |

### Segurança

- Headers de rastreamento sem PII/segredos; validar por tenant e rate limit; sanitizar e limitar quantidade.

## Referências

- RFC 9110, 9111, 7232; codex-idempotency
- [codex-restful-apis](codex-restful-apis.md) (índice)
