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

## Workflow

```
Progreso:
- [ ] 1. Análisis de los cambios
- [ ] 2. Clasificación y composición del mensaje
- [ ] 3. Validación contra las Lexis
- [ ] 4. Ejecución del commit
- [ ] 5. Verificación final
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

### Paso 4: Ejecución del Commit

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

### Paso 5: Verificación Final

- [ ] `git log -1 --format='%s'` muestra el subject correcto
- [ ] `git log -1 --show-signature` muestra firma GPG válida
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
- Nunca realizar un commit sin firma GPG configurada
- Si GPG no está configurado, alertar al usuario y orientar la configuración

## Referencias

- `lex-conventional-commits` — Formato obligatorio
- `lex-signed-commits` — Firma GPG obligatoria
- `lex-small-commits` — Atomicidad obligatoria
- `lex-commit-language` — Idioma obligatorio
- `codex-commit-standards` — Guía completa de estándares
- `cry-commit` — Atajo que invoca este Kata
