Execute Makefile. Executing Makefile targets in the Ahrena repository

# Cry: Execute Makefile

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Executing Makefile targets in the Ahrena repository

## Usage

```
/cry-make <target> [variables]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `target` | Yes | Makefile target to execute | `install`, `update`, `dev-install`, `bootstrap` |
| `variables` | No | Variables for make (format `NAME=value`) | `PLATFORM=cursor`, `SOURCE=../ahrena`, `LOCAL=1` |

For the full list of targets and variables, see `codex-make`.

## Dispatch by target

| Target | Kata executed |
|--------|----------------|
| `install` | `kata-make-install-framework` |
| `update` | `kata-make-update-framework` |
| `dev-install` | `kata-make-dev-install-framework` |
| `bootstrap` | `kata-make-bootstrap-framework` |
| `sync-cursor` | `kata-make-sync-cursor` |
| `uninstall` | `kata-make-uninstall-framework` |
| `clean` | `kata-make-clean-framework` |

Targets not listed above are invalid for this Cry; inform the user and list valid targets.

## What the Command Does

1. Validates the target against the table above (targets in `codex-make`)
2. If the target is invalid: inform the user and list valid targets; do not run a kata
3. Based on the valid target, chooses the corresponding Kata (table above)
4. Runs the chosen Kata with the given variables
5. The Kata consults codex-make, verifies the environment, runs `make` or the equivalent, and reports the result
6. Presents the output to the user or the error with a suggested fix

## Prompt Template

```
Context:
- Target: {{target}}
- Variables: {{variables}} (optional)

Task:
Based on the requested target, execute the corresponding Kata:
- install → kata-make-install-framework
- update → kata-make-update-framework
- dev-install → kata-make-dev-install-framework
- bootstrap → kata-make-bootstrap-framework
- sync-cursor → kata-make-sync-cursor
- uninstall → kata-make-uninstall-framework
- clean → kata-make-clean-framework
- target not listed above → report invalid target and list valid targets (do not run a kata)

The Kata consults codex-make for valid variables and equivalence without Make
when make is not available. Report the command output or the error with a
suggested fix.

Output format:
Command output or error message with indication of how to fix.
```

## Invocation Example

**Install for Cursor:**

```
/cry-make install PLATFORM=cursor
```

**Expected output:** output of `make install PLATFORM=cursor` (or the equivalent PowerShell command if make is not available).

**Update from local:**

```
/cry-make update LOCAL=1
```
