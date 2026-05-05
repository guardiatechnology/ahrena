---
paths:
  - "**/*.tsx"
  - "**/*.jsx"
  - "**/*.ts"
  - "**/*.js"
  - "**/*.vue"
  - "**/*.svelte"
  - "**/*.html"
  - "**/*.css"
  - "**/*.scss"
  - "**/*.sass"
  - "**/*.less"
  - "**/*.styl"
  - "**/*.pcss"
---

# Lexis: AI-First Experience by Default

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Guardia platform and app (end-user interfaces)

## Law

> **Every interface used by humans on the Guardia platform and app MUST adopt the AI-First pattern: conversation with Isac as the primary surface, live workspace reactive to dialog, real-time reasoning transparency (plan, sources, decisions), graduated control (pause, intervene, approve), and native auditability. Building primary architecture as a sidebar of feature modules, blocking modals before conversation, permanent dashboards for the user to monitor, or hiding what the agent is doing behind generic loaders is FORBIDDEN.**

## Coverage

- **Applies to:** web platform, mobile app, internal screens with significant human interaction.
- **Bound agents:** product designers, frontend, mobile, AI agents that produce UI code (warrior-hephaestus, warrior-iris).
- **Exceptions:** purely operational views without users (e.g., low-volume admin/superuser screens), transactional emails, and static marketing pages. Every exception in the main product requires a Notion proposal, justification, and approval by the CEO or designated Brand owner.

## Examples

### Correct

Home screen = chat with Isac in the foreground; workspace renders, in real time, sources consulted and artifacts (tables, charts, documents) as conversational responses; irreversible actions (sending, posting an entry, releasing value) are explicit confirmation points; the user can pause, edit the plan, or approve sensitive steps.

### Incorrect

Home screen with a sidebar (Reconciliation, Reports, Rules, Integrations) and Isac as a floating button; a 12-field form to create a reconciliation rule instead of a natural-language description; generic loaders without plan or source detail; final response reduced to "Done. 127 transactions reconciled." without trace.

## Automated Validation

- **Tooling:** design review (warrior-hephaestus + human Brand reviewer) with agentic checklist; E2E tests confirming every critical journey starts from conversation; periodic navigation-tree audit.
- **Timing:** design review (pre-implementation), UI PR review, quarterly product audit.
- **Metric:** 0 main screens with feature sidebar as primary architecture; 100% of irreversible actions with explicit confirmation; complete plan/source trace on 100% of Isac executions visible to the user.
