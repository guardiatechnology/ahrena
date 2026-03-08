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

## Comportamiento

El comando orienta la resolución de conflictos usando rebase:

1. **Verificar estado:** confirmar que hay conflictos o que la branch está detrás del remoto (ej.: tras un pull con divergencia).
2. **Ejecutar rebase:** `git rebase <base>` — reaplica los commits locales encima de `<base>`.
3. **Resolver conflictos (si los hay):** en cada conflicto, el agente ayuda a editar archivos, `git add` y `git rebase --continue`; o `git rebase --abort` para cancelar.
4. **Verificación final:** tras terminar el rebase, informar que el usuario puede hacer `git push` (posiblemente `--force-with-lease` si la branch ya había sido enviada).

Si el usuario invocó `/cry-sync` y hubo conflicto en el pull, usar este Cry para hacer rebase sobre el remoto y luego completar el push.

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
- `codex-contributing` — Flujo de contribución
