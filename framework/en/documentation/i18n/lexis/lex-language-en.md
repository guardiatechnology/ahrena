# Lexis: Rules for Translating to English

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Technical documentation translation to English (en)

## Purpose

This Lexis defines the specific rules for translating technical documentation **to English (en)**. It complements `lex-language` (cross-cutting rules) with linguistic and stylistic particularities of technical English.

## Law

> **Every translation to English MUST follow the cross-cutting rules from `lex-language` AND the specific rules defined in this Lexis.**

## Rules

### 1. English variant

Use **American English** as the standard. Maintain consistency throughout:
- "color" (not "colour")
- "organization" (not "organisation")
- "analyze" (not "analyse")

### 2. Voice and tense

Use **active voice** and **present tense** in instructions:
- "The agent reads the directives" (not "The directives are read by the agent")
- "Run the command" (not "The command should be run")
- "Create the file" (not "The file is to be created")

### 3. Conciseness

Prioritize **short, direct sentences**:
- Eliminate redundancy ("in order to" → "to")
- Avoid circumlocutions ("it is important to note that" → omit)
- One idea per sentence when possible

### 4. Industry-standard terminology

| Prefer | Avoid |
|--------|-------|
| execute | perform/carry out |
| create | generate/produce (generic) |
| delete | remove/eliminate (technical action) |
| configure | set up (formal context) |
| validate | verify/check (compliance context) |

### 5. Tone

**Professional-neutral** tone: clear, precise, no colloquial language.
- Avoid contractions in formal documentation ("do not" instead of "don't")
- Avoid slang and informal expressions
- Maintain consistent register throughout

### 6. Modal verbs (RFC 2119)

| Modal | Meaning |
|-------|---------|
| MUST | Required — no exception |
| MUST NOT | Prohibited — no exception |
| SHOULD | Recommended — justified exceptions |
| SHOULD NOT | Not recommended — justified exceptions |
| MAY | Optional |

### 7. Common pitfalls when translating from pt-BR/es

| Common mistake | Correct |
|----------------|---------|
| "realize" (≠ realizar) | "perform" or "carry out" |
| "actually" (≠ atualmente) | "currently" |
| "pretend" (≠ pretender) | "intend" |
| "library" (≠ livraria) | "bookstore" (livraria) / "library" (biblioteca) |

## Scope

- **Applies to:** every translation targeting English (en)
- **Bound agents:** `warrior-translator` and any agent translating to English
- **Exceptions:** None. Lexis do not admit exceptions.

## Consequences of Violation

1. **Inconsistent translation:** text that does not follow the rules of this Lexis may mix voice, use false cognates (e.g. "realize" for "perform"), or deviate from American English.
2. **Rejection in review:** translations to English that violate the rules must be corrected before being accepted into the framework.
3. **Remediation:** the agent must consult `codex-language-en` and this Lexis and reapply the rules to the translated text.

## Examples

### Correct

- "The agent **MUST** consult the .directives." (active voice, MUST per RFC 2119)
- "Use the defined workflow." (concise; "workflow" kept in English when standard)

### Incorrect

- "The directives are read by the agent" (prefer active: "The agent reads the directives")
- "Actually, the user must perform the action" ("actually" ≠ "atualmente"; use "Currently" if that is the meaning)
- "The library sells books" when meaning "bookstore" (library = biblioteca; bookstore = livraria)

## References

- `lex-language` — Cross-cutting rules (this Lexis complements)
- `codex-language-en` — Detailed guide for English translation
