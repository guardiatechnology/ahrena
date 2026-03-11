# Cry: Nueva Discusión

> **Prefijo:** `cry-` | **Tipo:** Comando Recorrente | **Alcance:** Atajo para abrir discusión en GitHub Discussions (Golden Circle)

## Invocación

```
/cry-new-discuss [QUÉ] [POR QUÉ] [CÓMO]
```

## Parámetros

| Parámetro | Obligatorio | Descripción |
|-----------|:-----------:|-------------|
| QUÉ / POR QUÉ / CÓMO | No | Si se proporcionan, el agente los usa para estructurar la discusión. En caso contrario, recoge con el usuario. |

## Comportamiento

1. Invoca **kata-contributing-discuss**.
2. El kata estructura la propuesta en el Golden Circle (QUÉ, POR QUÉ, CÓMO) y crea la discusión en GitHub Discussions vía MCP de GitHub cuando esté disponible (o indica apertura manual).

## Kata Asociado

`kata-contributing-discuss` — Procedimiento para abrir discusión en GitHub Discussions (Golden Circle).

## Referencias

- `codex-contributing` — Flujo de contribución Guardia (contexto del Cry)
- `kata-contributing-discuss` — Procedimiento ejecutado por este Cry (ver documentación del Kata)
- Golden Circle — QUÉ, POR QUÉ, CÓMO
