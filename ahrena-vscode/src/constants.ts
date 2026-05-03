import type { ArtifactKind, KindMeta, PlatformId, PlatformMeta } from './types';

export const KIND_ORDER: ArtifactKind[] = ['lex', 'codex', 'kata', 'warrior', 'cry', 'tool', 'mcp'];

export const KIND_META: Record<ArtifactKind, KindMeta> = {
  lex:     { kind: 'lex',     label: 'Lex',      iconFile: 'lex.svg',     defaultExpanded: false },
  codex:   { kind: 'codex',   label: 'Codex',    iconFile: 'codex.svg',   defaultExpanded: false },
  kata:    { kind: 'kata',    label: 'Katas',    iconFile: 'kata.svg',    defaultExpanded: true  },
  warrior: { kind: 'warrior', label: 'Warriors', iconFile: 'warrior.svg', defaultExpanded: true  },
  cry:     { kind: 'cry',     label: 'Cries',    iconFile: 'cry.svg',     defaultExpanded: false },
  tool:    { kind: 'tool',    label: 'Tools',    iconFile: 'tool.svg',    defaultExpanded: false },
  mcp:     { kind: 'mcp',     label: 'MCPs',     iconFile: 'mcp.svg',     defaultExpanded: true  },
};

export const PLATFORM_META: Record<PlatformId, PlatformMeta> = {
  ahrena:  { id: 'ahrena',  label: 'Ahrena',  color: '#7C3AED' },
  claude:  { id: 'claude',  label: 'Claude',  color: '#E07400' },
  cursor:  { id: 'cursor',  label: 'Cursor',  color: '#0078D4' },
  agno:    { id: 'agno',    label: 'Agno',    color: '#00BF63' },
  strands: { id: 'strands', label: 'Strands', color: '#DB6286' },
};

export const CONFIG_KEY = 'agentExplorer';
