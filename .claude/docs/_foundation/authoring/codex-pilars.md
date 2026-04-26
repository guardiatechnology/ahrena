# Codex: Ahrena Pilar System

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Creation, validation, and evolution of framework artifacts

## Content

### The Five Pilars

Ahrena organizes all knowledge into five Pilars, each with a distinct role. The prefix for each Pilar is the value defined in `naming.prefixes` in `.ahrena/.directives` (keys: `lexis`, `codex`, `katas`, `warriors`, `cries`); the user or project defines it.

| Pilar | Key in naming.prefixes | Nature | Question it answers |
|-------|------------------------|--------|---------------------|
| **Lexis** | `lexis` | Unbreakable Law | "What is prohibited or required?" |
| **Codex** | `codex` | Reference Manual | "What do I need to know about this domain?" |
| **Katas** | `katas` | Repeatable Procedure | "How do I perform this task step by step?" |
| **Warriors** | `warriors` | Specialized Agent | "Who is responsible for this domain?" |
| **Cries** | `cries` | Recurring Command | "How do I invoke this action quickly?" |

### Authority Hierarchy

The Pilars have an implicit authority hierarchy:

1. **Lexis** — highest authority. No other artifact can contradict a Lexis. They are absolute.
2. **Codex** — source of truth for domain knowledge. Guides decisions.
3. **Katas** — procedures that obey Lexis and consult Codex.
4. **Warriors** — agents that follow Lexis, consult Codex, and execute Katas.
5. **Cries** — shortcuts that trigger Katas or invoke Warriors.

### Relationships Between Pilars

```
Lexis ─────────── governs ─────────► all others
Codex ─────────── informs ─────────► Katas, Warriors
Katas ─────────── executed by ─────► Warriors, generic agents
Warriors ─────── invoked by ───────► Cries, users
Cries ──────────── triggers ───────► Katas (via Warriors or directly)
```

Each Pilar can reference artifacts from other Pilars:

| Pilar | References | Referenced by |
|-------|------------|---------------|
| Lexis | — | Codex, Katas, Warriors |
| Codex | Lexis | Katas, Warriors |
| Katas | Lexis, Codex | Warriors, Cries |
| Warriors | Lexis, Codex, Katas | Cries |
| Cries | Katas, Warriors | — |

**Invocation rules (summary):**

| From (invoker) | May invoke / access |
|----------------|---------------------|
| Cry | Only Kata(s) and/or Warrior(s) |
| Warrior | Kata(s); may consult Lexis and Codex |
| Orchestrator Warrior | Own Kata(s) **and** may delegate phases to other Warriors (via checkpoint handoff) |
| Kata | No artifact as "invocation"; applies Lexis and consults Codex |

### Orchestrator Warrior (special type)

An **Orchestrator Warrior** is a Warrior whose role is to coordinate a multi-phase flow that involves other specialist Warriors. Unlike a regular Warrior, it may delegate specific phases to other Warriors via handoff documented in `.ahrena/workflow/.../checkpoint.md`.

**Example:** `warrior-athena` (clade `engineering/workflow/`) orchestrates the 7-phase Issue-Driven Development flow, delegating:
- Phase 3 (API) → `warrior-daedalus`
- Phase 3 (events) → `warrior-kronos`
- Phase 4 (Python implementation) → `warrior-apollo`

**Rules for Orchestrator Warriors:**
- Must have name, identity, and persona like any other Warrior
- Delegation occurs only through checkpoint handoff (persisted state), not direct call
- The Orchestrator Warrior remains responsible for the global integrity of the flow, even during delegation
- Delegation must be explicitly documented in the "Delegated warriors" section of the Warrior itself

This formalization avoids uncontrolled chaining between Warriors and preserves clarity of responsibilities.

### Creation Kit

For the framework to be self-sufficient, each Pilar has a **Creation Kit** composed of:

| Piece | Pilar | Function |
|-------|-------|----------|
| Pilar Codex | Codex | Knowledge about what it is and how to write it well |
| Creation Kata | Kata | Step-by-step procedure to create a new artifact |
| Invocation Cry | Cry | Quick shortcut to trigger creation |

The execution chain is:

```
/cry-new-{pilar} → kata-create-{pilar} → codex-{pilar} + template + lexis
```

### How to Decide Which Pilar to Use

| Situation | Pilar | Justification |
|-----------|-------|---------------|
| Need to establish an absolute rule that no one can violate | **Lexis** | Laws do not admit exceptions |
| Need to document domain knowledge for reference | **Codex** | Structured knowledge base |
| Need to standardize how a recurring task is performed | **Kata** | Procedure with inputs, steps, and outputs |
| Need a dedicated agent with identity and scope | **Warrior** | Specialist with persona and responsibilities |
| Need a quick shortcut for an everyday action | **Cry** | Quick invocation of 1-2 steps |

Refinement questions:

- **Is it an absolute constraint?** → Lexis
- **Is it knowledge for reference?** → Codex
- **Is it a multi-step procedure?** → Kata
- **Does it need a persona and ongoing scope?** → Warrior
- **Is it a simple and quick invocation?** → Cry

### Standards and Conventions

| Aspect | Standard | Example |
|--------|----------|---------|
| File naming | `{prefix}-{name}.md` (prefix from `naming.prefixes`) | Per `.directives` |
| Casing | kebab-case | `codex-framework-language.md` |
| Addressing | `{lang}/{clade}/{subclade}/{pilar}/{file}` | `pt-BR/engineering/quality/lexis/lex-code-review.md` |
| Dual creation | framework (`.md`) + IDE (platform format) | `.md` + `.mdc` (Cursor) |

### Technical Constraints

- Every artifact **MUST** follow the official template for its Pilar (`paths.samples` in `.directives`)
- Every artifact **MUST** exist in the languages defined in `language.i18n`
- The default language (`language.default`) is the source of truth
- File names use the Pilar prefix defined in `naming.prefixes` and kebab-case
- Canonical terms (Lexis, Codex, Katas, Warriors, Cries, Clade, Subclade, Pilar) are never translated

---

### Artifact validation

Always consult `lex-pilars` as the Law; the criteria below operationalize validation.

**How to validate:**

1. **Identify the intended Pilar** of the artifact (by name, directory, or author statement).
2. **Consult `lex-pilars`** for the unbreakable rules of that Pilar.
3. **Apply the checklist** below for the corresponding Pilar.
4. **Verify invocation relationships:** if the artifact is a Cry, confirm it only invokes Kata(s) and/or Warrior(s); if a Kata, confirm it applies Lexis and Codex; if a Warrior, confirm it orchestrates Katas.

#### Lexis

**Definition in one sentence:** Lexis is an unbreakable law that governs the framework; it admits no exception.

| Criterion | Required |
|-----------|----------|
| File name uses the prefix defined in `naming.prefixes.lexis` (consult `.directives`) and kebab-case | Yes |
| Contains **Law** section with imperative statement (MUST/MUST NOT) | Yes |
| Contains **Scope** and **Exceptions: None** (or equivalent) | Yes |
| Structure follows official template (paths.samples.lexis) | Yes |
| Not invoked by Cry as "action" — Cry invokes Kata/Warrior that consult Lexis | Yes |

**Non-compliance:** Lexis file that describes recommendation instead of obligation; Lexis with exception clause; Cry whose flow includes "invoke" or "execute" a Lexis directly.

**Valid example:** `lex-directives` — states that every agent MUST read `.ahrena/.directives`; no exceptions; consulted by other artifacts, not invoked by Cry.

#### Codex

**Definition in one sentence:** Codex is a reference manual that organizes knowledge to guide decisions; it is consulted, not executed.

| Criterion | Required |
|-----------|----------|
| File name uses the prefix defined in `naming.prefixes.codex` (consult `.directives`) and kebab-case | Yes |
| Contains **Overview**, **Context**, and **Content** (or template equivalent) | Yes |
| Nature is reference/consultation; does not describe step-by-step execution as main focus | Yes |
| Structure follows official template (paths.samples.codex) | Yes |
| Not invoked by Cry as "action" — Cry invokes Kata/Warrior that consult Codex | Yes |

**Non-compliance:** Codex artifact that is in practice a numbered procedure (should be Kata); Cry that "reads" or "applies" a Codex directly as sole action instead of invoking a Kata/Warrior.

**Valid example:** `codex-lexis` — manual on how to write good Lexis; consulted by `kata-create-lexis`; not invoked by Cry.

#### Katas

**Definition in one sentence:** Kata is a repeatable procedure that applies Lexis and consults Codex to execute a task with defined inputs, steps, and outputs.

| Criterion | Required |
|-----------|----------|
| File name uses the prefix defined in `naming.prefixes.katas` (consult `.directives`) and kebab-case | Yes |
| Contains objective, application context, inputs, process (steps), and outputs (or template equivalent) | Yes |
| References applicable Lexis and/or Codex in References section or body | Yes |
| Invoked by Cries and/or Warriors; does not invoke another Kata directly as "command" (Warrior orchestrates multiple Katas) | Yes |
| Structure follows official template (paths.samples.katas) | Yes |

**Non-compliance:** Kata artifact without clear steps or without reference to Lex/Codex; Cry that executes detailed logic without delegating to a Kata.

**Valid example:** `kata-create-lexis` — numbered steps; consults `codex-lexis` and template; invoked by `cry-new-lex`.

#### Warriors

**Definition in one sentence:** Warrior is a specialized agent that orchestrates one or more Katas and may consult Lexis and Codex; has defined identity (persona) and scope.

| Criterion | Required |
|-----------|----------|
| File name uses the prefix defined in `naming.prefixes.warriors` (consult `.directives`) and kebab-case | Yes |
| Contains identity (name, domain), responsibilities, and Katas it orchestrates (or template equivalent) | Yes |
| References at least one Lexis (typically `lex-directives`) and applicable Codex/Katas | Yes |
| Invoked by Cries or users; orchestrates Katas (does not replace the definition of a Kata) | Yes |
| Structure follows official template (paths.samples.warriors) | Yes |

**Non-compliance:** Warrior artifact that does not orchestrate any Kata; Cry that invokes a non-existent Warrior or describes logic that should be in a Kata.

**Valid example:** `warrior-translator` — orchestrates `kata-translate`; consults Lexis and Codex for i18n; invoked by `cry-translate`.

#### Cries

**Definition in one sentence:** Cry is a high-level execution command that invokes only Katas and/or Warriors; it never invokes Lexis nor accesses Codex directly.

| Criterion | Required |
|-----------|----------|
| File name uses the prefix defined in `naming.prefixes.cries` (consult `.directives`) and kebab-case | Yes |
| Clearly documents which Kata and/or Warrior(s) is/are invoked | Yes |
| Does not contain instruction to "invoke" or "execute" a Lexis | Yes |
| Does not contain instruction to "apply" or "read" a Codex as the command's sole action (Codex is consulted by the invoked Kata/Warrior) | Yes |
| If it invokes multiple Katas, there is a Warrior that orchestrates those Katas or the Cry describes the order and delegates to a Warrior | Yes |
| Structure follows official template (paths.samples.cries) | Yes |

**Non-compliance:** Cry whose prompt says "read lex-X and apply"; Cry that "consult codex-Y and do X" without invoking a Kata or Warrior that encapsulates that consultation and action.

**Valid example:** `cry-new-lex` — invokes `kata-create-lexis`; the Kata in turn consults `codex-lexis` and Lexis. The Cry does not access Codex or Lexis directly.

---

### Project Artifacts (.ahrena)

Artifacts can be created first in the **project space** (`.ahrena/artifacts/`), specific to that repository. This allows iteration and validation before incorporating them into the canonical framework.

| Aspect | Project (`.ahrena/artifacts/`) | Framework (`framework/`) |
|--------|--------------------------------|---------------------------|
| **Use** | Project-specific; local validation | Part of the Ahrena repository; shared |
| **Structure** | Same as framework: `{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.md` | `framework/{lang}/{clade}/{subclade}/{pilar}/` |
| **Languages** | May exist only in the default language; on Push, others are generated if missing | **MUST** exist in all languages in `language.i18n` |
| **When to create here** | Rules or procedures still under validation; artifacts that may never go to the framework | Stable, approved artifacts for the framework |

**Recommended flow:**

1. **Create in project:** use the creation Katas (`kata-create-lexis`, `kata-create-codex`, etc.) with destination **project** — the artifact is saved under `.ahrena/artifacts/{lang}/{clade}/{subclade}/{pilar}/`.
2. **Sync .cursor local:** run `python .ahrena/update.py --sync-cursor` (or `make sync-cursor`). The update regenerates `.cursor/` from `.ahrena/framework/` and `.ahrena/artifacts/`.
3. **Validate and compare (optional):** use `kata-diff-artifacts --local` to see differences between `.ahrena/artifacts` and local `framework/`; use `kata-diff-artifacts --remote` to compare with the latest version of the framework on the remote.
4. **Push to framework:** run `kata-push-to-framework` (or `cry-push-to-framework`) with **--local** (copy to `framework/` in the current repo) or **--remote** (sync with the framework repository on GitHub).
5. **Update installation:** run `python .ahrena/update.py` (and optionally `--sync-cursor`) to bring in the latest version of the framework.

**Push: local and remote mode**

- **Local:** the current repo contains (or has access to) the `framework/` folder. Push = copy `.ahrena/artifacts/` to `paths.framework`, complete i18n, and optionally remove from the project. No network use.
- **Remote:** in a consumer project, the framework lives on GitHub. Push = send changes to the framework repository using the **GitHub MCP** (branch, push, open PR). The agent **MUST** use the GitHub MCP tools for all remote operations.

The canonical path for the project space is defined in `paths.project_artifacts` in `.ahrena/.directives` (default value: `.ahrena/artifacts/`).
