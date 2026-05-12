# Kata: Define PoV Scope

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Engineering — Agents (pre-operational stage): delimits the scope of an agent PoV before any instrumentation or implementation

## Objective

Produce, under `docs/{context}/agents-pov/{agent}/`, two canonical artifacts — `pov.md` (PoV overview) and `scope.md` (stabilized scope, cited by DoOC item d in `codex-agent-design-docs`) — with a **very narrow** scope (1 primary use case), an explicit discontinuation criterion ("if in N weeks the value metric does not reach X, terminate"), and an explicit `stage: pre-operational` declaration. Apply Directive 05 of `lex-agent-construction-directives` (Restricted Scope) in PoV context: narrow domain + fast feedback = steep learning curve. Without these two files, no other kata in the PoV cycle can run.

## When to Use

- When `cry-pov --context <name> --agent <slug> --kind <skill|subagent|plugin> --problem <description> --value-metric <description>` is invoked
- When `warrior-claudionor` needs to formalize scope before delegating implementation
- When an existing PoV lost focus and requires re-scoping (kata re-execution)

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| `--context <name>` | Yes | Bounded context in kebab-case (e.g., `reconciliation`, `fiscal-classification`) |
| `--agent <slug>` | Yes | PoV slug in kebab-case (e.g., `rec-pov-classifier`). Defines the subdir `docs/{context}/agents-pov/{agent}/`. When omitted in `cry-pov`, derived from `{context}-pov` |
| `--problem <description>` | Yes | Customer problem in 1 sentence. No generalities ("automate stuff") |
| `--value-metric <description>` | Yes | Leading metric to move, with window and threshold |
| `--kind <skill\|subagent\|plugin>` | Yes | Which Anthropic artifact to spawn |
| `--out-of-scope` | No | Explicit list of what is out; if absent, derived from the problem |
| `--discontinuation-criterion` | No | Overrides the default (4 weeks, value < 50% of declared target) |

## Workflow

```
Progress:
- [ ] 1. Validate inputs and resolve paths (including {agent})
- [ ] 2. Write "Customer problem" block
- [ ] 3. Define primary use case and what is out
- [ ] 4. Declare persona + explicit stage
- [ ] 5. Define discontinuation criterion
- [ ] 6. Write pov.md and scope.md and validate
```

### Step 1: Validate inputs and resolve paths

1. Confirm `--context`, `--agent`, `--problem`, `--value-metric`, and `--kind` are populated. Without any of them, abort with a clear message.
2. Resolve `docs/{context}/agents-pov/{agent}/` from the provided `{context}` and `{agent}`. If the directory already exists with a `pov.md` or `scope.md`, alert the user and require confirmation (`--force`) — overwriting an existing PoV is a conscious decision.
3. Create the directory if it does not exist.

### Step 2: Write "Customer problem" block

1. Quote the literal customer problem (from `--problem`), without rewording.
2. Add 2-3 sentences of business context (who suffers, where it appears, what the current workaround is). If the user did not provide this, ask.
3. The result becomes the first section of `pov.md`.

### Step 3: Define primary use case and what is out

1. Identify **1 primary use case** — the one that, if solved, is enough to prove value. Multiple cases = scope is too broad; re-scope until one remains.
2. List what is **out** (minimum 3 items). If `--out-of-scope` was passed, expand it; otherwise derive from the problem.
3. Signal explicitly in `pov.md` and in `scope.md` each use case **not** addressed by this PoV (future references go to another PoV or to Mêtis).

### Step 4: Declare persona + explicit stage

1. Define the PoV persona in 1 sentence (e.g., "Assistant that suggests accounting entries for automatic bank statement reconciliation").
2. **Declare `stage: pre-operational` literally in the persona block** — precondition for DoOC item 9 (`lex-agent-construction-directives`). Without this line, the kata aborts.

### Step 5: Define discontinuation criterion

1. Default: "If in 4 weeks the measured value is < 50% of the threshold declared in `--value-metric`, the PoV is terminated and the learning is archived in `value-proof.md`."
2. If `--discontinuation-criterion` was passed, use the user value as long as it contains: time window, metric, threshold.
3. The result becomes the "Discontinuation criterion" section of `pov.md` (and is referenced by `scope.md`).

### Step 6: Write pov.md and scope.md and validate

The two files are complementary and separated by intent:

- **`pov.md`** — overview consumed by humans and by `cry-agent-design --from-pov` (Mêtis). Sections: Customer problem, Primary use case, Out of scope, Persona, Stage, Leading value metric (literal copy of `--problem` and `--value-metric`), Discontinuation criterion, Next steps.
- **`scope.md`** — **stabilized** scope consumed by DoOC item d (codex-agent-design-docs § 14, "Evidence: SHA of the commit on `docs/{context}/agents-pov/{agent}/scope.md` + date ≥ 2 weeks ago"). Sections: Primary use case (literal copy of `pov.md`), Out of scope (literal copy), Stage (`stage: pre-operational`), Stabilization notes (PoV start date; who confirms stabilization). Does not duplicate the customer problem or the value metric — references `pov.md`.

Concrete steps:

1. Generate `docs/{context}/agents-pov/{agent}/pov.md` with the 8 sections listed above.
2. Generate `docs/{context}/agents-pov/{agent}/scope.md` with the 4 sections listed above. The physical separation between `pov.md` and `scope.md` is what allows Mêtis to compute the SHA of `scope.md` independently from `pov.md` for DoOC item d.
3. Next steps in `pov.md` always list the 6 remaining katas to execute: `kata-pov-system-prompt`, `kata-pov-tools-select`, `kata-pov-context-curate`, `kata-pov-observability-instrument`, `kata-pov-feedback-attach`, `kata-pov-value-track`.
4. Apply `kata-artifact-self-review` to both files before delivery.

### Final Validation

- [ ] `pov.md` exists in `docs/{context}/agents-pov/{agent}/`
- [ ] `scope.md` exists in `docs/{context}/agents-pov/{agent}/`
- [ ] Both contain `stage: pre-operational` literally in the persona / stage block
- [ ] Primary use case is exactly 1 and identical across both files
- [ ] Discontinuation criterion has window + metric + threshold in `pov.md`
- [ ] `scope.md` explicitly cites the PoV start date (input to the 2-week window required by DoOC item d)
- [ ] Next steps list the 6 remaining POV katas in `pov.md`

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| `pov.md` | Markdown | `docs/{context}/agents-pov/{agent}/pov.md` |
| `scope.md` | Markdown | `docs/{context}/agents-pov/{agent}/scope.md` |

## Execution Example

### Input

```
cry-pov --context reconciliation \
        --agent rec-pov-classifier \
        --kind skill \
        --problem "Accounting team spends 3h/day reconciling bank statements with ERP entries" \
        --value-metric "% automatic reconciliation ≥ 60% in 4 weeks"
```

### Output (excerpts)

**`docs/reconciliation/agents-pov/rec-pov-classifier/pov.md`** (excerpt):

```markdown
# PoV — reconciliation / rec-pov-classifier

## Customer problem

Accounting team spends 3h/day reconciling bank statements with ERP entries.
They currently do it manually in spreadsheets; errors produce duplicate entries.

## Primary use case

Given a bank statement and the list of ERP entries from the same window,
suggest the most likely pairing by value + date + similar description.

## Out of scope

- Automatic entry creation in the ERP (suggestion only)
- Cross-account reconciliation
- Fraud detection

## Persona

Assistant that suggests bank-statement-to-ledger-entry pairings.
**stage: pre-operational**

## Leading value metric

% automatic reconciliation ≥ 60% in 4 weeks (measured in a real sandbox).

## Discontinuation criterion

If in 4 weeks the measured value is < 30% (50% of the threshold), the PoV
is terminated; learning archived in value-proof.md.

## Next steps

1. kata-pov-system-prompt
2. kata-pov-tools-select
3. kata-pov-context-curate
4. kata-pov-observability-instrument
5. kata-pov-feedback-attach
6. kata-pov-value-track
```

**`docs/reconciliation/agents-pov/rec-pov-classifier/scope.md`** (excerpt):

```markdown
# Scope — reconciliation / rec-pov-classifier

> Stabilized scope document. Consumed by DoOC item d (codex-agent-design-docs).

## Primary use case

Given a bank statement and the list of ERP entries from the same window,
suggest the most likely pairing by value + date + similar description.

## Out of scope

- Automatic entry creation in the ERP (suggestion only)
- Cross-account reconciliation
- Fraud detection

## Stage

stage: pre-operational

## Stabilization notes

- PoV started on: {ISO date of creation}
- Stabilization confirmer: {responsible; filled by `kata-pov-value-track` when scope has been frozen for ≥ 14 days}
- Cross-reference: see `pov.md` for the customer problem, value metric, and discontinuation criterion.
```

## Restrictions

- **Never** a scope with more than 1 primary use case. If the customer problem covers more, split into multiple PoVs.
- **Never** a PoV without a discontinuation criterion — zombie is a declared risk in plan-031.
- **Never** a persona without `stage: pre-operational` declared — blocks DoOC item 9.
- **Never** produce only `pov.md` without `scope.md` (or vice versa); both are part of the DoOC contract.
- The kata **does not** delegate to Hephaestus or Apollo; it is 100% scoping work, before implementation.

---

**Model:** This Kata applies Directive 05 (`lex-agent-construction-directives`) to the PoV cycle. Focus on narrow + exit criterion avoids zombies. The `pov.md` + `scope.md` pair is the canonical contract declared in `codex-agent-design-docs` § 14. Consumed by `warrior-claudionor` as the first step of `cry-pov`.
