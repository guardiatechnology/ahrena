Create New Codex. Codex creation (reference manuals)

# Cry: Create New Codex

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Codex creation (reference manuals)

## Usage

```
/cry-new-codex <domínio> [público] [--clade clade/subclade]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `domínio` | Yes | Knowledge area to document | `"system architecture"` |
| `público` | No | Who consults the Codex. If omitted, assumes "AI agents and developers" | `"backend team"` |
| `--clade` | No | Clade/subclade in the taxonomy. If omitted, the agent infers from the domain | `--clade engineering/architecture` |

## What the Command Does

1. Reads `.ahrena/.directives` to obtain languages and conventions
2. Invokes `kata-create-codex` with the provided parameters; the Kata consults `codex-codex` and the official template and produces the Codex
3. (The Kata) Creates the Codex in the default language and translates to the remaining languages
4. Reports the created files

## Prompt Template

```
Contexto:
- Domínio: {{domínio}}
- Público-alvo: {{público}} (ou "agentes de IA e desenvolvedores")
- Clade/Subclade: {{clade}} (ou inferir do domínio)

Tarefa:
Execute o kata-create-codex. O Kata consulta .ahrena/.directives, codex-codex
e templates/codex-sample.md. Crie o Codex no idioma padrão e
traduza para todos os idiomas de language.i18n.

Formato de saída:
Lista de arquivos criados com confirmação de que o Codex tem escopo
delimitado, princípios acionáveis e gatilho de atualização.
```

## Invocation Example

**Create Codex with domain:**

```
/cry-new-codex "REST API patterns"
```

**Output:**

```
Codex created successfully.

Domain: REST API Patterns
Principles: 4 principles defined
Update trigger: on each new API version

Files created:
1. framework/pt-BR/engineering/backend/codex/codex-api-patterns.md ✓
2. framework/es/engineering/backend/codex/codex-api-patterns.md ✓
3. framework/en/engineering/backend/codex/codex-api-patterns.md ✓
```

## Constraints

- Does not create encyclopedic Codex artifacts — suggests splitting if the scope is too broad
- Always executes `kata-create-codex` (never creates directly)
- Always creates in all three mandatory languages
