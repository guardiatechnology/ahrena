# Cry: Nueva Feature Request

> **Prefijo:** `cry-` | **Tipo:** Comando Recorrente | **Alcance:** Atajo para abrir issue de feature request en el repositorio

## Invocación

```
/cry-new-feature-request [título o contexto]
```

## Parámetros

| Parámetro | Obligatorio | Descripción |
|-----------|:-----------:|-------------|
| título o contexto | No | Resumen o contexto para rellenar la plantilla. Si se omite, el agente recoge con el usuario. |

## Comportamiento

1. Invoca **kata-contributing-issue** con tipo `feature-request` (implícito por el nombre de este cry).
2. El kata usa la plantilla `.ahrena/contributing_templates/feature-request.md`, la rellena con el usuario y crea la issue vía MCP de GitHub (o `gh`).

## Kata Asociado

`kata-contributing-issue` — Procedimiento para abrir issue usando una de las 4 plantillas (en este caso, feature-request).

## Referencias

- `codex-contributing` — Flujo de contribución Guardia (contexto del Cry)
- `kata-contributing-issue` — Procedimiento ejecutado por este Cry (ver documentación del Kata)
- `.ahrena/contributing_templates/feature-request.md` — Plantilla de la issue
