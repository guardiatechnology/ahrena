# Kata: Flushar Plan a la Issue

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Sincronización del caché local `.plans/{N}.md` al body canónico de la Issue de GitHub, conforme al modelo de almacenamiento en 3 capas del ADR-002

## Objetivo

Persistir el contenido de `.plans/{N}.md` (working memory de la IA) en el body de la Issue de GitHub (canonical), filtrando bloques locales marcados `<!-- not-flushed -->` ... `<!-- /not-flushed -->`. Operación idempotente. Disparada en los 3 disparadores canónicos de `lex-agent-planning`: cada transición de label `status:`, cada Step concluido, y fin de sesión.

## Cuándo Usar

- Transición de label `status:` en la Issue/PR (`todo → development`, `development → to review`, etc.).
- Step del plan marcado como concluido (`[ ]` → `[x]`).
- Fin de sesión Claude Code (heartbeat finaliza o agente Athena/Argos/Janus sale).
- Handoff entre agentes (entrega antes de que entre el siguiente agente).
- Solicitud explícita del usuario ("flush plan", "actualiza la Issue").

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-----------|
| `issue_number` | Sí | Número de la Issue (`{N}` en `{owner}/{repo}#{N}`) |
| `owner/repo` | No | Repo donde vive la Issue. Default: repo actual del worktree |
| `source_path` | No | Path del archivo de caché local. Default: `<paths.plans>/{N}.md` |
| `force` | No | `true` fuerza la grabación incluso si hubo edición remota desconocida. Default: `false` (alerta + ofrece merge manual) |

## Workflow

```
Progreso:
- [ ] 1. Leer `.plans/{N}.md`
- [ ] 2. Filtrar bloques `<!-- not-flushed -->`
- [ ] 3. Detectar drift remoto (preflight)
- [ ] 4. Grabar vía MCP `update_issue` (preferido)
- [ ] 5. Fallback `gh issue edit --body-file`
- [ ] 6. Validar idempotencia
```

### Paso 1: Leer `.plans/{N}.md`

Cargar el contenido del caché local:

```bash
cat .plans/{N}.md
```

Si el archivo no existe o está vacío, abortar con mensaje orientando a correr `kata-load-plan-from-issue` primero.

### Paso 2: Filtrar bloques `<!-- not-flushed -->`

Eliminar del contenido todos los bloques delimitados:

```
<!-- not-flushed -->
...cualquier contenido...
<!-- /not-flushed -->
```

El resultado es el **body candidato** para grabar en la Issue. Implementación canónica vía Python:

```python
import re
filtered = re.sub(
    r"<!-- not-flushed -->.*?<!-- /not-flushed -->",
    "",
    raw_content,
    flags=re.DOTALL,
)
# elimina líneas vacías duplicadas que sobraron post-filtro
filtered = re.sub(r"\n{3,}", "\n\n", filtered).strip() + "\n"
```

### Paso 3: Detectar drift remoto (preflight)

Antes de grabar, **leer el body actual** de la Issue y comparar con el último estado conocido localmente:

1. `gh issue view {N} --json body --jq .body` → `remote_body_now`.
2. Comparar `remote_body_now` con `remote_body_at_last_load` (estado guardado localmente en `.plans/.{N}.remote.last` o similar — opcional; si está ausente, leer al momento).
3. Si es diferente, hubo **edición remota desconocida** (otra sesión o edición vía UI de GitHub).

Comportamiento en la detección de drift:

| Escenario | Default | Con `force=true` |
|---|---|---|
| Sin drift | Graba directamente | Graba directamente |
| Con drift | **Alerta** (no graba); ofrece: (a) mostrar diff y abortar, (b) merge manual, (c) overwrite | Graba directamente (sobrescribe los cambios remotos) |

El default `force=false` es más conservador — protege contra la pérdida de ediciones simultáneas.

### Paso 4: Grabar vía MCP `update_issue` (preferido)

Per `lex-mcp` regla 1, si el servidor GitHub MCP está listado en `mcp.servers` y activo:

```python
mcp.github.update_issue(
    owner=owner,
    repo=repo,
    issue_number=N,
    body=filtered_body,
)
```

Si tiene éxito, actualizar `.plans/.{N}.remote.last` con el body recién grabado, y saltar al Paso 6.

### Paso 5: Fallback `gh issue edit --body-file`

Per `lex-mcp` regla 4 (MCP indisponible):

```bash
# Grabar body candidato en archivo temporal
echo "$filtered_body" > /tmp/issue-{N}-body.md

# Grabar en la Issue vía gh
gh issue edit {N} --repo {owner}/{repo} --body-file /tmp/issue-{N}-body.md

# Limpiar
rm /tmp/issue-{N}-body.md
```

Si `gh` falla:

1. Retry único tras 5 segundos de backoff.
2. Si persiste, ofrecer al usuario (per `lex-mcp` regla 4 pasos 3-4): (a) intentar de nuevo, (b) pausar, (c) abortar.

### Paso 6: Validar idempotencia

Tras grabar, ejecutar `gh issue view {N} --json body --jq .body` y comparar con `filtered_body`. Resultado esperado: igual.

Si hay diferencia, el flush falló silenciosamente — abortar e investigar (normalmente: encoding, escaping de caracteres especiales, o rate-limit silenciado por GitHub).

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Body actualizado | Markdown (sin bloques `<!-- not-flushed -->`) | Issue `{N}` en GitHub |
| `.plans/.{N}.remote.last` (opcional) | Markdown | Caché local del último estado remoto conocido (preflight del siguiente flush) |

## Ejemplo de Ejecución

### Input de Ejemplo

```
issue_number: 96
owner/repo: guardiatechnology/ahrena
source_path: (default) .plans/96.md
force: false
```

### `.plans/96.md` antes del flush

```markdown
## Summary
...

## Plan
### Steps
- [x] Step 1
- [x] Step 2
- [x] Step 3 — Rewrite lex-agent-planning (Just completed)
- [ ] Step 4
...

<!-- not-flushed -->
## Working notes
- 23:55 — terminó Step 3; el caché aquí está más nuevo que el body de la Issue.

## Scratch
probando si update_issue MCP soporta body de >50KB. Sí, soporta (límite ~65KB).
<!-- /not-flushed -->
```

### Body grabado en la Issue tras el flush

```markdown
## Summary
...

## Plan
### Steps
- [x] Step 1
- [x] Step 2
- [x] Step 3 — Rewrite lex-agent-planning (Just completed)
- [ ] Step 4
...
```

Los bloques `<!-- not-flushed -->` quedan solo en el caché local. Cuando otra sesión corra `kata-load-plan-from-issue`, recibe el body sin los bloques — se preserva la propiedad de que canonical = body de la Issue.

## Restricciones

- **Idempotente:** múltiples ejecuciones producen el mismo body si el `.plans/{N}.md` no cambió.
- **Preflight obligatorio (default):** sin `force=true`, drift remoto bloquea el flush y exige decisión humana.
- **MCP > CLI:** preferir MCP `update_issue`; CLI `gh issue edit --body-file` es fallback per `lex-mcp` regla 4.
- **No crea Issue:** si `{N}` no existe, falla inmediato. Para crear, usar `kata-plan-task`.
- **No toca labels ni assignees:** el flush opera solo sobre el body. Las labels (incluyendo `status:*`) son responsabilidad del owner de la transición (per `lex-agent-planning` y `lex-issue-status`).
- **No logea contenido:** el filtrado `<!-- not-flushed -->` es silencioso por diseño — el body candidato no se filtra en log de sesión.

## Referencias

- `lex-agent-planning` — modelo de 3 capas y cadencia de flush (3 disparadores canónicos)
- `lex-mcp` — preferencia MCP + fallback CLI
- `lex-issue-status` — labels canónicos; el flush es disparado en cada transición
- `codex-agent-planning` — manual operacional
- ADR-002 — decisión de arquitectura
- `kata-load-plan-from-issue` — operación inversa (Issue → caché)
- `kata-pr-prepare` — invoca `kata-flush-plan-to-issue` antes de abrir el PR
- `warrior-athena`, `warrior-argos`, `warrior-janus` — agentes que disparan flush en las transiciones
