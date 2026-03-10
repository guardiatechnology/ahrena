# Codex: Tone and Writing Style

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Application of tone_and_writing_style in Ahrena

## Overview

This Codex details how to interpret and apply the tone and writing-style guidelines defined in `naming.tone_and_writing_style` in the `.ahrena/.directives` file. It complements `lex-tone` (which establishes the obligation) with examples of aligned and misaligned text and guidance by content type. Use this Codex when drafting or reviewing artifacts and communication in the Ahrena context.

## Context

- **Domain:** Tone, style, and clarity in framework text production
- **Audience:** AI agents that draft artifacts or communication; content reviewers
- **Update:** When the guidelines in `.directives` change or new examples are needed

## Content

### Origin of the guidelines

The guidelines are in `.ahrena/.directives`, section `naming.tone_and_writing_style`, usually as a list of phrases. Each item is a style rule the agent must follow. `lex-tone` requires every agent to apply them; this Codex explains how.

### Interpretation of typical guidelines

| Guideline (example) | Interpretation | Application |
|---------------------|----------------|-------------|
| Direct, strategic style guided by clarity, data, and purpose | Avoid roundabout phrasing; structure arguments with logic; use Why/What/How or Problem/Cause/Solution when useful | Objective introductions and conclusions; sections with clear topics |
| Avoid adornments or abstractions that stray from the essential | Cut decorative phrases; every sentence should add information or action | Remove "It is important to note that...", "Worth highlighting..." when unnecessary |
| Support claims with numbers, evidence, or verifiable references | When it makes sense, cite metrics, sources, or concrete criteria | In Validation, Consequences, Examples sections |
| Tone that combines confidence, approachability, and practical vision | Write with assurance without arrogance; be useful and actionable | Imperative instructions ("MUST", "Consult"); avoid unnecessary hedging |
| Ambition paired with feasibility | Big ideas accompanied by concrete steps | In purposes and objectives: not only "what" but "how" when relevant |
| Avoid dashes or colons to contextualize (unless requested) | Use parentheses for nuances within the sentence; reserve ellipses for interruption or continuation | Prefer "The agent must consult the file (per lex-directives)" to "The agent must — per lex-directives — consult the file" |
| Eliminate buzzwords with no meaning | Use technical vocabulary only when necessary and with a clear concept | Avoid "disruptive solution", vague "innovation"; prefer precise terms |
| Responses that help decide and move forward | Text must guide decision or action, not only inform | Include "Next step", "Recommendation", or actionable conclusion when it makes sense |
| For emails, posts, or content for third parties: deliver only the final text | When the user asks for copy to share, do not add commentary or introduction; only the ready-to-use content | Respect explicit requests for "only the text" or "ready to send" |

### Examples: aligned vs misaligned

**Aligned:**

- "Every artifact MUST use the Pilar prefix defined in `.directives`."
- "If the `terminal` section does not exist, the agent infers from the operating system or asks the user."
- "The invocation chain is: Cry → (Warrior) → Kata. Lexis and Codex are consulted, not invoked by the Cry."

**Misaligned:**

- "It is fundamental that artifacts use the correct prefix." (less imperative; prefer "MUST")
- "When there is no terminal, one may infer or ask." (vague; specify agent and action)
- "The whole thing works like this: the Cry calls something, and then Lexis and Codex come into the picture." (informal and imprecise)

### By artifact type

| Type | Tone focus |
|------|------------|
| Lexis | Clear imperative statement; concrete consequences; no exceptions |
| Codex | Objective reference; tables and lists; explicit update triggers |
| Katas | Actionable steps; clear inputs/outputs; verifiable validation |
| Warriors | Clear identity and scope; concrete "Does" and "Does Not" |
| Cries | Description in one sentence; prompt template with task and output format |

### Technical constraints

- The agent must not invent guidelines; it must apply only those listed in `naming.tone_and_writing_style` (or the default equivalent when the section does not exist).
- In case of conflict between two guidelines, prioritize clarity and action (what best helps the reader decide or execute).

## Glossary

| Term | Definition |
|------|------------|
| tone_and_writing_style | Optional section in `.ahrena/.directives` (under `naming`) that lists tone and style guidelines |
| Direct style | Objective sentences, without roundabout phrasing or unnecessary adornments |
| Actionable | Content that leads to a clear decision or action |

## References

- `lex-tone` — Law that mandates application of tone and style
- `lex-directives` — Mandatory consultation of `.ahrena/.directives`
- `codex-directives` — Meaning of the naming section in .directives
