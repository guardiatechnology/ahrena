---
name: kata-api-design
description: "RESTful API Design for New Feature. Guardia platform — design of REST APIs compliant with RESTful Lexis and Codex"
---

# Kata: RESTful API Design for New Feature

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Guardia platform — design of REST APIs compliant with RESTful Lexis and Codex

## Workflow

```
Progress:
- [ ] 1. Read directives and context
- [ ] 2. Consult RESTful Lexis and Codex
- [ ] 3. Identify resources and operations
- [ ] 4. Design endpoints (paths, methods, status, headers, payloads)
- [ ] 5. Document errors and idempotency
- [ ] 6. Produce specification
- [ ] 7. Final validation
```

### Step 1: Read Directives and Context

1. Read `.ahrena/.directives` to obtain `language.default`, canonical paths, and **paths.oas** (OpenAPI specification destination; default `docs/oas`)
2. Confirm that the feature description was provided; if incomplete, list gaps and request completion before proceeding
3. Record the provided base path or propose one (e.g., `/v1/<main-resource>`) using kebab-case and version in URL when applicable
4. Identify whether the API is public (Client Credentials, FAPI 2.0) or private (JWT, RBAC) to align with lex-auth

### Step 2: Consult RESTful Lexis and Codex

1. Consult **lex-directives** (mandatory)
2. Consult **lex-restful-apis** — overall HTTP endpoint compliance
3. Consult **codex-restful-apis** and referenced modules:
   - codex-restful-status-codes (when to use each status)
   - codex-restful-payload (data, pagination, errors, debug structure)
   - codex-restful-headers (Idempotency-Key, X-Grd-Trace-Id, etc.)
   - codex-restful-pagination (page_size, page_token, order_by, sort)
   - codex-restful-sorting (order_by, sort)
4. Consult **lex-entities** and **codex-entities** — base entity structure (entity_id, entity_type, version, created_at, updated_at, discarded_at)
5. Consult **lex-idempotency** and **codex-idempotency** — Idempotency-Key for mutations
6. Consult **lex-error-handling** and **codex-error-handling** — error structure (code, reason, message)
7. Consult **lex-auth** and **codex-auth** — authentication and authorization (OAuth 2.0, JWT, RBAC)

### Step 3: Identify Resources and Operations

1. Extract **resources** (nouns) from the feature description — e.g., transaction, user, contract
2. For each resource, list required **operations**: create, read, update, delete (soft delete when applicable), list (with pagination)
3. Identify operations that **modify state** (POST, PATCH) and mark Idempotency-Key as required
4. Identify listings that require **pagination** (page_size, page_token) and **sorting** (order_by, sort)
5. Map persistent entities that must follow the base structure (entity_id, entity_type, version, timestamps)

### Step 4: Design Endpoints (paths, methods, status, headers, payloads)

1. Define **paths** in RESTful format: resource in plural or singular per project convention; identifier in path (e.g., `/v1/transactions/{entity_id}`)
2. Assign **HTTP methods**: GET (read), POST (create), PATCH or PUT (update), DELETE (logical delete when applicable)
3. For each endpoint, define **status codes** per codex-restful-status-codes (e.g., 200, 201, 204, 400, 401, 403, 404, 409, 422, 429, 500)
4. Define **required headers**: Idempotency-Key for mutations; X-Grd-Trace-Id when applicable; Content-Type, Accept
5. Define **request payload**: body for POST/PATCH/PUT; query parameters for listing (page_size, page_token, order_by, sort)
6. Define **response payload**: `data` structure (object or array), `pagination` when paginated listing, per codex-restful-payload
7. Ensure entities in response include required codex-entities fields (entity_id, entity_type, created_at, updated_at, version when applicable)

### Step 5: Document Errors and Idempotency

1. For each mutation endpoint, document that **Idempotency-Key** is required; responses 400 (missing), 409 (same key, different payload)
2. List **known errors** per endpoint: ERR4xx/ERR5xx codes, reason (per codex-error-handling), developer-oriented message
3. Ensure error responses use only the `errors` structure (array of code, reason, message); do not expose sensitive data in authentication messages (lex-error-handling)
4. Document **pagination** for listings: request parameters (page_size, page_token), response structure (pagination with first_page_token, next_page_token, etc.)

### Step 6: Produce Specification

1. Obtain the canonical destination path from **paths.oas** (in `.ahrena/.directives`). Ensure that directory exists at the project root: if it does not exist, create it before saving any artifact
2. Generate specification artifact in one accepted format:
   - **OpenAPI 3.x** fragment (YAML or JSON) with paths, methods, parameters, requestBody, responses, headers
   - Or structured **Markdown** document with endpoint tables, methods, status, request/response, and errors
3. Include for each endpoint: path, method, summary, parameters (path, query, header), request body (when applicable), responses (200/201/204, 400, 401, 403, 404, 409, 422, 429, 500), payload examples when useful
4. Include **global headers** section (Idempotency-Key, X-Grd-Trace-Id, Content-Type, Authorization)
5. Save to the directory defined in **paths.oas** (create or update the file). If the user requests inline delivery in addition to the file, deliver in chat as well

### Step 7: Final Validation

Before delivering the output, verify:

- [ ] All endpoints follow lex-restful-apis (status, payload, headers, pagination, sorting per spec)
- [ ] Mutation operations require Idempotency-Key (lex-idempotency)
- [ ] Persistent entities follow base structure (lex-entities)
- [ ] Errors follow standardized structure and known codes (lex-error-handling)
- [ ] Authentication/authorization documented per lex-auth when the API is protected
- [ ] Paginated listings have page_size, page_token and pagination structure in response
- [ ] Specification is complete (paths, methods, status, request/response) and consistent with Lexis
- [ ] Specification was saved to the path defined in **paths.oas** (`.ahrena/.directives`; directory created if it did not exist)

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| API specification | OpenAPI 3.x (YAML/JSON) or structured Markdown | **paths.oas** directory in `.ahrena/.directives` (create directory if it does not exist; create or update the file) |
| Endpoint table | Markdown | Included in document at paths.oas or as appendix |

## Execution Example

### Example Input

```
Feature: Scheduled transfers module. User can create a scheduled transfer (date, amount, destination account), list their own, cancel or update date/amount. Listing must be paginated and sortable by date. Create/update/cancel operations must be idempotent.
Base path: /v1/scheduled-transfers
```

### Example Output (summary)

- `POST /v1/scheduled-transfers` — create (201, Idempotency-Key required)
- `GET /v1/scheduled-transfers` — list (200, pagination and order_by)
- `GET /v1/scheduled-transfers/{entity_id}` — get one (200, 404)
- `PATCH /v1/scheduled-transfers/{entity_id}` — update (200, 409 with Idempotency-Key)
- `DELETE /v1/scheduled-transfers/{entity_id}` — cancel/soft delete (204, 404)
- Response payload with data/pagination/errors per codex-restful-payload; entities with entity_id, entity_type, created_at, updated_at, version.

## Constraints

- This Kata does not implement code; it only produces design and specification
- It does not change already published OpenAPI contracts without justification and ADR
- Exceptions to Lexis must be documented in ADR and noted in the specification
- The agent MUST escalate to a human when there is conflict between Lexis and business requirement or when the feature involves multiple bounded contexts with unclear API boundaries
