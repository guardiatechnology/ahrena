# Kata: Guardar Checkpoint de Sesión

> **Prefijo:** `kata-` | **Tipo:** Habilidad Repetible | **Alcance:** Guardado bajo demanda + fin de sesión, conforme a `lex-checkpoint`

## Objetivo

Recolectar Session focus, Active plans, Open threads y Notes del contexto actual de la sesión y escribir `.checkpoint` en la raíz del workspace, respetando el schema canónico (4 secciones). Sobrescribe cualquier schema antiguo silenciosamente.

## Cuándo Usar

- Cuando el usuario invoca `cry-checkpoint` (disparador explícito)
- Al cerrar la sesión SI hubo cambio de contexto (nuevo Session focus, nuevo Active plan, nuevo Open thread, nuevas Notes)
- Cuando el agente detecta que está a punto de cerrar la ventana y hay contexto no persistido

NO usar:
- Después de cada activity automática (la granularidad vive en el plan)
- Para registrar contenido ya presente en el plan (duplicaría `lex-agent-planning`)
- En sesiones puramente operativas sin hilos paralelos (no hay contexto a preservar fuera del plan)

## Entradas

| Entrada | Obligatorio | Descripción |
|---------|:-----------:|-------------|
| Session focus | Sí | 1-3 frases describiendo el foco general de la ventana de trabajo |
| Active plans | No | Lista de `(plan-id, 1-line context)` de los planes activos en la sesión; puede estar vacía |
| Open threads | No | Lista de hilos paralelos pendientes; puede estar vacía |
| Notes | No | Texto libre — enlaces, recordatorios, snippets; puede estar vacío |
| Workspace root | Sí | Directorio donde escribir `.checkpoint` (default: `pwd`) |

Al menos uno entre Session focus, Active plans, Open threads o Notes debe tener contenido. Un checkpoint vacío no se escribe — `kata-checkpoint-save` retorna `nothing-to-save`.

## Flujo de Trabajo

```
Progreso:
- [ ] 1. Recolectar contexto de la sesión
- [ ] 2. Validar contenido (no duplicar plan)
- [ ] 3. Renderizar schema canónico
- [ ] 4. Escribir .checkpoint
- [ ] 5. Confirmar al usuario
```

### Paso 1: Recolectar contexto de la sesión

1. Capturar **Session focus** del contexto activo o pedirlo al usuario en 1-3 frases.
2. Listar **Active plans** — para cada plan en uso en la sesión, generar entrada `\`plan-NNN\` — slug; 1-line context ≤ 80 chars`. Inferir del contexto o consultar `.claude/plans/plan-*.md` activos (status `in-progress`).
3. Recolectar **Open threads** — preguntar al usuario o extraer del historial reciente de la conversación las decisiones pendientes que no se convirtieron en plan.
4. Recolectar **Notes** — texto libre adicional. Puede estar vacío.

### Paso 2: Validar contenido (no duplicar plan)

Antes de escribir, verificar:

- **Session focus** NO contiene `## Steps`, `## Decisiones cerradas`, `## Riesgos` (esos viven en el plan)
- **Active plans** entries tienen formato canónico (\`plan-NNN\` — descripción) y ≤ 80 chars
- **Open threads** NO contiene steps detallados de una task (si los contiene, mover al plan correspondiente antes de escribir)
- **Notes** NO contiene artifacts produced (lista de archivos modificados — `git diff` cubre)

Si la validación detecta duplicación, presentar al usuario y ofrecer:
- Mover el contenido duplicado al plan apropiado antes de escribir
- Ignorar y escribir como está (con warning explícito)

### Paso 3: Renderizar schema canónico

Componer el contenido del archivo:

```markdown
# Session checkpoint

- **Last update:** {YYYY-MM-DDTHH:MM:SSZ — UTC ISO 8601}
- **Session id:** {session_id o commit short SHA del HEAD}

## Session focus

{contenido recolectado en el Paso 1}

## Active plans

{lista; si está vacía, omitir bullets y dejar la sección con texto "Ningún plan activo registrado."}

## Open threads

{lista; si está vacía, omitir bullets y dejar la sección con texto "Ningún hilo abierto."}

## Notes

{texto libre; si está vacío, omitir y dejar la sección con texto "—"}
```

Las secciones vacías se preservan (encabezado mantenido) con placeholder textual — el schema es canónico, no opcional.

### Paso 4: Escribir `.checkpoint`

1. Path final: `{workspace_root}/.checkpoint`
2. Escritura atómica: escribir en `.checkpoint.tmp` y `mv` a `.checkpoint` (evita corromper en caso de interrupción)
3. Encoding UTF-8, line endings LF
4. Sobrescritura silenciosa de cualquier schema antiguo presente
5. Validar que `.gitignore` contenga `.checkpoint` (según `lex-checkpoint` regla 4); si no, alertar al usuario (pero escribir igualmente)

### Paso 5: Confirmar al usuario

```
✅ Checkpoint guardado en `.checkpoint`:
   - Session focus: {primera frase, max 100 chars}
   - Active plans: {N}
   - Open threads: {N}
   - Notes: {presente | vacío}
```

### Paso 6: Validación Final

- [ ] `.checkpoint` existe en la raíz del workspace
- [ ] La primera línea es `# Session checkpoint` (no `# Checkpoint`)
- [ ] Las 4 secciones (Session focus, Active plans, Open threads, Notes) están presentes
- [ ] No hay secciones prohibidas (Activity, Status, Progress, Decisions made, Next steps, Artifacts produced)
- [ ] `.gitignore` cubre `.checkpoint`
- [ ] La confirmación fue mostrada al usuario

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| `.checkpoint` | Markdown UTF-8 con schema canónico | Raíz del workspace |
| Estado (`saved`, `nothing-to-save`, `validation-warning`, `gitignore-missing`) | Enum interno | Contexto de la sesión |
| Confirmación al usuario | Texto markdown | Terminal/IDE |

## Ejemplo de Ejecución

### Entrada

```
Session focus: "Reposicionando lex-checkpoint en paralelo con revisión de plan-026."
Active plans:
  - plan-026 (commit-readiness-observer; aguardando ajuste)
  - plan-040 (reposicionamiento del .checkpoint; en redacción)
Open threads:
  - Evaluar absorción de "Risks de la sesión" en lex-agent-planning
  - Decidir clade de los Brand-related cries
Notes: "Enlace discusión kata-quality-gate: https://..."
Workspace: /Users/dev/workspace/guardia/tooling/ahrena
```

### Salida (`.checkpoint`)

```markdown
# Session checkpoint

- **Last update:** 2026-05-10T01:55:00Z
- **Session id:** abc1234

## Session focus

Reposicionando lex-checkpoint en paralelo con revisión de plan-026.

## Active plans

- `plan-026` — commit-readiness-observer; aguardando ajuste
- `plan-040` — reposicionamiento del `.checkpoint`; en redacción

## Open threads

- Evaluar absorción de "Risks de la sesión" en lex-agent-planning
- Decidir clade de los Brand-related cries

## Notes

Enlace discusión kata-quality-gate: https://...
```

### Confirmación

```
✅ Checkpoint guardado en `.checkpoint`:
   - Session focus: Reposicionando lex-checkpoint en paralelo con revisión de plan-026.
   - Active plans: 2
   - Open threads: 2
   - Notes: presente
```

## Restricciones

- NO escribe contenido que duplica el plan (Activity, Steps, Artifacts produced)
- NO trata el schema antiguo — sobrescribe silenciosamente
- NO emite save vacío — un checkpoint sin contenido retorna `nothing-to-save`
- NO escribe si el workspace es read-only o si los permisos lo impiden (alerta al usuario)
- La escritura es atómica (tmp + mv) — la interrupción mid-save no corrompe
- NO commitea `.checkpoint` — queda gitignored según `lex-checkpoint` regla 4
