# Lexis: Canonical Definition of the Pilars

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Structure and validation of Ahrena framework artifacts

## Purpose

Ahrena organizes all knowledge into five Pilars — Lexis, Codex, Katas, Warriors, and Cries. For the framework to be self-contained and self-validating, the definitions and rules of each Pilar must be explicit and unbreakable. Without a Law that defines what each Pilar is and what each may or may not do, there is no objective criterion to validate artifacts or to ensure consistency across creation, invocation, and evolution of the framework.

This Lexis exists to establish the **canonical definitions and rules of the five Pilars**, so that every artifact can be validated against it and every invocation respects the hierarchy and relationships between Pilars.

## Law

> **Every artifact of the Ahrena framework MUST belong to exactly one Pilar and MUST satisfy the definition and canonical rules of that Pilar established in this Lexis. Every invocation between artifacts MUST respect the invocation rules defined in this Lexis.**

### Pilar identification by prefix

The reliable way to identify whether an artifact is Lexis, Codex, Kata, Warrior, or Cry is **to observe the prefix defined in the directives**: the agent MUST consult `naming.prefixes` in `.ahrena/.directives` and use the values configured there (keys `lexis`, `codex`, `katas`, `warriors`, `cries`) to validate names and classify artifacts. The agent MUST NOT assume that prefixes will always be fixed values (e.g. `lex-`, `codex-`); the user or project defines them in `.directives`.

## Rules per Pilar

### 1. Lexis

- **Definition:** Lexis is an unbreakable law; it admits no exception.
- **Mandatory prefix:** the value defined in `naming.prefixes.lexis` in `.ahrena/.directives`. The user or project defines the prefix; the agent identifies that an artifact is Lexis by checking whether the file name uses the prefix configured for that Pilar.
- **Structure:** MUST follow the official template of the Pilar (`paths.samples.lexis` in `.directives`).
- **Authority:** Lexis governs all other Pilars; no artifact may contradict a Lexis.
- **Invocation:** Lexis is not invoked by Cries; it is consulted by Codex, Katas, and Warriors.

### 2. Codex

- **Definition:** Codex is a reference manual; it organizes knowledge to guide decisions.
- **Mandatory prefix:** the value defined in `naming.prefixes.codex` in `.ahrena/.directives`. Pilar identification is by the configured prefix, not a fixed value.
- **Structure:** MUST follow the official template of the Pilar (`paths.samples.codex`).
- **Role:** Informs Katas and Warriors; it is not executed directly (not invoked as a procedure).
- **Invocation:** Codex is not invoked by Cries; it is consulted by Katas and Warriors.

### 3. Katas

- **Definition:** Kata is a repeatable procedure (skill) that applies Lexis and consults Codex to execute a clear, reproducible task.
- **Mandatory prefix:** the value defined in `naming.prefixes.katas` in `.ahrena/.directives`. Pilar identification is by the configured prefix.
- **Structure:** MUST follow the official template of the Pilar (`paths.samples.katas`).
- **Dependency:** Kata applies Lexis and consults Codex; it must not contain logic that contradicts Lexis or ignore applicable Codex.
- **Invocation:** Kata is invoked by Cries (directly or via Warrior) or by Warriors.

### 4. Warriors

- **Definition:** Warrior is a specialized agent that orchestrates one or more Katas and may consult Lexis and Codex.
- **Mandatory prefix:** the value defined in `naming.prefixes.warriors` in `.ahrena/.directives`. Pilar identification is by the configured prefix.
- **Structure:** MUST follow the official template of the Pilar (`paths.samples.warriors`).
- **Role:** Orchestrates Katas (selects, orders, combines results); may consult Lexis and Codex.
- **Invocation:** Warrior is invoked by Cries or by users; it is not invoked by another Warrior as a formal artifact (unless the Cry instructs the agent to assume the role of another Warrior).

### 5. Cries

- **Definition:** Cry is a high-level execution command that activates skills or agents.
- **Mandatory prefix:** the value defined in `naming.prefixes.cries` in `.ahrena/.directives`. Pilar identification is by the configured prefix.
- **Structure:** MUST follow the official template of the Pilar (`paths.samples.cries`).
- **Invocation rule (unbreakable):** Cry **MUST NOT** invoke Lexis. Cry **MUST NOT** access Codex directly. Cry **ONLY** invokes Katas and/or Warriors.
- **Relationship:** A Cry may invoke one Kata (one-to-one) or one or more Warriors (one-to-many). If a Cry needs to invoke multiple Katas, a Warrior that orchestrates those Katas MUST exist.

## Authority hierarchy

1. **Lexis** — highest authority; cannot be contradicted.
2. **Codex** — source of truth for knowledge; guides Katas and Warriors.
3. **Katas** — execute by applying Lexis and consulting Codex.
4. **Warriors** — orchestrate Katas; consult Lexis and Codex.
5. **Cries** — trigger Katas or Warriors; never Lexis nor Codex.

## Scope

- **Applies to:** every artifact created or maintained in the Ahrena framework and every invocation chain (Cry → Warrior/Kata → Kata → Lex/Codex).
- **Bound agents:** all Warriors and generic agents that create, validate, or invoke framework artifacts.
- **Exceptions:** None. Lexis admit no exceptions.

## Consequences of Violation

1. **Invalid artifact:** an artifact that does not satisfy the definition of its Pilar must not be accepted into the framework; it must be corrected or reclassified.
2. **Invalid invocation:** a Cry that invokes Lexis or accesses Codex directly violates the Law; the Cry design must be corrected to delegate to a Kata or Warrior.
3. **Remediation:** the agent or reviewer must consult `lex-pilars` and `codex-pilars` to validate the artifact and the invocation chain and correct deviations.

## Examples

### Correct

- Cry `cry-translate` invokes the Warrior `warrior-translator`, which executes the Kata `kata-translate`; the Kata consults Lexis and Codex for translation.
- Cry `cry-new-lex` invokes the Kata `kata-create-lexis`; the Kata consults `codex-lexis` and the Lexis template; there is no invocation of Lexis by the Cry.

### Incorrect

- Cry whose prompt instructs the agent to "read lex-directives and apply" without invoking a Kata or Warrior that encapsulates that procedure — reading the Lex is use by the Kata/Warrior, not "invocation" of the Cry to the Lex; the Cry must invoke a Kata or Warrior. (If the Cry only triggers a Kata that in turn consults Lexis, it is correct.)
- Artifact named `guide-api.md` without the Codex Pilar prefix (defined in `naming.prefixes.codex`) in the codex directory — violates naming.

## Automated Validation

- **Tool:** verification by the agent or reviewer based on `lex-pilars` and `codex-pilars`; possible future extension with a naming and reference validation script.
- **When:** at artifact creation (kata-create-*), at PR review, and when validating Cries.
- **Metric:** 0 artifacts outside the definition of their Pilar; 0 Cries that invoke Lexis or access Codex directly.

## References

- `codex-pilars` — Central reference for Pilars and validation checklists per Pilar
- `codex-pilars` — Central reference for the Pilar system and relationships
- `.ahrena/.directives` — Prefixes and paths (naming.prefixes, paths.samples)
- `lex-template-usage` — Mandatory use of the template per Pilar
