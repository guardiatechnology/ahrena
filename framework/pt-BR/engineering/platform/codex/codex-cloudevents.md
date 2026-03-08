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
| id | UUID v7 | — | Sim | Identificador único do evento; imutável; RFC 9562. |
| source | URI | — | Sim | Origem do evento (ex.: https://&lt;tenant_id&gt;.guardia.finance/&lt;module&gt;/api/v1/&lt;entity_type&gt;/&lt;entity_id&gt;) |
| specversion | string | 1.0 | Sim | Versão da spec CloudEvents; valor fixo "1.0". |
| type | string | — | Sim | Formato event.{provider}.{module}.{entity_type}.{event_name}; catalogado no Hub. |
| time | datetime | — | Sim | Timestamp da ocorrência (RFC 3339). |
| datacontenttype | string | application/json | Sim | Valor fixo "application/json". |
| dataschema | URI | — | Opcional | URI do schema JSON no Hub. |
| subject | string | — | Sim | Formato {entity_type}/{entity_id}. |
| idempotencykey | UUID | — | Sim | Chave de idempotência; conforme codex-idempotency. |
| data | object | — | Sim | Dados da entidade; campos comuns: entity_id, entity_type, external_entity_id, created_at, updated_at, discarded_at, version, metadata; history omitido. Ver codex-entities. |

### Formato e serialização

- Serialização: JSON; encoding UTF-8.
- Timestamps: RFC 3339.
- Tamanho máximo do evento: inferior a 12KB.

### Comportamentos esperados

- Eventos imutáveis após publicação.
- Publicação em tópicos distintos por tipo: padrão event.guardia.{module}.{entity_type}.{event_name}.
- Consumidores DEVEM implementar idempotência.
- Ordem de entrega preservada para consistência temporal e causal.
- Eventos auto-descritivos; validação contra schema quando definido.

### Eventos externos

- Eventos externos que não seguem CloudEvents DEVEM ser mapeados para este padrão.
- Publicação em tópicos com nomenclatura event.{provider}.{module}.{entity_type}.{event_name}.

### Quando usar

- Sistemas distribuídos que trocam eventos; arquiteturas baseadas em eventos; integração entre serviços; consumo e propagação de eventos externos; mensageria assíncrona.

### Quando não usar

- Comunicação síncrona; transferência de arquivos grandes; streaming contínuo; comunicação em tempo real de baixa latência.

### Segurança

- Transmissão por canais seguros (TLS); dados sensíveis criptografados ou ofuscados; acesso controlado por autenticação e autorização (conforme spec Auth).

### Notas

- Retry para entrega; consumidores idempotentes; dead letter queue para eventos não processados.

## Referências

- [CloudEvents — Hub Guardia](https://hub.guardia.finance/docs/specifications/cloud-events/)
- codex-entities, codex-idempotency
- Cloud Events Specification; RFC 3339
