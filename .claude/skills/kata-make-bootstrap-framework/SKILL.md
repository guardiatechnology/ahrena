---
name: kata-make-bootstrap-framework
description: "Bootstrap the framework (Make bootstrap). First-time installation of the Ahrena framework via the Makefile target bootstrap"
---

# Kata: Bootstrap the framework (Make bootstrap)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** First-time installation of the Ahrena framework via the Makefile target `bootstrap`

## Workflow

```
Progress:
- [ ] 1. Consult codex-make (equivalence without Make for bootstrap)
- [ ] 2. Determine terminal
- [ ] 3. Run bootstrap (make or equivalent)
- [ ] 4. Report result
```

### Step 1: Consult codex-make

1. Read `codex-make` (target `bootstrap` and **Equivalence without Make** section for bootstrap)
2. Identify the command: `make bootstrap [variables]` or the PowerShell one-liner (download install.py, run, remove)

### Step 2: Determine terminal

1. Read `.ahrena/.directives` (section `terminal`) per `lex-terminal-type`; if missing, infer from OS (for bootstrap, `.ahrena/` may not exist yet; infer from OS)

### Step 3: Run bootstrap

1. If `make` is available: run `make bootstrap [variables]` in the project directory
2. If `make` is not available: run the command from the "Equivalence without Make" section of `codex-make` for bootstrap (download install.py from GitHub, run with variables, remove the script)
3. Capture output and exit code

### Step 4: Report result

1. Present the output to the user; on failure, indicate the error and suggest a fix

## Outputs

| Output | Format |
|--------|--------|
| Success | Output of the bootstrap command |
| Failure | Error message and suggested fix |
