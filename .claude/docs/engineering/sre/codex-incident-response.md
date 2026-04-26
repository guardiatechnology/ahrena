# Codex: Incident Response

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Production incident response procedure — severity levels, communication, war room structure, rollback decisions, blameless post-mortem

## Content

### Severity

| Sev | Criterion | Response time | Who to trigger |
|---|---|---|---|
| **SEV-1** | Tier-1 production down or corrupted data; massive impact (>30% users) or security | < 5 min | On-call + IC + Eng lead + Executive comms |
| **SEV-2** | Significant degradation; impact to >5% users OR SLO in serious risk | < 15 min | On-call + IC |
| **SEV-3** | Partial degradation; users have workaround; SLO still within budget | < 1h | On-call |
| **SEV-4** | Isolated bug; no immediate impact in production | Business hours | Engineering ticket |

### Roles during the incident

- **Incident Commander (IC)**: coordinates, decides rollback, communicates. NOT the one who debugs — the one who orchestrates.
- **Technical Lead**: leads debugging, chooses hypotheses to investigate.
- **Communications Lead**: updates internal channels (Slack), external status page, email to customers if applicable.
- **Scribe**: maintains investigation timeline in central document (for post-mortem).

In small incidents (sev-3/4), on-call accumulates IC + Tech + Comms.

### Response flow (first 30 minutes)

```
t+0    Alert fires / human reports
        → on-call acknowledge in 5 min
        → IC declares severity

t+5    War room opened (Zoom/Google Meet + dedicated Slack channel)
        → Technicians enter; initial triage
        → Scribe starts timeline

t+10   Primary hypothesis defined
        → Dashboards opened (see runbook)
        → Decision: mitigate fast vs. debug

t+15   Mitigation applied (rollback, feature flag off, scale up, etc.)
        → Confirm recovery via metrics

t+20   Comms updates status page + internal Slack
        → "Identified, mitigating"

t+30   Mitigation confirmed recovery in metrics
        → IC declares "stable, monitoring"
        → Begin root cause investigation (calmly)
```

### Decision: rollback vs. forward-fix

**Rollback when:**
- Recent deploy (< 2h) is primary suspect.
- Quick mitigation available (previous version works).
- Rollback cost is low (no irreversible data migration).

**Forward-fix when:**
- Change is in data (not code) — code rollback doesn't resolve it.
- Rollback requires complex reverse database migration.
- Root cause already identified and fix is trivial.

**Default:** when in doubt, **rollback** — debug can continue in staging without impact on the customer.

### Communication

**Internal (Slack/Teams):**
- Dedicated channel (`#inc-YYYY-MM-DD-refund-outage`).
- Updates every 15 min even when nothing changes ("still investigating hypothesis X").
- Technical language OK; audience are engineers.

**External (status page, customer email):**
- Objective messages without technical details.
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
- NEVER speculate about cause to the customer before confirming.

**Executive (when sev-1 or duration > 1h):**
- Hourly update until resolved.
- Focus on business impact, not technical detail.

### Blameless post-mortem

After each sev-1 and sev-2 (sev-3/4 optional):

1. **Within 5 business days**, draft document:
   - Factual timeline (times, actions, decisions).
   - Measured impact (users affected, revenue, SLA).
   - Root cause (without pointing to people; point to systems and decisions).
   - Contributors (factors that worsened; e.g.: outdated runbook, late alert).
   - Corrective actions (specific, with owner and deadline).
   - What worked well (quick rollback, clear comms) — reinforce.

2. **Review meeting**: 1h with involved team + leaders; questions and criticism of the process decision, not the person.

3. **Corrective actions** enter backlog with P1-P2 priority; reviewed 30 days later.

### Anti-patterns in incident response

| Anti-pattern | Problem |
|---|---|
| Debug without declaring severity | Lack of IC; comms becomes chaos; stakeholders are in the dark |
| Rollback without writing timeline | Data loss for post-mortem |
| Blame the deploy author in post-mortem | Kills psychological safety; next time the author hides error |
| "Monitoring" indefinitely without confirmed recovery | Comms stalls; customer loses confidence |
| Ignore minor incidents (sev-3) without post-mortem | Pattern emerges; future sev-1 with already-seen cause |

### Typical tools

- **Alerting/paging:** PagerDuty, Opsgenie, Grafana OnCall
- **Status page:** statuspage.io, Atlassian Statuspage, self-hosted
- **War room:** Zoom, Google Meet, Slack Huddle
- **Incident management:** Incident.io, Rootly, FireHydrant
- **Post-mortem:** Markdown in repo, Notion, Confluence
