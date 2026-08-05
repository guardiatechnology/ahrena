# Codex: Graphify — Codebase Knowledge Graph

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Engineering — code comprehension, impact mapping, and technical design support

## Overview

Graphify is a command-line tool that turns a repository into a queryable knowledge graph. Code extraction runs through tree-sitter AST parsing, locally and without API calls. Documents, PDFs, images, and database schemas go through an optional semantic pass that uses a language model.

The value for Guardia is specific: answering reverse-dependency questions. Step 2 of `kata-architecture-brief` produces the affected-components table, and that table is the scope boundary `kata-quality-gate` consumes in its scope-creep check. Today the table is assembled by reading the repository ad hoc, which finds direct dependencies and misses reverse ones. The `graphify affected` command answers "who breaks if I change this" with `file:line` precision.

This Codex documents the actual surface of the measured version (0.9.33), the cost model measured against a Guardia repository, and the observed limitations. It does not replace the vendor documentation; it records what was verified.

## Context

- **Domain:** codebase comprehension, impact mapping, technical design support
- **Audience:** engineering warriors (`warrior-apollo`, `warrior-hephaestus`, `warrior-athena`), developers, PR reviewers
- **Update:** on every Graphify version change that alters commands, the `graph.json` format, or the cost model

## Content

### Principles

1. **Code extraction is deterministic; the semantic pass is not.** The `--code-only` mode runs local AST parsing, with no API key and no network access. It is reproducible and safe for automation. The semantic pass depends on a language model and offers no such guarantee.
2. **The graph is advisory input, never a CI gate.** The agent decides; the graph informs. `scripts/validate.py` is deterministic by design and MUST NOT come to depend on a semantic pass.
3. **`INFERRED` does not mean "produced by an LLM".** Edge confidence describes how the relation was resolved, not which engine produced it. See "Patterns and Conventions".
4. **The graph ages with every commit.** `graph.json` carries `built_at_commit`. Querying a stale graph without checking that field produces wrong answers that look precise.
5. **The tool is optional.** Every consumer of the graph MUST degrade cleanly when the binary is absent, `graphify.enabled` is `false`, or the graph is stale.

### Patterns and Conventions

#### Edge confidence

| Confidence | Meaning | Example relation |
|------------|---------|------------------|
| `EXTRACTED` | The relation is explicit in the source code | `imports`, `calls`, `contains` |
| `INFERRED` | The relation was resolved by a Graphify heuristic | `uses` derived from type resolution |

Measurement on `financial-context`: of 49,563 edges, **45,782 are `EXTRACTED` and 3,781 are `INFERRED`** — and **all** carry `_origin: ast`. That is, `INFERRED` edges appear in `--code-only` mode with no API call at all. The mode remains deterministic; it simply is not free of `INFERRED` edges.

#### `graph.json` structure

| Field | Type | Note |
|-------|------|------|
| `nodes` | list | Keys: `label`, `file_type`, `source_file`, `source_location`, `_origin`, `id`, `community`, `norm_label` |
| `links` | list | Edges. Keys: `relation`, `confidence`, `source_file`, `source_location`, `weight`, `_origin`, `source`, `target`, `confidence_score` |
| `hyperedges` | list | Empty in the measured extraction |
| `built_at_commit` | string | Source commit of the graph — canonical basis for staleness detection |
| `directed` | boolean | `false` in the measured extraction |
| `multigraph` | boolean | `false` in the measured extraction |

The edge list is named `links`, not `edges` (D3 convention).

#### Verified command catalog

| Command | Function |
|---------|----------|
| `extract <path>` | Full headless extraction (AST plus semantic) for CI and scripts |
| `extract --code-only` | Indexes code only through local AST; skips documents, papers, and images |
| `update <path>` | Re-extracts code files and updates the graph, without an LLM |
| `affected "X"` | Reverse traversal: nodes impacted by X. Accepts `--relation` and `--depth` |
| `explain "X"` | Node and neighborhood in plain language, with degree and inbound and outbound edges |
| `path "A" "B"` | Shortest path between two nodes |
| `query "<question>"` | BFS traversal of the graph for a question. `--budget` caps output in tokens |
| `god-nodes` | Most connected nodes (architectural hubs) |
| `check-update <path>` | Checks the `needs_update` flag; cron-safe |
| `cluster-only <path>` | Reruns clustering and regenerates the report. `--no-label` avoids LLM calls |
| `benchmark [graph.json]` | Measures token reduction against the full-corpus approach |
| `diagnose multigraph` | Reports collapse risk for edges sharing endpoints |
| `watch <path>` | Watches a folder and rebuilds the graph on every change |
| `install --platform P` | Installs Graphify as a skill in the platform configuration directory |
| `hook install` | Installs post-commit and post-checkout git hooks |
| `merge-driver` | Git merge driver that union-merges two `graph.json` files |

`graphify-mcp` is a second executable installed alongside. It serves the graph over MCP on `stdio` or Streamable HTTP transport, with `--api-key`, `--host`, `--port`, and `--stateless`. Per `lex-mcp` rule 5 this is **tier 2 (native binary stdio)**; tier 1 (vendor-hosted remote HTTP) does not exist for this vendor. The decision to declare the server in `mcp.servers` belongs to the installation track, not to this Codex.

#### Language model backends

`--backend` accepts `gemini`, `kimi`, `claude`, `openai`, `deepseek`, `ollama`, and `claude-cli`.

The **`claude-cli`** backend is the recommended path at Guardia. It routes through the locally installed Claude Code CLI, via `claude -p --output-format json`, and authenticates with the existing Pro/Max subscription. Its price table is literally `{"input": 0.0, "output": 0.0}`: usage bills to the plan, not to pay-as-you-go API credit. No separate API key is required.

Two practical consequences: `--max-concurrency` is forced to 1 for `claude-cli`, and every invocation loads the local Claude Code context. See "Technical Constraints".

### Active Decisions

| Decision | Status |
|----------|--------|
| `graph.json` stays out of version control, cached under `.ahrena/`, and `graphify-out/` goes into the managed `.gitignore` block | Active |
| Staleness detection uses `built_at_commit` and `graphify check-update`, with no parallel SHA stamp | Active |
| Graph consumption is advisory; no CI gate depends on a semantic pass | Active |

On the first decision: the vendor offers `graphify merge-driver` precisely for teams that **version** `graph.json`, resolving conflicts by union. Guardia diverges from that practice because a versioned `graph.json` is a second representation of code structure, liable to drift from the actual code — which `lex-dry` forbids. The divergence is deliberate and recorded here.

### Technical Constraints

- **The real cost is plan quota, not dollars.** In the semantic measurement, 178,164 input tokens were consumed to process roughly 18,400 tokens of content — about 10× amplification. The cause sits in Graphify's own source (`llm.py`): Claude Code CLIs from version 2.1 onward do not treat `--system-prompt` as the sole authority and still load local `CLAUDE.md`, `AGENTS.md`, skills, and MCP context on every invocation. A trivial `claude -p "reply OK"` at the repository root reported `total_cost_usd: 0.82` with 82,453 cache-creation tokens.
- **Mitigation:** invoke Graphify from a neutral working directory, not from the root of a repository carrying a large `CLAUDE.md`. The bootstrap cost is charged per call and `claude-cli` does not parallelize.
- **`affected` requires a unique label.** `graphify affected "EntityId"` failed with `No unique node match for EntityId`. Ambiguous labels require the qualified node ID.
- **SQL requires an installation extra.** `.sql` files do not contribute to the graph without `tree_sitter_sql`. Install with `pip install "graphifyy[sql]"` (upstream issue #1745). Relevant for financial and tax contexts.
- **Some JSON files produce zero nodes.** In the measurement, 22 files generated no nodes, among them `ahrena.json`, `figma.json`, `github.json`, `notion.json`, and `slack.json` (upstream issue #1666).
- **Large graphs require `--no-viz`.** Above roughly 5,000 nodes, disable `graph.html` generation.
- **The measured graph is undirected** (`directed: false`), which affects how reverse traversal is interpreted. Use `diagnose multigraph` to assess edge-collapse risk.
- **`.gitignore` is respected by default.** In the measurement, 1,707 files were extracted out of 4,168 tracked, and virtual-environment dependencies were correctly excluded. `--no-gitignore` inverts this behavior.

#### Measured cost model

Measurement on `financial-context` at commit `3b1c756`, Graphify 0.9.33, 16 AST workers.

| | `--code-only` | Semantic (`--backend claude-cli`) |
|---|---|---|
| Wall clock | 359 s for 1,707 files (**0.21 s per file**) | 322 s for 22 documents (**14.6 s per file**) |
| Nodes / edges | 20,882 / 49,563 | 36 / 163 |
| Communities | 738 | not applicable (`--no-cluster`) |
| Tokens | 0 | 178,164 input / 40,517 output |
| API key | not required | not required (local CLI plus subscription) |
| Reported API cost | US$ 0.00 | US$ 0.0000 (billed to the plan) |
| Concurrency | 16 workers | forced to 1 |

`graphify benchmark` over the code graph: a corpus of 1,044,100 words, roughly 1,392,133 tokens in the naive approach, against approximately 12,841 tokens per query — a **108.4× reduction**. The per-question range ran from 83.2× ("what connects the data layer to the api") to 171.0× ("how does authentication work").

## Reference Diagram

```
                    ┌─────────────────────────┐
   repository ────► │ extract --code-only     │  local AST, tree-sitter
                    │ (deterministic, free)   │  0 API calls
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
   docs, PDFs ────► │ semantic pass           │  --backend claude-cli
   images           │ (optional, plan quota)  │  concurrency forced to 1
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │ graph.json              │
                    │  nodes / links          │
                    │  built_at_commit  ──────┼──► staleness basis
                    └───────────┬─────────────┘
                                │
        ┌───────────────┬───────┴───────┬────────────────┐
        ▼               ▼               ▼                ▼
    affected "X"    explain "X"    path "A" "B"     graphify-mcp
   (reverse         (node and      (link between    (stdio or HTTP)
    impact)          neighborhood)  two nodes)
```

## Glossary

| Term | Definition |
|------|------------|
| AST | Abstract syntax tree. Basis of deterministic code extraction, through tree-sitter |
| `EXTRACTED` | Edge explicit in the source code |
| `INFERRED` | Edge resolved by a Graphify heuristic, not necessarily by a language model |
| Community | Node grouping detected by the Leiden algorithm; approximates the notion of a subsystem |
| God node | Highly connected node; architectural hub |
| `built_at_commit` | Commit from which the graph was built |
| Semantic pass | Optional stage that uses a language model for documents, PDFs, and images |
| `claude-cli` | Backend that routes through the local Claude Code CLI and bills the subscription rather than API credit |

## References

- `kata-codebase-graph` — operational procedure that applies this Codex
- `cry-graph` — invocation shortcut
- `kata-architecture-brief` — consumer of the graph in step 2 (affected-components table)
- `kata-quality-gate` — consumes the scope boundary in the scope-creep check
- `lex-mcp` — rule 1 (preference for the MCP tool) and rule 5 (transport hierarchy)
- `lex-dry` — basis of the decision not to version `graph.json`
- `codex-git-spice` — Codex precedent for an external command-line tool
- Vendor repository: https://github.com/Graphify-Labs/graphify
