# design — Identidad de la Marca y Design System

Clade que cubre la identidad visual y verbal de Guardia (Brand Kit) y la capa de ejecución en producto (Design System). Refleja la estructura *Branding* en Notion y codifica las reglas como Lexis (leyes inquebrantables) y Codex (manuales de referencia) para uso por humanos y agentes de IA.

## Subclades

| Subclade | Foco | README |
|----------|------|--------|
| **brand** | Identidad de la marca: esencia, colores, tipografía, voz, logos | [brand/README.md](brand/README.md) |
| **system** | Capa de ejecución: Design System, componentes vía `@guardia/design-system`, AI-First Experience | [system/README.md](system/README.md) |

## Notas

- Notion es la fuente de verdad conceptual (intención, reglas, gobernanza).
- La implementación técnica vive en `@guardia/design-system` (catálogo visual en Chromatic; espejo de diseño en Figma).
- Las divergencias entre Notion, código y Figma se tratan como bug — corrige en el origen y propaga.
