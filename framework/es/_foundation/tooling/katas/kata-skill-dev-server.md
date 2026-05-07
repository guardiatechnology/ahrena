# Kata: Dev server local de skill (widgets HMR + script runner + tools stub)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Levantar entorno de desarrollo local para un proyecto de skill en `{paths.skills_root}/{slug}/`, con widgets en HMR (Vite), script runner HTTP/JSON y tool stub MCP, conforme `codex-skill-build-pipeline`

## Objetivo

Permitir iteración rápida en un proyecto de skill levantando, en una única invocación, los tres servidores que cubren widgets, scripts y tools. El kata respeta los opt-outs del `skill.config.json` — si el proyecto no tiene `widgets/`, el servidor de widgets no se levanta; ídem para scripts y tools.

## Cuándo Usar

- Cuando el usuario invoca `/cry-skill-dev <slug>`
- Antes de ejecutar `kata-build-skill`, para validar widgets, scripts y tools manualmente
- Cuando se ajustan bindings en `widgets/manifest.json` y se valida `called_via`

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `slug` | Sí | Nombre del proyecto en `{paths.skills_root}/{slug}/` |
| `widgets_port` | No | Override de port de los widgets (default: `skill.config.json` → `dev_server.widgets_port` → `5173`) |
| `scripts_port` | No | Override de port del script runner (default: `5174`) |
| `tools_stub_port` | No | Override de port del tool stub (default: `5175`) |
| `only` | No | Subconjunto a levantar (`widgets`, `scripts`, `tools`); default: todos los disponibles |

## Workflow

```
Progreso:
- [ ] 1. Resolver proyecto y config
- [ ] 2. Verificar precondiciones (paths, manifests, ports libres)
- [ ] 3. Levantar widgets (Vite dev) cuando aplica
- [ ] 4. Levantar script runner cuando aplica
- [ ] 5. Levantar tool stub cuando aplica
- [ ] 6. Reportar URLs e instrucciones
- [ ] 7. Acompañar hasta que el usuario indique parar
```

### Paso 1: Resolver proyecto y config

1. Leer `.ahrena/.directives` para resolver `paths.skills_root` (default `skills`)
2. Confirmar que `{paths.skills_root}/{slug}/` existe; abortar si no
3. Leer `{paths.skills_root}/{slug}/skill.config.json`; aplicar overrides de input sobre los valores del archivo
4. Resolver subconjuntos vía `only` o por la presencia de `widgets/`, `scripts/`, `tools/`

### Paso 2: Verificar precondiciones

1. Para widgets: confirmar `widgets/package.json`, `widgets/manifest.json`, `widgets/src/`; verificar si `node_modules/` existe (ejecutar `npm install` o `pnpm install` cuando esté ausente)
2. Para scripts (Python): confirmar `scripts/pyproject.toml` o `scripts/uv.lock` (ejecutar `uv sync` cuando sea necesario)
3. Para scripts (JS): confirmar `scripts/package.json`; ejecutar install si está ausente
4. Para tools: confirmar `tools/mcp.config.json` válido (JSON Schema de cada tool); confirmar handler refs existentes
5. Verificar disponibilidad de ports (lsof / netstat conforme `lex-terminal-type`); si está ocupada, sugerir override

### Paso 3: Levantar widgets (Vite dev) cuando `widgets/` existe y `only` lo permite

1. Comando: `cd {paths.skills_root}/{slug}/widgets && vite --port {widgets_port} --host`
2. Vite carga `vite.config.ts` (si existe) o usa defaults; React + TS detectados automáticamente
3. HMR activo; logs propagados al usuario
4. URL expuesta: `http://localhost:{widgets_port}/`

### Paso 4: Levantar script runner cuando `scripts/` existe y `only` lo permite

El script runner es servidor HTTP/JSON minimal que expone cada script como endpoint:

| `runtimes.scripts` | Implementación default | Comando |
|--------------------|------------------------|---------|
| `python` | `uv run` + servidor liviano (FastAPI o stdlib http.server) | `cd {paths.skills_root}/{slug}/scripts && uv run python -m skill_runner --port {scripts_port}` (módulo `skill_runner` es parte del scaffold cuando el autor opta por Python; cuando está ausente, el kata apunta al autor a `codex-skill-build-pipeline`) |
| `node` | Express/Fastify/server stdlib | `cd {paths.skills_root}/{slug}/scripts && npm run dev:server -- --port {scripts_port}` |

Ruteo:

- Cada archivo en `scripts/src/` exporta una función handler nombrada
- Endpoint default: `POST /{filename-sin-extension}`
- Body: JSON validado por el runner contra schema (cuando se declara en `widgets/manifest.json`)

URL expuesta: `http://localhost:{scripts_port}/`

### Paso 5: Levantar tool stub cuando `tools/` existe y `only` lo permite

El tool stub es un servidor MCP local mockeado:

1. Lee `tools/mcp.config.json`
2. Para cada tool declarada, expone endpoint `POST /tools/{tool_name}`
3. Respuesta default: eco de la entrada con flag `_stub: true`; el autor sobreescribe en `tools/handlers/{tool_name}_stub.py` (o `.js`) cuando requiere comportamiento específico
4. URL expuesta: `http://localhost:{tools_stub_port}/`

El tool stub es exclusivo del dev — `kata-build-skill` (Phase 4) valida el handler real, no el stub.

### Paso 6: Reportar URLs e instrucciones

Al final del bring-up:

```
✅ Dev server activo para {slug}:
   Widgets:      http://localhost:{widgets_port}/        (HMR Vite)
   Script runner: http://localhost:{scripts_port}/       (Python uv)
   Tool stub:    http://localhost:{tools_stub_port}/    (MCP mock)

Bindings de widgets/manifest.json:
   - TransferForm → tool: validate_amount    (stub en /tools/validate_amount)
   - TransferForm → script: scripts/src/format_currency.py (en /format-currency)

Para parar: Ctrl-C en este terminal.
Para build: /cry-skill-build {slug}
```

### Paso 7: Acompañar hasta que el usuario pare

1. Mantener el foreground del proceso Vite (HMR principal); script runner y tool stub en background cuando lo soporta el terminal
2. Los logs de cada servidor se prefijan (`[widgets]`, `[scripts]`, `[tools]`) para facilitar el diagnóstico
3. En caso de crash de cualquier subproceso, reportar y ofrecer reiniciar
4. Ctrl-C cierra todos los subprocesos limpiamente

## Salidas

| Salida | Formato |
|--------|---------|
| Éxito | URLs activas + foreground con logs hasta que el usuario interrumpa |
| Fallo (proyecto inexistente) | Mensaje citando `lex-skill-project-structure` |
| Fallo (port ocupada) | Mensaje instruyendo override vía `--*_port` |
| Fallo (manifest inválido) | Mensaje citando `codex-skill-tools-and-widgets` con la regla violada |
| Fallo (dependencia no instalada) | Mensaje instruyendo `uv sync` / `npm install` en el directorio correspondiente |

## Ejemplo de Ejecución

```
/cry-skill-dev hello-skill
```

```
✅ Dev server activo para hello-skill:
   Widgets:      http://localhost:5173/
   Tool stub:    http://localhost:5175/
   (sin scripts/ — omitido)

Presione Ctrl-C para finalizar.
```

## Restricciones

- No modifica `skills/{slug}/` (solo lee)
- No escribe en `.build/` ni `.dist/`
- El tool stub es **mock**; nunca usado en producción
- Los ports default son opinionados; siempre permite override
- Los logs respetan `lex-logging-decorator` cuando están integrados; el CLI boot del kata es excepción permitida (boundary de aplicación)
- `lex-terminal-type`: los comandos shell respetan el terminal definido en `.directives` (bash | powershell)

## Referencias

- `codex-skill-build-pipeline` — defaults de tooling, ports, fases del build (precondiciones del dev server y lo que él simula)
- `codex-skill-tools-and-widgets` — schemas de `mcp.config.json` y `manifest.json` validados por las precondiciones
- `codex-skill-project-architecture` — flujo dev → build → dist
- `codex-frontend-architecture` — convenciones de Vite y dev server aplicables a los widgets
- `lex-skill-project-structure` — ley del layout
- `lex-terminal-type` — terminal y sintaxis de comandos
- `cry-skill-dev` — atajo del usuario
- `kata-build-skill` — paso siguiente natural tras la validación en dev
