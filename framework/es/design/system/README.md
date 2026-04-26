# design/system — Design System de Guardia

Capa de ejecución del Brand Kit en producto. Cubre el consumo obligatorio de `@guardia/design-system`, patrones de componentes y la directriz de UX agéntica AI-First.

## Especificaciones (Lexis y Codex)

| Tema | Lexis | Codex |
|------|-------|-------|
| Design System (visión general, gobernanza, stack) | — | [codex-design-system](codex/codex-design-system.md) |
| Biblioteca obligatoria | [lex-design-system-library](lexis/lex-design-system-library.md) | [codex-design-system-components](codex/codex-design-system-components.md) |
| AI-First Experience | [lex-ai-first-experience](lexis/lex-ai-first-experience.md) | [codex-ai-first-experience](codex/codex-ai-first-experience.md) |

## Notas

- **Consumo obligatorio:** toda UI de Guardia DEBE usar `@guardia/design-system`. Reimplementar primitivos o usar valores cromáticos/tipográficos hardcodeados está prohibido.
- **AI-First por defecto:** la plataforma y la app adoptan el patrón *conversación + workspace en vivo* con Isac al centro. La sidebar de módulos como arquitectura primaria está prohibida.
- Fuentes de implementación: Notion (intención) → Código `@guardia/design-system` (verdad) → Chromatic (catálogo visual) → Figma (diseño reflejado).
