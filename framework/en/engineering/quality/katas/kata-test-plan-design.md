# Kata: Design Test Plan

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Designing a test plan for a feature — distributes ACs across the right levels, defines expected coverage, identifies risks and gaps

## Objective

Given a feature with requirements (numbered ACs) and architecture (affected components), produce a **structured test plan** that maps each AC to the appropriate levels (unit, integration, E2E), identifies error and edge scenarios, and documents known gaps. The plan serves as input for Apollo/Hephaestus to implement tests with traceability, and as input for Gate 2 to validate coverage.

## When to Use

- Phase 2.5 (optional) of the Issue-Driven flow, when the feature is complex enough to benefit from an explicit plan before implementation
- Invoked by `warrior-hera` directly or delegated by `warrior-athena` on tier-1 features
- Also applicable outside the Issue-Driven flow to audit coverage of an existing feature

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Requirements (ACs) | Yes | `.ahrena/issues/{n}/02-requirements.md` or equivalent list |
| Architecture | Yes | List of affected components (phase 3 of the Issue-Driven flow) |
| Stack | Yes | Detected languages, frameworks |
| Criticality | No | Tier (1/2/3/4); default 2 |

## Workflow

```
Progress:
- [ ] 1. Map ACs to the appropriate test levels
- [ ] 2. Identify scenarios beyond the happy path
- [ ] 3. Identify boundaries and risks
- [ ] 4. Define target coverage per component
- [ ] 5. List required tools and fixtures
- [ ] 6. Persist in .ahrena/issues/{n}/02b-test-plan.md
- [ ] 7. Update checkpoint
```

### Step 1: Map ACs to levels

For each AC:

1. Identify **type of behavior**: pure logic? persistence? UI? external integration?
2. Assign primary level according to decision tree in `codex-test-strategy`:
   - Pure logic → **Unit**
   - Persistence / real integration → **Integration**
   - External contract / multi-endpoint flow → **E2E API**
   - Critical user journey → **E2E UI**
3. Decide if the AC also deserves coverage at an adjacent level (e.g.: repository AC has unit of the domain + integration of the repo).

Produce table:

| AC | Behavior | Primary level | Adjacent level | Justification |
|---|---|---|---|---|
| AC-1 | Create refund via POST /v1/refunds | Integration | E2E API | Crosses service + repository + real DB |
| AC-2 | Idempotency via Idempotency-Key | Integration | Unit (hash key) | — |
| AC-3 | Refund after 30 days returns 422 | Unit (domain) | Integration | Pure business rule + integration proves HTTP |

### Step 2: Scenarios beyond the happy path

For each AC, **mandatory** to identify:

- **Known errors**: invalid inputs, unmet preconditions
- **Edges**: limits (amount = 0, amount = maximum), concurrency (double submit)
- **Idempotency / replay**: does repeating the operation produce the same result?
- **Dependency failures**: DB down, external API 500, timeout

Extra scenarios become **additional tests** (they do not duplicate ACs, they extend them).

### Step 3: Boundaries and risks

List explicitly:

- **External boundaries** that will be mocked: which? how? contracts updated?
- **Sensitive data** in fixtures: mask/redact; never real customer data.
- **Real costs** of E2E (e.g.: Stripe sandbox generates real token → cleanup needed).
- **Estimated execution time**: sum per level; if it exceeds budget (`codex-test-strategy`), escalate to human.

### Step 4: Target coverage

By criticality:

| Tier | Minimum coverage | Mutation score | Comment |
|---|---:|---:|---|
| Tier 1 (revenue, critical security) | 90% | >70% | Investment justified |
| Tier 2 (important) | 80% | — | Default |
| Tier 3 | 70% | — | Basic coverage |
| Tier 4 (internal) | 60% | — | Only happy path + obvious errors |

Adjust `quality.coverage_threshold` in `.ahrena/.directives` if different from the default 80%.

### Step 5: Tools and fixtures

- **Tools per level**: according to `codex-test-strategy`
- **Reusable fixtures**: identify new factories needed
- **Containers**: list Docker images (Postgres, Redis, LocalStack for AWS)
- **Test data**: necessary datasets; where they live (fixtures/, seeds/)

### Step 6: Persist the plan

Structure in `.ahrena/issues/{n}/02b-test-plan.md`:

```markdown
# Test Plan — Issue #{n}: {title}

- **References:** [Requirements](./02-requirements.md) · [Architecture](./03-architecture.md)
- **Criticality (tier):** 2
- **Target coverage:** 80%

## AC → Levels Mapping

| AC | Primary level | Adjacent level | Justification |
|---|---|---|---|

## Additional scenarios

### AC-1
- Errors: negative amount, non-existent payment_id, payment already refunded
- Edges: refund equal to original value; refund 1 cent less
- Idempotency: 2x same Idempotency-Key → 1 refund
- Failures: DB timeout, event does not publish

## Mocked boundaries

- Stripe: sandbox when available, contract test vs Pact
- SNS: real in staging; moto/localstack in integration

## Required resources

- Container: `postgres:16`
- New fixtures: `RefundFactory`, `PaymentWithCaptureFactory`
- Dataset: none new (reuses global fixtures)

## Risks and gaps

- E2E UI not covered in this iteration (no refund UI for end customer yet)
- Mutation testing: run in monthly offline cycle (not in each PR CI)
```

### Step 7: Update checkpoint

Add entry in `.ahrena/workflow/issue-{n}/checkpoint.md`:

```yaml
test_plan:
  artifact: .ahrena/issues/{n}/02b-test-plan.md
  total_acs_mapped: 5
  coverage_target: 80
  tier: 2
```

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Structured test plan | Markdown | `.ahrena/issues/{n}/02b-test-plan.md` |
| AC → levels mapping | Table in the plan | — |
| Fixture/container list | Section in the plan | — |

## Restrictions

- **Does not write tests**: this kata plans; the actual writing is by Apollo/Hephaestus.
- **Plan binding for Gate 2**: if the plan defines Integration for AC-1, Gate 2 checks that an integration test exists for AC-1.
- **Tier declared explicitly**: if omitted, Gate 2 assumes tier 2 (80% coverage).
- **Fixed destination**: `.ahrena/issues/{n}/02b-test-plan.md` (following `lex-issue-driven` convention).

## References

- `lex-test-pyramid`, `lex-test-isolation`
- `codex-test-strategy`
- `warrior-hera`
- `kata-quality-gate` — consumes the plan at Gate 2
- `lex-issue-driven`
