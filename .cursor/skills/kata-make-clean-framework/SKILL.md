---
name: kata-make-clean-framework
description: "Clean framework (Make clean). Removal of files installed by Ahrena (without confirmation) via the Makefile target clean"
---

# Kata: Clean framework (Make clean)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Removal of files installed by Ahrena (without confirmation) via the Makefile target `clean`

## Workflow

```
Progress:
- [ ] 1. Consult codex-make (equivalence without Make for clean)
- [ ] 2. Verify .ahrena/install.py (used for --clean)
- [ ] 3. Determine terminal
- [ ] 4. Run clean (make or equivalent)
- [ ] 5. Report result
```

### Step 1: Consult codex-make

1. Read `codex-make` (target `clean` and **Equivalence without Make** section)
2. Identify the command: `make clean [variables]` or `python .ahrena/install.py --target . --clean`

### Step 2: Verify .ahrena/install.py

1. For clean via equivalent: the `install.py` script with `--clean` removes the files; if `.ahrena/` was already removed, the command may fail — in that case, inform that it is already clean
2. If `make` is available, the Makefile calls `.ahrena/install.py --clean`; therefore `.ahrena/install.py` must exist before clean (or the Makefile is at the repo root)

### Step 3: Determine terminal

1. Read `.ahrena/.directives` (section `terminal`) per `lex-terminal-type`; if missing, infer from OS

### Step 4: Run clean

1. If `make` is available: run `make clean [variables]` in the project directory
2. If `make` is not available: run `python .ahrena/install.py --target <TARGET> --clean` per codex-make
3. Capture output and exit code

### Step 5: Report result

1. Present the output to the user; on failure, indicate the error and suggest a fix

## Outputs

| Output | Format |
|--------|--------|
| Success | Output of the clean command (confirmation of removal) |
| Failure | Error message and suggested fix |
