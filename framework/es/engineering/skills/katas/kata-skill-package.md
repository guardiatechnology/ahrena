# Kata: Empaquetar Skill

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Empaquetado determinístico de un proyecto de skill desde `{paths.skills_root}/{slug}/` (fuente) hacia `{paths.skills_dist}/{slug}.skill/` (entrega), con manifest, hashes y validación contra `lex-skill-package-structure`

## Objetivo

Producir, a partir de un proyecto fuente validado, el paquete `.skill/` final consumido por agentes externos en el formato Anthropic Agent Skills. El empaquetador es determinístico: dada la misma fuente y el mismo commit del framework, la salida es idéntica byte a byte, con `.skill-manifest.json` ordenado lexicográficamente, todos los hashes SHA-256 verificados y cero archivos huérfanos.

## Cuándo Usar

- Después de que `kata-skill-validate` retorne `ok` u `ok-with-warnings`
- Cuando `warrior-claudionor` debe entregar el paquete final bajo `{paths.skills_dist}/`
- Durante la Fase 2 (build → dist) de un release de skill

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `slug` | Sí | Nombre del proyecto (idéntico al nombre del directorio en `{paths.skills_root}/`) |
| `repo_root` | No | Raíz del repositorio (por defecto: directorio de trabajo actual) |
| `skills_root` | No | Override de `paths.skills_root` (por defecto: leído de `.ahrena/.directives`) |
| `skills_build` | No | Override de `paths.skills_build` |
| `skills_dist` | No | Override de `paths.skills_dist` |
| `dry_run` | No | `true` valida la fuente pero no escribe en build/dist |
| `format` | No | `text` (por defecto, humano) o `json` |

## Workflow

```
Progreso:
- [ ] 1. Resolver paths (.ahrena/.directives + overrides)
- [ ] 2. Validar la fuente (kata-skill-validate como precondición)
- [ ] 3. Resolver versión/idioma del frontmatter + SHA del framework
- [ ] 4. Copiar fuente → build/{slug}/
- [ ] 5. Materializar dist/{slug}.skill/ a partir de build
- [ ] 6. Generar .skill-manifest.json (schema_version, skill, framework, references, files)
- [ ] 7. Validar el paquete final contra lex-skill-package-structure
- [ ] 8. Reportar
```

### Paso 1: Resolver paths

1. Leer `.ahrena/.directives`, sección `paths`:
   - `paths.skills_root` (por defecto `skills`)
   - `paths.skills_build` (por defecto `.build`, gitignored)
   - `paths.skills_dist` (por defecto `.dist`, committed)
2. Aplicar los overrides recibidos por argumento
3. Verificar que la fuente `{repo_root}/{skills_root}/{slug}/` existe

### Paso 2: Validar la fuente como precondición

1. Invocar `kata-skill-validate skill_path={skills_root}/{slug}`
2. Si hay violaciones con severidad `error`, **abortar** sin escribir en `{skills_build}/` ni `{skills_dist}/`
3. Los warnings no bloquean — propagarlos al reporte final

### Paso 3: Resolver metadatos

1. Parsear el frontmatter de `{skills_root}/{slug}/SKILL.md`:
   - `metadata.version` → va a `manifest.skill.version`
   - `metadata.language` → va a `manifest.skill.language`
2. Resolver `framework.ahrena_commit` vía `git -C {repo_root} rev-parse HEAD`
3. Abortar si el SHA no se puede resolver (≥40 chars hex) — `lex-skill-package-structure` prohíbe `ahrena_commit` vacío

### Paso 4: Copiar fuente → build

1. Limpiar `{repo_root}/{skills_build}/{slug}/` si existe
2. Copiar recursivamente `{skills_root}/{slug}/` → `{skills_build}/{slug}/`, ignorando `__pycache__` y `.DS_Store`
3. No transformar — el build aquí es una copia 1:1 de la fuente; las transformaciones (bundle, resolución de dependencias) son responsabilidad de la stack del proyecto consumidor, fuera del alcance de este kata

### Paso 5: Materializar dist

1. Limpiar `{repo_root}/{skills_dist}/{slug}.skill/` si existe
2. Copiar `{skills_build}/{slug}/` → `{skills_dist}/{slug}.skill/` (misma exclusión de `__pycache__`/`.DS_Store`)

### Paso 6: Generar `.skill-manifest.json`

Schema canónico (`lex-skill-package-structure`):

```json
{
  "schema_version": 1,
  "skill": {
    "name": "<slug>",
    "version": "<metadata.version>",
    "language": "<metadata.language>"
  },
  "framework": {
    "ahrena_commit": "<HEAD SHA del framework>"
  },
  "references": [
    {
      "kind": "reference",
      "id": "<derivado de la ruta: references/<id>.md>",
      "source_commit": "<ahrena_commit>",
      "snapshot_path": "references/<id>.md",
      "snapshot_sha256": "<sha256 del archivo>"
    }
  ],
  "files": [
    { "path": ".skill-manifest.json", "sha256": "self" },
    { "path": "SKILL.md", "sha256": "..." },
    { "path": "references/<id>.md", "sha256": "..." },
    ...
  ]
}
```

1. La entrada `.skill-manifest.json` usa el literal `"self"` como sha256 (el manifest se referencia a sí mismo)
2. Las demás entradas: SHA-256 hexadecimal del contenido binario del archivo
3. `files[]` ordenado lexicográficamente por `path`
4. `references[]` ordenado por `id`
5. Persistir en `{skills_dist}/{slug}.skill/.skill-manifest.json` con indent=2 y newline final

### Paso 7: Validar el paquete final

Invocar `scripts/skills/package.py` en modo validación (ya integrado en la pipeline) contra `lex-skill-package-structure`, verificando los 5 criterios:

| Criterio | Verificación |
|----------|--------------|
| (a) frontmatter | `SKILL.md` con `name == slug` y `description ∈ [1, 1024]` |
| (b) manifest | schema_version=1, skill.{name,version,language}, framework.ahrena_commit no-vacío (≥40 hex) |
| (c) files+sha | cada `files[].path` existe y su sha256 coincide (excepto `"self"` para el propio manifest) |
| (d) references | cada `references[]` con `source_commit` no-vacío + snapshot presente + sha256 coincide |
| (e) huérfanos | todo archivo del paquete aparece en `files[]` |

Cualquier falla aquí **bloquea** el paquete — rehacer desde la fuente; jamás editar `{skills_dist}/` a mano.

### Paso 8: Reportar

1. Ruta del paquete producido
2. Ruta del manifest
3. Número de archivos empaquetados
4. Lista de violaciones (vacía en caso de éxito)
5. Exit code `0` cuando el paquete pasa los 5 criterios; `1` en caso contrario

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Directorio de entrega | `{paths.skills_dist}/{slug}.skill/` | filesystem (committed) |
| Manifest | `{paths.skills_dist}/{slug}.skill/.skill-manifest.json` | filesystem |
| Reporte | Texto humano o JSON | `stdout` |

## Ejemplo de Ejecución

### Input

```
kata-skill-package slug=scheduled-payments-skill
```

### Salida esperada

```
✅ package: .dist/scheduled-payments-skill.skill
   manifest: .dist/scheduled-payments-skill.skill/.skill-manifest.json
   files:    18
```

### Contenido de `.dist/scheduled-payments-skill.skill/`

```
.dist/scheduled-payments-skill.skill/
├── SKILL.md
├── .skill-manifest.json    # schema_version=1, files[], references[]
├── references/
│   └── REFERENCE.md
├── scripts/
│   └── ...
└── widgets/
    └── ...
```

## Restricciones

- El kata es **agnóstico al build**: la ley `lex-skill-package-structure` es explícita — Vite/uv/Node/zip son responsabilidad de la stack consumidora. Este kata copia 1:1 desde la fuente; las transformaciones quedan fuera de alcance
- El kata **nunca** edita `{skills_dist}/` a mano fuera del pipeline; rehacer desde la fuente es el único camino de remediación
- El kata **no actualiza** `.directives` — solo lee
- El kata **aborta** si la fuente tiene errores de validación; empaquetar sobre fuente inválida está prohibido
- Para skills con dependencias de runtime (Python venv, Node `node_modules`), la resolución queda fuera de alcance aquí — declarar la limitación en `SKILL.md` o agendar un plan dedicado

## Referencias

- `scripts/skills/package.py` — implementación determinística invocada
- `lex-skill-package-structure` — ley verificada (5 criterios + HARD-GATE)
- `lex-skill-project-structure` — precondición (fuente válida)
- `lex-semantic-version` — versionado de `skill.version`
- `kata-skill-validate` — prerrequisito (mismo runner)
- `warrior-claudionor` — orquestador que invoca este kata
- `cry-skill` — atajo `--mode package`
