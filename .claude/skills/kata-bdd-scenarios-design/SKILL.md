---
name: kata-bdd-scenarios-design
description: "BDD Scenarios Design. Engineering — Quality. First half of Phase 8 of the Issue-Driven flow. Produces the Gherkin scenario set for an issue, blind to the implementation source code."
---

# Kata: BDD Scenarios Design

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Engineering — Quality. First half of Phase 8 of the Issue-Driven flow. Produces the Gherkin scenario set for an issue, **blind to the implementation source code**.

## Workflow

```
Progress:
- [ ] 1. Verify preconditions and directives
- [ ] 2. Declare reading guard (blind to code)
- [ ] 3. Read allowed specification sources
- [ ] 4. Build AC inventory
- [ ] 5. Derive scenarios per AC (taxonomy)
- [ ] 6. Write declarative Gherkin
- [ ] 7. Self-lint (codex-gherkin regex)
- [ ] 8. Compose 07-bdd-scenarios.md (frontmatter + Gherkin)
- [ ] 9. Handle ambiguities (Issue comment)
- [ ] 10. Persist and update checkpoint
- [ ] 11. Final validation
```

### Step 1: Verify preconditions and directives

1. Read `.ahrena/.directives` per `lex-directives`.
2. Confirm that `github` and `notion` are in `mcp.servers` per `lex-mcp`. If `notion` is missing, proceed with Issue + artifacts only (record in the frontmatter).
3. Confirm `GITHUB_PAT` and `NOTION_API_KEY` (when applicable) are set.
4. Confirm the presence of `docs/issues/issue-{n}/01-brief.md`, `02-requirements.md`, `03-architecture.md`. If any is missing, stop and report — Phase 8 requires Phases 1-3 complete.

### Step 2: Declare reading guard (blind to code)

Before any reading, internally register the forbidden source set (per `lex-bdd-spec-only-sources` Rule 2). The agent **MUST NOT** open files under:

```
src/, app/, lib/, pkg/, internal/, tests/, spec/, __tests__/,
cypress/, e2e/, playwright/, *.feature consumed by a runner,
any code extension (.py, .ts, .tsx, .js, .jsx, .java, .go, .rs)
```

If an allowed source (e.g., `03-architecture.md`) cites an implementation file, **the cited path is only a textual reference** — the agent does not open the file.

### Step 3: Read allowed specification sources

In order (per `codex-bdd` Section 2):

1. `docs/issues/issue-{n}/02-requirements.md` — numbered ACs.
2. `docs/issues/issue-{n}/01-brief.md` — context.
3. GitHub Issue via `kata-mcp-github-read` — title, body, relevant comments.
4. Referenced Notion pages via `kata-mcp-notion-read` in `page` mode at `full` depth.
5. `docs/issues/issue-{n}/03-architecture.md` — constraints and user-visible contracts.
6. ADRs in `docs/adr/` when referenced by `03-architecture.md`.

For each source opened, internally record the path/URL (will be listed in the output frontmatter).

### Step 4: Build AC inventory

1. Extract every numbered `AC-{N}` from `02-requirements.md`.
2. For each AC, identify:
   - Requirement type (positive, negative, with numeric boundary, with NFR).
   - Domain terms appearing (to preserve ubiquitous language per `codex-bdd` Section 6).
   - Inter-AC dependencies (when applicable).
3. Keep the inventory as a mental table or scratch (not persisted).

### Step 5: Derive scenarios per AC (taxonomy)

Apply the minimum coverage rule from `codex-bdd` Section 4:

| For each AC | At least |
|---|---|
| Always | 1 `@happy-path` |
| Has explicit negative requirement ("rejects when", "rejects if") | 1 `@error` |
| Has numeric/temporal boundary (limits, ranges, dates) | 1 `@edge` |
| Has alternative success path | 1 `@alternative` |
| Has observable NFR (latency, idempotency) | 1 `@nfr` |

Assign a unique `SCN-{N}` id, contiguous within the file (regenerate numbering if scenarios are removed in review).

### Step 6: Write declarative Gherkin

For each scenario:

1. Apply the structure from `codex-gherkin` Section 1 (adopted subset).
2. Use `Background` only for shared business preconditions (per `lex-bdd-gherkin-format` Rule 6).
3. Steps in third person, active voice, present tense — in domain language (per `codex-bdd` Section 6).
4. `Then` always with an **observable** outcome (not "the operation happens").
5. For ≥ 3 variations of the same triple, use `Scenario Outline` + `Examples`.
6. Apply tags: ≥ 1 `@AC-{N}` + exactly 1 type tag (per `lex-bdd-gherkin-format` Rule 4).

### Step 7: Self-lint (codex-gherkin regex)

Before saving, scan step content against the regex set in `codex-gherkin` Section 12:

```
Forbidden in any step:
- HTTP methods + path
- status codes (numeric or named)
- function/method names with parentheses
- SQL (SELECT, INSERT INTO, UPDATE)
- implementation paths (src/, app/, etc.)
- CSS/XPath selectors
- code file extensions

Required per scenario:
- @AC-\d+ (≥ 1)
- @(happy-path|alternative|edge|error|nfr) (exactly 1)
- SCN-\d+ unique within the file
```

Violation → rewrite the step in business language before continuing. Do not save the file with violations.

### Step 8: Compose 07-bdd-scenarios.md

Final file structure:

```yaml
---
issue: {n}
repo: {owner/repo}
generated_at: "{ISO-8601}"
generated_by: warrior-themis
sources:
  github_issue: "{owner/repo}#{n}"
  notion_pages:
    - "{page URL 1}"
  flow_artifacts:
    - docs/issues/issue-{n}/01-brief.md
    - docs/issues/issue-{n}/02-requirements.md
    - docs/issues/issue-{n}/03-architecture.md
ac_coverage:
  - ac: AC-1
    scenarios: [SCN-1]
  - ac: AC-2
    scenarios: [SCN-2, SCN-3]
---
```

Gherkin block below, with `# language: <lang>` when the language is not `en`.

When there are > 3 Features or > 30 scenarios, split per `codex-gherkin` Section 2 into `scenarios/*.feature` and keep `07-bdd-scenarios.md` only as index + frontmatter.

### Step 9: Handle ambiguities

If an AC does not allow writing a scenario from the sources:

1. **DO NOT** consult the code (per `lex-bdd-spec-only-sources` Rule 4).
2. List the ambiguity in an Issue comment (via `kata-mcp-github-write` if available; otherwise ask the orchestrator to do it).
3. Mark the AC in the frontmatter as blocked:

```yaml
ac_coverage:
  - ac: AC-3
    scenarios: []
    status: BLOCKED
    blockers:
      - "Need to define what happens when the customer already has an active scheduling for the same date"
```

4. Do not invent the scenario. The Issue must be amended before Gate 3 can pass.

### Step 10: Persist and update checkpoint

1. Create `docs/issues/issue-{n}/` if it doesn't exist.
2. Save `07-bdd-scenarios.md` (and `scenarios/*.feature` files when applicable).
3. Update `.ahrena/workflow/issue-{n}/checkpoint.md` with YAML front-matter (per `lex-issue-driven` Rule 7):
   - `phase_completed: 8.1`
   - `phase_next: 8.2`
   - artifact under `artifacts.bdd_scenarios`
   - `updated_at` timestamp

### Step 11: Final validation

Before returning control to the orchestrator, check:

- [ ] Frontmatter declares only allowed sources (no paths under `src/`, `tests/`, etc.).
- [ ] `ac_coverage` lists every AC from `02-requirements.md` (with `scenarios` or `status: BLOCKED`).
- [ ] Every scenario has a unique `SCN-{N}` id.
- [ ] Every scenario has ≥ 1 `@AC-{N}` and exactly 1 type tag.
- [ ] Self-lint passes on every scenario.
- [ ] Scenarios with negative requirements have `@error`; scenarios with boundaries have `@edge`.
- [ ] Gherkin block language is consistent throughout the file.
- [ ] Checkpoint updated.

## Outputs

| Output | Format | Destination |
|-------|---------|-------------|
| Consolidated scenarios | Markdown + Gherkin | `docs/issues/issue-{n}/07-bdd-scenarios.md` |
| Scenarios per Feature (optional split) | `.feature` | `docs/issues/issue-{n}/scenarios/*.feature` |
| Issue comment (when ambiguity) | GitHub comment | Issue `{repo}#{n}` |
| Updated checkpoint | Markdown YAML | `.ahrena/workflow/issue-{n}/checkpoint.md` |
| Summary to orchestrator | Structured text | Response to `warrior-themis` / `warrior-athena` |

## Constraints

- **Blind to code:** never open files under `src/`, `app/`, `lib/`, `pkg/`, `internal/`, `tests/`, `spec/`, `cypress/`, `e2e/`, etc., nor run `grep`/`find` over them (per `lex-bdd-spec-only-sources`).
- **No step-runner:** the output is documentation; do not create `step_definitions/`, `behave.ini`, etc. (per `lex-bdd-no-framework-coupling`).
- **No imperative scenarios:** no UI selectors, status codes, function/table names (per `lex-bdd-gherkin-format`).
- **No invention:** if the Issue does not allow writing the scenario, the agent blocks the AC and returns it to source; does not consult code or deduce behavior.
- **Ubiquitous language:** when the scenario touches core domain (transfer, reconciliation, ledger entry), use the domain model terms (`warrior-theseus`, Event Storm).
