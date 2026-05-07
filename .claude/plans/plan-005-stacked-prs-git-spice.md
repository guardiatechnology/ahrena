---
plan_id: "005"
title: "stacked-prs-git-spice"
status: in-progress
agent: claude
issue: "guardiatechnology/ahrena#56"
created_at: "2026-05-06T00:00:00Z"
updated_at: "2026-05-07T17:40:00Z"
---

# Plano: Suporte a Stacked PRs via git-spice (gs)

## Objetivo

Estender os artefatos de stacked PRs do plan-004 (vanilla) com o caminho `git-spice` (`gs`). Entregar um Codex de tooling dedicado, ampliar os três Katas existentes com seções "Variant: git-spice" e tornar o Cry sensível à diretiva de tooling do projeto. Adicionar uma chave em `.directives.sample` para o projeto declarar qual ferramenta usar.

## Contexto

`git-spice` é uma ferramenta Go open-source (GPL-3.0) que automatiza branch-stacks em git nativo. Resolve a dor central do vanilla: o auto-restack das camadas superiores acontece automaticamente quando você faz `gs commit create`/`amend` na camada inferior. Outras vantagens: trunk declarado em `gs repo init`, `gs repo sync` deleta branches mergeadas e rebaseia, `gs auth login` reusa o token do `gh` se disponível.

Compatibilidade verificada com a doc oficial (https://abhinav.github.io/git-spice/, fetch em 2026-05-06):

| Lexis | Compatível? | Como |
|---|---|---|
| `lex-protected-trunk` | ✅ | `gs repo init --trunk main` declara o trunk; gs nunca commita direto |
| `lex-git-branches` | ✅ | `gs branch create --target feat/{N}-stack-{i}-{slug}` aceita o padrão |
| `lex-signed-commits` | ✅ | `gs commit create/amend` respeita config global de GPG signing |
| `lex-conventional-commits` | ✅ | gs não enforce; usuário escreve mensagem via `-m` |
| `lex-pr-quality` | ⚠️ parcial | `gs branch submit --title --body --draft` cria PR; labels/assignee/reviewers continuam via `gh pr edit` |
| `lex-git-worktrees` | ⚠️ | mesma exceção do vanilla: stack = um worktree (cláusula já adicionada no plan-004) |

Decisões fechadas com o usuário:

1. **Estratégia de tool:** suportar vanilla (plan-004) e git-spice (este plan-005), com seleção via `.directives`.
2. **Modelo de katas:** manter os 3 katas do plan-004 e adicionar uma seção "Variant: git-spice" em cada um, em vez de duplicar arquivos. Single source of truth por procedimento.
3. **Codex de tool:** `codex-git-spice` em `_foundation/tooling/` (mesmo lar de `codex-make`, `codex-mcp-*`, `codex-terminal-type`).
4. **Separação de decisões:** existem **duas decisões distintas** no fluxo de stacked PRs — **(a) decisão estratégica** (stack vs PR único) e **(b) decisão de ferramenta** (vanilla vs gs). A decisão (a) é coberta pelo plan-004 (Decision Checklist no codex + Pre-flight no kata-create). Este plan-005 cobre apenas (b): se o usuário confirmou stack, qual ferramenta usar é definido por `.directives.stacked_prs.tool` (default `vanilla`; `gs` quando o projeto declara). Não há análise por sinais para a decisão de tool — é config lookup direto.

## Escopo

### Artefatos a criar (3 idiomas: pt-BR canônico, es, en)

| Pilar | Arquivo | Conteúdo principal |
|---|---|---|
| Codex | `_foundation/tooling/codex/codex-git-spice.md` | Instalação (Homebrew, go install, releases binárias), pré-requisitos (Git 2.38+), setup (`gs repo init --trunk`, `gs auth login`), catálogo de comandos por categoria (repo, branch, stack, upstack, downstack, commit, log, navigation), mapeamento "operação → comando vanilla → comando gs equivalente", flags de force-push (`--force` vs default lease), interação com hooks GPG, troubleshooting comum |

### Atualizações em artefatos do plan-004 (3 idiomas)

| Arquivo | Mudança |
|---|---|
| `_foundation/contributing/katas/kata-stacked-pr-create.md` | Adicionar seção "## Variant: git-spice" após o procedimento vanilla. Conteúdo: `gs repo init --trunk main` (uma vez por repo), `gs branch create --target {branch}` por camada, `git add` + `gs commit create -m`, `gs stack submit --draft` (cria todos os PRs), `gh pr edit` por camada para mirror de labels/assignee/reviewers/size |
| `_foundation/contributing/katas/kata-stacked-pr-rebase.md` | Adicionar seção "## Variant: git-spice". Conteúdo: substitui o cascade manual por `gs commit amend`/`gs commit create` (auto-restack); `gs repo sync --restack` quando `main` avançou; `gs rebase continue/abort` em conflitos |
| `_foundation/contributing/katas/kata-stacked-pr-merge.md` | Adicionar seção "## Variant: git-spice". Conteúdo: `gh pr merge` da camada inferior (gs não cobre merge), `gs repo sync` (deleta branch mergeada e rebaseia o resto automaticamente em vez de edit manual de base) |
| `_foundation/contributing/cries/cry-new-stacked-pr.md` | Detectar `stacked_prs.tool` em `.directives` (default `vanilla`; valor `gs` quando o projeto adotar git-spice). Despachar para a seção correta do kata-stacked-pr-create |

### Atualizações de configuração

- `framework/.directives.sample`: o bloco `stacked_prs.tool` é introduzido pelo plan-004 com `vanilla` documentado. Este plan apenas atualiza o **comentário de valores aceitos** para `vanilla | gs` (o plan-004 já deixa o esqueleto pronto). Mudança mínima, uma linha.
- `framework/platforms.yaml`: registrar `_foundation/tooling/codex/codex-git-spice` em `cursor.rules` e `claude-code.rules`, com `paths: [".git/spice/**"]` para lazy-load (gs guarda metadata em `.git/spice/`).

## Fora de escopo

- **Suporte a outras ferramentas** (Graphite, Aviator, gh-stack quando GA, ghstack, spr) — cada uma seria objeto de seu próprio plan se demanda surgir.
- **Migração automática vanilla → gs** em projetos com stacks ativas. O codex documenta o procedimento manual via `gs branch track`; automação não justifica esforço.
- **Reorder/insert mid-stack** via `gs stack edit` — o codex menciona o comando, mas o kata-rebase não detalha esse caso (uso esporádico; usuário lê o codex direto).

## Steps

- [ ] 1. Confirmar plan-004 mergeado e seus artefatos presentes em `framework/{pt-BR,es,en}/_foundation/contributing/`
- [ ] 2. Abrir issue guarda-chuva no repo `guardiatechnology/ahrena` referenciando a issue do plan-004 como dependência
- [ ] 3. Criar branch `feat/{N}-add-git-spice-support` e worktree `.worktrees/{N}-add-git-spice-support/`
- [ ] 4. Atualizar status deste plan para `in-progress`
- [ ] 5. Redigir `codex-git-spice` em pt-BR seguindo `templates/codex-sample.md`
- [ ] 6. Traduzir `codex-git-spice` para `es` e `en`
- [ ] 7. Estender `kata-stacked-pr-create` em pt-BR com seção "Variant: git-spice"
- [ ] 8. Propagar extensão para `es` e `en`
- [ ] 9. Estender `kata-stacked-pr-rebase` em pt-BR
- [ ] 10. Propagar para `es` e `en`
- [ ] 11. Estender `kata-stacked-pr-merge` em pt-BR
- [ ] 12. Propagar para `es` e `en`
- [ ] 13. Atualizar `cry-new-stacked-pr` em pt-BR para despachar via `stacked_prs.tool`
- [ ] 14. Propagar para `es` e `en`
- [ ] 15. Atualizar comentário do bloco `stacked_prs.tool` em `framework/.directives.sample` para listar `vanilla | gs` como valores aceitos
- [ ] 16. Adicionar entry de `codex-git-spice` em `framework/platforms.yaml`
- [ ] 17. Rodar `python3 scripts/install.py --self --platform claude-code --local` e equivalente para Cursor
- [ ] 18. Validar: `codex-git-spice` listado em CLAUDE.md; cada um dos 3 katas tem seção "Variant: git-spice" nas 3 línguas; cry honra a diretiva
- [ ] 19. Smoke test manual: rodar `gs repo init --trunk main` + `gs branch create --target test/spice-1` + `gs stack submit --dry-run` num repo sandbox para validar que os comandos do codex/katas estão corretos
- [ ] 20. Commits atômicos por artefato/Pilar, em inglês + body bilíngue, assinados
- [ ] 21. Push e abrir PR via `kata-contributing-pr`, com `Closes #{N}` e referência cruzada à PR do plan-004
- [ ] 22. Após merge: mover plan para `archived/` e remover worktree

## Dependências

- **Plan-004 mergeado** — este plan estende os artefatos criados lá. Não pode rodar em paralelo (extensão de arquivos, não criação).
- `git-spice` instalado no ambiente de quem fizer o smoke test (passo 19): `brew install git-spice`.
- `templates/codex-sample.md` presente.
- `scripts/install.py` funcional.

## Riscos

- **gs versão muda flags antes de v1.0.** Mitigação: codex-git-spice fixa versão mínima testada e referencia a doc oficial.
- **Auto-restack do gs entra em loop com hooks pre-commit/post-commit pesados.** Mitigação: codex documenta limitação e sugere `gs commit create --no-verify` como escape (com cautela).
- **Usuário roda `gs commit amend` em commit já pushado e gera force-push em todas as camadas acima.** Mitigação: kata-rebase deixa explícito que amend em camada já submetida exige `gs stack submit --force` consciente; nunca `--force` cego.
- **Tradução técnica de termos gs (upstack/downstack/restack) para pt-BR/es.** Mitigação: termos não traduzem (`lex-language` rule 3 — keep technical terms in English).

## Verificação

1. **Estrutura:** `find framework -name "codex-git-spice.md"` retorna 3 arquivos (pt-BR, es, en).
2. **CLAUDE.md auto-gerado:** lista `_foundation/tooling/codex-git-spice.md` na seção Reference Docs.
3. **Katas estendidos:** cada um dos 3 katas em `_foundation/contributing/katas/` contém literalmente uma seção `## Variant: git-spice` (ou tradução equivalente em es/en) nas 3 línguas.
4. **Diretiva:** `framework/.directives.sample` tem bloco `stacked_prs.tool` documentado.
5. **Cry:** `cry-new-stacked-pr` referencia `stacked_prs.tool` no prompt do agente.
6. **Smoke test gs:** `gs repo init` + `gs stack submit --dry-run` funcionam contra um repo sandbox sem erro.
7. **PR:** body referencia `Closes #{N}` e a PR do plan-004; HARD-GATE de `lex-pr-quality` atendido.
