---
plan_id: "005"
title: "agent-explorer-scanner"
status: pending
agent: claude
created_at: "2026-05-03T00:00:00Z"
updated_at: "2026-05-03T00:00:00Z"
---

# Plan: Agent Explorer — Scanner + Platform Detector

## Objetivo

Orquestrar todos os detectores num único `scan()` que retorna `ScanResult`, detectar quais
plataformas estão instaladas no workspace, e manter o painel atualizado via `FileSystemWatcher`.

---

## `platform/detector.ts`

```typescript
export async function detectInstalledPlatforms(
  workspaceRoot: string
): Promise<PlatformId[]>
```

**Algoritmo:**

```
1. Verifica diretórios (rápido, síncrono via fs.existsSync):
   .ahrena/ → 'ahrena'
   .claude/  → 'claude'
   .cursor/  → 'cursor'

2. Amostra arquivos Python (async — só se necessário):
   vscode.workspace.findFiles('**/*.py', excludes, limit=50)
   Para cada arquivo: lê primeiras 30 linhas
   Se qualquer linha bate /^\s*(?:from|import)\s+agno/ → 'agno'
   Se qualquer linha bate /^\s*(?:from|import)\s+strands/ → 'strands'
   Para ao encontrar ambos (short-circuit)

3. Retorna array dedupado de PlatformId[]
```

---

## `scanner/workspace-scanner.ts`

```typescript
export class WorkspaceScanner {
  constructor(private readonly workspaceRoot: string) {}

  async scan(): Promise<ScanResult>
}
```

**Algoritmo do `scan()`:**

```
t0 = Date.now()
installedPlatforms = await detectInstalledPlatforms(workspaceRoot)

Para cada detector em DETECTOR_REGISTRY:
  files = await vscode.workspace.findFiles(detector.fileGlob, excludes)
  Para cada file:
    content = await vscode.workspace.fs.readFile(file)
    artifacts = detector.detect(filePath, content)  — em try/catch → ScanError se falha
    push artifacts

Dedup por id (Map<string, ArtifactDefinition>)
Ordena por kind (KIND_ORDER) + por name alfabético dentro de cada kind

return {
  artifacts,
  installedPlatforms,
  errors,
  durationMs: Date.now() - t0
}
```

**Exclusões padrão (glob):**
- `**/node_modules/**`
- `**/.venv/**`
- `**/dist/**`
- `**/__pycache__/**`

---

## `scanner/file-watcher.ts`

```typescript
export class ArtifactFileWatcher implements vscode.Disposable {
  constructor(
    private readonly scanner: WorkspaceScanner,
    private readonly onScanResult: (result: ScanResult) => void,
    private readonly delay: number,
  ) {}

  start(): void
  dispose(): void
}
```

**Padrões monitorados:**
```
**/.claude/rules/**/*.{md,mdc}
**/.cursor/rules/**/*.{md,mdc}
**/.claude/skills/**/SKILL.md
**/.cursor/skills/**/SKILL.md
**/.claude/agents/**/*.md
**/.cursor/agents/**/*.md
**/.claude/commands/**/*.md
**/.cursor/commands/**/*.md
**/*.py
**/.cursor/mcp.json
**/.mcp.json
**/.claude/settings*.json
```

**Debounce:**
```
pendingTimer: NodeJS.Timeout | undefined

onChange():
  clearTimeout(pendingTimer)
  pendingTimer = setTimeout(() => scan().then(onScanResult), delay)
```

`delay` vem de `AgentExplorerConfig.watchDelay` (default 500ms).

---

## Steps

- [ ] 1. Criar `platform/detector.ts`
- [ ] 2. Criar `scanner/workspace-scanner.ts`
- [ ] 3. Criar `scanner/file-watcher.ts`
- [ ] 4. Criar `test/suite/platform/detector.test.ts` (mock de fs)
- [ ] 5. Integrar scanner no `ExplorerViewProvider` (chama `scan()` em `resolveWebviewView`)
- [ ] 6. Confirmar no Extension Development Host que `ScanResult` chega com dados reais do ahrena

## Dependências

- `plan-004` (DETECTOR_REGISTRY pronto)
- `plan-001` (tipos)
