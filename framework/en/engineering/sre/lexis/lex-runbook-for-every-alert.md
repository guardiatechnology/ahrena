# Lexis: Every Alert Has a Runbook

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Monitoring alerts that trigger humans (page, on-call Slack) — each needs a linked runbook

## Purpose

Alerts without runbooks are operational cruelty: they wake engineers at 3 AM with no indication of what to do. On-call spends time figuring out what the alert means, where to see dashboards, which mitigation steps to apply — time in which the incident worsens. Worse: recurring alerts without runbooks normalize "ignore alert until it really breaks", destroying the value of the monitoring system.

This Lexis exists to ensure that **every alert that triggers a human has a versioned and linked runbook**, that **runbooks have actionable steps**, and that **alerts without runbooks are silenced or removed until they have one**.

## Law

> **Every alert that triggers a human (page, on-call) MUST have a versioned runbook in `docs/runbooks/{service}-{alert-name}.md`, linked directly in the alert annotation. The runbook MUST contain: symptoms, user impact, initial diagnosis (dashboards and queries), mitigation actions, escalation steps. Alerts without runbooks MUST be silenced or removed.**

## Rules

### 1. Minimum runbook structure

```markdown
# Runbook: {service} — {alert-name}

- **Severity:** P1 | P2 | P3
- **Owner:** team-{name} (on-call: @handle)
- **Last reviewed:** YYYY-MM-DD

## Symptoms (what the alert indicates)

{objective description: metric, threshold, duration}

## User impact

{who feels the problem, what they cannot do}

## Diagnosis

1. Dashboard: {link}
2. Logs: `{query or link to log aggregator}`
3. Traces: {link to APM/tracing for service}
4. Common hypotheses in order of prevalence:
   - Hypothesis A: cause → typical signal
   - Hypothesis B: cause → typical signal

## Mitigation

### Quick mitigation (rollback, feature flag)
1. Step 1
2. Step 2

### Deep mitigation (real fix)
1. Identify root cause
2. Fix and deploy
3. Verify recovery in dashboards

## Escalation

If mitigation does not resolve in 15 min:
- Trigger @team-escalation-list
- Open incident sev-X per `codex-incident-response`

## History (last 3 related incidents)

- {link 1}
- {link 2}
- {link 3}
```

### 2. Mandatory link in alert config

Every alert config (Prometheus, CloudWatch, Datadog) **MUST** have annotation:

```yaml
annotations:
  runbook_url: "https://github.com/guardiatechnology/{repo}/blob/main/docs/runbooks/refund-api-p99-breach.md"
  summary: "refund-api p99 > 300ms for 5 min"
```

### 3. Runbook reviewed quarterly

Each runbook has `Last reviewed: YYYY-MM-DD`:
- If > 6 months without review → warning in CI/dashboard.
- Minimum review: confirm links still work, hypotheses still relevant, correct owners.
- Related incident → runbook **MUST** be updated in the post-mortem.

### 4. Alert without runbook = silence or remove

New alert created without paired runbook:
- Blocked in the alert config PR (lint rule).
- Existing alerts without runbook: listed monthly in report; fix in 30 days or silence.

Silencing is not a permanent solution. Silenced for >60 days → remove.

### 5. No alerts that nobody understands

Golden rule: **on-call should be able to act with the runbook even without deep familiarity with the service**. Runbook written for "you in 6 months" or "the new on-call".

If the runbook requires exclusive tribal knowledge, it is incomplete.

## Applicability

- **Applies to:** every alert that pages/notifies a human in any channel (PagerDuty, Opsgenie, on-call Slack).
- **Linked agents:** `warrior-hestia` (ownership), `warrior-atlas` (when configuring alarms via IaC).
- **Exceptions:** informational alerts (dashboard only, without active notification) are outside scope — but documentation is still recommended.

## Consequences of Violation

1. **Resolution time inflates:** on-call spends 30min figuring out what the alert means before acting.
2. **Alert fatigue:** recurring alerts without runbook become noise; real emergency loses urgency.
3. **Compliance failure:** SOC 2 CC7.3 audit requires incident response procedures; without runbook, it fails.
4. **Remediation:**
   - Inventory of existing alerts; each receives a runbook ticket in 30 days.
   - Critical (P1) alerts without runbook: silence until documented.
   - CI lint blocks merge of alert config without `runbook_url`.

## Automated Validation

- **Tool:**
  - Lint on alert config files (Prometheus rules, Terraform CloudWatch): require `annotations.runbook_url`.
  - Cronjob checks that URL in `runbook_url` exists (not 404).
  - Dashboard: active alerts vs. existing runbooks → gap report.
- **Timing:** on each PR that adds/modifies alert; weekly (URL health).
- **Metric:** 100% of active alerts with valid `runbook_url`; 0 alerts silenced for > 60 days without deletion.

## References

- `lex-slo-required` — burn-rate alerts derived from SLO need runbook as well
- `lex-observability-required`
- `codex-incident-response` — larger procedures; runbook is the initial step
- `warrior-hestia`
- [Google SRE Book — Effective Alerting](https://sre.google/sre-book/monitoring-distributed-systems/)
