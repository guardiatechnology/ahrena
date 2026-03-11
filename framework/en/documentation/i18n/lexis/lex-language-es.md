# Lexis: Rules for Translating to Spanish

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Technical documentation translation to Spanish (es)

## Purpose

This Lexis defines the specific rules for translating technical documentation **to neutral Spanish (es)**. It complements `lex-language` (cross-cutting rules) with linguistic, stylistic, and cultural particularities of Spanish.

## Law

> **Every translation to Spanish MUST follow the cross-cutting rules from `lex-language` AND the specific rules defined in this Lexis.**

## Rules

### 1. Spanish variant

Use **neutral Spanish** — no regionalisms from Spain, Mexico, Argentina, or any other country. The goal is to produce documentation understandable by any Spanish speaker.

### 2. Formality

Maintain implicit formality appropriate for technical documentation:
- Impersonal voice when appropriate ("Se debe configurar..." instead of "Tú debes configurar...")
- Avoid colloquial language
- Professional and accessible tone

### 3. Form of address consistency

**DO NOT** mix "tú" and "usted" in the same document. Choose one and maintain consistency. For technical documentation, prefer impersonal constructions.

### 4. False cognates with pt-BR

Special attention to false cognates between pt-BR and Spanish:

| Portuguese | Spanish (CORRECT) | False cognate (INCORRECT) |
|------------|-------------------|---------------------------|
| esquisito (strange) | extraño, raro | exquisito (= exquisite) |
| polvo (octopus) | pulpo | polvo (= dust) |
| largo (wide) | amplio, ancho | largo (= long) |
| escritório (office) | oficina | escritorio (= desk) |
| sobrenome (surname) | apellido | sobrenombre (= nickname) |

### 5. Technical terms in English

Universal technical terms **MUST** remain in English:
- commit, merge, branch, pull request, framework, deploy
- When to translate: workflow → flujo de trabajo, output → salida, input → entrada

### 6. Modal verbs

| English | Spanish |
|---------|---------|
| MUST | DEBE |
| MUST NOT | NO DEBE / NO PUEDE |
| SHOULD | DEBERÍA / SE RECOMIENDA |
| MAY | PUEDE |

### 7. Punctuation and spelling

- Use opening question (¿) and exclamation (¡) marks correctly
- Accents following RAE rules
- Pay attention to current norms on "solo" (no accent per current standard)

## Scope

- **Applies to:** every translation targeting Spanish (es)
- **Bound agents:** `warrior-translator` and any agent translating to Spanish
- **Exceptions:** None. Lexis do not admit exceptions.

## Consequences of Violation

1. **Inconsistent translation:** text that does not follow the rules of this Lexis may mix formality, use false cognates, or deviate from neutral Spanish.
2. **Rejection in review:** translations to Spanish that violate the rules must be corrected before being accepted into the framework.
3. **Remediation:** the agent must consult `codex-language-es` and this Lexis and reapply the rules to the translated text.

## Examples

### Correct

- "The agent **MUST** consult the .directives." (impersonal voice, MUST in capitals)
- "The defined workflow should be used." (workflow → flujo de trabajo in Spanish; impersonal)

### Incorrect

- "The agent has to consult the .directives." (avoid "has to"; use "MUST")
- "Configure the escritorio" when the context is "office" (use "oficina", not "escritorio")
- Mixing "tú" and "usted" in the same document.

## References

- `lex-language` — Cross-cutting rules (this Lexis complements)
- `codex-language-es` — Detailed guide for Spanish translation
