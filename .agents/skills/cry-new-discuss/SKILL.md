---
name: cry-new-discuss
description: "Nova Discussão. Atalho para abrir discussão no GitHub Discussions (Golden Circle)"
---

# Cry: Nova Discussão

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para abrir discussão no GitHub Discussions (Golden Circle)

## Invocação

```
/cry-new-discuss [O QUÊ] [POR QUÊ] [COMO]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição |
|-----------|:-----------:|-----------|
| O QUÊ / POR QUÊ / COMO | Não | Se fornecidos, o agente usa para estruturar a discussão. Caso contrário, coleta com o usuário. |

## Comportamento

1. Invoca **kata-contributing-discuss**.
2. O kata estrutura a proposta no Golden Circle (O QUÊ, POR QUÊ, COMO) e cria a discussão no GitHub Discussions via MCP do GitHub quando disponível (ou indica abertura manual).

## Kata Associado

`kata-contributing-discuss` — Procedimento para abrir discussão no GitHub Discussions (Golden Circle).
