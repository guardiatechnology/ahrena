# Kata: Update Framework (Make update)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Updating the Ahrena framework installation via the Makefile `update` target

## Objective

Update the Ahrena framework installation in the project (remote or local) by running the Makefile `update` target — or the equivalent PowerShell/Python command when `make` is not available. Supports variables TARGET, SOURCE, LOCAL, VERSION, REPO (see `codex-make`).

## When to Use

- When the user invokes `/cry-make update` (with or without variables)
- When the latest version of the framework needs to be applied (remote or from the local development environment)

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Variables | No | E.g. `TARGET=.`, `SOURCE=../ahrena`, `LOCAL=1`, `VERSION=main`, `REPO=...`. See `codex-make` for the full list |

## Workflow

```
Progress:
- [ ] 1. Consult codex-make (variables and equivalence without Make for update)
- [ ] 2. Verify .ahrena/update.py
- [ ] 3. Determine terminal
- [ ] 4. Run update (make or equivalent)
- [ ] 5. Report result
```

### Step 1: Consult codex-make

1. Read `codex-make` (variables and **Equivalence without Make** section) for the `update` target
2. Identify the command to run based on the variables (remote vs LOCAL/SOURCE)

### Step 2: Verify .ahrena/update.py

1. Verify that the project has `.ahrena/update.py` (prior Ahrena installation)
2. If it does not exist, inform that install is required first (`/cry-make install` or equivalent)

### Step 3: Determine terminal

1. Read `.ahrena/.directives` (section `terminal`) per `lex-terminal-type`; if missing, infer from OS
2. Use the type for the equivalent command (PowerShell on Windows, per codex-make)

### Step 4: Run update

1. If `make` is available: run `make update [variables]` in the project directory (or per TARGET)
2. If `make` is not available: run the command from the "Equivalence without Make" section of `codex-make` for remote or local update
3. Capture output and exit code

### Step 5: Report result

1. Present the output to the user; on failure, state the error and suggest a fix

## Outputs

| Output | Format |
|--------|--------|
| Success | Output of the update command |
| Failure | Error message and suggested fix |

## References

- `codex-make` — Variables and equivalence without Make for `update`
- `lex-terminal-type` — Terminal type
- `cry-make` — Command that may invoke this Kata (target `update`)
