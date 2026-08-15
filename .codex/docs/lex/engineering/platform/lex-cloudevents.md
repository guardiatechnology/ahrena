# Lexis: Eventos CloudEvents na Plataforma Guardia

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Plataforma Guardia — sistemas distribuídos e eventos

## Lei

> **Eventos publicados ou consumidos pela plataforma Guardia em sistemas distribuídos DEVEM seguir a especificação CloudEvents (estrutura, propriedades obrigatórias, idempotencykey, serialização JSON, tamanho inferior a 12KB); eventos externos que não seguem o padrão DEVEM ser mapeados para esse formato antes de serem publicados ou processados.**

## Exemplos

### Correto

Evento com id, source, specversion, type, time, idempotencykey, subject, data; type no formato event.guardia.{module}.{entity_type}.{event_name}; data com campos de entidade conforme codex-entities; serialização JSON UTF-8; tamanho < 12KB.

### Incorreto

Evento sem idempotencykey; sem type catalogado; data sem entity_id/entity_type quando for entidade; tamanho superior a 12KB; formato diferente de JSON.

## Validação Automatizada

- **Ferramenta:** validação contra schema CloudEvents; revisão de publicadores e consumidores; `kata-events-review` invocado pelo `warrior-argos` durante revisão multi-eixo de Pull Request (captura violações de formato de type, ausência de `idempotencykey`, divergências de payload contra o catálogo da entidade, breaking changes contra a versão base).
- **Momento:** revisão de PR (via `cry-review-pr` → `warrior-argos` → `kata-events-review`) e testes de integração de eventos.
- **Métrica:** 0 eventos publicados fora do padrão CloudEvents quando a spec se aplicar.
