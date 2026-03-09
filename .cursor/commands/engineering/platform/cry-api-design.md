---
description: "API Design for New Feature. Shortcut to design the REST API of a new feature per Guardia Lexis and Codex"
---

# Cry: API Design for New Feature

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to design the REST API of a new feature per Guardia Lexis and Codex

## Usage

```
/cry-api-design <feature description> [base path]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `feature description` | Yes | Description of domain, entities, operations, and business rules relevant to the API | "Scheduled transfers module: create, list, update, cancel; paginated sortable listing; idempotent mutations" |
| `base path` | No | Desired URL prefix (e.g., /v1/transactions). If omitted, the agent proposes one based on the feature | `/v1/scheduled-transfers` |

## What the Command Does

1. Interprets the feature description and base path (if provided)
2. Assumes the role of the Daedalus Warrior (API design specialist) or delegates to the agent that executes kata-api-design-oas or kata-api-design-doc (per requested format)
3. Consults lex-directives and RESTful Lexis/Codex, entities, idempotency, errors, and auth
4. Identifies resources, operations, pagination, sorting, and Idempotency-Key requirements
5. Produces specification (OpenAPI or Markdown) with endpoints, methods, status, headers, payloads, and errors
6. Delivers the artifact in the requested format or inline

## Prompt Template

```
Context:
- Feature description: {{feature description}}
- Base path (optional): {{base path}}

Task:
Act as the Daedalus Warrior (API Design Specialist) and execute iteratively **kata-api-design-oas** and **kata-api-design-doc**, producing both artifacts in paths.oas.
Based on the feature description above, ask clarifying questions when needed (scope, authentication, pagination, sorting, base path, specific criteria) and refine the design based on their answers. Consult Guardia RESTful Lexis and Codex and produce the OpenAPI specification and API document in paths.oas.
Use the provided base path or propose an appropriate one.

Output format:
- Consult **paths.oas** in `.ahrena/.directives` for the destination
- Create the directory (paths.oas) if it does not exist in the project
- Create or update the OpenAPI specification and the API Markdown document in that path
- List or table of endpoints (path, method, summary); for each endpoint: parameters, required headers (e.g., Idempotency-Key for mutations), status codes, request/response structure (data, pagination, errors per codex-restful-payload)
```

## Invocation Example

**Input:**

```
/cry-api-design "Scheduled transfers module: user can create, list, update, and cancel; paginated listing sortable by date; create/update/cancel idempotent" /v1/scheduled-transfers
```

**Expected output:**

Structured response from the Daedalus Warrior with:
- Identified resources (e.g., scheduled-transfers)
- Endpoints: POST (create), GET (list with pagination/sorting), GET by id, PATCH (update), DELETE (cancel)
- Use of Idempotency-Key in POST and PATCH; status 200/201/204/400/409/422 etc.; payload with data/pagination/errors per codex-restful-payload
- Specification created or updated in the **paths.oas** path (`.ahrena/.directives`; directory created if it did not exist)

## Constraints

- The Cry does not implement code; it only triggers API design
- The feature description must be sufficient to identify resources and operations; if vague, the agent may request more detail
- Exceptions to Lexis must be documented in ADR; the agent may signal when a decision requires ADR

## Associated Kata and Warrior

- **kata-api-design-oas** — API design and OpenAPI 3.x specification output in paths.oas
- **kata-api-design-doc** — API design and structured Markdown document output in paths.oas
- **warrior-daedalus** — API Design Specialist; executes kata-api-design-oas and kata-api-design-doc (both in paths.oas)
