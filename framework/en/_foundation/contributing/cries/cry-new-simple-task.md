# Cry: New Simple Task

> **Prefix:** `cry-` | **Scope:** Create a simple task issue in the repository

## What it does

Creates a GitHub Issue using the `simple-task` template, which answers Why / What / How. Invokes `kata-contributing-issue` with type `simple-task`. Follows `lex-issue-quality` and `lex-issue-first`.

## Usage

```
/cry-new-simple-task [title]
```

## Parameters

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `title` | No | Brief task summary. If omitted, the agent asks before proceeding. |

## Examples

```
/cry-new-simple-task
/cry-new-simple-task update contributing guide with new branch naming rules
/cry-new-simple-task fix CI pipeline for Windows runners
```

## Invokes

`kata-contributing-issue` with `type: simple-task`
