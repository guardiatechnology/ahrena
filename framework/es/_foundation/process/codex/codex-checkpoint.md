# Codex: Checkpoint de Sesión

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Uso operacional del `.checkpoint` complementario a `lex-checkpoint` y `lex-agent-planning`

## Visión General

`.checkpoint` es un archivo de **scratchpad de sesión** ubicado en la raíz del workspace, gitignored, que captura el contexto de ventana de trabajo que NO cabe en un único plan. Este Codex documenta cómo el `.checkpoint` se relaciona con `lex-agent-planning`, cuándo conviene invocarlo y cómo depurar inconsistencias.

La Ley correspondiente es `lex-checkpoint`. Los procedimientos operacionales son `kata-checkpoint-read` (inicio de sesión) y `kata-checkpoint-save` (bajo demanda + fin de sesión). El atajo de usuario es `cry-checkpoint`.

## Contexto

- **Dominio:** continuidad de contexto entre sesiones con agentes de IA
- **Público objetivo:** Warriors, Katas, agentes genéricos y usuarios humanos que invocan `cry-checkpoint`
- **Actualización:** cuando `lex-checkpoint` cambia, o cuando el ecosistema de Katas/Cries en torno a él evoluciona

## Contenido

### Principios

1. **Sesión, no task.** Plan (`lex-agent-planning`) es la fuente de verdad de la task — committed, con Steps, Decisiones, Riesgos. Checkpoint cubre lo que no cabe en un único plan: foco de la ventana, hand-off entre múltiples planes activos, hilos paralelos, scratchpad libre.
2. **Schema reducido y canónico.** 4 secciones fijas (Session focus, Active plans, Open threads, Notes). Nada más — los campos que duplicarían el plan (Activity, Progress, Decisions made, Next steps, Artifacts produced) están prohibidos.
3. **Disparadores discretos.** Read al inicio de sesión; save bajo demanda del usuario o al cerrar sesión con cambio de contexto. Sin auto-save por activity.
4. **Degradación grácil.** `.checkpoint` ausente es un escenario válido. El schema antiguo genera warning de deprecation, no error. Sobrescritura silenciosa en el próximo save.

### Cuándo conviene invocarlo

| Escenario | Acción |
|-----------|--------|
| Inicio de conversación nueva con agente que tiene `.checkpoint` guardado | `kata-checkpoint-read` (automático en el boot) |
| Conversación exploratoria sin plan formal, con decisiones transversales | `cry-checkpoint` al final para preservar Open threads y Notes |
| Múltiples planes activos en paralelo en la sesión | `cry-checkpoint` para registrar Active plans con 1-line context |
| Pausa larga antes de retomar mañana | `cry-checkpoint` antes de cerrar |
| Task simple encapsulada en un único plan, sin hilos paralelos | NO invocar — el plan ya cubre todo |
| Cambio de plan (cerré plan-N, comenzando plan-M) | Actualizar Active plans vía `cry-checkpoint` |

### Cuándo NO usar

- **Para registrar progreso de task formal** — va en el plan (`lex-agent-planning`)
- **Para listar artefactos producidos** — `git diff` + plan cubren
- **Para versionar decisiones arquitectónicas** — ADR (`docs/adr/ADR-NNN-*.md`)
- **Para tracking de bug activo** — Issue de GitHub
- **Para handoff entre desarrolladores** — no funciona; `.checkpoint` es gitignored y per-machine

### Patrones y Convenciones

| Aspecto | Patrón | Ejemplo |
|---------|--------|---------|
| Nombre del archivo | `.checkpoint` (con punto, sin extensión) | `.checkpoint` |
| Ubicación | raíz del workspace | `/path/to/repo/.checkpoint` |
| Encoding | UTF-8, line endings LF | — |
| Schema | 4 secciones obligatorias + frontmatter de 2 campos | Ver `lex-checkpoint` regla 3 |
| Active plans entries | `\`plan-NNN\` — slug; 1 línea de contexto ≤ 80 chars` | `` `plan-040` — reposicionamiento; en redacción `` |
| Open threads entries | 1-2 líneas en bullet | `- Evaluar absorción de Risks de la sesión` |
| Notes | texto libre, sin schema | cualquier markdown |
| Tamaño típico | < 4 KB | — |

### Decisiones Vigentes

| Decisión | Estado | Origen |
|----------|--------|--------|
| Schema reducido (4 secciones) sustituye al schema antiguo (8 campos) | Activa | plan-040, issue #73 |
| Save bajo demanda + fin de sesión (no automático por activity) | Activa | plan-040 |
| Sin tool de migración dedicada — read detecta schema antiguo, emite warning, save sobrescribe | Activa | plan-040 |
| `Active plans` es hint opcional para otros agentes (ej.: plan-026 observer); no fuente de scope | Activa | plan-040 |

### Restricciones Técnicas

- `.checkpoint` es **per-machine, per-developer** — no se sincroniza entre máquinas, no se commitea
- La escritura es **last-write-wins** — múltiples agentes simultáneos compiten por el archivo (escenario raro)
- Read en schema antiguo es **lectura silenciosa** — no intenta parsear ni migrar; solo emite warning y prosigue
- El tamaño no tiene límite hard, pero > 8 KB indica que contenido del plan se filtró — auditar

## Troubleshooting

### `.checkpoint` ausente tras varias sesiones

- **Causa probable:** el usuario nunca invocó `cry-checkpoint` y ninguna sesión tuvo cambio de contexto fuera del plan.
- **Acción:** comportamiento esperado. Si hay contexto a preservar, invocar `cry-checkpoint`.

### `kata-checkpoint-read` emite warning de schema antiguo

- **Causa:** `.checkpoint` fue escrito antes de la reescritura (issue #73).
- **Acción:** `rm .checkpoint` o esperar la próxima invocación de save (sobrescribe con schema nuevo).

### Contenido del plan apareció en Notes del checkpoint

- **Causa:** el agente confundió alcances.
- **Acción:** mover el contenido a `## Steps` o `## Decisiones cerradas` del plan correspondiente; eliminarlo de Notes.

### `Active plans` crece indefinidamente

- **Causa:** los planes done no fueron eliminados de la lista.
- **Acción:** al cerrar plan (status `done`), actualizar `Active plans` eliminando la entrada vía `cry-checkpoint`.

### Checkpoint inconsistente entre sesiones paralelas (mismo workspace)

- **Causa:** múltiples agentes Claude Code/Cursor escribiendo simultáneamente.
- **Acción:** `.checkpoint` es per-workspace; las sesiones paralelas activas en el mismo workspace son raras. Si ocurre, last-write-wins resuelve — el usuario invoca `cry-checkpoint` en la sesión que tiene el estado correcto para sobrescribir.

## Glosario

| Término | Definición |
|---------|------------|
| Session focus | 1-3 frases describiendo el foco de la ventana de trabajo actual |
| Active plans | Lista de plan-IDs activos en la sesión con 1-line context cada uno |
| Open threads | Hilos de conversación que no se convirtieron en plan formal pero deben retomarse |
| Notes | Scratchpad libre — texto, enlaces, recordatorios |
| Schema antiguo | Estructura pre-issue-#73 con Activity/Status/Progress/Decisions/Next steps/Artifacts produced |
| Schema nuevo | Estructura canónica de 4 secciones (Session focus, Active plans, Open threads, Notes) |

## Referencias

- `lex-checkpoint` — Ley que define el schema y los disparadores
- `lex-agent-planning` — Ley del plan (fuente de verdad de la task)
- `kata-checkpoint-read` — procedimiento de lectura al iniciar sesión
- `kata-checkpoint-save` — procedimiento de guardado bajo demanda + fin de sesión
- `cry-checkpoint` — atajo de usuario para `kata-checkpoint-save`
- Issue #73 — reposicionamiento del `.checkpoint`
- Plan-040 — ejecución del reposicionamiento
