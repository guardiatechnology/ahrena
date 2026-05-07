# Kata: Discovery Insight Synthesis

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Product Discovery — reading heterogeneous sources and producing structured insights under `docs/discovery/{topic}/insights/`

## Objective

Standardize how `warrior-pitia` reads sources (APIs, OpenAPI, Notion, Figma, transcripts, legacy processes, screens) and produces Product Discovery insights in canonical format, with `status: proposed` and references to consulted sources. The insight is an indivisible unit of discovery — one insight per file, with front-matter per `codex-discovery-artifacts`.

## When to Use

- When `cry-discovery` is invoked with a `topic` and a list of `source_refs[]`
- When the user explicitly requests `warrior-pitia` to study a set of sources for an existing topic
- When `warrior-pitia` is in the `refining` state and needs to return a v2 of an insight (transition `refining → under_review`)

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| `topic` | Yes | Discovery initiative theme in kebab-case (e.g., `accountant-onboarding`). Creates the directory `docs/discovery/{topic}/` if it does not exist |
| `source_refs[]` | Yes (≥1) | List of URLs or paths of the sources to study. May include Notion, Figma, OpenAPI, transcripts in `docs/transcripts/`, GitHub repositories |
| `language` | No | Overrides `language.default` from `.directives` (default: pt-BR) |
| `mode` | No | `new` (default — creates new insights) or `refine` (updates existing insight in `status: refining`) |
| `target_insight_id` | Conditional | Required if `mode == refine` — id of the insight to update |
| `feedback` | Conditional | Required if `mode == refine` — text of the human feedback that motivated the refinement |

## Workflow

```
Progress:
- [ ] 1. Read directives and codex
- [ ] 2. Read sources via MCP or Read
- [ ] 3. Identify insight candidates
- [ ] 4. Apply the canonical schema
- [ ] 5. Generate the file(s)
- [ ] 6. Final validation
```

### Step 1: Read directives and codex

1. Read `.ahrena/.directives` to confirm `language.default` and `naming.casing`
2. Read `codex-discovery-artifacts` to internalize:
   - Addressing `docs/discovery/{topic}/insights/{NNN}-{slug}.md`
   - Full front-matter schema
   - State machine and valid transitions
3. Read `lex-discovery-flow` to internalize the applicable HARD-GATEs (especially HARD-GATE 2: initial creation belongs to Pitia, but any subsequent transition requires human direction)

### Step 2: Read sources via MCP or Read

For each item in `source_refs[]`, trigger the appropriate tool:

| Source type | Tool | Associated kata |
|-------------|------|-----------------|
| Notion URL | MCP `notion-fetch` or `notion-search` | `kata-mcp-notion-read` |
| Figma URL | MCP Figma `get_design_context` or `get_metadata` | `kata-mcp-figma-extract` |
| GitHub URL (repo, issue, PR, OpenAPI) | MCP `gh-*` or `Read` for local files | `kata-mcp-github-read` |
| Local path (`docs/transcripts/...`, OpenAPI YAML, process) | Direct `Read` | — |

When the corresponding MCP is not listed in `mcp.servers` of `.directives`, follow `lex-mcp` rule 4 (offer choice between CLI fallback, pause, or abort).

Accumulate the read content as evidence. When the content is extensive, save relevant excerpts quoted literally (with quotation marks) in the insight body.

### Step 3: Identify insight candidates

For each insight candidate, verify:

1. **Indivisible unit:** the insight expresses **one** observation. If the content covers 2 distinct pains, they are 2 separate insights.
2. **Conceptually actionable:** the insight points to a business implication, even if it does not yet propose a solution.
3. **Traceable:** the `source_refs[]` in the front-matter cover all sources that support this observation.
4. **No embedded solution:** if the text starts proposing a solution, move the solution part to "Initial implication" as a hypothesis, not as a decision. Idea formation is `warrior-phanes`'s responsibility.

### Step 4: Apply the canonical schema

For each confirmed candidate, assemble the front-matter per `codex-discovery-artifacts`:

- `id`: `{topic}/insights/{NNN}-{slug}` — `{NNN}` is the next sequential number within the topic (read `docs/discovery/{topic}/insights/` and increment)
- `topic`: identical to the input `topic`
- `status`: `proposed` (always, on initial creation)
- `source_refs`: list of the sources actually consulted (do not copy raw input — only those that genuinely support THIS insight)
- `tags`: optional; use them when they help aggregate with other insights
- `created_at`, `updated_at`: current ISO 8601 timestamp
- Conditional fields (`merged_into`, `idea_ref`, `rejected_reason`, `awaiting_evidence_reason`): `null` on creation

Structure the Markdown body in the 4 sections: **Observation**, **Source**, **Initial implication**, **Open questions**.

### Step 5: Generate the file(s)

1. Create intermediate directories if necessary (`docs/discovery/{topic}/insights/`)
2. Write one file per identified insight
3. When `mode == refine`:
   - Do not create a new file — update the existing one identified by `target_insight_id`
   - Update `updated_at` to the current timestamp
   - Rewrite the 4 body sections incorporating the received `feedback`
   - After persisting v2, update `status: under_review` — this transition is authorized per HARD-GATE 2 of `lex-discovery-flow` (precondition (d) met: v2 written with updated `updated_at`), executed by Pitia to close the `refining → under_review` cycle initiated by the original human direction
   - Record a message to the human that v2 is ready for new evaluation

### Step 6: Final validation

Before delivering:

- [ ] Each created insight has unique `id`, correct `topic`, and `source_refs[]` with at least 1 entry
- [ ] In `mode == new`: each created insight has `status: proposed`
- [ ] In `mode == refine`: the updated insight has `status: under_review` (Pitia closed the cycle per HG2 precondition (d)) and `updated_at` updated
- [ ] The 4 body sections (Observation, Source, Initial implication, Open questions) are filled — no placeholders such as "TBD"
- [ ] No insight proposes a solution; every solution hypothesis lives in the "Open questions" section as a question
- [ ] The content respects `lex-tone` (direct, strategic, no buzzwords) and the language matches `language.default`

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| New insight | Markdown with YAML front-matter | `docs/discovery/{topic}/insights/{NNN}-{slug}.md` |
| Updated insight (refine mode) | Markdown with YAML front-matter (same path) | `docs/discovery/{topic}/insights/{NNN}-{slug}.md` |
| Execution summary | Message to the human | Current session — lists created/updated files and points out `Open questions` that need evidence |

## Execution Example

### Example Input

```
topic: scheduled-payments-research
source_refs:
  - https://www.notion.so/guardia/interview-accountant-2026-05-04-abc123
  - docs/transcripts/process-walkthrough-erp-x.md
  - https://github.com/guardiatechnology/erp-x-spec/blob/main/openapi.yaml
mode: new
```

### Example Output

Generated file: `docs/discovery/scheduled-payments-research/insights/001-manual-reconciliation-bottleneck.md`

```markdown
---
id: "scheduled-payments-research/insights/001-manual-reconciliation-bottleneck"
topic: "scheduled-payments-research"
status: proposed
source_refs:
  - "https://www.notion.so/guardia/interview-accountant-2026-05-04-abc123"
  - "docs/transcripts/process-walkthrough-erp-x.md"
tags:
  - reconciliation
  - manual-process
created_at: "2026-05-06T11:00:00Z"
updated_at: "2026-05-06T11:00:00Z"
merged_into: null
idea_ref: null
rejected_reason: null
awaiting_evidence_reason: null
---

# Insight: Manual ERP × statement reconciliation is the largest operational bottleneck

## Observation

Accountants in mid-sized firms spend, on average, 4h per week manually reconciling divergent entries between the ERP and the bank statement. The most frequent divergence is accrual vs. cash date, followed by duplicated write-offs.

## Source

- Interview with accountant X (2026-05-04): "I spend almost every Tuesday just reconciling — nothing I do here adds value"
- Walkthrough of the process in ERP X: 7 screens to reconcile 1 divergent entry

## Initial implication

Reducing time spent on manual reconciliation frees accountant capacity for analysis — an activity perceived as higher-value by both the accountant and the firm.

## Open questions

- What is the actual distribution of time spent across divergence types (date, duplication, value, counterparty)?
- What is the expected acceptance rate of an automatic suggestion with ≥90% confidence?
- Which ERPs besides X concentrate the target client base?
```

## Restrictions

- Never propose a solution in the insight; the solution is Phanes's responsibility via Idea
- Never consolidate multiple insights into a single file — one insight per file
- The only `status` transitions Pitia executes autonomously are: `[*] → proposed` (new mode, initial creation) and `refining → under_review` (refine mode, closing the cycle after rewriting v2 — HG2 precondition (d) met). All other transitions require explicit human direction per HARD-GATE 2 of `lex-discovery-flow`
- Never embed a reference to `idea_ref` on initial creation; this field is filled by Phanes
- Always quote literal excerpts (with quotation marks) when referencing an interview or doc — avoids second-level interpretation

## References

- `lex-discovery-flow` — applicable law, with the HARD-GATEs that govern status
- `codex-discovery-artifacts` — full schema, state machine, addressing
- `kata-mcp-notion-read`, `kata-mcp-figma-extract`, `kata-mcp-github-read` — MCP reading procedures
- `lex-mcp` — fallback when MCP is unavailable
- `lex-tone`, `codex-tone` — writing style
- `warrior-pitia` — agent that executes this Kata
