# Codex: APIs RESTful da Plataforma Guardia

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Plataforma Guardia — APIs REST

## Visão Geral

Este Codex consolida as diretrizes para construção, consumo e documentação de APIs RESTful na plataforma Guardia. As regras estão organizadas em módulos específicos; cada um possui seu próprio artefato para consulta detalhada. Exceções à spec devem ser documentadas em ADR.

## Contexto

- **Domínio:** APIs HTTP da plataforma Guardia (respostas, headers, paginação, ordenação).
- **Público-alvo:** implementadores e consumidores de APIs.
- **Atualização:** quando as especificações RESTful no Hub forem alteradas.

## Módulos

| Módulo | Artefato | Conteúdo |
|--------|----------|----------|
| Status Codes | [codex-restful-status-codes](codex-restful-status-codes.md) | Códigos HTTP permitidos (2xx, 3xx, 4xx, 5xx) e quando usar/não usar |
| Payload de Resposta | [codex-restful-payload](codex-restful-payload.md) | Estrutura data, pagination, errors, debug |
| Headers | [codex-restful-headers](codex-restful-headers.md) | Headers padrão e customizados (X-Grd-*), Content-Digest, Idempotency-Key |
| Paginação | [codex-restful-pagination](codex-restful-pagination.md) | Parâmetros, resposta, tokens, erros conhecidos |
| Ordenação | [codex-restful-sorting](codex-restful-sorting.md) | order_by, sort, índices, partitionamento |

## Referências gerais

- codex-entities, codex-idempotency, codex-error-handling
- RFC 9110 (HTTP Semantics), RFC 9111 (Caching), RFC 7232 (Conditional Requests), RFC 7807 (Problem Details)
