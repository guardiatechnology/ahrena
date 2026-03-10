# Cry: Novo Epic

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para abrir issue de epic no repositório

## Invocação

```
/cry-new-epic [título ou contexto]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição |
|-----------|:-----------:|-----------|
| título ou contexto | Não | Resumo ou contexto para preencher o template. Se omitido, o agente coleta com o usuário. |

## Comportamento

1. Invoca **kata-contributing-issue** com tipo `epic` (implícito pelo nome deste cry).
2. O kata usa o template `.ahrena/contributing_templates/epic.md`, preenche com o usuário e cria a issue via MCP do GitHub (ou `gh`).

## Kata Associado

`kata-contributing-issue` — Procedimento para abrir issue usando um dos 4 templates (neste caso, epic).

## Referências

- `codex-contributing` — Fluxo de contribuição Guardia
- `kata-contributing-issue` — Kata invocado por este cry
- `.ahrena/contributing_templates/epic.md` — Template da issue
