# Cry: Hacer Rebase

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Atajo para resolver conflictos y actualizar la branch vía rebase

## Invocación

```
/cry-rebase [base]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `base` | No | Referencia sobre la que hacer rebase (por defecto: branch de rastreo o `origin/main`) | `origin/main`, `upstream/develop` |

## Qué Hace el Comando

1. Invoca el **kata-rebase**, que encapsula el procedimiento de rebase y resolución de conflictos.
2. El procedimiento detallado (verificar estado, ejecutar rebase, resolver conflictos, verificación final) está en el Kata; el Cry no define pasos con comandos externos — solo invoca el Kata.
3. Mientras el `kata-rebase` esté pendiente de creación, el agente puede orientar al usuario con base en `codex-contributing`; al crearse, el Cry lo invocará exclusivamente.

## Ejemplos de Uso

```
# Rebase de la branch actual sobre origin/main
/cry-rebase

# Rebase sobre upstream/develop
/cry-rebase upstream/develop

# Tras conflicto en sync: rebase y luego push
/cry-rebase origin/main
```

## Kata Asociado

`kata-rebase` — Procedimiento completo de rebase con resolución de conflictos. **Pendiente de creación.**

## Referencias

- `cry-sync` — Sincronización del repositorio (fetch, pull, push); usar rebase cuando haya conflictos
- `codex-contributing` — Flujo de contribución (contexto del Cry)
