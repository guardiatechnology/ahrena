---
name: kata-safe-refactoring
description: "Safe Refactoring. Improve internal design without changing observable behavior"
---

# Kata: Safe Refactoring

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Improve internal design without changing observable behavior

## Workflow

```
Progress:
- [ ] 1. Bound behavior and risk
- [ ] 2. Establish baseline and protection
- [ ] 3. Choose the smallest transformation
- [ ] 4. Execute reversible steps
- [ ] 5. Validate behavior and operations
- [ ] 6. Final validation
```

### Step 1: Bound Behavior and Risk

Describe observable behavior, consumers, invariants, contracts, and failure modes. Classify each statement as confirmed, hypothesis, or proposed decision.

### Step 2: Establish Baseline and Protection

Run existing tests and static analysis. Add characterization at the cheapest level that captures the risk when protection is missing. Measure performance only when it motivates the work.

### Step 3: Choose the Smallest Transformation

Consult `codex-code-design` and, for domain work, `codex-domain-driven-design`. Record the problem, choice, **when not to use it**, trade-offs, and reversal criterion.

### Step 4: Execute Reversible Steps

Separate structural from behavior changes, preserve interfaces, and run focused checks after each step. Do not expand into adjacent cleanup.

### Step 5: Validate Behavior and Operations

Rerun the baseline and applicable integration/contract tests. Check logs, metrics, migrations, concurrency, and security when touched.

### Step 6: Final Validation

- [ ] Observable behavior and contracts are preserved
- [ ] The original smell is smaller rather than relocated
- [ ] The abstraction has evidence and a removal criterion
- [ ] `lex-clean-code`, `lex-dry`, and stack Lexis pass
- [ ] Residual risks and executed checks are in the handoff

## Outputs

| Output | Format | Destination |
|---|---|---|
| Refactored code | Stack code | Original files |
| Behavior protection | Tests | Appropriate suite |
| Decision record | Summary/ADR when needed | Handoff or canonical project path |

## Execution Example

`PaymentService` mixes authorization rules, gateway calls, and retry. Characterization tests preserve responses and idempotency; the variable policy becomes a Strategy; retry remains in the adapter; no Factory is added because construction is simple.

## Constraints

- Do not call behavior, contract, or schema changes refactoring.
- Do not apply a pattern solely to satisfy a metric.
- Do not remove telemetry or failure handling during reorganization.
