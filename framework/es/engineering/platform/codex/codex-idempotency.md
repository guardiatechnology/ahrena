# Codex: Idempotencia en APIs y Eventos de la Plataforma Guardia

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Plataforma Guardia — idempotencia

## Visión General

Este Codex describe las reglas de idempotencia para operaciones que modifican estado en la plataforma Guardia (APIs y eventos). Objetiva consistencia de datos, confiabilidad en retries y deduplicación, en conformidad con la especificación de Idempotencia del Hub.

## Contexto

- **Dominio:** idempotencia en APIs REST y en eventos (publicación y consumo).
- **Público objetivo:** implementadores de APIs y procesadores de eventos.
- **Actualización:** cuando la especificación de Idempotencia en el Hub sea alterada.

## Contenido

### Principios fundamentales

1. **Mismo resultado:** las operaciones idempotentes DEBEN producir el mismo resultado para múltiples ejecuciones con los mismos parámetros.
2. **Clave + hash:** la verificación NO DEBE depender solo de la clave; DEBE considerar la combinación de la clave y el hash del payload (petición o evento). Algoritmo del hash: SHA-256.
3. **Clave proporcionada por el cliente:** la clave de idempotencia DEBE ser proporcionada por el cliente; DEBE ser única por operación y alcance de ruta; DEBE ser UUID (RFC 9562).
4. **Almacenamiento:** el estado de idempotencia DEBE almacenarse en caché distribuido y resiliente; retención mínima 2 horas, máxima 24 horas.
5. **Seguridad y auditoría:** estado almacenado de forma segura, acceso auditable; intentos maliciosos de repetición monitoreados y mitigados; logs con identificadores rastreables.

### Implementación en APIs

- Los endpoints que modifican estado (POST, PATCH) DEBEN ser idempotentes.
- El header `Idempotency-Key` DEBE ser obligatorio en esos endpoints.
- Cuando no se informe: retornar `400 BAD REQUEST`, código `ERR400_MISSING_OR_MALFORMED_HEADER`, motivo `IDEMPOTENCY_KEY_REQUIRED`.
- La respuesta DEBE incluir el mismo header `Idempotency-Key` recibido y el `Content-Digest` con el hash del payload.
- La clave DEBE propagarse por todas las capas (incluyendo eventos de dominio y webhooks).
- Primera ejecución: almacenar resultado, hash del payload, clave y timestamp.
- Peticiones posteriores con la misma clave y mismo hash: retornar resultado original almacenado; NO reejecutar; incluir header `Last-Modified` con fecha original.
- Cuando la clave ya esté registrada pero el hash del payload sea distinto: rechazar con `409 CONFLICT`, código `ERR409_SERVER_STATE_CONFLICT`, motivo `CONFLICTING_IDEMPOTENT_REQUEST`.

### Implementación en eventos

- Todos los eventos publicados por la plataforma DEBEN ser idempotentes.
- El campo `idempotencykey` DEBE estar presente en el payload (conforme spec de eventos).
- El consumidor DEBE registrar el estado de ejecución con base en la clave y el hash del evento.
- El evento es único por `idempotencykey`.
- Si el evento ya hubiera sido procesado: ignorar, retornar ACK al broker; NO reejecutar la lógica; la ejecución original PUEDE registrarse en logs para auditoría.

### Cuándo usar

- En cualquier operación que modifique el estado del sistema (APIs y eventos).
- En flujos críticos (creación de transacciones, usuarios, contratos).
- En sistemas sujetos a fallos de red, replicaciones o timeouts.
- Siempre que el cliente o consumidor tenga política de retry activa.

### Cuándo no usar

- En operaciones puramente de lectura (GET, eventos de consulta).
- En flujos que no generan efectos colaterales.
- En llamadas que por definición deben producir siempre resultado nuevo (ej.: generación de UUID aleatorio, polling).

## Referencias

- [Especificación de Idempotencia — Hub Guardia](https://hub.guardia.finance/docs/specifications/idempotency/)
- Draft RFC The Idempotency-Key Header Field
- RFC 9562 (UUID)
