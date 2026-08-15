# Lexis: Acessibilidade em Frontend (WCAG 2.1 AA)

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Acessibilidade em todas as interfaces web produzidas pela aplicação frontend

## Lei

> **Toda UI produzida DEVE atender ao WCAG 2.1 nível AA como mínimo. Elementos interativos DEVEM ser alcançáveis e operáveis por teclado. Imagens e ícones com significado DEVEM ter texto alternativo. Formulários DEVEM ter labels associadas. Cores DEVEM atender contraste 4.5:1 para texto normal e 3:1 para texto grande. Estado dinâmico DEVE ser anunciado a tecnologias assistivas.**

## Regras

### 1. HTML semântico

O agente **DEVE**:

1. Usar elementos nativos: `<button>`, `<a>`, `<nav>`, `<main>`, `<header>`, `<footer>`, `<article>`, `<section>`.
2. Não reinventar: um `<div onClick={...}>` com role e tabindex é pior do que um `<button>`.
3. Usar heading hierarchy correta: `h1` único por página, `h2` para seções, `h3` aninhado a `h2`, etc.

### 2. Navegação por teclado

Todo elemento interativo **DEVE**:

1. Ser alcançável via `Tab` (ordem lógica).
2. Ser ativável via `Enter` (links) ou `Space` (botões, checkboxes).
3. Ter foco visível (não remover `:focus-visible` do CSS).
4. Suportar `Esc` para fechar modais, dropdowns, drawers.
5. Suportar `Arrow` keys em listas, menus, tabs, radio groups (conforme ARIA Authoring Practices).

### 3. Imagens e mídia

1. **Toda `<img>`** com significado **DEVE** ter `alt` descritivo.
2. **Imagens decorativas** usam `alt=""` (explícito, não omitido).
3. **Ícones que são botões** usam `aria-label` ou texto visualmente oculto (`.sr-only`).
4. **Vídeos** devem ter legendas; **áudios** devem ter transcrição.

### 4. Formulários

1. **Todo `<input>`, `<textarea>`, `<select>`** **DEVE** ter `<label>` associada via `htmlFor` ou aninhamento.
2. **Campos obrigatórios** marcados com `required` e indicação visual + `aria-required="true"`.
3. **Erros de validação** expostos via `aria-invalid="true"` + mensagem em `aria-describedby`.
4. **Agrupamentos** usam `<fieldset>` + `<legend>`.

### 5. Contraste e cores

1. **Texto normal (≤18px)**: contraste mínimo 4.5:1 contra o fundo.
2. **Texto grande (≥18px bold ou ≥24px regular)**: contraste mínimo 3:1.
3. **Ícones e elementos gráficos**: contraste mínimo 3:1.
4. **Cor nunca é o único indicador** de estado (ex.: erro vermelho também tem ícone + texto).
5. Testar com ferramentas automatizadas (axe, Lighthouse) e manualmente em modo "daltonismo".

### 6. Conteúdo dinâmico

1. **Carregamento assíncrono** usa `aria-busy="true"` ou `role="status"` para indicar estado.
2. **Mensagens flash (toasts, alerts)** usam `role="alert"` (assertive) ou `role="status"` (polite).
3. **Modais** são focus-trapped e retornam o foco ao elemento que os abriu; usam `aria-modal="true"` e `role="dialog"`.
4. **Rotas SPA** movem o foco para o conteúdo novo após navegação.

### 7. Idioma e ordem de leitura

1. **`<html lang="pt-BR">`** (ou o idioma padrão do projeto).
2. **Conteúdo em outro idioma** usa `lang="en"` no elemento pai.
3. **Ordem de leitura** no DOM reflete a ordem visual (sem `order` em flex/grid quebrando fluxo lógico).

## Validação Automatizada

- **Ferramenta:**
  - `eslint-plugin-jsx-a11y` (lint)
  - `@axe-core/react` ou `jest-axe` (testes)
  - Lighthouse accessibility audit (CI)
  - Playwright/Cypress + axe-core (E2E)
- **Momento:** cada PR; checagem manual com leitor de tela a cada release significativa
- **Métrica:** 0 violações WCAG AA automaticamente detectáveis
