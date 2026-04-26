# Codex: AI-First Experience — Conversation + Workspace Pattern

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Agentic UX of the Guardia platform and app

## Content

### Principles

1. **Conversation as primary interface.** The main surface is dialogue with Isac. Screens, panels, and visualizations are born as agent responses or context invoked by conversation — not as navigation destinations.
2. **Intent over functionality.** The user expresses the desired result (reconcile, investigate, approve). Isac decides tools, sources, and steps. The UI does not expose isolated features expecting the user to combine them.
3. **Reasoning transparency.** Every execution is observable in real time (plan, steps, sources consulted, decisions made). Nothing happens in a black box.
4. **Graduated control.** The user can pause, intervene, correct, or take over any step. Isac's autonomy is an adjustable spectrum, not a switch.
5. **Artifacts on demand.** Tables, charts, reports, and dashboards are generated when they serve the decision at hand. No artifact lives as a permanent menu waiting for the user to open.
6. **Native auditability.** Each action generates a versioned trail (input, context, decision, result). The interface gives direct access to that history.
7. **Structured memory.** Operation context (clients, ongoing reconciliations, rules, preferences) is externalized and retrieved by the agent, not stacked into screen state.

### Layout pattern

Conversation + live workspace, aligned with market references (Anthropic's Claude and Meta's Manus AI).

| Region | Function | Content |
|--------|----------|---------|
| Left (or top on mobile) | Conversation with Isac | Primary input, session history, execution plan, status |
| Right (or bottom on mobile) | Dynamic workspace | Renders what Isac is consulting or producing (transaction table, reconciliation view, document, panel, external source) |

The workspace is **reactive to the dialogue**. When the conversation shifts context, the workspace follows. The user does not navigate to find a screen.

### Usage rules

#### Do

- Always start from user intent and let Isac decompose into steps.
- Show the plan before execution when the task has relevant impact (write, approve, external send).
- Show consulted sources and data used in each decision.
- Allow editing the plan, blocking steps, or approving sensitive steps before execution.
- Generate artifacts as outcomes of agentic work, with direct link to the originating context.
- Preserve long-term memory off-screen (files, persisted state, preferences), invoked when relevant.
- Treat irreversible actions (sending a message, posting an entry, releasing value) as explicit confirmation points.

#### Don't

- Build sidebars with stacked features (Reconciliation, Reports, Settings) as primary architecture. Features are Isac's capabilities, not destinations.
- Open modals or wizards forcing the user to fill fields before conversing.
- Hide what the agent is doing (generic loaders or "processing..." without detail).
- Duplicate the same data in multiple static screens. If it is relevant, Isac brings it when needed.
- Create permanent dashboards the user must monitor. Dashboards are materialized on demand or rule-triggered.
- Delegate orchestration between tools to the user. If two capabilities need to be combined, Isac combines them.
- Treat autonomy as binary (manual or automatic). There must be configurable levels per task type and user profile.

### Examples

#### Correct — reconciliation

User: *"Reconcile yesterday's Cielo settlements and let me know what's still open."*

- Isac shows the plan: fetch bank statement → fetch Cielo EDI file → apply matching rules → list mismatches.
- Workspace shows, in real time, each source being consulted and lines being reconciled.
- Result appears as an artifact (mismatch table) with per-line justification.
- The user can click any mismatch, ask why it didn't match, and Isac responds with full trace.

#### Correct — investigation

User: *"I want to understand why client X's Pix flow is noisy."*

- Isac proposes investigation (periods, counterparties, value patterns).
- Workspace renders requested cuts progressively.
- No pre-built report is opened. Everything is generated for that specific question.

#### Incorrect — module sidebar

Home screen with sidebar (Reconciliation, Reports, Rules, Integrations) and Isac chat as a floating button in the corner.
**Reason:** inverts hierarchy. Isac becomes a classic SaaS accessory. The user goes back to operating modules instead of delegating intent.

#### Incorrect — invisible action

Isac runs a reconciliation in the background and returns only "Done. 127 transactions reconciled."
**Reason:** breaks transparency and auditability. The user has no way to validate or learn.

#### Incorrect — long form

A 12-required-field form to create a reconciliation rule.
**Reason:** the user should describe the rule in natural language to Isac, who structures, validates, and confirms before persisting.

### Design System implications

- **Priority components:** chat bubbles, execution-plan blocks, step trace, consulted-source cards, inline-renderable artifacts (table, chart, document), and approval/intervention controls. These live in `@guardia/design-system` under the "Agentic" family (`ChatPanel`, `Workspace`, `PlanTrace`, `SourceCard`, `ApprovalGate`).
- **Navigation:** minimal. Session history, user memory, and settings. No feature tree.
- **Loading states:** replaced by *streaming* of reasoning and plan progress.
- **Tokens and visual patterns:** follow the Brand Kit; Figma translates into product components with parity between design and code.

### External references

Claude (Anthropic) and Manus AI (Meta) as benchmarks of the agentic pattern. The directive rests on the emerging consensus that the dominant layout for agents combines **persistent conversation + live workspace**, prioritizing transparency over visual polish.

### Governance

Any exception (screen with traditional architecture, feature without an agentic entry) requires a formal Notion proposal, with justification, and approval from the CEO or designated Brand owner. Exceptions feed system evolution; they do not become rules by omission.
