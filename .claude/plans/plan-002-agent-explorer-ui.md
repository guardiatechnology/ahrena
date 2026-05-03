---
plan_id: "002"
title: "agent-explorer-ui"
status: pending
agent: claude
created_at: "2026-05-03T00:00:00Z"
updated_at: "2026-05-03T00:00:00Z"
---

# Plan: Agent Explorer — UI

## Objetivo

Especificar layout, componentes, estados, interações e tokens CSS da interface do painel lateral
antes de qualquer implementação de webview.

---

## Layout Geral

```
┌─ Sidebar panel ─────────────────────────────────┐
│ AGENT EXPLORER                           ⟳       │  ← header VS Code nativo
├─────────────────────────────────────────────────┤
│ 🔍 Search artifacts...                          │  ← search bar
├─────────────────────────────────────────────────┤
│ [All] [Ahrena] [Claude] [Cursor]                │  ← platform chips (só detectados)
├─────────────────────────────────────────────────┤
│ ▼ Lex  ··· 58                                   │  ← section header (expandido)
│  ┌─────────────────────────────────────────┐    │
│  │ 📋  lex-python-error-handling           │    │  ← card
│  │     Bare except: are FORBIDDEN…         │    │
│  │     [Ahrena] [Claude]                   │    │
│  └─────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────┐    │
│  │ 📋  lex-entities                        │    │
│  │     Every persistent entity MUST…       │    │
│  │     [Ahrena] [Claude] [Cursor]          │    │
│  └─────────────────────────────────────────┘    │
│ ▶ Codex  ··· 35                                 │  ← colapsado
│ ▼ Katas  ··· 55                                 │
│  ┌─────────────────────────────────────────┐    │
│  │ ⚡  kata-python-implement               │    │
│  │     Implement Python code following…    │    │
│  │     [Ahrena] [Claude]                   │    │
│  └─────────────────────────────────────────┘    │
│ ▶ Warriors  ··· 14                              │
│ ▶ Cries  ··· 30                                 │
│ ▶ Tools  ··· 0                                  │
│ ▼ MCPs  ··· 1                                   │
│  ┌─────────────────────────────────────────┐    │
│  │ 🔌  github                              │    │
│  │     https://api.githubcopilot.com/mcp/  │    │
│  │     [Cursor]                            │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

---

## Componentes

### Search Bar

- `<input type="search">`, largura 100%, padding `6px 8px`, border-radius `4px`
- Ícone de lupa inline à esquerda (SVG 14px)
- Filtra `data-name` + `data-desc` de todos os cards (case-insensitive, client-side)
- Botão `×` aparece quando há texto; clique limpa e remove filtro
- Seção com todos os cards `hidden` colapsa e mostra count `(0)`

### Platform Chips

- Pills horizontais: `All` + uma pill por plataforma detectada
- **Seleção exclusiva**: clicar numa substitui o filtro atual; clicar na ativa = volta para `All`
- Pill **ativa**: `background: var(--vscode-badge-background)`, texto `var(--vscode-badge-foreground)`
- Pill **inativa**: `border: 1px solid var(--vscode-input-border)`, fundo transparente
- `data-platform="ahrena"` em cada pill; cards têm `data-platforms="ahrena claude"`
- Filtro de plataforma e search combinam com **AND**
- `flex-wrap: wrap` para sidebars estreitas

### Section Header

```
▼  Warriors  ···  14        (sem filtro)
▼  Warriors  ···  3 / 14   (com filtro ativo)
```

- Implementado com `<details>/<summary>` HTML nativo
- Triângulo customizado em CSS: `▶` colapsado / `▼` expandido via `details[open] summary::before`
- Hover: `var(--vscode-list-hoverBackground)`
- Seções com `count === 0` após filtro: `opacity: 0.5`, `pointer-events: none`
- Seções em `defaultExpandedKinds` renderizam com atributo `open`

### Card

```
┌──────────────────────────────────────────────┐
│  [icon 16px]  name (bold, truncado)          │
│               description (2 linhas, muted)  │
│               [badge] [badge]                │
└──────────────────────────────────────────────┘
```

| Atributo | Valor |
|----------|-------|
| `role` | `"button"` |
| `tabindex` | `"0"` |
| `data-file-path` | caminho absoluto do arquivo |
| `data-line-number` | número da linha (opcional) |
| `data-platforms` | ex: `"ahrena claude"` |
| `data-name` | nome em lowercase |
| `data-desc` | description em lowercase |

- Padding: `6px 8px`; gap ícone↔texto: `8px`
- Name: `font-weight: 600`, `overflow: hidden`, `text-overflow: ellipsis`, `white-space: nowrap`
- Description: `color: var(--vscode-descriptionForeground)`, `font-size: 11px`, `display: -webkit-box`, `-webkit-line-clamp: 2`
- Hover: `background: var(--vscode-list-hoverBackground)`, cursor `pointer`
- Active: `background: var(--vscode-list-activeSelectionBackground)`

#### Kind Icons (SVG 16×16, `fill: currentColor`)

| Kind | Conceito visual |
|------|----------------|
| `lex` | escudo / lei |
| `codex` | livro aberto |
| `kata` | raio / skill |
| `warrior` | robô / agente |
| `cry` | megafone / comando |
| `tool` | chave inglesa |
| `mcp` | plug / servidor |

#### Platform Badges

- Height `16px`, padding `0 6px`, border-radius `8px`
- Texto branco, `font-size: 10px`, `font-weight: 600`
- Cores por plataforma: Ahrena `#7C3AED` · Claude `#E07400` · Cursor `#0078D4` · Agno `#00BF63` · Strands `#DB6286`

---

## Estados da View

### Loading
```
         ◌  (spinner CSS)
    Scanning artifacts…
```

### Empty workspace
```
    🤖  (ícone grande, muted)
    No AI artifacts found
    in this workspace.
```
Ativado quando `artifacts.length === 0`.

### No results (filtro ativo)
```
    No artifacts match
    "python" · Cursor

    [Clear filters]
```
Exibido quando todos os cards estão `hidden`.  
Botão "Clear filters" reseta search e chip de plataforma.

### Erro fatal
```
    ⚠  Scan failed
    [mensagem curta]

    [Retry]
```
Erros de arquivo individual são silenciosos (logados no console, não exibidos na UI).

---

## Interações

| Ação | Resultado |
|------|-----------|
| Clicar / Enter / Space em card | `postMessage({ type: 'openArtifact', filePath, lineNumber })` |
| Clicar chip de plataforma | Filtra cards por `data-platforms` (client-side) |
| Digitar no search | Filtra por `data-name` + `data-desc` (client-side) |
| Clicar `×` no search | Limpa filtro de texto |
| Clicar header de seção | Expand/colapso via `<details>` nativo |
| Clicar botão `⟳` (toolbar VS Code) | Dispara `agentExplorer.refresh` |
| Arquivo salvo no workspace | Re-scan → `postMessage(scanResult)` → re-render completo |

---

## CSS Tokens VS Code

| Token | Uso |
|-------|-----|
| `--vscode-font-family` | `body` |
| `--vscode-font-size` | `body` |
| `--vscode-foreground` | texto principal |
| `--vscode-descriptionForeground` | description do card |
| `--vscode-sideBar-background` | `body` background |
| `--vscode-list-hoverBackground` | hover card + section |
| `--vscode-list-activeSelectionBackground` | card :active |
| `--vscode-input-background` | search background |
| `--vscode-input-border` | search border + chip inativo |
| `--vscode-input-foreground` | search texto |
| `--vscode-badge-background` | chip ativo |
| `--vscode-badge-foreground` | chip ativo texto |
| `--vscode-icon-foreground` | kind icons |
| `--vscode-errorForeground` | estado de erro |

---

## Acessibilidade

- `role="button"` + `tabindex="0"` em cada card
- `aria-expanded` nos `<summary>` de cada seção
- `aria-label="Filter by Ahrena"` nas platform chips
- `aria-live="polite"` no contador de resultados
- `aria-label="Clear search"` no botão `×`
- Tab percorre: search → chips → cards (ordem DOM)

---

## Steps

- [ ] 1. Criar `src/webview/html/style.css` com tokens e todos os componentes
- [ ] 2. Criar `src/webview/html/template.ts` com HTML estático de referência (sem dados)
- [ ] 3. Criar `src/webview/html/build-html.ts` que injeta `ScanResult` serializado no template
- [ ] 4. Implementar JS client-side de filtro (chips + search + contagens dinâmicas)
- [ ] 5. Implementar todos os estados (loading, empty, no-results, error)
- [ ] 6. Validar visualmente no Extension Development Host com fixture de dados estáticos

## Dependências

- `plan-001` (tipos, constantes, `ScanResult`)
- `plan-005` (scanner — necessário para dados reais em testes)
