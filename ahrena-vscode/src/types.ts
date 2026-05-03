export type ArtifactKind = 'lex' | 'codex' | 'kata' | 'warrior' | 'cry' | 'tool' | 'mcp';
export type PlatformId   = 'ahrena' | 'claude' | 'cursor' | 'agno' | 'strands';

export interface ArtifactDefinition {
  id: string;                        // `${kind}::${filePath}::${name}`
  name: string;
  description: string;
  kind: ArtifactKind;
  platforms: PlatformId[];
  filePath: string;
  lineNumber?: number;
  rawFields: Record<string, unknown>;
}

export interface KindMeta {
  kind: ArtifactKind;
  label: string;
  iconFile: string;
  defaultExpanded: boolean;
}

export interface PlatformMeta {
  id: PlatformId;
  label: string;
  color: string;
}

export interface ArtifactDetector {
  readonly kind: ArtifactKind;
  readonly fileGlob: string | string[];
  detect(filePath: string, content: string): ArtifactDefinition[];
}

export interface ScanError {
  filePath: string;
  message: string;
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

export type WebviewMessage =
  | { type: 'ready' }
  | { type: 'openArtifact'; filePath: string; lineNumber?: number }
  | { type: 'filterChanged'; platform: PlatformId | 'all'; query: string };

export type ExtensionMessage =
  | { type: 'scanResult'; result: ScanResult }
  | { type: 'loading' };
