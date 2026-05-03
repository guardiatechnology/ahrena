# Kata: Planificar una Tarea

> **Prefijo:** `kata-` | **Tipo:** Habilidad Repetible | **Alcance:** Creación y mantenimiento de documentos de plan de tareas por agentes, conforme a `lex-agent-planning`

## Objetivo

Crear o actualizar el documento de plan de una tarea antes de su ejecución, garantizando que el objetivo, el alcance, los pasos y las dependencias estén documentados y confirmados por el usuario antes de que comience cualquier acción irreversible.

## Cuándo Usar

- Al inicio de cualquier tarea de múltiples pasos
- Antes de invocar warriors, katas en secuencia o cries
- Antes de modificar múltiples archivos en una única sesión
- Cuando el usuario pide "hacer X" y X tiene más de un paso discernible

## Entradas

| Entrada | Obligatorio | Descripción |
|---------|:-----------:|-------------|
| Descripción de la tarea | Sí | Lo que el agente necesita hacer (puede ser vaga — el kata clarifica) |
| Issue de referencia | No | `owner/repo#N` cuando la tarea se origina de un issue de GitHub |
| Directorio del agente | No | Predeterminado resuelto automáticamente; puede ser sobrescrito por `paths.plans` en `.directives` |

## Flujo de Trabajo

```
Progreso:
- [ ] 1. Resolver path y nombre del archivo de plan
- [ ] 2. Verificar planes existentes
- [ ] 3. Redactar el plan
- [ ] 4. Presentar al usuario y confirmar
- [ ] 5. Escribir el archivo de plan
- [ ] 6. Ejecutar la tarea actualizando el plan
- [ ] 7. Finalizar el plan
```

### Paso 1: Resolver Path y Nombre del Archivo de Plan

1. Leer `.ahrena/.directives` y verificar si `paths.plans` está definido
2. Si sí → usar ese valor como directorio base
3. Si no → usar predeterminado por agente:
   - Claude Code → `.claude/plans/`
   - Cursor → `.cursor/plans/`
   - Desconocido → `.plans/`
4. Listar archivos existentes en el directorio (si existe) para determinar el siguiente número secuencial
5. Componer el nombre: `plan-{NNN}-{slug}.md` donde `{slug}` es el resumen de la tarea en kebab-case (máx. 60 caracteres)

### Paso 2: Verificar Planes Existentes

1. Si el directorio de planes no existe → se creará en el Paso 5
2. Si existe → listar planes con estado `in-progress` o `pending`:
   - Si hay un plan `in-progress` para la misma tarea → preguntar al usuario si desea retomar o crear uno nuevo
   - Si retoma → cargar el plan existente y saltar al Paso 6

### Paso 3: Redactar el Plan

Con base en la descripción de la tarea:

1. Identificar el **objetivo** (por qué existe esta tarea — máx. 3 frases)
2. Listar todos los archivos o sistemas que se verán afectados (**alcance**)
3. Descomponer la tarea en **pasos atómicos y verificables** (cada paso = una acción completable)
4. Identificar **dependencias** (otros planes, issues, decisiones pendientes)
5. Listar **riesgos conocidos** (qué puede salir mal; si ninguno, escribir "Ninguno identificado")

### Paso 4: Presentar al Usuario y Confirmar

Presentar el borrador del plan con la pregunta:

> "Este es el plan para la tarea. ¿Desea ajustar algo antes de que comience?"

Esperar respuesta. Incorporar ajustes si se solicitan. **No iniciar la ejecución antes de la confirmación.**

### Paso 5: Escribir el Archivo de Plan

1. Crear el directorio si no existe
2. Escribir el archivo con front-matter completo (`status: pending`) y el cuerpo del plan
3. Confirmar al usuario: "Plan guardado en `{path}`. Iniciando ejecución."
4. Actualizar `status` a `in-progress` y `updated_at`

### Paso 6: Ejecutar la Tarea Actualizando el Plan

Durante la ejecución:
- Marcar cada paso con `[x]` al completarlo
- Actualizar `updated_at` con cada cambio de paso
- Si se descubre un nuevo paso durante la ejecución → agregarlo al plan antes de ejecutarlo
- Si surge un bloqueo → registrarlo en el plan como nota y comunicarlo al usuario

### Paso 7: Finalizar el Plan

Cuando todos los pasos estén `[x]`:
1. Actualizar `status` a `done`
2. Actualizar `updated_at`
3. Informar al usuario: "Tarea completada. Plan en `{path}` marcado como `done`."
4. Recordar al usuario que el plan debe commitearse junto con los artefactos producidos

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Archivo de plan | Markdown con front-matter YAML | `{plans_dir}/plan-{NNN}-{slug}.md` |

## Ejemplo de Ejecución

### Entrada

```
Tarea: completar migración de cries a lex-feature-design-docs
Issue: guardiafinance/ahrena#42
```

### Paso 1 — Path resuelto

```
Agente: Claude Code
Directorio: .claude/plans/
Siguiente número: 001 (directorio vacío)
Archivo: .claude/plans/plan-001-complete-feature-design-docs.md
```

### Paso 3 — Borrador

```markdown
## Objetivo
Completar la actualización de Cries y katas que aún referencian paths.oas/paths.events/paths.domain
tras la creación de lex-feature-design-docs. Los warriors y katas principales ya están actualizados;
faltan los puntos de entrada (Cries) y 2 katas con referencias residuales.

## Alcance
- cry-api-design.md, cry-event-storm.md, cry-feature-design.md, cry-full-design.md (pt-BR, en, es)
- kata-api-design-review.md (pt-BR, en, es)
- kata-api-design-doc.md — corregir referencias a .directives (pt-BR, en, es)
- .cursor/commands/ correspondientes

## Pasos
- [ ] 1. Abrir issue en GitHub para rastrear el trabajo
- [ ] 2. Crear branch feat/{N}-complete-feature-design-docs
- [ ] 3-6. Actualizar 4 cries (× 3 idiomas)
- [ ] 7. Actualizar kata-api-design-review (× 3 idiomas)
- [ ] 8. Corregir kata-api-design-doc (× 3 idiomas)
- [ ] 9. Actualizar .cursor/commands/ afectados
- [ ] 10. Commitear todo (nuevos artefactos + cries + katas)
- [ ] 11. Abrir PR
```

### Paso 4 — Confirmación

```
Agente: "Este es el plan para completar la migración de feature-design-docs.
  Total: ~18 archivos. ¿Desea ajustar algo antes de que comience?"
```

## Restricciones

- **Nunca iniciar la ejecución sin confirmación del usuario** en el Paso 4
- **Nunca crear un plan vacío** — si la descripción es insuficiente para descomponer pasos, hacer preguntas de aclaración primero
- **Nunca eliminar un plan** — los planes cancelados se convierten en `abandoned`, no se eliminan
- **Nunca omitir el front-matter** — `plan_id`, `title`, `status`, `agent`, `created_at`, `updated_at` son obligatorios; `issue` cuando corresponda

## Referencias

- `lex-agent-planning` — Ley
- `codex-agent-planning` — Manual con plantilla completa y buenas prácticas
- `lex-checkpoint` — Seguimiento del estado de sesión (complementario)
- `lex-directives` — Lectura de `.ahrena/.directives`
