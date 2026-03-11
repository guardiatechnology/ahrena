# Cry: Create New Lexis

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Lexis creation (unbreakable laws)

## Description

Quick command to create a new Lexis in Ahrena. Invokes `kata-create-lexis`, which consults `codex-lexis` and the official template to produce a complete law in all three mandatory languages.

## Usage

```
/cry-new-lex <assunto> [escopo] [--clade clade/subclade]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `assunto` | Yes | Topic of the law to create | `"mandatory code review"` |
| `escopo` | No | Where the law applies. If omitted, the agent infers from the subject | `"all repositories"` |
| `--clade` | No | Clade/subclade in the taxonomy. If omitted, the agent infers from the subject | `--clade engineering/quality` |

## What the Command Does

1. Reads `.ahrena/.directives` to obtain languages and conventions
2. Invokes `kata-create-lexis` with the provided parameters; the Kata consults `codex-lexis` and the official template and produces the Lexis
3. (The Kata) Creates the Lexis in the default language and translates to the remaining languages
4. Reports the created files

## Prompt Template

```
Contexto:
- Assunto: {{assunto}}
- Escopo: {{escopo}} (ou inferir do assunto)
- Clade/Subclade: {{clade}} (ou inferir do assunto)

Tarefa:
Execute o kata-create-lexis. O Kata consulta .ahrena/.directives, codex-lexis
e templates/lex-sample.md. Crie a Lexis no idioma padrão e traduza para
todos os idiomas de language.i18n.

Formato de saída:
Lista de arquivos criados com confirmação de que a lei é clara, unívoca
e testável.
```

## Invocation Example

**Create Lexis with subject:**

```
/cry-new-lex "mandatory code review"
```

**Output:**

```
Lexis created successfully.

Law: "Every PR MUST have at least one approved reviewer before merge."

Files created:
1. framework/pt-BR/engineering/quality/lexis/lex-code-review.md ✓
2. framework/es/engineering/quality/lexis/lex-code-review.md ✓
3. framework/en/engineering/quality/lexis/lex-code-review.md ✓

Validation:
- Unambiguity: ✓ (single possible interpretation)
- Testability: ✓ (verifiable via GitHub API)
- Exceptions: None ✓
```

**With explicit scope and clade:**

```
/cry-new-lex "no secrets in repository" "all repositories" --clade engineering/security
```

## Constraints

- Does not create Lexis that admit exceptions — if it needs an exception, suggests creating a Codex instead
- Always executes `kata-create-lexis` (never creates directly)
- Always creates in all three mandatory languages

## Cry vs Kata

| Aspect | Cry | Kata |
|--------|-----|------|
| **Nature** | Quick invocation (1 command) | Complete procedure (6 steps) |
| **Complexity** | Low (subject + scope) | High (conception, writing, validation) |
| **Configures agent?** | No | Yes (defines behavior) |
| **Example** | `/cry-new-lex "code review"` | 6-step workflow with checklist |

## References

- `kata-create-lexis` — Procedure executed by this Cry (the Kata consults the applicable quality criteria; see Kata documentation)
- `templates/lex-sample.md` — Base template
