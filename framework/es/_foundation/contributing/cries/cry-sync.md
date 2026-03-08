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

## Comportamiento

El comando ejecuta, **en este orden**:

1. **Fetch:** `git fetch <remote>` — actualiza referencias y objetos del remoto sin alterar la working tree.
2. **Pull:** `git pull <remote> <branch>` — trae y hace merge (o rebase, según config) de los commits del remoto a la branch actual.
3. **Push:** `git push <remote> <branch>` — envía los commits locales al remoto.

Si hay conflictos en el pull, el agente informa y orienta el uso de `/cry-rebase` para resolver antes de intentar el push.

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
- `codex-contributing` — Flujo de contribución
