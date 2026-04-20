# Kata: Escribir Architecture Decision Record (ADR)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Producción de un ADR individual en formato MADR simplificado en `docs/adr/`

## Objetivo

Escribir un Architecture Decision Record (ADR) individual en el formato MADR simplificado, con numeración secuencial y status gestionado a lo largo del ciclo de vida (proposed → accepted → deprecated/superseded). Invocado por `kata-architecture-brief` para cada decisión arquitectónica relevante identificada, o manualmente cuando una decisión necesita formalizarse fuera del flujo Issue-Driven.

## Cuándo Usar

- Llamado por `kata-architecture-brief` en la Fase 3 del flujo Issue-Driven para cada decisión relevante
- Llamado manualmente cuando una decisión arquitectónica necesita formalizarse (ej.: migración de framework, patrón adoptado en el codebase)
- **No usar** para: bugfix puntual, refactor local, endpoint siguiendo patrón (según checklist en `codex-issue-workflow`)

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Título | Sí | Título corto e imperativo de la decisión (ej.: "Use FastAPI routers for module separation") |
| Contexto | Sí | Problema o fuerza que motivó la decisión |
| Decisión | Sí | La decisión tomada, en voz activa |
| Alternativas consideradas | Sí | Al menos 1 alternativa con justificación de rechazo |
| Status inicial | No | `proposed` (por defecto), `accepted` si se aprobó en la misma sesión |
| Issue relacionada | No | Número de la issue de GitHub (ej.: `42`) |

## Workflow

```
Progreso:
- [ ] 1. Detectar siguiente número secuencial
- [ ] 2. Generar slug del título
- [ ] 3. Componer contenido en formato MADR
- [ ] 4. Persistir en docs/adr/
- [ ] 5. Retornar referencia al invocador
```

### Paso 1: Detectar siguiente número secuencial

1. Listar archivos en `docs/adr/` con patrón `ADR-{n}-*.md`.
2. Extraer el mayor `n` existente (ej.: `ADR-007-*.md` → `7`).
3. Siguiente número = mayor + 1 (ej.: `8`).
4. Si `docs/adr/` no existe, crear el directorio e iniciar en `1`.
5. Formatear con zero-padding de 3 dígitos (`ADR-001`, `ADR-023`, `ADR-125`).

### Paso 2: Generar slug del título

1. Convertir el título a lowercase.
2. Reemplazar espacios por guiones.
3. Eliminar caracteres no alfanuméricos (excepto guiones).
4. Limitar a ~60 caracteres.

**Ejemplo:** `"Use FastAPI routers for module separation"` → `use-fastapi-routers-for-module-separation`

**Nombre de archivo final:** `docs/adr/ADR-{n}-{slug}.md` (ej.: `docs/adr/ADR-008-use-fastapi-routers-for-module-separation.md`)

### Paso 3: Componer contenido en formato MADR

```markdown
# ADR-{n}: {Título}

- **Status:** {proposed | accepted | deprecated | superseded by ADR-XXX}
- **Date:** {YYYY-MM-DD}
- **Issue:** #{issue-number}  (omitir si no aplica)

## Context

{problema o fuerza que motivó la decisión — 1-3 párrafos}

## Decision

{la decisión tomada, en voz activa — 1-2 párrafos}

## Consequences

### Positive

- {beneficio 1}
- {beneficio 2}

### Negative

- {costo o trade-off 1}
- {costo o trade-off 2}

### Neutral

- {cambio que no es claramente beneficio ni costo, pero es relevante}

## Alternatives Considered

- **{Alternativa A}:** {descripción breve}. Rechazada porque {justificación}.
- **{Alternativa B}:** {descripción breve}. Rechazada porque {justificación}.
```

**Reglas de contenido:**
- **Context** describe el problema, no la solución. Debe ser comprensible por alguien leyendo en 2 años.
- **Decision** es declarativa e imperativa ("Adoptamos X", "Usamos Y").
- **Consequences** incluye costos — un ADR sin Negative es sospechoso.
- **Alternatives** necesita al menos 1; "no hacer nada" es una alternativa válida.
- Si la decisión está vinculada a una issue, incluir `**Issue:** #{n}` con enlace clicable.

### Paso 4: Persistir en `docs/adr/`

1. Crear directorio `docs/adr/` si no existe.
2. Escribir el archivo en `docs/adr/ADR-{n}-{slug}.md`.
3. Si el archivo ya existe (improbable, pues n es secuencial), detener y reportar error.

### Paso 5: Retornar referencia al invocador

Retornar:
- Ruta relativa: `docs/adr/ADR-{n}-{slug}.md`
- Número: `ADR-{n}`
- Status: `proposed` (o el status informado)

Esta referencia la usa `kata-architecture-brief` para incluir en el documento de arquitectura y `warrior-athena` para presentar en el Gate 1.

## Transiciones de Status

Tras creado con status `proposed`, el ADR puede transitar a:

| Nuevo Status | Cuándo | Acción |
|---|---|---|
| `accepted` | Tras aprobación humana en el Gate 1 | Editar el ADR, cambiar `Status:` |
| `deprecated` | La decisión dejó de ser relevante pero no fue sustituida | Editar, cambiar `Status:` y agregar nota explicando |
| `superseded by ADR-XXX` | Sustituida por otro ADR | Editar, cambiar `Status:`; el nuevo ADR referencia este en su `Context` |

**Importante:** los ADRs son **append-only en espíritu** — una vez `accepted`, el contenido histórico se preserva. Los cambios se hacen creando un nuevo ADR que supersedes al anterior.

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Archivo ADR | Markdown MADR | `docs/adr/ADR-{n}-{slug}.md` |
| Referencia al invocador | Texto: ruta + número + status | Retorno |

## Restricciones

- **Numeración secuencial inviolable:** nunca reusar números; los gaps indican ADRs removidos (lo cual no debe ocurrir — ver "Importante" arriba).
- **MADR simplificado:** seguir estrictamente la estructura arriba; no agregar secciones opcionales sin justificación.
- **Al menos 1 alternativa:** un ADR sin alternativas es sospechoso (significa que la decisión se tomó sin considerar opciones).
- **Destino fijo:** `docs/adr/` según `lex-issue-driven` — nunca `.ahrena/` u otra ruta.
- **No editar ADRs `accepted` excepto para transición de status:** los cambios de decisión se convierten en un nuevo ADR (`superseded by`).

## Referencias

- `codex-issue-workflow` — checklist de cuándo generar ADR
- `lex-issue-driven` — obligatoriedad de ADR para decisiones relevantes
- `kata-architecture-brief` — kata que invoca este
- [MADR — Markdown Architectural Decision Records](https://adr.github.io/madr/)
