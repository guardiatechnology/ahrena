# Kata: Build de skill (fuente → `.build/{slug}/` + zip)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Implementación operacional del pipeline determinístico de build descrito en `codex-skill-build-pipeline`. Lee `{paths.skills_root}/{slug}/`, valida manifests, compila widgets, congela scripts, valida tools y emite `{paths.skills_build}/{slug}/` + zip testeable

## Objetivo

Producir un `.build/{slug}/` byte-determinístico (misma fuente → mismo output) y un `.build/{slug}.zip` que puede cargarse en otro agente Claude Code (o equivalente) para test manual end-to-end antes del empaquetado final en `.dist/` (PR 3).

## Cuándo Usar

- Cuando el usuario invoca `/cry-skill-build <slug>`
- Cuando la integración continua requiere generar zip testeable
- Antes de invocar `kata-package-skill` (PR 3) para producir entrega final

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `slug` | Sí | Proyecto en `{paths.skills_root}/{slug}/` |
| `clean` | No | `true` borra `.build/{slug}/` antes de comenzar; default `false` (build incremental aprovechando cache de Vite) |
| `skip_zip` | No | `true` omite la Phase 6 del zip (útil cuando el consumidor es solo `kata-package-skill`); default `false` |

## Workflow

```
Progreso:
- [ ] 1. Resolver paths y config
- [ ] 2. Phase 1 — Validate
- [ ] 3. Phase 2 — Build widgets
- [ ] 4. Phase 3 — Freeze scripts
- [ ] 5. Phase 4 — Resolve tools
- [ ] 6. Phase 5 — Rewrite bindings
- [ ] 7. Phase 6 — Emit (.build/ + zip)
- [ ] 8. Validar idempotencia
- [ ] 9. Reportar
```

### Paso 1: Resolver paths y config

1. Leer `.ahrena/.directives` para `paths.skills_root`, `paths.skills_build`
2. Confirmar que `{paths.skills_root}/{slug}/` existe
3. Leer `skill.config.json`; aplicar overrides
4. Si `clean=true`, remover `{paths.skills_build}/{slug}/` antes de proseguir
5. Garantizar que `{paths.skills_build}/{slug}/` existe (crear)

### Paso 2: Phase 1 — Validate

Per `codex-skill-build-pipeline` (Phase 1):

1. **`SKILL.md`**: parsear frontmatter; validar `name` (regex spec), `description` (1-1024), `compatibility` (≤500 cuando esté presente), `metadata.version` (semver), `metadata.language` (BCP 47)
2. **`skill.config.json`**: `schema_version: 1`, `runtimes.scripts` en `python|node`, ports presentes
3. **`tools/mcp.config.json`** (cuando `tools/` existe): `schema_version: 1`, cada `tools[].name` en snake_case, `tools[].input_schema` es JSON Schema válido, `tools[].handler` apunta a archivo+función existente
4. **`widgets/manifest.json`** (cuando `widgets/` existe): `schema_version: 1`, cada `components[].entry` apunta a archivo existente, cada `bindings[]` referencia tool o script existente
5. **`description` en SKILL.md**: avisar (no abortar) si < 30 chars (heurística de calidad per spec — descripciones cortas reducen activación)

En cualquier fallo, abortar con error específico citando la regla (`codex-skill-anthropic-agent-skills` para frontmatter, `codex-skill-tools-and-widgets` para manifests).

### Paso 3: Phase 2 — Build widgets

Cuando `widgets/` existe:

1. `cd {paths.skills_root}/{slug}/widgets`
2. Garantizar `node_modules/` (ejecutar `npm install` o `pnpm install` cuando esté ausente)
3. Ejecutar `vite build --mode production` (config estándar; override vía `vite.config.ts` si el autor declaró)
4. Output esperado: `widgets/dist/`
5. Copiar `widgets/dist/` a `{paths.skills_build}/{slug}/widgets/`
6. Reescribir `widgets/manifest.json` en `.build/`:
   - `components[].entry` apunta al archivo compilado correspondiente en `dist/`
   - `bindings[]` preservados; el rewrite ocurre en la Phase 5
7. Copiar `manifest.json` reescrito a `.build/{slug}/widgets/manifest.json`

### Paso 4: Phase 3 — Freeze scripts

Cuando `scripts/` existe:

1. Para Python (`runtimes.scripts: python`):
   - Confirmar `scripts/uv.lock` (generar con `uv lock` cuando esté ausente, abortando si el autor no permitió mutación)
   - Copiar `scripts/src/`, `scripts/pyproject.toml`, `scripts/uv.lock` a `.build/{slug}/scripts/`
2. Para Node (`runtimes.scripts: node`):
   - Confirmar lockfile (`package-lock.json` o `pnpm-lock.yaml`)
   - Copiar `scripts/src/`, `scripts/package.json`, lockfile a `.build/{slug}/scripts/`
3. No instalar dependencias en `.build/` (el consumidor instala en la carga)

### Paso 5: Phase 4 — Resolve tools

Cuando `tools/` existe:

1. Validar cada `tools[].handler` (path:funcion existe y es callable)
2. Copiar `tools/mcp.config.json` a `.build/{slug}/tools/`
3. Copiar `tools/handlers/` a `.build/{slug}/tools/handlers/` (preservar estructura)
4. Cuando el handler es Python y `runtimes.scripts: python`, reusar `uv.lock` de `scripts/` (los handlers pueden importar de `scripts/src/`)

### Paso 6: Phase 5 — Rewrite bindings

En `widgets/manifest.json` (ya en `.build/`):

1. Para cada binding `kind: script`:
   - Remover `called_via` (URL localhost de dev)
   - Añadir `called_via_prod`: path relativo al consumidor (default `./scripts/src/{filename}.{ext}`)
   - Cuando `skill.config.json.build.prefer_tool_over_script: true`, marcar como `via_tool: true` para que el host invoque la tool MCP equivalente en lugar de ejecutar script directo

En `SKILL.md` (copia en `.build/{slug}/SKILL.md`):

1. Añadir encabezado de aviso (después del frontmatter, antes del cuerpo) cuando `tools/` o `widgets/` esté presente:

   ```markdown
   > **Note:** This skill bundles `tools/` (MCP) and/or `widgets/` (React) as
   > Ahrena convention. Agents that only know the Anthropic Agent Skills spec
   > ignore those directories. See codex-skill-tools-and-widgets in the source
   > framework for binding semantics.
   ```

2. Validar que los paths citados en el cuerpo (`scripts/...`, `tools/...`, `widgets/...`) existen en `.build/`

### Paso 7: Phase 6 — Emit (.build/ + zip)

1. Escribir `.build/{slug}/.skill-manifest.json`:
   ```json
   {
     "schema_version": 1,
     "skill": { "name": "{slug}", "version": "...", "language": "..." },
     "framework": { "ahrena_commit": "{HEAD-da-fonte}" },
     "references": [],
     "files": [
       { "path": "SKILL.md", "sha256": "..." },
       { "path": "widgets/dist/index.js", "sha256": "..." },
       ...
     ]
   }
   ```
   `references[]` permanece vacío — completado por `kata-package-skill` (PR 3).
   `files[]` listado en orden **lexicográfico** de los paths.
2. Cuando `skip_zip=false`:
   - `mtime` de cada archivo en el zip fijado en `1980-01-01T00:00:00Z` (mínimo del formato)
   - Comando: `cd .build/{slug} && find . -type f | LC_ALL=C sort | zip -X --no-extra -@ ../{slug}.zip` (o equivalente cross-platform)
   - Output: `{paths.skills_build}/{slug}.zip`

### Paso 8: Validar idempotencia

1. Calcular sha256 del `.build/{slug}/{slug}.zip` (o de todo el árbol cuando `skip_zip=true`)
2. Comparar con el hash registrado en `.skill-manifest.json` (si lo hay de ejecución anterior)
3. En caso de drift inesperado, alertar — posibles causas: timestamps no fijados, ordering de filesystem, source maps con paths absolutos

### Paso 9: Reportar

```
✅ Build de {slug} concluido.
   Salida: {paths.skills_build}/{slug}/
   Zip:   {paths.skills_build}/{slug}.zip   (X.X MB)
   sha256: <hash>

Contenido:
   - SKILL.md (encabezado de aviso añadido)
   - widgets/dist/ (Vite production)
   - scripts/ (Python uv frozen)
   - tools/ (3 handlers validados)
   - .skill-manifest.json (8 files; references vacías hasta PR 3)

Próximos pasos:
   - Cargar el zip en otro agente Claude Code para test manual
   - kata-package-skill (PR 3) entrega .dist/{slug}.skill auditable
```

## Salidas

| Salida | Formato |
|--------|---------|
| Éxito | `.build/{slug}/` poblado + zip + manifest con hashes |
| Fallo (Phase 1) | Error específico de validación; nada escrito en `.build/` |
| Fallo (Phase 2) | Salida de Vite propagada; el build aborta |
| Fallo (Phase 3) | Lockfile ausente — instrucción para generar |
| Fallo (Phase 4) | Handler ref inválida — apuntar al handler faltante |
| Fallo (Phase 5) | Bindings inconsistentes (apuntan a archivo que desapareció) |
| Fallo de idempotencia | Alerta con causa probable; el build sobrevive pero indica investigar |

## Ejemplo de Ejecución

```
/cry-skill-build hello-skill
```

```
✅ Build de hello-skill concluido.
   Salida: .build/hello-skill/
   Zip:   .build/hello-skill.zip   (124 KB)
   sha256: 7a8c…
```

## Restricciones

- El build es **solo lectura** sobre `{paths.skills_root}/{slug}/`
- No toca `.dist/`
- Aborta en el primer fallo; nunca emite parcial
- El determinismo es criterio no negociable (`codex-skill-build-pipeline` § "Determinismo en el build"); cobertura completa en PR 3 (`lex-skill-export-determinism`)
- Los logs de aplicación siguen `lex-logging-decorator`; la salida del CLI del kata es excepción (boundary)
- `lex-terminal-type`: comandos shell en la sintaxis correcta

## Referencias

- `codex-skill-build-pipeline` — contrato del pipeline (defaults, fases, determinismo)
- `codex-skill-tools-and-widgets` — schemas validados en la Phase 1
- `codex-skill-anthropic-agent-skills` — frontmatter validado en la Phase 1
- `codex-skill-project-architecture` — flujo dev → build → dist
- `codex-python-tooling` — uv como runtime de Python
- `lex-skill-project-structure` — separación fuente/build/dist
- `lex-skill-export-determinism` (PR 3) — determinismo de la entrega final
- `cry-skill-build` — atajo del usuario
- `kata-skill-dev-server` — paso anterior natural; valida manualmente antes del build
- `kata-package-skill` (PR 3) — consumidor de `.build/` para producir `.dist/`
