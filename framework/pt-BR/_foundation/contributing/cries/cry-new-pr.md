# Cry: Novo Pull Request

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para abrir Pull Request no repositório origin

## Invocação

```
/cry-new-pr [--draft] [--title "..."]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição |
|-----------|:-----------:|-----------|
| `--draft` | Não | Criar PR como rascunho |
| `--title` | Não | Título do PR em Conventional Commits. Se omitido, o agente infere dos commits. |

## Comportamento

1. Invoca **kata-contributing-pr** (que alinha ao kata-contribute).
2. O kata usa o template `.ahrena/contributing_templates/pull_request_template.md` (ou `.github/pull_request_template.md`), valida commits conforme as Lexis e cria o PR via MCP do GitKraken (`pull_request_create`).

## Kata Associado

`kata-contributing-pr` — Procedimento para contribuir via Pull Request.

## Referências

- `codex-contributing` — Fluxo de contribuição Guardia
- `kata-contributing-pr` — Kata invocado por este cry
- `kata-commit` — Procedimento de commit (garantir conformidade antes do PR)
- `.ahrena/contributing_templates/pull_request_template.md` — Template de PR
