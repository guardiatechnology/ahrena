# Codex: Convenção Ahrena — `tools/` (MCP) e `widgets/` (React)

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Extensão Ahrena ao formato Anthropic Agent Skills — convenção para empacotar tools MCP (lógica) e widgets React (UI) dentro de um projeto de skill, e como widgets se ligam a scripts e tools

## Status — Convenção, não Spec

> **Atenção:** `tools/` e `widgets/` **não** fazem parte da spec Anthropic Agent Skills. Esta é uma convenção do framework Ahrena. O `SKILL.md` gerado em projetos com esses diretórios **deve** incluir um cabeçalho de aviso explícito para que consumidores externos saibam o que esperar.

## Conteúdo

### `tools/` — MCP tools próprias do skill

Tools MCP empacotadas com o skill expõem capacidades de domínio que o agente externo invoca durante a execução. Não substituem MCP servers globais (GitHub, Notion, Figma) — atendem necessidades específicas do skill.

#### Layout

```
tools/
├── mcp.config.json     # registro das tools
└── handlers/           # implementações
    ├── validate_amount.py
    └── ...
```

Linguagens dos handlers: Python (default — alinhado a `codex-python-architecture`) ou JavaScript/TypeScript (Node). Mistura é permitida.

#### `mcp.config.json` — schema

```json
{
  "schema_version": 1,
  "mcp": {
    "name": "{slug}-tools",
    "description": "MCP tools bundled with this skill (Ahrena convention).",
    "tools": [
      {
        "name": "validate_amount",
        "description": "Validate that a transfer amount is within the allowed range and currency.",
        "input_schema": {
          "type": "object",
          "properties": {
            "amount": { "type": "integer", "minimum": 1 },
            "currency": { "type": "string", "pattern": "^[A-Z]{3}$" }
          },
          "required": ["amount", "currency"]
        },
        "handler": "handlers/validate_amount.py:run"
      }
    ]
  }
}
```

| Campo | Descrição |
|-------|-----------|
| `schema_version` | Inteiro; reservado para evolução do schema (atual: `1`) |
| `mcp.name` | `{slug}-tools` por convenção; identificador local do server |
| `mcp.description` | Frase única descrevendo o propósito do conjunto |
| `mcp.tools[].name` | snake_case; identificador da tool dentro do server |
| `mcp.tools[].description` | Texto que o agente lê para decidir quando invocar |
| `mcp.tools[].input_schema` | JSON Schema Draft 7+ |
| `mcp.tools[].handler` | `<path-relativo>:<funcao>` — o build resolve para um runnable |

#### Convenções para handlers

- Python: handler é `def run(input: dict) -> dict | Result[T, E]`. Aplicar `lex-python-typing`, `lex-python-error-handling`, `lex-python-result-type` (quando uso de Result for natural), `lex-python-security`, `lex-mcp`.
- JS/TS: handler é `export async function run(input): Promise<unknown>`. Aplicar `lex-frontend-typing` (quando TS), tratamento idiomático de erro.
- Logging em qualquer linguagem segue `lex-logging-decorator`.

### `widgets/` — Componentes React

Widgets são componentes React (TypeScript) renderizados pelo agente host na superfície de chat. A arquitetura herda **integralmente** `codex-frontend-architecture`: camadas (Pages → Features → Components → Hooks → Services → State), state management apropriado por escopo, props tipadas, server state via TanStack Query / SWR quando há fetch real.

#### Layout

```
widgets/
├── package.json        # React 18 + TS strict + Vite
├── tsconfig.json       # strict: true, noUncheckedIndexedAccess: true
├── manifest.json       # registro dos componentes expostos
└── src/
    ├── components/     # primitivos reutilizáveis
    ├── features/       # blocos por feature
    └── transfer-form/  # exemplo de componente de feature
        └── index.tsx
```

#### `manifest.json` — schema

```json
{
  "schema_version": 1,
  "components": [
    {
      "name": "TransferForm",
      "entry": "src/transfer-form/index.tsx",
      "props_schema": {
        "type": "object",
        "properties": {
          "default_amount": { "type": "integer" },
          "currency": { "type": "string" }
        }
      },
      "events": [
        {
          "name": "submit",
          "payload_schema": {
            "type": "object",
            "properties": {
              "amount": { "type": "integer" },
              "currency": { "type": "string" }
            },
            "required": ["amount", "currency"]
          }
        }
      ],
      "bindings": [
        {
          "kind": "tool",
          "ref": "validate_amount"
        },
        {
          "kind": "script",
          "ref": "scripts/src/format_currency.py",
          "called_via": "http://localhost:5174/format-currency"
        }
      ]
    }
  ]
}
```

| Campo | Descrição |
|-------|-----------|
| `schema_version` | Inteiro; reservado (atual: `1`) |
| `components[].name` | PascalCase; identificador exposto ao host |
| `components[].entry` | Path relativo do componente que o build empacota |
| `components[].props_schema` | JSON Schema das props aceitas |
| `components[].events[]` | Eventos que o componente emite, com payload tipado |
| `components[].bindings[]` | Dependências externas (tools MCP ou scripts) — ver abaixo |

### Binding widget ↔ script ↔ tool

Widgets declaram explicitamente as dependências externas em `bindings[]`. O host resolve em runtime conforme o ambiente:

| `kind` | Quando usar | Resolução em dev (localhost) | Resolução em prod (host agente) |
|--------|-------------|------------------------------|---------------------------------|
| `tool` | Lógica MCP do skill (`tools/`) ou de outro server MCP ativo | Tool stub local em `localhost:5175` | Host invoca a tool MCP diretamente |
| `script` | Utilitário em `scripts/` chamado por HTTP/JSON | `fetch(called_via)` para o script runner em `localhost:5174` | Host executa script bundlado e expõe endpoint efêmero, ou roteia via tool MCP |

**Princípio:** o widget **não importa** scripts diretamente. Toda dependência cruza uma fronteira tipada (HTTP/JSON ou MCP) — isso mantém o widget renderizável em isolamento (preview em Storybook, smoke em Playwright) sem precisar do runtime do skill inteiro.

`called_via` em bindings `kind: script`:

- Em **dev**, aponta para o script runner local (`http://localhost:{scripts_port}/...`)
- Em **prod**, é reescrito pelo stack de build do projeto consumidor: vira um caminho relativo que o host resolve via tool MCP equivalente, ou um endpoint efêmero. A reescrita é parte do build, não da spec.

### Reuso de codex e Lexis

| Conteúdo | Codex de arquitetura | Lexis aplicáveis |
|----------|----------------------|------------------|
| `widgets/` React+TS | `codex-frontend-architecture` | `lex-frontend-typing`, `lex-frontend-accessibility`, `lex-frontend-security`, `lex-frontend-testing`, `lex-design-system-library` (em superfície Guardia), `lex-tone` (microcopy) |
| `tools/handlers/` Python | `codex-mcp-common`, `codex-python-architecture`, `codex-python-tooling` | `lex-mcp`, `lex-python-typing`, `lex-python-testing`, `lex-python-security`, `lex-python-error-handling`, `lex-python-result-type`, `lex-logging-decorator` |
| `tools/handlers/` JS/TS | `codex-mcp-common` | `lex-mcp`, `lex-frontend-typing` (quando TS), `lex-logging-decorator` |
| Manifesto e schemas | (deste codex) | `lex-skill-project-structure` |

### Compatibilidade com a spec

| Aspecto | Spec Anthropic | Convenção Ahrena |
|---------|----------------|------------------|
| `SKILL.md`, frontmatter, body | Definidos | Inalterados |
| `references/`, `scripts/`, `assets/` | Definidos | Inalterados — Ahrena não modifica esses diretórios |
| `tools/`, `widgets/` | **Não cobertos** | Adicionados — agentes spec-only ignoram |
| `.skill-manifest.json` | Não coberto | Manifesto raiz Ahrena (auditoria, hashes — ver `lex-skill-project-structure` e `lex-skill-package-structure`) |

Quando a spec evoluir e cobrir tools/widgets, este codex documenta a transição (mapeamento, depreciações). Skills que adotaram a convenção continuam funcionando enquanto agentes Ahrena reconhecerem o layout — a migração para a forma canônica da spec será incremental.

## Restrições

- O autor **não infere** binding — toda dependência externa é declarada em `manifest.json` (widgets) ou `mcp.config.json` (tools)
- Widget **não importa** script diretamente; sempre cruza fronteira HTTP/MCP
- `bindings[].kind: script` é resolvido com `called_via` em dev e reescrito pelo build para prod — não usar URL hardcoded de produção
- Manifestos são validados antes de build pelo stack de build do projeto consumidor; falha de schema aborta com erro específico
