# Lexis: Mandatory Tone and Writing Style

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Production of artifacts and communication in the Ahrena context

## Law

> **Every agent MUST apply the tone and writing-style guidelines defined in `naming.tone_and_writing_style` in the `.ahrena/.directives` file when producing artifacts (Lexis, Codex, Katas, Warriors, Cries), documentation, and communication in the Ahrena context. If the section does not exist, the agent MUST adopt a direct, strategic tone based on clarity and purpose.**

## Rules

### 1. Consulting the guidelines

When producing text in the Ahrena context, the agent **MUST**:

1. Consult `.ahrena/.directives` (per `lex-directives`).
2. Check whether the section `naming.tone_and_writing_style` exists.
3. If it exists, internalize each item in the list and apply it when drafting or reviewing content.
4. If it does not exist, adopt equivalent principles: direct and strategic style, clarity, data, and purpose; avoid adornments and abstractions that stray from the essential.

### 2. Scope of application

Tone and style apply to:

- Content of framework artifacts (Law, Purpose, Content, Examples, etc.).
- Documentation produced in the project context (README, ADRs, code comments when they are documentation).
- Communication produced by the agent in response to requests in the Ahrena context (responses, summaries, instructions).

They do not apply to source code (variables, functions) except when the user requests that comments or inline documentation follow the same style.

### 3. No modification of the section without authorization

The agent **MUST NOT** add or change the section `naming.tone_and_writing_style` in `.ahrena/.directives` without explicit user request.

## Examples

### Aligned with tone (typical guidelines)

- Direct, purposeful sentence: "Every artifact MUST use the Pilar prefix defined in `.directives`."
- Avoid adornments: prefer "The Law establishes the obligation" to "It is important to note that the Law establishes the obligation."
- Support with logical structure: use Why/What/How or Problem/Cause/Solution when it makes sense.

### Misaligned

- Vague: "Artifacts should use the correct prefix."
- Buzzword without meaning: "Disruptive, innovative solution."
- Excessive dashes or colons to contextualize: "The framework — which is very important — must be used — always — as follows:"

## Automated Validation

- **Tool:** human review or by the agent itself with a checklist based on `codex-tone`.
- **When:** when creating or reviewing artifacts and when delivering communication.
- **Metric:** produced content must comply with the guidelines in `tone_and_writing_style` when the section exists.
