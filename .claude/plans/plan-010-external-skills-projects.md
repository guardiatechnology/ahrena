---
plan_id: "010"
title: "external-skills-projects"
status: in-progress
agent: claude
issue: "guardiatechnology/ahrena#58"
created_at: "2026-05-07T12:00:00Z"
updated_at: "2026-05-07T18:45:00Z"
---

# Plano: Skills Externos como Projetos (Desenvolvimento + Build + Empacotamento)

## Objetivo

Tratar cada Skill externo como um **projeto de primeira classe** dentro do repositório, com (a) fase de desenvolvimento que segue os Pilares Ahrena e os codex de arquitetura existentes, (b) build local testável em `localhost`, e (c) empacotamento determinístico para entrega no formato Anthropic Agent Skills.

O bundle final é, conceitualmente, um **warrior externo**: agente especializado que combina widgets (frontend), scripts e tools (lógica) em um pacote auto-contido consumível por agentes fora do Ahrena.

## Contexto

### Decisões fechadas

| Decisão | Valor |
|---|---|
| Spec alvo | Anthropic Agent Skills (`SKILL.md` + bundle) |
| Layout do projeto fonte | `skills/{slug}/` com `SKILL.md`, `.skill-manifest.json`, `references/`, `scripts/`, `tools/`, `widgets/` |
| Build intermediário | `.build/{slug}/` + `.build/{slug}.zip` (testável em localhost) |
| Entrega final | `.dist/{slug}.skill` (ou diretório, conforme spec) |
| Widgets | React |
| Scripts | JS ou Python (escolha por contexto), conectáveis aos widgets |
| Test local | localhost (dev server orquestrando widgets + scripts/tools) |
| Pilares Ahrena na autoria | Sim — codex de arquitetura existentes governam o conteúdo |
| Skill é Pilar do framework? | Não — é projeto externo. Framework apenas governa a autoria e o build |

### Reuso de codex existentes (autoria)

| Codex existente | Uso no projeto de skill |
|---|---|
| `codex-frontend-architecture` | Arquitetura de `widgets/` (camadas, estado, hooks, services) |
| `codex-python-architecture` | Arquitetura de `tools/` e `scripts/` quando Python |
| `codex-python-tooling`, `codex-python-testing`, `codex-python-logging` | Setup de scripts/tools Python |
| `codex-oas-structure` | Quando uma tool expõe HTTP local |
| `codex-warriors` | Modelo conceitual — bundle ≈ warrior externo |
| `lex-frontend-typing`, `lex-frontend-accessibility`, `lex-frontend-security`, `lex-frontend-testing` | Aplicáveis aos widgets sem alteração |
| `lex-python-typing`, `lex-python-testing`, `lex-python-security`, `lex-python-error-handling` | Aplicáveis a scripts/tools Python |
| `lex-design-system-library`, `lex-brand-*` | Widgets respeitam DS e marca quando renderizados em superfície Guardia |

**Lacuna real:** não existe codex que defina a **arquitetura de um projeto de skill** (estrutura de `skills/{slug}/`, papel de cada subdiretório, ciclo dev → build → dist, ponte widget ↔ script). Isso é genuinamente novo.

## Escopo

### Layout canônico do projeto fonte

```
skills/{slug}/
├── SKILL.md                          # frontmatter (name, description, allowed-tools, version) + corpo
├── .skill-manifest.json              # metadados: refs externas, hashes (preenchido no build)
├── skill.config.{json|yaml}          # config de build: dev server, ports, runtime de scripts
├── references/                       # snapshots de lex/codex/kata externos do framework Ahrena
├── scripts/                          # JS ou Python — utilitários conectáveis a widgets
│   ├── package.json | pyproject.toml
│   └── src/...
├── tools/                            # MCP tools (lógica do agente)
│   ├── mcp.config.json
│   └── handlers/...
└── widgets/                          # React (TS) — componentes UI
    ├── package.json
    ├── manifest.json                 # nome, props, eventos, binding com scripts/tools
    └── src/...
```

### Layout dos diretórios de saída

```
.build/                               # gitignored
└── {slug}/
    ├── widgets/                      # bundle React compilado
    ├── scripts/                      # scripts prontos para execução
    ├── tools/                        # tools MCP empacotadas
    ├── SKILL.md                      # cópia + ajustes
    ├── .skill-manifest.json          # com hashes
    └── {slug}.zip                    # zip testável em localhost

.dist/                                # committed
└── {slug}.skill                      # entrega final (formato Anthropic — diretório ou arquivo)
```

### Pipeline de build

```
skills/{slug}/                        kata-build-skill                 .build/{slug}/
   widgets/  (React TS) ─────────►  vite/esbuild bundle  ──────►  widgets/ (JS bundled)
   scripts/  (JS|Python) ────────►  freeze + deps lock   ──────►  scripts/ runnable
   tools/    (MCP)        ────────►  validate config      ──────►  tools/   ready
   references (stub)      ────────►  resolve commit hash  ──────►  references/ snapshotted
   SKILL.md + manifest    ────────►  rewrite refs paths   ──────►  SKILL.md + manifest

                                      kata-package-skill
                                            │
                                            ▼
                                      .dist/{slug}.skill
```

### Dev workflow (localhost)

1. `cry-skill-dev {slug}` levanta:
   - **Widget dev server** (Vite com HMR) em `localhost:5173`
   - **Script runner** (Node ou Python) em `localhost:5174` quando o skill tem scripts conectados
   - **Tools MCP local** stub se aplicável
2. Widget chama script via `fetch('http://localhost:5174/...')` durante dev (configurado em `skill.config`).
3. No build, o `manifest.json` do widget declara o binding `script: "./scripts/foo.py"` que o host agente resolve em runtime.

### Artefatos novos no framework Ahrena (3 idiomas)

| Pilar | Arquivo | Papel |
|---|---|---|
| Codex | `engineering/skills/codex/codex-skill-project-architecture.md` | Layout `skills/{slug}/`, papel de cada subdir, fluxo dev → build → dist, binding widget ↔ script, `skill.config` |
| Codex | `engineering/skills/codex/codex-skill-anthropic-agent-skills.md` | Manual da spec Anthropic (frontmatter, file refs, packaging) com URL e versão validadas |
| Codex | `engineering/skills/codex/codex-skill-tools-and-widgets.md` | Convenção Ahrena para `tools/` (MCP) e `widgets/` (React + manifest); aviso "não é parte da spec Anthropic" |
| Codex | `engineering/skills/codex/codex-skill-build-pipeline.md` | Pipeline de build determinística, cache, hashes, ordering, integração com Vite/esbuild |
| Lexis | `engineering/skills/lexis/lex-skill-project-structure.md` | Obriga layout `skills/{slug}/`, presença de `SKILL.md` + `skill.config`, separação fonte/build/dist |
| Lexis | `engineering/skills/lexis/lex-skill-package-structure.md` | Frontmatter SKILL.md obrigatório, `.skill-manifest.json` válido, refs com hash; HARD-GATE bloqueia entrega sem manifest válido |
| Lexis | `engineering/skills/lexis/lex-skill-export-determinism.md` | Snapshot por commit hash, ordering lexicográfico, sem timestamps voláteis, rebuild idêntico |
| Kata | `engineering/skills/katas/kata-init-skill.md` | Scaffold de `skills/{slug}/` com templates de `SKILL.md`, `skill.config`, subdirs vazios, `.gitignore` herdado |
| Kata | `engineering/skills/katas/kata-build-skill.md` | Compila widgets, congela scripts, valida tools, escreve `.build/{slug}/` + zip |
| Kata | `engineering/skills/katas/kata-package-skill.md` | A partir de `.build/{slug}/`, snapshota refs externas com commit hash, escreve `.dist/{slug}.skill` |
| Kata | `engineering/skills/katas/kata-skill-dev-server.md` | Sobe dev server (widgets HMR + script runner + tools stub) em localhost |
| Cry | `engineering/skills/cries/cry-new-skill.md` | Atalho — invoca `kata-init-skill` |
| Cry | `engineering/skills/cries/cry-skill-dev.md` | Atalho — invoca `kata-skill-dev-server` |
| Cry | `engineering/skills/cries/cry-skill-build.md` | Atalho — invoca `kata-build-skill` (e opcionalmente `kata-package-skill`) |
| Templates | `templates/skill-project-sample/` | Diretório-template com `SKILL.md`, `skill.config.json`, `widgets/package.json`, `scripts/`, `tools/` mínimos |

### Atualizações em artefatos existentes

| Arquivo | Mudança |
|---|---|
| `framework/.directives.sample` | Adicionar `paths.skills_root: skills`, `paths.skills_build: .build`, `paths.skills_dist: .dist` |
| `_foundation/process/lexis/lex-directives.md` | Acrescentar entradas na tabela "Application by section" |
| `framework/platforms.yaml` | Registrar 4 codex + 3 lex em `cursor.rules`; 3 cries em `cursor.commands` |
| `.gitignore` (template do projeto) | `.build/` ignorado; `.dist/` committed |

### Diretivas novas

```yaml
paths:
  skills_root: skills        # diretório fonte dos projetos de skill
  skills_build: .build       # intermediário (gitignored)
  skills_dist: .dist         # entrega final (committed)
```

### Frontmatter SKILL.md canônico

```yaml
---
name: skill-name
description: "Frase única descrevendo quando o agente deve invocar este skill"
allowed-tools: ["Read", "Bash", "mcp__custom__tool_x"]
version: 0.1.0
language: pt-BR
---
```

### `.skill-manifest.json` (preenchido pelo build)

```json
{
  "schema_version": 1,
  "skill": { "name": "skill-name", "version": "0.1.0", "language": "pt-BR" },
  "framework": { "ahrena_commit": "abc123..." },
  "references": [
    {
      "kind": "lexis",
      "id": "_foundation/tooling/lexis/lex-mcp",
      "source_commit": "def456...",
      "snapshot_path": "references/lex-mcp.md",
      "snapshot_sha256": "..."
    }
  ],
  "files": [
    { "path": "SKILL.md", "sha256": "..." },
    { "path": "widgets/dist/index.js", "sha256": "..." }
  ]
}
```

## Por que não sobrepõe o que existe

| Existente | Papel | Novo | Conflito? |
|---|---|---|---|
| `kata-create-{lexis,codex,kata,warrior}` | Cria fonte interna em `framework/{lang}/` | `kata-init-skill` cria projeto em `skills/{slug}/` | Não — destinos distintos |
| `cry-new-{lex,kata,warrior}` | Atalhos de criação interna | `cry-new-skill` | Não |
| `codex-frontend-architecture`, `codex-python-architecture` | Arquiteturas | Reusados pelos widgets/scripts/tools | Reuso, não duplicação |
| `lex-frontend-*`, `lex-python-*` | Regras de qualidade | Aplicam-se aos widgets/scripts/tools sem ajuste | Reuso |
| `paths.*` no `.directives` | Caminhos canônicos | `paths.skills_root/build/dist` adicionados | Aditivo |

## Passos

### PR 1 — foundation (issue #58)

- [x] Abrir issue `feat: external skills foundation (1/3)` — guardiatechnology/ahrena#58
- [x] Criar branch `feat/58-external-skills-foundation` + worktree
- [x] Validar URL/versão atual da spec Anthropic Agent Skills (agentskills.io/specification)
- [x] **Codex** `codex-skill-project-architecture` (pt-BR)
- [x] **Codex** `codex-skill-anthropic-agent-skills` (pt-BR)
- [x] **Lexis** `lex-skill-project-structure` (pt-BR)
- [x] **Template** `templates/skill-project-sample/` com SKILL.md, skill.config.json, widgets+scripts+tools mínimos
- [x] **Kata** `kata-init-skill` (pt-BR)
- [x] **Cry** `cry-new-skill` (pt-BR)
- [x] Atualizar `framework/.directives.sample` (3 paths novos: skills_root/build/dist)
- [x] Atualizar `lex-directives.md` tabela (pt-BR, es, en)
- [x] Atualizar `framework/platforms.yaml` (cursor.rules + claude-code.rules + claude-code.docs)
- [x] Traduzir tudo para `es` (lex-language, lex-language-es)
- [x] Traduzir tudo para `en` (lex-language, lex-language-en)
- [x] Sync `.cursor/` e `.claude/` (`scripts/install.py --self --platform cursor` + `--platform claude-code`)
- [x] **Smoke 1:** scaffold de `skills/hello-skill/` produz layout válido, name=slug, sem placeholders
- [x] `.gitignore` atualizado com `.build/`
- [ ] Commits atômicos assinados (lex-small-commits, lex-conventional-commits, lex-signed-commits)
- [ ] Abrir PR (lex-pr-quality) com `Closes #58`
- [ ] Após merge: registrar progresso e abrir issue do PR 2

### PR 2 — build pipeline (issue #60) — **REVERTIDO no PR de cleanup #63**

- [x] Mergeado em main como `feat: external skills build pipeline (2/3)` — guardiatechnology/ahrena#60 / PR #61
- [x] Conteúdo entregue: codex-skill-tools-and-widgets, codex-skill-build-pipeline, kata-skill-dev-server, kata-build-skill, cry-skill-dev, cry-skill-build (3 idiomas)
- [~] **Reescopado:** após review com o maintainer, `codex-skill-build-pipeline`, `kata-skill-dev-server`, `kata-build-skill`, `cry-skill-dev`, `cry-skill-build` foram **removidos** no PR de cleanup (issue #63). Razão: Ahrena governa **autoria** + **estrutura de saída**; build/release pertence à stack do projeto consumidor (Makefile, GitHub Actions, npm scripts, uv). A spec não deve prescrever Vite/uv/ports/comandos zip.
- [x] Mantidos: `codex-skill-tools-and-widgets` (convenção de manifestos — autoria) + smoke `skills/hello-skill/` (widget + script + tool + manifests).

### PR cleanup — issue #63

- [x] Abrir issue `chore(framework): remove prescriptive build/release artifacts` — guardiatechnology/ahrena#63
- [x] Branch `chore/63-cleanup-prescriptive-build` + worktree
- [x] `git rm` 5 fontes × 3 idiomas (15) + 13 derivados (`.cursor/.claude/`)
- [x] `framework/platforms.yaml`: 2 keys removidas (codex-skill-build-pipeline em cursor.rules + claude-code.docs)
- [x] Trim cross-refs em codex-skill-tools-and-widgets, codex-skill-project-architecture, codex-skill-anthropic-agent-skills, lex-skill-project-structure, kata-init-skill, cry-new-skill (3 idiomas)
- [x] `skill.config.json`: drop blocos `dev_server` e `build` (template + hello-skill)
- [x] Sync `.cursor/` e `.claude/`
- [ ] Commits atômicos + PR #63

### `lex-skill-package-structure` — entregue **junto** ao cleanup PR #64

- [x] **Lexis** `lex-skill-package-structure` (3 idiomas) — lei do output `.skill`, agnostic ao build
  - HARD-GATE com 5 critérios canônicos: frontmatter Anthropic válido; manifest contra schema (com `framework.ahrena_commit` não-vazio); `files[].sha256` confere; `references[].source_commit` não-vazio + `snapshot_sha256` confere; zero arquivos órfãos
  - Schema canônico do `.skill-manifest.json` documentado na lei
  - Não prescreve Vite/uv/ports/zip — stack do projeto consumidor decide o build
- [x] `framework/platforms.yaml`: registro em cursor.rules + claude-code.rules (com glob `.dist/**`)

### Pós-cleanup — arquivar plan-010

- [ ] Após merge do #64: mover este plano para `.claude/plans/archive/`

## Dependências

Nenhum dos plans 005–008 bloqueia este — independente.

Decisões de tooling a tomar durante a redação dos codex:

- **Bundler de widgets:** Vite (recomendado por velocidade + zero-config para React) vs esbuild puro vs Webpack
- **Runtime de scripts JS:** Node 20 LTS
- **Runtime de scripts Python:** uv + Python 3.12 (alinhado a `codex-python-tooling`)
- **Ports default:** widgets `5173`, scripts `5174`, tools stub `5175`
- **Comunicação widget ↔ script:** HTTP/JSON em dev; em prod, via tool MCP que o host agente resolve

## Riscos

| Risco | Mitigação |
|---|---|
| Spec Anthropic Agent Skills evoluir e quebrar layout | Codex referencia versão validada; `.skill-manifest.json` tem `schema_version` próprio |
| Convenção `tools/` + `widgets/` confundida com spec oficial | Codex destaca "convenção Ahrena"; cabeçalho-comentário no SKILL.md gerado |
| Snapshot stale após mudança de ref no framework | `lex-skill-export-determinism` exige refresh; `source_commit` no manifest evidencia divergência |
| Build não-determinístico (timestamps, ordering, bundler diff) | Kata força ordering lexicográfico; Vite com `mode: production` consistente; sem timestamps no manifest |
| Vite/Node/Python adicionarem peso ao repo | Tratar como dev dependencies dos projetos de skill, não do framework Ahrena |
| Confusão entre Pilares internos do framework e regras do projeto de skill | `lex-skill-project-structure` deixa explícito: skills/{slug}/ herda regras de qualidade (lex-frontend-*, lex-python-*) mas é projeto externo |
| Tamanho do `.dist/` no repo (com bundles compilados) | Codex documenta budget por skill; `.dist/` granular por slug; Git LFS se necessário |
| Localhost orchestration frágil em Windows/macOS/Linux | `kata-skill-dev-server` usa portas configuráveis e abstrai shell via `terminal` em `.directives` |
| Widget chamar script via HTTP em prod (sem dev server) | Manifest do widget declara `binding` que o host resolve; documentar no codex-skill-tools-and-widgets |
