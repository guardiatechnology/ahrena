# Kata: Install Framework (Make install)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Installing the Ahrena framework via the Makefile `install` target

## Objective

Install the Ahrena framework in the project (remote or local) by running the Makefile `install` target — or the equivalent PowerShell/Python command when `make` is not available. Supports variables PLATFORM, TARGET, SOURCE, LOCAL, VERSION, REPO, and others (see `codex-make`).

## When to Use

- When the user invokes `/cry-make install` (with or without variables)
- When the framework needs to be installed for the first time or reinstalled (remote or from a local clone)

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Variables | No | E.g. `PLATFORM=cursor`, `TARGET=.`, `SOURCE=../ahrena`, `LOCAL=1`, `VERSION=main`, `REPO=...`. See `codex-make` for the full list |

## Workflow

```
Progress:
- [ ] 1. Consult codex-make (variables and equivalence without Make for install)
- [ ] 2. Verify Makefile or .ahrena/install.py
- [ ] 3. Determine terminal
- [ ] 4. Run install (make or equivalent)
- [ ] 5. Report result
```

### Step 1: Consult codex-make

1. Read `codex-make` (variables and **Equivalence without Make** section) for the `install` target
2. Identify the command to run based on the variables passed (remote vs LOCAL/SOURCE)

### Step 2: Verify Makefile or .ahrena/install.py

1. If at the Ahrena repo root: verify that `Makefile` and `scripts/install.py` exist
2. If in a project that already has Ahrena: verify that `.ahrena/install.py` exists (or that `Makefile` exists at repo root for dev-install)
3. If anything is missing, inform the user and suggest a fix

### Step 3: Determine terminal

1. Read `.ahrena/.directives` (section `terminal`) per `lex-terminal-type`; if missing, infer from OS
2. Use the type to choose the equivalent command syntax (PowerShell on Windows, per codex-make)

### Step 4: Run install

1. If `make` is available: run `make install [variables]` in the correct directory (repo root or per TARGET)
2. If `make` is not available: run the command from the "Equivalence without Make" section of `codex-make` for remote install, local (in repo), or local (path), according to variables
3. Capture output and exit code

### Step 5: Report result

1. Present the output to the user; on failure, state the error and suggest a fix (e.g. equivalence without Make, path check)

## Outputs

| Output | Format |
|--------|--------|
| Success | Output of the install command |
| Failure | Error message and suggested fix |

## References

- `codex-make` — Variables and equivalence without Make for `install`
- `lex-terminal-type` — Terminal type
- `cry-make` — Command that may invoke this Kata (target `install`)
