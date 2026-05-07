# Lexis: Estructura Obligatoria de Proyecto de Skill

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Proyectos de skill versionados en el repositorio Ahrena (fuente en `skills/{slug}/`, intermedio en `.build/`, entrega en `.dist/`)

## Ley

> **Todo proyecto de skill DEBE residir en `{paths.skills_root}/{slug}/` (default `skills/{slug}/`) con layout canónico definido en `codex-skill-project-architecture`: presencia obligatoria de `SKILL.md` y `skill.config.json` en la raíz; `{slug}` en kebab-case válido según la spec de Anthropic e idéntico al campo `name` del frontmatter del `SKILL.md`; separación física entre fuente (`{paths.skills_root}/`), intermedio (`{paths.skills_build}/`, gitignored) y entrega (`{paths.skills_dist}/`, committed); contenido del proyecto respetando íntegramente las Lexis de calidad aplicables al tipo de cada artefacto (widgets → `lex-frontend-*`; scripts/tools Python → `lex-python-*`; logging cross-language → `lex-logging-decorator`; MCP → `lex-mcp`). Editar artefactos directamente en `{paths.skills_build}/` o `{paths.skills_dist}/` está PROHIBIDO — esos directorios son derivados; los cambios entran por la fuente.**

## Alcance

- **Se aplica a:** todos los proyectos de skill mantenidos en el repositorio Ahrena, en cualquier idioma de `metadata.language`
- **Agentes vinculados:** `kata-init-skill` (scaffold), `cry-new-skill` (atajo), `warrior-hephaestus` (widgets), `warrior-apollo` (scripts/tools Python), y cualquier agente que edite el proyecto durante el ciclo dev → build → dist
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones. Los skills experimentales o de prueba siguen el mismo layout — los directorios de exploración ad-hoc fuera de `paths.skills_root` no se consideran proyectos de skill y no son gobernados por esta Lex

## Reglas

### 1. Localización y nomenclatura

- Directorio raíz del proyecto: `{paths.skills_root}/{slug}/` (default `skills/{slug}/`)
- `{slug}`: 1-64 caracteres, solo `a-z`, `0-9` y guion; sin guion al inicio o al fin; sin `--` consecutivo (según la spec de Anthropic — `codex-skill-anthropic-agent-skills`)
- `{slug}` debe ser **idéntico** al valor de `name` en el frontmatter del `SKILL.md`
- No usar nombres reservados por la documentación de Anthropic (`anthropic`, `claude`)

### 2. Archivos obligatorios en la raíz del proyecto

| Archivo | Papel |
|---------|-------|
| `SKILL.md` | Frontmatter Anthropic Agent Skills + cuerpo Markdown |
| `skill.config.json` | Configuración local del proyecto (idioma, runtimes, ports del dev server, refs externas a snapshotar) |

`.skill-manifest.json` esqueleto **debe existir** después del scaffold, pero es **escrito** únicamente por el build (PR 2/3). En el PR 1 el esqueleto contiene `schema_version` y campos vacíos.

### 3. Subdirectorios opcionales

Permitidos en el proyecto fuente según `codex-skill-project-architecture`:

- `references/` — Markdown adicional (level 3 de la spec)
- `scripts/` — código JS o Python ejecutable por el agente
- `tools/` — MCP tools propias del skill (convención Ahrena)
- `widgets/` — componentes React (convención Ahrena)
- `assets/` — recursos estáticos de la spec

Subdirectorios fuera de esa lista exigen justificación explícita en el `SKILL.md` o en `skill.config.json` (campo `metadata.notes` o equivalente). El agente que edita no crea nuevos top-level sin justificación.

### 4. Separación fuente / intermedio / entrega

| Tipo | Path default | Versionado | Quién escribe |
|------|--------------|:----------:|---------------|
| Fuente | `skills/{slug}/` | Sí | Autor (humano o agente, durante la autoría) |
| Intermedio | `.build/{slug}/` | **No** (en `.gitignore`) | Build (`kata-build-skill`, PR 2) |
| Entrega | `.dist/{slug}.skill` | Sí | Packaging (`kata-package-skill`, PR 3) |

Editar `.build/` o `.dist/` manualmente rompe el determinismo (`lex-skill-export-determinism`, PR 3) y la auditabilidad. **Los cambios entran por la fuente**, siempre.

### 5. Conformidad con Pilares y Lexis aplicables

El contenido del proyecto **hereda** las Lexis de calidad ya codificadas en el framework:

| Contenido del skill | Lexis y codex de calidad aplicables |
|---------------------|-------------------------------------|
| `widgets/` (React/TS) | `lex-frontend-typing`, `lex-frontend-accessibility`, `lex-frontend-security`, `lex-frontend-testing`, `lex-design-system-library` (cuando se renderiza en superficie Guardia), `codex-frontend-architecture` |
| `scripts/` Python | `lex-python-typing`, `lex-python-testing`, `lex-python-security`, `lex-python-error-handling`, `lex-python-result-type`, `lex-python-error-object`, `codex-python-architecture`, `codex-python-tooling` |
| `scripts/` JS/TS | `lex-frontend-typing` (cuando TS), tratamiento idiomático de errores |
| `tools/` MCP | `lex-mcp`, `codex-mcp-common`, además de las Lexis del lenguaje del handler |
| Logging en cualquier lenguaje | `lex-logging-decorator` |
| Texto en `SKILL.md` y `references/` | `lex-tone` |

Violar Lexis de calidad dentro de un proyecto de skill es violación directa — no hay "modo skill" que afloje regla existente.

### 6. `.gitignore` mínimo

El repositorio con proyectos de skill **debe** tener `.build/` en `.gitignore` (raíz o path equivalente cuando `paths.skills_build` se sobreescriba).

`.dist/` **no** entra al `.gitignore` — es entrega versionada.

`kata-init-skill` garantiza la entrada cuando se crea el primer proyecto.

## Consecuencias de Violación

1. **Bloqueo en revisión:** un PR que contenga un proyecto fuera del layout (slug fuera del regex, sin `SKILL.md`, sin `skill.config.json`, edición directa en `.build/`/`.dist/`) es rechazado por el reviewer (humano o Gate 2 cuando `kata-quality-gate` integre la verificación).
2. **Alerta:** divergencia entre `slug` del directorio y `name` del frontmatter detectada por `kata-init-skill` o por el build (PR 2) → error inmediato con instrucción de corrección.
3. **Remediación:** mover archivos a `skills/{slug}/`, crear los archivos obligatorios ausentes, renombrar el directorio/`name` para que coincidan, o descartar los cambios en `.build/`/`.dist/` y rehacer por la fuente.

## Ejemplos

### Correcto

```
skills/scheduled-payments-skill/
├── SKILL.md                    # frontmatter con name: scheduled-payments-skill
├── skill.config.json
├── .skill-manifest.json        # esqueleto
├── widgets/
│   ├── package.json
│   └── src/transfer-form/index.tsx
└── scripts/
    └── src/validate_amount.py

.build/                         # gitignored
.dist/                          # vacío hasta el PR 3 — committed
```

```yaml
# SKILL.md
---
name: scheduled-payments-skill   # idéntico al directorio
description: Schedules and approves bank transfers using widgets connected to Python tools. Use when the user wants to create or approve a scheduled transfer.
license: Apache-2.0
metadata:
  version: "0.1.0"
  language: pt-BR
---
```

### Incorrecto

```
my-skills/payments/              # ❌ fuera de paths.skills_root sin override declarado
skills/Payments_Skill/           # ❌ slug con underscore y mayúscula
skills/payments-skill/SKILL.md   # ❌ frontmatter con name: payments (no coincide con el directorio)
.build/payments-skill/widgets/   # ❌ edición directa en el intermedio
.dist/payments-skill.skill/      # ❌ edición directa en la entrega
```

```
skills/payments-skill/
├── SKILL.md
└── widgets/src/Form.jsx         # ❌ TS strict no aplicado, viola lex-frontend-typing
                                 # incluso dentro de un proyecto de skill, lex-frontend-* vale
```

## Validación Automatizada

- **Herramienta:**
  - `kata-init-skill` valida slug, frontmatter, presencia de archivos obligatorios en la creación
  - PR review (humano) verifica el layout mientras `kata-quality-gate` no integra
  - Lint genérico (existente) detecta violación de `lex-frontend-*` / `lex-python-*` dentro del proyecto, sin necesidad de regla nueva
  - El `.gitignore` raíz contiene `.build/` (verificable por inspección)
- **Momento:** scaffold (`kata-init-skill`); PR review; futura integración en el Gate 2
- **Métrica:** 0 proyectos de skill con `name` divergente del slug; 0 commits que editan `.build/` o `.dist/` directamente; 100 % de los proyectos con `SKILL.md` + `skill.config.json` en la raíz

## Referencias

- `codex-skill-project-architecture` — layout completo y papel de cada subdirectorio
- `codex-skill-anthropic-agent-skills` — restricciones de la spec sobre `name` y estructura
- `lex-directives` — lectura de `paths.skills_root/build/dist`
- `lex-template-usage` — uso de templates Ahrena al crear `SKILL.md` y `skill.config.json`
- `lex-frontend-*`, `lex-python-*`, `lex-mcp`, `lex-logging-decorator`, `lex-tone` — Lexis de calidad heredadas por el contenido del proyecto
