---
description: "API Design for New Feature. Shortcut to design the REST API of a new feature per Guardia Lexis and Codex"
---

# Cry: API Design for New Feature

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to design the REST API of a new feature per Guardia Lexis and Codex

## Description

This command invokes the Daedalus Warrior (or the agent assuming its role) to design the REST API of a new feature: consult Lexis and RESTful Codex and produce an **OpenAPI 3.x specification** (kata-api-design-oas) and a **structured Markdown document** of the API (kata-api-design-doc), both in **`docs/{context}/oas/`**.

## Usage

```
/cry-api-design <feature description> [base path]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `feature description` | Yes | Description of domain, entities, operations, and business rules relevant to the API | "Scheduled transfers module: create, list, update, and cancel; paginated and sortable listing; idempotent mutations" |
| `base path` | No | Desired URL prefix (e.g.: /v1/transactions). If omitted, the agent proposes one based on the feature | `/v1/scheduled-transfers` |

## What the Command Does

1. Interprets the feature description and base path (if provided)
2. Assumes the role of the Daedalus Warrior (API Design Specialist) or delegates to the agent executing kata-api-design-oas or kata-api-design-doc (according to the requested format)
3. The Daedalus Warrior (or the agent in its role) consults lex-directives and the RESTful Lexis/Codex: entities, idempotency, errors, and auth
4. Identifies resources, operations, pagination, sorting, and the need for Idempotency-Key
5. Produces specification (OpenAPI or Markdown) with endpoints, methods, status codes, headers, payloads, and errors
6. Delivers the artifact in the requested format or inline

## Prompt Template

```
Context:
- Feature description: {{feature description}}
- Base path (optional): {{base path}}

Task:
Act as the Daedalus Warrior (API Design Specialist) and iteratively execute **kata-api-design-oas** and **kata-api-design-doc** (the Katas consult the RESTful Lexis and Codex per their documentation). Based on the feature description, ask clarifying questions when necessary and refine the design based on the answers. Produce the OpenAPI specification and API document in `docs/{context}/oas/`. Use the provided base path or propose a suitable one.

Output format:
- Save to `docs/{context}/oas/` per `lex-feature-design-docs`
- Create the directory if it does not exist in the project
- Create or update the OpenAPI specification and API Markdown document at that path
- List or table of endpoints (path, method, summary); for each endpoint: parameters, required headers (e.g.: Idempotency-Key on mutations), status codes, request/response structure (data, pagination, errors per codex-restful-payload)
```

## Invocation Example

**Input:**

```
/cry-api-design "Scheduled transfers module: the user can create, list, update, and cancel; paginated and sortable listing by date; create/update/cancel are idempotent" /v1/scheduled-transfers
```

**Expected output:**

Structured response from the Daedalus Warrior with:
- Identified resources (e.g.: scheduled-transfers)
- Endpoints: POST (create), GET (list with pagination/sorting), GET by id, PATCH (update), DELETE (cancel)
- Idempotency-Key on POST and PATCH; statuses 200/201/204/400/409/422 etc.; payload with data/pagination/errors per codex-restful-payload
- Specification created or updated in `docs/{context}/oas/` (directory created if it did not exist)

## Constraints

- The Cry does not implement code; it only triggers the API design
- The feature description must be sufficient to identify resources and operations; if vague, the agent may ask for clarification
- Exceptions to Lexis must be documented in an ADR; the agent may flag when a decision requires an ADR

## Cry vs Kata

| Aspect | Cry | Kata |
|--------|-----|------|
| **Nature** | Quick invocation with feature description and base path | Complete procedure in multiple steps |
| **Complexity** | Low (1 command) | High (7 steps: directives, consult Lexis/Codex, resources, endpoints, errors, specification, validation) |
| **Configures agent?** | Yes (assumes the Daedalus Warrior role) | Yes (defines all design steps) |
| **Example** | "/cry-api-design create/list/cancel scheduled transfers" | Execute kata-api-design-oas or kata-api-design-doc with explicit inputs, per desired format |

## Associated Kata and Warrior

- **kata-api-design-oas** — API design and production of OpenAPI 3.x specification in `docs/{context}/oas/`
- **kata-api-design-doc** — API design and production of structured Markdown document in `docs/{context}/oas/`
- **warrior-daedalus** — API Design Specialist; executes kata-api-design-oas and kata-api-design-doc (both in `docs/{context}/oas/`)

## References

- `kata-api-design-oas`, `kata-api-design-doc` — Procedures executed by the Daedalus Warrior (the Katas consult the RESTful Lexis and Codex; see Kata documentation)
- `lex-feature-design-docs` — canonical structure `docs/{context}/{category}/`
