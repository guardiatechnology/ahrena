import * as vscode from 'vscode';
import { AgentExplorerConfig, ArtifactKind } from '../types';
import { CONFIG_KEY } from '../constants';

export function getConfig(): AgentExplorerConfig {
  const cfg = vscode.workspace.getConfiguration(CONFIG_KEY);
  return {
    enabled:             cfg.get<boolean>('enabled', true),
    additionalPaths:     cfg.get<string[]>('additionalPaths', []),
    watchDelay:          cfg.get<number>('watchDelay', 500),
    defaultExpandedKinds: cfg.get<ArtifactKind[]>('defaultExpandedKinds', ['warrior', 'kata', 'mcp']),
  };
}
