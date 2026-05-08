---
plan_id: "006"
title: "stacked-prs-athena-integration"
status: in-progress
agent: claude
issue: "guardiatechnology/ahrena#65"
created_at: "2026-05-06T00:00:00Z"
updated_at: "2026-05-08T00:00:00Z"
---

# Plano: Integração de Stacked PRs ao fluxo Athena (lex-issue-driven)

## Objetivo

Tornar Athena (warrior do fluxo Issue-Driven) ciente de stacked PRs. Estender `lex-issue-driven` para que a Phase 3 (Architecture) consulte a Decision Checklist do `codex-stacked-prs` (criado pelo plan-004), proponha decomposição em camadas, registre a estrutura no checkpoint e oriente as fases seguintes (Implementation, Quality Gate, PR) a operar por camada quando aplicável. Mudança aditiva — fluxos sem stack continuam idênticos.

## Contexto

`lex-issue-driven` rege o ciclo de 7 fases conduzido por `warrior-athena`:

1. Issue Analysis → 2. Requirements → 3. Architecture → **Gate 1** → 4. Implementation → 5. Security Review → 6. **Gate 2** (Quality) → 7. PR

Hoje, a Phase 7 invoca `kata-contributing-pr` produzindo um PR único. Não há mecanismo para decompor o trabalho em camadas reviewáveis. O plan-004 entrega os artefatos vanilla (codex + katas + cry); este plan-006 plugga esses artefatos no fluxo Athena.

Decisões fechadas com o usuário:

1. **Athena precisa contemplar stacks** — confirmado nesta rodada.
2. **Decision Checklist é canônica em `codex-stacked-prs`** — Athena consulta o codex; não duplica critérios.
3. **Decomposição entra em Phase 3 (Architecture)** — natural, junto com mapeamento de componentes afetados; humano aprova decomposição no Gate 1.
4. **Mudança aditiva** — checkpoint schema preserva schema_version 1 com bloco `stack:` opcional; ausência = comportamento atual (PR único).

## Escopo

### Atualizações em `lex-issue-driven.md` (3 línguas)

| Fase | Mudança |
|---|---|
| Phase 3 (Architecture) | Athena consulta `codex-stacked-prs` Decision Checklist contra escopo declarado. Se sinais altos ≥ 3 e 0 anti-sinais, **propõe decomposição** em `docs/issues/issue-{n}/03-architecture.md` (seção "Stacked PR Decomposition") com: tabela de camadas (layer N, slug, ACs cobertos, componentes tocados), justificativa, ferramenta selecionada (lookup em `.directives.stacked_prs.tool`). Se reprovou, registra "Single PR — checklist not met" e segue normal |
| Gate 1 | Humano aprova arquitetura + decomposição (ou solicita ajuste). Aprovação registra `stack.approved: true` no checkpoint |
| Phase 4 (Implementation) | Quando `stack.approved: true`, delegations são organizadas por camada; warrior implementa camada N apenas após camada N-1 estar pronta para review. `delegations[].layer: N` registra a qual camada cada delegação pertence |
| Phase 6 (Gate 2) | `kata-quality-gate` roda **por camada** antes de cada PR ser submetido. AC↔test traceability é checada apenas contra ACs cobertos pela camada (não o conjunto inteiro). Scope creep é checado contra os componentes declarados pela camada na Phase 3 |
| Phase 7 (PR) | Quando `stack.approved: true`, invoca `kata-stacked-pr-create` em vez de `kata-contributing-pr`. Kata lê `stacked_prs.tool` e segue a variant correspondente (vanilla ou gs) |

### Schema do checkpoint (aditivo, schema_version permanece 1)

Adicionar bloco opcional `stack:` ao front-matter de `.ahrena/workflow/issue-{n}/checkpoint.md`:

```yaml
stack:
  approved: false              # vira true após Gate 1
  tool: vanilla                # eco do .directives.stacked_prs.tool
  decomposition:
    - layer: 1
      slug: schema
      covers_acs: [AC-1, AC-2]
      components: ["db/migrations/*", "models/*"]
      status: pending          # pending | in-progress | submitted | merged
      pr: null                 # owner/repo#N quando submetido
    - layer: 2
      slug: api
      covers_acs: [AC-3, AC-4]
      components: ["api/routers/*", "use_cases/*"]
      status: pending
      pr: null
```

Ausência do bloco = fluxo PR único, comportamento atual preservado.

### Atualizações em `warrior-athena.md` (3 línguas)

- Adicionar à descrição: "consulta `codex-stacked-prs` durante Phase 3 e propõe decomposição quando aplicável"
- Adicionar referência cruzada para `codex-stacked-prs` e `kata-stacked-pr-create`

### Atualizações em `kata-quality-gate.md` (3 línguas)

- Acrescentar nota: quando o checkpoint contém bloco `stack`, Gate 2 é executado **por camada**. Cada layer.status só transita para `submitted` quando os 7 checks passam contra o subset de ACs e componentes daquela camada. Validação agregada final confirma que todas as camadas passaram.

### Atualizações em `lex-pr-quality.md` (3 línguas)

- HARD-GATE: clarificar que os 8 critérios (a)-(h) são avaliados **por PR da stack** (cada layer é um PR real). Nenhuma alteração aos critérios em si — apenas escopo de aplicação.

## Fora de escopo

- **Refactor estrutural do checkpoint** (schema_version 2) — mudança aditiva é suficiente; reservamos schema_version 2 para necessidade futura.
- **Auto-criação de issues filhas por camada** — modelo é "1 issue guarda-chuva → N camadas" por decisão prévia; não criar sub-issues.
- **Athena selecionar a tool entre vanilla e gs** — tool é decisão de projeto via `.directives`; Athena só lê.
- **Nova Lexis obrigando stacks** — adoção segue opcional.

## Steps

- [ ] 1. Confirmar plan-004 mergeado (artefatos `codex-stacked-prs`, 3 katas, cry presentes)
- [ ] 2. Abrir issue guarda-chuva no repo `guardiatechnology/ahrena` referenciando a issue do plan-004
- [ ] 3. Criar branch `feat/{N}-athena-stacked-prs` e worktree `.worktrees/{N}-athena-stacked-prs/`
- [ ] 4. Atualizar status deste plan para `in-progress`
- [ ] 5. Atualizar `lex-issue-driven.md` em pt-BR: Phase 3, Gate 1, Phase 4, Phase 6, Phase 7 e schema do checkpoint (bloco `stack` opcional)
- [ ] 6. Propagar `lex-issue-driven.md` para `es` e `en`
- [ ] 7. Atualizar `warrior-athena.md` em pt-BR (descrição + cross-references)
- [ ] 8. Propagar `warrior-athena.md` para `es` e `en`
- [ ] 9. Atualizar `kata-quality-gate.md` em pt-BR (avaliação por camada)
- [ ] 10. Propagar `kata-quality-gate.md` para `es` e `en`
- [ ] 11. Atualizar `lex-pr-quality.md` em pt-BR (HARD-GATE escopo por PR da stack)
- [ ] 12. Propagar `lex-pr-quality.md` para `es` e `en`
- [ ] 13. Rodar `python3 scripts/install.py --self --platform claude-code --local` e equivalente para Cursor
- [ ] 14. Validar via dry-run sintético: criar checkpoint fictício com bloco `stack` e validar que parsing/lint do schema aceita; rodar `kata-issue-analysis` mental contra issue de exemplo com sinais altos para confirmar que a checklist é referenciada
- [ ] 15. Validar que fluxos sem stack continuam funcionando (regressão zero — bloco `stack` é opcional)
- [ ] 16. Commits atômicos por arquivo modificado; subject em inglês + body bilíngue; assinados
- [ ] 17. Push e abrir PR via `kata-contributing-pr`, com `Closes #{N}` e referência à PR do plan-004
- [ ] 18. Após merge: arquivar plan e remover worktree

## Dependências

- **Plan-004 mergeado** — Athena precisa do codex e dos katas existentes para invocar.
- **Plan-005 não é dependência** — Athena despacha tool via `stacked_prs.tool`; se valor for `gs` mas plan-005 ainda não mergeou, kata-stacked-pr-create cai no caminho vanilla com warning.
- `templates/lex-sample.md`, `templates/warrior-sample.md`, `templates/kata-sample.md` presentes.
- `scripts/install.py` funcional.

## Riscos

- **Backward compatibility do checkpoint.** Mitigação: bloco `stack` é opcional; ausência = fluxo atual; dry-run em step 15 valida regressão zero.
- **Complexidade do Gate 2 por camada.** Mitigação: kata-quality-gate ganha lógica de subset (filtra ACs e componentes por layer); testes manuais antes do merge.
- **Athena propor decomposição ruim** (camadas não independentes ou granularidade errada). Mitigação: humano aprova no Gate 1; codex orienta Athena com critérios de "independência de review" e "camadas óbvias".
- **Conflito com plan-005 se mergearem em paralelo.** Mitigação: ambos tocam `cry-new-stacked-pr`, mas em seções diferentes (plan-005 adiciona dispatch por tool; plan-006 não toca o cry). Sem conflito esperado, mas merger atento.
- **Lexis em 3 línguas com mudança grande.** Mitigação: trechos novos seguem template existente; revisão manual obrigatória na tradução.

## Verificação

1. `lex-issue-driven.md` (3 línguas) contém seção sobre Decision Checklist na Phase 3 e bloco `stack` no schema do checkpoint
2. `warrior-athena.md` (3 línguas) referencia `codex-stacked-prs` e `kata-stacked-pr-create`
3. `kata-quality-gate.md` (3 línguas) descreve avaliação por camada
4. `lex-pr-quality.md` (3 línguas) HARD-GATE clarifica escopo "per PR da stack"
5. Checkpoint sintético com bloco `stack` é parsed sem erro pelo install.py / scripts de validação
6. Fluxo sem stack (issue simples) continua funcionando idêntico ao antes do plan-006 — regressão zero
7. PR final referencia `Closes #{N}` e a PR do plan-004; HARD-GATE de `lex-pr-quality` atendido
