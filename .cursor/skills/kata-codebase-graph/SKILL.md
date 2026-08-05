---
name: kata-codebase-graph
description: "Codebase Knowledge Graph. Engineering — building, updating, and querying the code graph for impact mapping"
---

# Kata: Codebase Knowledge Graph

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Engineering — building, updating, and querying the code graph for impact mapping

## Workflow

Copy this checklist and track progress:

```
Progress:
- [ ] 1. Verify enablement and binary availability
- [ ] 2. Build or update the graph
- [ ] 3. Check staleness through built_at_commit
- [ ] 4. Query the graph
- [ ] 5. Assemble the affected-components table
- [ ] 6. Final validation
```

### Step 1: Verify enablement and binary availability

1. Read `graphify.enabled` in `.ahrena/.directives`. If `false`, record "graph disabled by directive" and end the Kata without error.
2. Verify the binary exists on the PATH. If absent, record "Graphify not installed" and end without error — the calling agent continues with prior behavior.
3. Do not install the binary inside this Kata. Installation belongs to the framework installation track.

### Step 2: Build or update the graph

1. If no graph exists for the repository, run the deterministic extraction:

   ```
   graphify extract <path> --code-only --out <cache>
   ```

   The `--code-only` mode runs local AST parsing, requires no API key, and makes no network calls.

2. If a graph already exists, prefer the incremental update:

   ```
   graphify update <path>
   ```

3. Run the semantic pass **only** when the question depends on documents, PDFs, or images. In that case use `--backend claude-cli`, which bills the Pro/Max subscription and requires no separate API key. Invoke it from a neutral working directory: every call loads the local Claude Code context, and concurrency is forced to 1. See "Technical Constraints" in `codex-graphify`.
4. On graphs above roughly 5,000 nodes, disable visualization with `--no-viz`.

### Step 3: Check staleness through `built_at_commit`

1. Read the `built_at_commit` field from `graph.json`.
2. Compare it against the repository's current `HEAD`.
3. If they diverge, run `graphify check-update <path>` and decide:
   - small divergence and the query does not touch the changed files: proceed and **declare** that the graph sits at the earlier commit;
   - material divergence: update with `graphify update` before querying.
4. Never present a stale graph result without declaring the source commit. A stale answer that looks precise is worse than no answer.

### Step 4: Query the graph

Choose the command by the question:

| Question | Command |
|----------|---------|
| Who breaks if I change X? | `graphify affected "X" --depth N` |
| What is X and what does it connect to? | `graphify explain "X"` |
| How does A link to B? | `graphify path "A" "B"` |
| What are the architectural hubs? | `graphify god-nodes --top N` |
| Open question about the codebase | `graphify query "<question>" --budget N` |

1. `affected` requires a unique label. If it returns `No unique node match`, obtain the qualified node ID through `explain` or by inspecting `graph.json`, and retry with the ID.
2. Record the confidence of the edges that support the answer. `EXTRACTED` is a relation explicit in the code; `INFERRED` is resolution by a Graphify heuristic — and it occurs in `--code-only` mode as well.
3. Use `--budget` on `query` to cap output in tokens.

### Step 5: Assemble the affected-components table

Consolidate the result in the format `kata-architecture-brief` consumes:

| Component | Type | Action | ACs covered |
|---|---|---|---|

1. Every row derived from the graph MUST carry the `file:line` origin Graphify provides.
2. Separate explicitly the components found through **reverse** traversal — those are precisely the ones an ad hoc read would miss.
3. Mark rows supported only by `INFERRED` edges. They require human confirmation before becoming a scope boundary.
4. Do not include in scope components that appeared only in the graph and bear no relation to any acceptance criterion.

### Step 6: Final Validation

Before delivering the output, verify:

- [ ] The graph's source commit (`built_at_commit`) is declared in the output
- [ ] Components coming from reverse traversal are identified as such
- [ ] Rows supported only by `INFERRED` edges are marked
- [ ] Every table row references at least one acceptance criterion
- [ ] If the graph was unavailable or stale, that is declared explicitly

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Affected-components table | Markdown | Step 2 of `kata-architecture-brief` |
| Provenance declaration | Markdown | Same output: source commit, extraction mode, edge confidence |
| Graph cache | JSON | `.ahrena/` (outside version control) |

## Execution Example

### Sample Input

```
Repository: financial-context
Node of interest: VersionSeal
Question: who is impacted if I change VersionSeal?
```

### Sample Output

```
Graph: built_at_commit 3b1c756 (same as HEAD) · mode --code-only
20,882 nodes · 49,563 edges · 45,782 EXTRACTED / 3,781 INFERRED

graphify affected "VersionSeal" --depth 2
Relations traversed: calls, references, imports, uses, inherits, implements (+7)

Reverse impact:
| Component | Type | Action | ACs covered |
|---|---|---|---|
| components/commons/application/services/_lifecycle_test.py:L49 | test | review | AC-1 |
| components/commons/application/services/archive_entity_service_test.py:L35 | test | review | AC-1 |
| components/commons/infra/data/contracts/version_record.py:L39 | module | assess (INFERRED) | AC-1 |

VersionSeal: degree 238, community 1, defined at
components/commons/infra/data/version/seal.py:L34.

Note: version_record.py enters only through an INFERRED edge (a `uses`
relation resolved by heuristic). Confirm before treating it as a scope boundary.
```

## Constraints

- Never block the calling flow. An absent binary, `graphify.enabled: false`, or a stale graph result in an explicit record and return of control, not in an error
- Never present a result without declaring `built_at_commit` and the extraction mode
- Never treat an `INFERRED` edge as confirmed fact when defining a scope boundary
- Never version `graph.json`. The cache lives under `.ahrena/`, outside version control, per the decision recorded in `codex-graphify`
- Never run the semantic pass when the question is answerable from code. The `--code-only` mode is free and deterministic
- Never install the binary inside this Kata
- Consult `codex-graphify` before using any command not listed in step 4
