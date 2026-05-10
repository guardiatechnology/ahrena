# Cry: Iniciar revisión de PR con `purpose=review`

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Atajo para iniciar una sesión Claude Code de revisión de PR ya etiquetada para la subsección `Review` del sello de costo

## Descripción

Atajo que invoca `kata-pr-review`. El Kata orienta la marcación `purpose=review` (vía variable de entorno `GUARDIA_PURPOSE` o heurística del prompt) y dispara la revisión. Sin esa marca, los turnos de revisión caen en el balde `dev` y contaminan la lectura del esfuerzo que produjo la PR.

## Uso

```
/cry-pr-review <PR_NUMBER> [repositorio]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `PR_NUMBER` | Sí | Número de la PR a revisar | `72` |
| `repositorio` | No | `owner/repo`; por defecto: `gh repo view --json nameWithOwner` | `guardiatechnology/ahrena` |

## Qué Hace el Comando

1. Resuelve `PR_NUMBER` y repositorio a partir de los parámetros o del contexto.
2. Invoca `kata-pr-review` con esos inputs.
3. El Kata verifica `pr_cost_tracking.enabled` y `attribution_mode` en `.ahrena/.directives`, orienta al usuario sobre cómo marcar la sesión como `purpose=review` (caminos A/B/C documentados en el Kata) y dispara `/review` en la PR.

## Plantilla de Prompt

```
Contexto:
- PR objetivo: #{{PR_NUMBER}}
- Repositorio: {{repositorio}} (opcional; resuelva vía `gh repo view` si está ausente)

Tarea:
Invoque kata-pr-review con PR_NUMBER y repositorio resueltos. Antes de
disparar /review, oriente al usuario a definir `GUARDIA_PURPOSE=review`
(o iniciar la sesión de revisión con `GUARDIA_PURPOSE=review claude`)
para que los turnos se contabilicen en la subsección Review del sello.

Formato de salida:
Estado de la marcación (variable definida / prompt heurístico) seguido
de la conducción de la revisión como lo haría normalmente con /review.
```

## Ejemplo de Invocación

```
/cry-pr-review 72
```

**Salida esperada:** el agente recuerda definir `GUARDIA_PURPOSE=review` (o recomienda iniciar la sesión con `/review PR #72`), confirma que el hook escribió `purpose=review` en el sidecar y prosigue con la revisión.

## Referencias

- `kata-pr-review` — Procedimiento detallado de marcación + disparo
- `codex-pr-cost-tracking` — Manual con la cascada `purpose` y el formato del bloque `Review`
- `kata-pr-cost-stamp` — Sella el bloque con el conteo de revisión en la PR
