# Cry: Nova User Story (API)

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para abrir issue de user story de API no repositório

## Invocação

```
/cry-new-user-story-api [título ou contexto]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição |
|-----------|:-----------:|-----------|
| título ou contexto | Não | Resumo ou contexto para preencher o template. Se omitido, o agente coleta com o usuário. |

## Comportamento

1. Invoca **kata-contributing-issue** com tipo `user-story-for-api` (implícito pelo nome deste cry).
2. O kata usa o template `.ahrena/contributing_templates/user-story-for-api.md`, preenche com o usuário e cria a issue via MCP do GitHub (ou `gh`).

## Kata Associado

`kata-contributing-issue` — Procedimento para abrir issue usando um dos 4 templates (neste caso, user-story-for-api).

## Referências

- `codex-contributing` — Fluxo de contribuição Guardia
- `kata-contributing-issue` — Kata invocado por este cry
- `.ahrena/contributing_templates/user-story-for-api.md` — Template da issue
