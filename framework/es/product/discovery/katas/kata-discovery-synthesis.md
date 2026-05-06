# Kata: Síntesis de Insights de Discovery

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Ámbito:** Product Discovery — lectura de fuentes heterogéneas y producción de insights estructurados bajo `docs/discovery/{topic}/insights/`

## Objetivo

Estandarizar cómo `warrior-pitia` lee fuentes (APIs, OpenAPI, Notion, Figma, transcripciones, procesos legados, pantallas) y produce insights de Product Discovery en formato canónico, con `status: proposed` y referencias a las fuentes consultadas. El insight es unidad indivisible de descubrimiento — un insight por archivo, con front-matter conforme `codex-discovery-artifacts`.

## Cuándo Usar

- Cuando `cry-discovery` se invoca con un `topic` y una lista de `source_refs[]`
- Cuando el usuario pide explícitamente que `warrior-pitia` estudie un conjunto de fuentes para un topic existente
- Cuando `warrior-pitia` está en estado `refining` y necesita devolver una v2 de un insight (transición `refining → under_review`)

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `topic` | Sí | Tema de la iniciativa de Discovery en kebab-case (ej: `accountant-onboarding`). Crea el directorio `docs/discovery/{topic}/` si no existe |
| `source_refs[]` | Sí (≥1) | Lista de URLs o paths de las fuentes a estudiar. Puede incluir Notion, Figma, OpenAPI, transcripciones en `docs/transcripts/`, repositorios en GitHub |
| `language` | No | Sobrescribe `language.default` de `.directives` (default: pt-BR) |
| `mode` | No | `new` (default — crea insights nuevos) o `refine` (actualiza insight existente en `status: refining`) |
| `target_insight_id` | Condicional | Obligatorio si `mode == refine` — id del insight a actualizar |
| `feedback` | Condicional | Obligatorio si `mode == refine` — texto del feedback humano que motivó el refinamiento |

## Workflow

```
Progreso:
- [ ] 1. Lectura de las directivas y codex
- [ ] 2. Lectura de las fuentes vía MCP o Read
- [ ] 3. Identificación de candidatos a insight
- [ ] 4. Aplicación del schema canónico
- [ ] 5. Generación del/los archivo(s)
- [ ] 6. Validación final
```

### Paso 1: Lectura de las directivas y codex

1. Leer `.ahrena/.directives` para confirmar `language.default` y `naming.casing`
2. Leer `codex-discovery-artifacts` para internalizar:
   - Direccionamiento `docs/discovery/{topic}/insights/{NNN}-{slug}.md`
   - Schema completo del front-matter
   - Máquina de estados y transiciones válidas
3. Leer `lex-discovery-flow` para internalizar los HARD-GATEs aplicables (especialmente HARD-GATE 2: la creación inicial es de la propia Pitia, pero cualquier transición posterior exige dirección humana)

### Paso 2: Lectura de las fuentes vía MCP o Read

Para cada item en `source_refs[]`, accionar la herramienta apropiada:

| Tipo de fuente | Herramienta | Kata asociado |
|----------------|-------------|---------------|
| URL Notion | MCP `notion-fetch` o `notion-search` | `kata-mcp-notion-read` |
| URL Figma | MCP Figma `get_design_context` o `get_metadata` | `kata-mcp-figma-extract` |
| URL GitHub (repo, issue, PR, OpenAPI) | MCP `gh-*` o `Read` para archivos locales | `kata-mcp-github-read` |
| Path local (`docs/transcripts/...`, OpenAPI YAML, proceso) | `Read` directo | — |

Cuando el MCP correspondiente no esté listado en `mcp.servers` de `.directives`, seguir `lex-mcp` regla 4 (ofrecer elección entre fallback CLI, pausar, o abortar).

Acumular el contenido leído como evidencia. Cuando el contenido sea extenso, guardar fragmentos relevantes citados literalmente (con comillas) en el cuerpo del insight.

### Paso 3: Identificación de candidatos a insight

Para cada candidato a insight, verificar:

1. **Unidad indivisible:** el insight expresa **una** observación. Si el contenido cubre 2 dolores distintos, son 2 insights separados.
2. **Accionable conceptualmente:** el insight apunta a una implicación para el negocio, aunque todavía no proponga solución.
3. **Rastreable:** las `source_refs[]` en el front-matter cubren todas las fuentes que sustentan esa observación.
4. **Sin solución embebida:** si el texto empieza a proponer solución, mover la parte de solución a "Implicación inicial" como hipótesis, no como decisión. La formación de Idea es responsabilidad de `warrior-phanes`.

### Paso 4: Aplicación del schema canónico

Para cada candidato confirmado, montar el front-matter conforme `codex-discovery-artifacts`:

- `id`: `{topic}/insights/{NNN}-{slug}` — `{NNN}` es el próximo número secuencial dentro del topic (leer `docs/discovery/{topic}/insights/` e incrementar)
- `topic`: idéntico al `topic` de input
- `status`: `proposed` (siempre, en la creación inicial)
- `source_refs`: lista de las fuentes efectivamente consultadas (no copiar input crudo — solo las que realmente sustentan ESTE insight)
- `tags`: opcionales; usar cuando ayuden a agregar con otros insights
- `created_at`, `updated_at`: timestamp ISO 8601 actual
- Campos condicionales (`merged_into`, `idea_ref`, `rejected_reason`, `awaiting_evidence_reason`): `null` en la creación

Estructurar el cuerpo Markdown en las 4 secciones: **Observación**, **Fuente**, **Implicación inicial**, **Preguntas abiertas**.

### Paso 5: Generación del/los archivo(s)

1. Crear directorios intermedios si es necesario (`docs/discovery/{topic}/insights/`)
2. Escribir un archivo por insight identificado
3. Cuando `mode == refine`:
   - No crear archivo nuevo — actualizar el existente identificado por `target_insight_id`
   - Actualizar `updated_at` al timestamp actual
   - Reescribir las 4 secciones del cuerpo incorporando el `feedback` recibido
   - Mantener `status: refining` solo hasta la escritura completa; tras persistir, registrar en mensaje al humano que la v2 está lista para `under_review` (la transición en sí depende de acción humana, conforme HARD-GATE 2)

### Paso 6: Validación final

Antes de entregar:

- [ ] Cada insight creado tiene `id` único, `topic` correcto y `source_refs[]` con al menos 1 entrada
- [ ] Ningún insight tiene `status` distinto de `proposed` (en `mode == new`) o distinto de `refining` (en `mode == refine`, e incluso en ese caso el status real solo cambia por humano)
- [ ] Las 4 secciones del cuerpo (Observación, Fuente, Implicación inicial, Preguntas abiertas) están completadas — sin placeholders como "TBD"
- [ ] Ningún insight propone solución; toda hipótesis de solución está en la sección "Preguntas abiertas" como pregunta
- [ ] El contenido respeta `lex-tone` (directo, estratégico, sin buzzwords) y el idioma confirma con `language.default`

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Insight nuevo | Markdown con front-matter YAML | `docs/discovery/{topic}/insights/{NNN}-{slug}.md` |
| Insight actualizado (modo refine) | Markdown con front-matter YAML (mismo path) | `docs/discovery/{topic}/insights/{NNN}-{slug}.md` |
| Resumen de la ejecución | Mensaje al humano | Sesión actual — lista los archivos creados/actualizados y apunta las `Preguntas abiertas` que piden evidencia |

## Ejemplo de Ejecución

### Input de Ejemplo

```
topic: scheduled-payments-research
source_refs:
  - https://www.notion.so/guardia/interview-accountant-2026-05-04-abc123
  - docs/transcripts/process-walkthrough-erp-x.md
  - https://github.com/guardiatechnology/erp-x-spec/blob/main/openapi.yaml
mode: new
```

### Output de Ejemplo

Archivo generado: `docs/discovery/scheduled-payments-research/insights/001-manual-reconciliation-bottleneck.md`

```markdown
---
id: "scheduled-payments-research/insights/001-manual-reconciliation-bottleneck"
topic: "scheduled-payments-research"
status: proposed
source_refs:
  - "https://www.notion.so/guardia/interview-accountant-2026-05-04-abc123"
  - "docs/transcripts/process-walkthrough-erp-x.md"
tags:
  - reconciliation
  - manual-process
created_at: "2026-05-06T11:00:00Z"
updated_at: "2026-05-06T11:00:00Z"
merged_into: null
idea_ref: null
rejected_reason: null
awaiting_evidence_reason: null
---

# Insight: Conciliación manual ERP × extracto es el mayor cuello de botella operacional

## Observación

Los contadores en oficinas de mediano porte gastan, en promedio, 4h por semana conciliando manualmente lanzamientos divergentes entre el ERP y el extracto bancario. La divergencia más frecuente es diferencia de fecha de competencia vs. caja, seguida de duplicación de bajas.

## Fuente

- Entrevista con contador X (2026-05-04): "paso prácticamente todo el martes solo conciliando — nada de lo que hago aquí agrega valor"
- Walkthrough del proceso en el ERP X: 7 pantallas para conciliar 1 lanzamiento divergente

## Implicación inicial

Reducir el tiempo gastado en conciliación manual libera capacidad del contador para análisis — actividad percibida como de mayor valor por él y por la oficina.

## Preguntas abiertas

- ¿Cuál es la distribución real del tiempo gastado entre los tipos de divergencia (fecha, duplicación, valor, contraparte)?
- ¿Cuál es la tasa de aceptación esperada de una sugerencia automática con confianza ≥ 90%?
- ¿Qué ERPs además del X concentran la base de clientes objetivo?
```

## Restricciones

- Nunca proponer solución en el insight; la solución es responsabilidad de Phanes vía Idea
- Nunca consolidar múltiples insights en un archivo único — un insight por archivo
- Nunca alterar `status` de un insight existente a cualquier valor que no sea `refining` (en modo refine, por la propia Pitia) o `proposed` (en modo new); demás transiciones exigen dirección humana per HARD-GATE 2 de la `lex-discovery-flow`
- Nunca embeber referencia a `idea_ref` en la creación inicial; ese campo lo completa Phanes
- Siempre citar fragmento literal (con comillas) al referenciar entrevista o doc — evita interpretación en segundo nivel

## Referencias

- `lex-discovery-flow` — ley aplicable, con los HARD-GATEs que gobiernan status
- `codex-discovery-artifacts` — schema completo, máquina de estados, direccionamiento
- `kata-mcp-notion-read`, `kata-mcp-figma-extract`, `kata-mcp-github-read` — procedimientos de lectura vía MCP
- `lex-mcp` — fallback cuando MCP indisponible
- `lex-tone`, `codex-tone` — estilo de redacción
- `warrior-pitia` — agente que ejecuta este Kata
