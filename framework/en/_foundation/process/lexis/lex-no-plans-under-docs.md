# Lexis: Plans Do Not Live Under `docs/`

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Canonical paths for plan files (`plan-*.md`) in Ahrena projects

## Purpose

The `docs/` directory is reserved for canonical documentation artifacts: Issue-Driven flow phases (`docs/issues/issue-{N}/`), feature design docs (`docs/{context}/{entities,oas,events,agents,metrics}/`), ADRs (`docs/adr/`), and runbooks (`docs/runbooks/`).

Execution plans (`plan-*.md`) follow the hierarchical Issue → Plan → PR model described in `lex-agent-planning`: the GitHub Plan sub-issue body is the canonical source of truth; local provider caches (`.claude/plans/` or `.cursor/plans/`) materialize the content during the session and are gitignored.

Mixing plans under `docs/` breaks that separation: it confuses project navigation, pollutes phase artifacts with operational state, and opens the door to multiple unsynchronized sources of truth. Observed violation in downstream Ahrena consumers: files like `docs/skills/{slug}/plans/plan-{M}-{slug}.md` materialized next to specs.

## Law

> **Materializing plan files (`plan-*.md`) under `docs/`, under any path that combines `docs/` with `plans/` as path segments, or in any subdirectory of `docs/` is FORBIDDEN. The canonical paths for plans are exactly three: (a) `.claude/plans/plan-{M}-{slug}.md` (Claude Code provider cache, gitignored); (b) `.cursor/plans/plan-{M}-{slug}.md` (Cursor provider cache, gitignored); (c) GitHub Plan sub-issue body (canonical, committed via GitHub API). No other path is valid.**

## Coverage

- **Applies to:** every repository that adopts the Ahrena framework, including the framework repository itself and downstream consumer projects
- **Bound agents:** every agent that materializes, moves, or proposes creating plan files — `warrior-athena`, `warrior-eunomia`, `warrior-apollo`, `warrior-hephaestus`, `warrior-claudionor`, and any plan Kata (`kata-plan-task`, `kata-load-plan-from-subissue`, `kata-flush-plan-to-subissue`, `kata-decompose-issue-into-plans`)
- **Exceptions:** None. Lexis admit no exceptions

## Prospective Applicability

This Lex applies prospectively: legacy plan files detected under `docs/` in projects that adopted Ahrena before this Lex MUST be migrated to the canonical path (sub-issue body + provider cache) in the next session that touches that plan. There is no blind retroactive block — the agent that detects the orphan plan MUST signal the migration to the human before proceeding with any other work on that plan.

```
<HARD-GATE>
Every agent MUST NOT create, move, or accept instruction to materialize
a plan file (`plan-*.md`) at any path that combines `docs/` and `plans/`
as path segments.

Mandatory preconditions to create/materialize a plan:
  (a) The path starts with `.claude/plans/` or `.cursor/plans/` (local provider cache, gitignored)
  (b) Or the destination is the GitHub Plan sub-issue body via API
  (c) No path segment contains `docs/`
  (d) No path segment contains `plans/` under `docs/`

This rule applies to EVERY Ahrena project, regardless of:
  - perceived size ("it's just one skill plan file")
  - urgency ("I need to document this now")
  - who requested ("the user asked to put it there")
  - project historical pattern ("we always did it this way")

Single declared exception: None. Legacy orphan plans under `docs/`
MUST be migrated; never normalized.
</HARD-GATE>
```

## Detection Protocol

When finding a `plan-*.md` file under `docs/` during any operation (read, search, listing), the agent MUST:

1. PAUSE the current operation
2. Signal the human: orphan file path, parent Issue (if identifiable), migration recommendation
3. Wait for human direction before touching the file (do not migrate unilaterally — the content may carry phase context or be a candidate for another document category)

## Examples

### Correct

```
.claude/plans/plan-163-codify-3-lexis-hard-gate-rules.md   # Claude provider cache (gitignored)
.cursor/plans/plan-163-codify-3-lexis-hard-gate-rules.md   # Cursor provider cache (gitignored)
GitHub Issue #163 body (canonical)                          # via lex-agent-planning
```

### Incorrect

```
docs/skills/guardia-hello/plans/plan-001-init.md           # FORBIDDEN — combines docs/ + plans/
docs/issues/issue-163/plans/plan-execution.md              # FORBIDDEN — plans/ under docs/
docs/plans/plan-163.md                                      # FORBIDDEN — plans/ under docs/
docs/{context}/plans/plan-design.md                         # FORBIDDEN — combines docs/ + plans/
```

## Automated Validation

- **Tool:** CI lint script (extension of `lint-paths.yml`) that runs `find docs/ -name 'plan-*.md' -o -path '*/plans/*'` and fails the pipeline when any match is found
- **When:** local pre-commit hook + CI on every PR + monthly audit on downstream projects
- **Metric:** 0 `plan-*.md` files under `docs/` in any Ahrena repository; 0 `docs/**/plans/**` segments in any project tree
