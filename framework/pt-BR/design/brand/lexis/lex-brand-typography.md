# Lexis: Tipografia Oficial — Poppins, Lastica e Roboto

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Comunicação tipográfica da Guardia em qualquer canal

## Propósito

Sustentar coerência tipográfica. A Lastica é proprietária da assinatura da marca; a Poppins é a tipografia corrente; a Roboto é o fallback nativo para ambientes com restrição de fontes. Misturar fontes ad hoc, ou usar Lastica em corpos de texto, dilui a identidade e quebra hierarquia.

## Lei

> **A Guardia DEVE usar Poppins como tipografia corrente em toda comunicação (documentos, decks, propostas, materiais internos, web, app, redes sociais), com hierarquia padronizada (H1 Bold/SemiBold, H2 SemiBold, H3/H4 Medium, corpo Regular, apoio Light, ênfase Itálico ou SemiBold). A Lastica é EXCLUSIVA dos logotipos oficiais e da assinatura da marca — é PROIBIDO usá-la em corpo de texto, títulos editoriais ou peças que não sejam logotipo. A Roboto é o ÚNICO fallback aceito quando Poppins não estiver disponível, declarado em CSS como `font-family: 'Poppins', 'Roboto', sans-serif;`. Outras fontes (Inter, Montserrat, Helvetica, Arial, Lato, Open Sans, etc.) são PROIBIDAS, salvo exceções documentadas em ADR.**

## Abrangência

- **Aplica-se a:** UI (web, mobile, e-mail), decks, documentos, propostas, contratos, posts em redes sociais, blog, eventos, ícones com texto.
- **Agentes vinculados:** designers, frontend, mobile, marketing, comercial, agentes de IA que gerem peças com texto.
- **Exceções:** uso técnico de tipografia monoespaçada em snippets de código (livre escolha entre fontes mono populares: JetBrains Mono, Fira Code, Menlo); logos de parceiros (mantêm sua tipografia original).

## Consequências de Violação

1. **Identidade:** mistura de fontes corrói o reconhecimento e a sensação de cuidado da marca.
2. **Hierarquia:** ausência de hierarquia padronizada fragiliza leitura em decks, dashboards e materiais densos.
3. **Remediação:** substituir pela Poppins (ou Roboto em fallback); reservar Lastica aos arquivos oficiais de logotipo; refatorar tokens tipográficos em `@guardia/design-system` quando a violação ocorrer em código.

## Exemplos

### Correto

Slide com H1 Poppins Bold 700, corpo em Poppins Regular 400, citação em Poppins Italic; landing page com `font-family: 'Poppins', 'Roboto', sans-serif`; assinatura de e-mail em Poppins (texto) + arquivo oficial do logotipo em Lastica (imagem); contrato em Poppins com hierarquia Medium 500 para subtítulos.

### Incorreto

Bloco de texto em Lastica (fonte é exclusiva do logo); título em Inter ou Montserrat porque "ficou bonito"; deck comercial misturando Helvetica e Roboto; CSS sem fallback explícito (`font-family: 'Poppins', sans-serif`).

## Validação Automatizada

- **Ferramenta:** Stylelint regra `font-family-no-missing-generic-family-keyword` + lista permitida (Poppins, Roboto + monoespaçada); revisão de design (warrior-hephaestus) detectando uso de Lastica fora dos arquivos oficiais; tokens tipográficos centralizados em `@guardia/design-system`.
- **Momento:** pre-commit, CI de UI, revisão de PR para materiais não-UI.
- **Métrica:** 0 declarações `font-family` com fontes fora da lista permitida; 0 ocorrências de Lastica em corpo de texto; 100% das declarações CSS com fallback `'Poppins', 'Roboto', sans-serif`.

## Referências

- [codex-brand-typography](../codex/codex-brand-typography.md)
- Poppins (Google Fonts, SIL OFL); Roboto (Apache 2.0); Lastica (proprietária, Alberto Fontense)
- Notion — Branding / Tipografia
