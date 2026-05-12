# Kata: Cargar Plan desde la Issue

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Materialización del caché local `.plans/{N}.md` a partir del body canónico de la Issue de GitHub, conforme al modelo de almacenamiento en 3 capas del ADR-002

## Objetivo

Sincronizar el contenido del body de una Issue (canonical per `lex-agent-planning`) al caché local `.plans/{N}.md` de la IA. Operación idempotente: puede correr cuantas veces sea necesario y el resultado es determinístico. Corre al inicio de toda sesión que vaya a operar sobre un plan y en cada handoff entre agentes.

## Cuándo Usar

- Inicio de sesión Claude Code (cualquier agente: Athena, Argos, Janus, etc.) antes de cualquier edición en `.plans/{N}.md`.
- Handoff entre agentes (ej.: Athena entrega a Argos en el `to review → review`).
- Fresh clone del repo (caché local no existe).
- Sospecha de drift entre `.plans/{N}.md` y el body de la Issue (ej.: otra sesión editó el body vía UI de GitHub).

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-----------|
| `issue_number` | Sí | Número de la Issue (`{N}` en `{owner}/{repo}#{N}`) |
| `owner/repo` | No | Repo donde vive la Issue. Default: repo actual del worktree |
| `dest_path` | No | Path del archivo de caché. Default: `<paths.plans>/{N}.md` (resolución en `lex-agent-planning`) |

## Workflow

```
Progreso:
- [ ] 1. Resolver owner/repo + path de destino
- [ ] 2. Intentar MCP `get_issue` (preferido)
- [ ] 3. Fallback `gh issue view --json body`
- [ ] 4. Grabar body en `.plans/{N}.md`
- [ ] 5. Validar idempotencia
```

### Paso 1: Resolver owner/repo + path de destino

1. Si `owner/repo` fue pasado, usar. De lo contrario, derivar del worktree vía `gh repo view --json owner,name`.
2. Resolver path de destino:
   - Si `dest_path` fue pasado, usar.
   - De lo contrario, leer `paths.plans` en `.ahrena/.directives` (default `.plans/`).
   - Path final: `<paths.plans>/{N}.md`.
3. Garantizar que el directorio de destino existe (`mkdir -p`).

### Paso 2: Intentar MCP `get_issue` (preferido)

Per `lex-mcp` regla 1, si el servidor GitHub MCP está listado en `mcp.servers` y activo:

```python
issue = mcp.github.get_issue(owner=owner, repo=repo, issue_number=N)
body = issue["body"]
```

Si tiene éxito, saltar al Paso 4.

### Paso 3: Fallback `gh issue view --json body`

Per `lex-mcp` regla 4 (MCP indisponible), ejecutar el fallback CLI documentado:

```bash
gh issue view {N} --repo {owner}/{repo} --json body --jq .body > .plans/{N}.md
```

Si `gh` también falla:

1. Retry único tras 5 segundos de backoff.
2. Si persiste, ofrecer al usuario: (a) intentar de nuevo con otro comando, (b) pausar para investigación, (c) abortar.

### Paso 4: Grabar body en `.plans/{N}.md`

1. Si `.plans/{N}.md` ya existe y tiene contenido, **preservar bloques `<!-- not-flushed -->` ... `<!-- /not-flushed -->`** existentes:
   - Extraer todos los bloques `<!-- not-flushed -->` del archivo actual.
   - Sustituir el cuerpo principal por el body nuevo de la Issue.
   - Adjuntar los bloques `<!-- not-flushed -->` al final.
2. Si `.plans/{N}.md` no existe, grabar el body directamente (sin bloques `<!-- not-flushed -->` aún).

La preservación de bloques locales permite re-load sin perder scratch de la IA — re-load es solo re-sincronizar el contenido canónico.

### Paso 5: Validar idempotencia

Tras grabar, ejecutar una segunda llamada (read-only) y comparar:

```bash
# Comparación canónica (después de filtrar bloques no-flushados de ambos lados)
diff <(strip-not-flushed .plans/{N}.md) <(gh issue view {N} --json body --jq .body)
```

Resultado esperado: ninguna diferencia.

Si hay diferencia que no sea en bloques `<!-- not-flushed -->`, el re-load falló silenciosamente — abortar e investigar.

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `{N}.md` | Markdown (superset del body de la Issue + bloques `<!-- not-flushed -->` preservados) | `<paths.plans>/{N}.md` |

## Ejemplo de Ejecución

### Input de Ejemplo

```
issue_number: 96
owner/repo: guardiatechnology/ahrena
dest_path: (default) .plans/96.md
```

### Output de Ejemplo

`.plans/96.md` (justo después del primer load, sin bloques no-flushados aún):

```markdown
## Summary

**As** an Ahrena framework contributor,
**I want** to migrate plan storage to a 3-layer model,
**So that** plans live where they belong.

## Plan

### Objective
Refactorizar la capa de almacenamiento del plan para que el contenido viva en
tres capas con roles claros: Issue body (canonical) + .plans/ (caché IA)
+ .issues/ (Phase artifacts).

### Steps
- [x] Step 1 — Open Issue + branch + worktree
- [x] Step 2 — ADR-002
- [ ] Step 3 — Rewrite lex-agent-planning (3 langs)
...

### Risks
- .plans/ perdida en fresh clone — mitigado por kata-load-plan-from-issue.
...
```

Después de algunas ediciones de la IA en el caché local, el archivo lleva bloques no-flushados:

```markdown
## Summary
...
(contenido del body — espejado)
...

<!-- not-flushed -->
## Working notes
- 23:30 — comenzó Step 3; lex-agent-planning rewrite en pt-BR

## Next actions
1. Step 3.5 (split lex-issue-status)
2. Steps 6-8 (katas)

## Scratch
gh issue develop registra branch como "Development" en la sidebar — no olvidar.
<!-- /not-flushed -->
```

## Restricciones

- **Idempotente:** múltiples ejecuciones producen el mismo `.plans/{N}.md` para el mismo estado del body de la Issue.
- **No flushea:** este kata es one-way (Issue → caché). Para grabar de vuelta, usar `kata-flush-plan-to-issue`.
- **Preserva bloques locales:** los bloques `<!-- not-flushed -->` ... `<!-- /not-flushed -->` existentes en el `.plans/{N}.md` se preservan; solo el contenido canónico es re-sincronizado.
- **MCP > CLI:** preferir MCP `get_issue` cuando el servidor esté listado y activo; CLI `gh issue view` es fallback documentado per `lex-mcp` regla 4.
- **No crea Issue:** si la Issue `{N}` no existe, el kata falla con mensaje claro. Para crear Issue, usar `kata-plan-task` (Eunomia top-level) o `kata-create-subtasks` (Eunomia subtask).

## Referencias

- `lex-agent-planning` — modelo de 3 capas y cadencia de load/flush
- `lex-mcp` — preferencia MCP + fallback CLI
- `codex-agent-planning` — manual operacional
- ADR-002 — decisión de arquitectura
- `kata-flush-plan-to-issue` — operación inversa (caché → Issue)
- `kata-plan-task` — creación inicial del plan (rellena body de la Issue)
