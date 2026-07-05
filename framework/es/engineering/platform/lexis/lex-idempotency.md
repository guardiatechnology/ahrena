# Lexis: Idempotencia en Operaciones que Modifican Estado

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Plataforma Guardia — APIs y eventos

## Propósito

Garantizar que las operaciones que modifican estado (APIs y eventos) en la plataforma Guardia sean idempotentes, preservando consistencia de datos y confiabilidad en entornos con fallos de red, timeouts o retries. Evitar duplicación de transacciones, inconsistencias de estado y efectos colaterales no deseados.

## Ley

> **Las operaciones que modifican estado (APIs y eventos) en la plataforma Guardia DEBEN ser idempotentes conforme a la especificación de Idempotencia del Hub; los endpoints que modifican estado (POST, PATCH, etc.) DEBEN exigir y validar el header Idempotency-Key; los eventos publicados DEBEN incluir idempotencykey y los consumidores DEBEN registrar y deduplicar por clave y hash.**

## Puntos de Enforcement (Edge Interceptors)

La idempotencia DEBE aplicarse en el **edge interceptor** de cada borde de entrada que modifica estado — nunca por-handler ni por-service. Cada interceptor resuelve la clave de idempotencia a partir de su propio adapter y delega al núcleo de idempotencia compartido. Tres bordes de entrada, tres interceptors:

1. **Borde REST** — un interceptor de ruta/request en los endpoints HTTP que modifican estado (POST, PATCH, PUT); resuelve la clave a partir del header `Idempotency-Key`.
2. **Borde de agente** — un interceptor de tool-dispatch que envuelve cada tool call de agente que modifica estado; resuelve la clave de forma determinista a partir del input canónico resuelto (SHA-256 del content).
3. **Borde de worker/evento** — un interceptor de message-dispatch en los consumidores de eventos; resuelve la clave a partir del `idempotencykey` del mensaje.

Cualquier otro borde de entrada que modifique estado DEBE pasar por su propio edge interceptor o documentarse como excepción. El wiring de idempotencia por-handler o por-service está PROHIBIDO.

## Alcance

- **Se aplica a:** endpoints HTTP de mutación (POST, PATCH, PUT) y publicación/consumo de eventos en la plataforma Guardia.
- **Agentes vinculados:** todos los implementadores de APIs y procesadores de eventos.
- **Excepciones:** Ninguna para operaciones que modifican estado; las operaciones puramente de lectura (GET, eventos de consulta) no están comprendidas.

## Consecuencias de Violación

1. **Duplicación:** transacciones o efectos aplicados más de una vez.
2. **Inconsistencia:** estado divergente entre consumidores y proveedores.
3. **Remediación:** implementar idempotencia conforme a la spec y reprocesar o corregir datos afectados.

## Ejemplos

### Correcto

Endpoint POST con Idempotency-Key obligatorio; retorno 400 cuando esté ausente; 409 cuando misma clave con payload distinto; evento con idempotencykey en el payload; consumidor ignora evento ya procesado y retorna ACK.

### Incorrecto

Endpoint de mutación sin exigencia de Idempotency-Key; evento sin idempotencykey; consumidor reejecutando lógica para la misma clave y hash.

## Validación Automatizada

- **Herramienta:** revisión de contrato (OpenAPI) y código; pruebas de retry con la misma clave.
- **Momento:** revisión de PR y pruebas de integración.
- **Métrica:** 0 endpoints de mutación sin Idempotency-Key; 0 eventos sin idempotencykey cuando la spec aplique.

## Referencias

- codex-idempotency (engineering/platform) (engineering/platform)
- RFC 9562 (UUID); Draft RFC Idempotency-Key Header
