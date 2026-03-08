# Lexis: Eventos CloudEvents na Plataforma Guardia

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Plataforma Guardia — sistemas distribuídos e eventos

## Propósito

Garantir interoperabilidade, rastreabilidade e consistência na comunicação baseada em eventos. Eventos que não sigam o padrão CloudEvents com propriedades obrigatórias e idempotencykey quebram deduplicação e integração entre serviços.

## Lei

> **Eventos publicados ou consumidos pela plataforma Guardia em sistemas distribuídos DEVEM seguir a especificação CloudEvents (estrutura, propriedades obrigatórias, idempotencykey, serialização JSON, tamanho inferior a 12KB); eventos externos que não seguem o padrão DEVEM ser mapeados para esse formato antes de serem publicados ou processados.**

## Abrangência

- **Aplica-se a:** publicação e consumo de eventos em arquiteturas baseadas em eventos na plataforma Guardia; integração com eventos externos.
- **Agentes vinculados:** publicadores e consumidores de eventos.
- **Exceções:** Nenhuma para eventos que representem ocorrências significativas no sistema; comunicação síncrona, transferência de arquivos grandes e streaming contínuo não são abrangidos.

## Consequências de Violação

1. **Interoperabilidade:** consumidores não conseguem validar ou deduplicar eventos.
2. **Rastreabilidade:** ausência de metadados essenciais compromete auditoria.
3. **Remediação:** mapear eventos para CloudEvents ou publicar em tópicos compatíveis.

## Exemplos

### Correto

Evento com id, source, specversion, type, time, idempotencykey, subject, data; type no formato event.guardia.{module}.{entity_type}.{event_name}; data com campos de entidade conforme codex-entities; serialização JSON UTF-8; tamanho < 12KB.

### Incorreto

Evento sem idempotencykey; sem type catalogado; data sem entity_id/entity_type quando for entidade; tamanho superior a 12KB; formato diferente de JSON.

## Validação Automatizada

- **Ferramenta:** validação contra schema CloudEvents; revisão de publicadores e consumidores.
- **Momento:** revisão de PR e testes de integração de eventos.
- **Métrica:** 0 eventos publicados fora do padrão CloudEvents quando a spec se aplicar.

## Referências

- [Especificação CloudEvents — Hub Guardia](https://hub.guardia.finance/docs/specifications/cloud-events/)
- codex-cloudevents, codex-entities, codex-idempotency
- CloudEvents Specification; RFC 3339
