# Codex: Erros Conhecidos da Plataforma Guardia

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Plataforma Guardia — catálogo de erros padronizados

## Conteúdo

### Estrutura do catálogo

Cada entrada do catálogo segue o padrão:

- **`reason`** — string em UPPER_SNAKE_CASE, único por `code`.
- **Mensagem** — descrição orientada ao desenvolvedor (não exposta ao usuário final).
- **Retry** — elegibilidade de retentativa (✅ após correção, ❌ não retentar, ⏳ com backoff).
- **Tratamento sugerido** — passos para o cliente resolver o erro.

### ERR400_MISSING_OR_MALFORMED_HEADER

Header obrigatório ausente ou malformado.

| reason | Retry | Mensagem | Tratamento sugerido |
|--------|:-----:|----------|---------------------|
| `IDEMPOTENCY_KEY_REQUIRED` | ✅ após correção | O recurso solicitado exige `Idempotency-Key` válido. | Enviar header `Idempotency-Key` formatado conforme [codex-idempotency](codex-idempotency.md). |
| `MALFORMED_CORRELATION_ID` | ✅ após correção | O header `X-Grd-Correlation-Id` não está corretamente formatado. | Enviar UUID válido conforme [codex-restful-headers](codex-restful-headers.md). |
| `INVALID_DEBUG_HEADER_VALUE` | ✅ após correção | O header `X-Grd-Debug` aceita apenas `true` ou `false`. | Corrigir valor do header `X-Grd-Debug`. |
| `INVALID_CONTENT_DIGEST` | ✅ após correção | O header `Content-Digest` é inválido ou divergente do payload. | Recalcular SHA-256 sobre o JSON normalizado conforme [codex-restful-headers](codex-restful-headers.md). |

### ERR400_INVALID_PAYLOAD

Body da requisição com formato ou estrutura inválida. Códigos específicos serão adicionados conforme novos endpoints registrarem `reason`.

### ERR400_INVALID_PARAMETER

Parâmetros (path, query) com formato ou valor inválido.

| reason | Retry | Mensagem | Tratamento sugerido |
|--------|:-----:|----------|---------------------|
| `INVALID_LEDGER_NAME_LENGTH` | ✅ após correção | Nome do ledger fora dos limites permitidos. | Ajustar tamanho do nome conforme contrato do endpoint. |
| `INVALID_LEDGER_DESCRIPTION_LENGTH` | ✅ após correção | Descrição do ledger excede o limite. | Reduzir o tamanho da descrição. |
| `INVALID_PARAMETER_FORMAT` | ✅ após correção | Formato do body ou parâmetros é inválido. | Verificar contrato (OAS) e corrigir a requisição. |
| `INVALID_METADATA_FORMAT` | ✅ após correção | Metadados inválidos. | Garantir JSON válido e estrutura prevista em [codex-entities](codex-entities.md). |
| `INVALID_METADATA_LENGTH` | ✅ após correção | Metadados excedem o limite (10KB). | Reduzir o tamanho dos metadados. |
| `INVALID_EXTERNAL_ENTITY_ID_FORMAT` | ✅ após correção | `external_entity_id` em formato inválido. | Ajustar conforme [codex-entities](codex-entities.md) (máx. 36 caracteres). |
| `PAGE_TOKEN_INVALID` | ✅ após correção | `page_token` inválido. | Usar token retornado em resposta anterior; ver [codex-restful-pagination](codex-restful-pagination.md). |
| `PAGE_TOKEN_EXPIRED` | ✅ após correção | `page_token` expirado. | Reiniciar paginação a partir do `first_page_token` ou da primeira página. |
| `PAGE_SIZE_INVALID` | ✅ após correção | `page_size` inválido. | Enviar inteiro positivo conforme contrato. |
| `PAGE_SIZE_TOO_LARGE` | ✅ após correção | `page_size` acima do limite (100). | Reduzir `page_size` para o limite máximo. |
| `ORDER_BY_INVALID` | ✅ após correção | `order_by` inválido. | Usar `created_at`, `updated_at` ou `reference_at`. |
| `SORT_INVALID` | ✅ após correção | `sort` inválido. | Usar `asc` ou `desc` (case insensitive). |

### ERR401_UNAUTHORIZED

Autenticação ausente ou inválida. Reservado a falhas de OAuth 2.0/JWT. Mensagens NUNCA DEVEM indicar se um usuário existe.

### ERR402_INSUFFICIENT_FUNDS

| reason | Retry | Mensagem | Tratamento sugerido |
|--------|:-----:|----------|---------------------|
| `PAYMENT_IS_REQUIRED` | ❌ | Saldo insuficiente para a operação solicitada. | Regularizar saldo/pagamento antes de retentar. |

### ERR403_FORBIDDEN

Cliente autenticado, sem autorização para o recurso. `reason` específicos por escopo serão registrados conforme necessidade.

### ERR404_NOT_FOUND

| reason | Retry | Mensagem | Tratamento sugerido |
|--------|:-----:|----------|---------------------|
| `LEDGER_NOT_FOUND` | ⏳ se o ledger for criado | Ledger especificado não foi encontrado. | Conferir `entity_id` ou criar o ledger. |

### ERR405_INVALID_OPERATION

Operação não permitida no estado atual do recurso. `reason` específicos serão registrados por domínio.

### ERR408_REQUEST_TIMEOUT

Cliente não completou a requisição dentro do tempo limite. Geralmente retentável após estabilização de rede.

### ERR409_SERVER_STATE_CONFLICT

Conflito com o estado atual do recurso.

| reason | Retry | Mensagem | Tratamento sugerido |
|--------|:-----:|----------|---------------------|
| `CONFLICTING_IDEMPOTENT_REQUEST` | ✅ após correção | Mesma `Idempotency-Key` com payload diferente da execução anterior. | Usar nova chave para nova operação OU reenviar payload original. |
| `EXTERNAL_ENTITY_ID_ALREADY_IN_USE` | ✅ após correção | `external_entity_id` já em uso por outro recurso. | Escolher outro identificador externo. |
| `LEDGER_NAME_ALREADY_IN_USE` | ✅ após correção | Nome do ledger já em uso. | Escolher outro nome. |

### ERR422_BUSINESS_ERROR

Dados sintaticamente válidos, mas com erro semântico/regra de negócio. `reason` específicos por domínio.

### ERR429_RATE_LIMITED

Cliente excedeu o limite de requisições. Resposta DEVE incluir header `Retry-After`.

### ERR500_INTERNAL_ERROR

Falha interna inesperada. Cliente NÃO DEVE retentar imediatamente; aplicar backoff exponencial e circuit breaker conforme [codex-error-handling](codex-error-handling.md).

### ERR501_FEATURE_NOT_IMPLEMENTED

Funcionalidade não implementada. NÃO retentar.

### ERR503_SERVICE_UNAVAILABLE

Serviço temporariamente indisponível. Retentar com backoff respeitando `Retry-After` quando presente.

### ERR504_GATEWAY_TIMEOUT

Timeout entre serviços upstream. Retentar com backoff.

### Criação de novos `reason`

Ao adicionar um novo `reason` ao catálogo:

1. Confirmar que o `code` HTTP correto já existe nesta lista; se não, abrir nova seção `ERR{HTTP}_*`.
2. Garantir UPPER_SNAKE_CASE e singularidade dentro do `code`.
3. Documentar mensagem (sem dados sensíveis), elegibilidade de retry e tratamento sugerido.
4. Registrar o erro também no contrato OAS do endpoint que o emite.
5. Atualizar este Codex e a página **Known Errors** no Notion.
