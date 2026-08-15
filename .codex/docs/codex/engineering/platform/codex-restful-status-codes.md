# Codex: Status Codes HTTP em APIs RESTful

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Plataforma Guardia — APIs REST — status codes

## Conteúdo

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
