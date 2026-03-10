# Cry: Nova Feature Request

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para abrir issue de feature request no repositório

## Invocação

```
/cry-new-feature-request [título ou contexto]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição |
|-----------|:-----------:|-----------|
| título ou contexto | Não | Resumo ou contexto para preencher o template. Se omitido, o agente coleta com o usuário. |

## Comportamento

1. Invoca **kata-contributing-issue** com tipo `feature-request` (implícito pelo nome deste cry).
2. O kata usa o template `.ahrena/contributing_templates/feature-request.md`, preenche com o usuário e cria a issue via MCP do GitHub (ou `gh`).

## Kata Associado

`kata-contributing-issue` — Procedimento para abrir issue usando um dos 4 templates (neste caso, feature-request).

## Referências

- `codex-contributing` — Fluxo de contribuição Guardia
- `kata-contributing-issue` — Kata invocado por este cry
- `.ahrena/contributing_templates/feature-request.md` — Template da issue
