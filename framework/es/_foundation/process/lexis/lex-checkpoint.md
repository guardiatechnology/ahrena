# Lexis: Checkpoint de Sesión

> **Prefijo:** `lex-` | **Tipo:** Ley Inviolable | **Alcance:** Contexto de sesión entre conversaciones con agentes de IA, complementario a `lex-agent-planning`

## Propósito

Las sesiones con agentes de IA son efímeras — al cerrarse, el contexto acumulado fuera del plan (hilos paralelos, scratchpad pre-plan, hand-off entre múltiples planes activos, anotaciones de retomada) se pierde. `lex-agent-planning` cubre la fuente de verdad de la **task** (committed, con Steps `[x]`, Decisiones cerradas, Riesgos). El checkpoint cubre la **sesión** — lo que no cabe en un único plan.

Esta Lexis existe para garantizar que **el contexto de sesión fuera del plan** sea recuperable entre conversaciones, sin duplicar lo que el plan ya registra. El checkpoint es scratchpad de ventana de trabajo, no duplicado del plan.

## Ley

> **Todo agente DEBE verificar el archivo `.checkpoint` al iniciar una sesión y DEBE guardar el checkpoint bajo demanda del usuario o al cerrar la sesión cuando hubo cambio de contexto. El contenido del `.checkpoint` DEBE seguir el schema canónico (Session focus, Active plans, Open threads, Notes) y NO DEBE duplicar lo que vive en el plan (Activity, Steps, Decisiones cerradas, Riesgos, Artifacts). La superposición con `lex-agent-planning` está PROHIBIDA.**

## Reglas

### 1. Verificación obligatoria al iniciar

Al iniciar una sesión, el agente **DEBE**:

1. Verificar si existe un archivo `.checkpoint` en la raíz del workspace.
2. Si existe y está en el schema nuevo (4 secciones canónicas): leer y presentar al usuario un resumen (Session focus + Active plans + Open threads).
3. Si existe y está en el schema antiguo (Activity/Status/Progress/Decisions made/Next steps/Artifacts produced): emitir warning de deprecation, proseguir como si no hubiera checkpoint, y marcarlo para sobrescritura en la próxima invocación de save.
4. Preguntar al usuario si desea **retomar** el contexto guardado o **iniciar una nueva ventana** (descartando el checkpoint anterior).
5. Si no existe, proseguir normalmente. La ausencia de `.checkpoint` es un escenario válido — no es violación.

### 2. Guardado bajo demanda + fin de sesión

El agente **DEBE** persistir el checkpoint:

1. **Bajo demanda** — cuando el usuario invoque `cry-checkpoint` o lo solicite explícitamente.
2. **Al cerrar la sesión** — solo si hubo cambio real de contexto (nuevo Session focus, nuevo Active plan, nuevo Open thread, nuevas Notes). Cerrar sesión sin cambio de contexto NO requiere save.

La obligación automática de guardar después de cada activity fue eliminada — la granularidad de activity ya vive en el plan (`lex-agent-planning`).

### 3. Schema canónico

El archivo `.checkpoint` **DEBE** contener exactamente las 4 secciones siguientes, en cualquier orden:

```markdown
# Session checkpoint

- **Last update:** YYYY-MM-DDTHH:MM:SSZ
- **Session id:** {chat/session id o commit short SHA del HEAD}

## Session focus

{1-3 frases describiendo el foco general de la ventana de trabajo. No es Activity formal — es el puntero mental que ayuda al agente a reorientarse al retomar. Ejemplo: "Reposicionando lex-checkpoint en paralelo con revisión de plan-026."}

## Active plans

{Lista de plan-IDs activos en la sesión, con 1 línea de contexto cada uno. No duplicar contenido del plan — solo punteros.}

- `plan-026` — commit-readiness-observer; aguardando ajuste de dependencia de `.checkpoint`
- `plan-040` — reposicionamiento del `.checkpoint`; en redacción de los artefactos pt-BR

## Open threads

{Hilos de conversación que no se convirtieron en plan formal pero deben retomarse. Cada hilo en 1-2 líneas. Cubre lo que escapa de un único plan — decisiones pendientes transversales, ideas paralelas que merecen retorno.}

- Evaluar si `lex-agent-planning` debería absorber "Risks de la sesión" como categoría no bloqueante
- Decidir si los Brand-related cries deben vivir en `_foundation` o en `design/`

## Notes

{Texto libre. Pensamientos, enlaces, referencias, snippets, recordatorios. Sin schema obligatorio. Es el scratchpad puro.}
```

Los campos `Activity`, `Status`, `Progress`, `Decisions made`, `Next steps`, `Artifacts produced` (del schema antiguo) **NO PUEDEN** aparecer en el checkpoint nuevo — ese contenido vive en el plan (`lex-agent-planning`).

### 4. Responsabilidad compartida

- Cualquier agente (Warrior) que actúe en la sesión **hereda** esta obligación.
- El checkpoint es **agnóstico de disciplina** — se aplica a sesiones en cualquier Clade.
- El archivo `.checkpoint` **no debe ser commiteado** en el repositorio (debe estar en `.gitignore`).

### 5. Relación con `lex-agent-planning`

La delimitación entre plan y checkpoint es categórica:

| Contenido | Vive en |
|---|---|
| Objetivo, Steps `[x]`, Status (`pending → in-progress → done`), Decisiones cerradas, Riesgos, Verificación | Plan (`.claude/plans/plan-NNN-{slug}.md`) — committed |
| Activity, Progress detallado, Artifacts produced, Next steps de una task | Plan — committed |
| Foco general de la ventana de trabajo (Session focus) | Checkpoint — gitignored |
| Punteros para múltiples planes activos (Active plans) | Checkpoint — gitignored |
| Hilos paralelos que no se convirtieron en plan (Open threads) | Checkpoint — gitignored |
| Scratchpad libre, enlaces, recordatorios (Notes) | Checkpoint — gitignored |

En caso de duda, el contenido va al plan. El plan vence en durabilidad (committed) y en alcance (cubre task; el checkpoint cubre sesión).

## Cobertura

- **Aplica a:** todas las sesiones con agentes de IA en cualquier Clade
- **Agentes vinculados:** todos los Warriors y agentes genéricos
- **Excepciones:** Ninguna. Lexis no admite excepciones.

## Consecuencias de Violación

1. **Superposición con plan:** si el checkpoint contiene contenido del schema antiguo (Activity, Progress, Artifacts produced), `kata-checkpoint-read` emite warning e ignora el contenido — no hay pérdida de datos real porque la fuente de verdad es el plan.
2. **Pérdida de contexto de sesión:** las sesiones sin checkpoint resultan en pérdida de Open threads y Notes; el plan permanece intacto.
3. **Remediación:** el agente sobrescribe el `.checkpoint` antiguo en la próxima invocación de save con el schema nuevo. El contenido redundante con el plan se descarta.

## Ejemplos

### Correcto

```
Agente: Encontré un `.checkpoint` en el schema nuevo:
  - Session focus: Reposicionando lex-checkpoint en paralelo con revisión de plan-026
  - Active plans: plan-026, plan-040
  - Open threads: 2 ítems pendientes

  ¿Desea retomar este contexto o iniciar una nueva ventana?

Usuario: Retomar.

Agente: Continuando. Plan-040 estaba en redacción de los artefactos pt-BR.
        Open threads pendientes:
          1. Evaluar absorción de "Risks de la sesión" en lex-agent-planning
          2. Decidir clade de los Brand-related cries
        ¿Sigo con plan-040 o trato uno de los hilos primero?
```

### Incorrecto

```
Agente: Encontré un `.checkpoint`:
  ## Activity: Implementación del módulo X
  ## Progress: [x] step 1 [ ] step 2
  ## Artifacts produced: app/foo.py, tests/test_foo.py

# ❌ Schema antiguo. El contenido ya está (o debería estar) en el plan.
# El agente DEBE emitir warning de deprecation, ignorar el contenido,
# y proseguir como si no hubiera checkpoint.
```

```
# Checkpoint que duplica plan — VIOLA LA LEY
# .checkpoint
## Active plans
- plan-040

## Progress
- [x] Reescribir lex-checkpoint
- [ ] Reescribir codex-checkpoint

# ❌ Progress vive en el plan. El checkpoint solo apunta (Active plans).
```

## Validación Automatizada

- **Herramienta:** `kata-checkpoint-read` valida el schema canónico al leer; lint del checkpoint en CI verifica que las secciones obligatorias del schema antiguo estén ausentes (Activity, Progress, Artifacts produced)
- **Momento:** inicio de sesión (read) y save (bajo demanda + fin de sesión con cambio)
- **Métrica:** 0 ocurrencias de secciones del schema antiguo en `.checkpoint` recién escrito; 100% de `.checkpoint` adherentes al schema canónico
