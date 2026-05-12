# ADR-001: Workflow status unificado entre plano e Issue, com loop de revisão e notificações provider-agnósticas

- **Status:** proposed
- **Date:** 2026-05-11
- **Issue:** [#90](https://github.com/guardiatechnology/ahrena/issues/90)

## Context

O framework Ahrena governa o ciclo de vida de planos (`lex-agent-planning`) com um enum legado de 5 valores: `pending | in-progress | done | archived | abandoned`. A Issue do GitHub que ancora o trabalho não tem labels canônicos correspondentes, e o PR não carrega marcação de fase. O resultado é triplo:

1. **Drift entre plano, Issue e PR.** O mesmo trabalho aparece com três rótulos diferentes (ex.: plano `in-progress`, Issue sem label, PR aberto). Auditoria fica fragmentada e o digest de planos perde fidelidade.
2. **"Sala de espera" da revisão é invisível.** Não há distinção entre "PR aberto aguardando reviewer começar" e "reviewer trabalhando agora". Isso impede SLA por estado, gera dupla-revisão acidental, e deixa PRs parados sem follow-up automático.
3. **Notificações de PR parado dependem de humano lembrar.** Quando o reviewer demora, ninguém é cobrado; o PR estagna silenciosamente.

Há ainda dois pontos que pressionam a evolução do enum:

- **Plan-027** entregou `warrior-janus` (release orchestrator). A transição `to release → release → done` precisa de owner formal — Janus é o owner, mas não há contrato de transição no Lex hoje.
- **Plan-044** vai entregar `warrior-eunomia`, que será owner único da criação inicial (`— → todo`). Hoje a criação é "qualquer agente", sem amarração do par Issue↔branch↔worktree.

Em paralelo, a comunidade do framework tem times com providers de notificação distintos (Slack na Guardia; Discord e Teams em projetos externos esperados). Hardcodar Slack em Lexis/Codex/Warriors trava a portabilidade.

## Decision

Adotamos o enum unificado de 7 status (mais 1 terminal alternativo) para planos, Issues e PRs:

```
todo → development → to review → review → to release → release → done
                          ↘            ↘            ↘
                          abandoned (terminal alternativo, qualquer estágio)
```

Semântica:

- `todo` — plano criado, Issue aberta, branch remota vinculada, worktree pronto, ainda não começou.
- `development` — implementação em andamento (Athena Phase 4 ativa).
- `to review` — PR aberto, esperando reviewer pegar.
- `review` — Argos (ou humano) revisando ativamente.
- `to release` — review aprovado, esperando o agente de release iniciar.
- `release` — release em execução (tag, build, deploy).
- `done` — ciclo encerrado.

**Owners por transição** ficam codificados em `lex-agent-planning`:

| Transição | Owner | Gatilho |
|---|---|---|
| `— → todo` | `warrior-eunomia` (fallback: agente da sessão enquanto não shipada) | Criação do par plano + Issue + branch + worktree |
| `todo → development` | `warrior-athena` | Phase 4 (delegação de implementação) |
| `development → to review` | `warrior-athena` | `kata-pr-prepare` abre PR |
| `to review → review` | `warrior-argos` | Argos inicia ciclo de revisão |
| `review → to review` | `warrior-argos` | Argos termina ciclo sem aprovar; devolve para fila |
| `to review → to release` | `warrior-athena` | Humano aprova PR (loop detecta `APPROVED`) |
| `to release → release` | `warrior-janus` | `kata-release-prepare` inicia; gate humano |
| `release → done` | `warrior-janus` | `kata-release-publish` conclui |
| `qualquer → abandoned` | criador ou owner atual | Plano descartado |

**Loop de revisão (Athena):** ao abrir o PR, Athena agenda 3 ciclos de 15 min via `ScheduleWakeup`. A cada ciclo consulta `gh pr view --json reviewDecision,reviews`; ao 3º ciclo sem aprovação humana, dispara notificação via MCP de notificação configurado em `.directives` (`notifications.provider`) no canal `notifications.channels.pr_review_timeout`.

**Notificações provider-agnósticas:** Lexis, Codex e Warriors referenciam apenas `notifications.provider` e `notifications.channels.{key}` lidas de `.ahrena/.directives`. O provider concreto vem do MCP server habilitado (Slack como provider inicial via `framework/mcp/slack.json` + `codex-mcp-slack`). Trocar de provider = editar `.directives` + ativar outro MCP server; Lexis/Codex/Warriors permanecem inalterados.

Canais lógicos canônicos:

- `notifications.channels.pr_review_timeout` — Athena, ao esgotar 3 ciclos sem aprovação.
- `notifications.channels.release_notify` — Janus, ao concluir publish.
- `notifications.channels.plans_status` — Eunomia (plan-044), digest periódico de planos.

## Consequences

### Positive

- **Auditoria unificada.** Plano, Issue e PR carregam o mesmo `status:*`, permitindo um digest e dashboards consistentes.
- **Sala de espera da revisão fica explícita.** Separar `to review` (queued) de `review` (active) habilita SLA por estado, evita dupla-revisão, e dá visibilidade a PRs parados.
- **Cobrança automática de PR parado.** Loop 3×15min substitui a memória humana; cobra exatamente uma vez ao final, sem ruído por ciclo.
- **Owners explícitos.** Quem mexe em cada label deixa de ser convenção e vira contrato testável.
- **Portabilidade de provider de notificação.** Time pode trocar Slack por Discord/Teams sem fork de Lexis/Codex/Warriors.
- **Base para Eunomia (plan-044) e PM topology (plan-038 reduzido).** Status unificado é precondição para o digest e para o cálculo agregado de child↔subtasks.

### Negative

- **Migração de planos legados.** 30+ planos existentes têm `status: pending | in-progress | done | archived`. Script `migrate_plan_status.py` é necessário, mais `git mv` de `pending/ → todo/`.
- **Mais labels no GitHub.** 7 labels novos (`status: <name>`) somam ao conjunto já existente; risco de poluição visual da Issue. Mitigado por cores em gradiente.
- **3 línguas de Lexis/Codex para manter.** Cada mudança no enum, lifecycle, ou owners precisa replicar em pt-BR, es, en. Custo recorrente.
- **Loop 3×15min pode ser curto fora de horário comercial.** Mitigado por parâmetros configuráveis em `.directives` (`workflow.review_loop.cycles`, `workflow.review_loop.interval_minutes`; defaults 3 e 15).
- **Dependência operacional do provider de notificação.** Se o MCP do provider cai, a cobrança no 3º ciclo falha silenciosamente. Mitigado por log + fallback "log warning, prosseguir" (documentado em `codex-notifications`).

### Neutral

- **`abandoned` permanece fora do happy path.** Continua aceito como valor terminal alternativo (qualquer estágio → `abandoned`). Migração preserva planos antigos com esse valor.
- **Pasta `pending/` renomeada para `todo/`.** Alinha nome de filesystem ao novo status. `archived/` permanece como organização pós-merge (não é mais um estado do enum).
- **Epic continua sem `status:*`.** Epic é decomposto por Calliope (plan-038) e nunca passa por Athena. Tem ciclo próprio ("open / closed via Tracked-by children"). Documentado em `lex-issue-status`.

## Alternatives Considered

- **(A) Manter o enum legado e adicionar um campo `review_state` separado no front-matter.** Rejeitada porque dois eixos de status paralelos fragmentam o audit trail, complicam a sincronização com labels da Issue/PR, e dificultam o digest de Eunomia. Um único eixo serializado é mais legível e fácil de validar.
- **(B) Enum reduzido sem separar `to review`/`review` e `to release`/`release`.** Rejeitada porque apaga a distinção entre "fila" e "execução" — exatamente a informação que justifica o loop 3×15min e o cálculo agregado de child↔subtasks no plan-038. Sem essa separação, a "sala de espera" continua invisível.
- **(C) Hardcodar Slack em Lexis/Codex/Warriors.** Rejeitada porque trava a portabilidade do framework e conflita com `lex-mcp` regra 5 (trade-off rationale por tier de transporte). A abstração `notifications.provider` custa baixa indireção e elimina o lock-in.
- **(D) Loop infinito até aprovação humana.** Rejeitada porque vira ruído e treina o canal a ignorar a notificação. 3 ciclos de 15 min (~45 min cumulativos) é equilíbrio entre dar margem ao reviewer e evitar fadiga de alerta. Configurável para times que precisam de janela maior.
- **(E) Notificar a cada ciclo (não só no 3º).** Rejeitada pelo mesmo motivo de (D): 3 notificações para o mesmo PR em 45 min é spam. Uma notificação ao final, com contexto completo (autor, reviewers solicitados, link), é informação suficiente para o canal agir.
