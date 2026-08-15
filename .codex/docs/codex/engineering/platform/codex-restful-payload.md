# Codex: Payload de Resposta em APIs RESTful

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Plataforma Guardia — APIs REST — payload

## Conteúdo

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

- `errors`: array de { code, reason, message }; code conforme Tratamento de Erros; **message** orientada ao **desenvolvedor**, nunca ao usuário final (evitar expor ao UI sem tratamento).
- Em respostas 4xx/5xx, `data` e `pagination` ausentes; apenas `errors` (e `debug` se X-Grd-Debug: true).

### Debug

- Incluir **somente** quando o header de requisição `X-Grd-Debug: true`; nunca em produção por padrão.
- Objeto `debug` DEVE conter: `trace_id`, `correlation_id`, `instance`, `timestamp`, `duration`, `memory`, `query`, `params`, `internal_ip`, `external_ip`.
- NUNCA incluir dados sensíveis (segredos, PII, tokens).
- Exemplo de payload de erro com debug (quando X-Grd-Debug: true):

```json
{
  "errors": [
    {
      "code": "ERR404_NOT_FOUND",
      "reason": "RESOURCE_NOT_FOUND",
      "message": "Recurso não encontrado para o identificador informado."
    }
  ],
  "debug": {
    "trace_id": "019b9f12-3a4b-7c8d-9e0f-1a2b3c4d5e6f",
    "correlation_id": "019b9f12-0000-7000-8000-000000000001",
    "instance": "api-gateway-01",
    "timestamp": "2026-03-08T12:00:00Z",
    "duration": 15,
    "memory": 128,
    "query": "entity_id=abc",
    "params": {},
    "internal_ip": "10.0.1.5",
    "external_ip": "203.0.113.42"
  }
}
```
