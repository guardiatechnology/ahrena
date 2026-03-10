# Kata: Sync .cursor/ (Make sync-cursor)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Regenerate `.cursor/` from `.ahrena/framework/` and `.ahrena/artifacts/` via the Makefile target `sync-cursor`

## Objective

Regenerate the `.cursor/` directory (rules, skills, commands, agents) from `.ahrena/framework/` and `.ahrena/artifacts/`, **without downloading** anything from remote. Equivalent to the Makefile target `sync-cursor` — or to the equivalent PowerShell/Python command when `make` is not available.

## When to use

- When the user invokes `/cry-make sync-cursor` (with or without variables, e.g. TARGET)
- When content in `.ahrena/framework/` or `.ahrena/artifacts/` was modified and must be reflected in `.cursor/`
- After creating or editing project artifacts that should appear in Cursor

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Variables | No | E.g. `TARGET=.`. See `codex-make` |

## Workflow

```
Progress:
- [ ] 1. Consult codex-make (equivalence without Make for sync-cursor)
- [ ] 2. Verify .ahrena/update.py and .ahrena/.directives
- [ ] 3. Determine terminal
- [ ] 4. Run sync-cursor (make or equivalent)
- [ ] 5. Report result
```

### Step 1: Consult codex-make

1. Read `codex-make` (target `sync-cursor` and **Equivalence without Make** section)
2. Identify the command: `make sync-cursor [variables]` or `python .ahrena/update.py --target . --sync-cursor`

### Step 2: Verify .ahrena/update.py and .ahrena/.directives

1. Verify the project has `.ahrena/update.py` and `.ahrena/.directives` (prior Ahrena installation)
2. If they do not exist, inform that installation is required first (`/cry-make install` or bootstrap)

### Step 3: Determine terminal

1. Read `.ahrena/.directives` (section `terminal`) per `lex-terminal-type`; if missing, infer from OS

### Step 4: Run sync-cursor

1. If `make` is available: run `make sync-cursor [variables]` in the project directory
2. If `make` is not available: run `python .ahrena/update.py --target <TARGET> --sync-cursor` per codex-make
3. Capture output and exit code

### Step 5: Report result

1. Present the output to the user; on failure, indicate the error and suggest a fix

## Outputs

| Output | Format |
|--------|--------|
| Success | Output of the sync-cursor command |
| Failure | Error message and suggested fix |

## References

- `codex-make` — Target sync-cursor and equivalence without Make
- `lex-terminal-type` — Terminal type
- `cry-make` — Command that may invoke this Kata (target `sync-cursor`)
