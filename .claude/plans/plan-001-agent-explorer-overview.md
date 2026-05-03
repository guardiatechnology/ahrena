---
plan_id: "001"
title: "agent-explorer-overview"
status: in-progress
agent: claude
created_at: "2026-05-03T00:00:00Z"
updated_at: "2026-05-03T00:00:00Z"
---

# Plan: Agent Explorer — Overview

## Objetivo

Extensão VS Code que cataloga e visualiza todos os artefatos de IA de um workspace numa interface
estilo VS Code Extensions: cards com ícone, nome, descrição e badges de plataforma, organizados
por tipo de artefato, com filtro por plataforma instalada.

Localização: `ahrena/ahrena-vscode/`

---

## Modelo de Dados: Artefato × Plataforma

| Eixo | Tipo | Valores |
|------|------|---------|
| **Kind** (`ArtifactKind`) | O que é | `lex` · `codex` · `kata` · `warrior` · `cry` · `tool` · `mcp` |
| **Platform** (`PlatformId`) | Onde está | `ahrena` · `claude` · `cursor` · `agno` · `strands` |

Um artefato pode ter múltiplas plataformas. Ex: `.claude/rules/lex-python-error-handling.md`
→ `kind: 'lex'`, `platforms: ['ahrena', 'claude']`

### Detecção de plataformas instaladas

| Sinal | Plataforma |
|-------|-----------|
| Diretório `.ahrena/` existe | `ahrena` |
| Diretório `.claude/` existe | `claude` |
| Diretório `.cursor/` existe | `cursor` |
| Qualquer `.py` importa `agno` | `agno` |
| Qualquer `.py` importa `strands` | `strands` |

---

## Artefatos Suportados

| Kind | Fonte | Identificador | Campos extraídos |
|------|-------|---------------|-----------------|
| `lex` | `lex-*.md` em `.claude/rules/`, `lex-*.mdc` em `.cursor/rules/` | filename `lex-*` | name, description |
| `codex` | `codex-*.md` + `codex-*.mdc` (mesmos dirs) | filename `codex-*` | name, description |
| `kata` | `SKILL.md` em `.claude/skills/kata-*/`, `.cursor/skills/kata-*/` | frontmatter `name` | name, description |
| `warrior` | `warrior-*.md` (Ahrena), `*.md` em `.claude/agents/`, `Agent()` em `.py` | filename / path | name, description, model |
| `cry` | `cry-*.md` em `.claude/commands/`, `.cursor/commands/**/` | filename `cry-*` | name, description |
| `tool` | `*.py` com `@tool` (Agno / Strands) | decorator + fn name | name, description (docstring) |
| `mcp` | `.cursor/mcp.json`, `.mcp.json`, `settings.json` | `mcpServers` key | name, url/command |

---

## Estrutura de Pastas

```
ahrena-vscode/
├── src/
│   ├── extension.ts
│   ├── types.ts
│   ├── constants.ts
│   ├── platform/detector.ts
│   ├── detectors/{lex,codex,kata,warrior,cry,python,mcp,index}.ts
│   ├── parsers/{frontmatter,markdown-title,python-agent}.ts
│   ├── scanner/{workspace-scanner,file-watcher}.ts
│   ├── webview/{explorer-view-provider,message-handler}.ts
│   ├── webview/html/{build-html,template,style.css}.ts
│   └── commands/{index,refresh,open-artifact}.ts
├── media/
│   ├── explorer-icon.svg
│   └── icons/{lex,codex,kata,warrior,cry,tool,mcp}.svg
└── test/
    ├── fixtures/
    └── suite/{parsers,detectors,platform}/
```

---

## Sub-planos

| Plano | Escopo |
|-------|--------|
| `plan-002` | UI detalhada: layout, cards, filtros, estados, CSS |
| `plan-003` | Parsers: frontmatter, markdown-title, python-agent |
| `plan-004` | Detectors: um por kind, dedup, plataformas atribuídas |
| `plan-005` | Scanner + Platform detector + FileSystemWatcher |
| `plan-006` | WebviewView: HTML/CSS/JS, mensagens, provider |
| `plan-007` | Wiring: comandos, config, status bar, polish, .vsix |
