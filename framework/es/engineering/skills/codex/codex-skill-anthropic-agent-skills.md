# Codex: Anthropic Agent Skills (formato SKILL.md)

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Especificación canónica del formato Agent Skills de Anthropic — formato externo consumido por Claude API, Claude Code, Cursor, Codex CLI y otros agentes que adoptaron la spec abierta

## Visión general

Agent Skills es un estándar abierto promovido por Anthropic para empaquetar capacidades modulares que extienden agentes de IA. Cada Skill es un directorio con un archivo `SKILL.md` (YAML frontmatter + Markdown) que el agente carga progresivamente: metadata siempre, cuerpo cuando se activa, recursos bajo demanda.

Este Codex es la referencia conceptual y de campos de la spec. No cubre la convención Ahrena de empaquetar tools MCP y widgets React — eso queda en `codex-skill-tools-and-widgets`. No cubre el layout del proyecto fuente en el repositorio — eso queda en `codex-skill-project-architecture`.

Fuente canónica de la spec: [agentskills.io/specification](https://agentskills.io/specification). Documentación de Anthropic: [platform.claude.com/docs/en/agents-and-tools/agent-skills/overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).

## Contexto

- **Dominio:** formato externo de skill (entrega final consumida por agentes fuera del Ahrena)
- **Público objetivo:** autores de skills, `kata-init-skill`
- **Actualización:** cuando la spec oficial evolucione; revisar `metadata.spec_version` del skill producido

## Contenido

### Estructura del directorio

Un skill es un directorio con, como mínimo, un `SKILL.md`:

```
skill-name/
├── SKILL.md # Obligatorio — metadata + instrucciones
├── scripts/ # Opcional — código ejecutable
├── references/ # Opcional — documentación adicional
├── assets/ # Opcional — plantillas, recursos estáticos
└── ... # Cualquier otro archivo
```

**Restricción importante:** el nombre del directorio raíz **DEBE** ser idéntico al valor del campo `name` en el frontmatter.

### Frontmatter del SKILL.md

| Campo | Obligatorio | Restricciones |
|-------|:-----------:|---------------|
| `name` | Sí | 1-64 caracteres; solo `a-z`, `0-9` y guion; no empieza ni termina en guion; sin `--`; **debe coincidir con el nombre del directorio** |
| `description` | Sí | 1-1024 caracteres; no vacío; describe **qué hace** y **cuándo usar** |
| `license` | No | Nombre de licencia o referencia a archivo `LICENSE` empaquetado |
| `compatibility` | No | 1-500 caracteres; requisitos de entorno (producto destino, paquetes del sistema, acceso a la red) |
| `metadata` | No | Mapa clave→valor arbitrario para propiedades no definidas por la spec |
| `allowed-tools` | No | Cadena separada por espacios, herramientas preaprobadas (experimental; el soporte varía por agente) |

#### `name`

Identificador del skill. Coincide con el nombre del directorio raíz. No puede usar palabras reservadas (`anthropic`, `claude`) según la documentación de Anthropic.

Válidos: `pdf-processing`, `data-analysis`, `code-review`.

Inválidos: `PDF-Processing` (mayúsculas), `-pdf` (guion al inicio), `pdf--processing` (guiones consecutivos).

#### `description`

Texto que el agente lee al inicio (Level 1) para decidir cuándo activar el skill. **Debe incluir keywords concretas** que coincidan con la tarea del usuario; descripciones genéricas (`"helps with PDFs"`) reducen la activación correcta.

Bueno: *"Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction."*

#### `license`

Identificación corta (p. ej., `Apache-2.0`, `MIT`) o referencia a un archivo empaquetado (p. ej., `Proprietary. LICENSE.txt has complete terms`).

#### `compatibility`

Cuando el skill tiene requisitos no obvios. Ejemplos válidos:

```yaml
compatibility: Designed for Claude Code (or similar products)
compatibility: Requires git, docker, jq, and access to the internet
compatibility: Requires Python 3.14+ and uv
```

La mayoría de los skills no necesita el campo.

#### `metadata`

Mapa libre. Convenciones Ahrena (no de la spec) que el build del proyecto consumidor puede honrar:

| Clave | Uso Ahrena |
|-------|------------|
| `version` | Semver según `lex-semantic-version` (p. ej., `"0.1.0"`) |
| `language` | BCP 47 del contenido del skill (`pt-BR`, `es`, `en`) |
| `author` | Persona, equipo u organización autora |
| `spec_version` | Versión de la spec Agent Skills validada (control de drift) |

Otras claves son libres; el agente que consume solo ve el mapa crudo. Se recomienda prefijar las claves específicas de la organización (p. ej., `guardia.bounded_context: scheduled-payments`) para evitar colisiones.

#### `allowed-tools`

Cadena separada por espacios, en formato `Tool` o `Tool(scope)`:

```yaml
allowed-tools: Bash(git:*) Bash(jq:*) Read
```

**Experimental** — el soporte varía entre Claude Code, Claude API y otros agentes. Tratar como sugerencia, no como contrato fuerte.

### Cuerpo del SKILL.md (Markdown después del frontmatter)

Sin restricción estructural. El agente lee el cuerpo completo cuando activa el skill (Level 2). Recomendaciones de la spec:

- Mantener por debajo de **500 líneas** y **5 000 tokens**
- Mover el material extenso a `references/`
- Incluir: pasos, ejemplos de input/output, edge cases comunes

Sin restricción no significa ausencia de criterio — un cuerpo verboso afecta el token budget de toda la invocación.

### Directorios opcionales

#### `scripts/`

Código ejecutable invocado por el agente vía bash. Los lenguajes aceptados dependen del runtime del agente (Python, Bash, Node son comunes). Deben:

- Ser self-contained o documentar las dependencias de forma explícita
- Emitir mensajes de error útiles
- Tratar edge cases sin crash silencioso

Cuando el agente ejecuta un script, **solo la salida** entra en el contexto — el código fuente permanece en el filesystem (Level 3). Eso hace que el script sea más barato en tokens que pedirle al agente generar código equivalente inline.

#### `references/`

Markdown adicional para que el agente cargue **bajo demanda**. Convención común:

- `REFERENCE.md` — referencia técnica detallada
- `FORMS.md` — plantillas o formatos estructurados
- Archivos por dominio (`finance.md`, `legal.md`)

Mantener cada archivo enfocado y corto reduce el costo cuando el agente trae solo lo que necesita.

#### `assets/`

Recursos estáticos: plantillas de documento, imágenes, data files (CSV, JSON), schemas. El agente los abre cuando el flujo de la tarea lo requiere.

### Carga progresiva (3 niveles)

| Nivel | Cuándo carga | Costo aproximado | Contenido |
|-------|--------------|------------------|-----------|
| 1 — Metadata | Siempre, al inicio | ~100 tokens por skill | `name` + `description` del frontmatter |
| 2 — Instrucciones | Cuando el skill se activa | < 5 000 tokens recomendado | Cuerpo Markdown del `SKILL.md` |
| 3 — Recursos | Bajo demanda | Prácticamente ilimitado (no entra en el contexto hasta leerlo) | Archivos en `scripts/`, `references/`, `assets/` |

La partición del contenido en capas es el principio central de la spec. Skills bien diseñados respetan esa jerarquía — metadata escueto, cuerpo conciso, peso en los recursos.

### Referencias entre archivos

Rutas **relativas a la raíz del skill**:

```markdown
Vea [la guía de referencia](references/REFERENCE.md) para más detalles.

Para extraer, ejecute: `scripts/extract.py`
```

La spec recomienda mantener las referencias en **un nivel de profundidad** desde el `SKILL.md`. Cadenas profundas dificultan la carga progresiva.

### Disponibilidad por superficie

Un skill producido en la spec de Anthropic es consumible por:

| Superficie | Soporte | Distribución |
|------------|---------|--------------|
| Claude API | Pre-built + custom | Endpoint `/v1/skills`; requiere beta headers `code-execution-2025-08-25`, `skills-2025-10-02`, `files-api-2025-04-14` |
| Claude Code | Custom | Filesystem — `~/.claude/skills/{slug}/` (personal) o `.claude/skills/{slug}/` (proyecto) |
| claude.ai | Pre-built + custom (zip upload en Settings → Features; planes Pro+) | Por usuario; sin distribución org-wide |
| Cursor / Codex CLI / Gemini CLI | Adoptaron la spec abierta | Filesystem similar a Claude Code |

Los skills **no se sincronizan automáticamente entre superficies** — upload por separado en cada superficie.

### Restricciones de runtime

| Superficie | Red | Paquetes |
|------------|-----|----------|
| Claude API | Sin acceso externo | Solo preinstalados; sin instalación en runtime |
| Claude Code | El mismo acceso del programa del usuario | Se recomienda instalar local al skill, no global |
| claude.ai | Variable (config del admin/user) | Conforme a la superficie |

`compatibility` en el frontmatter es donde se declaran esas dependencias — los agentes que no las satisfacen pueden rechazar la activación.

### Validación

La spec mantiene el CLI [`skills-ref`](https://github.com/agentskills/agentskills/tree/main/skills-ref):

```bash
skills-ref validate ./my-skill
```

Verifica frontmatter válido, naming y estructura mínima. El stack de build del proyecto consumidor puede integrar esa validación.

### Seguridad

La documentación de Anthropic es explícita: tratar el skill como software instalado. Un skill malicioso puede invocar tools de modo perjudicial, filtrar datos o ejecutar código fuera del propósito declarado. Auditar:

- Cada archivo empaquetado (SKILL.md, scripts, references, assets)
- Llamadas de red (los skills que consultan URLs externas tienen riesgo amplificado)
- Patrones de acceso a archivo / bash incompatibles con el `description`

Los skills producidos en el Ahrena son auditables por la trilla de commit (refs con snapshot por hash, manifest determinístico en).

## Restricciones

- La spec **no define** layout para tools MCP ni widgets UI. La convención Ahrena (`codex-skill-tools-and-widgets`,) crea directorios `tools/` y `widgets/` adicionales — los agentes que solo conocen la spec ignoran esos directorios. Documentar la convención como "extensión Ahrena" es obligatorio en el SKILL.md generado.
- La spec **no define** el versionado del skill en sí — el Ahrena lo coloca en `metadata.version` (semver según `lex-semantic-version`).
- La spec **no define** internacionalización — el Ahrena lo coloca en `metadata.language`. Cada skill empaquetado es monoidioma.

## Glosario

| Término | Definición |
|---------|-----------|
| Agent Skills | Estándar abierto de Anthropic para skills basados en filesystem |
| SKILL.md | Archivo raíz con frontmatter + cuerpo |
| Progressive disclosure | Carga en 3 niveles (metadata, instrucciones, recursos) |
| Pre-built Skill | Skill de Anthropic disponible sin upload (PowerPoint, Excel, Word, PDF) |
| Custom Skill | Skill creado por terceros, distribuido vía filesystem o upload |

## Referencias

- [Spec canónica — agentskills.io/specification](https://agentskills.io/specification)
- [Documentación Anthropic — Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Repo abierto — anthropics/skills](https://github.com/anthropics/skills)
- [Engineering blog — Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- `codex-skill-project-architecture` — layout del proyecto fuente Ahrena (`skills/{slug}/`)
- `codex-skill-tools-and-widgets` — convención Ahrena para `tools/` (MCP) y `widgets/` (React)
- `lex-skill-project-structure` — ley del layout del proyecto fuente
