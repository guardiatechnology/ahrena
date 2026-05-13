New Tech Task. Create a tech task issue in the repository

# Cry: New Tech Task

> **Prefix:** `cry-` | **Scope:** Create a tech task issue in the repository

## What it does

Creates a GitHub Issue using the `tech-task` template, which answers Why / What / How. Invokes `kata-contributing-issue` with type `tech-task`. Follows `lex-issue-quality` and `lex-issue-first`.

## Usage

```
/cry-new-tech-task [title]
```

## Parameters

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `title` | No | Brief task summary. If omitted, the agent asks before proceeding. |

## Examples

```
/cry-new-tech-task
/cry-new-tech-task update contributing guide with new branch naming rules
/cry-new-tech-task fix CI pipeline for Windows runners
```

## Invokes

`kata-contributing-issue` with `type: tech-task`
