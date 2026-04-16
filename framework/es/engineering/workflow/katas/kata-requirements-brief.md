# Kata: Elicitación de Requisitos (perspectiva PO)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Fase 2 del flujo Issue-Driven — transformación del brief de la Fase 1 en lista numerada de criterios de aceptación, DoD y out-of-scope

## Objetivo

Adoptando la perspectiva de Product Owner, convertir el brief producido en la Fase 1 en un documento de requisitos que contenga: lista numerada de criterios de aceptación (ACs), Definition of Done (DoD), items fuera de alcance declarados explícitamente, y preguntas pendientes para el usuario. Los ACs numerados forman la base de la trazabilidad AC ↔ prueba exigida por el Gate 2 (según `lex-issue-driven`).

## Cuándo Usar

- Fase 2 del flujo orquestado por `warrior-athena`, tras la conclusión de la Fase 1 (`kata-issue-analysis`)
- Cuando es necesario formalizar criterios medibles a partir de una descripción genérica de feature/bugfix

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Brief de la Fase 1 | Sí | `docs/issues/issue-{n}/01-brief.md` |
| Confirmaciones del usuario | No | Respuestas a preguntas pendientes identificadas en el brief (vía interacción) |

## Workflow

```
Progreso:
- [ ] 1. Leer el brief de la Fase 1
- [ ] 2. Identificar actores, entidades y comportamientos
- [ ] 3. Formular ACs en formato Given/When/Then
- [ ] 4. Resolver incógnitas con preguntas al usuario
- [ ] 5. Definir DoD y out-of-scope
- [ ] 6. Persistir en docs/issues/issue-{n}/02-requirements.md
- [ ] 7. Actualizar checkpoint
```

### Paso 1: Leer el brief de la Fase 1

1. Leer `docs/issues/issue-{n}/01-brief.md`.
2. Si no existe, informar que la Fase 1 no fue ejecutada y detener.
3. Enfocar en las secciones: Problema, Contexto adicional, Tipo de trabajo, Riesgos e incógnitas.

### Paso 2: Identificar actores, entidades y comportamientos

1. Listar actores involucrados (ej.: cliente, sistema de pago, backoffice).
2. Listar entidades afectadas (ej.: Refund, Payment, AuditLog).
3. Listar comportamientos esperados (ej.: "crear refund", "auditar intento", "notificar cliente").
4. Registrar los tres grupos internamente para usar en el Paso 3.

### Paso 3: Formular ACs en formato Given/When/Then

Para cada comportamiento identificado, formular uno o más ACs en el formato:

```
AC-{N}: {título corto}
  Dado que {precondición observable}
  Cuando {acción o evento}
  Entonces {resultado observable y medible}
```

**Reglas para ACs:**
- Cada AC debe ser **testeable** — si no hay forma de escribir una prueba, reescribirlo.
- Cada AC cubre **un comportamiento**, no múltiples.
- ACs numerados secuencialmente desde `AC-1`, sin saltos.
- Cubrir casos felices, casos de error relevantes y bordes (ej.: idempotencia, concurrencia cuando aplica).

### Paso 4: Resolver incógnitas con preguntas al usuario

1. Para cada item en "Riesgos e incógnitas" del brief, formular pregunta objetiva al usuario.
2. Preguntas en lote (hasta 5 por ronda) para no cansar al usuario.
3. Registrar respuestas recibidas; si el usuario no puede responder ahora, marcar el AC correspondiente como `PENDIENTE` e incluir en la sección "Preguntas Pendientes" del documento final.
4. No inventar respuestas — si algo queda pendiente, queda explícitamente pendiente.

### Paso 5: Definir DoD y out-of-scope

1. **Definition of Done** — checklist objetivo:
   - Todos los ACs con prueba correspondiente (trazabilidad `AC-N`)
   - Gate 2 aprobado
   - Documentación en `docs/issues/issue-{n}/` completa
   - ADR(s) creados si hubo decisión arquitectónica relevante
   - PR aprobado por al menos 1 revisor

2. **Out of scope** — lista explícita de lo que **no** se hará en esta iteración:
   - Extraer del brief y de la interacción con el usuario
   - Cada item out-of-scope debe tener justificación o link a issue futura

### Paso 6: Persistir en `docs/issues/issue-{n}/02-requirements.md`

Estructura del documento:

```markdown
# Requisitos — Issue #{n}: {título}

- **Referencia:** [Brief de la Fase 1](./01-brief.md)
- **Fecha:** {YYYY-MM-DD}

## Criterios de Aceptación

### AC-1: {título corto}

- **Dado** {precondición}
- **Cuando** {acción}
- **Entonces** {resultado}

### AC-2: {título corto}

...

## Definition of Done

- [ ] Todos los ACs arriba tienen al menos una prueba con marcación `AC-N`
- [ ] Gate 2 (`kata-quality-gate`) aprobado
- [ ] Documentación completa en `docs/issues/issue-{n}/`
- [ ] ADR(s) creados si aplica en `docs/adr/`
- [ ] PR aprobado por al menos 1 revisor

## Out of Scope

- **{Item 1}:** {justificación o link a issue futura}
- **{Item 2}:** {justificación o link a issue futura}

## Preguntas Pendientes

- [ ] {Pregunta 1} — esperando respuesta de @{usuario}
- [ ] {Pregunta 2} — esperando respuesta de @{usuario}

## Siguiente fase

Fase 3: diseño arquitectónico (`kata-architecture-brief`).
```

### Paso 7: Actualizar checkpoint

1. Actualizar `.ahrena/workflow/issue-{n}/checkpoint.md` con:
   - fase completada: 2
   - siguiente fase: 3
   - referencia: `docs/issues/issue-{n}/02-requirements.md`
   - número total de ACs
   - preguntas pendientes (si hay)
2. Informar a `warrior-athena`.

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Documento de requisitos | Markdown con ACs numerados | `docs/issues/issue-{n}/02-requirements.md` |
| Checkpoint actualizado | Markdown | `.ahrena/workflow/issue-{n}/checkpoint.md` |
| Preguntas al usuario (si hay) | Texto estructurado | Respuesta al orquestador |

## Restricciones

- **Los ACs deben ser testeables:** no aceptar ACs vagos ("el sistema debe ser rápido"); siempre con métrica observable.
- **Numeración continua:** `AC-1`, `AC-2`, `AC-3`... sin saltos; ACs removidos quedan como `AC-N: (removido — ver nota)` para preservar numeración en iteraciones.
- **Sin inferencia de requisitos no documentados:** si no está en el brief ni fue confirmado por el usuario, queda en "Preguntas Pendientes".
- **Destino fijo:** `docs/issues/issue-{n}/02-requirements.md` (según `lex-issue-driven`).

## Referencias

- `lex-issue-driven` — leyes del flujo
- `codex-issue-workflow` — estructura del flujo y convención de trazabilidad
- `kata-issue-analysis` — kata predecesor (Fase 1)
- `kata-architecture-brief` — kata sucesor (Fase 3)
