---
name: cry-new-user-story-frontend
description: "Nova User Story (Frontend). Atalho para abrir issue de user story de frontend no repositório"
---

# Cry: Nova User Story (Frontend)

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para abrir issue de user story de frontend no repositório

## Invocação

```
/cry-new-user-story-frontend [título ou contexto]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição |
|-----------|:-----------:|-----------|
| título ou contexto | Não | Resumo ou contexto para preencher o template. Se omitido, o agente coleta com o usuário. |

## Comportamento

1. Invoca **kata-contributing-issue** com tipo `user-story-for-frontend` (implícito pelo nome deste cry).
2. O kata usa o template `.ahrena/contributing_templates/user-story-for-frontend.md`, preenche com o usuário e cria a issue via MCP do GitHub (ou `gh`).

## Kata Associado

`kata-contributing-issue` — Procedimento para abrir issue usando um dos 4 templates (neste caso, user-story-for-frontend).
