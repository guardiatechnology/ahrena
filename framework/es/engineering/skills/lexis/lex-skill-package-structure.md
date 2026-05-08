# Lexis: Estructura Obligatoria del Paquete `.skill` Entregado

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Paquetes `.skill` versionados en `{paths.skills_dist}/` (default `.dist/`) — entrega final consumida por agentes externos en el formato Anthropic Agent Skills

## Ley

> **Todo paquete `.skill` en `{paths.skills_dist}/` (default `.dist/`) DEBE contener (1) `SKILL.md` con frontmatter Anthropic Agent Skills válido (`name` 1-64 chars en kebab-case que coincida con el nombre del directorio del paquete, `description` 1-1024 chars), (2) `.skill-manifest.json` válido contra el schema canónico Ahrena (`schema_version`, `skill.name`, `skill.version`, `skill.language`, `framework.ahrena_commit` no vacío, `references[]` y `files[]`), (3) para cada entrada en `files[]`: el archivo DEBE existir en el paquete y su `sha256` DEBE coincidir, (4) para cada entrada en `references[]`: archivo presente en `references/<id>.md` con `snapshot_sha256` que coincide, y `source_commit` no vacío, (5) cero archivos huérfanos en el paquete (todo archivo entregado DEBE estar declarado en `files[]`). La ley gobierna el output empaquetado; es AGNOSTIC al build — `Vite`, `uv`, `Node`, `zip`, ports, herramientas de empaquetado son responsabilidad exclusiva del stack del proyecto consumidor (Makefile, GitHub Actions, npm scripts, devops propio). Ahrena valida lo que llega a `.dist/`, no cómo el build llegó allí.**

## Alcance

- **Se aplica a:** todo `.skill` (directorio o archivo sellado per spec Anthropic) entregado en `{paths.skills_dist}/`, en cualquier idioma declarado en `metadata.language`
- **Agentes vinculados:** reviewer humano, `kata-quality-gate` cuando integre la verificación, autores que añaden/modifican paquetes en `.dist/`
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones. Los `.skill` producidos por automatización o manualmente siguen la misma ley

## Schema canónico del `.skill-manifest.json`

```json
{
  "schema_version": 1,
  "skill": {
    "name": "scheduled-payments-skill",
    "version": "0.1.0",
    "language": "pt-BR"
  },
  "framework": {
    "ahrena_commit": "956826f0419aea431e72b8d1796a409d0351e749"
  },
  "references": [
    {
      "kind": "lexis",
      "id": "engineering/skills/lexis/lex-skill-project-structure",
      "source_commit": "956826f0419aea431e72b8d1796a409d0351e749",
      "snapshot_path": "references/lex-skill-project-structure.md",
      "snapshot_sha256": "a1b2c3..."
    }
  ],
  "files": [
    { "path": "SKILL.md", "sha256": "..." },
    { "path": ".skill-manifest.json", "sha256": "self" },
    { "path": "widgets/dist/index.js", "sha256": "..." },
    { "path": "references/lex-skill-project-structure.md", "sha256": "..." }
  ]
}
```

| Campo | Obligatorio | Restricción |
|-------|:-----------:|-------------|
| `schema_version` | Sí | Entero; actual: `1` |
| `skill.name` | Sí | Coincide con el nombre del directorio del `.skill` |
| `skill.version` | Sí | Semver per `lex-semantic-version` |
| `skill.language` | Sí | BCP 47 |
| `framework.ahrena_commit` | Sí | SHA-1 o SHA-256 del commit del framework Ahrena que produjo el paquete; **no puede estar vacío** |
| `references[]` | Sí (la lista puede estar vacía) | Cada entrada: `kind`, `id`, `source_commit` (no vacío), `snapshot_path` (relativo al paquete), `snapshot_sha256` |
| `files[]` | Sí (lista no vacía) | Lista lexicográficamente ordenada de TODOS los archivos del paquete con sus `sha256`; la entrada `.skill-manifest.json` puede usar el valor `"self"` (manifest que se autorreferencia) |

## Reglas

### 1. SKILL.md frontmatter válido

Per `codex-skill-anthropic-agent-skills`:

- `name`: regex `^[a-z0-9](?:[a-z0-9]|-(?!-)){0,62}[a-z0-9]?$`, 1-64 chars, sin palabras reservadas (`anthropic`, `claude`)
- `name` coincide con el nombre del directorio raíz del `.skill`
- `description`: 1-1024 chars, no vacío
- Otros campos opcionales (license, compatibility, metadata, allowed-tools) per spec cuando estén presentes

### 2. `.skill-manifest.json` válido

- Parsea como JSON
- Schema conforme a la tabla anterior
- `framework.ahrena_commit` es un SHA no vacío (40+ caracteres hexadecimales)
- `files[]` contiene **toda** entrada que existe en el paquete (sin huérfanos)
- El ordering de `files[]` es lexicográfico por `path` (per requisito de auditabilidad)

### 3. Los hashes coinciden

Para cada `files[].path`:

- El archivo existe en el paquete
- `sha256(<archivo>) == files[<i>].sha256` (excepto para `.skill-manifest.json` que puede usar el valor `"self"`)

Para cada `references[]`:

- `references/<...>.md` existe (path relativo al paquete)
- `sha256(<archivo de snapshot>) == references[<i>].snapshot_sha256`
- `source_commit` es un SHA no vacío (que referencia el commit del framework Ahrena desde el cual se tomó el snapshot de la referencia)

### 4. Sin archivos huérfanos

Todo archivo en el directorio del paquete (recursivo, excepto el propio `.skill-manifest.json`) DEBE aparecer en `files[]`. Los archivos huérfanos rompen la auditabilidad de lo entregado.

### 5. Agnostic al build

La ley NO prescribe:

- Bundler de widgets (Vite, esbuild, Webpack, Rollup — elección del proyecto)
- Runtime de scripts (Python via uv, pip, conda; Node, Bun, Deno; etc.)
- Comando de empaquetado (zip, tar, formato propietario, etc.)
- Herramienta de cálculo de hash, ordering, mtime
- Pipeline de CI/CD (GitHub Actions, GitLab CI, Jenkins, manual local)
- Ports, hosts, entornos de dev local

El stack del proyecto consumidor decide. La ley solo valida lo que llega a `.dist/`.

## HARD-GATE

Per [`lex-hard-gate-pattern`](../../../_foundation/quality/lexis/lex-hard-gate-pattern.md), el bloqueo textual canónico:

```
<HARD-GATE>
El reviewer (humano) y cualquier agente que valide PRs NO DEBE aprobar
el merge de un PR que añada o modifique un paquete `.skill` en
`{paths.skills_dist}/` (default `.dist/`) sin que el paquete satisfaga
TODOS los 5 criterios canónicos:

  (a) SKILL.md con frontmatter Anthropic válido (name, description)
      y name idéntico al nombre del directorio del paquete
  (b) .skill-manifest.json válido contra el schema (schema_version,
      skill, framework.ahrena_commit no vacío, references[], files[])
  (c) Para cada files[].path: archivo presente + sha256 coincide
  (d) Para cada references[]: snapshot presente + snapshot_sha256
      coincide + source_commit no vacío
  (e) Cero archivos huérfanos (todo archivo del paquete en files[])

Esta regla se aplica a TODO paquete .skill en .dist/, independientemente de:
  - tamaño percibido ("es solo una versión menor")
  - urgencia ("hay que entregar hoy")
  - quién lo solicitó ("el cliente lo está pidiendo")
  - confianza en el autor ("el autor ya lo validó local")

Excepción declarada: Ninguna. Volver a presentar el paquete corregido si
algún criterio falla.
</HARD-GATE>
```

## Consecuencias de la Violación

1. **Bloqueo de merge:** un PR que contenga un `.skill` que falle cualquiera de los 5 criterios es rechazado por el reviewer o (en el futuro) por `kata-quality-gate` integrado.
2. **Alerta:** el validador automático identifica el criterio violado y la ruta del archivo problemático.
3. **Remediación:** el autor corrige el paquete (regenera el build, actualiza el manifest, completa los hashes, declara los archivos huérfanos) y vuelve a presentarlo. No hay merge condicional.

## Ejemplos

### Correcto

```
.dist/hello-skill.skill/
├── SKILL.md                         # name: hello-skill (coincide con el directorio)
├── .skill-manifest.json             # schema_version=1, ahrena_commit=956826f..., 5 files, 1 ref
├── references/
│   └── lex-skill-project-structure.md   # snapshot, snapshot_sha256 coincide, source_commit=956826f...
└── widgets/
    └── dist/
        └── index.js                  # listado en files[], sha256 coincide
```

`.skill-manifest.json` que lista los 5 archivos en `files[]` ordenados; ningún archivo huérfano.

### Incorrecto

```
.dist/hello-skill.skill/
├── SKILL.md                         # name: helloskill (no coincide con el directorio)  ❌ criterio (a)
├── .skill-manifest.json             # framework.ahrena_commit: ""                ❌ criterio (b)
├── references/
│   └── lex-skill-project-structure.md   # source_commit: ""                       ❌ criterio (d)
├── extras/
│   └── debug.log                     # archivo presente, NO en files[]            ❌ criterio (e)
└── widgets/
    └── dist/
        └── index.js                  # sha256 declarado divergente                ❌ criterio (c)
```

Un PR que contenga este paquete debe ser bloqueado en review por 5 criterios violados simultáneamente.

## Validación Automatizada

- **Herramienta:** validador Python (futuro) usando `jsonschema` para validar `.skill-manifest.json` y `hashlib.sha256` para verificar cada archivo declarado; check de archivos huérfanos vía la diferencia entre `os.walk(paquete)` y `manifest.files[]`. Mientras el validador automático no exista, el reviewer humano ejecuta el checklist en el PR.
- **Momento:** PR review (humano hoy; futuro Gate 2 vía `kata-quality-gate` cuando el validador se integre); CI cuando esté habilitado.
- **Métrica:** 0 PRs merged con paquete `.skill` que viole cualquiera de los 5 criterios; 0 entradas con `framework.ahrena_commit` o `source_commit` vacíos; 0 archivos huérfanos.

## Referencias

- `codex-skill-anthropic-agent-skills` — frontmatter SKILL.md, naming, file references
- `codex-skill-project-architecture` — estructura del proyecto fuente que produce el paquete
- `codex-skill-tools-and-widgets` — convención de los manifests `tools/` y `widgets/`
- `lex-skill-project-structure` — separación fuente/build/dist
- `lex-semantic-version` — versionado de `skill.version`
- `lex-hard-gate-pattern` — patrón textual aplicado en esta ley
