# Cry: Iniciar Sesión de Product Discovery

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Ámbito:** Product Discovery — atajo para invocar `warrior-pitia` con un `topic` y `source_refs[]`

## Descripción

Atajo que invoca `warrior-pitia` para conducir una sesión de Product Discovery: leer las fuentes informadas y producir uno o más insights estructurados bajo `docs/discovery/{topic}/insights/`. El Cry **no** invoca Lexis ni Codex directamente — solo acciona el Warrior, que internamente ejecuta `kata-discovery-synthesis` y consulta `lex-discovery-flow` y `codex-discovery-artifacts`.

## Uso

```
/cry-discovery
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `topic` | Sí | Tema de la iniciativa de Discovery en kebab-case | `scheduled-payments-research` |
| `source_refs[]` | Sí (≥1) | Lista de URLs o paths de las fuentes a estudiar | URLs Notion, Figma, GitHub; paths locales |
| `mode` | No | `new` (default) o `refine` | `new` |
| `target_insight_id` | Condicional | Obligatorio si `mode == refine` — id del insight a actualizar | `scheduled-payments-research/insights/001-...` |
| `feedback` | Condicional | Obligatorio si `mode == refine` — texto del feedback humano | "Especificar lo que se considera divergencia alta" |

## Lo que Hace el Comando

1. Invoca `warrior-pitia` con los parámetros proporcionados
2. Pitia lee `.ahrena/.directives`, internaliza `lex-discovery-flow` y `codex-discovery-artifacts`
3. Pitia ejecuta `kata-discovery-synthesis` leyendo las `source_refs[]` vía MCP o `Read`
4. Pitia produce archivos nuevos en `docs/discovery/{topic}/insights/` (modo `new`) o actualiza archivo existente (modo `refine`)
5. Pitia reporta los archivos creados/actualizados y destaca preguntas abiertas críticas

## Prompt Template

```
Asume el papel de warrior-pitia (Product Discovery).

Parámetros recibidos:
- topic: {{topic}}
- source_refs:
{{source_refs}}
- mode: {{mode}}
- target_insight_id: {{target_insight_id}}
- feedback: {{feedback}}

Tarea:
Ejecute kata-discovery-synthesis con los parámetros anteriores.
Antes de cualquier escritura, lea .ahrena/.directives, lex-discovery-flow y codex-discovery-artifacts.
Produzca un insight por archivo en docs/discovery/{{topic}}/insights/{NNN}-{slug}.md
con status: proposed (modo new) o actualice el existente (modo refine).
No proponga solución — la solución es responsabilidad de warrior-phanes.
No altere status a nada distinto de la creación inicial en proposed (HARD-GATE 2).

Formato de salida:
- Lista de los archivos creados/actualizados con paths canónicos
- Para cada insight, 1 frase de resumen de la observación
- Preguntas abiertas críticas que piden evidencia adicional
- Candidatos a awaiting_evidence cuando aplicable (señala al humano; no cambia status)
```

## Ejemplo de Invocación

**Input:**

```
/cry-discovery
topic: scheduled-payments-research
source_refs:
  - https://www.notion.so/guardia/interview-accountant-2026-05-04-abc123
  - docs/transcripts/process-walkthrough-erp-x.md
  - https://github.com/guardiatechnology/erp-x-spec/blob/main/openapi.yaml
mode: new
```

**Output esperado:**

```
warrior-pitia ejecutó kata-discovery-synthesis. 3 insights creados con status: proposed:

1. docs/discovery/scheduled-payments-research/insights/001-manual-reconciliation-bottleneck.md
   — 4h/semana de conciliación manual; cuello de botella declarado por el contador entrevistado
2. docs/discovery/scheduled-payments-research/insights/002-erp-x-7-screens-per-divergence.md
   — 7 pantallas para resolver 1 divergencia; OpenAPI sin endpoint de conciliación en lote
3. docs/discovery/scheduled-payments-research/insights/003-date-vs-cash-divergence-pattern.md
   — Divergencia de fecha de competencia vs. caja concentra ~60% de las ocurrencias

Preguntas abiertas críticas:
- Mediana real del tiempo de conciliación por oficina (muestra de 1)
- Confirmación del patrón de divergencia en oficinas además del entrevistado

Candidato a awaiting_evidence: insight #003 (depende de mediana). La decisión de transición es tuya.
```

## Restricciones

- No modifica insights existentes salvo en modo `refine` con `target_insight_id` válido
- No crea Idea — la Idea es responsabilidad de `warrior-phanes` vía `cry-ideation`
- No altera status fuera de la creación inicial en `proposed` — toda otra transición depende de acción humana per HARD-GATE 2 de la `lex-discovery-flow`
- Salida siempre en el idioma definido en `language.default` de `.directives` (default: pt-BR)

## Diferencia con Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Atajo de invocación de Pitia | Procedimiento que Pitia ejecuta |
| **Quién invoca** | Usuario humano | Warrior (Pitia) |
| **Lo que hace** | Acciona el warrior con parámetros | Sintetiza fuentes en insights |
| **Ejemplo** | `/cry-discovery` | `kata-discovery-synthesis` |

## Referencias

- `warrior-pitia` — agente invocado por este Cry
- `kata-discovery-synthesis` — procedimiento ejecutado internamente
- `lex-discovery-flow` — ley aplicable (consultada por el warrior, no por el cry)
- `codex-discovery-artifacts` — schema de insights (consultado por el warrior)
