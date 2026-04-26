# Lexis: AI-First Experience by Default

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Guardia platform and app (end-user interfaces)

## Purpose

Sustain the **agentic accounting** positioning. The user describes the result; Isac plans, executes, and reports. Recreating a classic SaaS architecture (sidebar of modules, static forms, permanent dashboards, chat as a floating accessory) inverts the agentic hierarchy and breaks the product.

## Law

> **Every interface used by humans on the Guardia platform and app MUST adopt the AI-First pattern: conversation with Isac as the primary surface, live workspace reactive to dialog, real-time reasoning transparency (plan, sources, decisions), graduated control (pause, intervene, approve), and native auditability. Building primary architecture as a sidebar of feature modules, blocking modals before conversation, permanent dashboards for the user to monitor, or hiding what the agent is doing behind generic loaders is FORBIDDEN.**

## Coverage

- **Applies to:** web platform, mobile app, internal screens with significant human interaction.
- **Bound agents:** product designers, frontend, mobile, AI agents that produce UI code (warrior-hephaestus, warrior-iris).
- **Exceptions:** purely operational views without users (e.g., low-volume admin/superuser screens), transactional emails, and static marketing pages. Every exception in the main product requires a Notion proposal, justification, and approval by the CEO or designated Brand owner.

## Consequences of Violation

1. **Positioning:** the "agentic accounting" brand loses traction; the product becomes "yet another SaaS."
2. **Auditability:** agent actions without visible traces prevent the user from validating or learning.
3. **Remediation:** redo the screen architecture with conversation + workspace; move features into capabilities invoked by conversation; add plan, sources, and controls before resuming the release.

## Examples

### Correct

Home screen = chat with Isac in the foreground; workspace renders, in real time, sources consulted and artifacts (tables, charts, documents) as conversational responses; irreversible actions (sending, posting an entry, releasing value) are explicit confirmation points; the user can pause, edit the plan, or approve sensitive steps.

### Incorrect

Home screen with a sidebar (Reconciliation, Reports, Rules, Integrations) and Isac as a floating button; a 12-field form to create a reconciliation rule instead of a natural-language description; generic loaders without plan or source detail; final response reduced to "Done. 127 transactions reconciled." without trace.

## Automated Validation

- **Tooling:** design review (warrior-hephaestus + human Brand reviewer) with agentic checklist; E2E tests confirming every critical journey starts from conversation; periodic navigation-tree audit.
- **Timing:** design review (pre-implementation), UI PR review, quarterly product audit.
- **Metric:** 0 main screens with feature sidebar as primary architecture; 100% of irreversible actions with explicit confirmation; complete plan/source trace on 100% of Isac executions visible to the user.

## References

- [codex-ai-first-experience](../codex/codex-ai-first-experience.md)
- [codex-design-system](../codex/codex-design-system.md)
- Notion — Design System / AI-First Experience
