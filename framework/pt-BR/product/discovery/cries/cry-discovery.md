# Cry: Iniciar Sessão de Product Discovery

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Product Discovery — atalho para invocar `warrior-pitia` com um `topic` e `source_refs[]`

## Descrição

Atalho que invoca `warrior-pitia` para conduzir uma sessão de Product Discovery: ler as fontes informadas e produzir um ou mais insights estruturados sob `docs/discovery/{topic}/insights/`. O Cry **não** invoca Lexis nem Codex diretamente — apenas aciona o Warrior, que internamente executa `kata-discovery-synthesis` e consulta `lex-discovery-flow` e `codex-discovery-artifacts`.

## Uso

```
/cry-discovery
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `topic` | Sim | Tema da iniciativa de Discovery em kebab-case | `scheduled-payments-research` |
| `source_refs[]` | Sim (≥1) | Lista de URLs ou paths das fontes a estudar | URLs Notion, Figma, GitHub; paths locais |
| `mode` | Não | `new` (default) ou `refine` | `new` |
| `target_insight_id` | Condicional | Obrigatório se `mode == refine` — id do insight a atualizar | `scheduled-payments-research/insights/001-...` |
| `feedback` | Condicional | Obrigatório se `mode == refine` — texto do feedback humano | "Especificar o que é considerado divergência alta" |

## O que o Comando Faz

1. Invoca `warrior-pitia` com os parâmetros fornecidos
2. Pítia lê `.ahrena/.directives`, internaliza `lex-discovery-flow` e `codex-discovery-artifacts`
3. Pítia executa `kata-discovery-synthesis` lendo as `source_refs[]` via MCP ou `Read`
4. Pítia produz arquivos novos em `docs/discovery/{topic}/insights/` (modo `new`) ou atualiza arquivo existente (modo `refine`)
5. Pítia reporta os arquivos criados/atualizados e destaca perguntas em aberto críticas

## Prompt Template

```
Assuma o papel de warrior-pitia (Product Discovery).

Parâmetros recebidos:
- topic: {{topic}}
- source_refs:
{{source_refs}}
- mode: {{mode}}
- target_insight_id: {{target_insight_id}}
- feedback: {{feedback}}

Tarefa:
Execute kata-discovery-synthesis com os parâmetros acima.
Antes de qualquer escrita, leia .ahrena/.directives, lex-discovery-flow e codex-discovery-artifacts.
Produza um insight por arquivo em docs/discovery/{{topic}}/insights/{NNN}-{slug}.md
com status: proposed (modo new) ou atualize o existente (modo refine).
Não proponha solução — solução é responsabilidade de warrior-phanes.
Não altere status para nada além da criação inicial em proposed (HARD-GATE 2).

Formato de saída:
- Lista dos arquivos criados/atualizados com paths canônicos
- Para cada insight, 1 frase de resumo da observação
- Perguntas em aberto críticas que pedem evidência adicional
- Candidatos a awaiting_evidence quando aplicável (sinaliza ao humano; não muda status)
```

## Exemplo de Invocação

**Input:**

```
/cry-discovery
topic: scheduled-payments-research
source_refs:
  - https://www.notion.so/guardia/interview-accountant-2026-05-04-abc123
  - docs/transcripts/process-walkthrough-erp-x.md
  - https://github.com/guardiatechnology/erp-x-spec/blob/main/openapi.yaml
mode: new
```

**Output esperado:**

```
warrior-pitia executou kata-discovery-synthesis. 3 insights criados com status: proposed:

1. docs/discovery/scheduled-payments-research/insights/001-manual-reconciliation-bottleneck.md
   — 4h/semana de conciliação manual; gargalo declarado pelo contador entrevistado
2. docs/discovery/scheduled-payments-research/insights/002-erp-x-7-screens-per-divergence.md
   — 7 telas para resolver 1 divergência; OpenAPI sem endpoint de conciliação em lote
3. docs/discovery/scheduled-payments-research/insights/003-date-vs-cash-divergence-pattern.md
   — Divergência de data de competência vs. caixa concentra ~60% das ocorrências

Perguntas em aberto críticas:
- Mediana real do tempo de conciliação por escritório (amostra de 1)
- Confirmação do padrão de divergência em escritórios além do entrevistado

Candidato a awaiting_evidence: insight #003 (depende de mediana). Decisão de transição é sua.
```

## Restrições

- Não modifica insights existentes salvo em modo `refine` com `target_insight_id` válido
- Não cria Idea — Idea é responsabilidade de `warrior-phanes` via `cry-ideation`
- Não altera status fora da criação inicial em `proposed` — toda outra transição depende de ação humana per HARD-GATE 2 da `lex-discovery-flow`
- Saída sempre no idioma definido em `language.default` do `.directives` (default: pt-BR)

## Diferença de Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Natureza** | Atalho de invocação de Pítia | Procedimento que Pítia executa |
| **Quem invoca** | Usuário humano | Warrior (Pítia) |
| **O que faz** | Aciona o warrior com parâmetros | Sintetiza fontes em insights |
| **Exemplo** | `/cry-discovery` | `kata-discovery-synthesis` |

## Referências

- `warrior-pitia` — agente invocado por este Cry
- `kata-discovery-synthesis` — procedimento executado internamente
- `lex-discovery-flow` — lei aplicável (consultada pelo warrior, não pelo cry)
- `codex-discovery-artifacts` — schema de insights (consultado pelo warrior)
