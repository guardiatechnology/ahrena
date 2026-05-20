# Codex: CloudEvents na Plataforma Guardia

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Plataforma Guardia — eventos

## Visão Geral

Este Codex descreve o uso da especificação CloudEvents para representar eventos na plataforma Guardia. Cobre estrutura do evento, propriedades obrigatórias, formato, quando usar e quando não usar, e considerações de segurança. O shape dos dados em `data` segue codex-entities quando a entidade for persistente.

## Contexto

- **Domínio:** eventos em sistemas distribuídos na plataforma Guardia (publicação e consumo).
- **Público-alvo:** implementadores de publicadores e consumidores de eventos.
- **Atualização:** quando a especificação CloudEvents no Hub for alterada.

## Conteúdo

### Estrutura do evento

| Propriedade | Tipo | Padrão | Obrigatório | Descrição |
|-------------|------|--------|-------------|-----------|
| id | UUID v7 | — | Sim | Identificador único da emissão do evento. UUID v7 conforme RFC 9562. DEVE ser único por evento — a mesma entidade pode emitir vários eventos (ex.: `created`, `approved`, `executed`), cada um com `id` distinto. NÃO é igual ao `entity_id`. Imutável. |
| source | URI | — | Sim | Origem do evento. Formato: `https://api.guardia.technology/{context}/{entity_type}/{entity_id}` |
| specversion | string | 1.0 | Sim | Versão da spec CloudEvents; valor fixo "1.0". |
| type | string | — | Sim | Formato `event.{provider}.{domain}.{entity_name}.{event_name}`; todos os tokens em snake_case minúsculo; catalogado no Hub. |
| time | datetime | — | Sim | Timestamp da ocorrência (RFC 3339). |
| datacontenttype | string | application/json | Sim | Valor fixo "application/json". |
| dataschema | URI | — | Opcional | URI do schema JSON no Hub. |
| subject | string | — | Sim | Formato `{entity_type}/{entity_id}`. `entity_type` em UPPER_SNAKE_CASE. |
| idempotencykey | UUID | — | Sim | Chave de idempotência; conforme codex-idempotency. |
| data | object | — | Sim | Dados da entidade; campos comuns: entity_id, entity_type, external_entity_id, created_at, updated_at, discarded_at, version, metadata. **O histórico da entidade DEVE ser omitido dos eventos.** Ver codex-entities. |

Notas das propriedades:
- **type:** DEVE ser um tipo catalogado no catálogo de eventos do projeto (schemas).
- **dataschema:** quando presente, DEVE apontar para o schema JSON do projeto.
- **data.entity_type:** DEVE usar UPPER_SNAKE_CASE (ex.: `TRANSACTION`, `SCHEDULED_TRANSFER`), conforme `lex-entity-naming`.
- **data.entity_id:** DEVE usar o formato `{entity_id_prefix}:{uuid_v7}`.

### Formato do tipo CloudEvents

O formato canônico para eventos internos da Guardia é:

```
event.{provider}.{domain}.{entity_name}.{event_name}
```

| Token | Descrição | Exemplo |
|-------|-----------|---------|
| `provider` | Sempre `guardia` para eventos internos; nome do provedor externo para eventos externos mapeados | `guardia` |
| `domain` | Bounded context / domínio do serviço emissor | `platform`, `reconciliation`, `fiscal` |
| `entity_name` | Forma minúscula do `entity_type` em UPPER_SNAKE_CASE | `TRANSACTION` → `transaction` |
| `event_name` | Verbo no passado descrevendo o que ocorreu | `created`, `approved`, `executed`, `failed` |

O segmento `{entity_name}` é a exceção declarada à regra UPPER_SNAKE_CASE para `entity_type`: o padrão de notação dot-notation reverso do DNS do CloudEvents exige minúsculas, então `entity_name` é derivado ao converter `entity_type` para minúsculas.

### entity_id_prefix

Toda entidade tem um prefixo curto (2–5 caracteres alfanuméricos minúsculos) definido antes do início do desenvolvimento. O prefixo é combinado com um UUID v7 para formar o identificador da entidade:

```
{entity_id_prefix}:{uuid_v7}
```

Exemplos: `txn:01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f`, `rec:01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f`

O prefixo aparece onde quer que um `entity_id` seja referenciado: `data.entity_id`, `subject`, `source` e em qualquer campo de referência cruzada de entidade em `data`. O `id` do CloudEvents NÃO é um `entity_id` — é um UUID v7 novo a cada emissão de evento e não carrega prefixo.

### Exemplo de evento (JSON)

```json
{
  "id": "019b9f12-9999-7c8d-9e0f-aaaaaaaaaaaa",
  "source": "https://api.guardia.technology/platform/TRANSACTION/txn:019b9f12-3a4b-7c8d-9e0f-1a2b3c4d5e6f",
  "specversion": "1.0",
  "type": "event.guardia.platform.transaction.created",
  "time": "2026-03-08T12:00:00Z",
  "datacontenttype": "application/json",
  "dataschema": "https://<schema-base>/schemas/transaction.v1.json",
  "subject": "TRANSACTION/txn:019b9f12-3a4b-7c8d-9e0f-1a2b3c4d5e6f",
  "idempotencykey": "019b9f12-0000-7000-8000-000000000002",
  "data": {
    "entity_id": "txn:019b9f12-3a4b-7c8d-9e0f-1a2b3c4d5e6f",
    "entity_type": "TRANSACTION",
    "external_entity_id": "ext-123",
    "created_at": "2026-03-08T12:00:00Z",
    "updated_at": "2026-03-08T12:00:00Z",
    "discarded_at": null,
    "version": 1,
    "metadata": {}
  }
}
```

### Formato e serialização

- Serialização: JSON; encoding UTF-8.
- Timestamps: RFC 3339.
- Tamanho máximo do evento: inferior a 12KB.

### Comportamentos esperados

- Eventos imutáveis após publicação.
- Publicação em tópicos distintos por tipo: padrão `event.guardia.{domain}.{entity_name}.{event_name}` (todos os tokens em snake_case minúsculo).
- Consumidores DEVEM implementar idempotência.
- Ordem de entrega preservada para consistência temporal e causal.
- Eventos auto-descritivos; validação contra schema quando definido.

### Eventos externos

- Eventos externos que não seguem CloudEvents DEVEM ser mapeados para este padrão.
- Publicação em tópicos com nomenclatura `event.{provider}.{domain}.{entity_name}.{event_name}` (todos os tokens em snake_case minúsculo).

### Quando usar

- Sistemas distribuídos que trocam eventos; arquiteturas baseadas em eventos; integração entre serviços; consumo e propagação de eventos externos; mensageria assíncrona.

### Quando não usar

- Comunicação síncrona; transferência de arquivos grandes; streaming contínuo; comunicação em tempo real de baixa latência.

### Segurança

- Transmissão por canais seguros (TLS); dados sensíveis criptografados ou ofuscados; acesso controlado por autenticação e autorização (conforme spec Auth).

### Notas

- Retry para entrega; consumidores idempotentes; dead letter queue para eventos não processados.

## Referências

- codex-entities, codex-idempotency
- Cloud Events Specification; RFC 3339; RFC 9562
