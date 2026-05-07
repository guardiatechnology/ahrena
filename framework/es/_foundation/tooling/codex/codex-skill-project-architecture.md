# Codex: Arquitectura de Proyecto de Skill (Ahrena)

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Estructura interna de un proyecto de skill en el repositorio Ahrena (`skills/{slug}/`), papel de cada subdirectorio, ciclo `dev → build → dist`, y reuso de los codex de arquitectura existentes durante la autoría

## Visión general

Cada skill externo es un **proyecto de primera clase** en el repositorio Ahrena, con la fuente versionada en `skills/{slug}/`. El proyecto sigue los Pilares Ahrena durante la autoría — los widgets adoptan `codex-frontend-architecture`, los scripts y tools en Python adoptan `codex-python-architecture`, las reglas de calidad provienen de las Lexis correspondientes — sin duplicación. El resultado final es un paquete en formato Anthropic Agent Skills (según `codex-skill-anthropic-agent-skills`), entregado en `.dist/`.

Este Codex define **únicamente el layout del proyecto fuente y el ciclo dev/build/dist**. No cubre:

- Detalles del formato Anthropic Agent Skills → `codex-skill-anthropic-agent-skills`
- Convención de tools MCP y widgets React (manifestos, bindings) → `codex-skill-tools-and-widgets` [PR 2]
- Pipeline de build, hashing, ordering → `codex-skill-build-pipeline` [PR 2]
- Estructura final del paquete en `.dist/` → `lex-skill-package-structure` + codex correspondiente [PR 3]

## Contexto

- **Dominio:** proyectos de skill versionados en el repositorio Ahrena
- **Público objetivo:** autores de skill, `kata-init-skill`, agentes que delegan edición (`warrior-hephaestus` para widgets, `warrior-apollo` para scripts/tools Python)
- **Actualización:** cuando la convención de subdirectorios cambie; cuando se introduzcan nuevos tipos de artefacto en el PR 2/3

## Contenido

### Layout canónico del proyecto fuente

```
skills/{slug}/
├── SKILL.md                    # Frontmatter Agent Skills + cuerpo (orquesta los demás artefactos)
├── .skill-manifest.json        # Esqueleto; rellenado con refs+hashes por el build (PR 2/3)
├── skill.config.json           # Config local del proyecto (idioma, runtimes, ports del dev server)
├── references/                 # Markdown adicional (level-3 de la spec) — opcional
├── scripts/                    # JS o Python — utilitarios ejecutables por el agente — opcional
│   ├── package.json            # cuando JS
│   ├── pyproject.toml          # cuando Python
│   └── src/
├── tools/                      # MCP tools (lógica) — convención Ahrena, opcional
│   ├── mcp.config.json
│   └── handlers/
└── widgets/                    # React (TS) — UI — convención Ahrena, opcional
    ├── package.json
    ├── manifest.json
    └── src/
```

`{slug}` es kebab-case válido según la spec de Anthropic (`a-z`, `0-9`, guion; sin guion al inicio/fin; sin `--`; **idéntico al `name` en el SKILL.md**).

### Mapeo spec Anthropic ↔ proyecto Ahrena

| Ítem | Dónde queda en la spec (`.dist/{slug}/`) | Dónde queda en el proyecto fuente (`skills/{slug}/`) | Estado |
|------|------------------------------------------|-------------------------------------------------------|--------|
| `SKILL.md` | raíz | raíz | nativo de la spec |
| `references/` | raíz | raíz | nativo |
| `scripts/` | raíz (ejecutables listos) | raíz (fuente; el build congela en `.build/`) | nativo |
| `assets/` | raíz | (creado por el autor cuando es necesario) | nativo |
| `tools/` (MCP) | raíz | raíz | **convención Ahrena**, fuera de la spec |
| `widgets/` (React) | raíz | raíz | **convención Ahrena**, fuera de la spec |
| `.skill-manifest.json` | raíz | raíz (esqueleto, completado en el build) | **convención Ahrena** |
| `skill.config.json` | (no entra al paquete) | raíz | **convención Ahrena** (solo dev/build) |

Las convenciones Ahrena (`tools/`, `widgets/`, `.skill-manifest.json`) son **extensiones** de la spec — los agentes externos que solo conocen la spec ignoran esos directorios; los agentes que conocen la convención Ahrena las consumen.

### `SKILL.md` en el proyecto fuente

El `SKILL.md` en el proyecto fuente es el mismo archivo que va al paquete final (el build solo reescribe rutas relativas cuando es necesario). Estructura mínima:

```markdown
---
name: scheduled-payments-skill
description: Schedules and approves bank transfers using widgets connected to Python tools. Use when the user wants to create or approve a scheduled transfer.
license: Apache-2.0
metadata:
  version: "0.1.0"
  language: pt-BR
  spec_version: "agentskills.io/specification@2026-04"
---

# Scheduled Payments Skill

## Cuándo usar
{...}

## Flujo
1. Renderice el widget `widgets/transfer-form/` para el usuario.
2. Cuando el usuario confirme, invoque la tool `tools/handlers/create_transfer.py`.
3. Muestre el resultado en el widget de confirmación.

## Referencias
- Detalles del formulario: [references/FORM.md](references/FORM.md)
- Tool de creación: `tools/handlers/create_transfer.py`
```

Las recomendaciones de la spec se aplican: **< 500 líneas**, **< 5 000 tokens**, contenido extenso va a `references/`.

### `skill.config.json`

Configuración local del proyecto, **no entra al paquete final**. Leída por `kata-init-skill` (scaffold), `kata-skill-dev-server` (dev) y `kata-build-skill` (build) — todos en el PR 2.

Esqueleto canónico:

```json
{
  "schema_version": 1,
  "language": "pt-BR",
  "runtimes": {
    "scripts": "python | node",
    "widgets": "react"
  },
  "dev_server": {
    "widgets_port": 5173,
    "scripts_port": 5174,
    "tools_stub_port": 5175
  },
  "build": {
    "bundler": "vite",
    "minify": true,
    "source_maps": false
  },
  "external_refs": [
    {
      "kind": "lexis",
      "id": "_foundation/tooling/lexis/lex-mcp"
    }
  ]
}
```

`external_refs` lista artefactos del framework Ahrena (lex/codex/kata) que serán snapshotados en `references/` durante el build. Por ahora (PR 1) el campo existe en el scaffold pero la resolución real queda en el PR 2.

### Subdirectorios — papel y detalles

#### `SKILL.md` + `references/` (nativos de la spec)

Dominio del autor; sin regla Ahrena más allá de lo que `codex-skill-anthropic-agent-skills` define.

#### `scripts/` (nativo de la spec)

Código ejecutable invocado por el agente. **Lenguaje:** JS (Node) o Python — elección por contexto:

- Python para lógica de dominio, integración con APIs estructuradas, procesamiento de datos (alineado a `codex-python-architecture`, `codex-python-tooling`)
- JS para utilidades de DOM, generación de markup, interacción con runtime de browser
- La mezcla está permitida (un skill puede tener ambos)

Cada script sigue las Lexis y codex de su lenguaje **sin ajuste**:

| Aspecto | Python | JS/TS |
|---------|--------|-------|
| Tipado | `lex-python-typing` (mypy strict) | `lex-frontend-typing` (TS strict) — cuando aplique |
| Errores | `lex-python-error-handling`, `lex-python-result-type` | tratamiento idiomático |
| Tests | `lex-python-testing` | `lex-frontend-testing` |
| Logging | `lex-logging-decorator` (cross-language) | `lex-logging-decorator` |
| Seguridad | `lex-python-security` | `lex-frontend-security` |

Los detalles de la **conexión script ↔ widget** quedan en `codex-skill-tools-and-widgets` (PR 2).

#### `tools/` (convención Ahrena, opcional)

MCP tools que el agente externo invoca durante la ejecución del skill. Sirven como herramientas de dominio propias del skill, sin exponer artefactos brutos del Ahrena.

El detalle (manifest, registro, conexión) está en `codex-skill-tools-and-widgets` (PR 2). En el PR 1 (scaffold), el directorio existe vacío con `mcp.config.json` placeholder y un ejemplo trivial en `handlers/`.

#### `widgets/` (convención Ahrena, opcional)

Componentes React que el agente renderiza en el chat. **La arquitectura hereda íntegramente** `codex-frontend-architecture`:

- Capas (Pages → Features → Components → Hooks → Services → State)
- Server state vía TanStack Query / SWR; client state vía Zustand / Context según el alcance
- Tipos derivados de OpenAPI cuando esté disponible (vía `openapi-typescript`)
- Accesibilidad WCAG 2.1 AA según `lex-frontend-accessibility`
- Seguridad según `lex-frontend-security` (sin `dangerouslySetInnerHTML` sin sanitización, sin secrets en el bundle)
- Tests según `lex-frontend-testing`
- Design system Guardia según `lex-design-system-library` cuando el widget se renderice en superficie Guardia

El detalle de manifest, props, eventos y binding con scripts/tools está en `codex-skill-tools-and-widgets` (PR 2). En el PR 1, el directorio viene vacío con `package.json` mínimo y un componente de ejemplo.

### Reuso de codex y Lexis durante la autoría

| Contenido del proyecto | Codex de arquitectura aplicable | Lexis aplicables (sin ajuste) |
|------------------------|---------------------------------|-------------------------------|
| `widgets/` (React) | `codex-frontend-architecture` | `lex-frontend-typing`, `lex-frontend-accessibility`, `lex-frontend-security`, `lex-frontend-testing`, `lex-design-system-library` |
| `scripts/` Python | `codex-python-architecture`, `codex-python-tooling`, `codex-python-testing`, `codex-python-logging` | `lex-python-typing`, `lex-python-testing`, `lex-python-security`, `lex-python-error-handling`, `lex-python-result-type`, `lex-python-error-object`, `lex-logging-decorator` |
| `scripts/` JS | (futuro `codex-js-architecture` cuando emerja) | `lex-frontend-typing` cuando TS; `lex-logging-decorator` |
| `tools/` (MCP) | `codex-mcp-common`, `codex-python-architecture` cuando el handler sea Python | `lex-mcp`, además de las Lexis de Python/JS según el handler |
| Cuerpo de `SKILL.md` | `codex-skill-anthropic-agent-skills` | `lex-tone` (estilo directo, sin buzzwords) |

**Principio:** el proyecto de skill es un cliente de las mismas reglas que gobiernan el resto de la plataforma. No hay "reglas de skill" paralelas que dupliquen calidad ya codificada.

### Ciclo dev → build → dist

```
skills/{slug}/                            # FUENTE (versionada, autoría con Pilares)
       │
       │ kata-skill-dev-server (PR 2)
       ▼
   localhost — widgets HMR + script runner + tools stub
       │
       │ kata-build-skill (PR 2)
       ▼
.build/{slug}/                            # INTERMEDIO (gitignored)
   ├── widgets/    (React compilado)
   ├── scripts/    (deps lockeadas)
   ├── tools/      (config validada)
   ├── references/ (snapshots de external_refs)
   ├── SKILL.md    (rutas reescritas)
   ├── .skill-manifest.json (con hashes)
   └── {slug}.zip  (testeable en otro agente)
       │
       │ kata-package-skill (PR 3)
       ▼
.dist/{slug}.skill                        # ENTREGA (committed)
```

Reglas (algunas todavía solo consagradas en el PR 1, otras codificadas en PRs futuros):

- **La fuente es la verdad.** `.build/` y `.dist/` son derivados; ningún agente edita esos directorios manualmente
- **`.build/` es gitignored.** `.dist/` es committed (consumible por agentes que no tienen Ahrena)
- **Determinismo en el PR 3.** El build debe producir hashes idénticos para el mismo input; ordering lexicográfico, sin timestamps volátiles
- **Snapshots por commit hash en el PR 3.** `.skill-manifest.json` registra `source_commit` para cada ref del framework

En el PR 1 (scaffold), solo se establece el layout fuente; build y packaging son placeholders.

### Directivas relacionadas

`.ahrena/.directives` introduce tres paths para localizar la fuente y las salidas:

```yaml
paths:
  skills_root: skills        # directorio fuente de los proyectos de skill
  skills_build: .build       # intermedio (gitignored)
  skills_dist: .dist         # entrega final (committed)
```

Los proyectos pueden sobreescribir (p. ej., `skills_root: my-skills/`); los agentes consultan la clave en lugar de asumir literal.

### `.gitignore` recomendado

`.build/` en el `.gitignore` raíz; `.dist/` se mantiene versionado:

```
.build/
```

`kata-init-skill` (alcance de este PR) garantiza que la entrada exista cuando inicializa el primer skill.

## Restricciones

- **Skill no es Pilar del framework.** No tiene prefix en `framework/`, no aparece en `naming.prefixes`. Es un proyecto externo gobernado por los artefactos de este codex y de `lex-skill-project-structure`.
- **Las convenciones Ahrena (`tools/`, `widgets/`) son opcionales.** Los skills pueden existir solo con `SKILL.md` + `scripts/`/`references/` puros de la spec. La convención entra cuando el skill necesita UI o MCP propio.
- **Monoidioma por skill.** `metadata.language` declara un idioma; producir el mismo skill en pt-BR y en exige dos proyectos `skills/{slug}-ptbr/` y `skills/{slug}-en/` o un mecanismo de localización interno (no gobernado en este PR).
- **Slug del directorio == `name` del frontmatter.** La spec lo exige; `kata-init-skill` lo valida.

## Glosario

| Término | Definición |
|---------|-----------|
| Proyecto de skill | Directorio `skills/{slug}/` versionado en el repositorio Ahrena |
| Slug | Nombre en kebab-case del proyecto, idéntico al `name` de la spec |
| Paquete | Salida en `.dist/{slug}.skill` (formato Anthropic Agent Skills) |
| Build intermedio | Salida en `.build/{slug}/` (testeable en localhost; no es entrega) |
| Convención Ahrena | Directorios y archivos no definidos por la spec (`tools/`, `widgets/`, `.skill-manifest.json`, `skill.config.json`) |
| External ref | Artefacto del framework Ahrena (lex/codex/kata) snapshotado en `references/` durante el build |

## Referencias

- `codex-skill-anthropic-agent-skills` — spec externa
- `codex-frontend-architecture` — arquitectura para `widgets/`
- `codex-python-architecture`, `codex-python-tooling` — arquitectura para `scripts/` y `tools/` Python
- `codex-mcp-common` — patrones MCP usados en `tools/`
- `lex-skill-project-structure` — ley del layout
- `lex-directives` — dónde se leen los paths `skills_root/build/dist`
- `lex-frontend-*`, `lex-python-*` — calidad aplicable a los artefactos por lenguaje
