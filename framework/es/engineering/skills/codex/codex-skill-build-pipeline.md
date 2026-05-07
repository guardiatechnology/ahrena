# Codex: Pipeline de Build de Skills (Ahrena)

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Pipeline determinístico que lee `skills/{slug}/`, valida manifests, compila widgets, congela scripts, valida tools y emite `.build/{slug}/` + `.build/{slug}.zip`

## Visión General

El build es el puente entre **fuente** (`skills/{slug}/`, autorada con Pilares Ahrena) y **entrega** (`.dist/{slug}.skill`, formato Anthropic). Él:

1. Valida `SKILL.md`, `skill.config.json`, manifests de tools y widgets
2. Compila widgets React (Vite) con source maps configurables
3. Congela scripts (lock de dependencias) sin instalar runtime objetivo
4. Valida `tools/mcp.config.json` y resuelve refs de handlers
5. Reescribe paths y bindings para el formato post-build
6. Emite `.build/{slug}/` con layout listo para empaquetado (PR 3) y `.build/{slug}.zip` testeable manualmente en otro agente

Este codex documenta el **contrato** del pipeline. La implementación operacional vive en `kata-build-skill`. El empaquetado final en `.dist/` (snapshot de refs externas con commit hash, manifest raíz con hashes) es cobertura del PR 3 (`kata-package-skill`, `lex-skill-export-determinism`).

## Contexto

- **Dominio:** transformación fuente → intermedio (`.build/`); precondición para el empaquetado
- **Público objetivo:** `kata-skill-dev-server`, `kata-build-skill`; autores que requieren entender qué esperar del build
- **Actualización:** cuando los defaults de tooling (Vite, uv, Node) cambien; cuando la estructura del `.skill-manifest.json` evolucione

## Contenido

### Defaults de tooling

| Capa | Herramienta | Versión objetivo | Justificación |
|------|-------------|------------------|---------------|
| Bundler de widgets | **Vite** | 5.x | Velocidad, zero-config para React + TS, output multi-formato, dev server con HMR |
| Runtime JS de scripts | **Node** | 20 LTS | Estable, soporte ESM nativo |
| Runtime Python de scripts y handlers | **uv** + **Python 3.12** | uv ≥ 0.4 | Alineado a `codex-python-tooling`; install reproducible y rápido |
| Empaquetador final | `zip` POSIX (BSD/Info-ZIP) | cualquiera | Entrega zip testeable; `kata-package-skill` (PR 3) define el formato `.skill` final |

`skill.config.json` permite override por proyecto (`build.bundler`, `runtimes.scripts`); el pipeline rechaza combinaciones inconsistentes (ej.: `widgets/` presente sin bundler soportado).

### Ports default en el dev server

| Servidor | Port default | Override | Función |
|----------|-------------:|----------|---------|
| Widgets HMR (Vite) | `5173` | `dev_server.widgets_port` | Renderizado y hot reload |
| Script runner | `5174` | `dev_server.scripts_port` | Endpoints HTTP/JSON exponiendo `scripts/` a los widgets |
| Tool stub MCP | `5175` | `dev_server.tools_stub_port` | Mock local de tools declaradas en `tools/mcp.config.json` |

`kata-skill-dev-server` levanta los tres bajo demanda (solo los necesarios al skill en desarrollo).

### Pipeline — fases

```
skills/{slug}/                                    .build/{slug}/
   │
   ├─ Phase 1: Validate
   │     ├─ SKILL.md frontmatter (codex-skill-anthropic-agent-skills)
   │     ├─ skill.config.json (schema_version, runtimes, ports)
   │     ├─ tools/mcp.config.json (handler refs existen, JSON Schema válido)
   │     └─ widgets/manifest.json (entries existen, bindings consistentes)
   │
   ├─ Phase 2: Build widgets (cuando widgets/ existe)
   │     ├─ vite build --mode production
   │     ├─ output en .build/{slug}/widgets/
   │     └─ manifest.json reescrito apuntando a entries compiladas
   │
   ├─ Phase 3: Freeze scripts (cuando scripts/ existe)
   │     ├─ Python: uv lock → copy src + uv.lock a .build/{slug}/scripts/
   │     ├─ JS: npm/pnpm lock + copy src + lockfile
   │     └─ paths en scripts mantenidos (no compilados)
   │
   ├─ Phase 4: Resolve tools (cuando tools/ existe)
   │     ├─ valida cada handler ref (path:funcion existe)
   │     ├─ copia mcp.config.json + handlers/ a .build/{slug}/tools/
   │     └─ reescribe handler refs a paths post-build (si necesario)
   │
   ├─ Phase 5: Rewrite bindings
   │     ├─ widgets/manifest.json: bindings con kind: script pierden called_via
   │     │   localhost (solo dev) y ganan campo called_via_prod (path
   │     │   resuelto por el host) o se marcan como "via_tool" cuando
   │     │   el build sugiere migración de script→tool
   │     └─ SKILL.md: paths citados en ./scripts/, ./tools/, ./widgets/
   │       cotejados contra archivos efectivamente emitidos
   │
   ├─ Phase 6: Emit
   │     ├─ SKILL.md (copia + encabezado de aviso de convención cuando hay tools/widgets)
   │     ├─ .skill-manifest.json (esqueleto poblado con hashes — solo campos
   │     │   determinables en el build; references[] con snapshots de framework
   │     │   es responsabilidad del PR 3)
   │     └─ {slug}.zip (zip lexicográficamente ordenado; sin timestamps)
   │
   └─ Done
```

### Determinismo en el build (intermedio)

Las mismas entradas deben producir el mismo `.build/{slug}/` y el mismo `{slug}.zip`. Reglas:

- **Ordering lexicográfico** al listar archivos para zip (`zip -X`, `find . | sort`); evita orden dependiente del filesystem
- **Sin timestamps volátiles**: `mtime` de los archivos en el zip se fija en `1980-01-01` (mínimo del formato) o en el commit hash del `skills/{slug}/` (epoch de la última modificación versionada)
- **Sin source maps con paths absolutos**: `source_maps: false` por default en `skill.config.json`; cuando `true`, los paths se reescriben a relativos a la raíz del proyecto
- **Vite con mode `production`** siempre; modo dev (con HMR) es exclusivo de `kata-skill-dev-server`
- **Locks copiados, no regenerados**: `uv.lock` / `package-lock.json` de la fuente se preservan (no se re-resuelven en el build), garantizando reproducibilidad

La cobertura completa de determinismo (incluyendo snapshot de refs externas con commit hash) está en `lex-skill-export-determinism` (PR 3).

### Cache

`.build/{slug}/` está gitignored. `kata-build-skill` acepta el flag `--clean` para borrar y regenerar; sin el flag, build incremental cuando es posible (Vite gestiona cache propio en `node_modules/.vite/`). Los hashes registrados en `.skill-manifest.json` permiten verificar drift posteriormente.

### Hashes en `.skill-manifest.json`

Al final de la Phase 6, el build escribe `files[]` con:

```json
{
  "files": [
    { "path": "SKILL.md", "sha256": "..." },
    { "path": "widgets/dist/index.js", "sha256": "..." },
    { "path": "tools/mcp.config.json", "sha256": "..." }
  ]
}
```

`references[]` (snapshots de refs externas del framework) **no** se completa en esta etapa — es responsabilidad de `kata-package-skill` (PR 3) al consolidar `.dist/`. PR 2 entrega `references[]: []` en el manifest.

### Fallos — modos comunes

| Fallo | Causa | Salida esperada |
|-------|-------|-----------------|
| `SKILL.md` frontmatter inválido | name/description fuera de los límites | Error citando reglas de `codex-skill-anthropic-agent-skills`; el build aborta antes de la Phase 2 |
| Handler ref inválida en `tools/mcp.config.json` | Path:funcion no existe | Error listando ref y ubicación; aborta en la Phase 1 |
| Widget entry inválida en `widgets/manifest.json` | Path del entry no existe | Error con sugerencia de corrección; aborta en la Phase 1 |
| `uv.lock` ausente cuando `runtimes.scripts: python` | Lockfile no fue generado por el autor | Error instruyendo `uv lock` en la carpeta `scripts/`; aborta en la Phase 3 |
| El build de Vite falla | Error de TS strict, import roto, etc. | Salida de Vite propagada; aborta en la Phase 2 |
| Binding `kind: script` sin `called_via` en dev | Manifest incompleto | Error instruyendo declarar `called_via`; aborta en la Phase 5 |

### Integración con Storybook / Playwright (opcional)

Las skills que adoptan Storybook o Playwright en `widgets/` mantienen esas herramientas como **dev dependencies**; el build no las incluye en `.build/{slug}/`. Stories y specs son parte de la fuente (versionada), no de la entrega.

## Restricciones

- El build es **idempotente**: ejecutarlo dos veces seguidas con la fuente sin cambios produce `.build/{slug}/` byte-idéntico
- El build **no modifica** `skills/{slug}/` (solo lee)
- El build **no toca** `.dist/` (responsabilidad del PR 3)
- El pipeline aborta en el primer fallo; no intenta seguir parcialmente
- Los logs del pipeline siguen `lex-logging-decorator` cuando los emiten handlers Ahrena (boot CLI queda en `kata-build-skill`)

## Glosario

| Término | Definición |
|---------|------------|
| Phase | Etapa nombrada del pipeline (Validate, Build widgets, Freeze scripts, Resolve tools, Rewrite bindings, Emit) |
| Freeze | Copia de `scripts/` con lockfile preservado; sin instalar dependencias en `.build/` |
| Tool stub | Mock local de la tool, usado por el dev server; **no** va a `.build/` |
| Pipeline incremental | Reejecución que aprovecha cache de Vite cuando es válido |

## Referencias

- `codex-skill-anthropic-agent-skills` — schema del `SKILL.md` validado en la Phase 1
- `codex-skill-tools-and-widgets` — schemas de `mcp.config.json` y `manifest.json`
- `codex-skill-project-architecture` — flujo dev → build → dist a alto nivel
- `codex-python-tooling` — uv como runtime objetivo de Python
- `codex-frontend-architecture` — restricciones aplicables a widgets
- `lex-skill-project-structure` — ley que separa fuente/build/dist
- `lex-skill-export-determinism` (PR 3) — determinismo de la entrega final
- `kata-skill-dev-server` — orquestación del dev server que precede al build
- `kata-build-skill` — implementación operacional de este pipeline
