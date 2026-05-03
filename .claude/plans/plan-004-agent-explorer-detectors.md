---
plan_id: "004"
title: "agent-explorer-detectors"
status: pending
agent: claude
created_at: "2026-05-03T00:00:00Z"
updated_at: "2026-05-03T00:00:00Z"
---

# Plan: Agent Explorer — Detectors

## Objetivo

Implementar os 7 detectores de artefatos + o registry central. Cada detector recebe
`(filePath, content)` e retorna `ArtifactDefinition[]`.

---

## Interface comum

```typescript
export interface ArtifactDetector {
  readonly kind: ArtifactKind;
  readonly fileGlob: string | string[];
  detect(filePath: string, content: string): ArtifactDefinition[];
}
```

O campo `id` de cada artefato: `${kind}::${filePath}::${name}` — garante unicidade mesmo
quando o mesmo artefato existe em `.claude/` e `.cursor/` (caminhos distintos → IDs distintos).

---

## `detectors/lex.ts`

```
Globs:
  **/.claude/rules/**/lex-*.md
  **/.cursor/rules/**/lex-*.mdc

Plataformas:
  path contém /.claude/ → 'claude'  +  se .ahrena/ existe → 'ahrena'
  path contém /.cursor/ → 'cursor'  +  se .ahrena/ existe → 'ahrena'

Extração do nome:
  .mdc → parseFrontmatter().data.name ?? filename sem extensão
  .md  → parseMarkdownTitle().name ?? filename sem extensão

Extração da description:
  .mdc → data.description ?? ''
  .md  → parseMarkdownTitle().description
```

---

## `detectors/codex.ts`

Idêntico ao `lex.ts`, trocando `lex-*` por `codex-*` e `kind: 'codex'`.

---

## `detectors/kata.ts`

```
Globs:
  **/.claude/skills/kata-*/SKILL.md
  **/.cursor/skills/kata-*/SKILL.md

Plataformas:
  path contém /.claude/ → 'claude'  +  ahrena se aplicável
  path contém /.cursor/ → 'cursor'  +  ahrena se aplicável

Extração:
  parseFrontmatter() → data.name, data.description
  Se data.name começa com 'warrior-' → retorna [] (é warrior, não kata)
  name fallback: nome do diretório pai (kata-python-implement)

Dedup:
  Se o mesmo kata existir em .claude/ e .cursor/, são duas entradas distintas
  com platforms diferentes (claude vs cursor)
```

---

## `detectors/warrior.ts`

```
Globs:
  **/.cursor/agents/warrior-*.md   → platform: cursor + ahrena
  **/.claude/agents/*.md           → platform: claude + ahrena
  framework/*/warriors/warrior-*.md → platform: ahrena

Extração:
  parseFrontmatter() → data.name, data.description
  Fallback name: filename sem extensão
  Fallback description: parseMarkdownTitle().description

Nota: warriors em .cursor/skills/ são detectados pelo kata.ts
e descartados lá (retorna [] quando name começa com warrior-)
```

---

## `detectors/cry.ts`

```
Globs:
  **/.claude/commands/cry-*.md
  **/.cursor/commands/**/cry-*.md   (pode ter subpastas)

Plataformas:
  .claude/ → claude + ahrena se aplicável
  .cursor/ → cursor + ahrena se aplicável

Extração:
  .md sem frontmatter (.claude/commands/): 1ª linha não-vazia = description
    parseFrontmatter() retorna data: {} → usar 1ª linha do content
  .md com frontmatter (.cursor/commands/): data.description
  name: filename sem extensão e sem prefixo "cry-" opcional
        ex: cry-translate.md → "cry-translate"
```

---

## `detectors/python.ts`

```
Globs:
  **/*.py
  Excluir: **/node_modules/**, **/.venv/**, **/dist/**

Import guard:
  Se content não contém 'agno' nem 'strands' → retorna []

Chama parsePythonFile(content):
  Para cada agent → ArtifactDefinition { kind: 'warrior', platforms: [framework] }
  Para cada tool  → ArtifactDefinition { kind: 'tool',    platforms: [framework] }
  Retorna array misto

Plataforma:
  framework === 'agno'    → platforms: ['agno']
  framework === 'strands' → platforms: ['strands']
```

---

## `detectors/mcp.ts`

```
Globs:
  **/.cursor/mcp.json
  **/.mcp.json
  **/.claude/settings.json
  **/.claude/settings.local.json

Extração:
  JSON.parse(content) — em try/catch
  data?.mcpServers (objeto) → para cada key serverName:
    name        = serverName
    description = config.url ?? config.command ?? '(stdio)'
    rawFields   = sanitize(config):
      headers.*  → '***'
      env.*      → '***'
      url        → mantém (não é segredo)
      command    → mantém

Plataforma:
  path contém /.cursor/ → ['cursor']
  path contém /.claude/ → ['claude']
```

---

## `detectors/index.ts` — Registry

```typescript
export const DETECTOR_REGISTRY: ArtifactDetector[] = [
  new LexDetector(),
  new CodexDetector(),
  new KataDetector(),
  new WarriorDetector(),
  new CryDetector(),
  new PythonDetector(),
  new McpDetector(),
];
```

O scanner itera o registry e chama cada detector para os arquivos que casam com o glob.

---

## Deduplicação global

Feita no scanner (`plan-005`), não nos detectores. O `id` garante que:
- Mesmo artefato em `.claude/` e `.cursor/` = duas entradas distintas (plataformas diferentes)
- Mesmo artefato detectado duas vezes pelo mesmo glob = descartado pelo dedup por `id`

---

## Steps

- [ ] 1. Criar `detectors/lex.ts`
- [ ] 2. Criar `detectors/codex.ts`
- [ ] 3. Criar `detectors/kata.ts`
- [ ] 4. Criar `detectors/warrior.ts`
- [ ] 5. Criar `detectors/cry.ts`
- [ ] 6. Criar `detectors/python.ts`
- [ ] 7. Criar `detectors/mcp.ts`
- [ ] 8. Criar `detectors/index.ts` com DETECTOR_REGISTRY
- [ ] 9. Criar `test/suite/detectors/*.test.ts` por detector
- [ ] 10. `npm test` → todos passando

## Dependências

- `plan-003` (parsers prontos)
- `plan-001` (tipos e constantes)
