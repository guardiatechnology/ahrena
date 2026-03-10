# Cry: Nuevo Pull Request

> **Prefijo:** `cry-` | **Tipo:** Comando Recorrente | **Alcance:** Atajo para abrir Pull Request en el repositorio origin

## Invocación

```
/cry-new-pr [--draft] [--title "..."]
```

## Parámetros

| Parámetro | Obligatorio | Descripción |
|-----------|:-----------:|-------------|
| `--draft` | No | Crear el PR como borrador |
| `--title` | No | Título del PR en Conventional Commits. Si se omite, el agente infiere de los commits. |

## Comportamiento

1. Invoca **kata-contributing-pr** (que se alinea con kata-contribute).
2. El kata usa la plantilla `.ahrena/contributing_templates/pull_request_template.md` (o `.github/pull_request_template.md`), valida los commits según las Lexis y crea el PR vía MCP de GitKraken (`pull_request_create`).

## Kata Asociado

`kata-contributing-pr` — Procedimiento para contribuir vía Pull Request.

## Referencias

- `codex-contributing` — Flujo de contribución Guardia
- `kata-contributing-pr` — Kata invocado por este cry
- `kata-commit` — Procedimiento de commit (garantizar conformidad antes del PR)
- `.ahrena/contributing_templates/pull_request_template.md` — Plantilla de PR
