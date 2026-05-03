# Kata: RESTful API Design for New Feature — Structured Document (Markdown)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Guardia platform — REST API design and structured Markdown document production

> **Status:** complementary. The canonical API artifact is `docs/{context}/oas/openapi.yaml` produced by `kata-api-design-oas` and persisted by `kata-feature-design-docs`. This Kata remains for generating additional human-readable documentation on demand; when used, the output complements (does not replace) `openapi.yaml`.

## Objective

This Kata defines the procedure to design the REST API for a new feature and **produce documentation in structured Markdown format** (endpoint tables, methods, status, request/response, errors): consult Lexis and Codex, identify resources and operations, define endpoints, and persist the document as a readable complement to the canonical `openapi.yaml` at `docs/{context}/oas/`.

## When to Use

- When the desired output format is a **Markdown document** (not OpenAPI)
- When a new feature requires exposure via HTTP API and no contract is documented yet
- When invoked by `cry-api-design` or by the Daedalus Warrior with Markdown output
- When you need to generate or update an API document at `docs/{context}/oas/` for human reading or review

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Feature description | Yes | Textual description of the domain, entities, operations, and business rules relevant to the API |
| Context or scope | No | Constraints (e.g., read-only, single resource), desired base path, or existing convention |
| Base path | No | URL prefix (e.g., `/v1/transactions`). If omitted, the agent proposes one based on the feature |

## Workflow

```
Progress:
- [ ] 1. Read directives and context
- [ ] 2. Consult Lexis and Codex RESTful
- [ ] 3. Identify resources and operations
- [ ] 4. Design endpoints (paths, methods, status, headers, payloads)
- [ ] 5. Document errors and idempotency
- [ ] 6. Produce structured Markdown document
- [ ] 7. Final validation
```

### Step 1: Read Directives and Context

1. Read `.ahrena/.directives` to obtain `language.default`. The destination is `docs/{context}/oas/`, per `lex-feature-design-docs`. Confirm with the user the Bounded Context name in PascalCase (it will be converted to kebab-case in the folder)
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

### Step 3: Identify Resources and Operations

1. Extract **resources** (nouns) from the feature description — e.g., transaction, user, contract
2. For each resource, list **operations** needed: create, read, update, delete (soft delete when applicable), list (with pagination)
3. Identify operations that **modify state** (POST, PATCH, PUT) and mark Idempotency-Key as required
4. Identify listings that require **pagination** (page_size, page_token) and **sorting** (order_by, sort)
5. Map persistent entities that must follow the base structure (entity_id, entity_type, version, timestamps)

### Step 4: Design Endpoints (paths, methods, status, headers, payloads)

1. Define **paths** in RESTful format: resource in plural or singular per project convention; identifier by path (e.g., `/v1/transactions/{entity_id}`)
2. Assign **HTTP methods**: GET (read), POST (create), PATCH or PUT (update), DELETE (logical delete when applicable)
3. For each endpoint, define **status codes** per codex-restful-status-codes (e.g., 200, 201, 204, 400, 401, 403, 404, 409, 422, 429, 500)
4. Define **required headers**: Idempotency-Key for mutations; X-Grd-Trace-Id when applicable; Content-Type, Accept
5. Define **request payload**: body for POST/PATCH/PUT; query parameters for listing (page_size, page_token, order_by, sort)
6. Define **response payload**: `data` structure (object or array), `pagination` when paginated listing, per codex-restful-payload
7. Ensure entities in response include required fields from codex-entities (entity_id, entity_type, created_at, updated_at, version when applicable)

### Step 5: Document Errors and Idempotency

1. For each mutation endpoint, document that **Idempotency-Key** is required; responses 400 (missing), 409 (same key, different payload)
2. List **known errors** per endpoint: ERR4xx/ERR5xx codes, reason (per codex-error-handling), developer-oriented message
3. Ensure error responses use only the `errors` structure (array of code, reason, message); do not expose sensitive data in authentication messages (lex-error-handling)
4. Document **pagination** in listings: request parameters (page_size, page_token), response structure (pagination with first_page_token, next_page_token, etc.)

### Step 6: Produce Structured Markdown Document

1. Obtain the canonical path **docs/{context}/oas/** per `lex-feature-design-docs`. Ensure the directory exists at the project root; if not, create it
2. Generate a **Markdown document** (.md) containing:
   - Title and API summary
   - Endpoint table (path, method, summary)
   - For each endpoint: parameters (path, query, header), request body when applicable, responses (200/201/204, 400, 401, 403, 404, 409, 422, 429, 500) with payload structure per codex-restful-payload
   - **Global headers** section (Idempotency-Key, X-Grd-Trace-Id, Content-Type, Authorization) per codex-restful-headers
   - Known errors section per endpoint (codes, reason, message)
   - Request/response examples when useful
3. Name the file consistently (e.g., `api-scheduled-transfers.md`, `api.md`). Save to **docs/{context}/oas/** (create or update). If the user requests inline delivery in addition to the file, deliver in chat as well

### Step 7: Final Validation

Before delivering the output, verify:

- [ ] All endpoints follow lex-restful-apis (status, payload, headers, pagination, sorting per spec)
- [ ] Mutation operations require Idempotency-Key (lex-idempotency)
- [ ] Persistent entities follow base structure (lex-entities)
- [ ] Errors follow standardized structure and known codes (lex-error-handling)
- [ ] Authentication/authorization documented per lex-auth when the API is protected
- [ ] Paginated listings have page_size, page_token, and pagination structure in the response
- [ ] Document is complete (endpoint table, details per endpoint, global headers, errors) with no contradiction to the Lexis
- [ ] Document was saved to path **docs/{context}/oas/** (directory created if it did not exist)

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| API document | Markdown (.md) | Directory **docs/{context}/oas/** (create directory if it does not exist; create or update the file) |
| Endpoint table | Markdown | Included in the document |

## Execution Example

### Example Input

```
Feature: Scheduled transfers module. Create, list, update, and cancel; paginated and date-sortable listing; idempotent mutations.
Base path: /v1/scheduled-transfers
```

### Example Output (summary)

`.md` file at **docs/{context}/oas/** with:
- Table: `POST /v1/scheduled-transfers` (create), `GET /v1/scheduled-transfers` (list), `GET /v1/scheduled-transfers/{entity_id}`, `PATCH ...`, `DELETE ...`
- For each endpoint: parameters, headers, request/response, status 200/201/204/400/404/409/422 etc.
- Global headers (Idempotency-Key, X-Grd-Trace-Id, Content-Type, Authorization)
- Known errors and payloads per codex-restful-payload and codex-entities

## Constraints

- This Kata produces only a Markdown document; it does not implement code or generate OpenAPI
- Does not change already-published documents without justification and ADR
- Exceptions to the Lexis must be documented in an ADR and reflected in the document
- The agent MUST escalate to a human when there is conflict between Lexis and a business requirement, or when the feature involves multiple bounded contexts with unclear API boundaries

## References

- lex-directives, lex-restful-apis, lex-entities, lex-idempotency, lex-error-handling, lex-auth, lex-feature-design-docs
- codex-restful-apis, codex-restful-status-codes, codex-restful-payload, codex-restful-headers, codex-restful-pagination, codex-restful-sorting, codex-entities, codex-idempotency, codex-error-handling, codex-auth
- kata-api-design-oas — canonical OpenAPI artifact
- kata-feature-design-docs — persistence procedure
