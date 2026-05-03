# Kata: Domain Modeling (DDD)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Guardia platform — domain discovery and modeling for a feature or module using Domain-Driven Design

## Objective

Produce a complete domain model for a feature or module through structured DDD dialogue with the user: establish the Ubiquitous Language, map Bounded Contexts, define Entities and Aggregates (conforming to lex-entities and lex-entity-naming), document Use Cases and Application Services, identify integration events and anti-corruption layers, and draw a Context Map. The output feeds directly into API design (warrior-daedalus) and event documentation (warrior-kronos).

## When to Use

- Before designing APIs or documenting events for a new feature or module
- When the domain is complex, has multiple actors, or crosses service boundaries
- When invoked by warrior-theseus or warrior-prometheus as the first phase of feature design
- When the team needs a shared Ubiquitous Language before implementation begins

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Domain description | Yes | Business domain, feature scope, or module being modeled |
| Bounded Context name | Yes | Bounded Context identifier in PascalCase (e.g., `ScheduledPayments`, `Reconciliation`) |
| CloudEvents module | Yes | Module identifier used in CloudEvents type segments (e.g., `platform`, `reconciliation`, `fiscal`) |
| Known entities | No | Entities already identified; if provided, validate and extend from them |
| Bounded context scope | No | Single or multiple contexts; if omitted, the agent determines from description |

## Workflow

```
Progress:
- [ ] 1. Read directives and scope
- [ ] 2. Consult Lexis and Codex
- [ ] 3. Elicit domain description
- [ ] 4. Define Ubiquitous Language
- [ ] 5. Map Bounded Contexts
- [ ] 6. Define Entities and Aggregates
- [ ] 7. Define Use Cases and Application Services
- [ ] 8. Identify integration events and anti-corruption layers
- [ ] 9. Draw Context Map
- [ ] 10. Persist the domain model in the canonical structure
```

### Step 1: Read Directives and Scope

1. Read `.ahrena/.directives` to obtain `language.default`. The destination folder for artifacts is fixed at `docs/{context}/entities/` per `lex-feature-design-docs` (no longer a configurable `paths.domain`)
2. Confirm the domain description, the Bounded Context name (PascalCase), and the CloudEvents module were provided; if insufficient, **ask the user** (What is the main business process? Who are the actors? What are the system boundaries? What triggers the first action?) and wait for answers
3. Check whether files already exist in `docs/{context}/entities/` — incorporate them as input if available
4. Identify the bounded context scope: single context or multiple

### Step 2: Consult Lexis and Codex

1. Consult **lex-entities** — every persistent entity MUST have entity_id (UUID v7), entity_type, version, created_at, updated_at, discarded_at
2. Consult **lex-entity-naming** — `entity_type` and field names use snake_case; aggregate names in DDD documents use PascalCase
3. Consult **lex-cloudevents** — events follow `event.guardia.{module}.{entity_type}.{event_name}` with snake_case segments
4. Consult **codex-entities** — base entity model reference

### Step 3: Elicit Domain Description

If the domain description is insufficient to start modeling, ask the user targeted questions:

1. **Business process:** "Describe the main workflow step by step. What initiates it and what concludes it?"
2. **Actors:** "Who initiates actions — users, external systems, scheduled jobs?"
3. **Business rules:** "What are the key constraints? What can or cannot happen?"
4. **System boundaries:** "What is inside this module and what belongs to another service?"
5. **Known pain points:** "Are there areas of the domain that are unclear or disputed?"

Wait for answers before proceeding to Step 4.

### Step 4: Define Ubiquitous Language

Establish a shared vocabulary that domain experts and engineers will use consistently:

1. For each key domain term, document:
   - **Term** — the agreed name (PascalCase for entities/aggregates, plain for concepts)
   - **Definition** — precise meaning in this bounded context
   - **Synonyms to avoid** — alternative terms that must not be used (to prevent ambiguity)
2. Resolve naming conflicts: if two stakeholders use different terms for the same concept, agree on one and document the rejected alternative
3. Validate terms against lex-entity-naming: entity names in snake_case for APIs/events, PascalCase in DDD documents

Example glossary entry:
| Term | Definition | Synonyms to Avoid |
|------|------------|-------------------|
| ScheduledTransfer | A bank transfer ordered by an accountant to execute on a future date, requiring supervisor approval | "planned transfer", "future payment" |
| Execution | The moment the transfer is processed by the banking partner on the scheduled date | "processing", "settlement" |

### Step 5: Map Bounded Contexts

A Bounded Context is a boundary within which a particular domain model is defined and applicable:

1. Identify boundaries where terms change meaning or ownership shifts
2. For each Bounded Context, document:
   - **Name** — descriptive, reflects its responsibility (e.g., `ScheduledPayments`, `Approval`, `Reconciliation`)
   - **Responsibility** — what it owns and decides
   - **Owner** — team or service responsible
   - **Entities it owns** — list of aggregates within this context
3. Mark entities that appear in multiple contexts — they will require explicit mapping at boundaries
4. Flag context boundaries that are unclear as hotspots

### Step 6: Define Entities and Aggregates

#### Entities

For each persistent entity, document (conforming to lex-entities):

| Field | Requirement |
|-------|-------------|
| Name | PascalCase in DDD doc; snake_case as `entity_type` in APIs/events |
| `entity_type` | snake_case string (e.g., `scheduled_transfer`) |
| Bounded Context | Which context owns this entity |
| Key fields | Business-significant attributes (beyond base structure) |
| Lifecycle states | States the entity transitions through (e.g., `requested → approved → executed`) |

All entities MUST include the base structure from lex-entities: `entity_id`, `entity_type`, `version`, `created_at`, `updated_at`, `discarded_at`.

#### Aggregates

An Aggregate is a cluster of entities and value objects treated as a single unit with a root entity:

1. Identify the **Aggregate Root** — the entry point; all external references go through it
2. Document:
   - **Aggregate Root** — the root entity (e.g., `ScheduledTransfer`)
   - **Members** — entities and value objects within the aggregate boundary
   - **Invariants** — business rules that always hold across the aggregate (e.g., "A ScheduledTransfer cannot be executed if its status is not `approved`")
   - **Commands accepted** — what operations the aggregate processes
   - **Events produced** — domain events emitted on state change

### Step 7: Define Use Cases and Application Services

Use Cases describe what the system does from the actor's perspective:

1. For each use case, document:
   - **Name** — imperative verb + noun (e.g., `RequestScheduledTransfer`, `ApproveScheduledTransfer`)
   - **Actor** — who initiates (user role, external system, scheduler)
   - **Preconditions** — what must be true before the use case can execute
   - **Steps** — ordered sequence of actions
   - **Postconditions** — what is true after successful execution
   - **Failure paths** — what happens when the use case cannot complete (list as hotspots if undefined)
   - **Aggregate touched** — which aggregate processes the command
   - **Events emitted** — domain events produced on success

2. Group use cases by actor or by aggregate for readability

### Step 8: Identify Integration Events and Anti-Corruption Layers

**Integration events** cross bounded context boundaries:

1. For each event that must leave the bounded context, document:
   - **Event type** — `event.guardia.{module}.{entity_type}.{event_name}` (lex-cloudevents)
   - **Publisher** — which bounded context / aggregate produces it
   - **Consumers** — which contexts consume it
   - **Payload sketch** — key data fields (snake_case per lex-entity-naming)
2. Flag events where the same concept has different names in different contexts — these require **translation at the boundary**

**Anti-Corruption Layers (ACL):**

1. Identify external systems whose models differ from the Guardia domain model
2. For each ACL, document:
   - **External system** — name and owner
   - **Translation** — how external concepts map to Guardia entities
   - **Direction** — inbound (external → Guardia) or outbound (Guardia → external)

### Step 9: Draw Context Map

Produce a textual or Markdown-table Context Map showing relationships between bounded contexts:

| Relationship Pattern | When to Use |
|----------------------|-------------|
| **Shared Kernel** | Two contexts share a subset of the domain model; changes require coordination |
| **Customer/Supplier** | Upstream context provides what downstream consumes; downstream has requirements |
| **Conformist** | Downstream adopts upstream model without influence |
| **Anti-Corruption Layer** | Downstream translates upstream model to protect its own model |
| **Open Host Service** | Upstream publishes a protocol / API for multiple downstreams |
| **Published Language** | Shared language (e.g., CloudEvents) used across contexts |

For each context pair with a relationship, document the pattern and any constraints.

### Step 10: Persist the Domain Model in the Canonical Structure

The domain model **does not** become a monolithic file. It is distributed across the canonical files defined by `lex-feature-design-docs`:

- **Entity and aggregate catalog** → one `docs/{context}/entities/{entity-name}.md` file per entity, containing: DDD Classification, Why it exists, Fields, Business Rules, Invariants, Relations, Errors, References (template in `codex-feature-design-docs`)
- **Identified integration events** → forwarded to warrior-kronos to become `docs/{context}/events/events.md`
- **Use Cases, Bounded Contexts, Ubiquitous Language, Context Map, ACLs, Hotspots** → recorded as notes for warrior-prometheus to consolidate and publish to Notion (Guardia Platform > Domain Models)

For each entity in the catalog, invoke **`kata-feature-design-docs`** with:
- `Bounded Context` = name in PascalCase
- `Category` = `entities`
- `Content` = catalog of fields, rules, invariants, relations, and errors derived from modeling
- `Operation` = `create` (first run) or `update` (revision)

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Entity files | Markdown | `docs/{context}/entities/{entity-name}.md` (1 per entity) |
| Ubiquitous language glossary | Notes for Prometheus | Notion: Guardia Platform > Domain Models > {Bounded Context} |
| Integration events catalog | List | Input for warrior-kronos (Phase 3 of Prometheus) |

## Execution Example

### Input

```
Domain: Scheduled transfers — accountants schedule future bank transfers; supervisor approval required before execution; a scheduler triggers execution on the scheduled date.
Module: platform
```

### Output Summary

Files persisted via `kata-feature-design-docs`:

- `docs/scheduled-payments/entities/scheduled-transfer.md`

Additional notes consolidated by warrior-prometheus (published to Notion):

**Ubiquitous Language:**
| Term | Definition | Synonyms to Avoid |
|------|------------|-------------------|
| ScheduledTransfer | Transfer ordered for future execution, requiring approval | "planned transfer", "future payment" |
| Execution | Processing by the banking partner on the scheduled date | "processing", "settlement" |

**Bounded Contexts:** `ScheduledPayments` (owns ScheduledTransfer), `Approval` (owns approval flow), `BankingIntegration` (ACL to banking partner)

**Entity Catalog:**
| Entity | entity_type | Bounded Context | Lifecycle |
|--------|-------------|-----------------|-----------|
| ScheduledTransfer | `scheduled_transfer` | ScheduledPayments | requested → approved → executed \| failed \| cancelled |

**Use Cases:** `RequestScheduledTransfer`, `ApproveScheduledTransfer`, `ExecuteScheduledTransfer`, `CancelScheduledTransfer`

**Integration Events:** `event.guardia.platform.scheduled_transfer.requested`, `.approved`, `.executed`, `.failed`, `.cancelled`

**Open Hotspots:**
| Description | Priority | Owner |
|-------------|----------|-------|
| Retry policy on execution failure is undefined | P1 | Platform team |

## Constraints

- This Kata produces the modeling; **persistence is delegated to `kata-feature-design-docs`**
- Do not skip hotspot identification — every undocumented uncertainty becomes a bug or scope gap
- The entity catalog MUST be complete enough to feed warrior-daedalus and warrior-kronos without additional discovery
- Escalate to human when bounded context ownership is ambiguous or when a single aggregate spans multiple teams without a clear owner
- entity_type values MUST be in snake_case (lex-entity-naming); aggregate names in DDD sections MUST be in PascalCase
- Do not persist a monolithic `domain-model.md` document — distribute across `entities/`, `events/`, and `oas/` per `lex-feature-design-docs`

## References

- `lex-feature-design-docs` — canonical structure `docs/{context}/{category}/`
- `codex-feature-design-docs` — templates applied per category
- `kata-feature-design-docs` — persistence procedure
- `lex-entities` — base entity structure
- `lex-entity-naming` — snake_case for entity_type, fields, and CloudEvents segments
- `lex-cloudevents` — CloudEvents type format
- `codex-entities` — entity model reference
- [Domain-Driven Design — Eric Evans](https://www.domainlanguage.com/ddd/reference/)
- [Implementing Domain-Driven Design — Vaughn Vernon](https://vaughnvernon.com/)
