import * as vscode from 'vscode';
import { ExplorerViewProvider } from './webview/explorer-view-provider';

export function activate(context: vscode.ExtensionContext): void {
  const provider = new ExplorerViewProvider(context);

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider('agentExplorer.view', provider, {
      webviewOptions: { retainContextWhenHidden: true },
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('agentExplorer.refresh', () => provider.refresh()),
  );
}

export function deactivate(): void {}
