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

### Puntos de enforcement (edge interceptors)

La idempotencia se aplica en el **edge interceptor** de cada borde de entrada que modifica estado — un único interceptor de frontera por borde, no wiring por-handler ni por-service. Cada interceptor resuelve la clave a partir de su propio adapter y delega al núcleo de idempotencia compartido; la representación de replay se elige por borde.

| Borde | Interceptor | Resolución de la clave | Representación de replay |
|-------|-------------|------------------------|--------------------------|
| REST | interceptor de ruta/request en POST/PATCH/PUT | header `Idempotency-Key` del cliente (passthrough) | snapshot de la respuesta HTTP almacenado |
| Agente | interceptor de tool-dispatch en tools que modifican estado | determinista — SHA-256 del input canónico resuelto (content) | modelo de resultado almacenado |
| Worker/evento | interceptor de message-dispatch en los consumidores | `idempotencykey` del mensaje | modelo de resultado almacenado / ACK |

El interceptor es el único punto de enforcement: cualquier borde que modifique estado sin uno es una brecha. Cualquier nuevo borde de entrada que modifique estado DEBE pasar por su propio edge interceptor o documentarse como excepción.

El borde de agente deriva la clave de forma determinista en vez de exigir un UUID proporcionado por el cliente (principio 3): el llamador es un LLM, no un cliente con token de retry. Esta desviación DEBE registrarse en un ADR por el proyecto consumidor.

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

### Comportamientos esperados

#### APIs

- **Primera petición (clave nueva):** ejecutar la operación; almacenar resultado, hash del payload, clave y timestamp; retornar respuesta con status apropiado (ej.: 201); incluir header `Idempotency-Key` y `Content-Digest`.
- **Petición repetida (misma clave y mismo hash):** NO reejecutar; retornar el resultado original almacenado; incluir header `Last-Modified` con la fecha de la primera ejecución; status idéntico al de la primera respuesta.
- **Petición con misma clave y hash distinto:** rechazar con `409 CONFLICT`; código `ERR409_SERVER_STATE_CONFLICT`; motivo `CONFLICTING_IDEMPOTENT_REQUEST`; NO alterar estado ni sobrescribir el resultado anterior.

#### Eventos

- **Primera recepción de un evento (idempotencykey nueva):** procesar normalmente; registrar clave y hash; enviar ACK al broker.
- **Evento duplicado (misma idempotencykey ya procesada):** ignorar el procesamiento; retornar ACK al broker; NO reejecutar la lógica; la ejecución original PUEDE registrarse en logs para auditoría.

### Dependencias técnicas

- **Caché distribuido:** sistema de caché resiliente para almacenar estado de idempotencia (clave, hash, resultado, timestamp).
- **Hash:** algoritmo SHA-256 para el hash del payload (petición o cuerpo del evento).
- **Enrutamiento:** clave única por operación y alcance de ruta; propagación de la clave en todas las capas (APIs, eventos, webhooks).

### Seguridad y conformidad

- Estado de idempotencia almacenado de forma segura; acceso auditable.
- Intentos maliciosos de repetición (misma clave, payloads distintos) monitoreados y mitigados (ej.: rate limit, alertas).
- Logs con identificadores rastreables (clave, correlation_id) para conformidad e investigación.
- Retención del estado entre 2 y 24 horas; no almacenar datos sensibles en el caché de idempotencia más allá de lo estrictamente necesario.

## Referencias

- Draft RFC The Idempotency-Key Header Field
- RFC 9562 (UUID)
