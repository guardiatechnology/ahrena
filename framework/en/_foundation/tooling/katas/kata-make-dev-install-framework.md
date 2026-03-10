# Kata: Install Framework from Development (Make dev-install)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Installing the Ahrena framework from the current directory (repo root), target `dev-install`

## Objective

Install the Ahrena framework from the **current directory** (which must be the Ahrena repository root) by running the Makefile `dev-install` target — or the equivalent in PowerShell/Python when `make` is not available. Used by contributors who develop the framework and want to install into another project using local sources.

## When to Use

- When the user invokes `/cry-make dev-install` (with or without variables, e.g. PLATFORM, TARGET)
- When the framework needs to be installed from the local development clone (without downloading from GitHub)

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Variables | No | E.g. `PLATFORM=cursor`, `TARGET=../other-project`. See `codex-make` |

## Workflow

```
Progress:
- [ ] 1. Consult codex-make (equivalence without Make for dev-install)
- [ ] 2. Verify current directory is Ahrena repo root (framework/, scripts/)
- [ ] 3. Determine terminal
- [ ] 4. Run dev-install (make or equivalent)
- [ ] 5. Report result
```

### Step 1: Consult codex-make

1. Read `codex-make` (target `dev-install` and **Equivalence without Make** section for local install in the Ahrena repo)
2. Identify the command: `make dev-install [variables]` or `python scripts/install.py --local --target . [--platform cursor]` etc.

### Step 2: Verify Ahrena repo root

1. Confirm that `framework/` and `scripts/install.py` exist in the current directory (or working directory)
2. If they do not, inform that dev-install must be run from the Ahrena repository root

### Step 3: Determine terminal

1. Read `.ahrena/.directives` (section `terminal`) per `lex-terminal-type`; if missing, infer from OS

### Step 4: Run dev-install

1. If `make` is available: run `make dev-install [variables]` at the Ahrena repo root
2. If `make` is not available: run `python scripts/install.py --local --target <TARGET> [--platform cursor]` per codex-make (no --repo/--version)
3. Capture output and exit code

### Step 5: Report result

1. Present the output to the user; on failure, state the error and suggest a fix

## Outputs

| Output | Format |
|--------|--------|
| Success | Output of the dev-install command |
| Failure | Error message and suggested fix |

## References

- `codex-make` — Target dev-install and equivalence without Make
- `lex-terminal-type` — Terminal type
- `cry-make` — Command that may invoke this Kata (target `dev-install`)
