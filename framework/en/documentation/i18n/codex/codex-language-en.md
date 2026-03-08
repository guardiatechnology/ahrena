# Codex: Guide for Translating to English

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Conventions and guidance for technical translation to English (en)

## Overview

This Codex is the practical guide for translating technical documentation **to English (en)**. It complements `lex-language-en` (mandatory rules) with guidance, examples, and reference tables.

## Context

- **Domain:** Technical translation to English
- **Audience:** `warrior-translator` and agents translating to English
- **Updates:** whenever new English conventions are identified

## Content

### Technical Writing Conventions

1. **Imperative mood** for instructions: "Run the command", "Create the file"
2. **Active voice** whenever possible: "The agent reads" not "The file is read by the agent"
3. **Present tense** as default: "The system validates" not "The system will validate"
4. **One idea per sentence** — short, focused sentences

### Vocabulary Choices

| Prefer | Avoid | Reason |
|--------|-------|--------|
| Simple words | Complex synonyms | Clarity |
| Specific terms | Vague language | Precision |
| "Run X" | "You should run X" | Conciseness |
| "Create the file" | "The file needs to be created" | Active voice |
| "do not" | "don't" | Formality |
| "cannot" | "can't" | Formality |

### Formatting Patterns

| Pattern | Correct | Incorrect |
|---------|---------|-----------|
| Instructions | "Run `npm install`." | "You should run `npm install`." |
| Obligations | "The agent **MUST** validate." | "The agent has to validate." |
| Conditions | "If the file exists, read it." | "In the event that the file exists, you should proceed to read it." |
| Lists | Parallelism across items | Mixed styles |

### Common Pitfalls from pt-BR

| Mistake | Correction | Example |
|---------|-----------|---------|
| "realize" (≠ realizar) | "perform", "carry out" | "Perform the task" not "Realize the task" |
| "actually" (≠ atualmente) | "currently" | "Currently active" not "Actually active" |
| "pretend" (≠ pretender) | "intend" | "Intend to create" not "Pretend to create" |
| "resume" (≠ resumir) | "summarize" | "Summarize the results" not "Resume the results" |
| "assist" (≠ assistir) | "attend", "watch" | "Watch the presentation" not "Assist the presentation" |
| "fabric" (≠ fábrica) | "factory" | "The factory produces..." not "The fabric produces..." |
| Excessive "the" | Omit when generic | "Agents must read directives" not "The agents must read the directives" |

### Common Pitfalls from es

| Mistake | Correction | Example |
|---------|-----------|---------|
| "sensible" (≠ sensible) | "sensitive" | "Sensitive data" not "Sensible data" |
| "actual" (≠ actual) | "current" | "Current version" not "Actual version" |
| "eventual" (≠ eventual) | "possible", "occasional" | "A possible error" not "An eventual error" |

## References

- `lex-language-en` — Mandatory rules (this Codex complements)
- `lex-language` — Cross-cutting rules
- `codex-language` — Cross-cutting translation guide
