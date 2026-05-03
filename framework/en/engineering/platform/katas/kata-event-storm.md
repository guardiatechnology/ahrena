# Kata: Event Storming

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Guardia platform — discovery of domain events, commands, aggregates, policies, and bounded contexts for a feature or module

## Objective

This Kata defines the procedure to **conduct an Event Storming session** for a domain or feature: identify domain events, commands, aggregates, policies, external systems, read models, hotspots, and bounded contexts; map discovered events to CloudEvents types; and produce a structured discovery catalog ready to feed `kata-events-doc`.

## When to Use

- When starting the design of a new feature or module and the event landscape is not yet known
- When mapping an existing domain to surface missing, implicit, or undocumented events
- When invoked by Warrior Kronos at the discovery phase, before `kata-events-doc`
- When `cry-event-storm` is triggered by the user

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Domain or feature description | Yes | Textual description of the business domain, feature scope, or module to be stormed |
| Bounded Context name | Yes | Bounded Context identifier in PascalCase (e.g., `ScheduledPayments`) |
| CloudEvents module | Yes | Guardia module identifier used in CloudEvents type (e.g., `platform`, `reconciliation`, `fiscal`) |
| Bounded context scope | No | Whether to storm a single bounded context or multiple. If omitted, storms a single context |
| Known events | No | List of already-known events to use as starting point. If provided, extend and validate against them |

## Workflow

```
Progress:
- [ ] 1. Read directives and scope
- [ ] 2. Consult Lexis and Codex
- [ ] 3. Identify domain events (timeline)
- [ ] 4. Identify commands and actors
- [ ] 5. Identify aggregates
- [ ] 6. Identify policies (automatic reactions)
- [ ] 7. Identify external systems and read models
- [ ] 8. Mark hotspots
- [ ] 9. Identify bounded contexts
- [ ] 10. Map to CloudEvents types
- [ ] 11. Deliver the discovery catalog
```

### Step 1: Read Directives and Scope

1. Read `.ahrena/.directives` to obtain `language.default`
2. Confirm the domain/feature description, the Bounded Context name (PascalCase), and the CloudEvents module are provided. If insufficient, **ask the user** (what is the main business process? who are the actors? what is the system boundary? what triggers the first action?) and wait for answers
3. Check whether `docs/{context}/events/events.md` already exists — incorporate it as input if available
4. Identify the bounded context scope: single or multiple contexts

### Step 2: Consult Lexis and Codex

1. Consult **lex-cloudevents** — events MUST follow CloudEvents spec; type format `event.guardia.{module}.{entity_type}.{event_name}`
2. Consult **codex-cloudevents** — event structure: id, source, specversion, type, time, subject, idempotencykey, data; size < 12KB
3. Consult **lex-entities** and **codex-entities** — entity fields in `data` (entity_id, entity_type, version, created_at, updated_at; history omitted)
4. Consult **lex-idempotency** — events MUST carry idempotencykey; consumers MUST deduplicate

### Step 3: Identify Domain Events (Timeline)

Domain events are **things that happened** in the domain — stated in the past tense, from the business perspective:

1. Ask the user: "Walk me through the business process step by step. What happens first, and what follows?" — or infer from the description when the flow is clear
2. List all domain events in **chronological order** (e.g., `ScheduledTransferRequested`, `ScheduledTransferApproved`, `ScheduledTransferExecuted`, `ScheduledTransferFailed`)
3. For each event, capture:
   - **Name** — past tense, PascalCase noun phrase (e.g., `ScheduledTransferExecuted`)
   - **When it occurs** — business trigger (e.g., "after the accountant submits the transfer form")
   - **Entity it relates to** — the aggregate affected
4. Identify **gaps** in the timeline — events that must logically exist between two others but are not yet named
5. Mark contested or uncertain events as hotspots (see Step 8)

### Step 4: Identify Commands and Actors

Commands are **intentions that trigger events** — stated in the imperative, representing something a user or system wants to happen:

1. For each domain event, ask: "What triggered this? Who or what issued the command?"
2. Identify the **actor**: user role, internal system, external system, timer/scheduler, or policy (automatic reaction)
3. Document the chain: `[Actor] → [Command] → [Domain Event]`
   - e.g., `Accountant → RequestScheduledTransfer → ScheduledTransferRequested`
   - e.g., `Scheduler → ExecuteScheduledTransfer → ScheduledTransferExecuted`
4. Flag commands with no clear actor as hotspots

### Step 5: Identify Aggregates

Aggregates are **entities that handle commands and produce events** — they enforce business rules and maintain consistency:

1. Group related commands and events by the entity that processes them
2. Name each aggregate (singular noun, PascalCase, e.g., `ScheduledTransfer`, `LedgerEntry`, `ReconciliationRun`)
3. For each aggregate, document:
   - **Commands it accepts** — list of command names
   - **Events it produces** — list of domain event names
   - **Invariants** — business rules it enforces (e.g., "a transfer cannot be executed if the source balance is insufficient")
4. Identify aggregates referenced across multiple commands — potential candidates for a shared kernel or anti-corruption layer

### Step 6: Identify Policies (Automatic Reactions)

Policies are **automatic reactions** that fire in response to events: "When [Event], then [Command]":

1. For each domain event, ask: "Does this event automatically trigger anything else in the system?"
2. Document each policy: `When {DomainEvent} → Then {Command} (on {Aggregate})`
   - e.g., `When ScheduledTransferExecuted → Then PostLedgerEntry (on LedgerEntry)`
   - e.g., `When ReconciliationCompleted → Then NotifyAccountant (on Notification)`
3. Identify policies that **cross bounded contexts** — these become integration events and need explicit routing

### Step 7: Identify External Systems and Read Models

**External systems** — services outside this bounded context:

1. Name each system (e.g., `BankingPartner`, `FiscalAuthority`, `NotificationService`, `LedgerService`)
2. Identify whether each system **produces events** (inbound) or **receives commands** (outbound)
3. Document the integration point for each

**Read models** — data projections needed to support user decisions or views:

1. Name each read model (e.g., `ScheduledTransferHistoryView`, `ReconciliationDashboard`)
2. Identify which domain events feed each read model (projections)
3. Note the consumer of each view (user role, external report, Isac)

### Step 8: Mark Hotspots

Hotspots are **questions, uncertainties, conflicts, and risks** that need human resolution before implementation:

1. Document each hotspot with:
   - **Type** — `Question` (unclear rule or ownership) | `Conflict` (two valid interpretations) | `Gap` (missing event) | `Risk` (race condition, data loss, compliance)
   - **Description** — precise statement of the uncertainty
   - **Priority** — `P1` (blocks design, resolve before proceeding) | `P2` (resolve before implementation) | `P3` (can address in a follow-up)
   - **Owner** — team or person who should resolve it
2. Do not skip this step — unresolved hotspots are the primary source of integration bugs and scope creep

### Step 9: Identify Bounded Contexts

1. Group aggregates and events into **bounded contexts** — areas where terms have a consistent, shared meaning
2. Name each bounded context and describe its responsibility (e.g., `Payments`, `Reconciliation`, `FiscalReporting`)
3. Identify **context boundaries** — where domain events cross from one context to another (these become published integration events)
4. Map ownership: which team or service is responsible for each bounded context

### Step 10: Map to CloudEvents Types

Translate each domain event to Guardia's CloudEvents naming convention:

1. For each domain event, produce the CloudEvents `type`:
   - Format: `event.guardia.{module}.{entity_type}.{event_name}`
   - `entity_type` — snake_case entity name (e.g., `scheduled_transfer`, `reconciliation_run`)
   - `event_name` — snake_case past-tense verb (e.g., `created`, `approved`, `executed`, `failed`, `cancelled`)
2. For each type, define the initial `data` shape per codex-entities:
   - Required: `entity_id`, `entity_type`, key business fields relevant to consumers
   - Omit `history`; do not include PII unless strictly necessary
3. Mark integration events (crossing bounded contexts) — they require explicit `source` and `subject` values

### Step 11: Deliver the Discovery Catalog

The discovery **does not become a monolithic file**. The result is delivered as input to Phase 2 (`kata-events-doc`) and as notes that `warrior-prometheus` consolidates.

Internal structure to forward:

1. **Header** — domain, Bounded Context, CloudEvents module, date, scope
2. **Domain Events Timeline** — chronological list: name, trigger, entity
3. **Commands and Actors** — table: Actor | Command | Domain Event
4. **Aggregates** — one subsection per aggregate: commands accepted, events produced, invariants
5. **Policies** — table: When (Event) | Then (Command) | On (Aggregate)
6. **External Systems** — table: System | Direction (inbound/outbound) | Events / Commands
7. **Read Models** — table: View | Events that feed it | Consumer
8. **Hotspots** — table: Type | Description | Priority | Owner
9. **Bounded Contexts** — diagram or table: Context | Responsibility | Owner | Integration Events
10. **CloudEvents Catalog** — table: Domain Event | CloudEvents type | Initial data shape

Canonical persistence of the discovered events happens in Phase 2, at `docs/{context}/events/events.md`, via `kata-events-doc` + `kata-feature-design-docs`. Hotspots and supporting findings are published by Prometheus to Notion (Guardia Platform > Domain Models).

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| CloudEvents catalog | In-memory table | Direct input for `kata-events-doc` |
| Hotspot list | Table | Notes for `warrior-prometheus` to review and resolve |

## Execution Example

### Example Input

```
Domain: Scheduled transfers — accountants can schedule bank transfers to execute on a future date. A supervisor must approve before execution. The scheduler triggers execution at the scheduled time.
Module: platform
```

### Example Output (summary)

Discovery catalog delivered to Phase 2 (`kata-events-doc`):

**Timeline:** ScheduledTransferRequested → ScheduledTransferApproved → ScheduledTransferExecuted | ScheduledTransferFailed → ScheduledTransferCancelled

**Commands and actors:**
| Actor | Command | Domain Event |
|-------|---------|--------------|
| Accountant | RequestScheduledTransfer | ScheduledTransferRequested |
| Supervisor | ApproveScheduledTransfer | ScheduledTransferApproved |
| Scheduler | ExecuteScheduledTransfer | ScheduledTransferExecuted / ScheduledTransferFailed |
| Accountant | CancelScheduledTransfer | ScheduledTransferCancelled |

**Hotspots:**
| Type | Description | Priority | Owner |
|------|-------------|----------|-------|
| Question | What happens on execution failure: instant fail or retry? Retry policy undefined | P1 | Platform team |
| Risk | Race condition if supervisor approves while scheduler is already executing | P1 | Platform team |

**CloudEvents catalog:**
| Domain Event | CloudEvents type | data (key fields) |
|---|---|---|
| ScheduledTransferRequested | event.guardia.platform.scheduled_transfer.requested | entity_id, amount, currency, scheduled_date, requestor_id |
| ScheduledTransferApproved | event.guardia.platform.scheduled_transfer.approved | entity_id, approver_id, approved_at |
| ScheduledTransferExecuted | event.guardia.platform.scheduled_transfer.executed | entity_id, executed_at, ledger_entry_id |
| ScheduledTransferFailed | event.guardia.platform.scheduled_transfer.failed | entity_id, failure_reason, failed_at |
| ScheduledTransferCancelled | event.guardia.platform.scheduled_transfer.cancelled | entity_id, cancelled_by, cancelled_at |

## Constraints

- This Kata produces only the discovery catalog; it does not implement publishers, consumers, or API contracts
- Do not skip hotspot identification — every uncertainty left undocumented becomes a bug or scope gap
- The CloudEvents catalog produced here MUST be complete enough to run `kata-events-doc` without additional discovery; flag missing fields explicitly
- Escalate to a human when bounded context ownership is ambiguous or when a single event spans multiple aggregates with no clear owner
- Do not assume the event timeline is complete — actively probe for missing events at every gap in the causal chain

## References

- lex-cloudevents, lex-entities, lex-idempotency, lex-feature-design-docs
- codex-cloudevents, codex-entities, codex-idempotency, codex-feature-design-docs
- kata-events-doc — Phase 2 persistence
- kata-feature-design-docs — canonical persistence procedure
- [Event Storming — Alberto Brandolini](https://www.eventstorming.com/)
- [Domain-Driven Design Reference — Eric Evans](https://www.domainlanguage.com/ddd/reference/)
