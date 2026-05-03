# Plano: Extensão VS Code — Agent Explorer

## Context

Extensão VS Code que cataloga e visualiza **todos os artefatos de IA** de um workspace numa interface estilo VS Code Extensions: cards com ícone, nome, descrição e badges de plataforma, organizados por tipo de artefato, com filtro por plataforma instalada. O usuário precisa de uma forma visual de navegar warriors, katas, cries, lex, codex, tools e MCPs sem abrir pastas manualmente.

---

## Localização do Projeto

```
C:\Workspace\guardia\public\vscode-agent-explorer\
```

---

## Modelo de Dados: Artefato × Plataforma

Dois eixos independentes:

| Eixo | Tipo | Valores |
|------|------|---------|
| **Tipo** (`ArtifactKind`) | O que é o artefato | `lex` · `codex` · `kata` · `warrior` · `cry` · `tool` · `mcp` |
| **Plataforma** (`PlatformId`) | Onde está instalado | `ahrena` · `claude` · `cursor` · `agno` · `strands` |

Um artefato pode ter **múltiplas plataformas**. Ex: `.claude/rules/lex-python-error-handling.md` → `kind: 'lex'`, `platforms: ['ahrena', 'claude']`.

### Detecção de plataformas instaladas

| Sinal | Plataforma detectada |
|-------|---------------------|
| Diretório `.ahrena/` existe | `ahrena` |
| Diretório `.claude/` existe | `claude` |
| Diretório `.cursor/` existe | `cursor` |
| Qualquer `.py` importa `agno` | `agno` |
| Qualquer `.py` importa `strands` | `strands` |

O filter bar mostra **só as plataformas detectadas** no workspace.

---

## Artefatos Suportados

| Kind | Label UI | Arquivo / Fonte | Identificador | Campos extraídos |
|------|----------|-----------------|---------------|-----------------|
| `lex` | Lex | `lex-*.md` em `.claude/rules/`, `lex-*.mdc` em `.cursor/rules/` | filename `lex-*` | `name`, `description` (frontmatter ou 1ª linha do H1) |
| `codex` | Codex | `codex-*.md` em `.claude/rules/`, `codex-*.mdc` em `.cursor/rules/` | filename `codex-*` | `name`, `description` (frontmatter ou 1ª linha do H1) |
| `kata` | Katas | `SKILL.md` em `.claude/skills/kata-*/`, `.cursor/skills/kata-*/` | path + frontmatter `name` começa com `kata-` | `name`, `description` |
| `warrior` | Warriors | `warrior-*.md` (Ahrena), `*.md` em `.claude/agents/` (Claude), `Agent()` em `.py` (Agno/Strands) | filename / path / import | `name`, `description`, model, tools |
| `cry` | Cries | `cry-*.md` em `.claude/commands/`, `cry-*.md` em `.cursor/commands/**` | filename `cry-*` | `name`, `description` (1ª linha ou frontmatter) |
| `tool` | Tools | `*.py` com `@tool` (Agno ou Strands) | `@tool` decorator + import guard | `name` (fn name), `description` (docstring) |
| `mcp` | MCPs | `.cursor/mcp.json`, `.mcp.json`, `settings.json` com `mcpServers` | JSON key `mcpServers` | `name` (server key), `url` ou `command` |

---

## Arquitetura da UI

**Estilo VS Code Extensions:** `WebviewViewProvider` na Activity Bar (sidebar permanente), não um `WebviewPanel` one-shot.

```
Activity Bar (ícone) → WebviewView (sidebar)
┌────────────────────────────────────────┐
│ 🔍 Search...                           │
│ [All] [Ahrena] [Claude] [Cursor] [Agno]│  ← platform chips (detectados)
├────────────────────────────────────────┤
│ ▼ Lex  (58)                            │
│  ┌──────────────────────────────────┐  │
│  │ 📋 lex-python-error-handling     │  │  ← card: icon + name + desc + badges
│  │  Bare except: are FORBIDDEN...   │  │
│  │  [Ahrena] [Claude]               │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │ 📋 lex-entities                  │  │
│  │  Every persistent entity MUST...  │  │
│  │  [Ahrena] [Claude] [Cursor]       │  │
│  └──────────────────────────────────┘  │
├────────────────────────────────────────┤
│ ▼ Codex  (35)                          │
│ ▶ Katas  (55)                          │
│ ▶ Warriors  (14)                       │
│ ▶ Cries  (30)                          │
│ ▶ Tools  (0)                           │
│ ▶ MCPs  (1)                            │
└────────────────────────────────────────┘
```

Clicar num card → `vscode.workspace.openTextDocument` + `showTextDocument` (navega para o arquivo).

---

## Estrutura de Pastas

```
vscode-agent-explorer/
├── .vscode/
│   ├── launch.json
│   └── tasks.json
├── src/
│   ├── extension.ts            # activate(): registra WebviewViewProvider + comandos
│   ├── types.ts                # ArtifactDefinition, ArtifactKind, PlatformId, etc.
│   ├── constants.ts            # KIND_META, PLATFORM_META, globs, config keys
│   │
│   ├── platform/
│   │   └── detector.ts         # detectInstalledPlatforms(): lê dirs + amostra .py
│   │
│   ├── detectors/
│   │   ├── index.ts            # DETECTOR_REGISTRY[]
│   │   ├── lex.ts              # lex-*.md + lex-*.mdc → kind: 'lex'
│   │   ├── codex.ts            # codex-*.md + codex-*.mdc → kind: 'codex'
│   │   ├── kata.ts             # SKILL.md em kata-*/ → kind: 'kata'
│   │   ├── warrior.ts          # warrior-*.md + .claude/agents/*.md → kind: 'warrior'
│   │   ├── cry.ts              # cry-*.md → kind: 'cry'
│   │   ├── python.ts           # Agent() → 'warrior'; @tool → 'tool' (Agno + Strands)
│   │   └── mcp.ts              # mcpServers JSON → kind: 'mcp'
│   │
│   ├── parsers/
│   │   ├── frontmatter.ts      # gray-matter wrapper (YAML + fallback 1ª linha)
│   │   ├── markdown-title.ts   # extrai 1ª linha do H1 quando não há frontmatter
│   │   └── python-agent.ts     # paren-balancer + @tool extractor
│   │
│   ├── scanner/
│   │   ├── workspace-scanner.ts  # orquestra detectores, dedup por id
│   │   └── file-watcher.ts       # FileSystemWatcher + debounce
│   │
│   ├── webview/
│   │   ├── explorer-view-provider.ts   # WebviewViewProvider (sidebar permanente)
│   │   ├── message-handler.ts          # processa msgs webview → extension
│   │   └── html/
│   │       ├── build-html.ts           # monta HTML completo com nonce + CSS vars
│   │       ├── template.ts             # string template do HTML da view
│   │       └── style.css               # estilos usando var(--vscode-*)
│   │
│   ├── commands/
│   │   ├── index.ts
│   │   ├── refresh.ts          # agentExplorer.refresh
│   │   └── open-artifact.ts    # agentExplorer.openArtifact
│   │
│   └── config/
│       └── settings.ts         # AgentExplorerConfig
│
├── media/
│   ├── icons/
│   │   ├── lex.svg             # 📋 regra/lei
│   │   ├── codex.svg           # 📚 manual
│   │   ├── kata.svg            # ⚡ skill/procedimento
│   │   ├── warrior.svg         # 🤖 agente
│   │   ├── cry.svg             # 🔊 comando
│   │   ├── tool.svg            # 🔧 ferramenta
│   │   └── mcp.svg             # 🔌 servidor MCP
│   └── explorer-icon.svg       # ícone Activity Bar
│
├── test/
│   ├── fixtures/
│   │   ├── lex-valid.md        lex-*.md sem frontmatter (claude format)
│   │   ├── lex-valid.mdc       lex-*.mdc com frontmatter (cursor format)
│   │   ├── codex-valid.md
│   │   ├── warrior-valid.md
│   │   ├── skill-valid.md
│   │   ├── cry-valid.md
│   │   ├── agno_with_tools.py
│   │   ├── strands_with_tools.py
│   │   ├── mcp-valid.json
│   │   └── not-an-agent.py
│   └── suite/
│       ├── parsers/
│       ├── detectors/
│       └── platform/
│
├── package.json
├── tsconfig.json
├── esbuild.js
└── .vscodeignore
```

---

## Interfaces TypeScript (src/types.ts)

```typescript
export type ArtifactKind = 'lex' | 'codex' | 'kata' | 'warrior' | 'cry' | 'tool' | 'mcp';
export type PlatformId   = 'ahrena' | 'claude' | 'cursor' | 'agno' | 'strands';

export interface ArtifactDefinition {
  id: string;                  // `${kind}::${filePath}::${name}`
  name: string;
  description: string;
  kind: ArtifactKind;
  platforms: PlatformId[];     // ex: ['ahrena', 'claude']
  filePath: string;
  lineNumber?: number;
  rawFields: Record<string, unknown>;
}

export interface KindMeta {
  kind: ArtifactKind;
  label: string;               // "Lex", "Codex", etc.
  iconFile: string;
  defaultExpanded: boolean;
}

export interface PlatformMeta {
  id: PlatformId;
  label: string;               // "Ahrena", "Claude", etc.
  color: string;               // cor do badge
}

export interface ArtifactDetector {
  readonly kind: ArtifactKind;
  readonly fileGlob: string | string[];
  detect(filePath: string, content: string): ArtifactDefinition[];
}

export interface ScanResult {
  artifacts: ArtifactDefinition[];
  installedPlatforms: PlatformId[];
  errors: ScanError[];
  durationMs: number;
}

export interface AgentExplorerConfig {
  enabled: boolean;
  additionalPaths: string[];
  watchDelay: number;
  defaultExpandedKinds: ArtifactKind[];
}

// Mensagens webview ↔ extension
export type WebviewMessage =
  | { type: 'ready' }
  | { type: 'openArtifact'; filePath: string; lineNumber?: number }
  | { type: 'filterChanged'; platform: PlatformId | 'all'; query: string };

export type ExtensionMessage =
  | { type: 'scanResult'; result: ScanResult }
  | { type: 'loading' };
```

---

## Estratégia de Parsing por Tipo

### Lex e Codex (`lex.ts`, `codex.ts`)

```
Globs:
  lex.ts:   **/.claude/rules/**/lex-*.md   +  **/.cursor/rules/**/lex-*.mdc
  codex.ts: **/.claude/rules/**/codex-*.md +  **/.cursor/rules/**/codex-*.mdc

Plataformas atribuídas:
  Arquivo em .claude/ → ['claude'] + ['ahrena'] se .ahrena/ existe
  Arquivo em .cursor/ → ['cursor'] + ['ahrena'] se .ahrena/ existe

Formato .mdc (Cursor): tem frontmatter com 'description' e 'alwaysApply'
  → parseFrontmatter() → data.description

Formato .md (Claude Code): SEM frontmatter
  → fallback: parsers/markdown-title.ts extrai texto do primeiro H1
    ex: "# Lexis: Python Error Handling" → "Python Error Handling"
  → description: 1ª frase do body (até o 1º ponto final, máx 120 chars)
```

### Kata, Warrior, Cry
*(inalterado do plano anterior — ver Estratégia de Parsing)*

### Python (Agno + Strands) — `python.ts`

```
Mesmos arquivos .py, mesma passagem:

1. Import guard rápido: content.includes('agno') || content.includes('strands')
2. Identifica framework: regex de import → plataforma 'agno' ou 'strands'
3. Extrai Agent() constructors → kind: 'warrior'
4. Extrai @tool functions → kind: 'tool'
   Regex: /@tool\s*(?:\([^)]*\)\s*)?\ndef\s+(\w+)\s*\([^)]*\)[^:]*:\s*(?:"""([\s\S]*?)""")?/
   name = nome da função; description = 1ª linha da docstring
5. Retorna array misto (warriors + tools) com kinds diferentes
```

### MCP (`mcp.ts`)

```
Globs: **/.cursor/mcp.json  |  **/.mcp.json
       **/.claude/settings.json  |  **/.claude/settings.local.json

Extração:
  JSON.parse → data?.mcpServers (objeto)
  Para cada key serverName:
    name = serverName
    description = config.url ?? config.command ?? "(stdio)"
    rawFields = config com headers.* e env.* substituídos por "***"
  platforms: arquivo em .cursor/ → ['cursor']; .claude/ → ['claude']
```

---

## Comunicação Webview ↔ Extension

```
extension.ts                      webview HTML
     │                                │
     │── postMessage(loading) ──────► │  mostra spinner
     │                                │
     │◄── message({type:'ready'}) ─── │  webview carregou
     │                                │
scan()                                │
     │── postMessage(scanResult) ───► │  renderiza cards
     │                                │
     │◄── message(openArtifact) ───── │  usuário clicou num card
     │                                │
vscode.window.showTextDocument        │
     │◄── message(filterChanged) ──── │  usuário mudou platform/search
     │                                │  (filtro é client-side no JS da webview)
```

O filtro (platform + search) é **client-side**: o JS da webview esconde/mostra cards com CSS, sem round-trip para a extensão. Isso garante UI reativa mesmo em workspaces grandes.

---

## package.json — Campos Críticos

```json
{
  "name": "agent-explorer",
  "displayName": "Agent Explorer",
  "version": "0.1.0",
  "publisher": "guardia",
  "engines": { "vscode": "^1.85.0" },
  "activationEvents": ["onStartupFinished"],
  "main": "./dist/extension.js",
  "contributes": {
    "viewsContainers": {
      "activitybar": [{
        "id": "agentExplorer",
        "title": "Agent Explorer",
        "icon": "media/explorer-icon.svg"
      }]
    },
    "views": {
      "agentExplorer": [{
        "id": "agentExplorer.view",
        "name": "Artifacts",
        "type": "webview"         ← WebviewView, não tree
      }]
    },
    "commands": [
      { "command": "agentExplorer.refresh", "title": "Refresh", "icon": "$(refresh)" },
      { "command": "agentExplorer.openArtifact", "title": "Open Artifact" }
    ],
    "menus": {
      "view/title": [
        { "command": "agentExplorer.refresh", "when": "view == agentExplorer.view" }
      ]
    },
    "configuration": {
      "agentExplorer.enabled": { "type": "boolean", "default": true },
      "agentExplorer.additionalPaths": { "type": "array", "default": [] },
      "agentExplorer.watchDelay": { "type": "number", "default": 500 },
      "agentExplorer.defaultExpandedKinds": {
        "type": "array",
        "default": ["warrior", "kata", "mcp"]
      }
    }
  },
  "dependencies": { "gray-matter": "^4.0.3" },
  "devDependencies": { "esbuild", "typescript ^5.3", "@types/vscode ^1.85", "@types/mocha", ... }
}
```

---

## Fases de Implementação

### Fase 1 — Scaffold (Dia 1)
- Criar projeto, `package.json` com `"type": "webview"` na view, `tsconfig.json`, `esbuild.js`
- `extension.ts` mínimo: registra `WebviewViewProvider` que mostra apenas "Carregando..."
- Confirmar ícone na Activity Bar e painel vazio no Extension Development Host
- Criar `src/types.ts` completo

### Fase 2 — Parsers (Dia 2)
- `parsers/frontmatter.ts` (gray-matter + try/catch)
- `parsers/markdown-title.ts` (extrai texto do H1 + 1ª frase do body)
- `parsers/python-agent.ts` (paren-balancer + `@tool` regex)
- Fixtures de teste + testes unitários (sem VS Code API)

### Fase 3 — Detectores (Dia 3)
- `detectors/lex.ts`, `detectors/codex.ts` — ambos usam `markdown-title` fallback
- `detectors/kata.ts`, `detectors/warrior.ts`, `detectors/cry.ts`
- `detectors/python.ts` — retorna mix de `warrior` + `tool` na mesma passagem
- `detectors/mcp.ts` — JSON parse + sanitização de tokens
- `detectors/index.ts` — `DETECTOR_REGISTRY` ordenado
- Testes unitários por detector

### Fase 4 — Scanner + Platform Detector (Dia 4)
- `platform/detector.ts`: `detectInstalledPlatforms(workspaceFolders)` — verifica dirs + amostra Python
- `scanner/workspace-scanner.ts`: `scan()` → chama platform detector + todos os detectores → dedup por `id`
- `scanner/file-watcher.ts`: FileSystemWatcher com debounce

### Fase 5 — WebviewView HTML/CSS/JS (Dia 5)
- `webview/html/style.css` — usa exclusivamente `var(--vscode-*)` para temas
- `webview/html/template.ts` — HTML com nonce (CSP) + script inline de filtro client-side:
  - Platform chips: clique adiciona/remove classe `active`, `data-platform` nos cards é filtrado
  - Search: `input` filtra por `data-name` + `data-desc`
  - Section toggle (▼/▶): `details`/`summary` HTML nativo
- `webview/html/build-html.ts` — monta HTML final com `ScanResult` serializado como JSON no `<script>`

### Fase 6 — WebviewViewProvider + Mensagens (Dia 6)
- `webview/explorer-view-provider.ts` — implementa `vscode.WebviewViewProvider`:
  - `resolveWebviewView()`: cria webview, seta HTML de loading, dispara `scan()`
  - Ao receber `scanResult`: chama `build-html.ts` e atualiza `webview.html`
  - Listener de mensagens: `openArtifact` → `vscode.workspace.openTextDocument`
- `webview/message-handler.ts` — processa mensagens do webview

### Fase 7 — Comandos + Config + Watcher (Dia 7)
- `commands/refresh.ts`: re-scan → postMessage(scanResult)
- `config/settings.ts`: lê `AgentExplorerConfig`
- Conecta FileSystemWatcher → re-scan → atualiza webview
- `onDidChangeConfiguration` para re-scan quando settings mudam

### Fase 8 — Integração + Polish (Dia 8)
- Status bar: `$(robot) 193 artifacts`
- Loading state: spinner no webview enquanto scan roda
- Mensagem "nenhum artefato detectado" quando workspace vazio
- Testes de integração do WebviewViewProvider (mock de `ScanResult`, verifica HTML gerado)
- `.vscodeignore`, README, empacotar `.vsix`

---

## Riscos e Mitigações

| Risco | Mitigação |
|-------|-----------|
| Lex/codex duplicados entre `.claude/rules/` e `.cursor/rules/` | `id` inclui filePath → caminhos distintos → entradas distintas; usuário vê badge diferente (Claude vs Cursor) — é intencional |
| `.md` sem frontmatter e sem H1 | `markdown-title.ts` retorna `''`; scanner substitui por nome do arquivo sem extensão |
| Token Bearer exposto no MCP | `mcp.ts` sanitiza `headers.*` e `env.*` → `***` antes de qualquer serialização |
| Webview CSP bloqueia scripts inline | Usar `nonce` gerado por `crypto.randomBytes(16)` em cada render; add ao `Content-Security-Policy` e ao `<script nonce="...">` |
| Filtro client-side travando com 200+ artefatos | HTML é pré-renderizado; filtro usa só `classList.toggle('hidden')` — O(n) puro DOM, < 5ms para 500 cards |
| Python: `@tool` sem docstring | `description` fica `''`; card exibe apenas o nome (aceitável) |
| Warriors em `.cursor/skills/` detectados como kata | `kata.ts` retorna `[]` quando frontmatter `name` começa com `warrior-` |
| Re-scan em bulk git checkout (centenas de eventos) | Debounce 500ms + cancela scan pendente; no máximo 1 scan a cada 500ms |
| JSON malformado em `settings.json` | `mcp.ts` envolve `JSON.parse` em try/catch → arquivo ignorado, `ScanError` logado |
| Webview não persiste estado (scroll, filtro) ao perder foco | `retainContextWhenHidden: true` no `WebviewViewOptions` (trade-off: +memória, melhor UX) |

---

## Verificação

1. F5 → Extension Development Host com `guardia/public/ahrena` como workspace
2. Activity Bar exibe ícone Agent Explorer
3. Painel mostra chips de plataforma: **Ahrena · Claude · Cursor** (cursor detectado via `.cursor/`)
4. Seção **Lex** expandida com ~58 entradas; cada card exibe badges `[Ahrena] [Claude]`
5. Seção **Codex** com entradas de `codex-*.md` e `codex-*.mdc`
6. Seção **Katas** com ~55 entradas
7. Seção **Warriors** com 14 warriors Ahrena
8. Seção **Cries** com ~30 entradas
9. Seção **MCPs** com `github` (description: `https://api.githubcopilot.com/mcp/`); token não visível
10. Clicar chip **Cursor** → apenas artefatos de `.cursor/` visíveis
11. Digitar "python" no search → filtra todos os kinds simultaneamente
12. Clicar em `lex-python-error-handling` → abre `.claude/rules/engineering/backend/lex-python-error-handling.md`
13. Editar um arquivo e salvar → painel atualiza em < 1s
14. Fixture Python com `@tool` → aparece na seção **Tools**
15. `npm test` → todos os testes passando
