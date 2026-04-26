# Codex: Guardia Design System

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Brand Kit execution layer at any interface or material

## Content

### Relationship with the Brand Kit

| Brand Kit | Design System |
|-----------|---------------|
| Logo and Logotypes | How logos appear in interfaces, materials, and signatures |
| Colors | Tokens applied to components, states, and data categories |
| Typography | Hierarchical scales in buttons, cards, tables, and dashboards |
| Brand voice | Microcopy, labels, error and confirmation messages |
| Photography | Image treatment in banners, cards, and promotional materials |

Coherence between identity and execution is what makes the brand **recognizable**, not just pretty.

### Scope

| Area | Content |
|------|---------|
| AI-First Experience | Structural agentic UX guideline: primary conversation, live workspace, transparency, graduated control |
| Components | Reusable patterns (buttons, cards, alerts, forms, badges, content blocks) |
| Graphic elements | Textures, patterns, auxiliary shapes, decorative resources |
| Icons | Symbol library for actions, navigation, states, categories |
| Charts | Patterns for data viz, dashboards, and infographics |

### Where it applies

1. **Platform** — reconciliation screens, dashboards, operational flows, reports.
2. **Site and commercial materials** — landing pages, one-pagers, decks, proposals.
3. **App** — mobile interfaces with density and touch adaptations.
4. **Messaging channels** — WhatsApp, Telegram, Slack (stickers, interactive cards, templates).
5. **Technical documents** — contracts, operational reports, formal communications.

Adaptations are allowed in dimension and density. **Identity never changes.**

### Principles

1. **AI-First by default.** Agentic experience; Isac is the center of interaction. Features are agent capabilities, not navigation destinations. Details in [codex-ai-first-experience](codex-ai-first-experience.md).
2. **Token before raw value.** Components consume tokens (color, typography, spacing), never hardcoded values. Token change propagates across the system.
3. **Composition over customization.** Combine existing components before creating new ones. Customization breeds divergence; divergence breeds rework.
4. **Accessibility is a requirement.** WCAG 2.1 AA is the floor, not the goal. Focus, screen reader, and keyboard are part of the component.
5. **Density serves context.** Dense dashboards and roomy forms coexist; what changes is the application of spacing tokens.
6. **Document the exception.** Every deviation needs recorded justification (feeds system evolution).

### Reference sources

| Source | What lives there |
|--------|------------------|
| Notion | Intent, usage rules, principles, governance (conceptual source) |
| Code (`@guardia/design-system`) | Official implementation — source of truth for behavior |
| Chromatic | Versioned visual catalog (every state of every component) |
| Figma | Design library with mirrored variants and tokens |

**Divergences are treated as bugs.** The fix starts at the origin and propagates to the other points.

### Implementation stack

- **Components:** [shadcn/ui](https://ui.shadcn.com/) as base, [Tailwind CSS](https://tailwindcss.com/) for styling, [CopilotKit](https://www.copilotkit.ai/) for agentic interactions. Currently Tailwind v3; v4 migration conditional on compatibility.
- **Icons:** [Lucide](https://lucide.dev/).
- **Charts:** [shadcn/ui Charts](https://ui.shadcn.com/charts), respecting the data viz color schema.
- **Distribution:** `@guardia/design-system` library (mandatory consumption, see [lex-design-system-library](../lexis/lex-design-system-library.md)).

### Governance

Proposals for new components, patterns, icons, or chart types go through the governance flow. Before creating something new, verify whether the problem is already solved by an existing pattern. Real gaps become issues in the `@guardia/design-system` repository with context, use case, and proposal.

The system evolves with use. Every asset must withstand the question: **will this be reused, or is it case-specific?**

### Useful links

- Repository: [github.com/guardiatechnology/design-system](https://github.com/guardiatechnology/design-system) (under review)
- Chromatic catalog: [69e15f3b0534f646ac88774b-cpmytvatdp.chromatic.com](https://69e15f3b0534f646ac88774b-cpmytvatdp.chromatic.com/) (under review)
- Chromatic library: [chromatic.com/library?appId=69e15f3b0534f646ac88774b](https://www.chromatic.com/library?appId=69e15f3b0534f646ac88774b)
- Figma: [figma.com/design/F0TkqO6HigGa3C0P8XK9zL/Design-System](https://www.figma.com/design/F0TkqO6HigGa3C0P8XK9zL/Design-System) (deprioritized)
