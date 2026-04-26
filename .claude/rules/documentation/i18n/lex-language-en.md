# Lexis: Rules for Translating to English

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Technical documentation translation to English (en)

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

## Examples

### Correct

- "The agent **MUST** consult the .directives." (active voice, MUST per RFC 2119)
- "Use the defined workflow." (concise; "workflow" kept in English when standard)

### Incorrect

- "The directives are read by the agent" (prefer active: "The agent reads the directives")
- "Actually, the user must perform the action" ("actually" ≠ "atualmente"; use "Currently" if that is the meaning)
- "The library sells books" when meaning "bookstore" (library = biblioteca; bookstore = livraria)
