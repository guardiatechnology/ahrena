# Codex: Paginação em APIs RESTful

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Plataforma Guardia — APIs REST — paginação

## Visão Geral

Parâmetros, estrutura de resposta e comportamentos para listagens paginadas na plataforma Guardia. Tokens opacos, ordenação estável e erros padronizados.

## Contexto

- **Domínio:** paginação de recursos em APIs HTTP da plataforma Guardia.
- **Público-alvo:** implementadores e consumidores de APIs.
- **Atualização:** quando a especificação de paginação no Hub for alterada.

## Conteúdo

### Requisição

| Parâmetro | Tipo | Default | Máximo | Regra |
|----------|------|---------|--------|-------|
| page_size | uint32 | 20 | 100 | Rejeitar acima do limite com 400 ERR400_INVALID_PARAMETER (PAGE_SIZE_TOO_LARGE, etc.) |
| page_token | string | — | — | Token opaco; retornado em chamadas anteriores |
| order_by | string | created_at | — | created_at, updated_at, reference_at; outro valor → 400 ORDER_BY_INVALID |
| sort | string | asc | — | asc, desc (case insensitive); outro → 400 SORT_INVALID |

### Resposta

- `data`: array da página atual.
- `pagination`: page_size, total_count, first_page_token, previous_page_token, next_page_token, last_page_token (todos presentes; nulos quando não aplicável). **total_count** PODE ser omitido quando o custo de cálculo for proibitivo (ex.: contagem exata em bases muito grandes); quando omitido, documentar no contrato.
- Headers: Cache-Control (ex.: max-age=900), Link com rel first, previous, next, last.
- **Compliance by Design:** tokens opacos e expiração limitada; logs de acesso com X-Grd-Trace-Id; sem vazamento de dados entre tenants; parâmetros validados e rejeitados com code/reason padronizados.

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

Exemplo de resposta de erro (page_token inválido):

```json
{
  "errors": [
    {
      "code": "ERR400_INVALID_PARAMETER",
      "reason": "PAGE_TOKEN_INVALID",
      "message": "O token de paginação informado é inválido ou expirado."
    }
  ]
}
```

## Referências

- HATEOAS
- [codex-restful-apis](codex-restful-apis.md) (índice); [codex-restful-sorting](codex-restful-sorting.md)
