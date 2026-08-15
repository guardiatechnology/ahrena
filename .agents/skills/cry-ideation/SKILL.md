---
name: cry-ideation
description: "Promover Insight Aprovado a Idea. Product Discovery — atalho para invocar warrior-phanes com um ou mais insight_path aprovados"
---

# Cry: Promover Insight Aprovado a Idea

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Product Discovery — atalho para invocar `warrior-phanes` com um ou mais `insight_path` aprovados

## Uso

```
/cry-ideation
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `insight_path` | Sim | Path canônico do insight a promover (string ou array quando múltiplos insights formam uma Idea única) | `docs/discovery/scheduled-payments-research/insights/001-...` |
| `additional_context` | Não | Contexto extra fornecido pelo humano (dados de telemetria, hipótese refinada, piloto disponível) que ajuda Phanes a montar `success_metric` ou `effort_estimate` | "Cliente piloto disponível: escritório Y" |

## O que o Comando Faz

1. Invoca `warrior-phanes` com os parâmetros fornecidos
2. Phanes lê `.ahrena/.directives` e internaliza `lex-discovery-flow` e `codex-discovery-artifacts`
3. Phanes valida o HARD-GATE 1 em **três momentos** (per `kata-ideation-from-insight`): preflight de input (a, d) antes de qualquer leitura, preflight de output (b, c) sobre a Idea sintetizada antes de gravar, e pós-escrita (e) com rollback transacional caso a atualização parcial dos insights falhe
4. Se preflight passar, Phanes executa `kata-ideation-from-insight`, gerando o arquivo da Idea com os 5 campos de conteúdo obrigatórios preenchidos
5. Phanes atualiza o(s) insight(s) de origem para `status: promoted` com `idea_ref` apontando para a Idea (rollback automático se falhar)
6. Phanes reporta a Idea criada e os insights promovidos, sinalizando lacunas que pedem validação adicional

## Prompt Template

```
Assuma o papel de warrior-phanes (Product Ideation).

Parâmetros recebidos:
- insight_path:
{{insight_path}}
- additional_context:
{{additional_context}}

Tarefa:
Execute kata-ideation-from-insight com os parâmetros acima.
Antes de qualquer escrita, leia .ahrena/.directives, lex-discovery-flow e codex-discovery-artifacts.
Valide o HARD-GATE 1 em três momentos, conforme o kata:
  - Preflight de input (a, d) antes de qualquer leitura
  - Preflight de output (b, c) sobre a Idea sintetizada, ANTES de gravar
  - Pós-escrita (e) com rollback transacional se a atualização parcial dos insights falhar
Se qualquer preflight falhar, interrompa e informe o humano qual ação destrava.
Se passar, gere a Idea em docs/discovery/{topic}/ideas/{NNN}-{slug}.md
com os 5 campos de conteúdo obrigatórios (problem, hypothesis, target_user, success_metric, effort_estimate)
e linked_insights[] referenciando os insights de origem.
Atualize o(s) insight(s) de origem para status: promoted + idea_ref + updated_at.
Não altere status de insight para approved (HARD-GATE 2; prerrogativa humana).

Formato de saída:
- Confirmação da Idea criada com path canônico
- Lista dos insights promovidos
- Resumo de cada um dos 5 campos de conteúdo obrigatórios
- Lacunas que pedem validação adicional antes do design cycle
```

## Restrições

- Não cria Idea se o HARD-GATE 1 falhar — interrompe e informa o humano
- Não altera status de insight para `approved` — prerrogativa humana per HARD-GATE 2 da `lex-discovery-flow`
- Não modifica campos do insight de origem além de `status`, `idea_ref` e `updated_at`
- Não mistura `topics` distintos em uma única Idea
- Saída sempre no idioma definido em `language.default` do `.directives` (default: pt-BR)
