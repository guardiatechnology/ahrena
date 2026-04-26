# Codex: Terminal Type (Bash and PowerShell)

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Use of bash and PowerShell in Ahrena projects

## Content

### Declaration in Directives

The terminal type may be defined in `.ahrena/.directives` in the `terminal` section:

```yaml
# ─── Terminal ─────────────────────────────────────────────────
# Shell used for commands in the project. Values: bash | powershell

terminal: powershell   # Native Windows
# terminal: bash      # Linux, macOS, WSL
```

| Value        | Typical use                         |
|-------------|--------------------------------------|
| `bash`      | Linux, macOS, WSL, Git Bash on Windows |
| `powershell`| Windows (PowerShell Core or Windows PowerShell) |

If the section does not exist, the agent infers from the operating system (e.g., Windows → PowerShell) or asks the user.

### When to Use Each Shell

| Scenario                              | Recommendation  |
|--------------------------------------|------------------|
| Project developed only on Windows    | `powershell`     |
| Project only on Linux/macOS or WSL   | `bash`           |
| Cross-platform project (CI on Linux, dev on Windows) | Define one standard (e.g., `bash` for versioned scripts; document PowerShell in README if needed) |
| Ahrena repository (framework)        | May use `bash` as default; document PowerShell alternatives when relevant |

### Common Equivalences

Frequently needed commands and concepts, side by side:

| Action             | Bash                    | PowerShell                    |
|-------------------|-------------------------|-------------------------------|
| List files        | `ls` or `find . -type f`| `Get-ChildItem` or `Get-ChildItem -Recurse` |
| Environment variable | `echo $VAR`          | `$env:VAR` or `$env:VAR`      |
| Set variable      | `export VAR=value`     | `$env:VAR = "value"`          |
| Current directory | `pwd`                  | `Get-Location` or `(Get-Location).Path` |
| Change directory  | `cd path`              | `Set-Location path` or `cd path` |
| Chain commands    | `cmd1 && cmd2`         | `cmd1; cmd2` or `cmd1; if ($?) { cmd2 }` |
| Pipe              | `cmd1 | cmd2`           | `cmd1 | cmd2`                  |
| Redirect output   | `cmd > file`           | `cmd > file` or `cmd | Out-File file` |
| Run script        | `./script.sh` or `bash script.sh` | `.\script.ps1` or `pwsh -File script.ps1` |

### Conventions for Documentation

1. **One shell per artifact:** when the project defines a single terminal type, examples in documentation (README, Katas, Cries) must use only that type.
2. **Two shells:** when both bash and PowerShell must be covered in the same document, use identified blocks (e.g., "Bash:" and "PowerShell:" or separate tabs/sections).
3. **Comments:** in scripts, use comments that indicate the shell (`# bash` or `# PowerShell`) when not obvious from context.

### Technical Constraints

- The value of `terminal` in `.ahrena/.directives` must be exactly `bash` or `powershell` (lowercase).
- Versioned scripts in the repository must be named consistently (e.g., `.sh` for bash, `.ps1` for PowerShell) and documented in the README or this Codex when needed.
