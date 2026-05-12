# ADR-002: Issue-as-plan — armazenamento em três camadas (Issue body + `.plans/` cache + `.issues/` artifacts)

- **Status:** proposed
- **Date:** 2026-05-11
- **Issue:** [#96](https://github.com/guardiatechnology/ahrena/issues/96)
- **Builds on:** [ADR-001](ADR-001-workflow-status-unified-plan-and-issue.md) (workflow status unificado)

## Context

ADR-001 (entregue em PR #93) unificou o enum de `status:` entre plano, Issue e PR; codificou owners por transição (Eunomia/Athena/Argos/Janus); padronizou 7 labels canônicas; introduziu o loop de revisão 3×15min e o sub-ciclo Argos. O modelo de **armazenamento** do plano, entretanto, permaneceu inalterado: o plano é um arquivo Markdown committed em `.claude/plans/plan-{NNN}-{slug}.md`, e cada transição de `status:` exige um commit.

Três problemas tornaram-se visíveis depois do merge de ADR-001:

1. **Audit trail no lugar errado.** A cada toggle de `status:` (8 transições por ciclo no caso típico), um commit dedicado polui `git log`. O GitHub Issue já oferece um audit log nativo, com timestamp e autor por edição do body — replicar isso em git diff é redundância cara.
2. **Fricção bloqueia adoção da IA.** A IA precisa atualizar `status:` em pontos finos do fluxo (passos do plano, decisões intermediárias, próximas ações). Cerimônia de commit para cada edição transforma a IA em "robô que abre PR para mudar uma linha", contra `feedback_no_status_only_commits` (preferência registrada do usuário).
3. **Phase artifacts no lugar errado.** Os documentos produzidos pelo fluxo Issue-Driven (`01-brief.md` … `06-quality-report.md`) vivem em `docs/issues/issue-{N}/`. Mas `docs/` é product-facing (MkDocs serve essa raiz). Phase artifacts são operacionais, não documentação de produto. A localização mistura dois propósitos distintos.

## Decision

Adotamos um modelo de armazenamento em **três camadas** com papéis disjuntos:

### 1. GitHub Issue body — canônico

O body da Issue carrega o conteúdo canônico do plano: Summary + Plan section com **Objective**, **Steps**, **Risks**, **Dependencies**, **Open Questions**. Toda edição estrutural do plano (mudança de objective, adição de step, ajuste de risco) é uma edição no body da Issue.

Mecanismo de escrita: **MCP `update_issue` (GitHub MCP)** quando o server estiver listado em `mcp.servers` e ativo (per `lex-mcp` regra 1); fallback CLI documentado é `gh issue edit {N} --body-file <path>` (per `lex-mcp` regra 4: retry único, depois oferece escolha CLI/pausar/abortar).

Audit log = audit log nativo do GitHub (`PATCH /repos/{owner}/{repo}/issues/{N}` registra cada edição com timestamp e autor).

### 2. `.plans/{N}.md` — working memory da IA, gitignored

Cache local + scratchpad da IA, materializado em duas operações idempotentes:

- **`kata-load-plan-from-issue`** — invocado no início de cada sessão e em handoffs; copia o body da Issue para `.plans/{N}.md`. Comando canônico (MCP fallback): `gh issue view {N} --json body --jq .body > .plans/{N}.md`.
- **`kata-flush-plan-to-issue`** — invocado em transições de `status:`, em conclusões de Step, e no fim da sessão; lê `.plans/{N}.md`, filtra blocos marcados `<!-- not-flushed -->`, e atualiza o body da Issue.

Schema do `.plans/{N}.md` (per Open Question #4): **superset do body da Issue**. Carrega o body completo (espelhado) + seções locais marcadas `<!-- not-flushed -->` ... `<!-- /not-flushed -->`. Seções locais típicas: `## Working notes`, `## Next actions`, `## Scratch` — registro livre de decisões em rascunho, observações de debugging, próximos passos voláteis sem poluir o body canônico.

`.plans/` entra em `.gitignore` (e em `.gitignore.sample` distribuído pelo install).

### 3. `.issues/{N}/` — Phase artifacts, committed

Diretório committed na raiz do repo, espelha o número da Issue (sem prefix `issue-` — o nome do diretório já é semântico):

```
.issues/
└── {N}/
    ├── 01-brief.md
    ├── 02-requirements.md
    ├── 03-architecture.md
    ├── 05-security-review.md
    └── 06-quality-report.md
```

Move-se de `docs/issues/issue-{N}/` para `.issues/{N}/` — operação `git mv` preserva history. `docs/` continua product-facing; `.issues/` é operacional.

Adicionalmente: `.claude/plans/archived/` (histórico legado de planos pré-ADR-002) move-se para `.issues/_legacy/` via `git mv` (per Open Question #1). Arquivos preservados como audit imutável; README declara congelamento.

## Consequences

### Positivas

- **Audit no lugar certo.** Cada `status:` toggle vira uma edição no body da Issue, não um commit em git. `git log` foca em código entregue.
- **Fricção zero para a IA.** Editar `.plans/{N}.md` é Edit local — sem `git add`/`commit` por edição. Flush só na transição.
- **Source-of-truth claro.** A Issue é canônica. `.plans/` é cache regenerável (fresh clone perde `.plans/`; primeiro `kata-load-plan-from-issue` reconstrói).
- **Separação de propósitos.** `docs/` = produto; `.issues/` = operacional; `.plans/` = IA scratch. Cada camada tem dono e ciclo de vida distintos.
- **Plan-044 e plan-045 absorvidos.** Eunomia nasce no modelo novo (sem retrofit). Janus reescrito para o modelo de release-Issue (sem coding throw-away).

### Negativas

- **Histórico granular dos toggles fora do git.** Audit trail dos `status:` toggles deixa de aparecer em `git log` (vive em `gh api repos/.../issues/{N}/timeline`). Aceito: o GitHub timeline já é searchable e tem timestamp por edição.
- **`.plans/` sumiu de `grep -r`.** Pesquisas locais no working tree não acham o conteúdo dos planos. Mitigação: `kata-pull-issues` (opcional, futuro) cacheia bodies de Issues ativas em `.plans/_index.md` para grep local.
- **Custo de migração.** Repos consumidores que adotaram `docs/issues/issue-{N}/` precisam fazer `git mv docs/issues/ .issues/`. Janela de transição de 1 release (per Open Question #7): durante esse período, ambos caminhos são aceitos com warning visual; após o release seguinte, Gate 2 falha encontrando `docs/issues/`.
- **Flush conflitante entre sessões.** Se duas sessões editam `.plans/{N}.md` simultaneamente, o flush sobrescreve. Mitigação: `kata-flush-plan-to-issue` lê o body atual antes de gravar; se houve mudança remota desconhecida, alerta e oferece merge manual. Heartbeat de sessão (`codex-session-tracking`) permite detectar concorrência.

### Compatibilidade com ADR-001

Plan-046 **não substitui** ADR-001 — constrói por cima. Tudo que ADR-001 entregou continua válido:

- 7-status enum (`todo | development | to review | review | to release | release | done` + `abandoned`).
- Owners por transição (Eunomia/Athena/Argos/Janus).
- 7 labels canônicas com mutex.
- Notifications provider-agnósticas via MCP.
- Session tracking via heartbeat.
- Loop de revisão 3×15min (Athena).
- Sub-ciclo Argos.

O que muda é o **meio de armazenamento** do plano e a localização dos Phase artifacts.

### Split adicional do enum (dev cycle vs release cycle)

ADR-002 absorve plan-045 e introduz o split do `lex-issue-status` em **dois ciclos disjuntos sobre artefatos distintos**:

- **Tabela A — Dev cycle** (aplicável a Issues/PRs de feature/fix/chore/refactor/etc.): `todo → development → to review → review → done` + `abandoned`. Owners: Eunomia, Athena, Argos.
- **Tabela B — Release cycle** (aplicável **exclusivamente** a uma release Issue dedicada): `to release → release → done` + `abandoned`. Owner: Janus.

Sem release branches. Janus abre a **release Issue** como ponto de entrada do release cycle, popula `Tracks: #N1, #N2, ...` com os PRs mergeados desde o último tag, e conduz `to release → release → done`.

Mutex passa a ser **intra-artefato** (dentro de cada Issue/PR), não cross-artifact. HARD-GATE em `lex-issue-status` proíbe aplicar labels do release cycle em Issue/PR de feature, e vice-versa.

### Mapeamento de campos de auditoria de fechamento

Plan-043 (PR #93) estabeleceu `merge_commit:` e `closed_at:` como front-matter opcional para audit. No modelo de ADR-002:

- `closed_at` ≡ campo nativo `closedAt` da Issue do GitHub (`gh issue view {N} --json closedAt`).
- `merge_commit` ≡ `mergeCommit.oid` do PR linkado via `Closes #N` (`gh pr view {PR} --json mergeCommit`).

Para plans legados em `.issues/_legacy/` que mantêm o YAML front-matter histórico, `merge_commit:` e `closed_at:` ficam reconhecidos como front-matter opcional aceito — preserva o audit dos plans 043-045 sem retrofit.

## Cadência de load/flush

Per Open Question #3, sincronização em 3 gatilhos canônicos:

| Gatilho | Operação |
|---|---|
| Início de sessão / handoff entre agentes | `kata-load-plan-from-issue` |
| Transição de `status:` (todo→development, etc.) | `kata-flush-plan-to-issue` |
| Step do plano concluído (`[ ]` → `[x]`) | `kata-flush-plan-to-issue` |
| Fim de sessão (heartbeat conclui ou Athena/Argos sai) | `kata-flush-plan-to-issue` |

Toggles intermediários e edições de scratch são livres (não disparam flush). Documentação operacional em `codex-agent-planning` §9.

## Alternatives considered

1. **Manter plano em `.claude/plans/*.md` e tolerar fricção.** Rejeitado: contradiz `feedback_no_status_only_commits` e mantém audit no lugar errado.
2. **Mover plano para Notion.** Rejeitado: separa contexto do repo; rompe atomicidade entre plano e PR.
3. **Plano só na Issue, sem cache local.** Rejeitado: toda edição vira network call; offline impossível; IA perde flexibilidade de scratch.
4. **Manter `docs/issues/issue-{N}/`.** Rejeitado: `docs/` é product-facing (MkDocs); mistura propósitos. `.issues/` separa cleanly.

## References

- ADR-001 — workflow status unificado (precedente; plan-043 / PR #93)
- `lex-agent-planning` (reescrita) — passo (e) do HARD-GATE atualizado; Owners table reorganizada
- `lex-issue-status` (split) — Tabela A (dev) e Tabela B (release)
- `codex-agent-planning` (reescrita) — manual operacional do 3-layer model
- `kata-load-plan-from-issue`, `kata-flush-plan-to-issue` (novas katas)
- `lex-issue-driven`, `codex-issue-workflow` — path move `docs/issues/` → `.issues/`
- `warrior-janus` (reescrita) — release Issue como ponto de entrada do release cycle
- `warrior-eunomia` (nova) — criada no modelo novo (absorção de plan-044)
- `lex-mcp` regra 1 e regra 4 — preferência MCP + fallback CLI
