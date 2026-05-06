# Kata: Promoción de Insight Aprobado a Idea

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Ámbito:** Product Discovery — promoción de insight con `status: approved` a Idea bajo `docs/discovery/{topic}/ideas/`

## Objetivo

Estandarizar cómo `warrior-phanes` lee un insight aprobado y produce una Idea en el schema canónico (`problem`, `hypothesis`, `target_user`, `success_metric`, `effort_estimate`, `linked_insights[]`), actualizando el insight de origen a `status: promoted` con `idea_ref` apuntando a la Idea creada. La operación está regida por el HARD-GATE 1 de la `lex-discovery-flow` — cualquier precondición no atendida bloquea la promoción.

## Cuándo Usar

- Cuando `cry-ideation` se invoca con el `insight_path` de un insight cuyo `status` es `approved`
- Cuando el usuario pide explícitamente que `warrior-phanes` promueva uno o más insights aprobados a una Idea (caso múltiples insights compartan el mismo problema, pueden ser combinados en una única Idea vía `linked_insights[]`)

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `insight_path` | Sí | Path canónico del insight a promover. Puede ser una string o un array (cuando múltiples insights forman una Idea única) |
| `language` | No | Sobrescribe `language.default` de `.directives` (default: pt-BR) |
| `additional_context` | No | Contexto extra proporcionado por el humano (ej: datos de telemetría, hipótesis refinada) que ayuda a montar `success_metric` o `effort_estimate` |

## Workflow

```
Progreso:
- [ ] 1. Validación de las precondiciones del HARD-GATE 1
- [ ] 2. Lectura de los insights de origen
- [ ] 3. Síntesis de los 5 campos obligatorios de la Idea
- [ ] 4. Generación del archivo de la Idea
- [ ] 5. Actualización del/los insight(s) de origen
- [ ] 6. Validación final
```

### Paso 1: Validación de las precondiciones del HARD-GATE 1

Para cada insight en `insight_path`, verificar **antes de cualquier escritura**:

- [ ] (a) `insight.status == approved` (lee el front-matter; si difiere de `approved`, abortar e informar al humano)
- [ ] (d) Todos los insights en `insight_path` tienen el mismo `topic` (si diverge, abortar; una Idea no puede mezclar topics)

Si cualquier (a) o (d) falla, **interrumpir inmediatamente** e informar al humano con:

- Cuáles insights fallaron en cuál precondición
- Qué acción humana destraba (ej: aprobar el insight, separar en Ideas distintas por topic)

Phanes **NO** cambia status de insight a `approved` — eso es prerrogativa humana per HARD-GATE 2 de la `lex-discovery-flow`.

### Paso 2: Lectura de los insights de origen

Leer íntegramente el/los archivo(s) de insight, capturando:

1. Front-matter (`id`, `topic`, `tags`, `source_refs`)
2. Cuerpo: **Observación**, **Fuente**, **Implicación inicial**, **Preguntas abiertas**
3. Histórico de cambios relevantes (git log del archivo) — útil para entender lo que fue refinado y por qué

Acumular el contenido como base para la síntesis de la Idea.

### Paso 3: Síntesis de los 5 campos obligatorios

Para cada campo obligatorio, aplicar la heurística:

| Campo | Heurística |
|-------|------------|
| `problem` | Reescribir la "Observación" del insight como problema concreto en 1 frase, con magnitud cuando el insight tenga dato cuantitativo. Sin solución embebida |
| `hypothesis` | Estructura "Si X, entonces Y, medido por Z". X = solución conceptual; Y = efecto esperado; Z = criterio mensurable. Cuando el insight no tenga evidencia suficiente para fijar Y/Z, marcar con placeholder explícito (ej: "Y a confirmar vía experimento") en lugar de inventar número |
| `target_user` | Extraer del insight la persona específica (papel + contexto). Evitar "todos los usuarios"; cuando el insight no nombre, usar la persona de la fuente primaria |
| `success_metric` | Métrica leading o lagging con `baseline` (del insight) y `meta` (propuesta inicial basada en ganancia conservadora, e.g.: -50% del baseline). Cuando el insight no tenga baseline, declarar la necesidad de baseline antes de la implementación |
| `effort_estimate` | T-shirt size (`XS`, `S`, `M`, `L`, `XL`) con 1 frase entre paréntesis justificando: dependencias externas, modelo a ser construido, integraciones |

La síntesis es proposición inicial — `warrior-prometheus` posteriormente refina al transformarla en PRD.

### Paso 4: Generación del archivo de la Idea

1. Determinar `{NNN}`: próximo secuencial dentro de `docs/discovery/{topic}/ideas/`
2. Determinar `{slug}`: kebab-case corto resumiendo la Idea (no copiar del insight; puede ser distinto)
3. Componer `id`: `{topic}/ideas/{NNN}-{slug}`
4. Montar front-matter conforme `codex-discovery-artifacts`
5. Estructurar el cuerpo Markdown en las 3 secciones: **Síntesis**, **Insights de origen** (lista enumerada referenciando `linked_insights[]`), **Próximos pasos** (sugerencias de validación adicional, sin decisión de prioridad)
6. Crear directorios intermedios si es necesario y grabar el archivo

### Paso 5: Actualización del/los insight(s) de origen

Para cada insight en `linked_insights[]`:

1. Actualizar `status` a `promoted`
2. Completar `idea_ref` con el `id` de la Idea creada
3. Actualizar `updated_at` al timestamp actual
4. Mantener el resto del archivo intocado (cuerpo del insight permanece como auditoría)

Esta actualización es **la única transición de status que `warrior-phanes` ejecuta autónomamente** — autorizada por HARD-GATE 1 (e), con la precondición de que la Idea haya sido creada con éxito en la etapa anterior.

### Paso 6: Validación final

Antes de entregar:

- [ ] HARD-GATE 1 (a): `status == approved` en todos los insights de origen (validado en Paso 1)
- [ ] HARD-GATE 1 (b): `linked_insights[]` de la Idea tiene al menos 1 entrada
- [ ] HARD-GATE 1 (c): Los 5 campos obligatorios de la Idea están completados con texto no vacío (no placeholder crudo como "TBD")
- [ ] HARD-GATE 1 (d): `topic` de la Idea coincide con el `topic` de TODOS los `linked_insights[]`
- [ ] HARD-GATE 1 (e): Todos los insights de origen fueron actualizados a `status: promoted` con `idea_ref` correcto
- [ ] El `id` de la Idea es único dentro del topic
- [ ] El contenido respeta `lex-tone` y el idioma confirma con `language.default`
- [ ] Ningún insight tuvo campo además de `status`, `idea_ref` y `updated_at` modificado

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Idea nueva | Markdown con front-matter YAML | `docs/discovery/{topic}/ideas/{NNN}-{slug}.md` |
| Insight(s) actualizado(s) | Markdown con front-matter YAML actualizado (mismo path original) | `docs/discovery/{topic}/insights/{NNN}-{slug}.md` |
| Resumen de la ejecución | Mensaje al humano | Sesión actual — confirma la Idea creada, lista los insights promovidos, y señala campos de la Idea que dependen de validación adicional |

## Ejemplo de Ejecución

### Input de Ejemplo

```
insight_path:
  - docs/discovery/scheduled-payments-research/insights/001-manual-reconciliation-bottleneck.md
additional_context: |
  Cliente piloto disponible: oficina Y, con 80 contadores activos
```

### Output de Ejemplo

Archivo generado: `docs/discovery/scheduled-payments-research/ideas/001-auto-reconcile-erp-bank.md`

```markdown
---
id: "scheduled-payments-research/ideas/001-auto-reconcile-erp-bank"
topic: "scheduled-payments-research"
problem: "Los contadores en oficinas medianas gastan en promedio 4h/semana conciliando manualmente lanzamientos divergentes entre el ERP y el extracto bancario, sin percepción de valor agregado por la actividad."
hypothesis: "Si el sistema sugiere conciliación automática con confianza ≥ 90% para divergencias de fecha y duplicación, los contadores aceptarán la sugerencia en ≥ 70% de los casos, reduciendo el tiempo manual en ≥ 60%."
target_user: "Contador operacional en oficinas con 50–500 clientes activos, integrado al ERP X"
success_metric: "Tiempo medio de conciliación por mes por cliente — baseline 4h (entrevista 2026-05-04) → meta 1.5h en 90 días después del release"
effort_estimate: "M (2–4 sprints; depende de modelo de matching e integración con webhooks del ERP X)"
linked_insights:
  - "scheduled-payments-research/insights/001-manual-reconciliation-bottleneck"
created_at: "2026-05-10T15:00:00Z"
updated_at: "2026-05-10T15:00:00Z"
---

# Idea: Sugerencia automática de conciliación ERP × extracto bancario

## Síntesis

Los contadores en oficinas medianas pasan horas semanales conciliando manualmente lanzamientos divergentes; ofrecer sugerencia automática para los dos tipos de divergencia más frecuentes (fecha y duplicación) puede reducir tiempo manual en al menos 60%, validable con piloto en oficina con base de clientes del ERP X.

## Insights de origen

1. **scheduled-payments-research/insights/001-manual-reconciliation-bottleneck** — 4h/semana de conciliación manual; cuello de botella declarado por contadores entrevistados; ERP X requiere 7 pantallas para resolver 1 divergencia.

## Próximos pasos

- Confirmar baseline con 3 entrevistas más en oficinas distintas (validar que 4h/semana es mediana, no outlier)
- Recolectar muestra de 200 divergencias reales para entrenar/evaluar modelo de matching
- Mapear webhooks disponibles en el ERP X (laguna identificada en la entrevista, pero no validada con producto del ERP)
```

Y el insight de origen actualizado:

```markdown
# (mismo contenido del cuerpo)
---
status: promoted
idea_ref: "scheduled-payments-research/ideas/001-auto-reconcile-erp-bank"
updated_at: "2026-05-10T15:00:00Z"
# (demás campos sin alterar)
---
```

## Restricciones

- Nunca alterar `status` de un insight a `approved` — la aprobación es prerrogativa humana per HARD-GATE 2 de la `lex-discovery-flow`
- Nunca producir Idea sin haber validado íntegramente las 5 precondiciones del HARD-GATE 1
- Nunca mezclar `topics` distintos en una única Idea — `topic` de la Idea debe coincidir con el `topic` de todos los `linked_insights[]`
- Nunca completar los 5 campos obligatorios con placeholders crudos como "TBD"; cuando falte evidencia, declarar explícitamente que falta evidencia (ej: "baseline a confirmar vía 3 entrevistas adicionales")
- Nunca alterar campos del insight de origen además de `status`, `idea_ref` y `updated_at`

## Referencias

- `lex-discovery-flow` — ley aplicable; HARD-GATE 1 es la precondición central de este Kata
- `codex-discovery-artifacts` — schema completo, máquina de estados, transición `approved → promoted`
- `kata-discovery-synthesis` — Kata complementario (producción de insights upstream)
- `lex-tone`, `codex-tone` — estilo de redacción
- `warrior-phanes` — agente que ejecuta este Kata
