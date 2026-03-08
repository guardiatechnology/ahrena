# Cry: Create New Codex

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Codex creation (reference manuals)

## Description

Quick command to create a new Codex in Ahrena. Invokes `kata-create-codex`, which consults `codex-codex` and the official template to produce a complete reference manual in all three mandatory languages.

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
2. Consults `codex-codex` for quality criteria
3. Reads `templates/codex-sample.md` as the structural base
4. Executes `kata-create-codex` with the provided parameters
5. Creates the Codex in the default language and translates to the remaining languages
6. Reports the created files

## Prompt Template

```
Contexto:
- Domínio: {{domínio}}
- Público-alvo: {{público}} (ou "agentes de IA e desenvolvedores")
- Clade/Subclade: {{clade}} (ou inferir do domínio)

Tarefa:
Execute o kata-create-codex. Consulte .ahrena/.directives para obter os
idiomas obrigatórios. Consulte codex-codex para critérios de qualidade.
Use templates/codex-sample.md como base. Crie o Codex no idioma padrão e
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

## Cry vs Kata

| Aspect | Cry | Kata |
|--------|-----|------|
| **Nature** | Quick invocation (1 command) | Complete procedure (6 steps) |
| **Complexity** | Low (domain + audience) | High (structuring, writing, validation) |
| **Configures agent?** | No | Yes (defines behavior) |
| **Example** | `/cry-new-codex "API patterns"` | 6-step workflow with checklist |

## References

- `kata-create-codex` — Procedure executed by this Cry
- `codex-codex` — Quality criteria consulted
- `templates/codex-sample.md` — Base template
