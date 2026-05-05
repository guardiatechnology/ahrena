---
name: kata-api-design-review
description: "RESTful API Design Review. Guardia platform — compliance review of existing HTTP API contracts against Guardia Lexis and Codex"
---

# Kata: RESTful API Design Review

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Guardia platform — compliance review of existing HTTP API contracts against Guardia Lexis and Codex

## Workflow

```
Progress:
- [ ] 1. Read directives and locate contract
- [ ] 2. Consult Lexis and Codex
- [ ] 3. Validate endpoints (paths, methods, status codes)
- [ ] 4. Validate entity structure
- [ ] 5. Validate idempotency
- [ ] 6. Validate error structure
- [ ] 7. Validate authentication
- [ ] 8. Validate pagination and sorting
- [ ] 9. Produce review report
```

### Step 1: Read Directives and Locate Contract

1. Identify `language.default` from `.ahrena/.directives`
2. Locate the contract at the provided path. If the path does not exist or cannot be parsed, alert the user and stop
3. Identify whether the contract is OpenAPI 3.x (YAML/JSON) or Markdown. If unclear, ask the user
4. Note the review scope: all endpoints or a specific subset

### Step 2: Consult Lexis and Codex

1. Consult **lex-restful-apis** — general compliance for HTTP endpoints
2. Consult **codex-restful-apis**, codex-restful-status-codes, codex-restful-payload, codex-restful-headers, codex-restful-pagination, codex-restful-sorting
3. Consult **lex-entities** and **codex-entities** — base entity structure (entity_id, entity_type, version, timestamps)
4. Consult **lex-idempotency** and **codex-idempotency** — Idempotency-Key for mutations
5. Consult **lex-error-handling** and **codex-error-handling** — error structure (code, reason, message)
6. Consult **lex-auth** and **codex-auth** — authentication and authorization
7. Consult **codex-oas-structure** — operation ordering within paths (POST, GET, PUT, PATCH, DELETE)

### Step 3: Validate Endpoints (paths, methods, status codes)

For each endpoint in the contract:

1. **Path format** — RESTful naming: plural nouns, kebab-case, version prefix `/v1/`; identifier in path (e.g., `/{entity_id}`)
2. **HTTP methods** — correct semantics: POST = create, GET = read, PATCH or PUT = update, DELETE = remove
3. **Status codes** — only allowed codes per codex-restful-status-codes: 200, 201, 204, 400, 401, 403, 404, 409, 422, 429, 500; flag any code outside the allowed set
4. **Operation order** (OAS only) — POST, GET, PUT, PATCH, DELETE per path per codex-oas-structure; flag deviations
5. **Required headers** — X-Grd-Trace-Id when applicable; Content-Type, Accept

### Step 4: Validate Entity Structure

For each response payload that represents a persistent entity:

1. **entity_id** — present and typed as UUID
2. **entity_type** — present and non-empty string
3. **created_at**, **updated_at** — present as ISO 8601 timestamps
4. **discarded_at** — present when the endpoint supports soft delete; flag absence only when DELETE is implemented
5. **version** — present when optimistic locking is documented
6. Flag any entity missing required fields per lex-entities

### Step 5: Validate Idempotency

For each state-modifying operation (POST, PATCH, PUT):

1. **Idempotency-Key header** — declared as required in the endpoint definition
2. **Response 400** — documented for missing Idempotency-Key (`ERR400_MISSING_IDEMPOTENCY_KEY`)
3. **Response 409** — documented for same key with different payload
4. Flag any mutation endpoint missing Idempotency-Key per lex-idempotency

### Step 6: Validate Error Structure

For each error response:

1. **`errors` array** — body uses `{ "errors": [{ "code": "...", "reason": "...", "message": "..." }] }` structure
2. **`code` format** — follows `ERR{HTTP_CODE}_{NAME}` pattern (e.g., `ERR400_MISSING_FIELD`, `ERR404_NOT_FOUND`)
3. **`reason`** — must be a cataloged value per codex-known-errors
4. **Authentication messages** — 401/403 responses must not reveal whether the user or resource exists per lex-error-handling
5. Flag any error response deviating from the standard structure

### Step 7: Validate Authentication

1. **Protected endpoints** — authentication scheme declared (OAuth 2.0 / Bearer JWT)
2. **Public APIs** — Client Credentials + FAPI 2.0 extensions documented when applicable
3. **Private APIs** — JWT from trusted IdP + RBAC scope documented
4. Flag any protected endpoint missing authentication documentation per lex-auth

### Step 8: Validate Pagination and Sorting

For each listing endpoint (GET returning a collection):

1. **Request parameters** — `page_size` and `page_token` declared as query parameters
2. **Response structure** — `pagination` object with `first_page_token`, `next_page_token`, `prev_page_token`, `page_size` per codex-restful-pagination
3. **Sorting** — `order_by` and `sort` query parameters declared when sorting is supported
4. Flag any collection endpoint missing pagination per codex-restful-pagination

### Step 9: Produce Review Report

Generate a structured Markdown review report:

1. **Header** — contract reviewed (path, format, total endpoint count), overall verdict:
   - ✅ **Compliant** — zero ERRORs and zero WARNINGs
   - ⚠️ **Warnings** — zero ERRORs, one or more WARNINGs
   - ❌ **Violations** — one or more ERRORs
2. **Findings table** — one row per finding:

   | Severity | Endpoint | Lexis / Codex | Finding | Suggestion |
   |----------|----------|---------------|---------|------------|

   Severity levels:
   - `ERROR` — Lexis violation; MUST be fixed before merge
   - `WARNING` — Codex deviation; SHOULD be fixed
   - `INFO` — improvement opportunity; MAY be addressed

3. **Summary counts** — total ERROR / WARNING / INFO
4. **Next steps** — in `fix` mode, append inline correction for each ERROR and WARNING; in `report` mode, list the endpoints requiring attention

If no findings, state: "Contract fully compliant with Guardia Lexis and Codex."

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Review report | Markdown | Delivered in chat; optionally saved to `docs/reviews/api-review-{contract-name}.md` |

## Execution Example

### Example Input

```
Contract path: docs/oas/openapi.yaml
Review scope: all endpoints
Fix mode: report
```

### Example Output (summary)

```markdown
## API Design Review — openapi.yaml

**Endpoints reviewed:** 5 | **Verdict:** ❌ 2 ERRORs, 3 WARNINGs

| Severity | Endpoint | Rule | Finding | Suggestion |
|----------|----------|------|---------|------------|
| ERROR | POST /v1/transfers | lex-idempotency | Idempotency-Key header not declared | Add required header Idempotency-Key; document 400 and 409 responses |
| ERROR | GET /v1/transfers/{entity_id} | lex-entities | entity_type missing from response schema | Add entity_type: string (non-empty) to TransferResponse schema |
| WARNING | DELETE /v1/transfers/{entity_id} | codex-restful-status-codes | Status 200 used instead of 204 for empty body response | Change to 204 No Content |
| WARNING | GET /v1/transfers | codex-restful-pagination | page_token missing from pagination response object | Add page_token to the pagination schema |
| WARNING | POST /v1/transfers | codex-oas-structure | GET declared before POST in path definition | Reorder: POST, then GET |

**Next steps:** fix 2 ERRORs before merge; 3 WARNINGs should be addressed in the same PR.
```

## Constraints

- This Kata produces only a review report; it does not modify the contract unless `fix` mode is explicitly requested
- Every deviation MUST be classified as ERROR (Lexis) or WARNING (Codex) — never silently accept violations
- Escalate to a human when a deviation may be an intentional exception requiring an ADR
- Do not flag deviations in endpoints explicitly excluded from the review scope
