# Codex: Cross-Language Translation Guide

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** General guidance for technical documentation translation

## Content

### Identifying Source and Target Languages

1. **Source language:** determined by the file path. The first segment after `framework/` indicates the language (e.g., `framework/pt-BR/...` → source is pt-BR).
2. **Target language:** defined by the request parameter or by `language.i18n` in `.ahrena/.directives`.
3. **Default language:** defined in `language.default` — the source of truth when there is divergence.

### Preserving Markdown Structure

When translating, rigorously preserve:

| Element | Action |
|---------|--------|
| Headings (`#`, `##`, `###`) | Translate text, maintain hierarchy |
| Tables | Translate cell content, maintain structure |
| Lists (ordered and unordered) | Translate items, maintain order |
| Code blocks (`` ``` ``) | **Never** translate content |
| Blockquotes (`>`) | Translate text, maintain formatting |
| Links and URLs | **Never** alter URLs. Translate link text if needed |
| Images | **Never** alter paths. Translate alt text if present |
| YAML frontmatter | **Never** translate keys. Translate `description` values |

### Glossary of Untranslatable Terms

These terms are **NEVER** translated, under any circumstance:

**Ahrena terms:**
- Lexis, Codex, Katas, Warriors, Cries
- Ahrena, Clade, Subclade, Pilar
- Warrior names (Hermes, etc.)

**Universal technical terms:**
- commit, merge, branch, pull request, push, pull
- deploy, rollback, hotfix
- framework, middleware, API, SDK, CLI
- Markdown, YAML, JSON, HTML, CSS

### Examples of Good and Bad Translations

#### Good translation (pt-BR → en)

**Original (pt-BR):**
> O agente **DEVE** ler o `.ahrena/.directives` antes de iniciar qualquer atividade.

**Translation (en):**
> The agent **MUST** read `.ahrena/.directives` before starting any activity.

- Meaning preserved
- Modal force maintained (DEVE → MUST)
- File path preserved

#### Bad translation (pt-BR → en)

**Original (pt-BR):**
> O agente **DEVE** ler o `.ahrena/.directives` antes de iniciar qualquer atividade.

**Translation (en):**
> The agent should check the Ahrena directives file before it begins.

- "DEVE" (mandatory) downgraded to "should" (recommendation)
- Path `.ahrena/.directives` replaced with generic text
- Loss of technical precision

### Consultation Flow per Translation

For each translation, the agent must consult in this order:

1. `lex-language` — mandatory cross-cutting rules
2. `lex-language-{lang}` — target language rules
3. `codex-language` — this cross-cutting guide
4. `codex-language-{lang}` — target language-specific guide
