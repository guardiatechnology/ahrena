# Kata: Flushar Plan a la Sub-issue

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Sincronización del caché local provider-specific (`.claude/plans/plan-{M}-{slug}.md` o `.cursor/plans/plan-{M}-{slug}.md`) al body canónico de la sub-issue Plan, conforme al modelo jerárquico de `lex-agent-planning`

## Objetivo

Persistir el contenido del caché local provider-specific (working memory de la IA) en el body de la sub-issue Plan `{M}` de GitHub (canonical), filtrando bloques locales marcados `<!-- not-flushed -->` ... `<!-- /not-flushed -->`. Operación idempotente. Disparada en los 4 disparadores canónicos de `lex-agent-planning`: cada transición de label `status:` en la sub-issue/PR, cada Step completado (`[ ]` → `[x]`), fin de sesión (heartbeat finaliza o el owner sale), y handoff entre agentes.

## Cuándo Usar

- Transición de label `status:` en la sub-issue Plan o en el PR vinculado (`todo → development`, `development → to review`, `to review → review`, etc.).
- Step del plan marcado como completado (`[ ]` → `[x]`) en el caché local.
- Fin de sesión de Claude Code o Cursor (heartbeat finaliza o el agente Athena/Argos/Janus sale).
- Handoff entre agentes (entregar antes de que entre el siguiente agente).
- Solicitud explícita del usuario ("flushea el plan", "actualiza la sub-issue").

## Inputs

| Entrada | Obligatorio | Descripción |
|---------|:-----------:|-------------|
| `subissue_number` | Sí | Número `{M}` de la sub-issue Plan |
| `owner/repo` | No | Repo donde vive la sub-issue Plan. Default: repo actual del worktree |
| `source_path` | No | Path del archivo de caché local. Default: resuelto por la detección de provider (`.claude/plans/plan-{M}-{slug}.md` o `.cursor/plans/plan-{M}-{slug}.md`) |
| `force` | No | `true` fuerza la grabación incluso si hubo edición remota desconocida. Default: `false` (alerta + ofrece merge manual) |

## Workflow

```
Progreso:
- [ ] 1. Resolver provider + path de origen
- [ ] 2. Leer el caché local
- [ ] 3. Filtrar bloques `<!-- not-flushed -->`
- [ ] 4. Detectar drift remoto (preflight)
- [ ] 5. Grabar vía MCP `update_issue` (preferido)
- [ ] 6. Fallback `gh issue edit --body-file`
- [ ] 7. Validar idempotencia
```

### Paso 1: Resolver provider + path de origen

1. Si `source_path` se pasó, usarlo.
2. Si no, detectar el runtime del agente:
   - Claude Code → `.claude/plans/plan-{M}-{slug}.md`
   - Cursor → `.cursor/plans/plan-{M}-{slug}.md`
3. Si el archivo no existe o está vacío, abortar con mensaje orientando a ejecutar `kata-load-plan-from-subissue` primero.

### Paso 2: Leer el caché local

```bash
cat {source_path}
```

Validar que el contenido carga el schema canónico mínimo (Summary, Plan section). Si falta estructura, abortar y orientar a sincronizar primero vía `kata-load-plan-from-subissue`.

### Paso 3: Filtrar bloques `<!-- not-flushed -->`

Remover del contenido todos los bloques delimitados:

```
<!-- not-flushed -->
...cualquier contenido...
<!-- /not-flushed -->
```

El resultado es el **body candidato** para grabar en la sub-issue. Implementación canónica vía Python:

```python
import re
filtered = re.sub(
    r"<!-- not-flushed -->.*?<!-- /not-flushed -->",
    "",
    raw_content,
    flags=re.DOTALL,
)
# colapsa solo líneas en blanco triples+ a dobles; preserva indentación
filtered = re.sub(r"\n\n\n+", "\n\n", filtered).strip() + "\n"
```

El filtrado es silencioso por diseño — el body candidato no se filtra en el log de sesión.

### Paso 4: Detectar drift remoto (preflight)

Antes de grabar, **leer el body actual** de la sub-issue y comparar con el último estado conocido localmente:

1. `gh issue view {M} --repo {owner}/{repo} --json body --jq .body` → `remote_body_now`.
2. Comparar `remote_body_now` con `remote_body_at_last_load` (estado guardado localmente en `.claude/plans/.{M}.remote.last` o similar — opcional; si está ausente, leer en el momento).
3. Si es diferente, hubo **edición remota desconocida** (otra sesión flushó en paralelo o edición vía la UI de GitHub).

Comportamiento en la detección de drift:

| Escenario | Default (`force=false`) | Con `force=true` |
|---|---|---|
| Sin drift | Graba directo | Graba directo |
| Con drift | **Alerta** (no graba); ofrece: (a) mostrar diff y abortar, (b) merge manual, (c) overwrite | Graba directo (sobrescribe cambios remotos) |

El default `force=false` es más conservador — protege contra la pérdida de ediciones simultáneas.

### Paso 5: Grabar vía MCP `update_issue` (preferido)

Per regla 1 de `lex-mcp`, si el servidor GitHub MCP está listado en `mcp.servers` y activo:

```python
mcp.github.update_issue(
    owner=owner,
    repo=repo,
    issue_number=M,
    body=filtered_body,
)
```

Si tiene éxito, actualizar `.claude/plans/.{M}.remote.last` (o el equivalente en Cursor) con el body recién grabado, y saltar al Paso 7.

### Paso 6: Fallback `gh issue edit --body-file`

Per regla 4 de `lex-mcp` (MCP no disponible):

```bash
# Grabar body candidato en archivo temporal
echo "$filtered_body" > /tmp/subissue-{M}-body.md

# Grabar en la sub-issue vía gh
gh issue edit {M} --repo {owner}/{repo} --body-file /tmp/subissue-{M}-body.md

# Limpiar
rm /tmp/subissue-{M}-body.md
```

Si `gh` falla:

1. Retry único después de 5 segundos de backoff.
2. Si persiste, ofrecer al usuario (per regla 4 pasos 3-4 de `lex-mcp`): (a) intentar de nuevo, (b) pausar, (c) abortar.

### Paso 7: Validar idempotencia

Después de grabar, ejecutar `gh issue view {M} --json body --jq .body` y comparar con `filtered_body`. Resultado esperado: igual.

Si hay diferencia, el flush falló silenciosamente — abortar e investigar (normalmente: encoding, escape de caracteres especiales, o rate-limit silenciado por GitHub).

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Body actualizado | Markdown (sin bloques `<!-- not-flushed -->`) | Sub-issue `{M}` en GitHub |
| `.claude/plans/.{M}.remote.last` (opcional) | Markdown | Caché local del último estado remoto conocido (preflight del próximo flush) |

## Ejemplo de Ejecución

### Input de Ejemplo

```
subissue_number: 201
owner/repo: guardiatechnology/example-repo
source_path: (default; provider Claude Code) .claude/plans/plan-201.md
force: false
```

### `.claude/plans/plan-201.md` antes del flush

```markdown
## Summary

Refactorizar el agregado Ledger a event sourcing, separando comandos
(write-side) de lecturas (read-side projection).

Parent: #200

## Plan
### Steps
- [x] Step 1 — Modelar LedgerEvent base class
- [x] Step 2 — Reescribir Ledger.apply() como event projection (just completed)
- [ ] Step 3 — Repository persistiendo events en lugar de state
...

<!-- not-flushed -->
## Working notes
- 15:10 — terminó Step 2; el caché aquí está más nuevo que el body de la sub-issue.

## Scratch
discriminated union vs class hierarchy: quedó class hierarchy más legible.
<!-- /not-flushed -->
```

### Body grabado en la sub-issue después del flush

```markdown
## Summary

Refactorizar el agregado Ledger a event sourcing, separando comandos
(write-side) de lecturas (read-side projection).

Parent: #200

## Plan
### Steps
- [x] Step 1 — Modelar LedgerEvent base class
- [x] Step 2 — Reescribir Ledger.apply() como event projection (just completed)
- [ ] Step 3 — Repository persistiendo events en lugar de state
...
```

Los bloques `<!-- not-flushed -->` quedan solo en el caché local. Cuando otra sesión ejecute `kata-load-plan-from-subissue`, recibe el body sin los bloques — se preserva la propiedad de que canonical = body de la sub-issue.

## Restricciones

- **Idempotente:** múltiples ejecuciones producen el mismo body si el caché local no cambió.
- **Preflight obligatorio (default):** sin `force=true`, el drift remoto bloquea el flush y exige decisión humana.
- **MCP > CLI:** preferir MCP `update_issue`; CLI `gh issue edit --body-file` es fallback per regla 4 de `lex-mcp`.
- **No crea sub-issue:** si `{M}` no existe, falla inmediato. Para crear, usar `kata-plan-task` o `kata-decompose-issue-into-plans`.
- **No toca labels ni assignees:** el flush opera solo en el body. Las labels (incluyendo `status:*`) son responsabilidad del owner de la transición (per `lex-agent-planning` y `lex-issue-status`).
- **No loguea contenido filtrado:** el body candidato no aparece en los logs de sesión.
- **Preserva indentación:** la regex de colapso de líneas en blanco actúa solo sobre secuencias `\n\n\n+`; nunca sobre espacios horizontales (que destruirían la indentación Markdown de listas y code blocks).

## Referencias

- `lex-agent-planning` — modelo jerárquico Issue → Plan → PR; cadencia de flush (4 disparadores canónicos)
- `lex-mcp` — preferencia MCP + fallback CLI
- `lex-issue-status` — labels canónicas; flush se dispara en cada transición
- `codex-agent-planning` — manual operacional
- `kata-load-plan-from-subissue` — operación inversa (sub-issue → caché)
- `kata-plan-task` — creación de la sub-issue Plan (precondition)
- `kata-decompose-issue-into-plans` — descomposición de la Issue parent en N sub-issues Plan
- `kata-pr-prepare` — invoca este kata antes de abrir el PR
- `warrior-athena`, `warrior-argos`, `warrior-janus` — agentes que disparan flush en transiciones
