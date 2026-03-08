# Cry: Ejecutar Git Tag

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Atajo para crear o listar tags de release con versionado semántico

## Invocación

```
/cry-tag [versión] [mensaje] [commit]
/cry-tag --list
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|------------|:-----------:|-------------|---------|
| `versión` | No | Identificador SemVer (con o sin prefijo `v`) | `1.2.3`, `v1.2.3` |
| `mensaje` | No | Mensaje de anotación del tag | `"Release 1.2.3"` |
| `commit` | No | ID (hash) o mensaje (subject) del commit al que apuntará el tag; si se omite, usa HEAD | `abc123f`, `"feat(auth): add OAuth2"` |
| `--list` | — | Listar tags existentes (no crea tag) | `/cry-tag --list` |

Si se pasa `--list`, el comando solo lista los tags (ej.: `git tag -l --sort=-v:refname`). En caso contrario, invoca `kata-tag` para crear un nuevo tag.

Si la versión se omite al crear tag, el agente sugiere la próxima versión con base en el historial de tags y commits (consultando `codex-semantic-version`). Si se informa `commit`, el agente resuelve el ID o la mensaje a un commit válido y apunta el tag a él.

## Ejemplos de Uso

```
# Crear tag con versión y mensaje
/cry-tag v1.2.3 "Release 1.2.3"

# Crear tag apuntando a un commit por hash
/cry-tag v1.2.3 "Release 1.2.3" abc123f

# Crear tag apuntando a un commit por mensaje (subject)
/cry-tag v1.2.3 "Release 1.2.3" "feat(auth): add OAuth2"

# Crear tag solo con versión (mensaje por defecto, HEAD)
/cry-tag v1.2.3

# Sugerencia automática — el agente determina la próxima versión y confirma
/cry-tag

# Listar tags
/cry-tag --list
```

## Comportamiento

**Al crear tag (sin `--list`):**

1. Invoca `kata-tag` pasando versión, mensaje y commit (si se proporcionan)
2. Si la versión se omite, el agente analiza el historial y sugiere la próxima versión conforme a `codex-semantic-version`
3. Valida contra `lex-semantic-version` y `lex-signed-commits`
4. Crea el tag anotado y firmado e informa cómo publicar (`git push origin <versión>`)

**Al listar (`--list`):**

1. Ejecuta `git tag -l` (opcionalmente con ordenación por versión, ej.: `--sort=-v:refname`)
2. Muestra la lista de tags; no ejecuta el Kata de creación

## Kata Asociado

`kata-tag` — Procedimiento completo para aplicar versionado semántico con git tags

## Referencias

- `kata-tag` — Procedimiento ejecutado por este Cry al crear tag
- `lex-semantic-version` — Formato SemVer obligatorio
- `lex-signed-commits` — Firma GPG en tags de release
- `codex-semantic-version` — Guía de referencia para SemVer y git tags
