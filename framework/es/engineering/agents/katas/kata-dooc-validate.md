# Kata: Validación de la Definition of Operational Concrete (DoOC)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Ingeniería — Agents: gate-keeping de promoción de `pre-operational` a `operational-concrete` per `lex-agent-construction-directives`

## Objetivo

Verificar los 9 ítems canónicos de la Definition of Operational Concrete (DoOC) antes de permitir la promoción de un agent de `pre-operational` a `operational-concrete`. El Kata es la herramienta ejecutable del HARD-GATE de `lex-agent-construction-directives`: produce un informe `go`/`no-go` auditable, registrado en `docs/{context}/dooc/{agent}.md`. No es un HARD-GATE nuevo — es el verificador del HARD-GATE existente.

## Cuándo Usar

- Antes de cualquier transición de `stage: pre-operational` → `stage: operational-concrete` en system prompt de agent
- Siempre que `warrior-metis` recibe `cry-agent-design --from-pov docs/{context}/agents-pov/{agent}/`
- En el Gate 2 del flujo Issue-Driven cuando la feature toca `docs/{context}/agents/`
- En auditoría periódica de agentes `legacy-pov` (90 días tras merge de `lex-agent-construction-directives`)

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `context` | Sí | Bounded Context del agent (kebab-case) |
| `agent` | Sí | Slug del agent (kebab-case) |
| `--from-pov <path>` | No | Path a `docs/{context}/agents-pov/{agent}/` cuando hay PoV. Si ausente, modo `direct-entry` exige ADR/PDR |
| `--entry-mode` | No | `with-pov` (default cuando `--from-pov` presente) \| `direct-entry` \| `legacy-pov` |
| `--tier` | Sí | `tier-1` \| `tier-2` \| `tier-3` \| `tier-4` (tier-1/2 dispara obligación de SLO per `lex-slo-required`) |
| `--owner` | Sí | Nombre + papel del stakeholder owner del agent + canal de escalamiento |

## Workflow

```
Progreso:
- [ ] 1. Resolver paths y modo de entrada
- [ ] 2. Verificar ítem (a) — Origen del PoV declarada
- [ ] 3. Verificar ítem (b) — Métrica leading probada
- [ ] 4. Verificar ítem (c) — Métrica lagging declarada
- [ ] 5. Verificar ítem (d) — Alcance estabilizado ≥ 2 semanas
- [ ] 6. Verificar ítem (e) — Observability data ≥ 7 días
- [ ] 7. Verificar ítem (f) — Stakeholder owner identificado
- [ ] 8. Verificar ítem (g) — Capacidad de implementación confirmada
- [ ] 9. Verificar ítem (h) — Tier declarado (tier-1/2 → SLO mandatorio)
- [ ] 10. Verificar ítem (i) — Stage explícito en el system prompt del PoV
- [ ] 11. Aplicar cláusula de excepción cuando aplicable (legacy-pov, direct-entry, user-override)
- [ ] 12. Producir informe `dooc/{agent}.md` + decisión `go`/`no-go`
```

### Paso 1: Resolver paths y modo de entrada

1. Resuelve `pov_path = docs/{context}/agents-pov/{agent}/` si `--from-pov` proporcionado; en otro caso registra `pov_path: N/A`
2. Define `entry_mode` per regla de precedencia: argumento explícito → `with-pov` cuando `pov_path` existe → `direct-entry` cuando no
3. En `entry_mode: direct-entry`, exige path a ADR/PDR en `docs/adr/` declarando: razón del bypass de `pre-operational`, leading metric objetivo + ventana post-deploy, plan de observability instrumentado desde el día 0. Sin ADR/PDR, falla inmediato con mensaje claro
4. En `entry_mode: legacy-pov`, verifica que la fecha del PoV original sea anterior al merge de `lex-agent-construction-directives` Y esté dentro de la ventana de 90 días tras el merge. Fuera de la ventana, falla inmediato

### Paso 2: Verificar ítem (a) — Origen del PoV declarada

| `entry_mode` | Criterio |
|--------------|----------|
| `with-pov` | Existe `pov_path/pov.md` válido (contiene `stage: pre-operational` en el header) → ✅ |
| `direct-entry` | Marca `N/A — direct-entry (ADR: {path})` referenciando el ADR/PDR del Paso 1 → ✅ |
| `legacy-pov` | Existe PoV histórico identificable (commit ref o path en archivo) → ✅ |

Falla si ningún criterio se satisface.

### Paso 3: Verificar ítem (b) — Métrica leading probada

La métrica leading es la evidencia operacional de que el agent entrega valor antes del impacto agregado. Criterio:

1. Lee `pov_path/value-proof.md` (output de `kata-pov-value-track`) cuando `with-pov`
2. Busca: nombre de la métrica + threshold declarado + ventana de observación ≥ 7 días + valor observado ≥ threshold por ≥ 2 ciclos consecutivos
3. En `direct-entry`, marca `N/A — direct-entry` referenciando el ADR; el ADR DEBE declarar la leading metric objetivo y la ventana post-deploy (relleno posterior)

Falla si:
- `with-pov` sin `value-proof.md` válido
- threshold o ventana no declarados
- valor observado bajo el threshold

### Paso 4: Verificar ítem (c) — Métrica lagging declarada

La métrica lagging es la métrica de negocio impactada (e.g., tiempo de cierre contable, tasa de retrabajo de conciliación). Criterio:

1. Lee `pov_path/value-proof.md` campo `lagging_metric` o `docs/{context}/features/{feature}.md` cuando el agent sirve features existentes
2. La métrica DEBE estar declarada con unidad y dirección de mejora esperada (ej.: "reducir tiempo medio de cierre mensual de 5d a 3d")

Incluso en `direct-entry`, este ítem es mandatorio. Falla sin ADR explícito de excepción vía cláusula `user-override`.

### Paso 5: Verificar ítem (d) — Alcance estabilizado ≥ 2 semanas

Criterio: el alcance del agent (caso de uso primario + fuera de alcance declarados) no cambió en las últimas 2 semanas. Verificación:

1. Lee `pov_path/scope.md` (output de `kata-pov-scope-define`) y revisa el historial de commits del archivo vía `git log --since="2 weeks ago" -- {scope.md}`
2. Acepta: 0 cambios en 14 días O solamente cambios tipográficos (sin alteración de sección `caso de uso primario` o `fuera de alcance`)
3. En `direct-entry`, marca `N/A — direct-entry`; el alcance se declara de nuevo durante el design por Mêtis

Falla si hay cambio estructural reciente.

### Paso 6: Verificar ítem (e) — Observability data ≥ 7 días

Criterio: telemetría mínima de 7 días del PoV en operación, alineada a `lex-observability-required` (1 trace + 1 métrica + structured log con correlation_id).

1. Lee `pov_path/observability/` (output de `kata-pov-observability-instrument`)
2. Verifica que `traces-spec.md`, `prompts-log.md`, `tool-calls-log.md` y `value-metrics.md` existen
3. Pide confirmación de que dashboards / agregadores externos tienen ≥ 7 días de recolección (humano confirma o path al snapshot de los datos)

En `direct-entry`, marca `N/A — direct-entry`; observability será instrumentada por `warrior-apollo-agents` desde el día 0 conforme el ADR.

### Paso 7: Verificar ítem (f) — Stakeholder owner identificado

Criterio: nombre del owner + papel + canal de escalamiento documentados. Verificación:

1. Argumento `--owner` proporcionado O `pov_path/value-proof.md::owner` poblado
2. Canal de escalamiento DEBE ser concreto (Slack `#canal`, email, on-call) — no "TBD" o "a definir"

Mandatorio en todos los `entry_mode`. Falla sin excepción declarada.

### Paso 8: Verificar ítem (g) — Capacidad de implementación confirmada

Criterio:

1. `warrior-apollo-agents` está disponible (plan-013 mergeado — chequea vía existencia del archivo `framework/{lang}/engineering/backend/warriors/warrior-apollo-agents.md`) → ✅
2. O camino alternativo declarado en ADR (`docs/adr/ADR-{N}-{slug}.md`)

Sin ninguno de los dos, falla.

### Paso 9: Verificar ítem (h) — Tier declarado

Criterio:

1. Argumento `--tier` en {`tier-1`, `tier-2`, `tier-3`, `tier-4`}
2. Cuando `tier-1` o `tier-2`, registra obligación de producir `docs/{context}/agents/{agent}/metrics.md` con sección SLO per `lex-slo-required` (declarada como precondición para conclusión del design, no para paso de la DoOC)
3. `tier-3` / `tier-4` no dispara obligación de SLO

Falla si `--tier` ausente o fuera del enum.

### Paso 10: Verificar ítem (i) — Stage explícito en el system prompt del PoV

Criterio: `pov_path/system-prompt.md` contiene literalmente `stage: pre-operational` (per `lex-system-prompt`).

1. En `with-pov`, lee el archivo y busca el string literal
2. En `direct-entry`, marca `N/A — direct-entry`; Mêtis declarará `stage: operational-concrete` en el system prompt producido
3. En `legacy-pov`, requiere migración manual vía `kata-pov-system-prompt --retrofit` antes de proseguir; sin retrofit, falla

### Paso 11: Aplicar cláusula de excepción cuando aplicable

En `entry_mode: direct-entry`, los ítems (a), (b), (d) y (e) pueden aparecer como `N/A — direct-entry` si el ADR/PDR del Paso 1 declara (i) razón del bypass, (ii) leading metric objetivo + ventana post-deploy, (iii) plan de observability día 0. Ítems (c) y (f)-(i) permanecen mandatorios.

En `entry_mode: user-override` (CEO o Brand owner promueve con evidencias parciales), exige ADR/PDR declarando (i) cuáles ítems fueron sobrescritos, (ii) `Promoted by: {nombre}` en `dooc/{agent}.md`, (iii) ventana de compensación retroactiva (sugerido 30 días). Ítems sobrescritos se vuelven `N/A — user-override`.

### Paso 12: Producir informe `dooc/{agent}.md` + decisión

Persiste en `docs/{context}/dooc/{agent}.md` en el formato:

```markdown
# DoOC — {agent}

> **Bounded Context:** {context}
> **Entry mode:** with-pov | direct-entry | legacy-pov
> **Tier:** tier-1 | tier-2 | tier-3 | tier-4
> **Promoted by:** {nombre, papel} (en user-override)
> **PR ref:** {owner/repo#NNN}
> **Validation date:** {ISO 8601}
> **Validator:** warrior-metis vía kata-dooc-validate

## Ítems (9)

| # | Ítem | Status | Evidence |
|---|------|:------:|----------|
| a | Origen del PoV declarada | ✅ \| ❌ \| N/A | path o ADR ref |
| b | Métrica leading probada | ✅ \| ❌ \| N/A | path o ADR ref |
| c | Métrica lagging declarada | ✅ \| ❌ | path o ADR ref |
| d | Alcance estabilizado ≥ 2 semanas | ✅ \| ❌ \| N/A | git log evidence |
| e | Observability data ≥ 7 días | ✅ \| ❌ \| N/A | path |
| f | Stakeholder owner identificado | ✅ \| ❌ | nombre + canal |
| g | Capacidad de implementación confirmada | ✅ \| ❌ | warrior path o ADR |
| h | Tier declarado (SLO si tier-1/2) | ✅ \| ❌ | tier value |
| i | Stage explícito en system prompt del PoV | ✅ \| ❌ \| N/A | path |

## Decisión

`go` cuando todos los ítems sean ✅ o `N/A` justificado por ADR/PDR válido.
`no-go` en cualquier otro caso.

## ADRs / PDRs referenciados

- {path/nombre}

## Próximos pasos cuando `go`

Proseguir con `warrior-metis` orquestando los 8 katas de design restantes.

## Próximos pasos cuando `no-go`

Reportar ítems faltantes al usuario; sugerir retoma del PoV (`/cry-pov`) o ADR de excepción cuando aplicable.
```

### Validación Final

Antes de declarar `go`, verificar:

- [ ] Todos los 9 ítems con status ✅ o `N/A` justificado por ADR/PDR existente
- [ ] `dooc/{agent}.md` persistido en el path canónico
- [ ] Cuando `tier-1` o `tier-2`, registrar obligación pendiente de SLO en `metrics.md` (a ser producida por `kata-agent-feedback-design`)
- [ ] Owner + canal de escalamiento concretos (no placeholders)
- [ ] PR ref poblado cuando el Kata se invoca dentro de flujo Issue-Driven

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `dooc/{agent}.md` | Markdown | `docs/{context}/dooc/{agent}.md` |
| Decisión | `go` \| `no-go` | retorno al orquestrador (`warrior-metis`) |
| Lista de ítems faltantes | Lista textual | en caso de `no-go`, devuelta al invocador |

## Ejemplo de Ejecución

### Input de Ejemplo

```
kata-dooc-validate \
  --context reconciliation \
  --agent rec-classifier \
  --from-pov docs/reconciliation/agents-pov/rec-pov-classifier/ \
  --tier tier-2 \
  --owner "Marta Souza, Lead Reconciliation, #rec-oncall"
```

### Output de Ejemplo (extracto)

```markdown
# DoOC — rec-classifier

> **Bounded Context:** reconciliation
> **Entry mode:** with-pov
> **Tier:** tier-2
> **PR ref:** guardiatechnology/ahrena#543
> **Validation date:** 2026-05-12T15:30:00Z
> **Validator:** warrior-metis vía kata-dooc-validate

## Ítems (9)

| # | Ítem | Status | Evidence |
|---|------|:------:|----------|
| a | Origen del PoV declarada | ✅ | docs/reconciliation/agents-pov/rec-pov-classifier/pov.md |
| b | Métrica leading probada | ✅ | reconciliation_auto_rate = 62% (threshold 60%) por 21 días |
| c | Métrica lagging declarada | ✅ | docs/reconciliation/features/transaction-classification.md::lagging_metric |
| d | Alcance estabilizado ≥ 2 semanas | ✅ | git log scope.md: 0 cambios en 18 días |
| e | Observability data ≥ 7 días | ✅ | docs/reconciliation/agents-pov/rec-pov-classifier/observability/ (21 días) |
| f | Stakeholder owner identificado | ✅ | Marta Souza, Lead Reconciliation, #rec-oncall |
| g | Capacidad de implementación confirmada | ✅ | framework/.../warriors/warrior-apollo-agents.md (plan-013 mergeado) |
| h | Tier declarado | ✅ | tier-2 (SLO obligatorio en metrics.md) |
| i | Stage explícito en system prompt del PoV | ✅ | pov-path/system-prompt.md::stage: pre-operational |

## Decisión

`go` — todos los 9 ítems ✅. Proseguir con design de los 13 archivos.
```

## Restricciones

- El Kata es el **verificador** del HARD-GATE de `lex-agent-construction-directives`; no crea un HARD-GATE nuevo
- `no-go` es decisión final del Kata; quien decide retomar PoV o abrir ADR de excepción es el usuario humano
- En modo `direct-entry`, el ADR/PDR DEBE existir antes del Paso 1; crear ADR retroactivo solo para pasar el Kata se prohíbe (viola el espíritu del gate)
- No persistir `dooc/{agent}.md` cuando el output es `no-go` — solamente reportar; el snapshot va al destino canónico solo tras `go`
- No modificar `lex-agent-construction-directives` ni `lex-agent-design-docs`
- PR ref es obligatorio cuando el Kata corre dentro de flujo Issue-Driven; en auditoría periódica o ronda manual, rellena con `manual-audit`

---

**Modelo:** Kata gate-keeper canónico de promoción a `operational-concrete`. Ejecuta programáticamente los 9 ítems de la DoOC, aplica las 3 cláusulas de excepción declaradas en `lex-agent-construction-directives` (legacy-pov, direct-entry, user-override) y persiste el snapshot en `docs/{context}/dooc/{agent}.md` cuando `go`. Siempre invocado primero por `warrior-metis` antes de cualquier otro kata de design.
