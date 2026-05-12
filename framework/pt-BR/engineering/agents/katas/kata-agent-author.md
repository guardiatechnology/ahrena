# Kata: Scaffolding de Subagent Anthropic Isolado

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Engenharia — Agents (estágio pré-operacional): criação de um Claude Code subagent standalone com frontmatter Anthropic correto

## Objetivo

Scaffold rápido de um subagent Anthropic isolado em `agents/<name>.md` com frontmatter compatível com a spec Claude Code subagents. Útil para casos triviais de PoV onde a estrutura completa de Skill é excesso (sem widgets, sem tools/, sem references/) — basta um arquivo `.md` com identity + tooling declarado. Pode ser **standalone** (em `.claude/agents/`) ou **dentro de um plugin** (delegado a plan-034).

Diferentemente dos 7 katas POV que produzem o **dossiê documental** em `docs/{context}/agents-pov/{agent}/`, este kata produz o **artefato executável** (o subagent em si). Usado quando `cry-pov --kind subagent` precisa instanciar o agent, ou quando o usuário invoca `cry-agent` diretamente para criação trivial.

## Quando Usar

- `cry-pov --kind subagent` despacha aqui para criar o subagent após o dossiê POV estar pronto
- `cry-agent --slug <name>` invoca diretamente para criação standalone (sem ciclo POV completo)
- Quando um PoV existente quer derivar um subagent simples a partir de uma persona aprovada

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `--slug <name>` | Sim | Identificador em kebab-case (ex.: `reconciliation-assistant`) |
| `--target <path>` | Não | Destino. Default: `.claude/agents/<slug>.md`. Pode ser `<plugin>/agents/<slug>.md` (plan-034) |
| `--persona <warrior>` | Não | Importa identidade base de um warrior existente |
| `--from-pov <path>` | Não | Se invocado dentro de `cry-pov --kind subagent`, importa de `docs/{context}/agents-pov/{agent}/` |
| `--description <text>` | Sim | Descrição curta para o frontmatter (1-2 frases) |

## Workflow

```
Progresso:
- [ ] 1. Validar slug e path destino
- [ ] 2. Compor frontmatter Anthropic
- [ ] 3. Compor corpo do subagent
- [ ] 4. Persistir arquivo
- [ ] 5. Verificar conformidade mínima
```

### Passo 1: Validar slug e path destino

- `--slug` deve ser kebab-case, 1-64 chars, `[a-z0-9-]`, sem `--` consecutivos, sem hífen no início ou fim.
- Resolve `--target`. Default: `.claude/agents/<slug>.md`. Se passado outro path (ex.: `<plugin-root>/agents/<slug>.md`), garante diretório existe.
- Se já existe arquivo no destino, exige `--force`.

### Passo 2: Compor frontmatter Anthropic

Frontmatter mínimo conforme spec Claude Code subagents:

```yaml
---
name: <slug>
description: <descrição literal de --description>
---
```

Se `--from-pov` foi passado, lê `docs/{context}/agents-pov/{agent}/pov.md` e popula `description` com a persona declarada lá (1 frase).

### Passo 3: Compor corpo do subagent

Estrutura mínima do corpo (usuário pode expandir depois):

```markdown
# <Nome legível derivado do slug>

## Identidade

stage: pre-operational

<conteúdo da persona; se --from-pov, copia bloco persona de pov.md; se --persona, importa identidade do warrior referenciado>

## Capacidades

- <capacidade 1>
- <capacidade 2>

## Restrições

- Não persiste dados além da janela de contexto atual
- Não executa fora do escopo declarado em `description`

## Notas

- Criado por kata-agent-author em <ISO date>
- Origem: <`--from-pov path` | standalone | warrior reference>
```

Se `--from-pov` foi passado, copia os blocos `Identidade`, `Capacidades`, `Restrições` literalmente do `system-prompt.md` correspondente.

### Passo 4: Persistir arquivo

1. Grava no `--target`.
2. Verifica que o arquivo foi escrito com permissão correta.
3. Se destino é `<plugin>/agents/`, **não** registra no `manifest.skill.subagents` do plugin (responsabilidade de plan-034).

### Passo 5: Verificar conformidade mínima

- [ ] Frontmatter tem `name` e `description`
- [ ] Linha `stage: pre-operational` aparece literalmente no corpo
- [ ] Slug do frontmatter == nome do arquivo (sem `.md`)
- [ ] Descrição é frase concreta (não placeholder)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `<slug>.md` | Markdown com frontmatter YAML | `.claude/agents/<slug>.md` (default) ou `<plugin>/agents/<slug>.md` |

## Exemplo de Execução

### Input

```
cry-agent --slug reconciliation-assistant \
          --description "Sugere pareamentos extrato↔lançamento contábil em estágio pré-operacional"
```

### Output (`.claude/agents/reconciliation-assistant.md`)

```markdown
---
name: reconciliation-assistant
description: Sugere pareamentos extrato↔lançamento contábil em estágio pré-operacional
---

# Reconciliation Assistant

## Identidade

stage: pre-operational

Assistente especializado em sugerir pareamentos entre transações de extrato bancário
e lançamentos contábeis do ERP da mesma janela temporal.

## Capacidades

- Sugerir o pareamento mais provável por valor + data + descrição similar
- Indicar nível de confiança (alto / médio / baixo) por sugestão

## Restrições

- Não persiste dados além da janela de contexto atual
- Não executa fora do escopo declarado em `description`
- Não cria lançamentos no ERP (apenas sugere)

## Notas

- Criado por kata-agent-author em 2026-05-12
- Origem: standalone
```

## Restrições

- **Nunca** scaffold sem `stage: pre-operational` literal — bloqueia conformidade com `lex-agent-construction-directives`.
- **Nunca** placeholder remanescente (`<...>`) no arquivo final.
- **Nunca** o kata invoca Hephaestus ou Apollo — subagent Anthropic é puro markdown; não há código a delegar.
- **Sempre** quando destino é dentro de plugin, **plan-034** é responsável pelo registro no manifest do plugin; este kata só cria o arquivo.

---

**Modelo:** Este Kata é o atalho de scaffold trivial. Para PoVs estruturados, prefira `cry-pov` (ciclo completo). Quando o subagent é parte de um plugin, plan-034 toma o relay.
