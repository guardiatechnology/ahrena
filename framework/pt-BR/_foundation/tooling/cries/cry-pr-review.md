# Cry: Iniciar revisão de PR com `purpose=review`

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para iniciar uma sessão Claude Code de revisão de PR já etiquetada para a subseção `Review` do stamp de custo

## Descrição

Atalho para invocar `kata-pr-review`. O Kata orienta a marcação `purpose=review` (via env var `GUARDIA_PURPOSE` ou heurística no prompt) e dispara a revisão. Sem essa marcação, turnos de revisão entram no balde `dev` e poluem a leitura do esforço que originou a PR.

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

## Exemplo de Invocação

```
/cry-pr-review 72
```

**Output esperado:** o agente lembra de setar `GUARDIA_PURPOSE=review` (ou recomenda começar a sessão com `/review PR #72`), confirma que o hook escreveu `purpose=review` no sidecar e procede com a revisão.

## Referências

- `kata-pr-review` — Procedimento detalhado de marcação + disparo
- `codex-pr-cost-tracking` — Manual com a cascata `purpose` e o formato do bloco `Review`
- `kata-pr-cost-stamp` — Estampa o bloco com a contagem de revisão na PR
