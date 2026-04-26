# design — Brand Identity and Design System

Clade covering Guardia's visual and verbal identity (Brand Kit) and the product execution layer (Design System). It mirrors the *Branding* structure from Notion and codifies rules as Lexis (unbreakable laws) and Codex (reference manuals) for use by humans and AI agents.

## Subclades

| Subclade | Focus | README |
|----------|-------|--------|
| **brand** | Brand identity: essence, colors, typography, voice, logos | [brand/README.md](brand/README.md) |
| **system** | Execution layer: Design System, components via `@guardia/design-system`, AI-First Experience | [system/README.md](system/README.md) |

## Notes

- Notion is the conceptual source of truth (intent, rules, governance).
- Technical implementation lives in `@guardia/design-system` (visual catalog in Chromatic; design mirror in Figma).
- Divergences between Notion, code, and Figma are treated as bugs — fix at origin and propagate.
