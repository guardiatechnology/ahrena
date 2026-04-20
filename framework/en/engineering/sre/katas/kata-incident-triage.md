# Kata: Incident Triage

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Procedure for the first 15 minutes of an incident — declare severity, trigger roles, orchestrate initial diagnosis, decide mitigation

## Objective

Upon receiving an alert (or human report) of a production incident, execute a structured triage procedure in the first 15 minutes: acknowledge the alert, declare severity, open war room, activate roles, initial diagnosis via runbook, and decision between quick mitigation (rollback/feature flag) or in-depth investigation. Produces initial timeline and structured communication.

## When to Use

- Response to sev-1 or sev-2 alert firing to on-call
- Human report of significant degradation in production
- Security incident detected (leaked credential, suspected intrusion)

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Initial signal | Yes | Alert (PagerDuty ticket), Slack message, human report |
| Affected service | Yes | Service name (to find runbook and owner) |
| Communication channel | Yes | Slack or equivalent for war room |

## Workflow

```
Progress:
- [ ] 1. Acknowledge in <5 min
- [ ] 2. Declare severity
- [ ] 3. Open war room + activate roles
- [ ] 4. Consult alert runbook
- [ ] 5. Initial diagnosis via dashboards/logs
- [ ] 6. Decide mitigation vs. debug
- [ ] 7. Apply mitigation (if decided) and verify recovery
- [ ] 8. Communicate status (internal + external if applicable)
- [ ] 9. Deliver initial timeline to IC
```

### Step 1: Acknowledge in <5 min

1. Open the alert in the paging system (PagerDuty etc.), formal acknowledgement.
2. Record timestamp t+0 (when alert fired).
3. If on-call is on another task: pause, escalate to backup if necessary.

### Step 2: Declare severity

Consult `codex-incident-response` §Severity:

- SEV-1: tier-1 production down OR corrupted data OR >30% users
- SEV-2: significant tier-1/2 degradation OR >5% users
- SEV-3: partial; workaround exists
- SEV-4: isolated; no immediate impact

Declare severity in the incident channel (Slack) explicitly:

```
🚨 SEV-2 declared
Service: refund-api
Symptom: p99 > 500ms sustained 5min, error rate 2%
```

### Step 3: Open war room + activate roles

**SEV-1:**
- Create dedicated Zoom/Meet (if configured, automatic link from the incident system).
- Create Slack channel `#inc-YYYY-MM-DD-{service}-{short-desc}`.
- Trigger: IC (incident commander), Technical Lead, Comms Lead, Scribe.

**SEV-2:**
- Slack channel sufficient; war room on call optional.
- Trigger: IC + Technical Lead (on-call can accumulate).

**SEV-3:**
- Slack channel; on-call accumulates all roles.

If on-call is the **Hestia-spawn** (AI agent): Scribe/Comms role is ideal (keeps structured timeline); decisions stay with human.

### Step 4: Consult alert runbook

1. Open `runbook_url` of the alert (see `lex-runbook-for-every-alert`).
2. Read Symptoms, Impact, Diagnosis.
3. Share link in the channel:
   ```
   📘 Runbook: {url}
   ```

### Step 5: Initial diagnosis

According to runbook:

1. **Dashboards**: open the links; capture screenshots in the Slack channel with timestamps.
2. **Logs**: structured query in CloudWatch Logs / Datadog / Loki; filter by correlation_id if available.
3. **Traces**: open APM/X-Ray; identify slow or failing operations.
4. **Hypotheses**: list 2-3 in order of prevalence according to runbook. Mark which is being tested.

Share findings in the channel in real time — scribe ensures everything has a timestamp.

### Step 6: Decide mitigation vs. debug

According to `codex-incident-response` §Rollback vs. forward-fix:

| Situation | Action |
|---|---|
| Recent deploy (< 2h) + no data migration | Rollback |
| Problem in already-persisted data | Forward-fix |
| Clear root cause and trivial fix | Quick forward-fix |
| Obscure root cause + high impact | Rollback + investigation in staging |

When in doubt: **rollback**. Mitigate first, understand later.

### Step 7: Apply mitigation + verify recovery

Execute decided action:

- **Deploy rollback**: revert in pipeline, confirm via dashboard.
- **Feature flag off**: via flag system (LaunchDarkly, Unleash).
- **Scale up**: add instances if resource saturation.
- **Block malicious input**: WAF rule, rate limit.

**Verify recovery**: wait 5-10 min observing:
- Error rate returns to baseline.
- Latency p99 returns to normal.
- Alerts stop firing.

If it does NOT recover in 10 min → escalate severity or wrong hypothesis; return to Step 5.

### Step 8: Communicate status

**Internal** (incident channel):
```
✅ Mitigation applied — rolling back to v1.34.2
[15:42] Error rate dropping; p99 recovering
[15:47] Stable — monitoring for 10 min before declaring resolved
```

**External** (if SEV-1 or SEV-2 with customer impact):
- Update status page in each state: Investigating → Identified → Monitoring → Resolved.
- Comms Lead writes; IC approves; no one else publishes.

**Executive** (if SEV-1 or duration >1h):
- Email/Slack DM to leadership every hour or on state change.

### Step 9: Deliver initial timeline

Before leaving "triage mode" and entering "investigation mode":

1. Consolidate structured timeline in central document:
   ```markdown
   # Timeline — {service} {date}

   | Time (UTC) | Event |
   |---|---|
   | 14:32 | Alert fires — p99 > 500ms |
   | 14:35 | On-call acknowledge, SEV-2 declared |
   | 14:38 | War room opened |
   | ... |
   ```

2. This document feeds the post-mortem (`kata-postmortem-write`).

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Declared severity + activations | Structured message | Incident channel |
| Initial timeline | Markdown | Central document (Notion, Google Docs, repo) |
| Applied mitigation + confirmed recovery | Observation in dashboards | Print/link in channel |
| Status page updates | Structured text | statuspage.io or equivalent |

## Restrictions

- **Severity is NOT opinion**: apply `codex-incident-response` criteria objectively.
- **No blame during incident**: factual language ("deploy X caused degradation"), never ("dev Y deployed a bug"). Blameless post-mortem starts here.
- **Comms has one owner**: Comms Lead is the only one who publishes externally; avoids contradictions.
- **Mitigation comes before complete understanding**: restore service > figure out why; debug later.

## References

- `codex-incident-response` — severity, roles, comms templates
- `lex-runbook-for-every-alert` — runbook is the basis of Step 4
- `lex-slo-required` — incident consumes error budget
- `kata-postmortem-write` — post-incident procedure
- `warrior-hestia`
