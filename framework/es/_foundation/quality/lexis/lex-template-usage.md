# Lexis: Uso Obligatorio de Plantillas

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Creación de cualquier artefacto del Ahrena

## Propósito

El Ahrena mantiene plantillas oficiales (samples) para cada Pilar de la taxonomía — Lexis, Codex, Katas, Warriors y Cries. Esas plantillas garantizan consistencia estructural, completitud de información y estandarización entre todos los artefactos del framework.

Sin esa estandarización, los agentes pueden generar artefactos con secciones faltantes, estructura inconsistente o nomenclatura divergente, comprometiendo la interoperabilidad y la gobernanza del sistema.

Esta Lexis existe para garantizar que **todo artefacto nuevo se cree a partir de la plantilla oficial correspondiente**, preservando la integridad estructural del framework.

## Ley

> **Todo agente DEBE utilizar la plantilla oficial (sample) del Pilar correspondiente como base estructural al crear cualquier nuevo artefacto del Ahrena — Lexis, Codex, Kata, Warrior o Cry.**

## Reglas

### 1. Plantilla obligatoria por Pilar

Antes de crear un nuevo artefacto, el agente **DEBE** consultar la plantilla (sample) correspondiente al Pilar. Las rutas canónicas están en `.ahrena/.directives` en la sección `paths.samples` (ej.: `paths.samples.lexis`, `paths.samples.codex`, etc.). Valores típicos en el repositorio Ahrena:

| Pilar | Plantilla (paths.samples en .directives) | Plantilla (.cursor/) |
|-------|----------------------------------------|---------------------|
| **Lexis** | `templates/lex-sample.md` | `.cursor/rules/samples/lex-sample.mdc` |
| **Codex** | `templates/codex-sample.md` | `.cursor/rules/samples/codex-sample.mdc` |
| **Katas** | `templates/kata-sample.md` | `.cursor/skills/samples/kata-sample.mdc` |
| **Warriors** | `templates/warrior-sample.md` | `.cursor/skills/samples/warrior-sample.mdc` |
| **Cries** | `templates/cry-sample.md` | `.cursor/commands/samples/cry-sample.mdc` |

El agente **DEBE** usar los valores de `paths.samples` del `.directives` cuando estén disponibles; la tabla anterior refleja la convención predeterminada.

### 2. Proceso de creación

Al recibir una solicitud para crear un nuevo artefacto, el agente **DEBE**:

1. **Identificar el Pilar** — determinar si el artefacto es una Lexis, Codex, Kata, Warrior o Cry.
2. **Leer la plantilla** — cargar el contenido del sample correspondiente usando la tabla anterior.
3. **Usar como base estructural** — crear el nuevo artefacto manteniendo todas las secciones, encabezados y estructura de la plantilla.
4. **Rellenar los campos** — sustituir los campos entre corchetes `[]` por el contenido específico del artefacto.
5. **Eliminar instrucciones de la plantilla** — eliminar textos explicativos genéricos del sample (ej.: "Describa por qué existe esta ley") y sustituirlos por el contenido real.
6. **Respetar el direccionamiento** — guardar en la ruta correcta conforme a la taxonomía: `<clade>/<subclade>/<pilar>/<prefijo>-<nombre>.md`.

### 3. Estructura inviolable

El agente **NO PUEDE**:

- Omitir secciones obligatorias definidas en la plantilla.
- Inventar una estructura propia ignorando la plantilla.
- Alterar los encabezados estándar de la plantilla (puede añadir subsecciones, nunca eliminar las existentes).

### 4. Creación dual (framework + IDE)

Cuando el contexto lo exija, el agente **DEBE** crear el artefacto en ambos lugares:

- **`framework/`** — versión canónica en `.md` puro, sin frontmatter de IDE.
- **`.cursor/`** (u otra IDE) — versión derivada en `.mdc` con frontmatter YAML apropiado.

### 5. Frontmatter obligatorio en `.cursor/`

Al crear la versión `.mdc` para Cursor, el agente **DEBE** incluir el frontmatter YAML correcto al inicio del archivo, delimitado por `---`. El frontmatter varía según el recurso de Cursor utilizado:

#### Rules (Lexis y Codex)

```yaml
---
description: "Descripción concisa de lo que hace la rule y cuándo debe consultarse."
globs: "patrón/glob/si/aplica"
alwaysApply: false
---
```

| Campo | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `description` | Sí | Texto que Cursor muestra para que el agente entienda cuándo consultar esta rule |
| `globs` | Condicional | Patrón glob de archivos a los que aplica la rule. **Omitir o dejar vacío** cuando la rule aplica a todos los archivos o no está vinculada a tipos de archivo específicos |
| `alwaysApply` | Sí | `true` si la rule debe cargarse en toda interacción; `false` si se activa bajo demanda o por glob |

#### Skills (Katas y Warriors)

```yaml
---
name: prefijo-nombre
description: "Descripción concisa de lo que hace la skill y cuándo debe usarse."
---
```

| Campo | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `name` | Sí | Identificador de la skill, usando el prefijo del Pilar (ej.: `kata-code-review`, `warrior-spartacus`) |
| `description` | Sí | Texto que Cursor muestra para que el agente entienda cuándo activar esta skill |

#### Commands (Cries)

```yaml
---
description: "Descripción concisa de lo que hace el comando al ser invocado."
---
```

| Campo | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `description` | Sí | Texto que Cursor muestra para que el usuario entienda qué hace el comando |

### 6. Prefijo obligatorio

Todo artefacto **DEBE** usar el prefijo correcto de su Pilar en el nombre del archivo:

| Pilar | Prefijo | Ejemplo |
|-------|---------|---------|
| Lexis | `lex-` | `lex-no-secrets.md` |
| Codex | `codex-` | `codex-architecture.md` |
| Katas | `kata-` | `kata-code-review.md` |
| Warriors | `warrior-` | `warrior-spartacus.md` |
| Cries | `cry-` | `cry-changelog.md` |

## Alcance

- **Se aplica a:** creación de cualquier artefacto en cualquier Clade y Subclade
- **Agentes vinculados:** todos los Warriors y agentes genéricos
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de Violación

1. **Rechazo del artefacto:** artefactos creados sin seguir la plantilla oficial deben reescribirse antes de ser aceptados.
2. **Inconsistencia estructural:** artefactos fuera del estándar comprometen la navegabilidad y la gobernanza del framework.
3. **Remediación:** el agente debe recrear el artefacto usando la plantilla correcta, preservando el contenido ya producido pero adecuándolo a la estructura estándar.

## Ejemplos

### Correcto

```
Usuario: Crea una nueva Lexis sobre code review obligatorio.

Agente:
1. Identifica el Pilar: Lexis
2. Lee la plantilla: framework/lexis/lex-sample.md
3. Crea el artefacto siguiendo la estructura:
   - # Lexis: Code Review Obligatorio
   - > Prefijo: lex- | Tipo: Ley Inquebrantable | Alcance: ...
   - ## Propósito
   - ## Ley
   - ## Alcance
   - ## Consecuencias de Violación
   - ## Ejemplos
   - ## Validación Automatizada
4. Guarda en: engineering/quality/lexis/lex-code-review.md
5. Crea versión .cursor con frontmatter:
   ---
   description: "Code review obligatorio. Todo PR debe pasar por revisión antes del merge."
   alwaysApply: false
   ---
6. Guarda en: .cursor/rules/engineering/quality/lex-code-review.mdc
```

### Incorrecto

```
Usuario: Crea una nueva Lexis sobre code review obligatorio.

Agente: Aquí está la ley:

# Ley de Code Review
Todo PR necesita revisión.

# ❌ El agente ignoró la plantilla, creó estructura propia,
# omitió secciones obligatorias y no siguió el prefijo correcto.
# La versión .mdc se creó sin frontmatter YAML.
```

## Validación Automatizada

- **Herramienta:** verificación por el propio agente antes de guardar el artefacto
- **Momento:** durante la creación de cualquier nuevo artefacto del Ahrena
- **Métrica:** 100 % de los artefactos deben seguir la estructura de la plantilla oficial de su Pilar
