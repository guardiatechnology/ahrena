# Codex: Arquitetura de Projeto de Skill (Ahrena)

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Estrutura interna de um projeto de skill no repositório Ahrena (`skills/{slug}/`), papel de cada subdiretório, ciclo `dev → build → dist`, e reuso dos codex de arquitetura existentes durante a autoria

## Conteúdo

### Layout canônico do projeto fonte

```
skills/{slug}/
├── SKILL.md                    # Frontmatter Agent Skills + corpo (orquestra os demais artefatos)
├── .skill-manifest.json        # Esqueleto; preenchido com refs+hashes pelo build
├── skill.config.json           # Config local do projeto (idioma, runtimes, ports do dev server)
├── references/                 # Markdown adicional (level-3 da spec) — opcional
├── scripts/                    # JS ou Python — utilitários executáveis pelo agente — opcional
│   ├── package.json            # quando JS
│   ├── pyproject.toml          # quando Python
│   └── src/
├── tools/                      # MCP tools (lógica) — convenção Ahrena, opcional
│   ├── mcp.config.json
│   └── handlers/
└── widgets/                    # React (TS) — UI — convenção Ahrena, opcional
    ├── package.json
    ├── manifest.json
    └── src/
```

`{slug}` é kebab-case válido per spec Anthropic (`a-z`, `0-9`, hífen; sem hífen no início/fim; sem `--`; **idêntico ao `name` no SKILL.md**).

### Mapeamento spec Anthropic ↔ projeto Ahrena

| Item | Onde fica na spec (`.dist/{slug}/`) | Onde fica no projeto fonte (`skills/{slug}/`) | Status |
|------|--------------------------------------|------------------------------------------------|--------|
| `SKILL.md` | raiz | raiz | nativo da spec |
| `references/` | raiz | raiz | nativo |
| `scripts/` | raiz (executáveis prontos) | raiz (fonte; build congela em `.build/`) | nativo |
| `assets/` | raiz | (criado pelo autor quando necessário) | nativo |
| `tools/` (MCP) | raiz | raiz | **convenção Ahrena**, fora da spec |
| `widgets/` (React) | raiz | raiz | **convenção Ahrena**, fora da spec |
| `.skill-manifest.json` | raiz | raiz (esqueleto, completado no build) | **convenção Ahrena** |
| `skill.config.json` | (não vai pro pacote) | raiz | **convenção Ahrena** (apenas dev/build) |

Convenções Ahrena (`tools/`, `widgets/`, `.skill-manifest.json`) são **extensões** da spec — agentes externos que só conhecem a spec ignoram esses diretórios; agentes que conhecem a convenção Ahrena consomem.

### `SKILL.md` no projeto fonte

O `SKILL.md` no projeto fonte é o mesmo arquivo que vai pro pacote final (build apenas reescreve paths relativos quando necessário). Estrutura mínima:

```markdown
---
name: scheduled-payments-skill
description: Schedules and approves bank transfers using widgets connected to Python tools. Use when the user wants to create or approve a scheduled transfer.
license: Apache-2.0
metadata:
  version: "0.1.0"
  language: pt-BR
  spec_version: "agentskills.io/specification@2026-04"
---

# Scheduled Payments Skill

## Quando usar
{...}

## Fluxo
1. Renderize o widget `widgets/transfer-form/` para o usuário.
2. Quando o usuário confirma, invoque a tool `tools/handlers/create_transfer.py`.
3. Mostre o resultado no widget de confirmação.

## Restrições

- **Skill não é Pilar do framework.** Não tem prefix em `framework/`, não aparece em `naming.prefixes`. É projeto externo governado pelos artefatos deste codex e do `lex-skill-project-structure`.
- **Convenções Ahrena (`tools/`, `widgets/`) são opcionais.** Skills podem existir só com `SKILL.md` + `scripts/`/`references/` puros da spec. A convenção entra quando o skill precisa de UI ou MCP próprio.
- **Mono-idioma por skill.** `metadata.language` declara um idioma; produzir o mesmo skill em pt-BR e en exige dois projetos `skills/{slug}-ptbr/` e `skills/{slug}-en/` ou um mecanismo de localização interno (não governado neste PR).
- **Slug do diretório == `name` do frontmatter.** Spec exige; `kata-init-skill` valida.
