# Lexis: SLO Required for tier-1/2 Services

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Service Level Objectives (SLO) for tier-1 and tier-2 services — defined before go-live, measured in production, respected as an internal contract

## Purpose

Without SLO, "availability" and "performance" are opinion. Customers complain when something is bad; engineering debates what "good enough" means; prioritization of reliability vs. features becomes politics. SLO makes the discussion objective: numerical contracts with customers (internal or external) about what is acceptable, error budget consumed as currency for decisions.

This Lexis exists to ensure that **every tier-1 or tier-2 service has an explicit SLO before the first deploy to production**, that **SLO is measured by observable SLIs**, and that **consumed error budget drives prioritization between reliability and feature delivery**.

## Law

> **Every tier-1 or tier-2 service MUST have a declared and agreed SLO before the first deploy to production. SLO MUST be measured by SLI based on real telemetry (metrics, logs). When the period's error budget is consumed ≥ 80%, new features MUST be paused in favor of reliability work until the budget is recovered.**

## Rules

### 1. SLO declared before go-live

Each new tier-1 or tier-2 criticality service has, in the repository:

```yaml
# docs/slo/{service}.yaml
service: refund-api
tier: 1
slos:
  - name: availability
    sli: "successful_http_requests / total_http_requests (excluding 4xx validation errors)"
    objective: 99.9%
    window: 30d
    error_budget_policy: "pause features if ≥80% consumed"
  - name: latency_p99
    sli: "http_request_duration_seconds{quantile=0.99} p99 in production"
    objective: 300ms
    window: 30d
  - name: freshness (for async processors)
    sli: "event_processing_lag_seconds"
    objective: "< 60s at p95"
    window: 7d
owners:
  - team: platform-payments
    escalation: "@payments-oncall"
```

### 2. SLI based on real telemetry

The SLI **MUST**:
- Be measurable in production via existing metric or created for it.
- Reflect user experience (users complain about 5xx and latency, not internal CPU).
- Exclude causes unrelated to the service (e.g.: 401 due to customer credential does not count against availability).

### 3. Error budget as currency

For each SLO:

- **Error budget** = 1 - SLO × window. E.g.: 99.9% in 30d → 43.2 minutes of allowed downtime.
- **Consumed in real time** via dedicated dashboard.
- **≥ 80% consumed** → pause new features for that service; prioritize reliability (chaos tests, retry reinforcement, recurring bug fixes).
- **100% consumed** = SLO violated in the period → mandatory post-mortem; may trigger rollback of recent features.

### 4. Quarterly review

SLO is not carved in stone:

- **Review quarterly** with stakeholders (product, engineering, eventually customer).
- If chronic SLO (budget consumed > 3 consecutive periods) → relax SLO or invest in structural reliability.
- If budget chronically zeroed (never consumes) → tighten SLO (customer deserves more).

### 5. Tiers

| Tier | Criterion | Typical SLO | Error budget |
|---|---|---|---|
| 1 | Direct revenue, critical security (payment, auth) | 99.9%+ | 43min/month |
| 2 | Important (operational dashboards, external integrations) | 99.5% | 3.6h/month |
| 3 | Business-hours (internal BFF, admin tools) | 99% | 7h/month |
| 4 | Internal best-effort (experimental, small internal) | optional | — |

### 6. Derived dashboards and alerts

From SLO derives:

- **SLO dashboard**: error budget graph over the period; exhaustion forecast.
- **Burn-rate alerts**: fire when budget consumes faster than linear (e.g.: 2% of the month in 1h = burn rate 14x → page on-call).
- **Imminent violation alerts**: 80% budget → warning; 100% → post-mortem.

## Applicability

- **Applies to:** every new tier-1 or tier-2 service; existing services without SLO have up to 90 days to declare after this Lexis takes effect.
- **Linked agents:** `warrior-hestia`, `warrior-atlas` (when new infra), `warrior-athena` (enforce pre-deploy).
- **Exceptions:** tier-3 and tier-4 services have optional SLO; experimental (sandbox, prototype) are out of enforcement.

## Consequences of Violation

1. **No SLO:** prioritization discussion becomes politics; reliability loses to novelty until it breaks at the customer.
2. **Fictional SLO:** attractive number but without real measurement; external audit (SOC 2, ISO) detects gap.
3. **Blown budget ignored:** team keeps delivering features while reliability degrades; customer churn grows silently.
4. **Remediation:**
   - Declare SLO in `docs/slo/{service}.yaml` with squad review.
   - Configure dashboards (Grafana, Datadog SLO, CloudWatch).
   - Establish quarterly review ceremony.

## Automated Validation

- **Tool:** simple scanner of `docs/slo/*.yaml` vs. list of declared services (can be in `infra/` or registry); alert if tier-1/2 service has no SLO.
- **Timing:** pre-deploy (go-live checklist); quarterly (review).
- **Metric:** 100% of tier-1/2 services with documented SLO; 0 tier-1 services with chronically zeroed error budget (>3 periods).

## References

- `lex-runbook-for-every-alert` — alerts link to runbooks
- `lex-observability-required` — SLI comes from telemetry
- `codex-incident-response`
- `warrior-hestia`
- [Google SRE Workbook — Implementing SLOs](https://sre.google/workbook/implementing-slos/)
