# Cry: Design Canônico de Agent em Operação Concreta

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Engenharia — Agents: entry point para conduzir promoção de PoV → `operational-concrete` ou `direct-entry` em produção, sob orquestração de `warrior-metis`

## Descrição

`cry-agent-design` é o entry point canônico para projetar um agent em estágio `operational-concrete`. Invoca `warrior-metis`, que aplica o gate da DoOC (`kata-dooc-validate`), orquestra os 8 katas de design e entrega o pacote de 13 arquivos em `docs/{context}/agents/{agent}/`.

Quando `--from-pov` é fornecido, o ciclo consome o output de `warrior-claudionor` (PoV pré-operacional) e enriquece o context pack com material real (few-shot, exemplos negativos, telemetria). Quando ausente, opera em `direct-entry` (exige ADR/PDR explícito) ou `legacy-pov` (retrofit).

## Uso

```
/cry-agent-design --context <name> --agent <slug> [--from-pov <path>] --tier <1|2|3|4> [--owner "..."] [--entry-mode <with-pov|direct-entry|legacy-pov>] [--adr <path>]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `--context` | Sim | Bounded Context (kebab-case) — `docs/{context}/agents/{agent}/` | `reconciliation` |
| `--agent` | Sim | Slug do agent (kebab-case) | `rec-classifier` |
| `--from-pov` | Não | Path do PoV de origem produzido por `warrior-claudionor` | `docs/reconciliation/agents-pov/rec-pov-classifier/` |
| `--tier` | Sim | Tier de criticidade; tier-1/2 dispara SLO obrigatório per `lex-slo-required` | `tier-2` |
| `--owner` | Não (sugerido) | Nome + papel + canal de escalonamento do owner | `"Marta Souza, Lead Reconciliation, #rec-oncall"` |
| `--entry-mode` | Não | Modo de entrada; default = `with-pov` quando `--from-pov` presente, `direct-entry` quando ausente | `with-pov` \| `direct-entry` \| `legacy-pov` |
| `--adr` | Conditional | Path do ADR/PDR; obrigatório em `direct-entry` e em `legacy-pov` fora da janela de 90 dias | `docs/adr/ADR-029-rec-classifier-direct-entry.md` |

## O que o Comando Faz

1. Invoca `warrior-metis` com os parâmetros recebidos
2. Mêtis executa o ciclo completo:
   - Passo 0 — `kata-dooc-validate` (gate canônico)
   - Passos 1-8 — 8 katas de design em ordem
   - Passo 9 — reciprocidade Feature ↔ Agent
   - Passo 10 — snapshot DoOC
   - Passo 11 — handoff a `warrior-apollo-agents`
3. Reporta a árvore final de arquivos produzidos
4. Declara que o pacote está pronto para implementação por `warrior-apollo-agents`

## Prompt Template

```
Assuma o papel de warrior-metis. Conduza a promoção do agent
{{agent}} em {{context}} para stage `operational-concrete`.

Inputs canônicos:
- context: {{context}}
- agent: {{agent}}
- tier: {{tier}}
- owner: {{owner}}
- entry-mode: {{entry_mode}}
- from-pov: {{from_pov_path}} (quando aplicável)
- adr: {{adr_path}} (quando direct-entry ou legacy-pov fora da janela)

Execute o fluxo principal de warrior-metis:
  Passo 0 — kata-dooc-validate (gate)
  Passos 1-8 — 8 katas de design em ordem determinística
  Passo 9 — reciprocidade Feature ↔ Agent
  Passo 10 — snapshot DoOC
  Passo 11 — handoff a warrior-apollo-agents

Restrições:
- NÃO promova o agent sem kata-dooc-validate retornar `go`
- NÃO escreva código (Python, TS); o pacote é design, não implementação
- Aplique tom per lex-brand-voice (direto, estratégico, afirmativo, claro;
  proibido innovative, disruptive, transformative, revolutionary, fintech)
- Use idioma per language.default em .ahrena/.directives

Formato de saída:
- Árvore final em docs/{{context}}/agents/{{agent}}/
- DoOC sidecar em docs/{{context}}/dooc/{{agent}}.md
- Atualização em docs/{{context}}/feature-agent-map.md
- Sumário com decisão DoOC + paths produzidos + próximo passo (handoff a Apollo-Agents)
```

## Exemplo de Invocação

**Input:**

```
/cry-agent-design \
  --context reconciliation \
  --agent rec-classifier \
  --from-pov docs/reconciliation/agents-pov/rec-pov-classifier/ \
  --tier tier-2 \
  --owner "Marta Souza, Lead Reconciliation, #rec-oncall"
```

**Output esperado (sumário):**

```
🛡️  warrior-metis — APM Operação Concreta
   context: reconciliation | agent: rec-classifier | tier: tier-2 | entry-mode: with-pov

✅ DoOC gate: go (9/9 itens)
✅ 13 arquivos produzidos em docs/reconciliation/agents/rec-classifier/
✅ DoOC sidecar em docs/reconciliation/dooc/rec-classifier.md
✅ Reciprocidade Feature ↔ Agent atualizada em docs/reconciliation/feature-agent-map.md

Pacote pronto para warrior-apollo-agents implementar (plan-013).
```

## Restrições

- O Cry NÃO invoca Lexis nem Codex diretamente (per `lex-pilars`); invoca apenas `warrior-metis`
- `warrior-metis` orquestra todos os 9 katas internamente; o Cry permanece o entry point único
- Em `direct-entry` sem `--adr`, o Cry falha antes de invocar Mêtis (validação no shell wrapper)
- Em `legacy-pov` fora da janela de 90 dias sem `--adr`, idem
- O Cry NÃO modifica `.ahrena/.directives` nem `framework/`

## Diferença de Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Natureza** | Invocação rápida (1 entry point) | Procedimento estruturado |
| **Quem orquestra** | `warrior-metis` | Mêtis invoca os 9 katas |
| **Configura agente?** | Não (é o invocador) | Sim |
| **Exemplo** | `/cry-agent-design ...` | `kata-dooc-validate`, `kata-agent-overview-design`, ... |

## Cross-references

- `warrior-metis` — orquestrador invocado pelo Cry
- `kata-dooc-validate` — primeiro Kata invocado por Mêtis
- `warrior-claudionor` — upstream producer do PoV consumido via `--from-pov`
- `warrior-apollo-agents` — downstream consumer pós-design (per plan-013)
- `lex-agent-construction-directives`, `lex-agent-design-docs` — fundação das regras aplicadas

---

**Modelo:** Cry é o entry point único do estágio Operação Concreta. Invoca `warrior-metis`. Mêtis aplica gate DoOC, orquestra 8 katas de design, entrega 13 arquivos canônicos. Apollo-Agents implementa downstream.
