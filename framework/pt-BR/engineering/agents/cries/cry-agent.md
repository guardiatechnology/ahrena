# Cry: Scaffold de Subagent Anthropic Isolado

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Engenharia — Agents (estágio pré-operacional): criação rápida de um subagent Anthropic standalone sem o ciclo POV completo

## Descrição

Atalho para invocar `kata-agent-author` diretamente e criar um subagent Anthropic isolado em `.claude/agents/<slug>.md` (ou dentro de um plugin, delegado a plan-034). Para casos triviais onde o ciclo POV completo (`cry-pov`) é overhead — basta um arquivo `.md` com frontmatter Anthropic e identidade declarada. O subagent gerado **sempre** declara `stage: pre-operational` por construção; se o PoV maturar, a promoção para `operational-concrete` passa pela DoOC (`lex-agent-construction-directives`).

## Uso

```
/cry-agent --slug <name> --description "..." [--persona <warrior>] [--target <path>] [--from-pov <path>]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `--slug` | Sim | Identificador em kebab-case (1-64 chars, `[a-z0-9-]`) | `reconciliation-assistant` |
| `--description` | Sim | Descrição curta (1-2 frases) — vai para o frontmatter | `"Sugere pareamentos extrato↔lançamento contábil"` |
| `--persona` | Não | Importa identidade base de um warrior existente | `warrior-apollo` |
| `--target` | Não | Path destino. Default `.claude/agents/<slug>.md` | `.claude/agents/`, `plugins/foo/agents/` |
| `--from-pov` | Não | Importa de um PoV existente | `docs/reconciliation/agents-pov/` |
| `--force` | Não | Sobrescreve arquivo existente | (flag) |

## O que o Comando Faz

1. Valida `--slug` (kebab-case, sem `--` consecutivos)
2. Resolve `--target` (default `.claude/agents/`)
3. Invoca `kata-agent-author` com os parâmetros recebidos
4. Persistir arquivo `<slug>.md` com frontmatter Anthropic + corpo mínimo (Identidade + `stage: pre-operational` + Capacidades + Restrições)
5. Reporta o path final e validações aplicadas

## Prompt Template

```
Crie um subagent Anthropic standalone invocando kata-agent-author.

Slug: {{slug}}
Description: {{description}}
{% if persona %}Persona base: {{persona}}{% endif %}
{% if from_pov %}Origem PoV: {{from_pov}}{% endif %}
{% if target %}Destino: {{target}}{% endif %}

Garanta:
- Frontmatter Anthropic correto (`name`, `description`)
- Linha `stage: pre-operational` literal no corpo
- Sem placeholders remanescentes

Reporte o path final e o tree do arquivo gerado.
```

## Exemplo de Invocação

**Input:**

```
/cry-agent --slug reconciliation-assistant \
           --description "Sugere pareamentos extrato↔lançamento contábil em estágio pré-operacional"
```

**Output esperado:**

```
🛠  cry-agent — scaffold standalone
   slug: reconciliation-assistant
   target: .claude/agents/reconciliation-assistant.md

→ kata-agent-author
   ✅ frontmatter validado
   ✅ stage: pre-operational declarado
   ✅ arquivo criado

Conteúdo (extrato):
   ---
   name: reconciliation-assistant
   description: Sugere pareamentos extrato↔lançamento contábil em estágio pré-operacional
   ---
   # Reconciliation Assistant
   ## Identidade
   stage: pre-operational
   ...

Próximos passos:
   - Iterar o corpo do subagent conforme o uso
   - Quando precisar de ciclo PoV estruturado, considere /cry-pov --kind subagent
```

**Input (importando de PoV existente):**

```
/cry-agent --slug reconciliation-assistant \
           --description "Sugere pareamentos extrato↔lançamento contábil" \
           --from-pov docs/reconciliation/agents-pov/
```

**Output esperado:**

```
🛠  cry-agent — scaffold standalone (--from-pov)
   slug: reconciliation-assistant
   importando de: docs/reconciliation/agents-pov/

→ kata-agent-author
   ✅ persona importada de overview.md
   ✅ Capacidades e Restrições copiadas de system-prompt.md
   ✅ stage: pre-operational mantido
   ✅ arquivo criado em .claude/agents/reconciliation-assistant.md
```

## Restrições

- `--slug` deve seguir as restrições do Anthropic Agent Skills spec (kebab-case; sem `--` consecutivos; sem hífen no início/fim).
- `--description` deve ser concreto (não placeholder).
- O subagent gerado **sempre** tem `stage: pre-operational` — promoção para `operational-concrete` requer DoOC.
- Cry **não** invoca `lex-*` ou `codex-*` diretamente (`lex-pilars`); orquestração é responsabilidade do kata.
- Quando `--target` aponta para dentro de plugin, **plan-034** é responsável por registrar o subagent no manifest do plugin; este cry só cria o arquivo.

## Diferença de `cry-pov`

| Aspecto | `cry-agent` | `cry-pov` |
|---|---|---|
| **Natureza** | Scaffold trivial | Ciclo POV completo |
| **Output** | 1 arquivo `.md` | `docs/{context}/agents-pov/` + implementação |
| **Quando usar** | Já há clareza de escopo e tooling; basta o arquivo | Início de um PoV real com cliente |
| **Diretrizes** | Identidade declarada (Diretriz 01 mínima) | As 6 Diretrizes aplicadas no rigor pré-operacional |

---

**Modelo:** Este Cry é o atalho para criação trivial. Para PoVs estruturados, prefira `cry-pov` (ciclo completo).
