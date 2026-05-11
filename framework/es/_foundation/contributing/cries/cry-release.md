# Cry: Publicar Release

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Atajo para invocar `warrior-janus` y cerrar el ciclo de entrega — análisis de commits, propuesta de bump SemVer, aprobación humana y publicación de tag anotado/firmado + GitHub Release

## Invocación

```
/cry-release [--type major|minor|patch] [--dry-run]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `--type` | No | Sobrescribe la heurística de bump SemVer calculada a partir de los commits. Valores: `major`, `minor`, `patch` | `--type minor` |
| `--dry-run` | No | Presenta la propuesta sin persistir nada (sin crear archivo de changelog draft, sin crear tag, sin empujar) | `--dry-run` |

Si se proporciona `--type`, `warrior-janus` exhibe **tanto la heurística calculada como el override** para que el humano pueda comparar antes de aprobar. Sin flags, Janus usa solamente la heurística.

Si se proporciona `--dry-run`, el comando finaliza tras presentar la propuesta — ninguna escritura persistente ocurre.

## Ejemplos de Uso

```
# Flujo completo: análisis + gate humano + publicación
/cry-release

# Override de bump (el humano sabe que merece major aún sin BREAKING CHANGE)
/cry-release --type major

# Preview sin efectos colaterales
/cry-release --dry-run

# Override + dry-run combinados
/cry-release --type minor --dry-run
```

## Comportamiento

1. Invoca `warrior-janus`.
2. Janus ejecuta `kata-release-prepare`:
   - `git fetch --tags`, identifica el último tag SemVer
   - Recolecta y clasifica los commits desde el último tag (Conventional Commits)
   - Calcula el bump heurístico; aplica el override (`--type`) cuando está presente
   - Genera el changelog draft (en archivo, excepto en `--dry-run`)
   - Verifica el CI del trunk y lista los PRs abiertos
3. Janus presenta la propuesta estructurada y aguarda **aprobación humana explícita** ("sí" / "editar" / "cancelar").
4. En `--dry-run`, finaliza tras presentar la propuesta.
5. Tras "sí", Janus ejecuta `kata-release-publish`:
   - Crea tag anotado + firmado vía `kata-tag`
   - Empuja a `origin`
   - Aguarda `validate-tag.yml` (server-side, `lex-annotated-tags`)
   - Detecta workflow de release en el repo destino; aguarda Release auto-generado O hace fallback `gh release create`
   - Sobrescribe notas solo si el draft es sustancialmente más informativo
6. Reporta URL del Release, camino seguido y estado final.

## Warrior Asociado

`warrior-janus` — orquesta los dos Katas con gate humano explícito entre ellos.

## Referencias

- `warrior-janus` — Warrior invocado por este Cry
- `kata-release-prepare` — Fase 1 (análisis + propuesta)
- `kata-release-publish` — Fase 2 (publicación tras aprobación)
- `lex-annotated-tags` — Ley que gobierna la validez del tag empujado
- `lex-semantic-version`, `lex-signed-commits`, `lex-conventional-commits` — Lexis consultadas en todo el flujo
