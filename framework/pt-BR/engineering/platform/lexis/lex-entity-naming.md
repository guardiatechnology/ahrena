# Lexis: Convenções de Nomenclatura de Entidades e Identificadores

> **Prefixo:** `lex-` | **Tipo:** Lei Inviolável | **Escopo:** Plataforma Guardia — tipos de entidade, identificadores, nomes de campo, segmentos do tipo CloudEvents e nomes de colunas de banco de dados

## Propósito

Inconsistências de nomenclatura entre modelo de domínio, APIs, eventos e bancos de dados são uma fonte persistente de bugs de integração, confusão em code review e quebra de interoperabilidade entre serviços. Impor convenções canônicas em todos os limites do sistema elimina toda uma classe de erros de mapeamento.

## Lei

> **Todo valor de `entity_type` DEVE usar UPPER_SNAKE_CASE (ex.: `TRANSACTION`, `SCHEDULED_TRANSFER`). Todo nome de campo JSON e nome de coluna de banco de dados DEVE usar snake_case. Todo `entity_id` DEVE ser formatado como `{entity_id_prefix}:{uuid_v7}`, onde o prefixo é uma string alfanumérica minúscula de 2 a 5 caracteres definida antes do início do desenvolvimento. Campos de identificador de entidade em payloads JSON externos DEVEM seguir a convenção `{entity_name}_id` — o sufixo `_entity_id` é PROIBIDO. Em segmentos do tipo CloudEvents, `{entity_name}` DEVE ser a forma minúscula do `entity_type` em UPPER_SNAKE_CASE. Usar camelCase ou PascalCase para valores de `entity_type`, nomes de propriedades JSON ou segmentos do tipo CloudEvents é PROIBIDO.**

## Regras

### 1. Valores de entity_type — UPPER_SNAKE_CASE

`entity_type` é o discriminador canônico para a classe da entidade. DEVE:
- Usar UPPER_SNAKE_CASE: `TRANSACTION`, `SCHEDULED_TRANSFER`, `LEDGER_ENTRY`
- Ser no singular (não plural): `TRANSACTION`, não `TRANSACTIONS`
- Ser estável: alterar `entity_type` é uma mudança breaking e requer ADR

Os únicos contextos onde `entity_type` aparece em minúsculas são:
- Segmentos de path de URL (ex.: `/v1/scheduled-transfers` em kebab-case conforme `lex-restful-apis`)
- O segmento `{entity_name}` do campo `type` do CloudEvents (ex.: `SCHEDULED_TRANSFER` → `scheduled_transfer`), como exceção declarada justificada pelo padrão de notação dot-notation reverso do DNS do CloudEvents

### 2. Formato de entity_id — {entity_id_prefix}:{uuid_v7}

Todo identificador de entidade DEVE ser formatado como:

```
{entity_id_prefix}:{uuid_v7}
```

- `entity_id_prefix`: 2 a 5 caracteres alfanuméricos minúsculos definidos antes do início do desenvolvimento (ex.: `txn`, `rec`, `org`, `per`, `doc`)
- `uuid_v7`: UUID v7 conforme a [RFC 9562](https://datatracker.ietf.org/doc/html/rfc9562), assegurando ordenação temporal
- Exemplo: `txn:01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f`

O prefixo DEVE ser declarado no documento de design da entidade antes do início da codificação. Alterar um prefixo é uma mudança breaking que requer ADR.

### 3. Nomenclatura de campo de identificador — {entity_name}_id

Ao referenciar uma entidade pelo seu identificador em um payload JSON de outra entidade:
- O campo DEVE ser nomeado `{entity_name}_id`, onde `{entity_name}` é a forma minúscula do `entity_type`
- Correto: `transaction_id`, `ledger_entry_id`, `scheduled_transfer_id`
- O sufixo `_entity_id` é PROIBIDO: nunca usar `transaction_entity_id`, `ledger_entry_entity_id`

Exceção: dentro do próprio payload da entidade, o campo de identificador canônico é sempre `entity_id`.

### 4. Nomes de campos JSON — snake_case

Todos os nomes de campos em corpos de requisição JSON, payloads de resposta e objetos `data` de CloudEvents DEVEM usar snake_case:
- Correto: `entity_id`, `created_at`, `idempotency_key`, `scheduled_date`, `failure_reason`
- Incorreto: `entityId`, `createdAt`, `idempotencyKey`, `scheduledDate`, `failureReason`

### 5. Segmentos do tipo CloudEvents — minúsculas

O formato de tipo CloudEvents `event.{provider}.{domain}.{entity_name}.{event_name}` exige todos os segmentos variáveis em snake_case minúsculo:
- `{provider}`: `guardia` para eventos internos; nome do provedor externo para eventos externos mapeados
- `{domain}`: `platform`, `reconciliation`, `fiscal`
- `{entity_name}`: forma minúscula do `entity_type` em UPPER_SNAKE_CASE (ex.: `SCHEDULED_TRANSFER` → `scheduled_transfer`)
- `{event_name}`: `created`, `approved`, `executed`, `failed`, `cancelled`
- Exemplo completo: `event.guardia.financial.scheduled_transfer.approved`

### 6. Nomes de colunas de banco de dados — snake_case

Nomes de colunas de banco de dados DEVEM usar snake_case:
- Correto: `entity_id`, `entity_type`, `created_at`, `scheduled_date`
- Incorreto: `entityId`, `EntityType`, `created-at`

### 7. Documentos de modelo de domínio — exceção para PascalCase

Em artefatos DDD (documentos de modelo de domínio, diagramas de bounded context, definições de agregados), **nomes de agregados e entidades usados como identificadores conceituais** DEVEM usar PascalCase. Esta é a única exceção:
- Agregado em documento DDD: `ScheduledTransfer`, `LedgerEntry`, `Transaction`
- A mesma entidade nos limites do sistema: `entity_type: "SCHEDULED_TRANSFER"`, `event.guardia.financial.scheduled_transfer.created`

PascalCase em documentos DDD reflete a linguagem do domínio; UPPER_SNAKE_CASE nos limites do sistema impõe consistência técnica.

### 8. Segmentos de path de URL — plural kebab-case

Segmentos de path de URL de recursos da API seguem **plural em kebab-case** conforme convenções RESTful (`lex-restful-apis`). A forma plural é derivada do `entity_type` singular em UPPER_SNAKE_CASE:

| `entity_type` (dado) | Segmento de recurso na URL |
|----------------------|----------------------------|
| `TRANSACTION` | `transactions` |
| `RECORD` | `records` |
| `SCHEDULED_TRANSFER` | `scheduled-transfers` |
| `LEDGER_ENTRY` | `ledger-entries` |

Exemplo de path completo: `/v1/scheduled-transfers/txn:01957f3e-...`. O valor de `entity_type` no payload JSON permanece UPPER_SNAKE_CASE singular (`SCHEDULED_TRANSFER`) independentemente da forma da URL. URIs de `source` de CloudEvents seguem a mesma convenção — ver `codex-cloudevents`.

## Escopo

- **Aplica-se a:** modelagem de entidades, contratos de API (OpenAPI/JSON), payloads de CloudEvents, schemas de banco de dados, documentos de modelo de domínio, documentação de eventos.
- **Agentes vinculados:** todos os agentes que criam ou revisam entidades, APIs, eventos ou modelos de domínio (warrior-theseus, warrior-daedalus, warrior-kronos, warrior-apollo, warrior-hera).
- **Exceções:** nomes de campos de integrações de terceiros que chegam em camelCase de sistemas externos — mapear na camada anti-corruption layer; não propagar camelCase internamente.

## Exemplos

### Correto

```json
{
  "entity_id": "txn:01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f",
  "entity_type": "SCHEDULED_TRANSFER",
  "scheduled_date": "2026-04-30",
  "failure_reason": null,
  "created_at": "2026-04-26T10:00:00Z",
  "updated_at": "2026-04-26T10:00:00Z",
  "version": 1
}
```

Tipo CloudEvents: `event.guardia.financial.scheduled_transfer.approved`

Subject CloudEvents: `SCHEDULED_TRANSFER/txn:01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f`

Agregado no documento de modelo de domínio: `ScheduledTransfer`

Referência cruzada de entidade: `"transaction_id": "txn:01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f"`

### Incorreto

```json
{
  "entityId": "01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f",
  "entityType": "ScheduledTransfer",
  "transaction_entity_id": "txn:...",
  "scheduledDate": "2026-04-30",
  "createdAt": "2026-04-26T10:00:00Z"
}
```

Tipo CloudEvents (inválido): `event.guardia.financial.ScheduledTransfer.Approved`

## Validação Automatizada

- **Ferramenta:** JSON Schema / linter OpenAPI com padrão `entity_type` `^[A-Z][A-Z0-9_]*$`; padrão de nome de campo JSON `^[a-z][a-z0-9_]*$`; regex de tipo CloudEvents `^event\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$`; padrão de entity_id `^[a-z0-9]{2,5}:[0-9a-f-]{36}$`; regra de lint bloqueando o sufixo `_entity_id`; linter de migration de banco de dados (squawk) verificando casing de nomes de coluna.
- **Quando:** pre-commit, CI (validação OpenAPI), PR review para documentos de modelo de domínio.
- **Métrica:** 0 valores de `entity_type` em minúsculas em payloads JSON; 0 sufixos `_entity_id` em nomes de campo; 0 valores de entity_id sem prefixo; 0 nomes de campo em camelCase em schemas JSON; 0 tipos CloudEvents com segmentos não minúsculos; 0 colunas de banco de dados fora de snake_case.

## Referências

- `lex-entities` — estrutura base de entidades (entity_id, entity_type, version, timestamps)
- `lex-cloudevents` — formato e estrutura do tipo CloudEvents
- `lex-restful-apis` — convenções de URL de API (kebab-case para segmentos de path)
- `codex-entities` — referência do modelo de entidades
