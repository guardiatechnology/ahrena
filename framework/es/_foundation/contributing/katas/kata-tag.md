# Kata: Aplicar Versionado Semántico con Git Tag

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Creación de tags de release conformes con lex-semantic-version y lex-signed-commits

## Objetivo

Este Kata define el procedimiento estandarizado para aplicar versionado semántico en el proyecto usando git tags: determinar la próxima versión (o usar la indicada), validar contra las Lexis y crear tag anotada y firmada.

## Cuándo Usar

- Cuando es necesario crear un tag de release siguiendo Semantic Versioning 2.0
- Cuando el usuario solicita ayuda para marcar una versión en el repositorio
- Cuando es invocado por `cry-tag` para crear tag (no para listar)

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Versión | No | Identificador SemVer (ej.: `1.2.3` o `v1.2.3`). Si se omite, el agente sugiere con base en el historial de tags y commits |
| Mensaje | No | Mensaje de anotación del tag. Si se omite, usar mensaje por defecto (ej.: "Release X.Y.Z") |
| Commit | No | ID (hash) o mensaje (subject) del commit al que apuntará el tag. Si se omite, usar HEAD |

## Workflow

```
Progreso:
- [ ] 1. Verificar estado del repositorio
- [ ] 2. Determinar próxima versión
- [ ] 3. Validar formato contra lex-semantic-version
- [ ] 4. Crear tag anotada y firmada
- [ ] 5. Verificación final
```

### Paso 1: Verificar Estado del Repositorio y Resolver el Commit Objetivo

1. Ejecutar `git status` para confirmar que no hay cambios sin commitear que deban entrar en el release (o que el usuario está al tanto)
2. Ejecutar `git tag -l` (o `git tag -l --sort=-v:refname`) para listar tags existentes y obtener la última versión
3. **Resolver el commit donde se creará el tag:**
   - Si el usuario indicó **commit** (ID o mensaje): resolver a un hash válido.
     - Si es un hash (o abreviatura): `git rev-parse <ref>` para obtener el commit.
     - Si es mensaje (subject): buscar commit cuyo subject corresponda, ej.: `git log -1 --all --format=%H --grep="<mensaje>"` o búsqueda por subject; si hay varios resultados, usar el más reciente o pedir confirmación al usuario.
   - Si **commit** se omitió: usar HEAD (`git rev-parse HEAD`).
4. Opcional: ejecutar `git log <último-tag>..<commit-objetivo> --oneline` para ver commits desde el último tag (útil para sugerir versión)

### Paso 2: Determinar Próxima Versión

1. Consultar `codex-semantic-version` para reglas de incremento
2. Si el usuario indicó la versión, usarla (normalizar al formato adoptado por el proyecto, ej.: con o sin `v`)
3. Si la versión se omitió:
   - Obtener el último tag en formato SemVer
   - Analizar los commits desde ese tag (ej.: `git log <último-tag>..HEAD --pretty=format:'%s'`)
   - Aplicar la tabla del codex: BREAKING CHANGE / feat! / fix! → MAJOR; feat → MINOR; fix/perf/etc. → PATCH
   - Si no hay último tag, sugerir `v1.0.0` (o `1.0.0`) como primera versión
4. Garantizar que el identificador está en formato MAJOR.MINOR.PATCH (con o sin prefijo `v`)

### Paso 3: Validación contra lex-semantic-version

Antes de crear el tag, verificar:

- [ ] El identificador sigue Semantic Versioning 2.0 (MAJOR.MINOR.PATCH)
- [ ] No es un formato inválido (ej.: `release-1.2`, `1.2`, `latest`)
- [ ] Pré-release o metadatos (si se usan) siguen la especificación SemVer 2.0
- [ ] El tag aún no existe en el repositorio (`git tag -l '<versión>'` vacío)

Si alguna validación falla, corregir o orientar al usuario antes de continuar.

### Paso 4: Crear Tag Anotada y Firmada

1. Verificar que GPG está configurado para firma de tags (`lex-signed-commits`): `git config --get user.signingkey`
2. Si no está configurado, alertar al usuario y orientar la configuración; no crear tag sin firma
3. Definir el mensaje del tag: usar el mensaje proporcionado por el usuario o por defecto (ej.: "Release 1.2.3")
4. Usar el **commit objetivo** resuelto en el Paso 1 (HEAD o el commit indicado por el usuario).
5. Ejecutar:
   ```
   git tag -s <versión> <commit-objetivo> -m "<mensaje>"
   ```
   Ejemplo (tag en HEAD): `git tag -s v1.2.3 -m "Release 1.2.3"` (equivale a `git tag -s v1.2.3 HEAD -m "Release 1.2.3"`).
   Ejemplo (tag en commit específico): `git tag -s v1.2.3 abc123f -m "Release 1.2.3"`

### Paso 5: Verificación Final

- [ ] El tag existe: `git tag -l '<versión>'` devuelve la versión
- [ ] El tag está firmado: `git tag -v <versión>` (o `git show <versión>`) muestra verificación GPG
- [ ] El formato es correcto conforme a `lex-semantic-version`
- [ ] Informar al usuario que para publicar el tag es necesario: `git push origin <versión>`

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Tag creada | Git tag (anotada y firmada) | Repositorio local |
| Instrucción de push | Texto | Ej.: "Para publicar: git push origin v1.2.3" |

## Restricciones

- Nunca crear tag de release sin conformidad con `lex-semantic-version` (formato SemVer 2.0)
- Nunca crear tag de release sin firma GPG; seguir `lex-signed-commits`
- Si el usuario pide solo listar tags (ej.: vía `cry-tag --list`), no ejecutar este Kata de creación; solo listar con `git tag -l` (y opcionalmente `-n` u ordenación)
- Referenciar siempre `codex-semantic-version` y `lex-semantic-version` al sugerir o validar versión

## Referencias

- `lex-semantic-version` — Formato SemVer obligatorio para releases
- `lex-signed-commits` — Firma GPG obligatoria para tags de release
- `codex-semantic-version` — Manual de referencia para SemVer y git tags
- `cry-tag` — Atajo que invoca este Kata para crear tag (y listar tags)
