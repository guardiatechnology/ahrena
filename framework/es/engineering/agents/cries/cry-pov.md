# Cry: Ciclo de PoV de Agent

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Ingeniería — Agents (etapa pre-operacional): entry point principal para crear un PoV de agent vía stack Anthropic con observabilidad nativa

## Descripción

Entry point principal para generar un PoV (Proof of Value) de agent en la stack Anthropic — Skill, Subagent o Plugin. Invoca `warrior-claudionor` (Fábrica de Agents Pre-operacional), que orquesta los 7 katas POV (`kata-pov-scope-define` → `kata-pov-value-track`) seguidos de la implementación (skill vía `kata-skill-implement`, subagent vía `kata-agent-author`, plugin vía plan-034). Produce `docs/{context}/agents-pov/{agent}/` consumible por `cry-agent-design --from-pov` cuando el agent madura a `operational-concrete`.

## Invocación

```
/cry-pov --context <name> [--agent <slug>] --kind <skill|subagent|plugin> --problem "..." --value-metric "..." [--tier N] [--dry-run]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `--context` | Sí | Bounded context en kebab-case | `reconciliation` |
| `--agent` | No | Slug del PoV en kebab-case. Default: derivado como `{context}-pov`. Define el subdir `docs/{context}/agents-pov/{agent}/` | `rec-pov-classifier` |
| `--kind` | Sí | Tipo de artefacto Anthropic | `skill`, `subagent`, `plugin` |
| `--problem` | Sí | Problema del cliente en 1 frase | `"Equipo contable dedica 3h/día conciliando extracto"` |
| `--value-metric` | Sí | Métrica leading con ventana y threshold | `"% conciliación automática ≥ 60% en 4 semanas"` |
| `--tier` | No | Tier de criticidad (default: 3) | `3` |
| `--dry-run` | No | Lista artefactos a crear sin persistir | (flag) |
| `--force` | No | Sobreescribe PoV existente en el mismo `--context`/`--agent` | (flag) |

## Lo que el Comando Hace

1. Resuelve `--context` y `--agent` (deriva `{context}-pov` si `--agent` se omite) y prepara `docs/{context}/agents-pov/{agent}/`
2. Invoca `warrior-claudionor`, que dispara en secuencia:
   - `kata-pov-scope-define` → `pov.md` + `scope.md`
   - `kata-pov-system-prompt` → `system-prompt.md`
   - `kata-pov-tools-select` → `tools.md`
   - `kata-pov-context-curate` → `context-pack.md`
   - `kata-pov-observability-instrument` → `observability/`
   - `kata-pov-feedback-attach` → `feedback.md`
   - `kata-pov-value-track` → `value-proof.md` (template inicial)
3. Despacha la implementación según `--kind`:
   - `skill` → **Fase 8a:** si `{paths.skills_root}/{slug}/` no existe, invoca `kata-init-skill --slug={context}-pov-skill` (scaffold). **Fase 8b:** invoca `kata-skill-implement` (delega widgets a Hephaestus, Python a Apollo)
   - `subagent` → `kata-agent-author --from-pov docs/{context}/agents-pov/{agent}/`
   - `plugin` → delega a plan-034 (capability ortogonal). Si plan-034 no está mergeado, aborta con mensaje claro
4. Reporta el tree final de `docs/{context}/agents-pov/{agent}/` + paths de los artefactos de implementación

## Prompt Template

```
Estás iniciando un PoV de agent. Asume el papel de warrior-claudionor
(Fábrica de Agents Pre-operacional) y ejecuta el ciclo POV completo.

Context: {{context}}
Agent: {{agent | default: {{context}}-pov}}
Kind: {{kind}}
Problem: {{problem}}
Value metric: {{value_metric}}
Tier: {{tier | default: 3}}

Ejecuta los 7 katas POV en secuencia, persistiendo cada output en
docs/{{context}}/agents-pov/{{agent}}/. Aplica las 6 Directrices de Construcción
(lex-agent-construction-directives) en el rigor pre-operacional. Garantiza
que `stage: pre-operational` aparece literalmente en system-prompt.md.

Después despacha la implementación según --kind:
- skill: kata-init-skill (si es necesario) → kata-skill-implement
- subagent: kata-agent-author --from-pov
- plugin: delega a plan-034 (aborta si no está disponible)

Al final, reporta el tree completo y el status (listo para operar / faltan
completar / bloqueado por dependencia).
```

## Ejemplo de Invocación

**Input:**

```
/cry-pov --context reconciliation \
         --agent rec-pov-classifier \
         --kind skill \
         --problem "Equipo contable dedica 3h/día conciliando extracto bancario con asientos del ERP" \
         --value-metric "% conciliación automática ≥ 60% en 4 semanas"
```

**Output esperado:**

```
🛠  warrior-claudionor — ciclo PoV iniciado
   context: reconciliation
   agent: rec-pov-classifier
   kind: skill
   tier: 3 (default)

Fase 1/8 — kata-pov-scope-define
   ✅ pov.md + scope.md creados (caso de uso primario: pareo extracto↔asiento;
      criterio de descontinuación: < 30% tras 4 semanas)

Fase 2/8 — kata-pov-system-prompt
   ✅ system-prompt.md (stage: pre-operational declarado)

Fase 3/8 — kata-pov-tools-select
   ✅ tools.md (str_replace_editor + code execution; sin MCP custom)

Fase 4/8 — kata-pov-context-curate
   ✅ context-pack.md (4 few-shot positivos + 2 anti-patrones; PII anonimizada)

Fase 5/8 — kata-pov-observability-instrument
   ✅ observability/{traces-spec,prompts-log,tool-calls-log,value-metrics}.md

Fase 6/8 — kata-pov-feedback-attach
   ✅ feedback.md (métrica objetiva: aprobación del operador en 7 días)

Fase 7/8 — kata-pov-value-track
   ✅ value-proof.md (template; cadencia quincenal — tier-3)

Fase 8/8 — Implementación (--kind=skill)
   → kata-init-skill (scaffold)
     ✅ skills/reconciliation-pov-skill/ creado a partir del template
   → kata-skill-implement
     ↳ warrior-hephaestus: ningún widget necesario en este PoV (CLI/headless)
     ↳ warrior-apollo: script de similitud en scripts/match_transactions.py
   ✅ skill en skills/reconciliation-pov-skill/

Próximos pasos:
   - Operar PoV por 4 semanas; ejecutar kata-pov-value-track quincenalmente
   - Cuando value-proof.md::status = ready_for_dooc, invocar:
     /cry-agent-design --context reconciliation --from-pov docs/reconciliation/agents-pov/rec-pov-classifier/
```

## Restricciones

- `--problem` y `--value-metric` son obligatorios y deben ser concretos (sin genericidades como "automatizar cosas").
- `--kind=plugin` exige plan-034 mergeado; caso contrario aborta con mensaje claro.
- `--context` debe ser kebab-case y único; si ya existe `docs/{context}/agents-pov/{agent}/`, exige `--force` para sobreescribir.
- Todos los 7 katas POV se ejecutan en secuencia, sin skip; falla en cualquiera interrumpe el ciclo.
- El Cry **no** invoca `lex-*` ni `codex-*` directamente (`lex-pilars`); el trabajo lo hacen los katas vía `warrior-claudionor`.

## Diferencia de Kata y de otros Cries

| Aspecto | `cry-pov` | `cry-skill` | `cry-agent` |
|---|---|---|---|
| **Naturaleza** | Ciclo PoV completo + implementación | Skill como artefacto distribuible | Subagent aislado standalone |
| **Output** | `docs/{context}/agents-pov/{agent}/` + skill/subagent/plugin | `.dist/<slug>.skill/` | `.claude/agents/<slug>.md` |
| **Cuándo usar** | Probar valor de un agent al cliente | Empaquetar skill ya madura | Scaffold trivial sin ciclo POV |

---

**Modelo:** Este Cry invoca `warrior-claudionor` para el ciclo PoV completo. Para empaquetado puro de Skill, use `cry-skill`. Para scaffold trivial de subagent, use `cry-agent`.
