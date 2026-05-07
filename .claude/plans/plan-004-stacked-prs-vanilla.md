---
plan_id: "004"
title: "stacked-prs-vanilla"
status: in-progress
agent: claude
issue: "guardiatechnology/ahrena#50"
created_at: "2026-05-06T00:00:00Z"
updated_at: "2026-05-07T03:10:00Z"
---

# Plano: Suporte a Stacked PRs no fluxo vanilla (git + gh)

## Objetivo

Codificar a prática de Stacked PRs no framework usando exclusivamente `git` e `gh` (sem extensão externa). Entregar Codex tool-agnostic, três Katas (criar, rebase em cascata, merge bottom-up) e um Cry de atalho. Ajustar `lex-git-worktrees` para acomodar uma stack inteira em um único worktree compartilhado.

## Contexto

Stacked PRs são uma cadeia de PRs onde cada branch targeta a anterior, permitindo review camada-por-camada de mudanças grandes. O caminho vanilla funciona em qualquer repositório GitHub hoje, sem allowlist nem dependência de extensão em preview privado. A operação é mais trabalhosa (cascade rebase manual após mudança em camada inferior; atualização explícita do `base` do PR seguinte após merge), mas é universal e zero-risco.

Decisões fechadas com o usuário:

1. **Modelo issue↔stack:** 1 issue guarda-chuva → N camadas. Camadas intermediárias fazem `Refs #N`; última faz `Closes #N`.
2. **Worktree:** uma stack inteira ocupa um worktree (`.worktrees/{N}-{slug}-stack/`). Exceção declarada em `lex-git-worktrees`.
3. **Adoção:** opcional, recomendado para PRs grandes. Sem nova Lexis obrigando uso. Codex + Katas + Cry.
4. **Estratégia de tool:** este plano cobre o caminho vanilla. O caminho git-spice é objeto do plan-005, que estende este.
5. **Modelo de decisão (estratégia stack vs PR único):** agente propõe, usuário confirma. Checklist objetiva fica no codex; agente executa no Pre-flight do kata-create (Fase 0) e do cry. Athena (lex-issue-driven) **não** roda essa checagem nesta iteração — segue como follow-up.

## Modelo de decisão (estratégia)

A decisão de transformar uma issue em stacked PR vs PR único usa **checklist objetiva no codex + Pre-flight no kata**. O agente nunca decide sozinho; sempre propõe ao usuário.

**Sinais altos** (cada um conta 1 ponto):
- Diff estimado > 500 linhas modificadas
- Issue com ≥ 4 ACs independentes
- ≥ 2 Pilares técnicos atravessados (ex.: backend + frontend)
- Camadas óbvias presentes (schema → API → UI; data → service → handler)
- Independência de review entre camadas (reviewer A não precisa do contexto de Y para revisar X)
- Risco de rollback por camada (migração + feature visível na mesma issue)

**Anti-sinais** (presença de qualquer um veta a stack):
- Hotfix / resposta a incidente (velocidade > granularidade)
- Cross-fork PR (ferramentas de stack não suportam bem)
- Refactor monolítico que não decompõe em camadas independentes

**Heurística:** ≥ 3 sinais altos **e** 0 anti-sinais → agente propõe stack com decomposição concreta. Caso contrário, redireciona para `kata-contributing-pr`.

## Escopo

### Artefatos a criar (3 idiomas: pt-BR canônico, es, en)

| Pilar | Arquivo | Conteúdo principal |
|---|---|---|
| Codex | `_foundation/contributing/codex/codex-stacked-prs.md` | Conceito de stacked PRs, modelo de naming compatível com `lex-git-branches` (`{type}/{N}-stack-{layer}-{slug}`), modelo de issue (1 guarda-chuva → N camadas), referência cruzada por Lexis afetada (`lex-protected-trunk`, `lex-issue-first`, `lex-pr-quality`, `lex-git-worktrees`, `lex-signed-commits`, `lex-conventional-commits`). **Decision Checklist** com sinais altos e anti-sinais (ver seção "Modelo de decisão" deste plan) — fonte canônica que o kata e o cry consultam |
| Kata | `_foundation/contributing/katas/kata-stacked-pr-create.md` | **Fase 0 — Pre-flight Decision:** agente roda a Decision Checklist do codex contra issue + escopo declarado, computa sinais altos vs anti-sinais; se ≥ 3 sinais altos e 0 anti-sinais, **propõe decomposição concreta em camadas** (ex.: "Camada 1=schema, 2=API, 3=UI") e pede confirmação do usuário antes de prosseguir; caso contrário, redireciona para `kata-contributing-pr` (PR único). **Fase 1+:** validar issue guarda-chuva e ACs numerados → criar branch base + worktree único `.worktrees/{N}-{slug}-stack/` → loop por camada (`git checkout -b feat/{N}-stack-{i}-{slug}`, work, commit assinado, push, `gh pr create --base {anterior} --title --body`) → mirror de labels/size/assignee/reviewers em cada PR via `gh pr edit` → última camada com `Closes #N`, intermediárias com `Refs #N` |
| Kata | `_foundation/contributing/katas/kata-stacked-pr-rebase.md` | Procedimento de cascade rebase manual após mudança em camada inferior: amend/commit no layer N → `git push --force-with-lease` → loop ascendente (`git checkout layer N+1 && git rebase layer N && git push --force-with-lease`). Resolução de conflitos com `git rebase --continue`/`--abort`. Quando usar `git rebase --onto` (squash merge upstream criou divergência) |
| Kata | `_foundation/contributing/katas/kata-stacked-pr-merge.md` | Política bottom-up: merge layer 1 → atualizar `base` do layer 2 (`gh pr edit {pr-2} --base main`) → rebase layer 2 onto main e force-push → cascade nos layers superiores → cleanup do worktree e branches mergeadas |
| Cry | `_foundation/contributing/cries/cry-new-stacked-pr.md` | Atalho que invoca `kata-stacked-pr-create`. Mesmo em invocação explícita pelo usuário, o kata roda a Decision Checklist; se sinais negativos (anti-sinal presente ou sinais altos < 3), agente avisa "não parece valer a pena, prosseguir como stack mesmo assim?" antes de continuar — usuário pode forçar |

### Atualizações

- `_foundation/contributing/lexis/lex-git-worktrees.md` (3 línguas): adicionar à seção "Allowed exceptions" a cláusula **uma stack ocupa um único worktree compartilhado** com path `.worktrees/{N}-{slug}-stack/`. Manter o restante intacto.
- `framework/.directives.sample`: adicionar bloco comentado para a nova diretiva `stacked_prs`. Estrutura:
  ```yaml
  # ─── Stacked PRs ────────────────────────────────────────────────
  # Tool used to manage stacked pull requests when a feature is
  # decomposed into N layers. Default is `vanilla` (git + gh CLI).
  # Set to `gs` (git-spice) when the project adopts the extension.
  # See codex-stacked-prs and codex-git-spice for details.

  # stacked_prs:
  #   tool: vanilla   # vanilla | gs
  ```
  Plan-004 declara a estrutura com `vanilla` documentado; plan-005 documentará `gs` como valor adicional sem reabrir a estrutura.
- `_foundation/process/lexis/lex-directives.md` (3 línguas): adicionar linha na tabela "Application by section" para a nova chave `stacked_prs.tool`.
- `framework/platforms.yaml`: registrar entries para `codex-stacked-prs` em `cursor.rules` e `claude-code.rules` com `description` mínima e `paths:` opcional (`.worktrees/**-stack/**`).
- `framework/{lang}/CLAUDE.md` é auto-gerado pelo `install.py`; não editar manualmente.

## Fora de escopo

- **Suporte a `git-spice`** — coberto pelo plan-005, que estende os artefatos deste plano com seções "Variant: git-spice".
- **Integração com Athena (`lex-issue-driven`)** — coberto pelo plan-006, que adiciona Decision Checklist na Phase 3, decomposição em camadas no checkpoint schema e Gate 2 por camada.
- **Hook/CI guardrails** que detectam quando uma PR é grande demais e sugerem stack. Pode virar um plan próprio quando demanda surgir.
- **Variante "N issues → N camadas"** — descartada na decisão.

## Steps

- [x] 1. Abrir issue guarda-chuva no repo `guardiatechnology/ahrena` com template `feature-request`, labels e Issue Type apropriados (`lex-issue-quality`) — issue #50
- [x] 2. Criar branch `feat/50-add-stacked-prs-vanilla` e worktree `.worktrees/50-add-stacked-prs-vanilla/` (`lex-git-branches`, `lex-git-worktrees`)
- [x] 3. Atualizar status deste plan para `in-progress`
- [ ] 4. Redigir `codex-stacked-prs` em pt-BR seguindo `templates/codex-sample.md`
- [ ] 5. Traduzir `codex-stacked-prs` para `es` e `en` (`kata-translate`)
- [ ] 6. Redigir `kata-stacked-pr-create` em pt-BR
- [ ] 7. Traduzir `kata-stacked-pr-create` para `es` e `en`
- [ ] 8. Redigir `kata-stacked-pr-rebase` em pt-BR
- [ ] 9. Traduzir `kata-stacked-pr-rebase` para `es` e `en`
- [ ] 10. Redigir `kata-stacked-pr-merge` em pt-BR
- [ ] 11. Traduzir `kata-stacked-pr-merge` para `es` e `en`
- [ ] 12. Redigir `cry-new-stacked-pr` em pt-BR
- [ ] 13. Traduzir `cry-new-stacked-pr` para `es` e `en`
- [ ] 14. Atualizar `lex-git-worktrees` (pt-BR) com exceção "uma stack = um worktree"
- [ ] 15. Propagar atualização de `lex-git-worktrees` para `es` e `en`
- [ ] 16. Adicionar bloco `stacked_prs.tool` (comentado) em `framework/.directives.sample`
- [ ] 17. Atualizar tabela "Application by section" em `lex-directives.md` (3 línguas) com a chave `stacked_prs.tool`
- [ ] 18. Adicionar entries em `framework/platforms.yaml` (`cursor.rules` e `claude-code.rules`) para `codex-stacked-prs`
- [ ] 19. Rodar `python3 scripts/install.py --self --platform claude-code --local` e equivalente para Cursor
- [ ] 20. Validar: 15 arquivos novos (5 artefatos × 3 línguas) presentes; codex listado em CLAUDE.md auto-gerado; kata aparece como skill; cry aparece como command; bloco `stacked_prs.tool` presente em `.directives.sample`; tabela em `lex-directives.md` cita a nova chave
- [ ] 21. Commits atômicos (`lex-small-commits`): um por artefato/Pilar, em inglês no subject + body bilíngue (`lex-commit-language`), assinados (`lex-signed-commits`)
- [ ] 22. Push e abrir PR via `kata-contributing-pr`, com `Closes #{N}`, mirror de labels da issue, size label, reviewers via `CODEOWNERS`
- [ ] 23. Após merge: mover plan para `archived/` e remover worktree (`git worktree remove`)

## Dependências

- `templates/{codex,kata,cry}-sample.md` presentes (já são).
- `scripts/install.py` funcional (já está, conforme plan-003).
- Nenhum bloqueio em plans 001-003.
- Plans 005 (git-spice) e 006 (Athena) **dependem deste** plan-004 mergear primeiro. Plan-005 e plan-006 podem rodar em paralelo entre si.

## Riscos

- **Cascade rebase manual é cansativo.** Para stacks de 4+ camadas, o overhead operacional cresce. Mitigação: codex declara explicitamente o limite recomendado (3-4 camadas no vanilla; mais camadas → considerar git-spice via plan-005).
- **Tradução pt-BR → es/en perder precisão técnica em comandos shell.** Mitigação: code blocks e nomes de comandos não traduzem (`lex-language` rule 3); revisar manualmente os trechos narrativos.
- **Athena ainda não conhece stacks após este plan.** Mitigação: plan-006 fecha esse gap; este plan deixa os artefatos prontos para serem invocados quando Athena evoluir.
- **Risco de force-push errado em camada inferior.** Mitigação: kata-rebase usa exclusivamente `--force-with-lease`; nunca `--force`.

## Verificação

1. **Estrutura:** `find framework -name "codex-stacked-prs.md" -o -name "kata-stacked-pr-*.md" -o -name "cry-new-stacked-pr.md"` retorna 5 × 3 = 15 arquivos.
2. **CLAUDE.md auto-gerado:** lista `_foundation/contributing/codex-stacked-prs.md` na seção Reference Docs.
3. **Skills/commands:** `kata-stacked-pr-create`, `kata-stacked-pr-rebase`, `kata-stacked-pr-merge` aparecem em `available skills`; `cry-new-stacked-pr` aparece em commands.
4. **Lex-git-worktrees:** seção "Allowed exceptions" cita explicitamente stacks nas 3 línguas.
5. **Platforms.yaml:** entry para `_foundation/contributing/codex/codex-stacked-prs` presente.
6. **PR:** body referencia `Closes #{N}`, todos os 6 critérios de `lex-pr-quality` HARD-GATE atendidos.
