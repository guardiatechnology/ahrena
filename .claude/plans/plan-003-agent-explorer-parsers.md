---
plan_id: "003"
title: "agent-explorer-parsers"
status: pending
agent: claude
created_at: "2026-05-03T00:00:00Z"
updated_at: "2026-05-03T00:00:00Z"
---

# Plan: Agent Explorer — Parsers

## Objetivo

Implementar os três parsers de baixo nível que todos os detectores usam, com testes unitários
por parser (sem VS Code API — Node puro).

---

## `parsers/frontmatter.ts`  ← já existe (stub)

Wrapper sobre `gray-matter` com try/catch.

```typescript
export interface FrontmatterResult {
  data: Record<string, unknown>;
  content: string;          // corpo sem o bloco YAML
}

export function parseFrontmatter(raw: string): FrontmatterResult
```

**Casos de borda:**
- YAML malformado → `data: {}`, `content: raw`
- Arquivo vazio → `data: {}`, `content: ''`
- Frontmatter sem corpo → `data: {...}`, `content: ''`

---

## `parsers/markdown-title.ts`  ← já existe (stub)

Para arquivos `.claude/rules/` que não têm frontmatter — começa direto com `# Lexis: ...`.

```typescript
export interface MarkdownTitleResult {
  name: string;         // texto após "# Lexis:" / "# Codex:" etc.
  description: string;  // 1ª frase relevante do body
}

export function parseMarkdownTitle(content: string): MarkdownTitleResult
```

**Estratégia de extração da description:**

1. Tenta o bloco `> **...**` da seção `## Law` (padrão Ahrena)
2. Fallback: 1ª linha não-heading e não-blockquote após o H1
3. Remove `**bold**` e trunca em 120 chars

**Casos de borda:**
- Sem H1 → `name: ''`, `description: ''`
- H1 sem prefixo "Lexis:" → captura o título inteiro
- Body todo em blockquote → usa o blockquote
- Arquivo só com frontmatter (`.mdc`) → não é chamado para esses arquivos

---

## `parsers/python-agent.ts`

Parser de arquivos Python para extrair `Agent()` e `@tool`.

```typescript
export interface PyAgent {
  name: string;
  description: string;
  model: string;
  tools: string[];
  lineNumber: number;
}

export interface PyTool {
  name: string;
  description: string;    // 1ª linha da docstring
  lineNumber: number;
}

export interface PythonParseResult {
  agents: PyAgent[];
  tools: PyTool[];
  framework: 'agno' | 'strands' | 'unknown';
}

export function parsePythonFile(content: string): PythonParseResult
```

**Algoritmo — Agent() extraction:**

1. Import guard: `content.includes('agno') || content.includes('strands')` — skip se falso
2. Detecta framework via regex de import
3. Regex `Agent\s*\(` + **paren-balancer** para extrair o corpo completo (multi-linha)
4. Do corpo: extrai `name=`, `description=`/`instructions=`, `model=`, `tools=[...]`

**Paren-balancer** (evita regex greedy em multi-linha):
```
depth = 0; inString = false
para cada char:
  toggle inString em ' e "  (respeita \\)
  se não inString:
    ( → depth++
    ) → depth--; se depth==0 → fim do corpo
```

**Algoritmo — @tool extraction:**

```
regex: /@tool\s*(?:\([^)]*\)\s*)?\ndef\s+(\w+)/g
para cada match:
  fnName = match[1]
  lineNumber = contar \n até match.index
  buscar docstring imediatamente após ':'
  description = 1ª linha da docstring (strip)
```

**Casos de borda:**
- `@tool` sem docstring → `description: ''`
- `Agent()` multi-linha com strings contendo parênteses → paren-balancer resolve
- Arquivo sem `agno`/`strands` import → `{ agents: [], tools: [], framework: 'unknown' }`
- Dois frameworks no mesmo arquivo → `strands` prevalece (mais específico)

---

## Fixtures de Teste

```
test/fixtures/
  lex-no-frontmatter.md       # .claude/rules format: começa com # Lexis: ...
  lex-with-frontmatter.mdc    # .cursor/rules format: YAML + description
  codex-no-frontmatter.md
  agno_agent_simple.py        # Agent() single-line
  agno_agent_multiline.py     # Agent() com tools multi-linha
  strands_with_tools.py       # @tool functions
  agno_and_tools.py           # Agent() + @tool no mesmo arquivo
  no_framework.py             # Python sem agno/strands
  broken_frontmatter.mdc      # YAML inválido
```

---

## Steps

- [ ] 1. Completar `parsers/frontmatter.ts` (já existe stub)
- [ ] 2. Completar `parsers/markdown-title.ts` (já existe stub)
- [ ] 3. Criar `parsers/python-agent.ts` com paren-balancer e @tool extractor
- [ ] 4. Criar fixtures de teste
- [ ] 5. Criar `test/suite/parsers/frontmatter.test.ts`
- [ ] 6. Criar `test/suite/parsers/markdown-title.test.ts`
- [ ] 7. Criar `test/suite/parsers/python-agent.test.ts`
- [ ] 8. `npm test` → todos passando

## Dependências

- `plan-001` (tipos)
- `gray-matter` já instalado
