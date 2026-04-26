Create New Cry. Cries creation (recurring commands)

# Cry: Create New Cry

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Cries creation (recurring commands)

## Usage

```
/cry-new-cry <ação> [kata] [--clade clade/subclade]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `ação` | Yes | What the new command does | `"generate changelog"` |
| `kata` | No | Kata that the Cry invokes. If omitted, the agent identifies or suggests creation | `kata-generate-changelog` |
| `--clade` | No | Clade/subclade in the taxonomy. If omitted, the agent infers from the action | `--clade engineering/process` |

## What the Command Does

1. Reads `.ahrena/.directives` to obtain languages and conventions
2. Invokes `kata-create-cry` with the provided parameters; the Kata consults `codex-cries` and the official template and produces the Cry (and checks whether the associated Kata exists)
3. (The Kata) Creates the Cry in the default language and translates to the remaining languages
4. Reports the created files

## Prompt Template

```
Contexto:
- Ação: {{ação}}
- Kata associado: {{kata}} (ou identificar/sugerir)
- Clade/Subclade: {{clade}} (ou inferir da ação)

Tarefa:
Execute o kata-create-cry. O Kata consulta .ahrena/.directives, codex-cries
e templates/cry-sample.md. Verifique se o Kata associado existe. Crie o Cry
no idioma padrão e traduza para todos os idiomas de language.i18n.

Formato de saída:
Lista de arquivos criados com confirmação de que o Cry tem sintaxe clara,
parâmetros mínimos e prompt template referenciando o Kata.
```

## Invocation Example

**Create Cry with action:**

```
/cry-new-cry "generate changelog"
```

**Output:**

```
Cry created successfully.

Command: /cry-changelog
Action: Generate changelog from commits
Associated Kata: kata-generate-changelog (suggested — does not exist yet)

Files created:
1. framework/pt-BR/engineering/process/cries/cry-changelog.md ✓
2. framework/es/engineering/process/cries/cry-changelog.md ✓
3. framework/en/engineering/process/cries/cry-changelog.md ✓

Pending: kata-generate-changelog needs to be created.
Suggestion: /cry-new-kata "generate changelog"
```

**With explicit Kata:**

```
/cry-new-cry "translate document" kata-translate --clade documentation/i18n
```

## Constraints

- Every Cry MUST reference a Kata — if the Kata does not exist, flag it as pending
- Always executes `kata-create-cry` (never creates directly)
- Always creates in all three mandatory languages
