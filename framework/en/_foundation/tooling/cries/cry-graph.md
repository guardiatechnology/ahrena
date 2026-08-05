# Cry: Query the Codebase Graph

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Engineering — quick query against the codebase knowledge graph

## Description

Shortcut to build, update, or query a repository's knowledge graph. The command invokes `kata-codebase-graph`, which runs the full procedure: verifies enablement, builds or updates the graph, checks staleness, and returns the answer with provenance declared.

The most frequent use is answering "who breaks if I change this", the reverse-dependency question that reading the repository ad hoc does not answer.

## Usage

```
/cry-graph [question or node] [--repo <path>] [--depth N] [--refresh]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `question or node` | No | Label of the node to analyze, or an open question. With no argument, the command builds or updates the graph and reports hubs | `VersionSeal` |
| `--repo` | No | Repository path. Default: current repository | `--repo ../financial-context` |
| `--depth` | No | Depth of the reverse traversal. Default: 2 | `--depth 3` |
| `--refresh` | No | Forces a graph update before querying | `--refresh` |

## What the Command Does

1. Invokes `kata-codebase-graph` with the arguments received
2. The Kata verifies `graphify.enabled` and the presence of the binary; if unavailable, it reports and ends without error
3. The Kata builds or updates the graph in deterministic mode and compares `built_at_commit` against `HEAD`
4. The Kata runs the query appropriate to the question and returns the answer with source commit, extraction mode, and edge confidence

## Prompt Template

```
Execute kata-codebase-graph.

Context:
- Repository: {{--repo | current repository}}
- Query target: {{question or node | none — build/update only and report hubs}}
- Reverse traversal depth: {{--depth | 2}}
- Force update: {{--refresh | no}}

Task:
Follow the kata-codebase-graph workflow from step 1 through 6. When a query
target is present, prioritize reverse traversal (impact) over direct traversal.
If the graph is unavailable, disabled, or stale, declare the situation and
return control without error.

Output format:
- Provenance line: built_at_commit, extraction mode, node and edge counts
  with the EXTRACTED / INFERRED split
- Affected-components table in the kata-architecture-brief format
  (Component | Type | Action | ACs covered)
- Explicit identification of components coming from reverse traversal
- Marking of rows supported only by INFERRED edges
```

## Invocation Example

**Input:**

```
/cry-graph VersionSeal --repo ../financial-context --depth 2
```

**Expected output:**

```
Graph: built_at_commit 3b1c756 (same as HEAD) · mode --code-only
20,882 nodes · 49,563 edges · 45,782 EXTRACTED / 3,781 INFERRED

VersionSeal — degree 238, community 1
Defined at components/commons/infra/data/version/seal.py:L34

Reverse impact (depth 2):
| Component | Type | Action | ACs covered |
|---|---|---|---|
| components/commons/application/services/_lifecycle_test.py:L49 | test | review | — |
| components/commons/infra/data/contracts/version_record.py:L39 | module | assess (INFERRED) | — |

1 row supported only by an INFERRED edge. Confirm before treating it as a
scope boundary.
```

## Constraints

- Does not build the graph on its own: it delegates entirely to `kata-codebase-graph`
- Does not install the Graphify binary
- Does not version `graph.json`
- Does not block the flow when the graph is unavailable — it reports and ends without error
- Does not present a result without the provenance line

## Difference from Kata

| Aspect | Cry | Kata |
|--------|-----|------|
| **Nature** | Quick invocation | Complete procedure |
| **Complexity** | Low: receives arguments and delegates | High: 6 steps with final validation |
| **Configures an agent?** | No | Yes |
| **Example** | `/cry-graph VersionSeal` | `kata-codebase-graph` from step 1 through 6 |
