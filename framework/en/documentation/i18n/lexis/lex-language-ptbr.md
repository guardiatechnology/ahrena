# Lexis: Rules for Translating to Brazilian Portuguese

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Technical documentation translation to pt-BR

## Purpose

This Lexis defines the specific rules for translating technical documentation **to Brazilian Portuguese (pt-BR)**. It complements `lex-language` (cross-cutting rules) with pt-BR's linguistic, stylistic, and cultural particularities.

## Law

> **Every translation to pt-BR MUST follow the cross-cutting rules from `lex-language` AND the specific rules defined in this Lexis.**

## Rules

### 1. Form of address

Use **"você"** as the form of address. Never use "tu", "vós", or overly formal forms like "Vossa Senhoria". The tone is technical yet accessible.

### 2. Standard grammar

The translation **MUST** follow standard Brazilian Portuguese grammar:
- Rigorous use of accents (é, á, ã, ç, etc.)
- Correct punctuation
- Verbal and nominal agreement
- Verbal and nominal regency

### 3. Technical terms in English

Technical terms well-established in the tech community **MUST** remain in English when there is no consolidated pt-BR equivalent:

| Keep in English | Translate |
|-----------------|-----------|
| deploy | implantar (when generic verb) |
| commit | — (never translate) |
| merge | — (never translate) |
| branch | — (never translate) |
| pull request | — (never translate) |
| framework | — (never translate) |
| workflow | fluxo de trabalho |
| output | saída |
| input | entrada |

### 4. Anglicisms

Avoid anglicisms when a consolidated pt-BR equivalent exists:
- **"excluir"** not "deletar"
- **"configurar"** not "setar"

### 5. Tone

**Formal-accessible** tone: technical without being ornate, direct without being colloquial.

### 6. Modal verbs

| English | Portuguese |
|---------|-----------|
| MUST | DEVE |
| MUST NOT | NÃO DEVE / NÃO PODE |
| SHOULD | DEVERIA / RECOMENDA-SE |
| MAY | PODE |

### 7. Formal structures

For instructions and technical documentation:
- "O agente **DEVE**..." (not "O agente tem que...")
- "É necessário..." (not "Precisa...")

## Scope

- **Applies to:** every translation targeting pt-BR
- **Bound agents:** `warrior-translator` and any agent translating to pt-BR
- **Exceptions:** None. Lexis do not admit exceptions.

## Consequences of Violation

1. **Inconsistent translation:** text that does not follow the rules of this Lexis may mix formality, use unnecessary anglicisms, or deviate from the standard norm.
2. **Rejection in review:** translations to pt-BR that violate the rules must be corrected before being accepted into the framework.
3. **Remediation:** the agent must consult `codex-language-ptbr` and this Lexis and reapply the rules to the translated text.

## Examples

### Correct

- "The agent **MUST** consult the .directives." (active voice, MUST in capitals, technical term preserved)
- "It is recommended to use the defined workflow." (workflow translated where appropriate; impersonal construction)

### Incorrect

- "The agent has to consult the .directives." (avoid "has to"; use "MUST")
- "Delete the file" (use "Exclude the file" per pt-BR convention)

## References

- `lex-language` — Cross-cutting rules (this Lexis complements)
- `codex-language-ptbr` — Detailed guide for pt-BR translation
