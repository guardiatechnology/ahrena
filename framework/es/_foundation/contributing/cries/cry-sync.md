# Cry: Sincronizar Repositorio

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Atajo para sincronizar el repositorio local con el remoto (fetch, pull, push)

## Invocación

```
/cry-sync [remote] [branch]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `remote` | No | Nombre del remoto (por defecto: `origin`) | `origin`, `upstream` |
| `branch` | No | Branch a sincronizar (por defecto: branch actual) | `main`, `develop` |

## Qué Hace el Comando

1. Invoca el **kata-sync**, que encapsula el procedimiento de sincronización del repositorio (fetch, pull, push y tratamiento de conflictos).
2. El procedimiento detallado está en el Kata; el Cry no define pasos con comandos externos — solo invoca el Kata.
3. Mientras el `kata-sync` esté pendiente de creación, el agente puede orientar al usuario con base en `codex-contributing`; al crearse, el Cry lo invocará exclusivamente.

## Ejemplos de Uso

```
# Sincronizar branch actual con origin
/cry-sync

# Sincronizar main con origin
/cry-sync origin main

# Sincronizar con remoto upstream
/cry-sync upstream main
```

## Kata Asociado

`kata-sync` — Procedimiento completo de sincronización (fetch, pull, push y tratamiento de conflictos). **Pendiente de creación.**

## Referencias

- `cry-rebase` — Usar cuando haya conflictos tras el pull para resolver vía rebase
- `codex-contributing` — Flujo de contribución (contexto del Cry)
