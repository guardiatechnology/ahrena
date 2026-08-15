# Lexis: Conformidade RESTful em Endpoints HTTP

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Plataforma Guardia — APIs REST

## Lei

> **Todo endpoint HTTP da plataforma Guardia DEVE seguir as regras da especificação RESTful (status codes, payloads de resposta, headers, paginação e ordenação) definidas no Hub e referenciadas no Codex RESTful, salvo exceções justificadas e documentadas em ADR.**

## Exemplos

### Correto

Endpoint que retorna 200/201/204/400/401/404/409/422/429/500 conforme tabela de status; payload com data/errors/pagination/debug conforme estrutura padrão; headers Idempotency-Key, X-Grd-Trace-Id, etc. conforme spec; listagens paginadas com page_size, page_token, order_by, sort.

### Incorreto

Uso de status fora da lista permitida; payload de sucesso sem data ou de erro sem array errors; ausência de X-Grd-Trace-Id; listagem sem paginação quando aplicável.

## Validação Automatizada

- **Ferramenta:** revisão de contrato OpenAPI e código; testes de contrato.
- **Momento:** revisão de PR e validação de API.
- **Métrica:** 0 endpoints fora da spec, salvo exceções em ADR.
