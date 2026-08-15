# Codex: Domain-Driven Design

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Strategic and tactical modeling of complex domains

## Overview

This Codex guides Domain-Driven Design decisions without reducing DDD to a folder layout or mandatory pattern catalog. Start with language, boundaries, ownership, and invariants; introduce tactical patterns only when complexity justifies them.

## Context

- **Domain:** bounded-context, model, and integration design
- **Audience:** engineering, product, domain experts, and design agents
- **Update:** when component architecture, entity taxonomy, or event contracts change

## Content

### Principles

1. **Strategic before tactical:** Ubiquitous Language, subdomains, bounded contexts, and the Context Map precede Aggregate, Repository, or Domain Service.
2. **Local model:** the same term may have different models across contexts; explicit translation protects each language.
3. **Aggregate by invariant:** the boundary guarantees transactional consistency, not table or object-tree similarity.
4. **Earn complexity:** simple CRUD does not need to imitate a rich domain; evolve when rules and conflicts emerge.
5. **Semantic events:** a Domain Event records an internal fact; an Integration Event is a published contract and may require an outbox, versioning, and data policy.

### Decision Sequence

| Gate | Question | Expected evidence |
|---|---|---|
| Language | Are terms and meaning conflicts explicit? | Glossary and domain-approved examples |
| Boundary | Who decides and owns data and rules? | Bounded context and owners |
| Relationship | How do contexts depend on and translate models? | Context Map and published contract |
| Consistency | Which rules must hold in the same commit? | Invariants and Aggregate boundary |
| Persistence | Which concurrency and failure modes matter? | Unit of work, version, and retry policy |
| Integration | Which fact may leave and with what guarantee? | Versioned event, outbox/inbox, and idempotency as needed |

### Tactical Patterns — When Not to Use Them

| Pattern | Use when | Avoid when |
|---|---|---|
| Entity | Identity and lifecycle matter | Value is defined only by attributes |
| Value Object | Immutable concept with invariants | It is only an unstructured data bag |
| Aggregate | Invariants require joint consistency | Objects only need query/join behavior |
| Repository | Domain needs an abstract collection | A direct CRUD handler is sufficient and clear |
| Domain Service | Domain rule fits no Entity/VO | It is only IO orchestration |
| CQRS | Read and write models have proven different pressures | Ordinary CRUD without demonstrated asymmetry |
| Event Sourcing | History is the primary model and operations can support it | A simple audit log is sufficient |

### Operational Boundaries

- A local transaction does not span HTTP, queues, or external providers.
- An uncertain commit requires reconciliation; blind retries may duplicate financial effects.
- Eventual consistency declares a window, lag indicator, reprocessing path, and owner.
- External integrations use an Adapter/ACL when vocabularies differ.

### Current Decisions

| Decision | Status | Consequence |
|---|---|---|
| DDD-first begins with domain understanding | Confirmed | The document is not an Aggregate form |
| Physical layout is guidance, not the definition of DDD | Confirmed | Structural validators do not replace semantic review |
| Queryable patterns dictionary | Ahrena v2 proposal | This Codex supplies criteria the catalog must preserve |

### Technical Constraints

- Do not derive bounded contexts directly from tables, teams, or endpoints without language and ownership evidence.
- Do not allow external direct access to Aggregate internals.
- Do not confuse Domain Events with Integration Events or publish sensitive data for convenience.
- Do not impose one layering or folder structure on every stack.

## Glossary

| Term | Definition |
|---|---|
| Bounded Context | Boundary in which a language and model have consistent meaning |
| Invariant | Rule that must remain true during a state change |
| Context Map | Relationships and dependency direction among bounded contexts |
| Hotspot | Ambiguity or conflict that requires further discovery |

## References

- `kata-domain-model`, `codex-component-architecture`, `codex-feature-design-docs`
- `lex-entities`, `lex-entity-naming`, `lex-cloudevents`, `lex-idempotency`
