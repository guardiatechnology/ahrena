# Kata: Cargar Plan desde la Sub-issue

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Materialización del caché local provider-specific (`.claude/plans/plan-{M}-{slug}.md` o `.cursor/plans/plan-{M}-{slug}.md`) a partir del body canónico de la sub-issue Plan, conforme al modelo jerárquico de `lex-agent-planning`

## Objetivo

Sincronizar el body de la sub-issue Plan `{M}` (canonical per `lex-agent-planning`) hacia el caché local provider-specific. Operación idempotente: puede ejecutarse cuantas veces sea necesario y el resultado es determinístico. Se ejecuta al inicio de toda sesión que va a operar sobre un Plan, en cada handoff entre agentes y en un fresh clone del repo.

Este kata materializa caché local a partir de una sub-issue Plan **ya existente** en GitHub. Cuando la sub-issue no existe (plan-archivo orphan con `status: draft` en el front-matter, `issue: TBD`, o escenario plan-first), este kata NO se aplica directamente — el agente DEBE primero accionar la **promoción plan-first** definida en `lex-agent-planning` (crear Issue parent vía `kata-contributing-issue`, crear sub-issue Plan vía `kata-decompose-issue-into-plans` o `kata-plan-task`) y solo después invocar este kata con el número `{M}` de la sub-issue recién creada para materializar el caché.

## Cuándo Usar

- Inicio de sesión de Claude Code o Cursor (cualquier agente: Athena, Argos, Janus, etc.) antes de cualquier edición en `.claude/plans/plan-{M}-{slug}.md` o `.cursor/plans/plan-{M}-{slug}.md`.
- Handoff entre agentes (ej.: Athena entrega a Argos en `to review → review`).
- Fresh clone del repo (el caché local no existe).
- Sospecha de drift entre el caché local y el body de la sub-issue Plan (ej.: otra sesión editó el body vía la UI de GitHub u otro agente flushó en paralelo).

## Inputs

| Entrada | Obligatorio | Descripción |
|---------|:-----------:|-------------|
| `subissue_number` | Sí | Número `{M}` de la sub-issue Plan |
| `owner/repo` | No | Repo donde vive la sub-issue Plan. Default: repo actual del worktree |
| `dest_path` | No | Path del archivo de caché. Default: resuelto por la detección de provider (ver Paso 1) |

## Workflow

```
Progreso:
- [ ] 1. Resolver owner/repo + provider + path de destino
- [ ] 2. Confirmar que la sub-issue Plan existe (guardrail plan-first)
- [ ] 3. Leer el body de la sub-issue vía MCP `get_issue` (preferido)
- [ ] 4. Fallback `gh issue view --json body`
- [ ] 5. Grabar el body en `.claude/plans/plan-{M}-{slug}.md` o `.cursor/plans/plan-{M}-{slug}.md`
- [ ] 6. Validar idempotencia
```

### Paso 1: Resolver owner/repo + provider + path de destino

1. Si `owner/repo` se pasó, usarlo. Si no, derivar del worktree vía `gh repo view --json owner,name`.
2. Detectar el runtime del agente:
   - Claude Code (CLI, VSCode, Desktop, claude.ai/code) → `.claude/plans/`
   - Cursor → `.cursor/plans/`
   - Otro → consultar `.ahrena/.directives` y preguntar al usuario si es ambiguo.
3. Resolver el path de destino:
   - Si `dest_path` se pasó, usarlo.
   - Si no, path final: `<provider-dir>/plan-{M}-{slug}.md`.
4. Asegurar que el directorio de destino existe (`mkdir -p`).

### Paso 2: Confirmar que la sub-issue Plan existe

Este kata supone que la sub-issue Plan `{M}` ya existe en GitHub. Verificar:

```bash
# Preferido — vía MCP
mcp.github.get_issue(owner=owner, repo=repo, issue_number=M)

# Fallback CLI
gh issue view {M} --repo {owner}/{repo} --json number,state,labels
```

Si la sub-issue NO existe (HTTP 404), **no fallar como error fatal**. El escenario es válido (plan-archivo orphan, camino plan-first). El kata DEBE retornar status `PROMOTION_REQUIRED` con mensaje:

> "Sub-issue Plan #{M} no encontrada en {owner}/{repo}, o el plan-archivo carga `status: draft`/`issue: TBD`. Escenario plan-first válido. Accione la promoción per `lex-agent-planning`: `kata-contributing-issue` para crear la Issue parent (si aún no existe), después `kata-decompose-issue-into-plans` o `kata-plan-task` para crear la sub-issue Plan. Después de la promoción, retorne a este kata con el número de la sub-issue para materializar el caché."

El agente invocador DEBE tratar `PROMOTION_REQUIRED` como señal de flujo (accionar promoción plan-first), no como falla fatal.

Si la sub-issue existe, continuar.

### Paso 3: Leer el body de la sub-issue vía MCP `get_issue` (preferido)

Per regla 1 de `lex-mcp`, si el servidor GitHub MCP está listado en `mcp.servers` y activo:

```python
issue = mcp.github.get_issue(owner=owner, repo=repo, issue_number=M)
body = issue["body"]
```

Si tiene éxito, saltar al Paso 5.

### Paso 4: Fallback `gh issue view --json body`

Per regla 4 de `lex-mcp` (MCP no disponible), ejecutar el fallback CLI documentado:

```bash
gh issue view {M} --repo {owner}/{repo} --json body --jq .body > {dest_path}
```

Si `gh` también falla:

1. Retry único después de 5 segundos de backoff.
2. Si persiste, ofrecer al usuario: (a) intentar de nuevo con otro comando, (b) pausar para investigación, (c) abortar.

### Paso 5: Grabar el body en `.claude/plans/plan-{M}-{slug}.md` o `.cursor/plans/plan-{M}-{slug}.md`

1. Si el caché local ya existe y tiene contenido, **preservar bloques `<!-- not-flushed -->` ... `<!-- /not-flushed -->`** existentes:
   - Extraer todos los bloques `<!-- not-flushed -->` del archivo actual.
   - Sustituir el cuerpo principal por el body nuevo de la sub-issue.
   - Apender los bloques `<!-- not-flushed -->` al final.
2. Si el caché local no existe, grabar el body directamente (sin bloques `<!-- not-flushed -->` todavía).

La preservación de bloques locales permite reload sin perder scratch de la IA — reload solo re-sincroniza el contenido canónico.

### Paso 6: Validar idempotencia

Después de grabar, ejecutar una segunda llamada (read-only) y comparar:

```bash
# Comparación canónica (después de filtrar bloques no-flushados en ambos lados)
diff <(strip-not-flushed {dest_path}) <(gh issue view {M} --json body --jq .body)
```

Resultado esperado: ninguna diferencia.

Si hay diferencia fuera de bloques `<!-- not-flushed -->`, el reload falló silenciosamente — abortar e investigar.

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Caché local | Markdown (superset del body de la sub-issue + bloques `<!-- not-flushed -->` preservados) | `.claude/plans/plan-{M}-{slug}.md` o `.cursor/plans/plan-{M}-{slug}.md` |

## Ejemplo de Ejecución

### Input de Ejemplo

```
subissue_number: 201
owner/repo: guardiatechnology/example-repo
dest_path: (default; provider detectado: Claude Code) .claude/plans/plan-201.md
```

### Output de Ejemplo

`.claude/plans/plan-201.md` (justo después del primer load, sin bloques no-flushados todavía):

```markdown
## Summary

Refactorizar el agregado Ledger a event sourcing, separando comandos
(write-side) de lecturas (read-side projection).

Parent: #200

## Plan

### Objective
Entregar la primera porción ejecutable de la User Story #200: Ledger
reescrito como aggregate event-sourced, con factory + repository.

### Steps
- [ ] Step 1 — Modelar LedgerEvent base class
- [ ] Step 2 — Reescribir Ledger.apply() como event projection
- [ ] Step 3 — Repository persistiendo events en lugar de state
- [ ] Step 4 — Migration helper para legacy state → events
- [ ] Step 5 — Tests de aggregate

### Dependencies
None

### Risks
- migration helper puede fallar en datasets con inconsistencia
  histórica — mitigado por dry-run + checksum.

### Open Questions
None
```

Después de algunas ediciones de la IA en el caché local, el archivo carga bloques no-flushados:

```markdown
## Summary
...
(contenido del body — espejado)
...

<!-- not-flushed -->
## Working notes
- 14:32 — comenzó Step 1; LedgerEvent va a heredar de DomainEvent base.

## Next actions
1. Step 2 — apply() recibe LedgerEvent, retorna nuevo state inmutable.
2. Step 3 — repository.save() llama event_store.append().

## Scratch
considerando usar discriminated union en lugar de class hierarchy.
<!-- /not-flushed -->
```

## Restricciones

- **Idempotente:** múltiples ejecuciones producen el mismo caché local para el mismo estado del body de la sub-issue.
- **No flusha:** este kata es one-way (sub-issue → caché). Para grabar de vuelta, usar `kata-flush-plan-to-subissue`.
- **Preserva bloques locales:** los bloques `<!-- not-flushed -->` ... `<!-- /not-flushed -->` existentes en el caché local se preservan; solo el contenido canónico se re-sincroniza.
- **Promoción plan-first:** si la sub-issue Plan `{M}` no existe, el kata retorna `PROMOTION_REQUIRED` (no error fatal) orientando al agente invocador a accionar `kata-contributing-issue` + `kata-decompose-issue-into-plans` (o `kata-plan-task`) antes de retornar.
- **MCP > CLI:** preferir MCP `get_issue` cuando el servidor esté listado y activo; CLI `gh issue view` es fallback documentado per regla 4 de `lex-mcp`.
- **No crea sub-issue:** si la sub-issue `{M}` no existe, el kata falla; la creación es responsabilidad de `kata-plan-task` o `kata-decompose-issue-into-plans`.
- **Provider-specific:** Claude Code → `.claude/plans/`; Cursor → `.cursor/plans/`. No hay caché compartido entre providers.

## Referencias

- `lex-agent-planning` — modelo jerárquico Issue → Plan → PR; cadencia de load/flush; guardrail plan-first
- `lex-mcp` — preferencia MCP + fallback CLI
- `codex-agent-planning` — manual operacional
- `kata-flush-plan-to-subissue` — operación inversa (caché → sub-issue)
- `kata-plan-task` — creación inicial de la sub-issue Plan (precondition de este kata)
- `kata-decompose-issue-into-plans` — descomposición de la Issue parent en N sub-issues Plan
