# Lexis: Planificación Obligatoria para Tareas de Agentes

> **Prefijo:** `lex-` | **Tipo:** Ley Inviolable | **Alcance:** Toda tarea de múltiples pasos iniciada por cualquier agente o subagente (Claude, Cursor, IDEs, warriors, katas, cries)

## Propósito

Los agentes que ejecutan sin planificación previa producen resultados parciales, dejan archivos en estados inconsistentes y obligan al usuario a reconstruir el contexto manualmente. Esta Lexis elimina ese patrón exigiendo que todo agente documente su plan antes de ejecutar, haciendo que la intención, el alcance y la secuencia sean auditables por humanos y por otros agentes.

## Ley

> **Todo agente DEBE crear un documento de plan en `./{agent_dir}/plans/plan-{NNN}-{slug}.md` (o en el path definido en `paths.plans` de `.ahrena/.directives`) ANTES de iniciar cualquier tarea que involucre 2 o más pasos, afecte múltiples archivos o produzca artefactos permanentes. El plan DEBE ser presentado al usuario para confirmación antes de que comience la ejecución. Iniciar ejecución de múltiples pasos sin un plan documentado y confirmado está PROHIBIDO.**

## Cobertura

- **Aplica a:** Claude Code (CLI, VSCode, Desktop, claude.ai/code), Cursor, cualquier agente o subagente de IA que invoque katas, warriors o cries en el contexto de Ahrena
- **Agentes vinculados:** todos, sin excepción por rol
- **Excepciones permitidas:** operaciones triviales de un solo paso (editar un único archivo con instrucción directa, consultas de solo lectura, comandos aislados sin efecto secundario permanente)

## Resolución del Path del Plan (precedencia)

| Prioridad | Fuente | Valor |
|:---:|---|---|
| 1 | `paths.plans` en `.ahrena/.directives` | Override de proyecto — reemplaza todo lo demás |
| 2 | Predeterminado por agente | `.claude/plans/` para Claude Code; `.cursor/plans/` para Cursor; `.plans/` para agente desconocido |

Nombre del archivo: `plan-{NNN}-{slug}.md` donde `{NNN}` es secuencial por directorio (001, 002, …), sin saltos.

## Estructura Mínima Obligatoria del Plan

```markdown
---
plan_id: "{NNN}"
title: "{slug}"
status: pending | in-progress | done | archived | abandoned
agent: claude | cursor | unknown
issue: "{owner/repo#N}"
created_at: "YYYY-MM-DDTHH:MM:SSZ"
updated_at: "YYYY-MM-DDTHH:MM:SSZ"
---

# Plan: {título legible}

## Objetivo
{Por qué se está realizando esta tarea — 1 a 3 frases}

## Alcance
{Qué se modificará: archivos, sistemas, artefactos afectados}

## Pasos
- [ ] Paso 1
- [ ] Paso 2
...

## Dependencias
{Planes o issues de los que depende esta tarea; "Ninguna" si no hay}

## Riesgos
{Riesgos conocidos y mitigaciones; "Ninguno identificado" si no hay}
```

## Ciclo de Vida del Plan

```
pending → in-progress → done
                     ↘ abandoned
done → archived
```

- El agente DEBE actualizar `status` en el front-matter al iniciar (`in-progress`) y al concluir (`done`)
- Los pasos DEBEN marcarse con `[x]` conforme se completan
- Los planes `done` o `abandoned` DEBEN moverse a `archived` tras el merge del PR correspondiente
- Los planes DEBEN commitearse junto con el trabajo que describen (no son efímeros como `.checkpoint`)

## Relación con Otros Artefactos

- **Issue de GitHub:** un plan referencia un issue; un issue puede tener múltiples planes (ej.: diseño, implementación, pruebas)
- **Checkpoint (`.checkpoint`):** el checkpoint rastrea el estado de sesión; el plan rastrea la intención y el progreso estructurado — son complementarios, no excluyentes
- **ADR:** cuando un plan identifica una decisión arquitectónica relevante, DEBE abrirse un ADR conforme a `lex-issue-driven`

## Ejemplos

### Correcto

```
Tarea: actualizar 4 cries y 2 katas a la nueva estructura de paths
→ El agente crea .claude/plans/plan-001-complete-feature-design-docs.md
→ Presenta al usuario: objetivo, 12 archivos a editar, secuencia
→ El usuario confirma
→ El agente ejecuta marcando pasos, actualiza status a done
→ Plan commiteado junto con las ediciones
```

### Incorrecto

```
Tarea: actualizar 4 cries y 2 katas
→ El agente comienza editando cry-api-design.md directamente sin crear un plan
→ ❌ Viola lex-agent-planning — ejecución de múltiples pasos sin plan documentado
```

## Validación Automatizada

- **Herramienta:** verificación por el agente antes de cualquier ejecución de múltiples pasos; `kata-plan-task` como punto de entrada canónico
- **Momento:** antes de cualquier ejecución de tarea de múltiples pasos — sin excepción
- **Métrica:** 0 tareas de múltiples pasos ejecutadas sin plan documentado en `{agent_dir}/plans/`

## Referencias

- `codex-agent-planning` — manual con plantilla completa, ejemplos y buenas prácticas
- `kata-plan-task` — procedimiento operacional para crear y mantener planes
- `lex-checkpoint` — seguimiento del estado de sesión (complementario)
- `lex-issue-driven` — flujo de desarrollo dirigido por issues
