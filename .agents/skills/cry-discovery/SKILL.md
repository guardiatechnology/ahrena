---
name: cry-discovery
description: "Iniciar Sessão de Product Discovery. Product Discovery — atalho para invocar warrior-pitia com um topic e source_refs[]"
---

# Cry: Iniciar Sessão de Product Discovery

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Product Discovery — atalho para invocar `warrior-pitia` com um `topic` e `source_refs[]`

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

## Restrições

- Não modifica insights existentes salvo em modo `refine` com `target_insight_id` válido
- Não cria Idea — Idea é responsabilidade de `warrior-phanes` via `cry-ideation`
- Não altera status fora da criação inicial em `proposed` — toda outra transição depende de ação humana per HARD-GATE 2 da `lex-discovery-flow`
- Saída sempre no idioma definido em `language.default` do `.directives` (default: pt-BR)
