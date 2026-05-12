# Cry: Design Canónico de Agent en Operación Concreta

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Ingeniería — Agents: entry point para conducir promoción de PoV → `operational-concrete` o `direct-entry` en producción, bajo orquestación de `warrior-metis`

## Descripción

`cry-agent-design` es el entry point canónico para proyectar un agent en stage `operational-concrete`. Invoca `warrior-metis`, que aplica el gate de la DoOC (`kata-dooc-validate`), orquesta los 8 katas de design y entrega el paquete de 13 archivos en `docs/{context}/agents/{agent}/`.

Cuando `--from-pov` es proporcionado, el ciclo consume el output de `warrior-claudionor` (PoV pre-operacional) y enriquece el context pack con material real (few-shot, ejemplos negativos, telemetría). Cuando ausente, opera en `direct-entry` (exige ADR/PDR explícito) o `legacy-pov` (retrofit).

## Uso

```
/cry-agent-design --context <name> --agent <slug> [--from-pov <path>] --tier <1|2|3|4> [--owner "..."] [--entry-mode <with-pov|direct-entry|legacy-pov>] [--adr <path>]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `--context` | Sí | Bounded Context (kebab-case) — `docs/{context}/agents/{agent}/` | `reconciliation` |
| `--agent` | Sí | Slug del agent (kebab-case) | `rec-classifier` |
| `--from-pov` | No | Path del PoV de origen producido por `warrior-claudionor` | `docs/reconciliation/agents-pov/rec-pov-classifier/` |
| `--tier` | Sí | Tier de criticidad; tier-1/2 dispara SLO obligatorio per `lex-slo-required` | `tier-2` |
| `--owner` | No (sugerido) | Nombre + papel + canal de escalamiento del owner | `"Marta Souza, Lead Reconciliation, #rec-oncall"` |
| `--entry-mode` | No | Modo de entrada; default = `with-pov` cuando `--from-pov` presente, `direct-entry` cuando ausente | `with-pov` \| `direct-entry` \| `legacy-pov` |
| `--adr` | Condicional | Path del ADR/PDR; obligatorio en `direct-entry` y en `legacy-pov` fuera de la ventana de 90 días | `docs/adr/ADR-029-rec-classifier-direct-entry.md` |

## Lo que el Comando Hace

1. Invoca `warrior-metis` con los parámetros recibidos
2. Mêtis ejecuta el ciclo completo:
   - Paso 0 — `kata-dooc-validate` (gate canónico)
   - Pasos 1-8 — 8 katas de design en orden
   - Paso 9 — reciprocidad Feature ↔ Agent
   - Paso 10 — snapshot DoOC
   - Paso 11 — handoff a `warrior-apollo-agents`
3. Reporta el árbol final de archivos producidos
4. Declara que el paquete está listo para implementación por `warrior-apollo-agents`

## Prompt Template

```
Asume el papel de warrior-metis. Conduce la promoción del agent
{{agent}} en {{context}} a stage `operational-concrete`.

Inputs canónicos:
- context: {{context}}
- agent: {{agent}}
- tier: {{tier}}
- owner: {{owner}}
- entry-mode: {{entry_mode}}
- from-pov: {{from_pov_path}} (cuando aplicable)
- adr: {{adr_path}} (cuando direct-entry o legacy-pov fuera de la ventana)

Ejecuta el flujo principal de warrior-metis:
  Paso 0 — kata-dooc-validate (gate)
  Pasos 1-8 — 8 katas de design en orden determinístico
  Paso 9 — reciprocidad Feature ↔ Agent
  Paso 10 — snapshot DoOC
  Paso 11 — handoff a warrior-apollo-agents

Restricciones:
- NO promuevas el agent sin kata-dooc-validate retornar `go`
- NO escribas código (Python, TS); el paquete es design, no implementación
- Aplica tono per lex-brand-voice (directo, estratégico, afirmativo, claro;
  prohibido innovative, disruptive, transformative, revolutionary, fintech)
- Usa idioma per language.default en .ahrena/.directives

Formato de salida:
- Árbol final en docs/{{context}}/agents/{{agent}}/
- DoOC sidecar en docs/{{context}}/dooc/{{agent}}.md
- Actualización en docs/{{context}}/feature-agent-map.md
- Sumario con decisión DoOC + paths producidos + próximo paso (handoff a Apollo-Agents)
```

## Ejemplo de Invocación

**Input:**

```
/cry-agent-design \
  --context reconciliation \
  --agent rec-classifier \
  --from-pov docs/reconciliation/agents-pov/rec-pov-classifier/ \
  --tier tier-2 \
  --owner "Marta Souza, Lead Reconciliation, #rec-oncall"
```

**Output esperado (sumario):**

```
🛡️  warrior-metis — APM Operación Concreta
   context: reconciliation | agent: rec-classifier | tier: tier-2 | entry-mode: with-pov

✅ DoOC gate: go (9/9 ítems)
✅ 13 archivos producidos en docs/reconciliation/agents/rec-classifier/
✅ DoOC sidecar en docs/reconciliation/dooc/rec-classifier.md
✅ Reciprocidad Feature ↔ Agent actualizada en docs/reconciliation/feature-agent-map.md

Paquete listo para warrior-apollo-agents implementar (plan-013).
```

## Restricciones

- El Cry NO invoca Lexis ni Codex directamente (per `lex-pilars`); invoca solo `warrior-metis`
- `warrior-metis` orquesta todos los 9 katas internamente; el Cry permanece el entry point único
- En `direct-entry` sin `--adr`, el Cry falla antes de invocar Mêtis (validación en el shell wrapper)
- En `legacy-pov` fuera de la ventana de 90 días sin `--adr`, ídem
- El Cry NO modifica `.ahrena/.directives` ni `framework/`

## Diferencia de Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Invocación rápida (1 entry point) | Procedimiento estructurado |
| **Quién orquesta** | `warrior-metis` | Mêtis invoca los 9 katas |
| **Configura agente?** | No (es el invocador) | Sí |
| **Ejemplo** | `/cry-agent-design ...` | `kata-dooc-validate`, `kata-agent-overview-design`, ... |

## Cross-references

- `warrior-metis` — orquestador invocado por el Cry
- `kata-dooc-validate` — primer Kata invocado por Mêtis
- `warrior-claudionor` — upstream producer del PoV consumido vía `--from-pov`
- `warrior-apollo-agents` — downstream consumer post-design (per plan-013)
- `lex-agent-construction-directives`, `lex-agent-design-docs` — fundación de las reglas aplicadas

---

**Modelo:** Cry es el entry point único del stage Operación Concreta. Invoca `warrior-metis`. Mêtis aplica gate DoOC, orquesta 8 katas de design, entrega 13 archivos canónicos. Apollo-Agents implementa downstream.
