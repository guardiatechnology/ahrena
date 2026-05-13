# Kata: Preparar Pull Request

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Fase 7 del flujo Issue-Driven — creación de branch, push de los archivos y apertura de PR en GitHub vía MCP, con body estructurado referenciando todos los artefactos del flujo

## Objetivo

Tras el Gate 2 resultar en `go`, crear la branch, hacer push de los archivos modificados y abrir un Pull Request en GitHub vía MCP. El body del PR es estructurado referenciando la issue original, los ACs numerados, los ADRs creados y los artefactos del flujo en `.ahrena/issues/{n}/`. El resultado es un PR listo para revisión humana, con trazabilidad completa.

## Cuándo Usar

- Fase 7 (última) del flujo orquestado por `warrior-athena`, tras `kata-quality-gate` resultar en `go`
- Cuando es necesario someter una implementación validada a revisión vía PR

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-----------|
| Número de la issue | Sí | Número de la issue original (ej.: `42`) |
| Repositorio | Sí | `owner/repo` |
| Base branch | No | Branch objetivo del PR; default: `main` |
| Artefactos del flujo | Sí | `.ahrena/issues/{n}/*` y `docs/adr/ADR-*` creados en las fases anteriores |
| Estrategia del PR | No | `draft` (default: `false`) |

## Workflow

```
Progreso:
- [ ] 1. Verificar precondiciones MCP y Gate 2
- [ ] 2. Determinar nombre de la branch y título del PR
- [ ] 3. Crear branch vía GitHub MCP
- [ ] 4. Push de los archivos modificados
- [ ] 5. Componer body del PR con referencias
- [ ] 6. Crear PR linkado a la issue
- [ ] 7. Actualizar status de los ADRs (proposed → accepted)
- [ ] 8. Actualizar checkpoint final
```

### Paso 1: Verificar precondiciones MCP y Gate 2

1. Confirmar que `github` está en `mcp.servers` (conforme a `lex-mcp`). Si no, informar y cerrar.
2. Confirmar `GITHUB_PAT` definida.
3. Leer `.ahrena/issues/{n}/06-quality-report.md` y confirmar resultado `go`. Si `no-go`, rechazar crear PR y retornar al orquestador.
4. Consultar `codex-mcp-github` para identificar herramientas correctas (`create_branch`, `push_files`, `create_pull_request`).

### Paso 2: Determinar nombre de la branch y título del PR

**Nombre de la branch** — convención:

```
{tipo}/issue-{n}-{slug-corto}
```

Donde:
- `{tipo}` — extraer del brief de la Fase 1 (sección "Tipo de trabajo"): `feat`, `fix`, `refactor`, `chore`
- `{slug-corto}` — del título de la issue, convertido a kebab-case, limitado a ~40 chars

**Ejemplo:** `feat/issue-42-add-refund-endpoint`

**Título del PR** — en el formato de Conventional Commits:

```
{tipo}({alcance}): {descripción} (#{n})
```

Donde:
- `{alcance}` — módulo principal afectado (detectado vía componentes de la Fase 3)
- `{descripción}` — resumen corto del cambio

**Ejemplo:** `feat(refunds): add refund creation endpoint (#42)`

### Paso 3: Crear branch vía GitHub MCP

1. Invocar `create_branch` con:
   - `owner`, `repo`
   - `branch` — nombre generado en el Paso 2
   - `from_branch` — base branch (`main` o el configurado)
2. Si la branch ya existe (de iteración anterior), saltar este paso.

### Paso 4: Push de los archivos modificados

1. Ejecutar `git diff --name-only {base}...HEAD` para listar archivos tocados.
2. Para cada archivo, leer el contenido del working tree.
3. Invocar `push_files` con:
   - `owner`, `repo`, `branch` (creada en el Paso 3)
   - `message` — mensaje de commit en el formato Conventional Commits:
     ```
     {tipo}({alcance}): {descripción}

     Refs: #{n}
     ```
   - `files` — array de `{path, content}`
4. Si hay múltiples commits lógicos (recomendado para PRs grandes), invocar `push_files` múltiples veces con mensajes distintos.

### Paso 5: Componer body del PR con referencias

Estructura:

```markdown
## Resumen

{1-2 párrafos describiendo el cambio, extraídos del brief y requirements}

Resolves #{n}

## Criterios de Aceptación

<!-- Copiados de .ahrena/issues/{n}/02-requirements.md -->

- [x] **AC-1:** {descripción}
- [x] **AC-2:** {descripción}
- [x] **AC-3:** {descripción}

## Arquitectura

Ver [documento de arquitectura](.ahrena/issues/{n}/03-architecture.md).

### ADRs creados

- [ADR-{n}: {título}](docs/adr/ADR-{n}-{slug}.md)

(omitir si no hubo ADR)

## Calidad

- ✅ Gate 2 aprobado ([reporte](.ahrena/issues/{n}/06-quality-report.md))
- ✅ Revisión de seguridad aprobada ([reporte](.ahrena/issues/{n}/05-security-review.md))
- Cobertura: {actual}% (threshold: {threshold}%)

## Cómo probar

{Instrucciones extraídas del architecture-brief — cómo correr, variables necesarias, escenarios clave}

## Checklist de revisión

- [ ] ACs atendidos (verificar matriz de trazabilidad en el reporte del Gate 2)
- [ ] ADRs revisados (si es aplicable)
- [ ] Las pruebas se ejecutan localmente
- [ ] Documentación de uso actualizada (si es aplicable)

## Session Trace

<!-- Construido por el Paso 5b a partir de .ahrena/workflow/sessions/*.json
     filtrados por branch == {branch}. Obligatorio cuando session_tracking.enabled
     == true y la branch tiene heartbeat files. Los PRs human-driven pueden usar la frase
     "_(human-driven; no session trace)_". Per lex-pr-quality y codex-session-tracking. -->

| Session | Entrypoint | Role | Started | Last Heartbeat |
|---|---|---|---|---|
| `85846253` | claude-vscode | creator + executor | 2026-05-11T12:30Z | 2026-05-11T14:00Z |

- Plan(s): plan-{NNN}
- Worktree: `.worktrees/{N}-{slug}`
- Cumulative active time: ~Xh Ymin

---

🤖 Generado por el flujo Issue-Driven Development de Ahrena (`warrior-athena`)
```

### Paso 5b: Construir la sección "Session Trace"

Per `lex-pr-quality` (reglas 9, j) y `codex-session-tracking` §7, antes de invocar `create_pull_request` agregar todos los heartbeat files de la branch actual:

1. Verificar `session_tracking.enabled` en `.ahrena/.directives` (default `true`). Si `false`, saltar este paso.
2. Resolver `session_tracking.heartbeat_dir` (default `.ahrena/workflow/sessions/`).
3. Listar `*.json` en el directorio; filtrar por aquellos cuyo `branch` coincide con la branch actual (`git rev-parse --abbrev-ref HEAD`).
4. Ordenar por `started_at` ascendente.
5. Calcular `cumulative_active_time` = suma de `(last_heartbeat - started_at)` por sesión. Formatear como `~Xh Ymin`.
6. Construir tabla con columnas `Session` (UUID corto — primeros 8 chars), `Entrypoint`, `Role`, `Started`, `Last Heartbeat`.
7. Insertar la sección en el body del PR antes del bloque "🤖 Generado...".
8. **PR sin heartbeats asociados** (humano puro, sin agente Claude Code corriendo): sustituir la tabla por la frase canónica `_(human-driven; no session trace)_`.

Esta sección es métrica complementaria al `cry-pr-cost-stamp` (que mide tokens/USD). Aquí mide tiempo de sesión real.

### Paso 5c: Flush del plan

Antes de invocar `create_pull_request`, garantizar que el body de la Issue refleja el estado actual del trabajo:

1. Invocar `kata-flush-plan-to-issue` pasando el número de la Issue.
2. El kata lee `.plans/{N}.md`, filtra bloques `<!-- not-flushed -->`, ejecuta preflight de drift remoto, y graba el contenido filtrado en el body de la Issue vía MCP `update_issue` (preferido) o `gh issue edit --body-file` (fallback).
3. En caso de drift remoto detectado (default `force=false`), el kata pausa y ofrece merge manual — no proseguir hasta resolución.

Ese paso sustituye la mecánica antigua de "actualizar `status:` en el front-matter del plan" (modelo legado pre-): en el Issue-as-plan model, el body de la Issue es el canonical; el caché local `.plans/{N}.md` es regenerable.

### Paso 6: Crear PR linkado a la issue

1. Invocar `create_pull_request` con:
   - `owner`, `repo`
   - `title` — del Paso 2
   - `head` — nombre de la branch
   - `base` — branch objetivo
   - `body` — del Paso 5
   - `draft` — conforme al input (default `false`)
2. Capturar `html_url` del PR creado.
3. Si `Resolves #{n}` está en el body, GitHub linkará automáticamente la issue.

### Paso 6b: Aplicar `status: to review` (transición `development → to review`)

Per `lex-issue-status` Eje A y `lex-agent-planning` Tabla A, al abrir el PR Athena ejecuta la transición `development → to review`:

```bash
# 1. PR — entra en "to review" inmediatamente
gh pr edit {pr_number} --add-label "status: to review"

# 2. Issue — sincronizar (mutex intra-artefacto)
gh issue edit {issue_number} \
  --remove-label "status: development" \
  --add-label "status: to review"
```

Per `lex-issue-status` Regla 3 (mutex intra-artefacto), garantizar que cada artefacto queda con exactamente un `status:*`. Per Regla 5 (sync Issue↔PR), actualizar simultáneamente.

La label es la única fuente de verdad del estado — el body de la Issue (canonical del plan) ya fue actualizado en el Paso 5c.

### Paso 6c: Argos pre-flight cycles (hasta 3, interactivos vía AskUserQuestion)

Antes de cobrar al reviewer humano, Athena ofrece hasta **3 ciclos de review automatizada por Argos**. Cada ciclo es gateado por AskUserQuestion — Athena nunca invoca Argos sin confirmación del usuario. El propósito es elevar la calidad del PR (resolver findings P0/P1) antes de tomar tiempo del reviewer humano.

**Estado inicial:** PR abierto, label `status: to review` aplicada (per Paso 6b).

**Loop Argos (hasta 3 ciclos `A1, A2, A3`):**

Para cada ciclo `A{n}`:

1. Athena pregunta vía `AskUserQuestion`:

   ```
   Athena: "Cycle A{n}/3 — ¿quieres review de Argos en el HEAD actual? (PR #{N}, HEAD {sha_corto})"

     (a) sí, invocar Argos ahora
     (b) no, saltar Argos e ir directo al review humano
     (c) stop — cerrar el flujo entero
   ```

2. Comportamiento por elección:
   - **(a)** Athena transiciona `status: to review → review`, invoca el subagente `warrior-argos` (vía Agent tool con `subagent_type=warrior-argos` o vía `/cry-pr-review` — ver feedback `argos_via_subagent`), aguarda Argos publicar review con marker `argos-review-id:...`, transiciona `status: review → to review`, y prosigue al paso 3.
   - **(b)** Athena registra el rechazo en working notes (bloque `<!-- not-flushed -->` en `.plans/{N}.md`), salta directo al **Paso 6d**.
   - **(c)** Athena registra "Loop cerrado por el usuario en el Argos cycle A{n}" en el body de la Issue vía `kata-flush-plan-to-issue`, NO prosigue al Paso 6d ni al Paso 7. El flujo termina aquí.

3. Athena lee los findings de la review:
   - **P0 BLOCKER** → Athena DEBE address (modificar código) antes de continuar; sin opt-out.
   - **P1 WARNING** → Athena presenta cada finding al usuario vía `AskUserQuestion` ("¿Address ahora o defer a follow-up Issue?"). Address → modifica código; defer → registra TODO en el body de la Issue.
   - **P2 SUGGESTION** → Athena registra como nota informativa en el body de la Issue (sin prompt).

4. Si Athena modificó código en el paso 3, **DEBE** commitear y hacer push antes del próximo ciclo. Cada commit dispara `kata-flush-plan-to-issue` (per Paso 5c — Step concluido cuenta como gatillo de flush). El próximo check de Argos tendrá HEAD nuevo (no idempotente — Argos corre de hecho).

5. Si `n < 3`, volver al paso 1 (próximo ciclo). Si `n == 3`, salir del loop Argos e ir al **Paso 6d**.

**Criterios de salida anticipada del loop Argos:**
- Argos retorna "Argos approves, awaiting human" sin findings P0/P1 actionable → Athena puede ofrecer "¿Quieres otro ciclo Argos o ir directo al review humano?" y salir si el usuario elige saltar.
- Usuario elige (c) stop en cualquier ciclo → flujo termina sin Paso 6d/7.

**Idempotencia:** si HEAD no cambió desde la última review de Argos (mismo commit_id), Athena DEBE alertar al usuario ("HEAD inalterado desde la última review — la nueva review será idempotente; Argos abortará por su propio marker"). Sugerir address de al menos un finding antes de re-invocar Argos.

#### Sub-paso: AI reviewers paralelos a Argos

Tras el usuario elegir (a) en el paso 1 del ciclo A{n}, Athena DEBE evaluar si tiene sentido invocar **AI reviewers paralelos** (GitHub Apps integradas al repo), basado en el contenido del diff:

| Reviewer | Cuándo tiene sentido | Cómo invocar | Detección idempotente |
|---|---|---|---|
| **Gemini** (`gemini-code-assist[bot]`) | PR toca código nuevo de cualquier lenguaje; bueno en sugerencias idiomáticas y seguridad | `gh pr comment {N} --body "/gemini review"` | `gh pr view {N} --json reviews --jq '[.reviews[] | select(.author.login == "gemini-code-assist[bot]") | .commit_id] | last'` |
| **Coderabbit** (`coderabbitai[bot]`) | PR multi-archivo; bueno en consistency checks y best practices | `gh pr comment {N} --body "@coderabbitai review"` | similar (`.author.login == "coderabbitai[bot]"`) |
| **Qodo-Merge** (`qodo-merge-pro[bot]`) | PR backend (Python, Node) — fuerte en test coverage y edge cases | `gh pr comment {N} --body "/review"` | similar |

**Criterio de propuesta:** Athena inspecciona `gh pr view {N} --json files --jq '[.files[].path]'` y decide qué reviewers tienen sentido:

- PR solo-docs (`docs/**`, `README*`, `*.md`) → ningún AI reviewer adicional (Argos basta).
- PR con código de producción (`src/**`, `framework/**` en el caso del propio Ahrena) → proponer 1-2 reviewers según stack.
- PR mixto → proponer el subset que cubre el stack predominante.

**Presentación:** Athena reúne los reviewers candidatos en una única `AskUserQuestion`:

```
Athena: "AI reviewers paralelos a Argos para A{n}/3? (multi-select)

  [ ] Gemini (/gemini review)
  [ ] Coderabbit (@coderabbitai review)
  [ ] Qodo-Merge (/review)
  [ ] ninguno — solo Argos
```

**Comportamiento:**

1. Para cada reviewer marcado, Athena postea el comentario de invocación en secuencia (no en paralelo — reduce ruido en el timeline).
2. Athena **NO bloquea** esperando esos reviewers — son asíncronos (GitHub App webhook); resultados aparecen como reviews/comments en el tiempo de la app (~30s a algunos min).
3. Athena prosigue al paso 2 del ciclo A{n} (transición `to review → review` e invocación del Argos subagente). Argos corre su review en paralelo con los AI reviewers externos.
4. En el paso 3 (Athena lee findings), Athena recolecta findings de **todos los reviewers** con nuevos `submittedAt > HEAD push time` (Argos + Gemini + Coderabbit + Qodo). Trata cada finding vía el mismo schema P0/P1/P2:
   - Argos publica P0/P1/P2 explícitamente con marker.
   - Gemini/Coderabbit/Qodo publican sugerencias libre-formato — Athena clasifica heurísticamente (palabras: "must", "blocker", "critical" → P0; "should", "consider" → P1; "nit", "optional" → P2).
5. Idempotencia: si un AI reviewer ya revisó el HEAD actual (vía commit_id capturado), Athena NO re-invoca ese reviewer en el próximo ciclo hasta que haya nuevos commits.

**Criterio de NO proponer:** si A{n} es ciclo de re-validación tras fix de findings de A{n-1} (HEAD nuevo tras address), y Argos fue confirmado, AI reviewers extras pueden saltarse — la re-validación es primariamente sobre cerrar findings, no levantar nuevos. Athena propone `ninguno` como default en esos casos.

### Paso 6d: Human nudge loop (3 ciclos vía ScheduleWakeup, con notificación Slack por ciclo)

Tras los Argos cycles (Paso 6c), Athena agenda el loop de cobranza al reviewer humano. Diferente del Argos cycle (interactivo), el human nudge loop usa `ScheduleWakeup` para wake-ups periódicos.

**Mecanismo de agendamiento:** Athena pregunta vía `AskUserQuestion`:

```
Athena: "Listo para el human nudge loop (3×15min). ¿Cómo agendar?

  (a) /loop 15m — yo reagendo vía ScheduleWakeup dentro de esta sesión
  (b) cron remoto — la skill `schedule` crea una rutina */15 que verifica y reporta
  (c) manual — sin agendamiento; el humano avisa cuando la review ocurra

¿Qué opción?"
```

**Comportamiento por elección:**

- **(a)** Athena llama `ScheduleWakeup` con `delaySeconds=900` y prompt re-checando `gh pr view {N} --json reviewDecision,mergedAt`. En cada cycle: dispara la notificación Slack (ver "Notificación Slack por ciclo" abajo) + verifica el state.
- **(b)** Athena invoca la skill `schedule` creando una rutina cron `*/15 * * * *` con un agente que ejecuta el check, dispara la notificación Slack, y reporta.
- **(c)** Athena registra "Loop manual" en el body de la Issue. Sin agendamiento; el humano avisa.

**Notificación Slack por ciclo:**

En cada ciclo `H1, H2, H3`, Athena dispara un mensaje vía MCP de notificación configurado en `.ahrena/.directives` (`notifications.provider`) en el canal `notifications.channels.pr_review_timeout`. El contenido escala en urgencia:

| Ciclo | Mensaje default |
|---|---|
| H1 (start) | `PR #{N} listo para review — {title}. {url}` |
| H2 (+15min) | `Reminder #1: PR #{N} esperando review hace ~15min. {url}` |
| H3 (+30min) | `Reminder #2: PR #{N} esperando review hace ~30min — segunda cobranza. {url}` |

Tras H3 sin aprobación → el loop cierra silenciosamente (3 cobranzas fue suficiente).

**Estados detectables durante el loop:**

| `gh pr view` retorna | Acción de Athena |
|---|---|
| `mergedAt != null` | Transición `status: to review → done` en PR + Issue; captura `mergeCommit.oid`; cierra loop. |
| `reviewDecision == "APPROVED"` y `mergedAt == null` | Comenta "PR aprobado, aguardando merge"; cierra loop. |
| `reviewDecision == "CHANGES_REQUESTED"` | → **Paso 6e** (CHANGES_REQUESTED handler). |
| Caso contrario (`REVIEW_REQUIRED` o null) | Si `H < 3` → reagendar; si `H == 3` → cerrar. |

### Paso 6e: CHANGES_REQUESTED handler (reset del loop)

Si durante el Paso 6d el reviewer humano pide cambios (`reviewDecision == "CHANGES_REQUESTED"`):

1. Athena lee los comentarios de review del humano vía `gh pr view {N} --json reviews --jq '.reviews[-1]'`.
2. Athena presenta el resumen de los requests al usuario vía `AskUserQuestion`:
   ```
   Athena: "Reviewer pidió cambios. ¿Address ahora?

     (a) sí, voy a implementar los cambios
     (b) defer — registro como follow-up Issue y mantengo el PR abierto
     (c) stop — cierro el loop y el PR
   ```
3. Comportamiento por elección:
   - **(a)** Athena implementa los cambios (modificar código, commitear, push). Cada commit dispara `kata-flush-plan-to-issue`. El push genera nuevo HEAD SHA.
   - **(b)** Athena registra TODO en el body de la Issue + abre follow-up Issue referenciando el request. Mantiene `status: to review`.
   - **(c)** Athena cierra el PR (`gh pr close 97`), transiciona la Issue para `status: abandoned` con nota explicativa. Flujo termina.

4. Tras (a) o (b), Athena **reagenda el loop a partir del Paso 6c** (Argos pre-flight cycles 3 nuevos en el HEAD nuevo) — porque nuevos commits invalidan la review anterior de Argos. No salta directo al Paso 6d.

5. Si el usuario eligió (b) defer (sin nuevos commits), Athena puede saltar el Paso 6c e ir directo al Paso 6d (since HEAD no cambió).

**Este handler garantiza que CHANGES_REQUESTED resetea el ciclo completo de calidad, no solo el human nudge loop.**

Sin la elección del humano sobre el agendamiento (opciones a/b/c del Paso 6d), Athena **NO DEBE** proseguir al Paso 7 — el loop es responsabilidad declarada en la Tabla A; asumir una opción default sin confirmación sería contrario al principio AI-First (que exige aprobación explícita en acciones con efecto colateral, ver `lex-ai-first-experience`).

### Paso 7: Actualizar status de los ADRs (proposed → accepted)

Para cada ADR creado en la Fase 3 (listados en el checkpoint):

1. Leer `docs/adr/ADR-{n}-{slug}.md`.
2. Alterar `**Status:** proposed` a `**Status:** accepted`.
3. El ADR fue aprobado en el Gate 1 y sobrevivió al Gate 2 — ahora es oficial.
4. Incluir esos archivos modificados en el push (o hacer un commit adicional si ya se hizo push).

### Paso 8: Actualizar checkpoint final

1. Actualizar `.ahrena/workflow/issue-{n}/checkpoint.md`:
   - fase concluida: 7
   - status final: `completed`
   - URL del PR creado
   - branch creada
   - ADRs transicionados a `accepted`
2. Informar al `warrior-athena` (y al humano):
   - PR creado en `{URL}`
   - Próximo paso humano: revisar y aprobar

## Salidas

| Salida | Formato | Destino |
|-------|---------|---------|
| Branch | Git branch | GitHub (vía `create_branch` MCP) |
| Commits | Git commits con mensajes Conventional | GitHub (vía `push_files` MCP) |
| Pull Request | PR con body estructurado | GitHub (vía `create_pull_request` MCP) |
| URL del PR | String | Retorno al orquestador |
| ADRs transicionados | Markdown actualizado | `docs/adr/ADR-*` con `Status: accepted` |
| Checkpoint final | Markdown | `.ahrena/workflow/issue-{n}/checkpoint.md` |

## Restricciones

- **Usar únicamente MCP:** no usar `git push` directo ni `gh pr create` cuando el MCP GitHub está activo (conforme a `lex-mcp`).
- **Sin credenciales hardcoded:** autenticación exclusivamente vía `GITHUB_PAT`.
- **Gate 2 `go` es prerrequisito inviolable:** no abrir PR si `06-quality-report.md` resultó `no-go`.
- **El body del PR debe referenciar .ahrena/issues/{n}/:** la trazabilidad desde la issue hasta el PR exige esos links.
- **Conventional Commits obligatorio:** título del PR y mensajes de commit deben seguir el formato (conforme a `lex-conventional-commits`).

## Referencias

- `lex-issue-driven` — leyes del flujo
- `codex-issue-workflow` — posición de este kata
- `kata-mcp-github-read` — patrón análogo de uso de GitHub MCP
- `codex-mcp-github` — herramientas y parámetros
- `lex-conventional-commits` — formato de commits y título del PR
- `codex-contributing` — flujo de contribución del proyecto
