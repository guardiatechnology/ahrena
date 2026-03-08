# Lexis: Eventos CloudEvents en la Plataforma Guardia

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Plataforma Guardia — sistemas distribuidos y eventos

## Propósito

Garantizar interoperabilidad, rastreabilidad y consistencia en la comunicación basada en eventos. Los eventos que no sigan el estándar CloudEvents con propiedades obligatorias e idempotencykey rompen la deduplicación e integración entre servicios.

## Ley

> **Los eventos publicados o consumidos por la plataforma Guardia en sistemas distribuidos DEBEN seguir la especificación CloudEvents (estructura, propiedades obligatorias, idempotencykey, serialización JSON, tamaño inferior a 12KB); los eventos externos que no sigan el estándar DEBEN ser mapeados a este formato antes de ser publicados o procesados.**

## Alcance

- **Se aplica a:** publicación y consumo de eventos en arquitecturas basadas en eventos en la plataforma Guardia; integración con eventos externos.
- **Agentes vinculados:** publicadores y consumidores de eventos.
- **Excepciones:** Ninguna para eventos que representen ocurrencias significativas en el sistema; comunicación síncrona, transferencia de archivos grandes y streaming continuo no están comprendidos.

## Consecuencias de Violación

1. **Interoperabilidad:** los consumidores no pueden validar ni deduplicar eventos.
2. **Rastreabilidad:** ausencia de metadatos esenciales compromete la auditoría.
3. **Remediación:** mapear eventos a CloudEvents o publicar en tópicos compatibles.

## Ejemplos

### Correcto

Evento con id, source, specversion, type, time, idempotencykey, subject, data; type en formato event.guardia.{module}.{entity_type}.{event_name}; data con campos de entidad conforme codex-entities; serialización JSON UTF-8; tamaño < 12KB.

### Incorrecto

Evento sin idempotencykey; sin type catalogado; data sin entity_id/entity_type cuando sea entidad; tamaño superior a 12KB; formato distinto de JSON.

## Validación Automatizada

- **Herramienta:** validación contra schema CloudEvents; revisión de publicadores y consumidores.
- **Momento:** revisión de PR y pruebas de integración de eventos.
- **Métrica:** 0 eventos publicados fuera del estándar CloudEvents cuando la spec aplique.

## Referencias

- [Especificación CloudEvents — Hub Guardia](https://hub.guardia.finance/docs/specifications/cloud-events/)
- codex-cloudevents, codex-entities, codex-idempotency
- CloudEvents Specification; RFC 3339
