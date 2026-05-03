---
plan_id: "007"
title: "agent-explorer-wiring"
status: pending
agent: claude
created_at: "2026-05-03T00:00:00Z"
updated_at: "2026-05-03T00:00:00Z"
---

# Plan: Agent Explorer — Wiring, Polish e Empacotamento

## Objetivo

Conectar todos os módulos no `extension.ts`, adicionar status bar, polish visual,
tratar edge cases e gerar o `.vsix` final.

---

## `commands/refresh.ts`

```typescript
export function registerRefreshCommand(
  context: vscode.ExtensionContext,
  provider: ExplorerViewProvider,
): vscode.Disposable {
  return vscode.commands.registerCommand('agentExplorer.refresh', () => provider.refresh());
}
```

---

## `commands/open-artifact.ts`

```typescript
export function registerOpenArtifactCommand(
  context: vscode.ExtensionContext,
): vscode.Disposable {
  return vscode.commands.registerCommand(
    'agentExplorer.openArtifact',
    async (filePath: string, lineNumber?: number) => {
      const doc = await vscode.workspace.openTextDocument(filePath);
      const editor = await vscode.window.showTextDocument(doc);
      if (lineNumber) {
        const range = new vscode.Range(lineNumber - 1, 0, lineNumber - 1, 0);
        editor.revealRange(range, vscode.TextEditorRevealType.InCenter);
      }
    },
  );
}
```

---

## Status Bar

Item exibido quando o painel está ativo:

```
$(robot) 193 artifacts    ← clique abre o painel
```

```typescript
const statusBar = vscode.window.createStatusBarItem(
  vscode.StatusBarAlignment.Left, 100
);
statusBar.command = 'agentExplorer.refresh';
statusBar.tooltip = 'Agent Explorer — click to refresh';

// Atualiza após cada scan:
statusBar.text = `$(robot) ${result.artifacts.length} artifacts`;
statusBar.show();
```

---

## `onDidChangeConfiguration`

Quando o usuário altera settings do `agentExplorer.*`, re-scan automático:

```typescript
vscode.workspace.onDidChangeConfiguration((e) => {
  if (e.affectsConfiguration('agentExplorer')) {
    provider.refresh();
  }
}, null, context.subscriptions);
```

---

## `extension.ts` final

```typescript
export function activate(context: vscode.ExtensionContext) {
  const provider = new ExplorerViewProvider(context);

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider('agentExplorer.view', provider, {
      webviewOptions: { retainContextWhenHidden: true },
    }),
    registerRefreshCommand(context, provider),
    registerOpenArtifactCommand(context),
    createStatusBar(context, provider),
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (e.affectsConfiguration('agentExplorer')) provider.refresh();
    }),
  );
}
```

---

## Polish

| Item | Detalhe |
|------|---------|
| Scroll position | `retainContextWhenHidden: true` preserva scroll e filtros ativos |
| Erros individuais | Logados com `console.warn`; não quebram o scan |
| Workspace vazio | Estado "No AI artifacts found" (ver `plan-002`) |
| Sidebar muito estreita | Platform chips com `flex-wrap: wrap`; description oculta < 220px |
| Scan lento (> 2s) | Manter spinner; não há timeout — workspaces grandes podem demorar |
| Multi-root workspace | `vscode.workspace.workspaceFolders` → scan em cada raiz, merge results |

---

## `README.md`

Seções:
1. Features (lista de artefatos suportados)
2. Getting started (F5, ícone na Activity Bar)
3. Platform detection (tabela de sinais)
4. Configuration (`agentExplorer.*`)
5. Supported frameworks (Ahrena, Claude Code, Cursor, Agno, Strands)

---

## Empacotamento

```bash
# Instalar vsce se necessário
npm install -g @vscode/vsce

# Empacotar
cd ahrena-vscode
vsce package

# Gera: agent-explorer-0.1.0.vsix
```

`.vscodeignore` já está configurado para excluir `src/`, `test/`, `node_modules/`.

---

## Steps

- [ ] 1. Criar `commands/refresh.ts` e `commands/open-artifact.ts`
- [ ] 2. Criar `commands/index.ts` exportando todos os comandos
- [ ] 3. Adicionar status bar ao `ExplorerViewProvider`
- [ ] 4. Registrar `onDidChangeConfiguration` no `extension.ts`
- [ ] 5. Atualizar `extension.ts` com todos os subscriptions
- [ ] 6. Suporte a multi-root workspace no scanner
- [ ] 7. Criar `README.md`
- [ ] 8. `vsce package` → validar `.vsix`
- [ ] 9. Instalar `.vsix` localmente e testar no workspace do ahrena (end-to-end)

## Dependências

- `plan-006` (webview completo)
- `plan-005` (scanner)
