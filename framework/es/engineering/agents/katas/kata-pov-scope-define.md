# Kata: Definir Alcance de PoV

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Ingeniería — Agents (etapa pre-operacional): delimitación del alcance de un PoV de agent antes de cualquier instrumentación o implementación

## Objetivo

Producir, en `docs/{context}/agents-pov/{agent}/`, dos artefactos canónicos — `pov.md` (visión general del PoV) y `scope.md` (alcance estabilizado, citado por la DoOC ítem d en `codex-agent-design-docs`) — con alcance **muy estrecho** (1 caso de uso primario), criterio explícito de descontinuación ("si en N semanas la métrica de valor no alcanza X, se cierra") y declaración explícita de `stage: pre-operational`. Aplica la Directriz 05 de `lex-agent-construction-directives` (Alcance Restringido) en la óptica de PoV: dominio estrecho + feedback rápido = curva de aprendizaje pronunciada. Sin estos dos archivos, ningún otro kata del ciclo PoV puede ejecutarse.

## Cuándo Usar

- Cuando `cry-pov --context <name> --agent <slug> --kind <skill|subagent|plugin> --problem <description> --value-metric <description>` es invocado
- Cuando `warrior-claudionor` necesita formalizar alcance antes de delegar implementación
- Cuando un PoV existente perdió foco y exige reescopo (re-ejecución del kata)

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `--context <name>` | Sí | Bounded context en kebab-case (ej.: `reconciliation`, `fiscal-classification`) |
| `--agent <slug>` | Sí | Slug del PoV en kebab-case (ej.: `rec-pov-classifier`). Define el subdir `docs/{context}/agents-pov/{agent}/`. Cuando se omite en `cry-pov`, se deriva de `{context}-pov` |
| `--problem <description>` | Sí | Problema del cliente en 1 frase. Sin genericidades ("automatizar cosas") |
| `--value-metric <description>` | Sí | Métrica leading que se quiere mover, con ventana y threshold |
| `--kind <skill\|subagent\|plugin>` | Sí | Cuál artefacto Anthropic se generará |
| `--out-of-scope` | No | Lista explícita de lo que está fuera; si ausente, se deriva del problema |
| `--discontinuation-criterion` | No | Sobreescribe el default (4 semanas, valor < 50% de la meta declarada) |

## Workflow

```
Progreso:
- [ ] 1. Validar inputs y resolver paths (incluyendo {agent})
- [ ] 2. Redactar bloque "Problema del cliente"
- [ ] 3. Definir caso de uso primario y lo que está fuera
- [ ] 4. Declarar persona + stage explícito
- [ ] 5. Definir criterio de descontinuación
- [ ] 6. Escribir pov.md y scope.md y validar
```

### Paso 1: Validar inputs y resolver paths

1. Se confirma que `--context`, `--agent`, `--problem`, `--value-metric` y `--kind` están completados. Sin cualquiera de ellos, aborta con mensaje claro.
2. Se resuelve `docs/{context}/agents-pov/{agent}/` a partir del `{context}` y `{agent}` informados. Si el directorio ya existe y contiene `pov.md` o `scope.md`, se alerta al usuario y se exige confirmación (`--force`) — sobreescribir un PoV existente es decisión consciente.
3. Se crea el directorio si no existe.

### Paso 2: Redactar bloque "Problema del cliente"

1. Se cita el problema literal del cliente (de `--problem`), sin reescribir.
2. Se añaden 2-3 frases de contexto de negocio (quién sufre, dónde aparece, cuál es el workaround actual). Si el usuario no lo proporcionó, se pregunta.
3. El resultado es la primera sección de `pov.md`.

### Paso 3: Definir caso de uso primario y lo que está fuera

1. Se identifica **1 caso de uso primario** — aquel que, si se resuelve, basta para probar valor. Múltiples casos = alcance demasiado amplio; se reescopa hasta que sobre 1.
2. Se lista lo que está **fuera** (mínimo de 3 ítems). Si `--out-of-scope` fue pasado, se expande; si no, se deriva del problema.
3. Se señala explícitamente en `pov.md` y en `scope.md` cada caso de uso que **no** se aborda en este PoV (referencias futuras van a otro PoV o a Mêtis).

### Paso 4: Declarar persona + stage explícito

1. Se define la persona del PoV en 1 frase (ej.: "Asistente que sugiere asientos contables para conciliación automática de extracto bancario").
2. **Se declara literalmente `stage: pre-operational` en el bloque persona** — precondición de la DoOC ítem 9 (`lex-agent-construction-directives`). Sin esa línea, el kata aborta.

### Paso 5: Definir criterio de descontinuación

1. Default: "Si en 4 semanas el valor medido es < 50% del threshold declarado en `--value-metric`, el PoV se cierra y el aprendizaje se archiva en `value-proof.md`."
2. Si `--discontinuation-criterion` fue pasado, se usa el valor del usuario siempre que contenga: ventana temporal, métrica, threshold.
3. El resultado se convierte en la sección "Criterio de descontinuación" de `pov.md` (y referenciada por `scope.md`).

### Paso 6: Escribir pov.md y scope.md y validar

Los dos archivos son complementarios y separados por intención:

- **`pov.md`** — visión general consumida por humanos y por `cry-agent-design --from-pov` (Mêtis). Secciones: Problema del cliente, Caso de uso primario, Fuera de alcance, Persona, Stage, Value metric leading (copia literal de `--problem` y `--value-metric`), Criterio de descontinuación, Próximos pasos.
- **`scope.md`** — alcance **estabilizado** consumido por la DoOC ítem d (codex-agent-design-docs § 14, "Evidence: SHA del commit en `docs/{context}/agents-pov/{agent}/scope.md` + fecha ≥ 2 semanas atrás"). Secciones: Caso de uso primario (copia literal de `pov.md`), Fuera de alcance (copia literal), Stage (`stage: pre-operational`), Notas de estabilización (fecha de inicio del PoV; quién confirma estabilización). No duplica el problema del cliente ni el value metric — referencia `pov.md`.

Pasos concretos:

1. Se genera `docs/{context}/agents-pov/{agent}/pov.md` con las 8 secciones listadas arriba.
2. Se genera `docs/{context}/agents-pov/{agent}/scope.md` con las 4 secciones listadas arriba. La separación física entre `pov.md` y `scope.md` es lo que permite a Mêtis calcular el SHA del `scope.md` independientemente del `pov.md` para el ítem d de la DoOC.
3. Próximos pasos en `pov.md` siempre listan los 6 katas siguientes a ejecutar: `kata-pov-system-prompt`, `kata-pov-tools-select`, `kata-pov-context-curate`, `kata-pov-observability-instrument`, `kata-pov-feedback-attach`, `kata-pov-value-track`.
4. Se aplica `kata-artifact-self-review` a los dos archivos antes de entregar.

### Validación Final

- [ ] `pov.md` existe en `docs/{context}/agents-pov/{agent}/`
- [ ] `scope.md` existe en `docs/{context}/agents-pov/{agent}/`
- [ ] Ambos contienen literalmente `stage: pre-operational` en el bloque persona / stage
- [ ] Caso de uso primario es exactamente 1 e idéntico en los dos archivos
- [ ] Criterio de descontinuación tiene ventana + métrica + threshold en `pov.md`
- [ ] `scope.md` cita explícitamente la fecha de inicio del PoV (insumo de la ventana de 2 semanas exigida por la DoOC ítem d)
- [ ] Próximos pasos listan los 6 katas POV restantes en `pov.md`

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `pov.md` | Markdown | `docs/{context}/agents-pov/{agent}/pov.md` |
| `scope.md` | Markdown | `docs/{context}/agents-pov/{agent}/scope.md` |

## Ejemplo de Ejecución

### Input

```
cry-pov --context reconciliation \
        --agent rec-pov-classifier \
        --kind skill \
        --problem "Equipo contable dedica 3h/día conciliando extracto bancario con asientos del ERP" \
        --value-metric "% de conciliación automática ≥ 60% en 4 semanas"
```

### Output (extractos)

**`docs/reconciliation/agents-pov/rec-pov-classifier/pov.md`** (extracto):

```markdown
# PoV — reconciliation / rec-pov-classifier

## Problema del cliente

Equipo contable dedica 3h/día conciliando extracto bancario con asientos del ERP.
Hoy lo hacen manualmente en planilla; errores generan asientos duplicados.

## Caso de uso primario

Dado un extracto bancario y la lista de asientos del ERP de la misma ventana,
sugerir el pareo más probable por valor + fecha + descripción similar.

## Fuera de alcance

- Creación automática de asientos en el ERP (solo sugerencia)
- Conciliación multi-cuenta cruzada
- Detección de fraude

## Persona

Asistente que sugiere pareos extracto↔asiento contable.
**stage: pre-operational**

## Value metric leading

% de conciliación automática ≥ 60% en 4 semanas (medido en sandbox real).

## Criterio de descontinuación

Si en 4 semanas el valor medido es < 30% (50% del threshold), el PoV se cierra;
aprendizaje archivado en value-proof.md.

## Próximos pasos

1. kata-pov-system-prompt
2. kata-pov-tools-select
3. kata-pov-context-curate
4. kata-pov-observability-instrument
5. kata-pov-feedback-attach
6. kata-pov-value-track
```

**`docs/reconciliation/agents-pov/rec-pov-classifier/scope.md`** (extracto):

```markdown
# Scope — reconciliation / rec-pov-classifier

> Documento de alcance estabilizado. Consumido por la DoOC ítem d (codex-agent-design-docs).

## Caso de uso primario

Dado un extracto bancario y la lista de asientos del ERP de la misma ventana,
sugerir el pareo más probable por valor + fecha + descripción similar.

## Fuera de alcance

- Creación automática de asientos en el ERP (solo sugerencia)
- Conciliación multi-cuenta cruzada
- Detección de fraude

## Stage

stage: pre-operational

## Notas de estabilización

- PoV iniciado en: {fecha ISO de la creación}
- Confirmador de la estabilización: {responsable; completado por `kata-pov-value-track` cuando el alcance está parado hace ≥ 14 días}
- Referencia cruzada: ver `pov.md` para problema del cliente, value metric y criterio de descontinuación.
```

## Restricciones

- **Nunca** alcance con más de 1 caso de uso primario. Si el problema del cliente cubre más, divídase en múltiples PoVs.
- **Nunca** PoV sin criterio de descontinuación — zombi es riesgo declarado en plan-031.
- **Nunca** persona sin `stage: pre-operational` declarado — bloquea DoOC ítem 9.
- **Nunca** producir solo `pov.md` sin `scope.md` (o viceversa); los dos son contrato con la DoOC.
- El kata **no** delega a Hephaestus ni a Apollo; es trabajo 100% de alcance, anterior a la implementación.

---

**Modelo:** Este Kata aplica la Directriz 05 (`lex-agent-construction-directives`) al ciclo PoV. Foco en estrecho + criterio de salida evita zombis. El par `pov.md` + `scope.md` es el contrato canónico declarado en `codex-agent-design-docs` § 14. Consumido por `warrior-claudionor` como primer paso de `cry-pov`.
