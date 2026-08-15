---
name: cry-pr-review
description: "Iniciar revisão de PR com `purpose=review`. Atalho para iniciar uma sessão Claude Code de revisão de PR já etiquetada para a subseção Review do stamp de custo"
---

# Cry: Iniciar revisão de PR com `purpose=review`

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para iniciar uma sessão Claude Code de revisão de PR já etiquetada para a subseção `Review` do stamp de custo

## Uso

```
/cry-pr-review <PR_NUMBER> [repositório]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `PR_NUMBER` | Sim | Número da PR a revisar | `72` |
| `repositório` | Não | `owner/repo`; default: `gh repo view --json nameWithOwner` | `guardiatechnology/ahrena` |

## O que o Comando Faz

1. Resolve `PR_NUMBER` e repositório a partir dos parâmetros ou do contexto.
2. Invoca `kata-pr-review` com esses inputs.
3. O Kata verifica `pr_cost_tracking.enabled` e `attribution_mode` em `.ahrena/.directives`, orienta o usuário sobre como marcar a sessão como `purpose=review` (caminhos A/B/C documentados no Kata) e dispara `/review` na PR.

## Prompt Template

```
Contexto:
- PR alvo: #{{PR_NUMBER}}
- Repositório: {{repositório}} (opcional; resolva via `gh repo view` se ausente)

Tarefa:
Invoque kata-pr-review com PR_NUMBER e repositório resolvidos. Antes de
disparar /review, oriente o usuário a setar `GUARDIA_PURPOSE=review` (ou
iniciar a sessão de revisão com `GUARDIA_PURPOSE=review claude`) para
que os turnos sejam contabilizados na subseção Review do stamp.

Formato de saída:
Status da marcação (env var setada / prompt heurístico) seguido da
condução da revisão como faria normalmente em /review.
```
