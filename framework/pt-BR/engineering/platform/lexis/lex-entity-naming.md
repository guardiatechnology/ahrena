# Lexis: Convenções de Nomenclatura de Entidades — snake_case

> **Prefixo:** `lex-` | **Tipo:** Lei Inviolável | **Escopo:** Plataforma Guardia — identificadores de entidade, nomes de campo, segmentos do tipo CloudEvents e nomes de colunas de banco de dados

## Propósito

Inconsistências de nomenclatura entre modelo de domínio, APIs, eventos e banco de dados são uma fonte persistente de bugs de integração, confusão em code review e quebra de interoperabilidade entre serviços. Impor uma única convenção de casing em todos os limites do sistema elimina toda uma classe de erros de mapeamento.

## Lei

> **Todo valor de `entity_type`, nome de campo JSON, nome de coluna de banco de dados e segmento variável no formato de tipo CloudEvents (`{module}`, `{entity_type}`, `{event_name}`) DEVE usar snake_case. Em documentos de modelo de domínio (artefatos DDD), nomes de agregados e entidades usados como identificadores conceituais DEVEM usar PascalCase. Usar camelCase, PascalCase ou kebab-case para valores de `entity_type`, nomes de propriedades JSON ou segmentos do tipo CloudEvents é PROIBIDO.**

## Regras

### 1. Valores de entity_type

`entity_type` é um identificador de string para a classe da entidade. DEVE:
- Usar snake_case: `scheduled_transfer`, `ledger_entry`, `reconciliation_run`
- Ser no singular (não plural): `scheduled_transfer`, não `scheduled_transfers`
- Ser estável: alterar `entity_type` é uma mudança breaking e requer ADR

### 2. Nomes de campos JSON (APIs e eventos)

Todos os nomes de campos em corpos de requisição JSON, payloads de resposta e objetos `data` de CloudEvents DEVEM usar snake_case:
- Correto: `entity_id`, `created_at`, `idempotency_key`, `scheduled_date`, `failure_reason`
- Incorreto: `entityId`, `createdAt`, `idempotencyKey`, `scheduledDate`, `failureReason`

### 3. Segmentos do tipo CloudEvents

O formato de tipo CloudEvents `event.guardia.{module}.{entity_type}.{event_name}` exige todos os segmentos variáveis em snake_case:
- `{module}`: `platform`, `reconciliation`, `fiscal`
- `{entity_type}`: `scheduled_transfer`, `ledger_entry`
- `{event_name}`: `created`, `approved`, `executed`, `failed`, `cancelled`
- Exemplo completo: `event.guardia.platform.scheduled_transfer.approved`

### 4. Nomes de colunas de banco de dados

Nomes de colunas de banco de dados DEVEM usar snake_case:
- Correto: `entity_id`, `entity_type`, `created_at`, `scheduled_date`
- Incorreto: `entityId`, `EntityType`, `created-at`

### 5. Documentos de modelo de domínio — exceção para PascalCase

Em artefatos DDD (documentos de modelo de domínio, diagramas de bounded context, definições de agregados), **nomes de agregados e entidades usados como identificadores conceituais** DEVEM usar PascalCase. Esta é a única exceção ao snake_case:
- Agregado em documento DDD: `ScheduledTransfer`, `LedgerEntry`, `ReconciliationRun`
- A mesma entidade em APIs e eventos: `entity_type: "scheduled_transfer"`, `event.guardia.platform.scheduled_transfer.created`

PascalCase em documentos DDD reflete a linguagem do domínio; snake_case nos limites do sistema impõe consistência técnica.

### 6. Segmentos de path de URL — kebab-case (não é nomenclatura de entidade)

Segmentos de path de URL de recursos da API seguem kebab-case (`/v1/scheduled-transfers`) conforme convenções RESTful (`lex-restful-apis`). Isso é roteamento de API, não nomenclatura de entidade — `entity_type` no payload permanece em snake_case mesmo quando a URL usa kebab-case.

## Escopo

- **Aplica-se a:** modelagem de entidades, contratos de API (OpenAPI/JSON), payloads de CloudEvents, schemas de banco de dados, documentos de modelo de domínio, documentação de eventos.
- **Agentes vinculados:** todos os agentes que criam ou revisam entidades, APIs, eventos ou modelos de domínio (warrior-theseus, warrior-daedalus, warrior-kronos, warrior-apollo, warrior-hera).
- **Exceções:** nomes de campos de integrações de terceiros que chegam em camelCase de sistemas externos — mapear na camada anti-corruption layer; não propagar camelCase internamente.

## Exemplos

### Correto

```json
{
  "entity_id": "01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f",
  "entity_type": "scheduled_transfer",
  "scheduled_date": "2026-04-30",
  "failure_reason": null,
  "created_at": "2026-04-26T10:00:00Z",
  "updated_at": "2026-04-26T10:00:00Z",
  "version": 1
}
```

Tipo CloudEvents: `event.guardia.platform.scheduled_transfer.approved`

Agregado no documento de modelo de domínio: `ScheduledTransfer`

### Incorreto

```json
{
  "entityId": "01957f3e-...",
  "entityType": "ScheduledTransfer",
  "scheduledDate": "2026-04-30",
  "failureReason": null,
  "createdAt": "2026-04-26T10:00:00Z"
}
```

Tipo CloudEvents (inválido): `event.guardia.platform.scheduledTransfer.Approved`

## Validação Automatizada

- **Ferramenta:** JSON Schema / linter OpenAPI com padrão de nome de propriedade `^[a-z][a-z0-9_]*$`; regex de tipo CloudEvents `^event\.guardia\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$`; linter de migration de banco de dados (squawk) verificando casing de nomes de coluna.
- **Quando:** pre-commit, CI (validação OpenAPI), PR review para documentos de modelo de domínio.
- **Métrica:** 0 nomes de campo em camelCase ou PascalCase em schemas JSON; 0 tipos CloudEvents com segmentos fora de snake_case; 0 colunas de banco de dados fora de snake_case.

## Referências

- `lex-entities` — estrutura base de entidades (entity_id, entity_type, version, timestamps)
- `lex-cloudevents` — formato e estrutura do tipo CloudEvents
- `lex-restful-apis` — convenções de URL de API (kebab-case para segmentos de path)
- `codex-entities` — referência do modelo de entidades
