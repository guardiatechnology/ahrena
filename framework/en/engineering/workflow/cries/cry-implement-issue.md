# Cry: Implement Issue (Issue-Driven Development)

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Entry point for the Issue-Driven Development flow — invokes `warrior-athena` to drive the GitHub issue through the 7 phases until PR creation

## Description

This command triggers the full issue-driven development flow: from reading the issue on GitHub to creating the reviewable PR, passing through requirements, architecture, Gate 1 (scope), (delegated) implementation, security, Gate 2 (quality), and PR preparation. The orchestrator is **Warrior Athena**, who coordinates all Katas in the `engineering/workflow/` clade and delegates to specialists (Apollo, Daedalus, Kronos) when appropriate.

## Usage

```
/cry-implement-issue <issue-number> [<owner>/<repo>]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `issue-number` | Yes | GitHub issue number | `42` |
| `<owner>/<repo>` | No | Target repository; default: current repo (via git remote) | `guardiafinance/ahrena` |

## Prerequisites

- `github` listed in `mcp.servers` in `.ahrena/.directives`
- `notion` listed in `mcp.servers` (optional — enriches with Notion context when available)
- Environment variables: `GITHUB_PAT` (required) and `NOTION_API_KEY` (optional)
- Existing issue in the indicated repository

## What the Command Does

Invokes **warrior-athena** to drive the 7 phases of the flow:

1. **Phase 1 — Issue Analysis** (`kata-issue-analysis`): reads the issue on GitHub and fetches context from Notion → `.ahrena/issues/{n}/01-brief.md`
2. **Phase 2 — Requirements** (`kata-requirements-brief`): elicits numbered ACs with a PO perspective → `.ahrena/issues/{n}/02-requirements.md`
3. **Phase 3 — Architecture** (`kata-architecture-brief`): maps components, delegates API/event design to Daedalus/Kronos when applicable, invokes `kata-adr-write` for relevant decisions → `.ahrena/issues/{n}/03-architecture.md` + ADRs in `docs/adr/`
4. **Gate 1 — Scope Approval:** Athena presents artifacts to the human and awaits explicit approval
5. **Phase 4 — Implementation:** Athena delegates to `warrior-apollo` (or the stack warrior) via `kata-python-implement`; tests mark `AC-N` for traceability
6. **Phase 5 — Security Review** (`kata-security-review`): OWASP + CVE scan → `.ahrena/issues/{n}/05-security-review.md`
7. **Phase 6 — Gate 2 Quality** (`kata-quality-gate`): 6 checks (AC↔test traceability, scope creep, best practices, tests, coverage, types) → `.ahrena/issues/{n}/06-quality-report.md`; `no-go` returns to Phase 4
8. **Phase 7 — Prepare PR** (`kata-pr-prepare`): creates branch + push + PR via GitHub MCP; transitions ADRs `proposed → accepted`

## Prompt Template

```
Context:
- Issue: #{{issue-number}}
- Repository: {{<owner>/<repo>}} (or detected via git remote)

Task:
Act as **warrior-athena** and drive the complete Issue-Driven Development flow for issue #{{issue-number}}.

Execute the 7 phases in strict order per `codex-issue-workflow`:

1. **Phase 1:** kata-issue-analysis — read the issue via GitHub MCP and fetch context via Notion MCP; produce the brief at .ahrena/issues/{n}/01-brief.md.

2. **Phase 2:** kata-requirements-brief — elicit numbered acceptance criteria (AC-1, AC-2, ...); ask the user clarifying questions if needed; produce 02-requirements.md.

3. **Phase 3:** kata-architecture-brief — map affected components; delegate to warrior-daedalus (API) or warrior-kronos (events) when applicable; invoke kata-adr-write for relevant architectural decisions; produce 03-architecture.md + ADRs in docs/adr/.

4. **Gate 1:** Present brief + ACs + architecture + proposed ADRs to the user and **await explicit approval** before proceeding.

5. **Phase 4:** Delegate to warrior-apollo (or equivalent) for implementation. Each test must reference `AC-N` per the convention in codex-issue-workflow.

6. **Phase 5:** kata-security-review — review the diff against OWASP Top 10 and CVE scan.

7. **Phase 6:** kata-quality-gate — run the 6 checks. `no-go` returns to Phase 4; `go` advances.

8. **Phase 7:** kata-pr-prepare — create branch, push files, and PR via GitHub MCP; transition ADRs proposed → accepted; deliver the PR URL.

Strictly respect lex-issue-driven: no skipping gates, with AC↔test traceability, ADRs for relevant decisions, documentation in docs/.
```

## Invocation Example

**Input:**

```
/cry-implement-issue 42 guardiafinance/ahrena
```

**Expected output (sequential flow with human pauses):**

- Athena reads issue #42, produces `.ahrena/issues/42/01-brief.md`
- Athena asks the user clarifying questions (if needed)
- Athena produces `02-requirements.md` with 5 ACs
- Athena produces `03-architecture.md` + creates `docs/adr/-*.md`
- **Gate 1:** Athena presents a summary; user approves
- Apollo implements; each test marks the corresponding AC
- `kata-security-review` approves (0 critical findings)
- `kata-quality-gate`: 6 checks ✅ → `go`
- Athena creates the PR and reports the URL: `https://github.com/guardiafinance/ahrena/pull/123`

## Restrictions

- **Gate 1 is inviolable:** the command does not advance to implementation without explicit human approval
- **Gate 2 is inviolable:** the command does not create a PR if Gate 2 resulted in `no-go`
- **Only existing issues:** the command refuses if the issue does not exist or is empty (per `lex-issue-driven`)
- **Documentation in `docs/`:** all public flow artifacts go to `.ahrena/issues/{n}/` and `docs/adr/`
- **The command orchestrates, does not implement:** the command itself does not write code or contracts — it delegates to Katas and specialist warriors

## Associated Cries and Warriors

- **warrior-athena** — Orchestrator, invoked by this Cry
- **warrior-apollo** — Delegated in Phase 4 for Python implementation
- **warrior-daedalus** — Delegated in Phase 3 for API design
- **warrior-kronos** — Delegated in Phase 3 for event design
- **cry-api-design**, **cry-event-storm**, **cry-python-implement** — Related cries (isolated flows; this Cry orchestrates them into a unified flow starting from the issue)

## References

- `warrior-athena` — flow orchestrator
- `lex-issue-driven` — unbreakable laws
- `codex-issue-workflow` — full flow structure
- `engineering/workflow/README.md` — narrative guide for humans
