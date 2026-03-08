---
description: "Install specific version. Executing Makefile targets in the Ahrena repository"
---

# Cry: Execute Makefile

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Executing Makefile targets in the Ahrena repository

## Invocation

```
/cry-make <target> [variables]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `target` | Yes | Makefile target to execute | `install`, `bootstrap`, `clean` |
| `variables` | No | Environment variables for make | `PLATFORM=cursor VERSION=1.0.0` |

## Available Targets

| Target | Description |
|--------|-------------|
| `bootstrap` | Set up the development environment |
| `install` | Install the framework on the specified platform |
| `update` | Update an existing installation |
| `uninstall` | Remove the framework installation |
| `clean` | Clean temporary artifacts |

## Usage Examples

```
# Install for Cursor
/cry-make install PLATFORM=cursor

# Bootstrap the environment
/cry-make bootstrap

# Clean artifacts
/cry-make clean

# Install specific version
/cry-make install PLATFORM=cursor VERSION=1.0.0
```

## Behavior

1. Verify that the `Makefile` exists at the repository root
2. Validate that the requested target exists
3. Execute `make <target> [variables]`
4. Report the command output to the user
5. If the command fails, present the error and suggest a fix

## Note

This Cry is **specific to the Ahrena repository** — it is not a generic framework artifact. It exists to facilitate running development and maintenance tasks within the Ahrena project itself.
