---
name: cry-pov
description: "Ciclo de PoV de Agent. Engenharia — Agents (estágio pré-operacional): entry point principal para criar um PoV de agent via stack Anthropic com observabilidade nativa"
---

# Cry: Ciclo de PoV de Agent

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Engenharia — Agents (estágio pré-operacional): entry point principal para criar um PoV de agent via stack Anthropic com observabilidade nativa

## Uso

```
/cry-pov --context <name> [--agent <slug>] --kind <skill|subagent|plugin> --problem "..." --value-metric "..." [--tier N] [--dry-run]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `--context` | Sim | Bounded context em kebab-case | `reconciliation` |
| `--agent` | Não | Slug do PoV em kebab-case. Default: derivado como `{context}-pov`. Define o subdir `docs/{context}/agents-pov/{agent}/` | `rec-pov-classifier` |
| `--kind` | Sim | Tipo de artefato Anthropic | `skill`, `subagent`, `plugin` |
| `--problem` | Sim | Problema do cliente em 1 frase | `"Time contábil gasta 3h/dia reconciliando extrato"` |
| `--value-metric` | Sim | Métrica leading com janela e threshold | `"% reconciliação automática ≥ 60% em 4 semanas"` |
| `--tier` | Não | Tier de criticidade (default: 3) | `3` |
| `--dry-run` | Não | Lista artefatos a criar sem persistir | (flag) |
| `--force` | Não | Sobrescreve PoV existente no mesmo `--context`/`--agent` | (flag) |

## O que o Comando Faz

1. Resolve `--context` e `--agent` (deriva `{context}-pov` se `--agent` for omitido) e prepara `docs/{context}/agents-pov/{agent}/`
2. Invoca `warrior-claudionor`, que dispara em sequência:
   - `kata-pov-scope-define` → `pov.md` + `scope.md`
   - `kata-pov-system-prompt` → `system-prompt.md`
   - `kata-pov-tools-select` → `tools.md`
   - `kata-pov-context-curate` → `context-pack.md`
   - `kata-pov-observability-instrument` → `observability/`
   - `kata-pov-feedback-attach` → `feedback.md`
   - `kata-pov-value-track` → `value-proof.md` (template inicial)
3. Despacha a implementação por `--kind`:
   - `skill` → **Fase 8a:** se `{paths.skills_root}/{slug}/` não existe, invoca `kata-init-skill --slug={context}-pov-skill` (scaffold). **Fase 8b:** invoca `kata-skill-implement` (delega widgets a Hephaestus, Python a Apollo)
   - `subagent` → `kata-agent-author --from-pov docs/{context}/agents-pov/{agent}/`
   - `plugin` → delega a plan-034 (capability ortogonal). Se plan-034 não estiver mergeado, aborta com mensagem clara
4. Reporta o tree final do `docs/{context}/agents-pov/{agent}/` + paths dos artefatos de implementação

## Prompt Template

```
Você está iniciando um PoV de agent. Assuma o papel de warrior-claudionor
(Pré-operacional Agent Factory) e execute o ciclo POV completo.

Context: {{context}}
Agent: {{agent | default: {{context}}-pov}}
Kind: {{kind}}
Problem: {{problem}}
Value metric: {{value_metric}}
Tier: {{tier | default: 3}}

Execute os 7 katas POV em sequência, persistindo cada output em
docs/{{context}}/agents-pov/{{agent}}/. Aplique as 6 Diretrizes de Construção
(lex-agent-construction-directives) no rigor pré-operacional. Garanta
que `stage: pre-operational` aparece literalmente em system-prompt.md.

Depois despache a implementação conforme --kind:
- skill: kata-init-skill (se necessário) → kata-skill-implement
- subagent: kata-agent-author --from-pov
- plugin: delega a plan-034 (aborta se não disponível)

Ao final, reporte o tree completo e o status (pronto para operar / faltam
preencher / bloqueado por dependência).
```

## Restrições

- `--problem` e `--value-metric` são obrigatórios e devem ser concretos (sem genericidades como "automatizar coisas").
- `--kind=plugin` exige plan-034 mergeado; caso contrário aborta com mensagem clara.
- `--context` deve ser kebab-case e único; se já existe `docs/{context}/agents-pov/{agent}/`, exige `--force` para sobrescrever.
- Todos os 7 katas POV são executados em sequência, sem skip; falha em qualquer um interrompe o ciclo.
- O Cry **não** invoca `lex-*` ou `codex-*` diretamente (`lex-pilars`); o trabalho é feito pelos katas via `warrior-claudionor`.

## Diferença de Kata e de outros Cries

| Aspecto | `cry-pov` | `cry-skill` | `cry-agent` |
|---|---|---|---|
| **Natureza** | Ciclo PoV completo + implementação | Skill como artefato distribuível | Subagent isolado standalone |
| **Output** | `docs/{context}/agents-pov/{agent}/` + skill/subagent/plugin | `.dist/<slug>.skill/` | `.claude/agents/<slug>.md` |
| **Quando usar** | Provar valor de um agent para o cliente | Empacotar skill já madura | Scaffold trivial sem ciclo POV |

---

**Modelo:** Este Cry invoca `warrior-claudionor` para o ciclo PoV completo. Para empacotamento puro de Skill, use `cry-skill`. Para scaffold trivial de subagent, use `cry-agent`.
