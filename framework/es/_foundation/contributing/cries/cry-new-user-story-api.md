# Cry: Nueva User Story (API)

> **Prefijo:** `cry-` | **Tipo:** Comando Recorrente | **Alcance:** Atajo para abrir issue de user story de API en el repositorio

## Invocación

```
/cry-new-user-story-api [título o contexto]
```

## Parámetros

| Parámetro | Obligatorio | Descripción |
|-----------|:-----------:|-------------|
| título o contexto | No | Resumen o contexto para rellenar la plantilla. Si se omite, el agente recoge con el usuario. |

## Comportamiento

1. Invoca **kata-contributing-issue** con tipo `user-story-for-api` (implícito por el nombre de este cry).
2. El kata usa la plantilla `.ahrena/contributing_templates/user-story-for-api.md`, la rellena con el usuario y crea la issue vía MCP de GitHub (o `gh`).

## Kata Asociado

`kata-contributing-issue` — Procedimiento para abrir issue usando una de las 4 plantillas (en este caso, user-story-for-api).

## Referencias

- `codex-contributing` — Flujo de contribución Guardia
- `kata-contributing-issue` — Kata invocado por este cry
- `.ahrena/contributing_templates/user-story-for-api.md` — Plantilla de la issue
