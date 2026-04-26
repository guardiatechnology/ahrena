# design — Identidade da Marca e Design System

Clade que cobre a identidade visual e verbal da Guardia (Brand Kit) e a camada de execução em produto (Design System). Espelha a estrutura *Branding* do Notion e codifica as regras como Lexis (leis inquebráveis) e Codex (manuais de referência) para uso por humanos e agentes de IA.

## Subclades

| Subclade | Foco | README |
|----------|------|--------|
| **brand** | Identidade da marca: essência, cores, tipografia, voz, logos | [brand/README.md](brand/README.md) |
| **system** | Camada de execução: Design System, componentes via `@guardia/design-system`, AI-First Experience | [system/README.md](system/README.md) |

## Notas

- Notion é a fonte da verdade conceitual (intenção, regras, governança).
- Implementação técnica vive em `@guardia/design-system` (catálogo visual em Chromatic; espelho de design em Figma).
- Divergências entre Notion, código e Figma são tratadas como bug — corrige na origem e propaga.
