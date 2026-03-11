# Cry: Create New Kata

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Katas creation (repeatable procedures)

## Description

Quick command to create a new Kata in Ahrena. Invokes `kata-create-kata`, which consults `codex-katas` and the official template to produce a complete standardized procedure in all three mandatory languages.

## Usage

```
/cry-new-kata <tarefa> [contexto] [--clade clade/subclade]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `tarefa` | Yes | Task to standardize into a procedure | `"create ADR"` |
| `contexto` | No | Additional information about the domain or constraints | `"microservices projects"` |
| `--clade` | No | Clade/subclade in the taxonomy. If omitted, the agent infers from the task | `--clade engineering/architecture` |

## What the Command Does

1. Reads `.ahrena/.directives` to obtain languages and conventions
2. Invokes `kata-create-kata` with the provided parameters; the Kata consults `codex-katas` and the official template and produces the Kata
3. (The Kata) Creates the Kata in the default language and translates to the remaining languages
4. Reports the created files

## Prompt Template

```
Contexto:
- Tarefa: {{tarefa}}
- Contexto adicional: {{contexto}} (ou nenhum)
- Clade/Subclade: {{clade}} (ou inferir da tarefa)

Tarefa:
Execute o kata-create-kata. O Kata consulta .ahrena/.directives, codex-katas
e templates/kata-sample.md. Crie o Kata no idioma padrão e
traduza para todos os idiomas de language.i18n.

Formato de saída:
Lista de arquivos criados com confirmação de que o Kata tem inputs definidos,
passos atômicos e validação final.
```

## Invocation Example

**Create Kata with task:**

```
/cry-new-kata "create ADR"
```

**Output:**

```
Kata created successfully.

Task: Create ADR (Architecture Decision Record)
Steps: 6 steps defined
Inputs: 3 (decision, context, alternatives)

Files created:
1. framework/pt-BR/engineering/architecture/katas/kata-create-adr.md ✓
2. framework/es/engineering/architecture/katas/kata-create-adr.md ✓
3. framework/en/engineering/architecture/katas/kata-create-adr.md ✓
```

## Constraints

- If the task has fewer than 4 steps, suggests creating a Cry instead of a Kata
- Always executes `kata-create-kata` (never creates directly)
- Always creates in all three mandatory languages

## Cry vs Kata

| Aspect | Cry | Kata |
|--------|-----|------|
| **Nature** | Quick invocation (1 command) | Complete procedure (6 steps) |
| **Complexity** | Low (task + context) | High (decomposition, writing, validation) |
| **Configures agent?** | No | Yes (defines behavior) |
| **Example** | `/cry-new-kata "create ADR"` | 6-step workflow with checklist |

## References

- `kata-create-kata` — Procedure executed by this Cry (the Kata consults the applicable quality criteria; see Kata documentation)
- `templates/kata-sample.md` — Base template
