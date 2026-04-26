# Codex: Idempotency in Guardia Platform APIs and Events

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guardia platform — idempotency

## Content

### Fundamental principles

1. **Same result:** idempotent operations MUST produce the same result for multiple executions with the same parameters.
2. **Key + hash:** verification MUST NOT depend on the key alone; it MUST consider the combination of key and payload hash (request or event). Hash algorithm: SHA-256.
3. **Client-provided key:** the idempotency key MUST be provided by the client; MUST be unique per operation and route scope; MUST be UUID (RFC 9562).
4. **Storage:** idempotency state MUST be stored in distributed, resilient cache; retention minimum 2 hours, maximum 24 hours.
5. **Security and audit:** state stored securely, access auditable; malicious replay attempts monitored and mitigated; logs with traceable identifiers.

### Implementation in APIs

- Endpoints that modify state (POST, PATCH) MUST be idempotent.
- The `Idempotency-Key` header MUST be required on those endpoints.
- When not provided: return `400 BAD REQUEST`, code `ERR400_MISSING_OR_MALFORMED_HEADER`, reason `IDEMPOTENCY_KEY_REQUIRED`.
- The response MUST include the same `Idempotency-Key` header received and `Content-Digest` with the payload hash.
- The key MUST be propagated through all layers (including domain events and webhooks).
- First execution: store result, payload hash, key, and timestamp.
- Subsequent requests with same key and same hash: return stored original result; do NOT re-execute; include `Last-Modified` header with original date.
- When the key is already registered but the payload hash differs: reject with `409 CONFLICT`, code `ERR409_SERVER_STATE_CONFLICT`, reason `CONFLICTING_IDEMPOTENT_REQUEST`.

### Implementation in events

- All events published by the platform MUST be idempotent.
- The `idempotencykey` field MUST be present in the payload (per event spec).
- The consumer MUST record execution state based on key and event hash.
- The event is unique per `idempotencykey`.
- If the event was already processed: ignore, return ACK to broker; do NOT re-execute logic; original execution MAY be logged for audit.

### When to use

- In any operation that modifies system state (APIs and events).
- In critical flows (creation of transactions, users, contracts).
- In systems subject to network failures, replication, or timeouts.
- Whenever the client or consumer has an active retry policy.

### When not to use

- In purely read-only operations (GET, query events).
- In flows that do not generate side effects.
- In calls that by definition must always produce new results (e.g., random UUID generation, polling).

### Expected behaviors

#### APIs

- **First request (new key):** execute the operation; store result, payload hash, key, and timestamp; return response with appropriate status (e.g., 201); include `Idempotency-Key` and `Content-Digest` headers.
- **Repeated request (same key and same hash):** do NOT re-execute; return stored original result; include `Last-Modified` header with first execution date; status identical to first response.
- **Request with same key and different hash:** reject with `409 CONFLICT`; code `ERR409_SERVER_STATE_CONFLICT`; reason `CONFLICTING_IDEMPOTENT_REQUEST`; do NOT change state or overwrite previous result.

#### Events

- **First receipt of an event (new idempotencykey):** process normally; record key and hash; send ACK to broker.
- **Duplicate event (same idempotencykey already processed):** skip processing; return ACK to broker; do NOT re-execute logic; original execution MAY be logged for audit.

### Technical dependencies

- **Distributed cache:** resilient cache system to store idempotency state (key, hash, result, timestamp).
- **Hash:** SHA-256 algorithm for payload hash (request or event body).
- **Routing:** key unique per operation and route scope; key propagation across all layers (APIs, events, webhooks).

### Security and compliance

- Idempotency state stored securely; access auditable.
- Malicious replay attempts (same key, different payloads) monitored and mitigated (e.g., rate limit, alerts).
- Logs with traceable identifiers (key, correlation_id) for compliance and investigation.
- State retention between 2 and 24 hours; do not store sensitive data in idempotency cache beyond what is strictly necessary.
