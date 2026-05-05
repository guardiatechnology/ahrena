---
paths:
  - "**/*.py"
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.go"
  - "**/api/**"
  - "**/handlers/**"
  - "**/jobs/**"
  - "**/consumers/**"
---

# Lexis: Observability Is Mandatory

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Every new HTTP endpoint, event consumer, background job, or long-running process across any stack

## Law

> **Every new HTTP endpoint, event consumer, scheduled job, or long-running worker MUST emit a distributed trace (span), at least one latency metric, and structured logs with a correlation ID on success and failure paths. Services communicating over HTTP or event buses MUST propagate the correlation ID (W3C Trace Context or equivalent). Logs MUST NOT contain sensitive data (PII, secrets, full card numbers).**

## Rules

### 1. Three signals per new runtime surface

For each new endpoint, consumer, or job, the agent **MUST** wire:

1. **Trace:** a span wrapping the unit of work, with attributes (entity id, operation name, outcome).
2. **Metric:** at minimum, a latency histogram; counters for errors/retries when applicable.
3. **Log:** structured (JSON) with `correlation_id`, `entity_type`, `entity_id`, `operation`, `outcome`.

Preferred stack-neutral foundation: **OpenTelemetry SDK** (OTLP exporter); platform-specific fallbacks (CloudWatch EMF, Datadog APM) acceptable when OTel is unavailable in the environment.

### 2. Correlation ID propagation

The agent **MUST**:

1. Accept `traceparent` header (W3C Trace Context) on inbound HTTP; generate if absent.
2. Propagate that trace context outbound (other HTTP calls, event publishes) via `traceparent` header or event envelope metadata.
3. Include `correlation_id` (lowercase trace id) in every log line produced during the unit of work.

### 3. Sensitive data in logs

The agent **MUST NOT** log:

- Full credit card numbers, CVVs, PINs.
- Passwords, API tokens, session cookies.
- Full national IDs (CPF, SSN) — mask or hash (last 4 digits acceptable when auditable identifier needed).
- Email bodies or message content when user data is non-essential for debugging.

Logging libraries SHOULD apply redaction filters; agents MUST review generated log statements for leak.

### 4. Error paths are observed too

The agent **MUST** ensure:

1. Unhandled exceptions bubble up in the trace as error status + recorded exception.
2. Expected error outcomes (validation failures, known business errors) emit counters and are logged at `WARN` level with `outcome=error` and error code.
3. `except: ...` blocks that swallow errors without at minimum a log + metric are forbidden (reinforces `lex-python-error-handling`).

### 5. Gate 2 enforcement

`kata-quality-gate` Check 3 **MUST** verify instrumentation is present for each new runtime surface declared in Phase 3's component table. Heuristic (stack-dependent):

- Python: look for `@trace`, `tracer.start_as_current_span`, `metric.observe`, structured logger usage.
- Frontend (server routes): look for tracing middleware, `sendBeacon`/APM SDK initialization.
- Infrastructure: X-Ray / OTel integration configured where services run.

Absence = ❌ `Check 3 — lex-observability-required`.

## Applicability

- **Applies to:** every `docs/issues/issue-{n}/03-architecture.md` component listed as new endpoint/consumer/job.
- **Bound agents:** all warriors that implement runtime code (Apollo, Hephaestus, Hera when executing tests, etc.); verified by `warrior-athena` at Gate 2.
- **Exceptions:** None. Lexis admit no exceptions.

## Automated Validation

- **Tool:**
  - Lint rule / static analysis scanning for instrumentation calls on declared new surfaces.
  - Synthetic request in staging — verify trace appears in the tracing backend.
  - Log redaction checks (regex for credential patterns in sampled log lines).
- **Timing:** Gate 2 (pre-PR); continuous in production via log/metric pipelines.
- **Metric:** 100% of new endpoints/consumers with span + metric + structured log; 0 sensitive data leak events.
