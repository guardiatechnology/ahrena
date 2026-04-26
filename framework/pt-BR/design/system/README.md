# design/system — Design System da Guardia

Camada de execução do Brand Kit em produto. Cobre o consumo obrigatório de `@guardia/design-system`, padrões de componentes e a diretriz de UX agêntica AI-First.

## Especificações (Lexis e Codex)

| Tema | Lexis | Codex |
|------|-------|-------|
| Design System (visão geral, governança, stack) | — | [codex-design-system](codex/codex-design-system.md) |
| Biblioteca obrigatória | [lex-design-system-library](lexis/lex-design-system-library.md) | [codex-design-system-components](codex/codex-design-system-components.md) |
| AI-First Experience | [lex-ai-first-experience](lexis/lex-ai-first-experience.md) | [codex-ai-first-experience](codex/codex-ai-first-experience.md) |

## Notas

- **Consumo obrigatório:** toda UI da Guardia DEVE usar `@guardia/design-system`. Reimplementar primitivos ou usar valores cromáticos/tipográficos hardcoded é proibido.
- **AI-First por padrão:** plataforma e app adotam o padrão *conversa + workspace ao vivo* com o Isac no centro. Sidebar de módulos como arquitetura primária é proibida.
- Fontes da implementação: Notion (intenção) → Código `@guardia/design-system` (verdade) → Chromatic (catálogo visual) → Figma (design espelhado).
