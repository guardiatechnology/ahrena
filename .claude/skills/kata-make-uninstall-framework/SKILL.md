---
name: kata-make-uninstall-framework
description: "Uninstall framework (Make uninstall). Removal of the Ahrena framework installation via the Makefile target uninstall"
---

# Kata: Uninstall framework (Make uninstall)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Removal of the Ahrena framework installation via the Makefile target `uninstall`

## Workflow

```
Progress:
- [ ] 1. Consult codex-make (equivalence without Make for uninstall)
- [ ] 2. Verify .ahrena/uninstall.py
- [ ] 3. Determine terminal
- [ ] 4. Run uninstall (make or equivalent)
- [ ] 5. Report result
```

### Step 1: Consult codex-make

1. Read `codex-make` (target `uninstall` and **Equivalence without Make** section)
2. Identify the command: `make uninstall [variables]` or `python .ahrena/uninstall.py --target .` (and optionally `--force` to skip confirmation)

### Step 2: Verify .ahrena/uninstall.py

1. Verify the project has `.ahrena/uninstall.py`
2. If it does not exist, inform that Ahrena may already be removed or that the installation is incomplete

### Step 3: Determine terminal

1. Read `.ahrena/.directives` (section `terminal`) per `lex-terminal-type`; if missing, infer from OS

### Step 4: Run uninstall

1. If `make` is available: run `make uninstall [variables]` in the project directory
2. If `make` is not available: run `python .ahrena/uninstall.py --target <TARGET>` per codex-make (the script may ask for confirmation)
3. Capture output and exit code

### Step 5: Report result

1. Present the output to the user; on failure, indicate the error and suggest a fix

## Outputs

| Output | Format |
|--------|--------|
| Success | Output of the uninstall command (confirmation of removal) |
| Failure | Error message and suggested fix |
