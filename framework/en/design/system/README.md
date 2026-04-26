# design/system — Guardia Design System

Brand Kit execution layer in product. Covers mandatory consumption of `@guardia/design-system`, component patterns, and the AI-First agentic UX directive.

## Specifications (Lexis and Codex)

| Topic | Lexis | Codex |
|-------|-------|-------|
| Design System (overview, governance, stack) | — | [codex-design-system](codex/codex-design-system.md) |
| Mandatory library | [lex-design-system-library](lexis/lex-design-system-library.md) | [codex-design-system-components](codex/codex-design-system-components.md) |
| AI-First Experience | [lex-ai-first-experience](lexis/lex-ai-first-experience.md) | [codex-ai-first-experience](codex/codex-ai-first-experience.md) |

## Notes

- **Mandatory consumption:** all Guardia UI MUST use `@guardia/design-system`. Reimplementing primitives or using hardcoded color/typography values is forbidden.
- **AI-First by default:** platform and app adopt the *conversation + live workspace* pattern with Isac at the center. Module sidebar as primary architecture is forbidden.
- Implementation sources: Notion (intent) → Code `@guardia/design-system` (truth) → Chromatic (visual catalog) → Figma (mirrored design).
