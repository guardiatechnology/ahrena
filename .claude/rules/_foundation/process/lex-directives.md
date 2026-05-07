# Lexis: Mandatory Consultation of .directives

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** All sessions and activities of AI agents

## Law

> **Every agent MUST read and apply the instructions defined in `.ahrena/.directives` before starting any activity that produces artifacts, documentation, or communication in the Ahrena context.**

## Rules

### 1. Canonical location

The directives file **ALWAYS** resides at:

```
.ahrena/.directives
```

The `.ahrena/` directory is the canonical entry point of the framework in any project that adopts Ahrena. The agent **MUST** look for this directory at the repository root.

### 2. Mandatory read at start

When starting a session or activity, the agent **MUST**:

1. Locate the `.ahrena/` directory at the repository root.
2. Read the `.ahrena/.directives` file in full.
3. Internalize the directives as active constraints for the entire session.

If the `.ahrena/` directory or the `.directives` file does not exist, the agent **MUST** alert the user to the absence and suggest its creation.

### 3. Directives as source of truth

The directives defined in `.ahrena/.directives` **take precedence** over:

- Agent assumptions based on training or generic context.
- Undocumented implicit preferences.

When there is a conflict between a directive and a user instruction in the session, the agent **MUST** follow the user instruction but **alert** to the divergence from the canonical directive.

### 4. Application by section

The agent **MUST** apply each section of the directives to the corresponding behavior:

| Section | Application |
|---------|-------------|
| `paths` | Use canonical paths when referencing or creating framework artifacts |
| `language` | Produce documentation and artifacts in the default language (`default`) and ensure required languages (`required`) are covered when applicable |
| `naming.prefixes` | Apply the correct prefix when naming artifacts for each Pilar |
| `naming.extensions` | Use the correct extension per context (`.md` for framework, `.mdc` for Cursor) |
| `naming.casing` | Follow the defined casing convention for files and directories |
| `naming.addressing` | Follow the addressing pattern when placing artifacts in the taxonomy |
| `naming.reserved_clades` | Recognize special Clades and respect their usage rules |
| `terminal` | Consult for shell commands; use the defined type (bash or PowerShell). See `lex-terminal-type`. |
| `naming.tone_and_writing_style` | Apply tone and style when producing artifacts and communication. See `lex-tone`. |
| `stacked_prs.tool` | Select the tool used to operate Stacked Pull Requests when applicable: `vanilla` (default — plain `git` + `gh`) or `gs` (git-spice). See `codex-stacked-prs`. |
| `paths.skills_root` | Root directory for external skill projects (default `skills`). See `lex-skill-project-structure`. |
| `paths.skills_build` | Directory for skill build intermediates (default `.build`, gitignored). Consumed by `kata-build-skill` (PR 2). |
| `paths.skills_dist` | Directory for the final delivery of packaged skills (default `.dist`, committed). Consumed by `kata-package-skill` (PR 3). |

Complementary manuals for interpreting sections: `codex-directives` (file overview), `codex-paths` (canonical paths), `codex-naming` (naming conventions).

### 5. Extensibility

New sections may be added to `.directives` at any time. The agent **MUST** interpret unknown sections based on the key name and structure, applying the directive in a reasonable way. In case of ambiguity, the agent **MUST** ask the user.

### 6. No modification without authorization

The agent **MUST NOT** modify the `.directives` file without explicit user request. The directives are canonical and governed by the framework maintainer.

## Examples

### Correct

```
Agent: [Session start]
1. Locates .ahrena/ at the repository root
2. Reads .ahrena/.directives
3. Identifies:
   - Default language: pt-BR
   - Required languages: pt-BR, es, en
   - Casing: kebab-case
   - Prefix for Lexis: lex-
4. Produces artifact in pt-BR, names it lex-code-review.md,
   saves under engineering/quality/lexis/

User: Create the documentation for this feature.

Agent: Documentation created in pt-BR (default).
Do you want me to also generate the Spanish and English versions,
per the framework directives?
```

### Incorrect

```
Agent: [Session start — ignores .ahrena/.directives]

User: Create a new Lexis about logging.

Agent: Here's your new Lexis:
# Lexis: Logging
...

# ❌ The agent did not locate .ahrena/ or read .directives.
# ❌ Ignored the default language (pt-BR) defined in the directives.
# ❌ Did not consult paths.samples to find the correct template.
# ❌ Did not offer versions in the required languages.
```

## Automated Validation

- **Tool:** verification by the agent itself at the start of each session
- **When:** before any production of artifacts or formal communication
- **Metric:** 100% of sessions must have `.ahrena/.directives` consulted and applied
