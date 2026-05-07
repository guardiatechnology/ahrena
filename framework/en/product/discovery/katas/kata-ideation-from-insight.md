# Kata: Promotion of an Approved Insight to an Idea

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Product Discovery — promotion of an insight with `status: approved` into an Idea under `docs/discovery/{topic}/ideas/`

## Objective

Standardize how `warrior-phanes` reads an approved insight and produces an Idea in the canonical schema (`problem`, `hypothesis`, `target_user`, `success_metric`, `effort_estimate`, `linked_insights[]`), updating the source insight to `status: promoted` with `idea_ref` pointing to the created Idea. The operation is governed by HARD-GATE 1 of `lex-discovery-flow` — any unmet precondition blocks the promotion.

## When to Use

- When `cry-ideation` is invoked with the `insight_path` of an insight whose `status` is `approved`
- When the user explicitly requests `warrior-phanes` to promote one or more approved insights into an Idea (when multiple insights share the same problem, they MAY be combined into a single Idea via `linked_insights[]`)

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| `insight_path` | Yes | Canonical path of the insight to promote. May be a string or an array (when multiple insights form a single Idea) |
| `language` | No | Overrides `language.default` from `.directives` (default: pt-BR) |
| `additional_context` | No | Extra context provided by the human (e.g., telemetry data, refined hypothesis) that helps assemble `success_metric` or `effort_estimate` |

## Workflow

```
Progress:
- [ ] 1. Input preflight validation (HG1 a, d)
- [ ] 2. Read source insights
- [ ] 3. Synthesize the 5 mandatory content fields
- [ ] 4. Output preflight validation (HG1 b, c) — before write
- [ ] 5. Generate the Idea file
- [ ] 6. Update the source insight(s)
- [ ] 7. Post-write validation (HG1 e) with rollback
- [ ] 8. Integral final validation
```

### Step 1: Input preflight validation (HG1 a, d)

For each insight in `insight_path`, verify **before any read or synthesis**:

- [ ] (a) `insight.status == approved` (read the front-matter; if other than `approved`, abort and inform the human)
- [ ] (d) All insights in `insight_path` share the same `topic` (if divergent, abort; an Idea cannot mix topics)

If any of (a) or (d) fails, **interrupt immediately** and inform the human with:

- Which insights failed which precondition
- Which human action unblocks (e.g., approve the insight, separate into distinct Ideas per topic)

Phanes **MUST NOT** change an insight status to `approved` — that is a human prerogative per HARD-GATE 2 of `lex-discovery-flow`.

### Step 2: Read source insights

Read the insight file(s) in full, capturing:

1. Front-matter (`id`, `topic`, `tags`, `source_refs`)
2. Body: **Observation**, **Source**, **Initial implication**, **Open questions**
3. Relevant change history (file's git log) — useful to understand what was refined and why

Accumulate the content as the basis for the Idea synthesis.

### Step 3: Synthesize the 5 mandatory content fields

For each mandatory field, apply the heuristic:

| Field | Heuristic |
|-------|-----------|
| `problem` | Rewrite the insight's "Observation" as a concrete problem in 1 sentence, with magnitude when the insight has quantitative data. No embedded solution |
| `hypothesis` | Structure "If X, then Y, measured by Z". X = conceptual solution; Y = expected effect; Z = measurable criterion. When the insight lacks evidence to fix Y/Z, mark with an explicit placeholder (e.g., "Y to be confirmed via experiment") instead of inventing a number |
| `target_user` | Extract the specific persona from the insight (role + context). Avoid "all users"; when the insight does not name one, use the persona from the primary source |
| `success_metric` | Leading or lagging metric with `baseline` (from the insight) and `target` (initial proposal based on a conservative gain, e.g.: -50% of the baseline). When the insight has no baseline, declare the need for a baseline before implementation |
| `effort_estimate` | T-shirt size (`XS`, `S`, `M`, `L`, `XL`) with 1 sentence in parentheses justifying: external dependencies, model to be built, integrations |

The synthesis is an initial proposition — `warrior-prometheus` later refines it when transforming it into a PRD.

### Step 4: Output preflight validation (HG1 b, c) — BEFORE write

On the synthesized Idea (in memory, before writing the file), verify:

- [ ] (b) The Idea's `linked_insights[]` has at least 1 entry (will be filled with the `id`s of the insights read in Step 2)
- [ ] (c) The 5 mandatory content fields — `problem`, `hypothesis`, `target_user`, `success_metric`, `effort_estimate` — have substantive text (no raw placeholder such as "TBD" or empty string). If the Step 3 heuristic could not produce content for some field, **interrupt** and inform the human which additional evidence unblocks

If any of (b) or (c) fails, **abort before writing** — no file is created, no insight is updated.

### Step 5: Generate the Idea file

1. Determine `{NNN}`: next sequential number within `docs/discovery/{topic}/ideas/`
2. Determine `{slug}`: short kebab-case summarizing the Idea (do not copy from the insight; it MAY differ)
3. Compose `id`: `{topic}/ideas/{NNN}-{slug}`
4. Assemble front-matter per `codex-discovery-artifacts`
5. Structure the Markdown body in the 3 sections: **Synthesis**, **Source insights** (numbered list referencing `linked_insights[]`), **Next steps** (suggestions for additional validation, no priority decision)
6. Create intermediate directories if needed and write the file

### Step 6: Update the source insight(s)

**Before writing**, capture in memory the original `updated_at` of each insight (needed for rollback in Step 7; the original `status` does not need a snapshot because it is always `approved`, validated in Step 1 (a)).

For each insight in `linked_insights[]`:

1. Update `status` to `promoted`
2. Fill `idea_ref` with the `id` of the created Idea
3. Update `updated_at` to the current timestamp
4. Keep the rest of the file untouched (the insight body remains as audit trail)

This update is **the only status transition `warrior-phanes` executes autonomously** — authorized by HARD-GATE 1 (e), with the precondition that the Idea was successfully created in Step 5.

### Step 7: Post-write validation (HG1 e) with rollback

After Step 6, verify that **all** insights in `linked_insights[]` were updated:

- [ ] Each source insight has `status: promoted` persisted on disk
- [ ] Each source insight has `idea_ref` pointing to the created Idea's `id`
- [ ] Each source insight has `updated_at` updated

If any insight failed to update (write error, permission, conflict), execute a **transactional rollback**:

1. Delete the Idea file created in Step 5 (`docs/discovery/{topic}/ideas/{NNN}-{slug}.md`)
2. Revert any partial update on the insights that did persist (restore original `status`, `idea_ref: null`, prior `updated_at`)
3. Report to the human which operation failed and the restored state

The rollback's goal is to keep the invariant: *Idea exists ⇔ all of its `linked_insights[]` are `promoted` with correct `idea_ref`*. There MUST NOT be an orphan Idea nor a `promoted` insight without an Idea.

### Step 8: Integral final validation

Before delivering (after Step 7 has passed cleanly):

- [ ] HARD-GATE 1 (a): `status == approved` in all source insights (validated in Step 1)
- [ ] HARD-GATE 1 (b): The Idea's `linked_insights[]` has at least 1 entry (validated in Step 4)
- [ ] HARD-GATE 1 (c): The 5 mandatory content fields of the Idea have substantive text (validated in Step 4)
- [ ] HARD-GATE 1 (d): The Idea's `topic` matches the `topic` of ALL `linked_insights[]` (validated in Step 1)
- [ ] HARD-GATE 1 (e): All source insights have been updated to `status: promoted` with the correct `idea_ref` (validated in Step 7)
- [ ] The Idea's `id` is unique within the topic
- [ ] The content respects `lex-tone` and the language matches `language.default`
- [ ] No insight had any field besides `status`, `idea_ref`, and `updated_at` modified

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| New Idea | Markdown with YAML front-matter | `docs/discovery/{topic}/ideas/{NNN}-{slug}.md` |
| Updated insight(s) | Markdown with updated YAML front-matter (same original path) | `docs/discovery/{topic}/insights/{NNN}-{slug}.md` |
| Execution summary | Message to the human | Current session — confirms the created Idea, lists promoted insights, and flags Idea fields that depend on additional validation |

## Execution Example

### Example Input

```
insight_path:
  - docs/discovery/scheduled-payments-research/insights/001-manual-reconciliation-bottleneck.md
additional_context: |
  Pilot client available: firm Y, with 80 active accountants
```

### Example Output

Generated file: `docs/discovery/scheduled-payments-research/ideas/001-auto-reconcile-erp-bank.md`

```markdown
---
id: "scheduled-payments-research/ideas/001-auto-reconcile-erp-bank"
topic: "scheduled-payments-research"
problem: "Accountants in mid-sized firms spend on average 4h/week manually reconciling divergent entries between the ERP and the bank statement, with no perception of value added by the activity."
hypothesis: "If the system suggests automatic reconciliation with ≥90% confidence for date and duplication divergences, accountants will accept the suggestion in ≥70% of cases, reducing manual time by ≥60%."
target_user: "Operational accountant in firms with 50-500 active clients, integrated with ERP X"
success_metric: "Average reconciliation time per month per client — baseline 4h (interview 2026-05-04) → target 1.5h in 90 days after release"
effort_estimate: "M (2-4 sprints; depends on the matching model and integration with ERP X webhooks)"
linked_insights:
  - "scheduled-payments-research/insights/001-manual-reconciliation-bottleneck"
created_at: "2026-05-10T15:00:00Z"
updated_at: "2026-05-10T15:00:00Z"
---

# Idea: Automatic suggestion for ERP × bank statement reconciliation

## Synthesis

Accountants in mid-sized firms spend hours each week manually reconciling divergent entries; offering an automatic suggestion for the two most frequent divergence types (date and duplication) can reduce manual time by at least 60%, validatable with a pilot in a firm with an ERP X client base.

## Source insights

1. **scheduled-payments-research/insights/001-manual-reconciliation-bottleneck** — 4h/week of manual reconciliation; bottleneck declared by interviewed accountants; ERP X requires 7 screens to resolve 1 divergence.

## Next steps

- Confirm baseline with 3 more interviews in different firms (validate that 4h/week is median, not outlier)
- Collect a sample of 200 real divergences to train/evaluate the matching model
- Map available webhooks in ERP X (gap identified in the interview, but not validated against the ERP product)
```

And the updated source insight:

```markdown
# (same body content)
---
status: promoted
idea_ref: "scheduled-payments-research/ideas/001-auto-reconcile-erp-bank"
updated_at: "2026-05-10T15:00:00Z"
# (other fields unchanged)
---
```

## Restrictions

- Never change an insight's `status` to `approved` — approval is a human prerogative per HARD-GATE 2 of `lex-discovery-flow`
- Never produce an Idea without fully validating the 5 preconditions of HARD-GATE 1
- Never mix distinct `topics` in a single Idea — the Idea's `topic` MUST match the `topic` of all `linked_insights[]`
- Never fill the 5 mandatory content fields with raw placeholders such as "TBD"; when evidence is missing, explicitly declare it (e.g., "baseline to be confirmed via 3 additional interviews")
- Never modify source insight fields beyond `status`, `idea_ref`, and `updated_at`
- The Step 7 rollback is part of the normal workflow when partial source-insight updates fail — it is not an exception path, it is the invariance mechanism. Do NOT skip Step 7 even when the write "appears successful"; verify on-disk persistence and execute the transactional rollback if any insight ended up out of sync with the Idea

## References

- `lex-discovery-flow` — applicable law; HARD-GATE 1 is the central precondition of this Kata
- `codex-discovery-artifacts` — full schema, state machine, `approved → promoted` transition
- `kata-discovery-synthesis` — complementary Kata (upstream insight production)
- `lex-tone`, `codex-tone` — writing style
- `warrior-phanes` — agent that executes this Kata
