# Kata: RESTful API Design for New Feature — OpenAPI Specification (OAS)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Guardia platform — REST API design and OpenAPI 3.x specification production

## Objective

This Kata defines the procedure to design the REST API for a new feature and **produce a specification in OpenAPI 3.x format** (YAML or JSON): consult Lexis and Codex, identify resources and operations, define endpoints, and persist the contract in **docs/{context}/oas/openapi.yaml** in compliance with Guardia rules.

## When to Use

- When the desired output format is **OpenAPI 3.x** (YAML or JSON)
- When a new feature requires exposure via HTTP API and no contract exists yet
- When invoked by `cry-api-design` or by the Daedalus Warrior with OAS output
- When you need to generate or update an OAS file at `docs/{context}/oas/openapi.yaml`

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Feature description | Yes | Textual description of the domain, entities, operations, and business rules relevant to the API |
| Bounded Context name | Yes | Bounded Context identifier in PascalCase (e.g., `ScheduledPayments`); converted to kebab-case in the folder |
| Context or scope | No | Constraints (e.g., read-only, single resource), desired base path, or existing convention |
| Base path | No | URL prefix (e.g., `/v1/transactions`). If omitted, the agent proposes one based on the feature |
| OAS format | No | YAML or JSON. If omitted, use YAML as default |

## Workflow

```
Progress:
- [ ] 1. Read directives and context
- [ ] 2. Consult Lexis and Codex RESTful
- [ ] 3. Identify resources and operations
- [ ] 4. Design endpoints (paths, methods, status, headers, payloads)
- [ ] 5. Document errors and idempotency
- [ ] 6. Produce OpenAPI 3.x specification
- [ ] 7. Final validation
```

### Step 1: Read Directives and Context

1. Read `.ahrena/.directives` to obtain `language.default`. The destination is fixed: `docs/{context}/oas/openapi.yaml`, per `lex-feature-design-docs`. Confirm with the user the Bounded Context name in PascalCase (it will be converted to kebab-case in the folder)
2. Confirm that the feature description was provided. **Work iteratively:** if incomplete or ambiguous, **ask the user** (e.g., public or private API? Pagination and sorting? Base path? Soft delete or discarded_at? Filters?) and wait for answers; repeat until criteria are clear
3. Record the base path provided or propose one (e.g., `/v1/<main-resource>`) in kebab-case with version in the URL when applicable
4. Identify whether the API is public (Client Credentials, FAPI 2.0) or private (JWT, RBAC) to align with lex-auth

### Step 2: Consult Lexis and Codex RESTful

1. Consult **lex-directives** (required)
2. Consult **lex-restful-apis** — general compliance for HTTP endpoints
3. Consult **codex-restful-apis** and referenced modules: codex-restful-status-codes, codex-restful-payload, codex-restful-headers, codex-restful-pagination, codex-restful-sorting
4. Consult **lex-entities** and **codex-entities** — base entity structure (entity_id, entity_type, version, created_at, updated_at, discarded_at)
5. Consult **lex-idempotency** and **codex-idempotency** — Idempotency-Key for mutations
6. Consult **lex-error-handling** and **codex-error-handling** — error structure (code, reason, message)
7. Consult **lex-auth** and **codex-auth** — authentication and authorization (OAuth 2.0, JWT, RBAC)
8. Consult **codex-oas-structure** — order of operations in paths (POST, GET, PUT, PATCH, DELETE)

### Step 3: Identify Resources and Operations

1. Extract **resources** (nouns) from the feature description — e.g., transaction, user, contract
2. For each resource, list **operations** needed: create, read, update, delete (soft delete when applicable), list (with pagination)
3. Identify operations that **modify state** (POST, PATCH, PUT) and mark Idempotency-Key as required
4. Identify listings that require **pagination** (page_size, page_token) and **sorting** (order_by, sort)
5. Map persistent entities that must follow the base structure (entity_id, entity_type, version, timestamps)

### Step 4: Design Endpoints (paths, methods, status, headers, payloads)

1. Define **paths** in RESTful format: resource in plural or singular per project convention; identifier by path (e.g., `/v1/transactions/{entity_id}`)
2. Assign **HTTP methods**: GET (read), POST (create), PATCH or PUT (update), DELETE (logical delete when applicable). Order HTTP methods per path per **codex-oas-structure**: POST, GET, PUT, PATCH, DELETE (omit unused methods for the path, keeping the order)
3. For each endpoint, define **status codes** per codex-restful-status-codes (e.g., 200, 201, 204, 400, 401, 403, 404, 409, 422, 429, 500)
4. Define **required headers**: Idempotency-Key for mutations; X-Grd-Trace-Id when applicable; Content-Type, Accept
5. Define **request payload**: body for POST/PATCH/PUT; query parameters for listing (page_size, page_token, order_by, sort)
6. Define **response payload**: `data` structure (object or array), `pagination` when paginated listing, per codex-restful-payload
7. Ensure entities in responses include required fields from codex-entities (entity_id, entity_type, created_at, updated_at, version when applicable)

### Step 5: Document Errors and Idempotency

1. For each mutation endpoint, document that **Idempotency-Key** is required; responses 400 (missing), 409 (same key, different payload)
2. List **known errors** per endpoint: ERR4xx/ERR5xx codes, reason (per codex-error-handling), developer-oriented message
3. Ensure error responses use only the `errors` structure (array of code, reason, message); do not expose sensitive data in authentication messages (lex-error-handling)
4. Document **pagination** in listings: request parameters (page_size, page_token), response structure (pagination with first_page_token, next_page_token, etc.)

### Step 6: Produce OpenAPI 3.x Specification

1. Generate the **OpenAPI 3.x document** in YAML, containing:
   - `openapi: 3.x`
   - `paths` with each endpoint; for each path, list operations in **codex-oas-structure** order: post, get, put, patch, delete; for each operation: `parameters` (path, query, header), `requestBody` when applicable, `responses` (200, 201, 204, 400, 401, 403, 404, 409, 422, 429, 500)
   - Global header components (Idempotency-Key, X-Grd-Trace-Id, Content-Type, Authorization) per codex-restful-headers
   - Request/response schemas aligned with codex-restful-payload and codex-entities; mirror the field catalog from entities persisted in `docs/{context}/entities/`
2. **Persist via `kata-feature-design-docs`** with:
   - `Bounded Context` = name in PascalCase
   - `Category` = `oas`
   - `Content` = generated YAML
   - `Operation` = `create` or `update`
   - The kata writes to `docs/{context}/oas/openapi.yaml` and creates the directory if needed
3. If the user requests inline delivery in addition to the file, deliver it in chat as well

### Step 7: Final Validation

Before delivering the output, verify:

- [ ] All endpoints follow lex-restful-apis (status, payload, headers, pagination, sorting per spec)
- [ ] Mutation operations require Idempotency-Key (lex-idempotency)
- [ ] Persistent entities follow base structure (lex-entities)
- [ ] Errors follow standardized structure and known codes (lex-error-handling)
- [ ] Authentication/authorization documented per lex-auth when the API is protected
- [ ] Paginated listings have page_size, page_token, and pagination structure in the response
- [ ] OpenAPI 3.x file is complete (paths, methods, parameters, responses) with no contradiction to the Lexis
- [ ] Order of operations in each path follows codex-oas-structure (POST, GET, PUT, PATCH, DELETE)
- [ ] Persistence delegated to `kata-feature-design-docs` with category `oas` (canonical path `docs/{context}/oas/openapi.yaml`)

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| OpenAPI 3.x specification | YAML | `docs/{context}/oas/openapi.yaml` (persisted via `kata-feature-design-docs`) |

## Execution Example

### Example Input

```
Feature: Scheduled transfers module. Create, list, update, and cancel; paginated and date-sortable listing; idempotent mutations.
Base path: /v1/scheduled-transfers
Format: YAML
```

### Example Output (summary)

File `openapi.yaml` (or similar) at **docs/{context}/oas/openapi.yaml** with `paths` including:
- `POST /v1/scheduled-transfers` — 201, Idempotency-Key required
- `GET /v1/scheduled-transfers` — 200, query page_size, page_token, order_by, sort; response with data and pagination
- `GET /v1/scheduled-transfers/{entity_id}` — 200, 404
- `PATCH /v1/scheduled-transfers/{entity_id}` — 200, 409 (Idempotency-Key)
- `DELETE /v1/scheduled-transfers/{entity_id}` — 204, 404

Payloads and errors per codex-restful-payload and codex-entities.

## Constraints

- This Kata produces only OpenAPI 3.x specification; it does not implement code
- Does not change already-published OAS contracts without justification and ADR
- Exceptions to the Lexis must be documented in an ADR and reflected in the OAS
- The agent MUST escalate to a human when there is conflict between Lexis and a business requirement, or when the feature involves multiple bounded contexts with unclear API boundaries

## References

- lex-directives, lex-restful-apis, lex-entities, lex-idempotency, lex-error-handling, lex-auth, lex-feature-design-docs
- codex-restful-apis, codex-restful-status-codes, codex-restful-payload, codex-restful-headers, codex-restful-pagination, codex-restful-sorting, codex-entities, codex-idempotency, codex-error-handling, codex-auth, codex-oas-structure, codex-feature-design-docs
- kata-feature-design-docs — persistence procedure
- [OpenAPI Specification 3.x](https://spec.openapis.org/oas/v3.0.3)
