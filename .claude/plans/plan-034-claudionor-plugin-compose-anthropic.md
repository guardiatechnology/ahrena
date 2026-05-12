---
plan_id: "034"
title: "claudionor-plugin-compose-anthropic"
status: pending
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-09T13:40:00Z"
updated_at: "2026-05-09T13:40:00Z"
---

# Plano: warrior-claudionor — Plugin Compose Anthropic (split de plan-031 Fase D)

## Objetivo

Adicionar a `warrior-claudionor` ([plan-029](plan-029-warrior-claudionor-skill-architect.md) + [plan-031](plan-031-claudionor-anthropic-ecosystem.md)) a capacidade de **gerar plugins Anthropic a partir de clades/subclades do próprio Ahrena** — caminho de auto-publicação do framework como plugin instalável em Claude Code. Cada subclade vira 1 plugin: cada Cry vira `commands/`, cada Warrior vira `agents/`, cada Kata vira `skills/`, e Lexis/Codex são embutidos como instructions. **Originalmente Fase D de plan-031 v1**, foi separado para manter plan-031 focado no propósito core (PoV Factory) — este capability é meta-framework, não core do ciclo PoV→Operação Concreta.

## Contexto

### Por que separado de plan-031

A v1 de plan-031 (pré-reframe) tinha como tema central "expandir Claudionor para o ecossistema Anthropic completo" — skills + subagents + plugins. Após o reframe (Pré-operacional Agent Factory), o core de plan-031 ficou centrado em PoVs de produto Guardia. Plugin compose tem propósito ortogonal: distribuir o **framework Ahrena** como plugins consumíveis pela comunidade Claude Code.

| Capacidade | Plano | Propósito |
|---|---|---|
| Spawn agent PoV (Skill + Subagent) | plan-031 | Provar valor ao cliente Guardia |
| Compose plugin a partir de clade Ahrena | **plan-034 (este)** | Distribuir framework Ahrena como plugin |
| Validar/empacotar plugin | **plan-034** | Idem |

### Mapa de geração (determinístico)

| Componente Anthropic | Equivalente Ahrena | Mapeamento |
|---|---|---|
| Plugin (`.claude-plugin/plugin.json`) | Slice de `framework/{lang}/<clade>/<subclade>/` | 1 subclade → 1 plugin |
| `skills/<name>/SKILL.md` | Kata + Codex que ele consulta | 1 Kata → 1 SKILL.md |
| `commands/<name>.md` | Cry | 1 Cry → 1 command (`cry-foo` → `foo`) |
| `agents/<name>.md` | Warrior | 1 Warrior → 1 agent |
| `hooks/hooks.json` | Settings + automações | Geração opcional |
| `.mcp.json` | `mcp.servers` em `.directives` | Subset por subclade |
| `settings.json` | Default settings | Gerado a partir de paths.platforms |
| `README.md` | Lexis + Codex aplicáveis | Concatena com cross-links resolvidos |

A regra de mapeamento é **determinística** — codificada em `lex-plugin-mapping`.

### Mapeamento de fluxo

```
cry-plugin --mode compose|validate|package|all --clade <C> --subclade <S>
  └─→ warrior-claudionor (capacidade adicional)
        ├─→ kata-plugin-compose
        │     ├─ lê framework/{lang}/<C>/<S>/{lexis,codex,katas,warriors,cries}/
        │     ├─ aplica lex-plugin-mapping
        │     ├─ inline Lexis+Codex como instructions e/ou README
        │     └─ produz {paths.plugins_root}/<plugin-slug>/
        ├─→ kata-plugin-validate
        │     ├─ scripts/plugins/validate.py
        │     ├─ valida .claude-plugin/plugin.json (Anthropic schema)
        │     ├─ valida estrutura per lex-plugin-package-structure
        │     ├─ checa namespacing (sem conflito de skill name)
        │     └─ executa kata-skill-validate (plan-029) em cada skill embutido
        └─→ kata-plugin-package
              ├─ scripts/plugins/package.py
              ├─ aplica paths.plugins_root → paths.plugins_dist
              └─ produz {paths.plugins_dist}/<plugin-slug>.zip

cry-agent --slug <name> [--persona <warrior>]
  └─→ kata-agent-author
        ├─ scaffolda agents/<name>.md com frontmatter Anthropic
        └─ se --persona aponta para warrior existente, importa persona
```

> **Nota:** `kata-agent-author` e `cry-agent` são usados também por plan-031. Este plano os entrega; plan-031 referencia.

## Pré-requisitos

### Bloqueantes

- **plan-029 mergeado:** `warrior-claudionor` v1 + skill katas (`kata-skill-implement`, `kata-skill-validate`, `kata-skill-package`) — base para compose embutir skills
- **plan-031 mergeado:** Claudionor reframado como PoV Factory; `kata-agent-author` opcionalmente já entregue lá ou por este plano (decidir no kickoff)

### Recomendado (não bloqueante)

- **plan-033 mergeado:** `lex-agent-construction-directives` — plugins gerados por subclade `engineering/agents/` declaram `stage:` automaticamente
- **plan-030 mergeado:** `kata-plugin-validate` invoca `check_posthog.py` quando plugin tem widgets UI
- **plan-021 (Ahrena MCP server):** se entregue, plugin pode incluir `.mcp.json` apontando para MCP do Ahrena

## Escopo

### Artefatos a criar (todos em pt-BR + es + en)

| #  | Tipo  | Nome                            | Path                                                                                |
|----|-------|---------------------------------|-------------------------------------------------------------------------------------|
| 1  | Lexis | `lex-plugin-mapping`            | `framework/{lang}/engineering/plugins/lexis/lex-plugin-mapping.md`                  |
| 2  | Lexis | `lex-plugin-package-structure`  | `framework/{lang}/engineering/plugins/lexis/lex-plugin-package-structure.md`        |
| 3  | Codex | `codex-claude-code-plugins`     | `framework/{lang}/engineering/plugins/codex/codex-claude-code-plugins.md`           |
| 4  | Codex | `codex-claude-code-subagents`   | `framework/{lang}/_foundation/tooling/codex/codex-claude-code-subagents.md`         |
| 5  | Kata  | `kata-plugin-compose`           | `framework/{lang}/engineering/plugins/katas/kata-plugin-compose.md`                 |
| 6  | Kata  | `kata-plugin-validate`          | `framework/{lang}/engineering/plugins/katas/kata-plugin-validate.md`                |
| 7  | Kata  | `kata-plugin-package`           | `framework/{lang}/engineering/plugins/katas/kata-plugin-package.md`                 |
| 8  | Cry   | `cry-plugin`                    | `framework/{lang}/engineering/plugins/cries/cry-plugin.md`                          |

**Subclade nova:** `engineering/plugins/` (concentra plugin-specific). Codex de subagents fica em `_foundation/tooling/` (espelha MCP — capacidade da plataforma Claude Code).

### Artefatos a atualizar

| #  | Tipo    | Nome                              | Mudança                                                                                  |
|----|---------|-----------------------------------|------------------------------------------------------------------------------------------|
| 9  | Warrior | `warrior-claudionor`              | Bound katas crescem para incluir kata-plugin-{compose,validate,package}; Lexis carregadas adicionam lex-plugin-{mapping,package-structure} |
| 10 | Cry     | `cry-pov` (plan-031)              | Aceita `--kind plugin` despachando para `cry-plugin`                                      |
| 11 | Config  | `framework/platforms.yaml`        | 2 lex + 2 codex em `cursor.rules`; 3 katas em `cursor.skills` + `claude-code.skills`; 1 cry em `cursor.commands` + `claude-code.commands` |
| 12 | Config  | `.directives.sample`              | Adicionar `paths.plugins_root` (default `plugins/`, committed) e `paths.plugins_dist` (default `.dist-plugins/`, committed) |
| 13 | Lexis   | `lex-directives` (3 línguas)      | Documentar nova seção `paths.plugins_*`                                                  |

### Tooling

| #  | Arquivo                                | Descrição                                                                                       |
|----|----------------------------------------|-------------------------------------------------------------------------------------------------|
| 14 | `scripts/plugins/compose.py`           | Gerador: lê clade/subclade, aplica lex-plugin-mapping, escreve `paths.plugins_root/<slug>/`     |
| 15 | `scripts/plugins/validate.py`          | Validador: checa estrutura per lex-plugin-package-structure + Anthropic schema                  |
| 16 | `scripts/plugins/package.py`           | Empacotador: tarball/zip pronto para marketplace ou `--plugin-url`                              |
| 17 | `scripts/plugins/__init__.py` + tests  | Fixtures: clade simples; clade complexa; plugin com hooks; plugin com MCP                        |

### Marketplace (Fase futura — fora deste plano)

- `.claude-plugin/marketplace.json` agregando todos os plugins gerados — quando tivermos ≥3 plugins maduros em produção
- CI workflow `plugins-build.yml` (regerar e checar drift em PR) — só faz sentido depois de marketplace ativo

## Steps

### Bloco A — Codex de referência

- [ ] **A.1.** Issue (`feature-request`, labels `feature request ➕` + `framework` + `plugins`, Issue Type `Feature`, assignee `@me`)
- [ ] **A.2.** Branch `feat/{N}-claudionor-plugin-compose-anthropic` em worktree
- [ ] **A.3.** Status do plan → `in-progress`
- [ ] **A.4.** `codex-claude-code-plugins.md` (pt-BR) — estrutura completa de plugin per [code.claude.com/docs/en/plugins](https://code.claude.com/docs/en/plugins) (manifest, skills/, commands/, agents/, hooks/, .mcp.json, settings.json), namespacing, marketplace, distribuição
- [ ] **A.5.** Tradução `codex-claude-code-plugins` (es + en)
- [ ] **A.6.** `codex-claude-code-subagents.md` (pt-BR) — formato `agents/<name>.md`, frontmatter, comparação com warriors
- [ ] **A.7.** Tradução `codex-claude-code-subagents` (es + en)

### Bloco B — Lexis de regras

- [ ] **B.1.** `lex-plugin-package-structure.md` (pt-BR) — HARD-GATE: estrutura final obrigatória; preconditions; counter-pretextos
- [ ] **B.2.** Tradução `lex-plugin-package-structure` (es + en)
- [ ] **B.3.** `lex-plugin-mapping.md` (pt-BR) — tabela determinística (Pilar Ahrena → componente Anthropic); HARD-GATE: gerador MUST aplicar a tabela sem desvios silenciosos
- [ ] **B.4.** Tradução `lex-plugin-mapping` (es + en)
- [ ] **B.5.** Atualizar `framework/platforms.yaml` com 4 entradas (2 lex + 2 codex)
- [ ] **B.6.** Atualizar `.directives.sample` com `paths.plugins_root` e `paths.plugins_dist`
- [ ] **B.7.** Atualizar `lex-directives` (3 línguas) — documentar seção `paths.plugins_*`

### Bloco C — Tooling (scripts)

- [ ] **C.1.** `scripts/plugins/compose.py` — gerador determinístico
- [ ] **C.2.** `scripts/plugins/validate.py` — validador per lex + Anthropic schema
- [ ] **C.3.** `scripts/plugins/package.py` — tarball/zip
- [ ] **C.4.** Tests dos 3 scripts com fixtures

### Bloco D — Katas e Cry

- [ ] **D.1.** `kata-plugin-compose.md` (pt-BR) — invoca compose.py; sequência de validação pós-geração
- [ ] **D.2.** Tradução `kata-plugin-compose` (es + en)
- [ ] **D.3.** `kata-plugin-validate.md` (pt-BR) — invoca validate.py; itera kata-skill-validate (plan-029) sobre cada skill embutido; invoca check_posthog.py (plan-030) quando aplicável
- [ ] **D.4.** Tradução `kata-plugin-validate` (es + en)
- [ ] **D.5.** `kata-plugin-package.md` (pt-BR) — invoca package.py; valida resultado
- [ ] **D.6.** Tradução `kata-plugin-package` (es + en)
- [ ] **D.7.** `cry-plugin.md` (pt-BR) — `--mode compose|validate|package|all`, `--clade <C>`, `--subclade <S>`, `--dry-run`
- [ ] **D.8.** Tradução `cry-plugin` (es + en)

### Bloco E — Atualizações em Claudionor e cross-links

- [ ] **E.1.** Atualizar `warrior-claudionor` (3 línguas) — bound katas crescem; Lexis carregadas adicionam lex-plugin-*
- [ ] **E.2.** Atualizar `cry-pov` (plan-031, 3 línguas) — aceita `--kind plugin` despachando para `cry-plugin`
- [ ] **E.3.** Sync — `python3 scripts/install.py --self --target . --platform {claude-code,cursor}`

### Bloco F — Dogfood (gerar primeiro plugin a partir de clade real)

- [ ] **F.1.** Eleger clade-piloto — proposta: `_foundation/contributing/` (cries de commit/tag/sync; pequeno e bem coberto)
- [ ] **F.2.** Rodar `cry-plugin --mode all --clade _foundation --subclade contributing` — gerar `plugins/ahrena-contributing/`
- [ ] **F.3.** Validar localmente — `claude --plugin-dir plugins/ahrena-contributing` e testar 1 command + 1 agent gerado
- [ ] **F.4.** Repetir para `engineering/backend/` — clade densa (6 katas + 1 warrior + 2 cries); valida o gerador no caso real
- [ ] **F.5.** Documentar achados — adicionar seção "Plugins gerados" em README do framework com lista e instruções via `--plugin-dir`

### Bloco G — Fechamento

- [ ] **G.1.** Commits atômicos:
  1. `feat(plugins): add codex-claude-code-{plugins,subagents}`
  2. `feat(plugins): add lex-plugin-{mapping,package-structure}`
  3. `feat(plugins): add scripts/plugins + tests`
  4. `feat(plugins): add kata-plugin-{compose,validate,package} + cry-plugin`
  5. `chore(plugins): cross-link claudionor + cry-pov + directives + platforms.yaml`
  6. `feat(plugins): dogfood ahrena-contributing + ahrena-backend plugins`
  7. `chore: sync .claude and .cursor`
- [ ] **G.2.** PR via `kata-contributing-pr` — `Closes #{N}`, mirroring + `plugins`, size, CODEOWNERS; body referencia plan-034 + plan-029 + plan-031
- [ ] **G.3.** Pós-merge — status `done` → `archived`, remover worktree

## Dependências

### Bloqueantes

- **plan-029** mergeado (Claudionor v1 + skill katas)
- **plan-031** mergeado (Claudionor reframado + kata-agent-author + cry-pov)

### Recomendado

- **plan-033** mergeado (lex-agent-construction-directives) — plugins gerados de `engineering/agents/` declaram `stage:` automaticamente
- **plan-030** mergeado (analytics) — `check_posthog.py` em validate
- **plan-021** mergeado (Ahrena MCP) — `.mcp.json` em plugins gerados

### Independente

- plan-013, plan-027, plan-028, plan-032

## Riscos

| # | Risco | Probab. | Mitigação |
|---|---|:------:|---|
| 1 | Mapeamento determinístico (`lex-plugin-mapping`) é insuficiente — Cries/Warriors com semântica especial não cabem | Alta | Lex declara overrides explícitos por path em `.directives` (`plugins.overrides[]`); fallback "skip + warning" |
| 2 | Plugin gerado a partir de clade pequena vira "plugin de 1 comando" sem valor | Média | Threshold mínimo no compose.py: ≥2 artefatos coerentes; abaixo emite "skip with reason" e sugere agrupamento |
| 3 | Frontmatter Anthropic muda e gerador fica obsoleto | Alta | codex-claude-code-plugins versionado por data; teste de "schema atual" em CI; alerta quando Anthropic muda |
| 4 | Inlining de Lexis+Codex em README do plugin gera README de 50KB | Média | compose.py aplica truncamento + cross-link para repositório fonte; README focado em "como usar" |
| 5 | Conflito de namespace: `cry-commit` (Ahrena) → `commit` em outro plugin existente | Média | Plugin name = `ahrena-<subclade>`; namespace garantido por Anthropic (`ahrena-contributing:commit`) |
| 6 | Multilingue incompleto: 8 artefatos × 3 línguas = 24 arquivos | Alta | Steps separados por língua; PR pode ser stacked |
| 7 | Subagents/plugins funcionam só em Claude Code, não em Cursor — falsa expectativa | Baixa | codex-claude-code-plugins é explícito "Claude Code only"; Cursor não tem plugin equivalent (ainda) |

## Decisões em aberto

- **Naming convenção do plugin gerado:** `ahrena-{subclade}` ou `ahrena-{clade}-{subclade}` para clades multi-subclade. Decidir antes de C.1
- **`paths.plugins_root` committed ou gitignored:** proposta committed (igual `paths.skills_dist`); permite review em PR
- **Hooks gerados automaticamente:** Fase A não gera. Fase futura pode mapear `update-config` → `hooks/hooks.json`
- **Marketplace official Anthropic vs. self-hosted git:** defer para plano futuro de publicação
- **Versionamento do plugin gerado:** proposta inicial: `version` = git commit SHA do Ahrena na hora da geração; considerar `version` explícito derivado de tag `v*.*.*` para releases curados
- **`kata-agent-author` é entregue aqui ou em plan-031:** decidir no kickoff. Proposta: plan-031 entrega (faz parte do core PoV); plan-034 referencia

## Verificação

1. **Estrutura entregue:** 8 artefatos × 3 línguas + 3 scripts + tests = ~30 arquivos
2. **Atualizações:** warrior-claudionor (3), cry-pov (3), platforms.yaml, .directives.sample, lex-directives (3), .claude/, .cursor/
3. **Pré-requisitos:** plan-029 + plan-031 mergeados
4. **Dogfood (F.2-F.4):** ≥2 plugins reais gerados, validados, testáveis via `--plugin-dir`
5. **HARD-GATE de PR:** atende `lex-pr-quality`
6. **Body da PR final:** referencia plan-034, plan-029, plan-031; lista plugins gerados como evidência
