# Kata: Contribuir Pilar al Framework

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Envío de Pilares al repositorio del Ahrena

## Objetivo

Este Kata define el procedimiento estandarizado para contribuir un Pilar (o conjunto de Pilares) al repositorio del framework Ahrena — incluyendo validación, commit y envío vía PR o commit directo dependiendo del rol del contribuidor.

## Cuándo Utilizar

- Cuando un nuevo Pilar fue creado (vía `kata-create-*`) y necesita ser incorporado al framework
- Cuando el usuario solicita enviar una contribución al repositorio del Ahrena
- Cuando es invocado por el `cry-contribute`

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Ruta del Pilar | Sí | Ruta del artefacto principal en el idioma predeterminado (ej: `framework/pt-BR/.../lex-example.md`) |
| Mensaje | No | Descripción de la contribución. Si se omite, el agente la compone a partir del Pilar |

## Workflow

```
Progreso:
- [ ] 1. Validación del Pilar
- [ ] 2. Verificación de i18n
- [ ] 3. Detección de permiso
- [ ] 4. Commit de los cambios
- [ ] 5. Envío
- [ ] 6. Verificación final
```

### Paso 1: Validación del Pilar

1. Verificar que el artefacto sigue el template oficial (`lex-template-usage`):
   - Identificar el Pilar por el prefijo del archivo
   - Leer el template correspondiente (`templates/{pilar}-sample.md`)
   - Verificar que todas las secciones obligatorias están presentes
2. Verificar que el artefacto está en la ruta correcta de la taxonomía:
   - Sigue el direccionamiento `{lang}/{clade}/{subclade}/{pilar}/{prefijo}-{nombre}.md`
   - Utiliza kebab-case
   - Utiliza el prefijo correcto del Pilar
3. Verificar que no contradice Lexis existentes
4. Verificar que no duplica artefactos existentes

### Paso 2: Verificación de i18n

1. Leer `.ahrena/.directives` para obtener `language.i18n`
2. Para cada idioma obligatorio, verificar que existe la versión traducida:
   - `framework/pt-BR/.../{artefacto}.md`
   - `framework/es/.../{artefacto}.md`
   - `framework/en/.../{artefacto}.md`
3. Si faltan traducciones, alertar y sugerir utilizar `kata-translate` o `cry-translate`

### Paso 3: Detección de Permiso

1. Verificar si el repositorio actual es el Ahrena:
   ```
   git remote get-url origin
   ```
2. Verificar si el usuario es codeowner consultando `.github/CODEOWNERS`
3. Opcionalmente, verificar vía API:
   ```
   gh api repos/{owner}/{repo}/collaborators/{username}/permission
   ```
4. Determinar el camino:
   - **Codeowner:** commit directo + push
   - **Contribuidor externo:** branch + PR

### Paso 4: Commit de los Cambios

1. Ejecutar `git add` para los archivos del Pilar (todas las versiones i18n)
2. Invocar `kata-commit` con:
   - Tipo: `docs` (para artefactos del framework)
   - Alcance: nombre del Pilar (ej: `lex-conventional-commits`)
   - Descripción en inglés describiendo la contribución

### Paso 5: Envío

**Si es codeowner:**
1. Push directo al branch:
   ```
   git push origin HEAD
   ```

**Si es contribuidor externo:**
1. Crear branch:
   ```
   git checkout -b docs/{pilar-name}
   ```
2. Push al fork:
   ```
   git push -u origin docs/{pilar-name}
   ```
3. Abrir PR:
   ```
   gh pr create --title "docs({pilar}): add {name}" --body "..."
   ```
4. Completar el body del PR con:
   - Qué: descripción del Pilar
   - Por qué: justificación
   - Referencias: issue o discusión relacionada

### Paso 6: Verificación Final

- [ ] El Pilar sigue el template oficial (`lex-template-usage`)
- [ ] Existe versión en todos los idiomas de `language.i18n`
- [ ] El commit sigue las 4 Lexis de commit
- [ ] El commit está firmado (GPG verified)
- [ ] El envío fue realizado (push o PR creado)
- [ ] CI está pasando (si corresponde)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Commit(s) firmado(s) | Git commit | Repositorio local/remoto |
| PR (si es contribuidor externo) | GitHub Pull Request | Repositorio del Ahrena |

## Restricciones

- Nunca enviar un Pilar sin validación completa (template + i18n)
- Nunca omitir la firma GPG
- Si hay duda sobre el Clade/Subclade correcto, escalar a humano
- Si el Pilar contradice una Lexis existente, escalar a humano

## Referencias

- `codex-contributing` — Flujo de contribución Guardia
- `codex-commit-standards` — Estándares de mensaje de commit
- `kata-commit` — Procedimiento para realizar commits conformes
- `lex-template-usage` — Ley de uso obligatorio de templates
- `lex-framework-language` — Ley de estructura de idiomas
- `warrior-framework-curator` — Agente que ejecuta este Kata
- `cry-contribute` — Atajo que invoca este Kata
