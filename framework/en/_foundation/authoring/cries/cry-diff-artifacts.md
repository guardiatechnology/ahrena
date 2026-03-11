# Cry: Diff Artifacts

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Comparing project artifacts with the framework

## Description

Shortcut to compare project artifacts (`.ahrena/artifacts` and, when applicable, `.ahrena/framework`) with the framework in **--local** mode (vs framework in the repo) or **--remote** mode (vs latest version of the framework on GitHub, obtained via GitHub MCP). It invokes `kata-diff-artifacts` and presents the diff report.

## Usage

```
/cry-diff-artifacts [--local | --remote] [target]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `--local` | No* | Compare `.ahrena/artifacts` (and optionally `.ahrena/framework`) with the local framework (`paths.framework`). | `--local` |
| `--remote` | No* | Compare local state with the latest version of the framework on the remote; **required** to use the GitHub MCP to obtain remote content. | `--remote` |
| `target` | No | Path(s) under `paths.project_artifacts` or "all". If omitted, consider all artifacts. | `pt-BR/engineering/quality/lexis/lex-foo.md` or `all` |

*One of the modes (`--local` or `--remote`) must be specified.

## What the Command Does

1. Determines the mode (local or remote) from `--local` or `--remote`
2. Invokes `kata-diff-artifacts` with the mode and target indicated
3. Presents the diff report to the user (read-only; no files are modified)

## Prompt Template

```
Context:
- Mode: {{--local}} or {{--remote}}
- Target: {{target}} (or all artifacts in .ahrena/artifacts/)

Task:
Execute kata-diff-artifacts in the indicated mode. In remote mode, use
the GitHub MCP to obtain the state of the framework on the remote.

Output format:
Report with artifacts only in artifacts, only in the framework (local or remote),
and those that differ (with diff indication). No changes to files.
```

## Invocation Examples

**Compare with the local framework:**

```
/cry-diff-artifacts --local
```

**Compare with the latest version on the remote (via GitHub MCP):**

```
/cry-diff-artifacts --remote
```

**Compare a specific artifact with the local framework:**

```
/cry-diff-artifacts --local pt-BR/engineering/quality/lexis/lex-code-review.md
```

## Constraints

- Read-only; the command does not modify `.ahrena/` or `framework/`.
- In **--remote** mode, the GitHub MCP must be used.

## References

- `kata-diff-artifacts` — Procedure executed by this Cry (the Kata consults artifact flow and concepts; see Kata documentation)
