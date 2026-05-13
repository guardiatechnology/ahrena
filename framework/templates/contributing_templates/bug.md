# Bug

Use this template to report a defect: code, behavior, or documentation that does not match the declared specification.

## Why (impact)

Who is affected and what is the consequence? Link to incident, customer report, or failing test if applicable.

<!-- placeholder: e.g. Payment confirmation emails dropped for ~2% of orders since 2026-05-09; customers re-submit payment thinking it failed. -->

## What (observable defect)

Describe what is happening vs. what should happen. Include exact error messages, log lines, or screenshots.

<!-- placeholder:
Expected: 200 OK with confirmation_id in response.
Actual: 500 Internal Server Error; log line "NoneType has no attribute 'send'".
-->

Expected behavior:

Actual behavior:

## How (reproduction + verification path)

Minimum steps to reproduce; environment (prod/staging/local); commit SHA if known; how a fix will be verified.

<!-- placeholder:
Steps to reproduce:
1. POST /v1/payments with valid body
2. Wait 2s
3. Observe 500

Environment: production, commit abc1234, region us-east-1
Verification: integration test in tests/payments/test_confirmation_email.py
-->

Steps to reproduce:
1.
2.
3.

Environment:

Verification:

## Severity

Select one:
- **blocker** — blocks release, no workaround
- **critical** — broken core flow, workaround exists but painful
- **major** — broken non-core flow or degraded UX
- **minor** — visual/typo/edge case

## Additional Context

Screenshots, links, related issues, logs, or any other relevant context (optional).

---

> To track progress, follow this issue on GitHub.
