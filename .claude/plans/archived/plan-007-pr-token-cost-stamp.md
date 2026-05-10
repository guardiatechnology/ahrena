---
plan_id: "007"
title: "pr-token-cost-stamp"
status: in-progress
agent: claude
issue: "guardiatechnology/ahrena#67"
created_at: "2026-05-06T00:00:00Z"
updated_at: "2026-05-09T01:30:00Z"
---

# Plano: Stamp de custo de tokens (Claude Code) em PRs

## Objetivo

Computar tokens consumidos e custo estimado em USD durante o desenvolvimento que originou cada PR, e estampar esses números no body da PR. Entregar Codex de referência, Kata de cálculo/escrita, integração com `kata-contributing-pr` e diretiva opcional para opt-out por projeto. Independente dos plans 004/005/006 (que tratam de stacked PRs).

## Contexto

Claude Code persiste o histórico de cada sessão em arquivos JSONL sob `~/.claude/projects/<project-hash>/`. Cada turno registra tokens de input, output, cache reads e cache writes, mais o modelo usado. A ferramenta open-source [`ccusage`](https://github.com/ryoppippi/ccusage) parseia esses logs e produz relatórios agregados (diário, mensal, por sessão) com cálculo de custo em USD baseado na tabela de preços por modelo.

Hoje, PRs do framework não trazem informação sobre quanto da assistência IA custou. Adicionar essa informação:
- Dá visibilidade financeira (custo médio por feature, por bug, por refactor)
- Cria baseline para medir ROI da automação
- Ajuda a calibrar quando vale agente vs trabalho humano direto

Decisões confirmadas (2026-05-09):

1. **Backend:** `ccusage` como ferramenta primária (`npx ccusage@latest --json`); fallback de script Bash em `scripts/` que parseia JSONL diretamente quando `npx`/`node` não disponíveis. `jq` instalado localmente para o smoke do fallback.
2. **Adoção:** opcional. Sem nova Lexis. Projeto declara `pr_cost_tracking.enabled: true` em `.directives` para ativar
3. **Trigger:** step no `kata-contributing-pr` invoca `kata-pr-cost-stamp` antes do `gh pr create`/`gh pr edit`. Stamp roda também em PR updates (recalcula com sessões adicionais)
4. **Escopo de sessões:** filtro primário via flag nativa `ccusage session --project <repo-name>`; janela temporal `[branch_creation_date, now]`. O filtro por `cwd` permanece documentado como complemento, não como caminho principal
5. **Formato:** bloco markdown padronizado no body da PR, delimitado por marcadores HTML para idempotência (`<!-- ahrena:cost-stamp:start -->` ... `<!-- ahrena:cost-stamp:end -->`)
6. **Stacked PRs:** cada PR da stack ganha seu próprio stamp; janela temporal é `[branch_creation_date, current_time]` filtrada pelo branch checkout time (heurística — não é cirúrgico, mas serve)

## Escopo

### Artefatos a criar (3 idiomas)

| Pilar | Arquivo | Conteúdo principal |
|---|---|---|
| Codex | `_foundation/tooling/codex/codex-pr-cost-tracking.md` | Conceito, fonte de dados (Claude Code JSONL logs), tabela de preços por modelo (referência: docs Anthropic — não hardcodar; usar tabela do ccusage), formato do bloco de output, marcadores HTML de delimitação, integração com pre/post-merge tooling, considerações de privacidade (custo é dado interno; não publicar em repos públicos sem revisão) |
| Kata | `_foundation/tooling/katas/kata-pr-cost-stamp.md` | Validar `.directives.pr_cost_tracking.enabled` → invocar `ccusage --json --since {branch_date}` (ou fallback script) → filtrar sessões por `cwd` do projeto → agregar por modelo → renderizar bloco markdown → ler body atual da PR (`gh pr view --json body`) → fazer upsert do bloco entre os marcadores → atualizar PR (`gh pr edit --body`) |

### Atualizações

- `_foundation/contributing/katas/kata-contributing-pr.md` (3 línguas): adicionar step "Stamp de custo (opcional)" que invoca `kata-pr-cost-stamp` quando `.directives.pr_cost_tracking.enabled: true`. Step é não-bloqueante: falha do stamp não impede a PR.
- `framework/.directives.sample`: adicionar bloco comentado:
  ```yaml
  # ─── PR Cost Tracking ────────────────────────────────────────────
  # Computes Claude Code token consumption and USD cost for the
  # development that produced each PR, and stamps the result in the
  # PR body via kata-pr-cost-stamp. Disabled by default to keep
  # cost data inside teams that explicitly opt in.

  # pr_cost_tracking:
  #   enabled: false              # true | false
  #   currency: USD               # currency for display
  #   include_cache_breakdown: true   # show cache reads/writes separately
  ```
- `_foundation/process/lexis/lex-directives.md` (3 línguas): adicionar `pr_cost_tracking.*` à tabela "Application by section"
- `framework/platforms.yaml`: registrar `_foundation/tooling/codex/codex-pr-cost-tracking` e o kata em `cursor.rules`/`claude-code.rules`
- `scripts/pr-cost-stamp.sh` (novo): fallback script puro em Bash + `jq` que parseia JSONL diretamente quando `ccusage` não estiver disponível. Saída JSON compatível com o que o kata espera

### Formato do bloco no body da PR

```markdown
<!-- ahrena:cost-stamp:start -->
## AI Assistance Cost (Claude Code)

| Metric | Value |
|---|---|
| Sessions | 3 |
| Input tokens | 245,892 |
| Output tokens | 18,432 |
| Cache reads | 1,245,888 |
| Cache writes | 89,234 |
| Estimated cost | $4.32 USD |
| Models | claude-opus-4-7 (78%), claude-sonnet-4-6 (22%) |

_Computed by `kata-pr-cost-stamp` on 2026-05-06T14:32:00Z. Range: 2026-05-04 → now. Tool: ccusage 1.x._
<!-- ahrena:cost-stamp:end -->
```

Marcadores HTML garantem idempotência: re-rodar substitui o bloco em vez de duplicar.

## Fora de escopo

- **Cursor IDE** ou outros agentes — primeira iteração só Claude Code. Codex menciona Cursor como follow-up.
- **Aggregation cross-PR/cross-team dashboards** — a estampagem por PR é o input; analytics agregada é tema próprio.
- **Validação de pricing por API call** — depender de tabela mantida no ccusage; auditar trimestralmente. Hardcodar preços no kata é proibido.
- **Stamp em commits ou em issues** — só PR.
- **Custo de mão de obra humana** — só custo de IA.

## Steps

- [x] 1. Abrir issue guarda-chuva com template `feature-request`, labels e Issue Type apropriados → guardiatechnology/ahrena#67
- [x] 2. Criar branch `feat/67-pr-token-cost-stamp` e worktree em `.worktrees/67-pr-token-cost-stamp/`
- [x] 3. Atualizar status deste plan para `in-progress`
- [x] 4. Validar que `ccusage` instala e roda no ambiente: confirmado `npx ccusage@latest --help` ok; flags `--project` e `--instances` disponíveis nativamente
- [x] 5. Redigir `codex-pr-cost-tracking` em pt-BR
- [x] 6. Traduzir `codex-pr-cost-tracking` para `es` e `en`
- [x] 7. Redigir `kata-pr-cost-stamp` em pt-BR
- [x] 8. Traduzir `kata-pr-cost-stamp` para `es` e `en`
- [x] 9. Implementar `scripts/pr-cost-stamp.sh` (fallback puro Bash + jq, portátil bash 3.2+)
- [x] 10. Atualizar `kata-contributing-pr` (3 línguas) com step opcional "Stamp de custo"
- [x] 11. Adicionar bloco `pr_cost_tracking` em `framework/.directives.sample`
- [x] 12. Atualizar tabela em `lex-directives.md` (3 línguas)
- [x] 13. Adicionar entries em `framework/platforms.yaml`
- [x] 14. Rodar `python3 scripts/install.py --self --target . --platform {claude-code,cursor}` no worktree
- [x] 15. Smoke ccusage: `daily --project=<id> --since=<date>` retornou dados reais agregados; subcomando `daily` (não `session`) usado para o filtro `--project`; PROJECT_ID derivado de `dirname "$(git rev-parse --git-common-dir)"` para suportar worktrees
- [x] 16. Smoke fallback: `scripts/pr-cost-stamp.sh --project ahrena --since 20260508` retornou JSON com `totals` (11 sessões), `breakdown` por modelo, `cost_unavailable: true` por design
- [x] 17. Commits atômicos por artefato; subject em inglês + body bilíngue; assinados (5 commits: codex+platforms, kata, script, integração, sync+plan)
- [ ] 18. Push e abrir PR via `kata-contributing-pr` — esta própria PR vai trazer o stamp (dogfooding)
- [ ] 19. Após merge: arquivar plan e remover worktree

## Dependências

- `npx`/`node` disponível no ambiente (ou fallback via `scripts/pr-cost-stamp.sh`)
- `jq` instalado (para fallback)
- `gh` CLI autenticado (para `gh pr view`/`gh pr edit`)
- `~/.claude/projects/` populado (sessões Claude Code já rodaram)
- Tabela de preços do ccusage atualizada (versão >= 1.x — verificar no step 4)
- Nenhuma dependência em plans 004/005/006

## Riscos

- **Tabela de preços desatualizada gera número errado.** Mitigação: codex declara que a tabela é a do ccusage; auditoria trimestral; codex menciona que "Estimated cost" é estimativa, não fatura
- **Privacidade — exposição de custo em repo público.** Mitigação: feature é opt-in via `.directives`; codex alerta sobre publicar; possibilidade de bloquear via hook quando `gh repo view --json visibility` retornar `PUBLIC` (defer para iteração futura se demanda surgir)
- **Sessões cross-machine não capturadas.** Se dev trabalhou em duas máquinas, só a máquina onde roda o kata conta. Mitigação: codex documenta limitação; agregação cross-machine é fora de escopo
- **Janela temporal heurística (branch_date → now) inclui sessões off-topic.** Dev pode ter usado Claude Code para outras coisas no mesmo projeto durante o intervalo. Mitigação: filtro por `cwd` ajuda; codex documenta tradeoff; futura iteração pode usar `session_id` rastreado por hooks
- **Stacked PRs com múltiplas camadas — janelas se sobrepõem.** Mitigação: heurística "[branch_checkout_time, current_time]" por camada; aceitar imprecisão; codex documenta
- **`ccusage` mudar formato JSON entre versões.** Mitigação: kata fixa versão mínima testada; smoke test no step 4 valida

## Verificação

1. **Estrutura:** 2 artefatos novos × 3 línguas = 6 arquivos + 1 script Bash novo
2. **Diretiva:** bloco `pr_cost_tracking` presente em `.directives.sample` com `enabled: false` default
3. **Integração:** `kata-contributing-pr` (3 línguas) tem step opcional para o stamp
4. **Idempotência:** rodar `kata-pr-cost-stamp` 2x na mesma PR não duplica o bloco
5. **Fallback:** script Bash produz output equivalente ao do ccusage quando este não está disponível
6. **Dogfooding:** a PR final deste plan-007 traz o stamp gerado pela própria feature
7. **Regressão zero:** projetos com `pr_cost_tracking.enabled: false` (default) não veem mudança no comportamento de `kata-contributing-pr`
