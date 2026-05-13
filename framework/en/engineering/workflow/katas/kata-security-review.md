# Kata: Security Review

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Phase 5 of the Issue-Driven flow — security review of the implemented code against OWASP Top 10, authentication/authorization patterns, sensitive data handling, and vulnerable dependencies

## Objective

Perform a security review on the code implemented in Phase 4, identifying known vulnerabilities (OWASP Top 10), authentication/authorization issues, sensitive data exposure, credentials in code, and dependencies with known CVEs. Produces a report under `.ahrena/issues/{n}/05-security-review.md` with classified severity; critical findings block Gate 2.

## When to Use

- Phase 5 of the flow orchestrated by `warrior-athena`, after Apollo (or an equivalent warrior) completes the implementation in Phase 4
- Whenever code changes need to be audited for security risks before creating the PR

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Implementation diff | Yes | `git diff` between the working branch and the base branch |
| Phase 2 requirements | Yes | `.ahrena/issues/{n}/02-requirements.md` |
| Phase 3 architecture | Yes | `.ahrena/issues/{n}/03-architecture.md` (includes external integrations) |

## Workflow

```
Progress:
- [ ] 1. Collect diff and context
- [ ] 2. OWASP Top 10 check
- [ ] 3. Authentication and authorization
- [ ] 4. Sensitive data and credentials
- [ ] 5. Dependencies (CVE scan)
- [ ] 6. Consolidate report with severity
- [ ] 7. Persist to .ahrena/issues/{n}/05-security-review.md
- [ ] 8. Update checkpoint
```

### Step 1: Collect diff and context

1. Run `git diff {base-branch}...HEAD` or equivalent.
2. Read `03-architecture.md` to understand involved external integrations.
3. Read `02-requirements.md` to identify ACs with security implications (e.g., authentication, authorization, sensitive data).

### Step 2: OWASP Top 10 check

For each category, explicitly verify in the diff:

| Category | Verification |
|---|---|
| **A01 — Broken Access Control** | Do new endpoints have authorization checks (RBAC, ABAC)? Ownership check where applicable? |
| **A02 — Cryptographic Failures** | Are sensitive data in transit/at rest encrypted? Correct algorithm usage (no MD5/SHA1)? |
| **A03 — Injection** | Parameterized SQL queries? Inputs validated before use in commands/queries? |
| **A04 — Insecure Design** | Insecure patterns (e.g., predictable tokens, excessive timeouts)? |
| **A05 — Security Misconfiguration** | Security headers configured? Debug mode disabled? |
| **A06 — Vulnerable Components** | (see Step 5) |
| **A07 — Identification & Auth Failures** | Rate limiting on auth endpoints? Brute-force protection? Correct session management? |
| **A08 — Software & Data Integrity Failures** | Signatures verified? Safe deserialization? |
| **A09 — Security Logging Failures** | Are relevant events (auth, sensitive data access) logged? Do logs contain sensitive data? |
| **A10 — SSRF** | Are input URLs validated against an allowlist? |

Record each finding with: OWASP category, file/line, severity (`critical`/`high`/`medium`/`low`), recommendation.

### Step 3: Authentication and authorization

If the issue involves HTTP endpoints:

1. Does each new endpoint have auth verification? (bearer token, OAuth2, etc.)
2. Does each operation have permission checks (RBAC)?
3. Ownership check: can the user only operate on resources they own?
4. Does information in tokens not leak sensitive data?

If involves event consumption/publication:

1. Do high-privilege events require signing/verification?
2. Do events contain only IDs and not sensitive data in the payload?

### Step 4: Sensitive data and credentials

1. Scan for credential patterns in the diff: `password`, `secret`, `api_key`, `token`, strings that look like keys.
2. Check `.env`, `.env.example`: only placeholders, never actual values.
3. Sensitive data (national IDs, email, card numbers) in logs? Must be masked/redacted.
4. Sensitive data in error messages returned to the client? Must not leak.
5. Sensitive data in API responses that the client does not need? Remove.

### Step 5: Dependencies (CVE scan)

1. If there were changes in dependency files (`pyproject.toml`, `requirements.txt`, `package.json`, `Cargo.toml`, etc.), run a scan:
   - Python: `pip-audit` or `safety check`
   - Node: `yarn audit` or `npm audit`
   - Rust: `cargo audit`
2. Classify found CVEs by severity (CVSS).
3. Critical CVEs (CVSS ≥ 9.0) in dependencies used by the touched code → critical severity in the report.

### Step 6: Consolidate report with severity

Consolidate all findings into a prioritized list:

- **Critical** — block Gate 2; must be resolved before reopening.
- **High** — must be resolved before merging the PR.
- **Medium** — record as PR TODOs; may be resolved in a future iteration.
- **Low** — informational note.

If **zero critical or high findings**, report `approved` to proceed to Gate 2.

### Step 7: Persist to `.ahrena/issues/{n}/05-security-review.md`

Structure:

```markdown
# Security Review — Issue #{n}: {title}

- **Reference:** [Architecture](./03-architecture.md)
- **Date:** {YYYY-MM-DD}
- **Overall result:** {approved | changes-required | blocked}

## Summary

- Critical: {n}
- High: {m}
- Medium: {k}
- Low: {j}

## Critical Findings

### S-1: {title}
- **Category:** OWASP A{nn} — {name}
- **Location:** `{file}:{line}`
- **Description:** {what is there}
- **Recommendation:** {how to fix}

## High Findings

### S-2: ...

## Medium Findings

### S-3: ...

## Low / Informational Findings

### S-4: ...

## Dependencies

| Package | Version | CVE | Severity | Recommendation |
|---|---|---|---|---|
| ... | ... | CVE-XXXX-YYYY | {critical/high/...} | {upgrade to X} |

## Conclusion

{1-2 paragraphs: final status, what must be resolved before Gate 2}
```

### Step 8: Update checkpoint

1. Update `.ahrena/workflow/issue-{n}/checkpoint.md`:
   - completed phase: 5
   - next: 6 (Gate 2)
   - result: `approved`, `changes-required`, or `blocked`
   - number of findings per severity
2. Inform `warrior-athena`:
   - If `approved`: proceed to Phase 6
   - If `changes-required` or `blocked`: return to Phase 4 with the report

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Security report | Markdown | `.ahrena/issues/{n}/05-security-review.md` |
| Result | `approved` / `changes-required` / `blocked` | Return to orchestrator |
| Updated checkpoint | Markdown | `.ahrena/workflow/issue-{n}/checkpoint.md` |

## Restrictions

- **Do not modify code:** this kata is review-only; fixes are applied by Phase 4 in a new iteration.
- **Severity is blocking:** critical findings always block Gate 2; there is no automatic override.
- **Scope limited to the diff:** do not review pre-existing code not touched by the diff (that would be a separate audit task).
- **No silent false positives:** if a finding is a false positive after analysis, record it explicitly in the report with justification, do not omit.
- **Fixed destination:** `.ahrena/issues/{n}/05-security-review.md` (per `lex-issue-driven`).

## References

- `lex-issue-driven` — laws of the flow
- `codex-issue-workflow` — this kata's position in the flow
- `lex-python-security` — security rules for Python code
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
