---
plan_id: "039"
title: "pr-cost-stamp-implementation-time"
status: in-progress
agent: claude
issue: "guardiatechnology/ahrena#71"
created_at: "2026-05-09T22:00:00Z"
updated_at: "2026-05-09T22:30:00Z"
---

# Plan: Adicionar tempo de implementação ao stamp de custo da PR

## Objetivo

Estender o stamp de custo da PR (entregue em plan-007 / PR #68) para incluir uma terceira dimensão: **tempo de implementação**. Hoje o bloco mostra tokens e custo estimado em USD. A extensão adiciona duas métricas que aparecem sempre juntas quando `pr_cost_tracking.enabled: true`: (a) **tempo ativo de sessão** — soma de janelas com gap < `idle_gap_minutes` por `sessionId`, equivale a "horas de trabalho assistido por IA"; (b) **tempo de calendário** — `[branch_creation → merged_or_now]`. Mesmo opt-in, mesma idempotência via marcadores HTML, mesmo caminho não-bloqueante.

## Contexto

- O stamp atual (`kata-pr-cost-stamp`, `codex-pr-cost-tracking`, `scripts/pr-cost-stamp.sh`) usa `ccusage daily --project=<id>` como backend primário e fallback Bash que parseia JSONL diretamente.
- Os logs JSONL do Claude Code trazem `timestamp` por turno e `sessionId` por conversa. Isso permite derivar:
  - **Active session time:** para cada `sessionId`, ordenar turnos por `timestamp`, partir em "janelas ativas" sempre que houver gap maior que um threshold de inatividade (proposta: 10 min); somar a duração de cada janela. O total cross-sessions é a estimativa de horas de trabalho engajado com a IA.
  - **ccusage blocks:** o subcomando `ccusage blocks --json` agrupa atividade em blocos de billing de 5h. É menos preciso para "trabalho engajado" (5h é o teto, não o ativo), mas serve como sanity check.
- Tempo de calendário é trivial: `git log --reverse <base>..<head> --format=%cI | head -1` para o início e `gh pr view --json mergedAt,createdAt,state` para o fim (merged → `mergedAt`; aberta → `now`).
- A "fatura" para um time não é só o USD — é também quantas horas a feature consumiu de assistência IA. Ter as duas dimensões juntas dá ROI por PR mais legível.

## Escopo

### Artefatos a atualizar (3 idiomas cada)

| Pilar | Arquivo | Mudança |
|---|---|---|
| Codex | `_foundation/tooling/codex/codex-pr-cost-tracking.md` | Nova seção "Tempo de implementação" descrevendo as duas métricas, fonte de dados (JSONL `timestamp`/`sessionId` + `ccusage blocks` para sanity), threshold de gap de inatividade (10 min default, sub-flag `pr_cost_tracking.idle_gap_minutes`), formato dos novos campos no bloco, limitações (ex.: turno único conta como duração mínima de 1 min) |
| Kata | `_foundation/tooling/katas/kata-pr-cost-stamp.md` | Novo Passo 3.5 "Computar tempo de implementação"; novo Passo 4 (renderização) com 2 linhas adicionais na tabela; fluxo de fallback para tempo (script Bash) |
| Lexis | `_foundation/process/lexis/lex-directives.md` | Linha adicional na tabela "Application by section" para `pr_cost_tracking.idle_gap_minutes` |
| Sample | `framework/.directives.sample` | Estender o bloco `pr_cost_tracking` com `idle_gap_minutes` e seu default |

### Atualizações no script fallback

- `scripts/pr-cost-stamp.sh`: adicionar agregação de tempo ativo lendo `timestamp` e `sessionId` dos JSONL filtrados; emitir `totals.active_minutes` e `totals.calendar_minutes` no JSON de saída. Cost continua `cost_unavailable: true` no fallback (sem mudança).

### Formato proposto do bloco atualizado

```markdown
<!-- ahrena:cost-stamp:start -->
## AI Assistance Cost (Claude Code)

| Métrica | Valor |
|---|---|
| Sessões | 3 |
| Tokens de input | 245.892 |
| Tokens de output | 18.432 |
| Cache reads | 1.245.888 |
| Cache writes | 89.234 |
| Custo estimado | $4.32 USD |
| **Tempo ativo** | **2h 47min** |
| **Tempo de calendário** | **1d 4h** (2026-05-04 → 2026-05-05) |
| Modelos | claude-opus-4-7 (78%), claude-sonnet-4-6 (22%) |

_Computado por `kata-pr-cost-stamp` em 2026-05-09T01:30:00Z. Janela: 2026-05-04 → agora. Fonte: ccusage 1.x._
_Tempo ativo = soma de janelas com gap < 10min entre turnos. Estimativas baseadas em pricing público da Anthropic; a fatura real vem do console._
<!-- ahrena:cost-stamp:end -->
```

Tempo ativo e tempo de calendário aparecem sempre que o stamp está ligado (`pr_cost_tracking.enabled: true`).

### Novas chaves de `.directives`

```yaml
pr_cost_tracking:
  enabled: false
  currency: USD
  include_cache_breakdown: true
  # nova:
  idle_gap_minutes: 10            # gap (min) que separa janelas ativas
```

## Fora de escopo

- **Tempo gasto fora do Claude Code** (revisão humana, leitura de Notion, reuniões). O stamp continua sendo "custo de assistência IA", não esforço total da feature.
- **Cross-machine merge de tempo.** Se o dev trabalhou em duas máquinas, só a máquina que rodou o kata é considerada. Mesma limitação do tokens/USD.
- **Cursor/outros agentes.** Apenas Claude Code, como no stamp original.
- **Gráficos/dashboards de tendência por PR.** Continua tema próprio.
- **Bilhetagem fiscal real.** Tempo ativo é estimativa baseada em logs locais, não substitui controle de horas.

## Steps

- [x] 1. Validar premissa via doc oficial: confirmado em `docs/guide/json-output.md` do `ccusage` que (a) JSON usa camelCase (`inputTokens`, `cacheReadTokens`, `modelBreakdowns`); (b) `daily` aceita `--project` e `--since`/`--until`; (c) **NENHUM** subcomando expõe `timestamp` por turno — `blocks` agrega em janelas de 5h (`blockStart`/`blockEnd`) e `session` só tem `lastActivity` (data). Conclusão: parsing direto dos JSONL é o único caminho viável para tempo ativo preciso.
- [x] 2. Decisão registrada: caminho **2a (parsing direto dos JSONL)**. Centralizado em `scripts/pr-cost-stamp.sh` (fonte única de verdade para tempo ativo + tempo de calendário); kata invoca o script para tempo independentemente de qual backend (`ccusage` ou fallback) está fornecendo tokens/USD. 2b (`ccusage blocks`) descartado: bloco de 5h é teto, não medida de engajamento.
- [x] 3. Issue aberta: guardiatechnology/ahrena#71 (template feature-request; labels `feature request ➕`, `enhancement 🔝`, `documentation 📃`; Issue Type `Feature`; assignee `@me`; corpo com Why/What/How)
- [x] 4. Branch `feat/71-pr-cost-stamp-implementation-time` e worktree em `.worktrees/71-pr-cost-stamp-implementation-time/` criados a partir de `origin/main`
- [x] 5. Status deste plan atualizado para `in-progress`
- [ ] 6. Estender `scripts/pr-cost-stamp.sh`: novas flags `--idle-gap-minutes`, agregação de janelas ativas por `sessionId`, novos campos no JSON de saída (`totals.active_minutes`, `totals.calendar_minutes` quando branch fornecida)
- [ ] 7. Smoke do script atualizado em uma branch real do repo (rodar contra a própria worktree)
- [ ] 8. Atualizar `kata-pr-cost-stamp.md` em pt-BR (Passo 3.5 + tabela renderizada + Passo 6 com novos checks)
- [ ] 9. Traduzir as mudanças do kata para `es` e `en`
- [ ] 10. Atualizar `codex-pr-cost-tracking.md` em pt-BR (nova seção "Tempo de implementação", limitações, decisões vigentes atualizadas)
- [ ] 11. Traduzir as mudanças do codex para `es` e `en`
- [ ] 12. Atualizar `framework/.directives.sample` com `idle_gap_minutes` + comentário explicativo
- [ ] 13. Atualizar `lex-directives.md` (3 línguas) — adicionar `pr_cost_tracking.idle_gap_minutes` na tabela "Application by section"
- [ ] 14. Rodar `python3 scripts/install.py --self --target . --platform claude-code` e `--platform cursor` no worktree para sincronizar artefatos derivados
- [ ] 15. Smoke ponta-a-ponta: ativar `pr_cost_tracking.enabled: true` localmente, rodar `kata-pr-cost-stamp` numa PR teste; validar que tempo ativo aparece com unidade legível (`Xh Ymin` ou `Ymin`); rodar 2x para validar idempotência
- [ ] 16. Smoke do fallback: matar `npx ccusage` (forçar erro), rodar e validar que o tempo ativo continua aparecendo via fallback
- [ ] 17. Commits atômicos por artefato (subject em inglês; assinados por GPG)
- [ ] 18. Push e abrir PR via `kata-contributing-pr`; PR final dogfooda o stamp atualizado, mostrando seu próprio tempo ativo
- [ ] 19. Após merge: arquivar este plan e remover worktree (`git worktree remove`, `git branch -d`)

## Dependências

- Stamp atual já em `main` (PR #68 mergeado em `e433e91`) — confirmado.
- `ccusage` continua disponível e estável em `--json` (validar no step 1).
- `~/.claude/projects/<id>/*.jsonl` traz `timestamp` por turno (formato ISO 8601 + `sessionId`) — confirmado pela inspeção do fallback atual.
- Sem dependência em plans posteriores (008+).

## Riscos

- **Cálculo de tempo ativo é heurística.** Threshold de 10 min pode subestimar (turno longo de leitura) ou superestimar (idle entre turnos). Mitigação: tornar configurável via `idle_gap_minutes`; codex documenta o tradeoff e mostra a definição na linha de procedência do bloco.
- **Mudanças no formato JSONL do Claude Code.** Se a Anthropic mudar `timestamp`/`sessionId`, parsing quebra. Mitigação: kata é não-bloqueante (warning + skip); smoke test mensal manual.
- **Tempo ativo cross-machine.** Mesma limitação do USD; documentar.
- **Stacked PRs.** Janelas se sobrepõem entre camadas, então a soma de tempos ativos das PRs da stack > tempo ativo real. Mitigação: codex documenta; aceitar imprecisão.
- **Adicionar 2 linhas ao bloco aumenta verbosidade.** Mitigação: ambas entram na tabela existente, sem nova seção; rótulos curtos (`Tempo ativo`, `Tempo de calendário`).
- **Diff entre 3 idiomas vai ficar grande.** Mitigação: padronizar diff em pt-BR primeiro, traduzir es/en mecanicamente, validar via revisão humana focada em rótulos.

## Verificação

1. **Estrutura:** kata + codex (3 línguas) + lex-directives (3 línguas) + script fallback + sample atualizados
2. **Diretiva:** `idle_gap_minutes` presente em `.directives.sample` com default 10
3. **Renderização:** linhas "Tempo ativo" e "Tempo de calendário" sempre presentes quando `enabled: true`
4. **Idempotência:** rodar 2x sem nova sessão produz o mesmo body
5. **Fallback:** script Bash emite `totals.active_minutes` quando ccusage indisponível
6. **Dogfooding:** PR final traz seu próprio tempo ativo no body
7. **Regressão zero:** projetos com `pr_cost_tracking.enabled: false` não veem mudança
