# Lexis: Mandatory Use of Defined Terminal Type

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Execution of shell commands by AI agents

## Law

> **Every agent MUST use the terminal type (bash or PowerShell) defined in `.ahrena/.directives` when executing or proposing shell commands. If the directive does not exist, the agent MUST infer the type from the user's operating system (e.g., Windows → PowerShell; Linux/macOS → bash) or ask the user.**

## Rules

### 1. Consulting the canonical directive

When executing or suggesting terminal commands, the agent **MUST**:

1. Consult `.ahrena/.directives` (per `lex-directives`).
2. Check whether the `terminal` section exists with value `bash` or `powershell`.
3. Use that value as the source of truth for command syntax and interpreter.

### 2. Behavior when the section does not exist

If the `terminal` section is not present in `.ahrena/.directives`:

- The agent **MUST** infer from context when possible (e.g., information that the environment is Windows → PowerShell; Linux or macOS → bash).
- If the context is unclear, the agent **MUST** ask the user which terminal type to use before executing or generating commands that depend on the shell.

### 3. Consistency within the session

Once the terminal type is defined (by directive, inference, or user response), the agent **MUST** keep that type for the entire session when proposing or executing commands, unless the user explicitly instructs otherwise.

### 4. Documentation and examples

In artifacts that contain command examples (documentation, README, Katas, Cries), the agent **MUST** generate examples in the terminal type defined by the project or clearly indicate which shell is being used (e.g., with a comment or identified block).

### 5. No modification without authorization

The agent **MUST NOT** add or change the `terminal` section in `.ahrena/.directives` without explicit user request.

## Examples

### Correct

```
# .ahrena/.directives contains:
terminal: powershell

# Agent proposes command in PowerShell:
Get-ChildItem -Path . -Filter "*.md" | Select-Object Name
```

```
# .ahrena/.directives contains:
terminal: bash

# Agent proposes command in bash:
find . -name "*.md" -type f
```

### Incorrect

```
# User on Windows; .directives does not define terminal.
# Agent assumes bash and suggests:
find . -name "*.md"

# ❌ In native PowerShell, find does not exist as a command.
# The agent should have inferred PowerShell or asked the user.
```

## Automated Validation

- **Tool:** verification by the agent itself before executing or proposing shell commands.
- **When:** when starting command execution and when generating documentation with terminal examples.
- **Metric:** 100% of proposed or executed shell commands must respect the defined or inferred terminal type.
