# Cry: Start a Product Discovery Session

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Product Discovery — shortcut to invoke `warrior-pitia` with a `topic` and `source_refs[]`

## Description

Shortcut that invokes `warrior-pitia` to conduct a Product Discovery session: read the provided sources and produce one or more structured insights under `docs/discovery/{topic}/insights/`. The Cry **does not** invoke Lexis or Codex directly — it only triggers the Warrior, which internally executes `kata-discovery-synthesis` and consults `lex-discovery-flow` and `codex-discovery-artifacts`.

## Usage

```
/cry-discovery
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `topic` | Yes | Discovery initiative theme in kebab-case | `scheduled-payments-research` |
| `source_refs[]` | Yes (≥1) | List of URLs or paths of the sources to study | Notion, Figma, GitHub URLs; local paths |
| `mode` | No | `new` (default) or `refine` | `new` |
| `target_insight_id` | Conditional | Required if `mode == refine` — id of the insight to update | `scheduled-payments-research/insights/001-...` |
| `feedback` | Conditional | Required if `mode == refine` — text of the human feedback | "Specify what counts as a high divergence" |

## What the Command Does

1. Invokes `warrior-pitia` with the provided parameters
2. Pitia reads `.ahrena/.directives`, internalizes `lex-discovery-flow` and `codex-discovery-artifacts`
3. Pitia executes `kata-discovery-synthesis`, reading the `source_refs[]` via MCP or `Read`
4. Pitia produces new files in `docs/discovery/{topic}/insights/` (`new` mode) or updates an existing file (`refine` mode)
5. Pitia reports the created/updated files and highlights critical open questions

## Prompt Template

```
Take the role of warrior-pitia (Product Discovery).

Received parameters:
- topic: {{topic}}
- source_refs:
{{source_refs}}
- mode: {{mode}}
- target_insight_id: {{target_insight_id}}
- feedback: {{feedback}}

Task:
Execute kata-discovery-synthesis with the parameters above.
Before any write, read .ahrena/.directives, lex-discovery-flow, and codex-discovery-artifacts.
Produce one insight per file in docs/discovery/{{topic}}/insights/{NNN}-{slug}.md
with status: proposed (new mode) or update the existing one (refine mode).
Do not propose a solution — solutions are warrior-phanes's responsibility.
Do not change status to anything other than the initial creation in proposed (HARD-GATE 2).

Output format:
- List of created/updated files with canonical paths
- For each insight, 1-sentence summary of the observation
- Critical open questions that need additional evidence
- Candidates for awaiting_evidence when applicable (signal to the human; do not change status)
```

## Invocation Example

**Input:**

```
/cry-discovery
topic: scheduled-payments-research
source_refs:
  - https://www.notion.so/guardia/interview-accountant-2026-05-04-abc123
  - docs/transcripts/process-walkthrough-erp-x.md
  - https://github.com/guardiatechnology/erp-x-spec/blob/main/openapi.yaml
mode: new
```

**Expected output:**

```
warrior-pitia executed kata-discovery-synthesis. 3 insights created with status: proposed:

1. docs/discovery/scheduled-payments-research/insights/001-manual-reconciliation-bottleneck.md
   — 4h/week of manual reconciliation; bottleneck declared by the interviewed accountant
2. docs/discovery/scheduled-payments-research/insights/002-erp-x-7-screens-per-divergence.md
   — 7 screens to resolve 1 divergence; OpenAPI without batch reconciliation endpoint
3. docs/discovery/scheduled-payments-research/insights/003-date-vs-cash-divergence-pattern.md
   — Accrual vs. cash date divergence concentrates ~60% of occurrences

Critical open questions:
- Real median reconciliation time per firm (sample of 1)
- Confirmation of the divergence pattern in firms beyond the interviewed one

Candidate for awaiting_evidence: insight #003 (depends on median). Transition decision is yours.
```

## Restrictions

- Does not modify existing insights except in `refine` mode with a valid `target_insight_id`
- Does not create an Idea — Idea is `warrior-phanes`'s responsibility via `cry-ideation`
- Does not change status outside the initial creation in `proposed` — every other transition depends on human action per HARD-GATE 2 of `lex-discovery-flow`
- Output always in the language defined in `language.default` of `.directives` (default: pt-BR)

## Difference from Kata

| Aspect | Cry | Kata |
|--------|-----|------|
| **Nature** | Shortcut to invoke Pitia | Procedure that Pitia executes |
| **Who invokes** | Human user | Warrior (Pitia) |
| **What it does** | Triggers the warrior with parameters | Synthesizes sources into insights |
| **Example** | `/cry-discovery` | `kata-discovery-synthesis` |

## References

- `warrior-pitia` — agent invoked by this Cry
- `kata-discovery-synthesis` — procedure executed internally
- `lex-discovery-flow` — applicable law (consulted by the warrior, not by the cry)
- `codex-discovery-artifacts` — insight schema (consulted by the warrior)
