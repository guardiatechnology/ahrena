# Cry: Promover Insight Aprobado a Idea

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Ámbito:** Product Discovery — atajo para invocar `warrior-phanes` con uno o más `insight_path` aprobados

## Descripción

Atajo que invoca `warrior-phanes` para promover insights aprobados a una Idea bajo `docs/discovery/{topic}/ideas/`. El Cry **no** invoca Lexis ni Codex directamente — solo acciona el Warrior, que internamente ejecuta `kata-ideation-from-insight`, valida el HARD-GATE 1 de la `lex-discovery-flow` y consulta `codex-discovery-artifacts`.

## Uso

```
/cry-ideation
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `insight_path` | Sí | Path canónico del insight a promover (string o array cuando múltiples insights forman una Idea única) | `docs/discovery/scheduled-payments-research/insights/001-...` |
| `additional_context` | No | Contexto extra proporcionado por el humano (datos de telemetría, hipótesis refinada, piloto disponible) que ayuda a Phanes a montar `success_metric` o `effort_estimate` | "Cliente piloto disponible: oficina Y" |

## Lo que Hace el Comando

1. Invoca `warrior-phanes` con los parámetros proporcionados
2. Phanes lee `.ahrena/.directives` e internaliza `lex-discovery-flow` y `codex-discovery-artifacts`
3. Phanes valida el HARD-GATE 1 en **tres momentos** (per `kata-ideation-from-insight`): preflight de input (a, d) antes de cualquier lectura, preflight de output (b, c) sobre la Idea sintetizada antes de grabar, y post-escritura (e) con rollback transaccional si la actualización parcial de los insights falla
4. Si el preflight pasa, Phanes ejecuta `kata-ideation-from-insight`, generando el archivo de la Idea con los 5 campos de contenido obligatorios completados
5. Phanes actualiza el/los insight(s) de origen a `status: promoted` con `idea_ref` apuntando a la Idea (rollback automático si falla)
6. Phanes reporta la Idea creada y los insights promovidos, señalando lagunas que piden validación adicional

## Prompt Template

```
Asume el papel de warrior-phanes (Product Ideation).

Parámetros recibidos:
- insight_path:
{{insight_path}}
- additional_context:
{{additional_context}}

Tarea:
Ejecute kata-ideation-from-insight con los parámetros anteriores.
Antes de cualquier escritura, lea .ahrena/.directives, lex-discovery-flow y codex-discovery-artifacts.
Valide el HARD-GATE 1 en tres momentos, conforme el kata:
  - Preflight de input (a, d) antes de cualquier lectura
  - Preflight de output (b, c) sobre la Idea sintetizada, ANTES de grabar
  - Post-escritura (e) con rollback transaccional si la actualización parcial de los insights falla
Si cualquier preflight falla, interrumpa e informe al humano qué acción destraba.
Si pasa, genere la Idea en docs/discovery/{topic}/ideas/{NNN}-{slug}.md
con los 5 campos de contenido obligatorios (problem, hypothesis, target_user, success_metric, effort_estimate)
y linked_insights[] referenciando los insights de origen.
Actualice el/los insight(s) de origen a status: promoted + idea_ref + updated_at.
No altere status de insight a approved (HARD-GATE 2; prerrogativa humana).

Formato de salida:
- Confirmación de la Idea creada con path canónico
- Lista de los insights promovidos
- Resumen de cada uno de los 5 campos de contenido obligatorios
- Lagunas que piden validación adicional antes del design cycle
```

## Ejemplo de Invocación

**Input:**

```
/cry-ideation
insight_path: docs/discovery/scheduled-payments-research/insights/001-manual-reconciliation-bottleneck.md
additional_context: |
  Cliente piloto disponible: oficina Y con 80 contadores activos
```

**Output esperado:**

```
warrior-phanes validó HARD-GATE 1 ✅ y ejecutó kata-ideation-from-insight.

Idea creada: docs/discovery/scheduled-payments-research/ideas/001-auto-reconcile-erp-bank.md

Insights promovidos:
- scheduled-payments-research/insights/001-manual-reconciliation-bottleneck → status: promoted

Resumen de la Idea:
- Problem: 4h/semana de conciliación manual, sin percepción de valor
- Hypothesis: sugerencia automática con confianza ≥ 90% será aceptada en ≥ 70% de los casos
- Target user: contador operacional en oficinas 50–500 clientes integrados al ERP X
- Success metric: tiempo de conciliación por mes por cliente — baseline 4h → meta 1.5h en 90 días
- Effort estimate: M (2–4 sprints; depende de modelo de matching y webhooks ERP X)

Lagunas que piden validación:
- Baseline 4h viene de 1 entrevista — recomiendo confirmar con 3 entrevistas adicionales
- Webhooks del ERP X no fueron validados con la documentación del producto

Idea lista para consumo de warrior-prometheus.
```

**Escenario de falla:**

```
/cry-ideation
insight_path: docs/discovery/scheduled-payments-research/insights/005-payment-method-confusion.md
```

```
warrior-phanes interrumpió. HARD-GATE 1 falló:
- (a) status: under_review ❌ (esperado: approved)

Para destrabar:
1. Evalúa el insight en PR review
2. Si apruebas, actualiza status: approved en el front-matter (decisión tuya per HARD-GATE 2)
3. Reinvoca /cry-ideation con el mismo insight_path
```

## Restricciones

- No crea Idea si el HARD-GATE 1 falla — interrumpe e informa al humano
- No altera status de insight a `approved` — prerrogativa humana per HARD-GATE 2 de la `lex-discovery-flow`
- No modifica campos del insight de origen además de `status`, `idea_ref` y `updated_at`
- No mezcla `topics` distintos en una única Idea
- Salida siempre en el idioma definido en `language.default` de `.directives` (default: pt-BR)

## Diferencia con Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Atajo de invocación de Phanes | Procedimiento que Phanes ejecuta |
| **Quién invoca** | Usuario humano | Warrior (Phanes) |
| **Lo que hace** | Acciona el warrior con parámetros | Valida HARD-GATE 1 y promueve insight a Idea |
| **Ejemplo** | `/cry-ideation` | `kata-ideation-from-insight` |

## Referencias

- `warrior-phanes` — agente invocado por este Cry
- `kata-ideation-from-insight` — procedimiento ejecutado internamente
- `lex-discovery-flow` — ley aplicable (consultada por el warrior, no por el cry)
- `codex-discovery-artifacts` — schema de insights e Ideas (consultado por el warrior)
- `cry-discovery` — Cry complementario (producción de insights upstream)
