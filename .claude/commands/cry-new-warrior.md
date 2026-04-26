Create New Warrior. Warriors creation (specialized agents)

# Cry: Create New Warrior

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Warriors creation (specialized agents)

## Usage

```
/cry-new-warrior <papel> [domínio] [--name nome] [--clade clade/subclade]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `papel` | Yes | Function the Warrior performs | `"Software Architect"` |
| `domínio` | No | Area of operation. If omitted, the agent infers from the role | `"architectural decisions"` |
| `--name` | No | Proper name of the Warrior. If omitted, the agent suggests a thematic name | `--name Athena` |
| `--clade` | No | Clade/subclade in the taxonomy. If omitted, the agent infers from the domain | `--clade engineering/architecture` |

## What the Command Does

1. Reads `.ahrena/.directives` to obtain languages and conventions
2. Invokes `kata-create-warrior` with the provided parameters; the Kata consults `codex-warriors` and the official template and produces the Warrior
3. (The Kata) Creates the Warrior in the default language and translates to the remaining languages
4. Reports the created files

## Prompt Template

```
Contexto:
- Papel: {{papel}}
- Domínio: {{domínio}} (ou inferir do papel)
- Nome: {{name}} (ou sugerir nome temático)
- Clade/Subclade: {{clade}} (ou inferir do domínio)

Tarefa:
Execute o kata-create-warrior. O Kata consulta .ahrena/.directives, codex-warriors
e templates/warrior-sample.md. Crie o Warrior no idioma padrão e
traduza para todos os idiomas de language.i18n.

Formato de saída:
Lista de arquivos criados com confirmação de que o Warrior tem identidade
completa, responsabilidades delimitadas e cadeia de consulta definida.
```

## Invocation Example

**Create Warrior with role:**

```
/cry-new-warrior "Software Architect"
```

**Output:**

```
Warrior created successfully.

Identity:
- Name: Athena
- Role: Software Architect
- Domain: Architectural decisions and structural quality
- Persona: Analytical, rigorous, focused on trade-offs

Files created:
1. framework/pt-BR/engineering/architecture/warriors/warrior-athena.md ✓
2. framework/es/engineering/architecture/warriors/warrior-athena.md ✓
3. framework/en/engineering/architecture/warriors/warrior-athena.md ✓
```

**With explicit name and clade:**

```
/cry-new-warrior "Code Reviewer" "code quality" --name Linus --clade engineering/quality
```

## Constraints

- Does not create generic Warriors without a delimited scope
- Always executes `kata-create-warrior` (never creates directly)
- Always creates in all three mandatory languages
