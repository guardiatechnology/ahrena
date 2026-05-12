---
plan_id: "035"
title: "public-docs-sync-and-catchup"
status: pending
agent: claude
issue: "TBD"
created_at: "2026-05-09T12:10:00Z"
updated_at: "2026-05-09T12:15:00Z"
---

# Plano: Sincronização de Docs Públicos — Lex de Fundação + Atualização de Authoring + Catch-up do Backlog

## Objetivo

Fechar a lacuna entre `framework/{lang}/` (fonte da verdade) e `docs/ahrena/` (docs públicos em guardiafinance.github.io/ahrena). O estado atual da `main` tem 40 artefatos faltando nos 3 idiomas, um clade inteiro (`product`) e uma subclade (`engineering/skills`) ausentes dos docs públicos. Também não existe Lexis de fundação que garanta que isso não volte a acontecer. Este plano entrega (1) um Lexis que torna inviolável a sincronização dos docs públicos, (2) atualização de todos os `kata-create-*` e do `kata-push-to-framework` para impor o novo passo, e (3) um catch-up único do backlog existente.

## Auditoria (congelada na criação do plano)

Fonte da verdade: `framework/en/` (70 lex, 72 codex, 63 kata, 15 warrior, 33 cry → 253 artefatos × 3 idiomas = 759).
Comparação contra `docs/ahrena/{pilar}.{lang}.md`:

### Faltando em `docs/ahrena/lexis.{en,pt-BR,es}.md` (13 em cada)

- lex-agent-planning · lex-discovery-flow · lex-dry · lex-feature-design-docs · lex-git-worktrees · lex-hard-gate-pattern · lex-logging-decorator · lex-pr-quality · lex-protected-trunk · lex-python-error-object · lex-python-result-type · lex-skill-package-structure · lex-skill-project-structure

### Faltando em `docs/ahrena/codex.{en,pt-BR,es}.md` (10 em cada)

- codex-agent-planning · codex-discovery-artifacts · codex-feature-design-docs · codex-git-spice · codex-git-worktrees · codex-python-logging · codex-skill-anthropic-agent-skills · codex-skill-project-architecture · codex-skill-tools-and-widgets · codex-stacked-prs

### Faltando em `docs/ahrena/katas.{en,pt-BR,es}.md` (11 em cada, +1 stale)

- kata-artifact-self-review · kata-discovery-synthesis · kata-feature-design-docs · kata-git-worktree · kata-ideation-from-insight · kata-init-skill · kata-plan-task · kata-python-logging-setup · kata-stacked-pr-create · kata-stacked-pr-merge · kata-stacked-pr-rebase
- Stale: `kata-sample` (template, DEVE ser excluído)

### Faltando em `docs/ahrena/warriors.{en,pt-BR,es}.md` (2 em cada, +1 stale)

- warrior-phanes · warrior-pitia
- Stale: `warrior-sample` (template)

### Faltando em `docs/ahrena/cries.{en,pt-BR,es}.md` (4 em cada, +1 stale)

- cry-discovery · cry-ideation · cry-new-skill · cry-new-stacked-pr
- Stale: `cry-sample` (template)

### Faltando em `docs/ahrena/clades.{en,pt-BR,es}.md`

- Clade **`product`** inteiro (subclade `discovery` com 1 lex, 1 codex, 2 kata, 2 warrior, 2 cry)
- Subclade **`engineering/skills`** (2 lex, 3 codex, 1 kata, 1 cry)
- Todas as contagens de linhas de subclades estão defasadas em `_foundation`, `design`, `documentation`, `engineering`
- Tabela de resumo no rodapé: contagem de clades, contagem de subclades, totais

### Defasado em `docs/ahrena/index.{en,pt-BR,es}.md`

A tabela de escala declara 39 lex / 55 codex / 53 kata / 14 warrior / 31 cry / 4 clades / 16 subclades / ~649 total. Números reais: 70 / 72 / 63 / 15 / 33 / 5 / 18 / 759.

### Defasado em `README.{md,en.md,es.md}`

A tabela "Clades and Subclades" sob `engineering` não lista a subclade `skills`.

## Entregáveis

### Parte A — Lexis de fundação (1 lex novo × 3 idiomas)

**`framework/{lang}/_foundation/authoring/lexis/lex-public-docs-sync.md`**

Lei (literal): Todo artefato enviado para `framework/{lang}/` (qualquer Pilar) DEVE ter entrada correspondente em `docs/ahrena/{pilar}.{lang}.md` para **cada** idioma em `language.i18n`. Toda nova clade ou subclade DEVE aparecer em `docs/ahrena/clades.{lang}.md` com contagens precisas por Pilar; a tabela de resumo e a tabela de escala em `docs/ahrena/index.{lang}.md` DEVEM refletir as contagens reais.

Bloco HARD-GATE (per `lex-hard-gate-pattern`):
- Sujeito: qualquer agente ou humano enviando para `framework/{lang}/`
- Ação proibida: mergeear PR que adiciona/remove/realoca artefato, subclade ou clade do framework sem a atualização correspondente em `docs/ahrena/`
- Pré-condições: (a) entrada existe em `docs/ahrena/{pilar}.{lang}.md` para cada idioma em `language.i18n`; (b) linha em `clades.{lang}.md` reflete a nova contagem; (c) tabela de escala em `index.{lang}.md` reflete os novos totais; (d) resumo no rodapé de `clades.{lang}.md` atualizado; (e) ao adicionar clade ou subclade nova, tabela de clades do README também atualizada
- Contra-pretextos: "é só um artefato"; "faço a doc num PR de follow-up"; "a doc é auto-gerada" (não é — são índices curados à mão); "só a versão en importa"
- Exceção: entradas stale `*-sample` são templates e estão explicitamente excluídas das listagens públicas

Validação: extensão do `scripts/validate.py` que faz diff entre `find framework/{lang} -name '{prefix}-*.md' | exclude *-sample` e `grep -oE '{prefix}-[a-z-]+' docs/ahrena/{pilar}.{lang}.md`. CI falha em qualquer divergência.

### Parte B — Atualizar katas existentes (5 katas × 3 idiomas = 15 arquivos)

Adicionar um "Passo N — Atualizar docs públicos" em cada `kata-create-*` cobrindo:
- `kata-create-lexis` → adicionar entrada em `docs/ahrena/lexis.{lang}.md` (3 idiomas)
- `kata-create-codex` → adicionar entrada em `docs/ahrena/codex.{lang}.md`
- `kata-create-kata` → adicionar entrada em `docs/ahrena/katas.{lang}.md`
- `kata-create-warrior` → adicionar entrada em `docs/ahrena/warriors.{lang}.md`
- `kata-create-cry` → adicionar entrada em `docs/ahrena/cries.{lang}.md`

Cada passo atualiza:
- A listagem do Pilar relevante para **todos** os idiomas em `language.i18n`
- `docs/ahrena/clades.{lang}.md` se nova subclade ou clade for envolvida
- Contadores da tabela de escala em `docs/ahrena/index.{lang}.md`

Estender também o **`kata-push-to-framework`** para verificar a sincronização dos docs como parte do preflight (bloqueia push se o artefato novo ainda não está em `docs/ahrena/`).

### Parte C — Helper opcional (decidido no PR2 abaixo)

Considerar um `scripts/sync_docs_ahrena.py` que, dada a árvore atual de `framework/{lang}/`, regenera as partes determinísticas de `docs/ahrena/clades.{lang}.md` (tabelas de contagem por subclade + resumo) e `docs/ahrena/index.{lang}.md` (tabela de escala). As listas de entradas escritas à mão em `lexis.{lang}.md` etc. permanecem manuais (cada entrada tem descrição curada de 1 linha); o script só impõe "a entrada existe" via lint, não auto-gera o texto.

### Parte D — Catch-up único

- Adicionar 13 lex × 3 idiomas = 39 entradas em lexis
- Adicionar 10 codex × 3 idiomas = 30 entradas em codex
- Adicionar 11 kata × 3 idiomas = 33 entradas em katas
- Adicionar 2 warrior × 3 idiomas = 6 entradas em warriors
- Adicionar 4 cry × 3 idiomas = 12 entradas em cries
- Remover 3 entradas stale × 3 idiomas = 9 deleções (`kata-sample`, `warrior-sample`, `cry-sample`)
- Atualizar `clades.{lang}.md` × 3: inserir clade `product`, inserir linha de subclade `engineering/skills`, atualizar contagens de todas as linhas, atualizar resumo
- Atualizar `index.{lang}.md` × 3: tabela de escala com contagens reais
- Atualizar `README.{md,en.md,es.md}` × 3: tabela de clades para listar subclade `skills`

Total de toques em arquivos: ~135.

## Passos

- [ ] **Passo 1 — Abrir issue.** Tipo `simple-task`, label `documentation 📃`, Why/What/How preenchidos, assignee `@me`. Per `lex-issue-quality` e `lex-issue-first`. Capturar número da issue para a branch e para o front-matter do plano.
- [ ] **Passo 2 — Criar branch e worktree.** `chore/{N}-public-docs-sync-and-catchup` per `lex-git-branches` e `lex-git-worktrees`.
- [ ] **Passo 3 — Planejar a stack.** O trabalho se divide cleanly em 3 PRs revisáveis; usar PRs empilhados per `kata-stacked-pr-create`:
  - PR1: Lexis de fundação + entrada em cursor.rules + `_foundation/authoring/lexis/lex-public-docs-sync.md` × 3 idiomas (sem catch-up de docs ainda — prova que o gate existe antes do catch-up ser exigido para passar)
  - PR2: atualizações dos katas (`kata-create-{lex,codex,kata,warrior,cry}` e `kata-push-to-framework`) × 3 idiomas + `scripts/sync_docs_ahrena.py` (linter opcional)
  - PR3: catch-up único de `docs/ahrena/*` × 3 idiomas + correção da tabela de clades dos READMEs
- [ ] **Passo 4 — PR1 (Lexis de fundação).** Autorar o novo Lexis em pt-BR (default) per `framework/templates/lex-sample.md`; traduzir para en + es per `cry-translate`; registrar entrada em `framework/platforms.yaml` `cursor.rules` per `lex-platforms-rules`; rodar `python3 scripts/install.py --self --target . --platform claude-code` e `--platform cursor` para sincronizar `.claude/` e `.cursor/`; commit per `lex-conventional-commits` e `lex-small-commits`.
- [ ] **Passo 5 — Aceite do PR1.** O novo Lexis + comando de lint deve agora FALHAR no estado atual da `main` (provando que funciona) — capturar a saída de falha no corpo do PR como evidência, depois mergear PR1 (a falha do gate agora bloqueia PR2 a menos que PR2 também trate o catch-up — ver passo 7).
- [ ] **Passo 6 — PR2 (atualizações de katas).** Adicionar o passo "atualizar docs/ahrena/" a cada um dos 5 `kata-create-*` × 3 idiomas e ao `kata-push-to-framework` × 3 idiomas. Decidir o escopo do `scripts/sync_docs_ahrena.py` (lint-only é preferível; não auto-gerar texto).
- [ ] **Passo 7 — PR3 (catch-up).** Aplicar o delta de 135 arquivos da tabela de auditoria. Para cada nova entrada, espelhar o estilo de descrição de 1 linha já usado em `docs/ahrena/{pilar}.{lang}.md`. Para `clades.{lang}.md`, regenerar contagens deterministicamente. Para `index.{lang}.md`, atualizar tabela de escala. Para os READMEs, corrigir a tabela de clades.
- [ ] **Passo 8 — Verificar gate.** Rodar o validador (ou `diff` manual por Pilar/idioma) — deve reportar 0 faltando, 0 stale em todo idioma.
- [ ] **Passo 9 — Sync e merge.** Merge bottom-up per `kata-stacked-pr-merge`. Cada merge re-baseia a próxima camada.

## Dependências

- `lex-hard-gate-pattern` — usado pela Parte A.
- `lex-platforms-rules` — o novo Lexis da Parte A precisa ser registrado em `framework/platforms.yaml`.
- `kata-create-lexis`, `kata-create-codex`, `kata-create-kata`, `kata-create-warrior`, `kata-create-cry`, `kata-push-to-framework` — modificados pela Parte B.
- `kata-stacked-pr-create`, `kata-stacked-pr-merge`, `kata-stacked-pr-rebase` — usados para entregar como stack.
- `cry-translate` — usado para traduzir o novo Lexis e as edições dos katas.
- `scripts/install.py --self` — usado para sincronizar `.cursor/` e `.claude/` após edições no framework.

## Riscos

- **Drift de tradução.** Com 135 toques em arquivos × 3 idiomas, descrições podem divergir. Mitigação: manter descrições em uma única linha; espelhar o tom existente em cada `docs/ahrena/{pilar}.{lang}.md`; uma passada completa com `cry-translate` antes de abrir o PR3.
- **Entradas stale `*-sample`.** Atualmente listadas em algumas páginas de Pilar — garantir que o novo linter exclua explicitamente os templates `*-sample` (por viverem sob `framework/templates/`, nunca dentro de uma clade).
- **Contagens voltam a ficar stale assim que o PR3 mergear.** Mitigação: o lint do PR2 precisa rodar em CI em todo PR que toca `framework/`. Sem isso, os katas manuais derivam.
- **PR3 grande é difícil de revisar.** Mitigação: estruturar o histórico de commits do PR3 por Pilar (um commit por Pilar × 3 idiomas), e por idioma para `clades`/`index`/README; revisor pode varrer um pedaço de cada vez. Aplicar `lex-small-commits`.
- **Reivindicação de "docs auto-geradas" se infiltra.** Os arquivos atuais de `docs/ahrena/*.md` são catálogos curados à mão (cada entrada tem descrição de 1 linha). Auto-geração via script perderia isso. Manter autoria manual; enforcement só via lint.