# Codex: Resposta a Incidentes

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Procedimento de resposta a incidentes em produção — severity levels, comunicação, estrutura de war room, decisões de rollback, post-mortem blameless

## Conteúdo

### Severidade

| Sev | Critério | Tempo de resposta | Quem acionar |
|---|---|---|---|
| **SEV-1** | Produção tier-1 down ou dados corrompidos; impacto massivo (>30% usuários) ou segurança | < 5 min | On-call + IC + Eng lead + Executive comms |
| **SEV-2** | Degradação significativa; impacto a >5% usuários OU SLO em risco grave | < 15 min | On-call + IC |
| **SEV-3** | Degradação parcial; usuários têm workaround; SLO ainda dentro do budget | < 1h | On-call |
| **SEV-4** | Bug isolado; sem impacto imediato em produção | Horário comercial | Engineering ticket |

### Papéis durante o incidente

- **Incident Commander (IC)**: coordena, decide rollback, comunica. NÃO é quem debuga — é quem orquestra.
- **Technical Lead**: líder do debugging, escolhe hipóteses para investigar.
- **Communications Lead**: atualiza canais internos (Slack), status page externa, email para clientes se aplicável.
- **Scribe**: mantém timeline da investigação em documento central (para post-mortem).

Em incidentes pequenos (sev-3/4), on-call acumula IC + Tech + Comms.

### Fluxo de resposta (primeiros 30 minutos)

```
t+0    Alert dispara / humano reporta
        → on-call acknowledge em 5 min
        → IC declara severity

t+5    War room aberto (Zoom/Google Meet + canal Slack dedicado)
        → Técnicos entram; triage inicial
        → Scribe inicia timeline

t+10   Hipótese primária definida
        → Dashboards abertos (ver runbook)
        → Decisão: mitigar rápido vs. debugar

t+15   Mitigação aplicada (rollback, feature flag off, scale up, etc.)
        → Confirmar recovery via métricas

t+20   Comms atualiza status page + Slack interno
        → "Identified, mitigating"

t+30   Mitigação confirmada recovery em métricas
        → IC declara "stable, monitoring"
        → Começa investigação de causa raiz (calma)
```

### Decisão: rollback vs. forward-fix

**Rollback quando:**
- Deploy recente (< 2h) é suspeito principal.
- Mitigação rápida disponível (versão anterior funciona).
- Custo de rollback é baixo (não há migração de dados irreversível).

**Forward-fix quando:**
- Mudança é em dados (não código) — rollback de código não resolve.
- Rollback requer migração de banco reversa complexa.
- Causa raiz já identificada e fix é trivial.

**Default:** quando em dúvida, **rollback** — debug pode continuar em staging sem impacto no cliente.

### Comunicação

**Interna (Slack/Teams):**
- Canal dedicado (`#inc-YYYY-MM-DD-refund-outage`).
- Updates a cada 15 min mesmo quando nada muda ("ainda investigando hipótese X").
- Linguagem técnica OK; audiência são engenheiros.

**Externa (status page, email clientes):**
- Mensagens objetivas sem detalhes técnicos.
- Template:
  ```
  {HH:MM UTC} — Investigating
    We're investigating reports of elevated errors on {feature}.
    Affected users may see {symptom}.

  {HH:MM UTC} — Identified
    We identified the cause and are applying a fix.

  {HH:MM UTC} — Monitoring
    Fix deployed. Monitoring for recovery.

  {HH:MM UTC} — Resolved
    Service is fully restored. Total duration: {X}. Post-mortem coming in {N} days.
  ```
- NUNCA especular sobre causa ao cliente antes de confirmar.

**Executivo (quando sev-1 ou duração > 1h):**
- Atualização horária até resolved.
- Foca em impacto de negócio, não detalhe técnico.

### Post-mortem blameless

Após cada sev-1 e sev-2 (sev-3/4 opcional):

1. **Em até 5 dias úteis**, redigir documento:
   - Timeline factual (horários, ações, decisões).
   - Impacto medido (usuários afetados, receita, SLA).
   - Causa raiz (sem apontar pessoas; apontar sistemas e decisões).
   - Contribuidores (fatores que agravaram; ex.: runbook desatualizado, alert tardio).
   - Ações corretivas (específicas, com owner e deadline).
   - O que funcionou bem (rollback rápido, comms clara) — reforçar.

2. **Revisão em reunião**: 1h com equipe envolvida + líderes; perguntas e críticas à decisão de processo, não à pessoa.

3. **Ações corretivas** entram em backlog com prioridade P1-P2; revisadas 30 dias depois.

### Anti-patterns em incident response

| Anti-pattern | Problema |
|---|---|
| Debugar sem declarar severity | Falta de IC; comms vira caos; stakeholders ficam no escuro |
| Rollback sem escrever timeline | Perda de dados para post-mortem |
| Culpar o autor do deploy no post-mortem | Mata psicológico safety; próxima vez o autor esconde erro |
| "Monitorando" indefinidamente sem recovery confirmado | Comms fica parado; cliente perde confiança |
| Ignorar incidentes menores (sev-3) sem post-mortem | Padrão emerge; sev-1 no futuro com causa já vista |

### Ferramentas típicas

- **Alerting/paging:** PagerDuty, Opsgenie, Grafana OnCall
- **Status page:** statuspage.io, Atlassian Statuspage, auto-hospedada
- **War room:** Zoom, Google Meet, Slack Huddle
- **Incident management:** Incident.io, Rootly, FireHydrant
- **Post-mortem:** Markdown em repo, Notion, Confluence
