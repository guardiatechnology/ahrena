# Codex: Planificación de Tareas de Agentes

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Creación, mantenimiento y ciclo de vida de planes de tareas de agentes en el contexto de Ahrena

## Visión General

Este Codex es el manual canónico de planificación de tareas de agentes. Complementa `lex-agent-planning` (la Ley) con plantillas, ejemplos de relleno, reglas de numeración, buenas prácticas y orientación para casos límite. Todo agente que cree planes DEBE consultar este Codex.

## Contexto

- **Dominio:** disciplina de ejecución de tareas por agentes de IA
- **Público objetivo:** todos los agentes (Claude, Cursor, warriors, katas) y revisores humanos
- **Actualización:** cuando la plantilla o las convenciones cambien (se recomienda ADR para cambios en el front-matter)

---

## 1. Resolución del Path de Planes

El agente resuelve el directorio de planes en el siguiente orden:

```
1. Leer .ahrena/.directives
2. Si paths.plans existe → usar ese valor (ej.: ".plans/")
3. En caso contrario → usar predeterminado por agente:
   - Claude Code (CLI, VSCode, Desktop, claude.ai) → .claude/plans/
   - Cursor                                         → .cursor/plans/
   - Agente desconocido                             → .plans/
```

Ejemplo de override en el proyecto:
```yaml
# .ahrena/.directives
paths:
  root: ".ahrena/"
  plans: ".plans/"    # override: todos los agentes usan .plans/
```

---

## 2. Convención de Nombre de Archivo

```
plan-{NNN}-{slug}.md
```

| Campo | Regla |
|---|---|
| `{NNN}` | Número secuencial de 3 dígitos con ceros (001, 002, …). Incrementar desde el mayor existente en el directorio. Sin saltos cuando sea posible; si hay un salto (plan abandonado), no reutilizar el número |
| `{slug}` | kebab-case, máximo 60 caracteres, resumen de la tarea |

Ejemplos:
- `plan-001-complete-feature-design-docs.md`
- `plan-002-create-warrior-hecate.md`
- `plan-003-update-discovery-warriors.md`

---

## 3. Plantilla Completa del Plan

```markdown
---
plan_id: "001"
title: "complete-feature-design-docs"
status: pending
agent: claude
issue: "guardiafinance/ahrena#42"
created_at: "2026-05-02T14:30:00Z"
updated_at: "2026-05-02T14:30:00Z"
---

# Plan: Complete Feature Design Docs — actualizar cries y katas

## Objetivo

Completar la migración de artefactos de diseño de feature a la estructura canónica
`docs/{context}/{category}/` definida por `lex-feature-design-docs`. Los warriors y katas
ya están actualizados; lo que falta son los Cries (puntos de entrada del usuario) y 2 katas con referencias residuales.

## Alcance

Archivos a modificar:
- `framework/pt-BR/engineering/platform/cries/cry-api-design.md`
- `framework/pt-BR/engineering/platform/cries/cry-event-storm.md`
- `framework/pt-BR/engineering/platform/cries/cry-feature-design.md`
- `framework/pt-BR/engineering/platform/cries/cry-full-design.md`
- `framework/pt-BR/engineering/platform/katas/kata-api-design-review.md`
- `framework/pt-BR/engineering/platform/katas/kata-api-design-doc.md`
- Equivalentes en `framework/en/` y `framework/es/`
- `.cursor/skills/` y `.cursor/commands/` correspondientes

Total: ~18 archivos.

## Pasos

- [ ] 1. Abrir issue en GitHub para rastrear este trabajo
- [ ] 2. Crear branch `feat/{N}-complete-feature-design-docs`
- [ ] 3. Actualizar `cry-api-design.md` (pt-BR, en, es)
- [ ] 4. Actualizar `cry-event-storm.md` (pt-BR, en, es)
- [ ] 5. Actualizar `cry-feature-design.md` (pt-BR, en, es)
- [ ] 6. Actualizar `cry-full-design.md` (pt-BR, en, es)
- [ ] 7. Actualizar `kata-api-design-review.md` (pt-BR, en, es)
- [ ] 8. Corregir `kata-api-design-doc.md` (pt-BR, en, es)
- [ ] 9. Actualizar `.cursor/commands/` y `.cursor/skills/` afectados
- [ ] 10. Commitear todos los artefactos anteriores (nuevos feature-design-docs + cries + katas)
- [ ] 11. Abrir PR referenciando el issue

## Dependencias

- Trabajo previo (sin commitear): `lex-feature-design-docs`, `codex-feature-design-docs`, `kata-feature-design-docs` + warriors + katas ya actualizados

## Riesgos

- Los cries en en/es requieren traducción consistente — usar las versiones pt-BR como fuente de verdad
- cry-feature-design tiene más referencias (paths.domain + paths.oas + paths.events) — verificar todas
```

---

## 4. Estados del Ciclo de Vida

| Estado | Cuándo usar | Quién actualiza |
|---|---|---|
| `pending` | Plan creado, esperando confirmación del usuario o inicio | Agente al crear |
| `in-progress` | Ejecución iniciada | Agente al comenzar el primer paso |
| `done` | Todos los pasos marcados con `[x]` | Agente al concluir |
| `abandoned` | Tarea cancelada antes de completar | Agente con nota de motivo |
| `archived` | PR mergeado, el plan ya no necesita atención activa | Agente tras el merge |

---

## 5. Cuándo se Requiere un Plan (y Cuándo No)

### Obligatorio

- Tarea con 2+ pasos encadenados
- Cualquier operación que toque 2+ archivos
- Toda invocación de warrior o cry (por definición de múltiples pasos)
- Cualquier tarea que produzca artefactos permanentes (archivos, commits, PRs, publicaciones)

### No obligatorio (paso único trivial)

- Editar un único archivo con instrucción directa y precisa
- Leer/consultar archivos sin escritura
- Ejecutar un único comando aislado sin efecto secundario permanente
- Responder una pregunta factual

### Zona gris — usar plan por precaución

- Tarea aparentemente simple que puede ramificarse (ej.: "arreglar el bug" sin conocer el alcance)
- Operación irreversible aunque sea de un solo paso (ej.: eliminar archivos)

---

## 6. Relación Entre Planes y Otros Artefactos

```
Issue de GitHub
    └── Plan (plan de tarea — committed)
            ├── ADR (si hay decisión arquitectónica relevante)
            └── ─ ─ ─ no confundir con ─ ─ ─
                Checkpoint (.checkpoint — gitignored, sesión)
```

- Un plan **referencia** un issue pero no lo reemplaza
- Un plan puede **generar** un ADR cuando se identifica una decisión de impacto durante la ejecución
- El **checkpoint** NO está subordinado al plan; es artefacto paralelo de **sesión**, no de **task**

### Plan vs `.checkpoint` — delimitación canónica

Plan cubre **task**: Objetivo, Alcance, Steps `[x]`, Decisiones cerradas, Riesgos, Verificación. Committed.
Checkpoint cubre **sesión**: Session focus, Active plans (punteros), Open threads, Notes. Gitignored.

| Contenido | Plan | Checkpoint |
|---|:---:|:---:|
| Steps `[x]` | ✅ | ❌ |
| Decisiones cerradas de la task | ✅ | ❌ |
| Riesgos de la task | ✅ | ❌ |
| Artifacts produced | ✅ | ❌ |
| Foco general de la ventana de trabajo | ❌ | ✅ |
| Lista de planes activos en la sesión | ❌ | ✅ |
| Hilos paralelos que no se convirtieron en plan | ❌ | ✅ |
| Scratchpad libre, enlaces, recordatorios | ❌ | ✅ |

Si el contenido se repite en ambos, hay superposición — el plan vence (committed). La superposición está PROHIBIDA por `lex-checkpoint` regla 5 y por `lex-agent-planning` "Relación con otros artefactos".

---

## 7. Buenas Prácticas

1. **Escribir el plan antes de saberlo todo.** El objetivo es hacer visible la intención, no producir documentación perfecta. Un plan impreciso que evoluciona es mejor que ningún plan.
2. **Mantener pasos atómicos.** Cada paso debe ser verificable: hecho o no hecho. Evitar pasos vagos como "encargarse de la parte de eventos".
3. **Actualizar en tiempo real.** Marcar `[x]` a medida que se completa cada paso, no al final de todo.
4. **Sin planes fantasma.** Si la tarea se cancela antes de comenzar, marcar `abandoned` con motivo — no eliminar el archivo.
5. **Commitear el plan.** El plan es parte del trabajo; debe ir en el mismo PR que los artefactos que describe.

---

## Referencias

- `lex-agent-planning` — Ley correspondiente
- `kata-plan-task` — procedimiento operacional para crear y mantener planes
- `lex-checkpoint` — seguimiento del estado de sesión
- `lex-issue-driven` — flujo Issue-Driven
