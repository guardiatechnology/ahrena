---
plan_id: "041"
title: "pr-cost-stamp-scope-and-review"
status: in-progress
agent: claude
issue: "guardiatechnology/ahrena#77"
created_at: "2026-05-10T13:00:00Z"
updated_at: "2026-05-10T18:25:00Z"
---

# Plan: Atribuição fina do stamp + custo de revisão na PR

## Objetivo

Refinar duas dimensões do stamp de custo da PR (entregue em #68 e estendido em #72) para que o número exibido reflita melhor a realidade do trabalho que originou a PR e o esforço de revisão sobre ela:

1. **Atribuição fina:** filtrar tokens/tempo apenas aos turnos Claude Code que efetivamente trabalharam **nesta branch**, eliminando o ruído de "tudo que rodou no projeto durante a janela". Hoje, qualquer sessão paralela (perguntas off-topic, outra feature na mesma main checkout) entra na conta.
2. **Custo de revisão:** separar o stamp em **Development** + **Review** + **Total**, onde Review agrega esforço de qualquer revisor AI que comentou na PR (Claude Code via `/review`/`warrior-argos`, Ultrareview, Gemini Code Assist, Cursor, e outros que apareçam no histórico de comments).

Mesmo opt-in (`pr_cost_tracking.enabled: true`), mesma idempotência via marcadores HTML, mesmo caminho não-bloqueante.

## Contexto

### Por que hoje não atribui bem

O stamp atual filtra turnos JSONL por (a) `--project=<id>` (matching de hash do path do repo) e (b) `--since <YYYYMMDD>` (data do primeiro commit da branch). Resultado: **toda** sessão Claude Code naquele projeto entre `branch_creation` e agora entra na soma. Não há sinal no JSONL que correlacione um turno a uma branch específica — `cwd` ajuda só quando o dev usa worktrees dedicados, e mesmo assim não captura o caso "dev rodou Claude Code no main checkout depois de fazer checkout da branch".

`ccusage` não expõe metadado de branch por turno, e aumentar o filtro temporal (mid-day cutoff) ajudaria pouco — branches paralelas no mesmo dia continuariam misturadas.

### Por que separar review

O stamp atual mede "custo de criação". O custo real de uma feature inclui o ciclo de revisão — que pode rivalizar ou superar o custo de dev quando há iteração com agentes AI revisores (já é o caso do PR #72: a revisão do Gemini foi automática; uma revisão Claude/Ultrareview adicionaria mais turnos). Saber **quanto da fatura é dev × review** dá leitura mais útil para retros e ROI por PR.

### Achados de feasibility por fonte de revisão

| Fonte | Pode pegar USD? | Pode pegar contagem/atividade? | Estratégia |
|-------|:---------------:|:------------------------------:|------------|
| Claude Code local (`/review`, `warrior-argos`) | **Sim** (JSONL local com tag `purpose=review`) | Sim | Hook captura `purpose`; kata bucket-iza por tag |
| Ultrareview (Anthropic cloud) | **Não pública** | Sim (via PR reviews/comments do bot author) | Conta ocorrências e linka billing dashboard |
| Gemini Code Assist | **Não pública** (Google-managed) | Sim (PR reviews do `gemini-code-assist[bot]`) | Conta ocorrências; sem USD |
| Cursor / outros agentes | **Não exposta** | Talvez (depende se commenta na PR e se o author é detectável) | Conta ocorrências quando autor identificável |

**USD agregado é honesto:** soma só o que temos USD para (Claude local). Linha "Ocorrências externas" lista revisores sem USD. Bloco declara explicitamente o que entra e o que não entra na soma.

## Escopo

### Componentes a entregar

#### 1. Hook de atribuição (Fase 2 — fonte do dado fino)

**Onde:** novo `framework/templates/claude-code-hooks/pr-cost-attribution.sh` + entries em `.claude/settings.json` install via `scripts/install.py`.

**Eventos:** `UserPromptSubmit` (a cada turno do usuário) e `SessionStart`.

**O que grava:** uma linha JSONL por turno em `~/.claude/projects/<hash>/branches.jsonl`:

```json
{
  "ts": "2026-05-10T13:42:11Z",
  "session_id": "<sessionId>",
  "project_id": "<hash>",
  "repo": "guardiatechnology/ahrena",
  "branch": "feat/71-pr-cost-stamp-implementation-time",
  "cwd": "/Users/.../.worktrees/71-...",
  "purpose": "dev"
}
```

**Captura de `purpose`** (cascata, primeiro match vence):
1. Env var `GUARDIA_PURPOSE` setada na sessão (ex.: `review`, `dev`, `refactor`) → usa esse valor literal.
2. Heurística do prompt (best-effort no hook): primeira linha do prompt do turno começa com `/review`, `review pr`, `review #<N>`, `revise pr`, `revisar pr`, ou contém `pull request review` → marca `purpose=review` para o turno corrente.
3. Default: `purpose=dev`.

A heurística do item (2) é "best-effort por turno" — não persiste decisão entre turnos. Quem quer atribuição garantida usa o item (1) (env var ou via `cry-pr-review`, ver componente 1b).

**Performance:** ~50ms por turno (`git rev-parse --abbrev-ref HEAD`, `git remote get-url origin`, `pwd`, append a 1 arquivo).

**Cleanup:** sem TTL automático nesta iteração; `branches.jsonl` cresce com o uso; documentado como "purga manual quando passar de 50 MB". Iteração futura pode rotacionar.

#### 1b. Mecanismo de tag para sessões de revisão (auto-contido)

Como plan-036 (`warrior-argos-pr-reviewer`) foi arquivado, plan-041 entrega o caminho completo para que sessões de review sejam contabilizadas separadamente — sem depender de outro plan.

Três caminhos complementares; o usuário escolhe o que couber:

**A) `cry-pr-review` — caminho recomendado.** Novo Cry em `framework/{lang}/_foundation/tooling/cries/cry-pr-review.md` (3 idiomas) que invoca `kata-pr-review` (a criar). O kata é só um wrapper instrucional curto que (i) recomenda exportar `GUARDIA_PURPOSE=review` antes de iniciar a sessão de review e (ii) chama `/review` ou um prompt instruído de revisão. Documenta-se que o usuário pode rodar `GUARDIA_PURPOSE=review claude` no shell, ou colocar `export GUARDIA_PURPOSE=review` num pre-launch script de review.

**B) Heurística no hook.** Cobre o caso "esqueci de exportar a env var" — descrita em (2) acima. Não substitui o caminho A; é rede de segurança.

**C) Convenção textual no prompt.** Documentada no `codex-pr-cost-tracking`: começar a sessão com prompt `/review PR #<N>` ou `revise PR #<N>` é o gatilho que a heurística captura. Vira parte da etiqueta de uso do framework, não exige automação adicional.

**Por que não criar warrior-pr-reviewer aqui:** plan-036 era um warrior pleno (orquestração de revisão). Aqui só precisamos de uma marcação de contexto para o stamp; um warrior dedicado é over-engineering. Se no futuro alguém criar um warrior de revisão, ele só precisa exportar `GUARDIA_PURPOSE=review` para se integrar — sem mudanças no stamp.

Componente A (`cry-pr-review` + `kata-pr-review`) é o entregável novo deste sub-bloco. Componentes B e C são propriedades do hook + documentação no codex (tratados nos componentes 1 e 2 acima).

#### 2. Filtro fino no kata + script (consumo do dado)

`scripts/pr-cost-stamp.sh` ganha duas flags:

| Flag | Tipo | Efeito |
|------|------|--------|
| `--branch <name>` | string opcional | Inclui só turnos cujo `branches.jsonl` registra `branch == <name>` para o `session_id` daquele turno |
| `--purpose <dev\|review>` | string opcional | Bucketiza turnos: filtra por `purpose == <value>` |

**Fallback em ausência de `branches.jsonl`:**
- Se o sidecar não existe → comportamento atual (filtro só por project + since), com warning no `meta.warnings: ["no branch attribution data; counts may include off-branch sessions"]`.
- Se existe parcialmente → mistura: turnos com sidecar usam o filtro, turnos sem sidecar contam pelo modelo antigo (com warning).

Isso preserva backward compat e permite rollout gradual.

`kata-pr-cost-stamp` (3 línguas) ganha:
- Step 4 invoca o script duas vezes:
  - `--branch <HEAD_REF> --purpose dev` → bucket "Development"
  - `--branch <HEAD_REF> --purpose review` → bucket "Review (Claude Code)"

#### 3. Detector de revisores externos via PR comments

Novo `scripts/pr-cost-stamp-reviews.sh`:

```bash
gh pr view <PR> --json reviews,comments --jq '
  [
    (.reviews // [])[] | { author: .author.login, ts: .submittedAt, kind: "review" },
    (.comments // [])[] | { author: .author.login, ts: .createdAt, kind: "comment" }
  ]
  | group_by(.author)
  | map({
      author: .[0].author,
      count: length,
      first_at: (map(.ts) | min),
      last_at: (map(.ts) | max)
    })
'
```

Output JSON: lista de autores com `count` por autor. Kata aplica heurística:

| Author pattern | Classificação |
|----------------|---------------|
| `*[bot]` ending | AI (não-humano) |
| Conhecidos: `gemini-code-assist[bot]`, `claude[bot]`, `coderabbitai[bot]`, etc. | AI revisor com label conhecida |
| Owner do repo / membros (autenticados via `--json author.user`) | Humano |

Lista de autores conhecidos vai em `framework/.directives.sample` como `pr_cost_tracking.known_ai_reviewers` (default ships com 4-5 mais comuns, projeto pode estender).

#### 4. Layout do bloco (subseções)

```markdown
<!-- ahrena:cost-stamp:start -->
## AI Assistance Cost (Claude Code)

### Development

| Metric | Value |
|---|---|
| Sessions | 3 |
| Input / Output tokens | 245,892 / 18,432 |
| Cache reads / writes | 1,245,888 / 89,234 |
| Estimated cost | $4.32 USD |
| Active time | 2h 47min |
| Calendar time | 1d 4h |
| Models | claude-opus-4-7 (78%), claude-sonnet-4-6 (22%) |

### Review

| Source | Sessions / Occurrences | USD | Active time |
|--------|:---------------------:|:---:|:-----------:|
| Claude Code (local, `purpose=review`) | 1 session | $1.10 | 18min |
| Ultrareview (Anthropic cloud) | 0 runs | — | — |
| Gemini Code Assist | 1 review | n/a | n/a |

### Total

**Tracked AI cost: $5.42 USD · 3h 5min active · 1d 4h calendar**
External AI activity (no public USD): 1 (Gemini)

_Computed by `kata-pr-cost-stamp` on <utc_now>. Window: <since> → <pr_end>. Source: ccusage 1.x + pr-cost-stamp.sh 1.2.0. Idle gap: 10min._
_Estimates based on Anthropic public pricing; the actual invoice comes from the console. External AI sources without public usage are listed for visibility only._
<!-- ahrena:cost-stamp:end -->
```

Quando uma seção fica vazia (sem reviews ainda; sem dev tags), renderiza só "—" mantendo o esqueleto, ou omite completamente; escolhido na implementação (proposta: omitir Review se zerado em todas as fontes).

#### 5. Diretivas

```yaml
pr_cost_tracking:
  enabled: false
  idle_gap_minutes: 10
  # novas:
  attribution_mode: hook                # hook | project (legacy)
  branches_sidecar_max_mb: 50           # warning quando ultrapassa
  known_ai_reviewers:
    - "gemini-code-assist[bot]"
    - "claude[bot]"
    - "coderabbitai[bot]"
    - "qodo-merge-pro[bot]"
```

`attribution_mode: project` mantém o comportamento atual (compat).

### Artefatos a tocar (3 idiomas onde aplicável)

| Pilar | Arquivo | Mudança |
|---|---|---|
| Codex | `_foundation/tooling/codex/codex-pr-cost-tracking.md` | Nova seção "Atribuição" (modo hook vs project), nova seção "Custo de revisão" (fontes, classificação, USD vs ocorrências), novo formato do bloco com subseções, decisões/limitações atualizadas |
| Kata | `_foundation/tooling/katas/kata-pr-cost-stamp.md` | Step 1 lê `attribution_mode`; Step 4 invoca `--branch --purpose dev`/`review`; Step 5 invoca `pr-cost-stamp-reviews.sh`; novo Step 6 renderiza subseções; Step 7 upsert |
| Lexis | `_foundation/process/lexis/lex-directives.md` | 3 linhas novas (`attribution_mode`, `branches_sidecar_max_mb`, `known_ai_reviewers`) |
| Sample | `framework/.directives.sample` | Bloco `pr_cost_tracking` estendido |
| Hook | `framework/templates/claude-code-hooks/pr-cost-attribution.sh` (novo) | Script captura branch+purpose (env var → heurística → default), append em sidecar |
| Install | `scripts/install.py` | Cria `.claude/settings.json` entries para `UserPromptSubmit`/`SessionStart` quando `pr_cost_tracking.enabled` e `attribution_mode: hook` |
| Script | `scripts/pr-cost-stamp.sh` | Flags `--branch`, `--purpose`; consumir `branches.jsonl` |
| Script | `scripts/pr-cost-stamp-reviews.sh` (novo) | Agrega autores de reviews/comments |
| Cry | `_foundation/tooling/cries/cry-pr-review.md` (novo, 3 idiomas) | Caminho oficial para iniciar sessão de revisão com `purpose=review` |
| Kata | `_foundation/tooling/katas/kata-pr-review.md` (novo, 3 idiomas) | Wrapper instrucional invocado por `cry-pr-review`: orienta `export GUARDIA_PURPOSE=review` + dispara `/review` |

### Block Schema

Para downstream consumers (futuras dashboards), o block fica versionado: `<!-- ahrena:cost-stamp:start v=2 -->`. Se vier um body com `v=1`, o kata faz upsert preservando subseções vazias com placeholder até a próxima execução.

## Fora de escopo

- **USD para revisores externos** (Gemini, Ultrareview, Cursor) — sem API pública de usage por-PR. Documentado como "n/a · listed for visibility".
- **Cross-machine merge** de turnos (continua só máquina onde rodou o kata).
- **Atribuição retroativa** para PRs antes do hook — modo `project` (atual) cobre como melhor esforço.
- **Histórico cross-PR** ou dashboards agregados — fora desta iteração.
- **Custo humano de revisão** (tempo de reviewer humano) — métrica de gestão, não de IA.
- **Validar autoria do hook** (assinatura, etc) — fica como "honor system" do dev local.

## Steps

- [ ] 1. Validar formato esperado de `~/.claude/settings.json` para hooks `UserPromptSubmit`/`SessionStart` na doc oficial do Claude Code; identificar qual env vars/payload o hook recebe (especialmente o conteúdo do prompt para a heurística do componente 1, item 2) e onde gravar `branches.jsonl` sem race condition.
- [ ] 2. Mapear nomes de bot conhecidos no histórico de PRs do repo (`gh search prs --review-comments-by app/...`) para popular default de `known_ai_reviewers` com cobertura realista.
- [ ] 3. Especificar a cascata de detecção de `purpose=review` (env var → heurística do prompt → default), congelar a lista de regex/prefixos da heurística e documentar a etiqueta de uso para o usuário (caminho A: `cry-pr-review`; caminho B: heurística; caminho C: convenção textual). Saída: rascunho do trecho que vai pro `codex-pr-cost-tracking` + lista canônica de gatilhos da heurística.
- [ ] 4. Abrir issue guarda-chuva (template feature-request, labels mirroradas, Why/What/How completo).
- [ ] 5. Branch + worktree (`feat/<N>-pr-cost-stamp-scope-and-review`).
- [ ] 6. Atualizar status deste plan para `in-progress`.
- [ ] 7. Implementar `framework/templates/claude-code-hooks/pr-cost-attribution.sh` (cascata env var → heurística → default). Smoke local: invoca com env var, sem env var + prompt `/review PR #1`, sem env var + prompt comum; valida que `branches.jsonl` tem entrada por turno com `purpose` correto; sem corromper concurrent writers.
- [ ] 8. Estender `scripts/install.py`: cria `.claude/settings.json` (ou merge com existente) com `hooks.UserPromptSubmit`/`SessionStart` apontando para o script, condicionado a `pr_cost_tracking.enabled` + `attribution_mode: hook`.
- [ ] 9. Estender `scripts/pr-cost-stamp.sh`: flags `--branch`, `--purpose`, `--branches-sidecar <path>`; consumir `branches.jsonl` para correlacionar `sessionId → branch/purpose`; emitir warning em `meta.warnings` quando sidecar ausente; bumpar VERSION para `1.2.0`.
- [ ] 10. Smoke do script: rodar com sidecar populado e validar que turnos off-branch são excluídos; rodar sem sidecar e validar que warning aparece e contagem cai pro modo legacy.
- [ ] 11. Implementar `scripts/pr-cost-stamp-reviews.sh`: invoca `gh pr view --json reviews,comments`, classifica autores via `known_ai_reviewers` + heurística `*[bot]`, emite JSON `{ai_reviewers: [...], human_reviewers: [...]}`.
- [ ] 12. Criar `kata-pr-review` (3 idiomas) em `_foundation/tooling/katas/`: wrapper curto que (i) lembra de exportar `GUARDIA_PURPOSE=review` antes da sessão, (ii) invoca `/review` com o PR alvo, (iii) referencia `codex-pr-cost-tracking` para o leitor entender por que isso importa.
- [ ] 13. Criar `cry-pr-review` (3 idiomas) em `_foundation/tooling/cries/`: invoca `kata-pr-review`. Cry não acessa Lexis nem Codex direto (per `lex-pilars`).
- [ ] 14. Atualizar `kata-pr-cost-stamp.md` (pt-BR, depois traduções): novos passos para invocar 2x o script (dev+review) e o reviews-script, novo formato de renderização com subseções.
- [ ] 15. Atualizar `codex-pr-cost-tracking.md` (3 idiomas): nova seção "Atribuição", nova seção "Custo de revisão" (incluindo a cascata env var → heurística → default e os 3 caminhos A/B/C), formato do bloco com subseções, limitações atualizadas (USD não disponível para revisores externos), versão do schema.
- [ ] 16. Atualizar `framework/.directives.sample` + `lex-directives.md` (3 idiomas) com `attribution_mode`, `branches_sidecar_max_mb`, `known_ai_reviewers`.
- [ ] 17. Rodar `python3 scripts/install.py --self --target . --platform {claude-code,cursor}` no worktree.
- [ ] 18. **Smoke ponta-a-ponta (atribuição):** ativar hook localmente (`pr_cost_tracking.attribution_mode: hook`), trabalhar em duas branches paralelas no mesmo projeto por alguns turnos cada, rodar o stamp na PR de uma das branches e validar que tokens/tempo da outra não aparecem. Backward smoke: desligar hook, rodar stamp em modo `project`, validar warning visível e mesmo comportamento de hoje.
- [ ] 19. **Smoke da cascata de purpose:** (a) `GUARDIA_PURPOSE=review claude` + prompt qualquer → sidecar grava `purpose=review`; (b) sem env var + prompt `/review PR #72` → heurística marca `purpose=review`; (c) sem env var + prompt comum → `purpose=dev`. Validar os 3 casos.
- [ ] 20. **Smoke do reviews-script:** rodar contra PR #72 (que já tem 1 review do `gemini-code-assist[bot]` + 1 da fernandoseguim) e validar classificação correta (1 AI / 1 humano).
- [ ] 21. **Smoke do `cry-pr-review`:** invocar o cry, validar que o kata orienta corretamente e que turnos subsequentes ganham `purpose=review` no sidecar.
- [ ] 22. Dogfood: stamp da própria PR mostra Dev e Review (esta PR ganha review do Gemini durante o ciclo, e idealmente uma rodada de `cry-pr-review` para popular a coluna Claude Code review).
- [ ] 23. Commits atômicos por componente (hook, script-cost extensão, script-reviews novo, kata-pr-review + cry-pr-review, codex, kata-pr-cost-stamp, lex/sample, sync).
- [ ] 24. Push, abrir PR via `kata-contributing-pr` com labels mirroradas + size + reviewer team.
- [ ] 25. Após merge: arquivar plan, remover worktree.

## Dependências

- Stamp base (#68 + #72) já em main.
- `gh` CLI autenticado para `gh pr view --json reviews,comments`.
- Hooks funcionais no Claude Code local (validar versão mínima no Step 1).
- Plan-036 (`warrior-argos-pr-reviewer`) está arquivado e **não** é dependência: este plan absorve toda a marcação de sessão de revisão via componente 1b (`cry-pr-review` + `kata-pr-review`) + cascata env var/heurística no hook. Se um futuro warrior de revisão for criado, basta exportar `GUARDIA_PURPOSE=review` para se integrar — sem mudanças no stamp.
- Sem dependência em outros planos.

## Riscos

- **Hook concurrent writes em `branches.jsonl`** podem corromper se duas sessões escreverem simultaneamente. Mitigação: append-only + `flock` quando disponível; em macOS sem flock, append simples (kernel garante atomicidade até PIPE_BUF). Documentar o tradeoff.
- **`branches.jsonl` cresce sem limite.** Mitigação: warning quando passa de `branches_sidecar_max_mb`; rotação automática fica para iteração futura.
- **Hook falha mascara dado.** Se o hook retorna não-zero, Claude Code (dependendo da versão) pode bloquear o turno. Mitigação: hook sempre retorna 0; falhas vão para stderr; smoke valida no Step 7.
- **Modo `project` (legacy) deixa de ser default.** Decisão: novos projetos com `pr_cost_tracking.enabled: true` ganham `attribution_mode: hook` por default. Projetos antigos com diretiva já existente continuam em `project` até migração explícita.
- **`known_ai_reviewers` desatualizado** quando aparecem novos bots. Mitigação: lista é configurável por projeto; codex orienta como adicionar; heurística `*[bot]` cobre o caso até a lista pegar o nome.
- **Ultrareview não dá USD.** Mitigação assumida: bloco mostra count + link para billing console quando o user setou `pr_cost_tracking.ultrareview_billing_url`. Documentado como "visibility only".
- **PRs grandes com muitos comentários ruidosos** (typos, drive-by) inflam contagem de "Review". Mitigação: contar só `reviews` formais (não `comments`) ou só primeira review por author. Decisão: começar com primeira review por author; `comments` ignorados por default.
- **Schema versionado quebra parser local antigo.** Mitigação: marker `v=2` é incremento; v=1 continua válido; downstream parsers detectam e adaptam.
- **Heurística do hook captura falso-positivo** (prompt menciona "review" sem ser sessão de revisão). Mitigação: lista de gatilhos é específica (regex/prefixos congelados no Step 3), não match livre por palavra; o caminho A (`cry-pr-review` com env var explícita) é o oficial e elimina o risco. Documentado no codex.
- **`cry-pr-review` adiciona um Cry trivial.** Mitigação: o Cry é fino e justificado por `lex-pilars` — Cries acionam Katas; o Kata encapsula a orientação ("export env, depois `/review`"). Alternativa rejeitada: deixar só convenção textual sem cry — perde descobribilidade.

## Verificação

1. **Hook funciona:** `branches.jsonl` ganha 1 linha por turno, com `branch`, `cwd`, `purpose`.
2. **Filtro fino exclui off-branch:** trabalhar 5 turnos na branch A e 5 na B no mesmo projeto/dia → stamp da PR de A mostra ~5 turnos, não 10.
3. **Subseções:** Dev e Review aparecem com números coerentes; Total agrega só USD disponível.
4. **Revisores externos contados:** Gemini (1 review na PR de teste) aparece na linha "Gemini Code Assist", USD = n/a.
5. **Backward compat:** projeto com `attribution_mode: project` continua funcionando como hoje, com warning de "no branch attribution data".
6. **Idempotência preservada:** rodar 2x sem novos turnos/reviews produz mesmo body.
7. **Dogfooding:** PR final do plano mostra subseções no próprio body, com revisões do ciclo já contabilizadas.
8. **Auto-suficiência:** plan-041 entrega Dev + Review sem depender de nenhum outro plan; futuro warrior de revisão (se criado) só precisa exportar `GUARDIA_PURPOSE=review` para se integrar.
