# Kata: Realizar Commit Estandarizado

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Creación de commits conformes con las Lexis de Guardia

## Objetivo

Este Kata define el procedimiento estandarizado para crear un commit que respete todas las Lexis de commit de Guardia — formato Conventional Commits, atomicidad, firma GPG e idioma.

## Cuándo Utilizar

- Cuando es necesario realizar un commit de cambios siguiendo los estándares de Guardia
- Cuando el usuario solicita ayuda para hacer commit de cambios
- Cuando es invocado por el `cry-commit`
- Cuando es invocado internamente por el `kata-contribute`

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Cambios | Sí | Archivos en staging o indicación de qué incluir en el commit |
| Tipo | No | Tipo Conventional Commits (feat, fix, docs, etc.). Si se omite, el agente lo infiere del diff |
| Alcance | No | Módulo o dominio afectado. Si se omite, el agente lo infiere del diff |
| Descripción | No | Texto del subject. Si se omite, el agente lo compone a partir del diff |
| `--warrior <nombre>` | No | Nombre del warrior que invoca el kata (ej.: `apollo`, `athena`, `hephaestus`). Habilita el ruteo bot-author cuando `bot_author.enabled=true` y el nombre está en `bot_author.apply_to`. Cuando se omite, el flujo es siempre commit local (humano). |

## Workflow

```
Progreso:
- [ ] 1. Análisis de los cambios
- [ ] 2. Clasificación y composición del mensaje
- [ ] 3. Validación contra las Lexis
- [ ] 4. Resolución del autor (humano o ahrena-bot)
- [ ] 5. Ejecución del commit
- [ ] 6. Verificación final
```

### Paso 1: Análisis de los Cambios

1. Ejecutar `git status` para verificar archivos en staging
2. Si no hay archivos en staging, analizar el diff y sugerir qué incluir con `git add`
3. Ejecutar `git diff --staged` para comprender el contenido de los cambios
4. Verificar que los cambios son atómicos (`lex-small-commits`):
   - ¿Todos los cambios pertenecen a un único propósito?
   - Si no, orientar al usuario para dividir en commits separados

### Paso 2: Clasificación y Composición del Mensaje

1. Consultar `codex-commit-standards` como referencia
2. **Identificar el tipo:** feat, fix, docs, build, chore, ci, style, refactor, perf, test
3. **Identificar el alcance:** módulo o dominio principal afectado (opcional)
4. **Componer el subject:**
   - Imperativo presente en inglés (`lex-commit-language`)
   - Máximo 72 caracteres
   - Sin punto final
   - Formato: `tipo(alcance): descripción`
5. **Componer el body (si es necesario):**
   - Versión en inglés con etiqueta `[en]`
   - Versión en idioma local con etiqueta `[pt-BR]` o `[es]` (si se solicita)
   - Detallar el "por qué" del cambio
6. **Agregar pies (si corresponde):**
   - `Closes #N` para cerrar issues
   - `BREAKING CHANGE:` para cambios incompatibles
   - `Co-authored-by:` para pair programming

### Paso 3: Validación contra las Lexis

Se debe verificar la conformidad con cada Lexis antes de ejecutar:

- [ ] `lex-conventional-commits`: ¿formato `tipo(alcance): descripción` correcto?
- [ ] `lex-small-commits`: ¿cambios atómicos (un único propósito)?
- [ ] `lex-commit-language`: ¿subject en inglés? ¿Etiqueta de idioma en el body?
- [ ] `lex-signed-commits`: ¿GPG configurado? (`git config --get commit.gpgsign` = true)

Si alguna validación falla, se debe corregir antes de continuar.

### Paso 4: Resolución del Autor (humano o ahrena-bot)

Antes de invocar `git commit`, el kata decide entre dos caminos de autoría:

1. **Cargar `scripts/ahrena-auth.sh`** (siempre — es no-op cuando `bot_author.enabled=false`):
   ```bash
   source scripts/ahrena-auth.sh
   ```
   Cuando la directiva está desactivada, el script retorna inmediatamente sin exportar nada. Cuando está activa, exporta `GH_TOKEN_AHRENA_BOT` (token de instalación del GitHub App) y las variables `GIT_AUTHOR_*` / `GIT_COMMITTER_*` apuntando a la identidad `ahrena-bot[bot]`.

2. **Leer `bot_author.enabled` y `bot_author.apply_to`** en `.ahrena/.directives`.

3. **Decisión de ruteo:**
   - Si `bot_author.enabled == true` Y el input `--warrior <nombre>` fue proporcionado Y `<nombre>` está en `bot_author.apply_to`: usar el **camino bot-author** (Paso 5a abajo).
   - En caso contrario (ausencia de `--warrior`, master switch desactivado o warrior fuera de `apply_to`): usar el **camino humano** (Paso 5b).

4. **Camino bot-author** — componer el `Co-authored-by` del humano que dirige la sesión:
   ```bash
   HUMAN_CO_AUTHOR="$(git config user.name) <$(git config user.email)>"
   ```
   Ese valor entra como trailer del commit en el Paso 5a.

### Paso 5: Ejecución del Commit

#### Paso 5a: Camino bot-author (servidor)

Cuando el ruteo del Paso 4 seleccionó el camino bot-author:

1. Invocar `scripts/ahrena-api-commit.sh` para crear el commit vía GitHub Git Data API:
   ```bash
   scripts/ahrena-api-commit.sh \
     --branch "$(git rev-parse --abbrev-ref HEAD)" \
     --message "$(cat <<'EOF'
   tipo(alcance): descripción

   [en]
   Detailed description in English.

   [es]
   Descripción detallada en español.

   Closes #123
   EOF
   )" \
     --co-author "${HUMAN_CO_AUTHOR}"
   ```

2. El script ejecuta `POST /git/blobs` (por archivo staged) → `POST /git/trees` → `POST /git/commits` → `PATCH /git/refs/heads/{branch}`. El commit resultante es firmado por el token de instalación del App (verificado por el servidor) y atribuido a `ahrena-bot[bot]`.

3. Exit codes del script:
   - `0` — commit creado con éxito en el remoto + working tree local sincronizada.
   - `2` — falla de red/API (commit NO creado). **Fallback obligatorio**: caer al Paso 5b (camino humano) y emitir aviso visible al usuario explicando la degradación.
   - `3` — commit creado en el remoto PERO el `git fetch && git reset --hard` local falló. Avisar al usuario para sincronizar manualmente antes del próximo push.

4. En caso de fallback por exit code `2`, el agente DEBE mantener el contenido de los archivos staged (no deshacer `git add`) y proseguir con el Paso 5b.

#### Paso 5b: Camino humano (local, firma GPG)

Cuando el ruteo del Paso 4 seleccionó el camino humano (o en el fallback del 5a):

1. Ejecutar el commit con firma GPG:
   ```
   git commit -S -m "<mensaje>"
   ```
2. Para mensajes multiline (con body), utilizar:
   ```
   git commit -S -m "$(cat <<'EOF'
   tipo(alcance): descripción

   [en]
   Detailed description in English.

   [es]
   Descripción detallada en español.

   Closes #123
   EOF
   )"
   ```

### Paso 6: Verificación Final

- [ ] `git log -1 --format='%s'` muestra el subject correcto
- [ ] **Camino humano (5b):** `git log -1 --show-signature` muestra firma GPG válida
- [ ] **Camino bot-author (5a):** `git log -1 --format='%an <%ae>'` muestra `ahrena-bot[bot]` y el commit aparece con el badge **Verified** en GitHub
- [ ] **Camino bot-author (5a):** el body del commit contiene el trailer `Co-authored-by: <humano>` cuando `bot_author.commit_co_author=human`
- [ ] El commit contiene solo los cambios previstos
- [ ] El subject está en inglés y sigue Conventional Commits
- [ ] El commit es atómico (un cambio lógico)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Commit firmado y formateado | Git commit | Repositorio local |

## Restricciones

- Nunca realizar un commit sin verificar la conformidad con las 4 Lexis
- Nunca mezclar cambios no relacionados en un único commit
- En el camino humano (Paso 5b), nunca realizar un commit sin firma GPG configurada — si GPG no está configurado, alertar al usuario y orientar la configuración
- En el camino bot-author (Paso 5a), la firma es provista por el token de instalación del GitHub App; no es necesario GPG local
- Nunca silenciar una falla del `ahrena-api-commit.sh` — siempre informar al usuario cuando hay fallback al camino humano

## Referencias

- `lex-conventional-commits` — Formato obligatorio
- `lex-signed-commits` — Firma GPG obligatoria (camino humano) o firma vía App (camino bot)
- `lex-small-commits` — Atomicidad obligatoria
- `lex-commit-language` — Idioma obligatorio
- `codex-commit-standards` — Guía completa de estándares
- `codex-git-workflow` — Sección "Author identity" describe el ruteo humano vs bot
- `scripts/ahrena-auth.sh` — Gate `bot_author.enabled` + resolución de credenciales del GitHub App
- `scripts/ahrena-api-commit.sh` — Commit vía Git Data API (camino bot-author)
- `cry-commit` — Atajo que invoca este Kata
