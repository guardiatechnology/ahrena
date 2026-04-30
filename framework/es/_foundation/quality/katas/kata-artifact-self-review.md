# Kata: Auto-revisión de Artefacto

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Auto-revisión pre-humana de cualquier artefacto producido por agente — Lexis, Codex, Kata, Warrior, Cry, PRD, Capability Spec, ADR, plan de release, PLR, wireframes

## Objetivo

Antes de someter cualquier artefacto a revisión humana, el agente que produjo el artefacto DEBE ejecutar este Kata para detectar defectos comunes: placeholders olvidados, contradicciones internas, ambigüedades cuantificables, scope drift, secciones vacías, vocabulario fuera del tono Guardia, divergencia entre versiones multilingües.

La auto-revisión reduce iteración con humano (corrige defectos obvios antes de la revisión) y fortalece la salida entregada. Inspirado en el patrón Spec Self-Review del skill `brainstorming` en [obra/superpowers](https://github.com/obra/superpowers).

## Cuándo Usar

- Antes de someter artefacto nuevo (Lexis, Codex, Kata, Warrior, Cry) a `kata-push-to-framework` o revisión humana
- Antes de cerrar PRD, Capability Spec, ADR
- Antes de cerrar plan de release o PLR
- Antes de que cualquier warrior orquestador entregue paquete a un Gate humano

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Artefacto a revisar | Sí | Path absoluto o relativo al archivo Markdown |
| Tipo del artefacto | Sí | Uno de: `lexis`, `codex`, `kata`, `warrior`, `cry`, `prd`, `capability-spec`, `adr`, `release-plan`, `plr`, `wireframe-lf`, `wireframe-hf`, `insights`, `otro` |
| Template de referencia | No | Path al sample correspondiente cuando el tipo tiene template canónico |

## Workflow

```
Progreso:
- [ ] 1. Scan de placeholders
- [ ] 2. Scan de contradicciones internas
- [ ] 3. Scan de ambigüedades cuantificables
- [ ] 4. Scan de scope drift
- [ ] 5. Scan de secciones vacías y estructura incompleta
- [ ] 6. Scan de tono y vocabulario
- [ ] 7. Verificación de equivalencia multilingüe (cuando aplicable)
- [ ] 8. Reporte consolidado
```

### Paso 1: Scan de placeholders

Busque marcadores no completados: `TBD`, `TODO`, `FIXME`, `XXX`, texto entre corchetes intencional del template (`[Nombre de la Ley]`, `[descripción]`), elipsis en contenido declarativo, strings genéricas (`Lorem ipsum`, `placeholder`, `insertar aquí`), headings vacíos.

Para cada hallazgo: ubicación (línea), contenido problemático, acción (completar / eliminar / convertir en open question).

### Paso 2: Scan de contradicciones internas

Verifique consistencia entre secciones:
- Ley/Objetivo en la apertura vs. Reglas/Workflow en las secciones siguientes
- Ejemplos "Correcto" e "Incorrecto" alineados con las reglas
- Inputs/outputs vs. Workflow — ¿cada input declarado es consumido? ¿cada output es producido?
- Criterios numerados — ¿N en la Ley coinciden con N en Validación Automatizada?

### Paso 3: Scan de ambigüedades cuantificables

Identifique declaraciones vagas: "muchos", "varios", "rápido", "simple", "complejo", "razonable", "alta latencia", "bajo costo".

Para cada uno: alternativa cuantificable (ej.: "muchos casos" → "≥80% de los casos observados"; "rápido" → "p99 ≤ 300ms"). Excepción: ambigüedad aceptable cuando el número vendrá en fase posterior — documentar la postergación.

### Paso 4: Scan de scope drift

Verifique que el artefacto no haya excedido su alcance:
- Lexis: ¿trata de una única ley? ¿no incrusta kata o codex?
- Capability Spec: ¿sigue las 8 secciones rígidas? ¿no invade diseño técnico?
- Kata: ¿describe UN procedimiento?
- Warrior: ¿orquesta pero no ejecuta?
- PRD: ¿se enfoca en WHAT/WHY?

### Paso 5: Scan de secciones vacías y estructura incompleta

Verifique conformidad con el template canónico (cuando exista):
- ¿Todas las secciones obligatorias están presentes?
- ¿Cada sección tiene contenido sustantivo?
- ¿Jerarquía de headings correcta?
- ¿Frontmatter completo (cuando aplicable a `.cursor/` o `.claude/`)?
- ¿Los enlaces internos resuelven (no 404)?

### Paso 6: Scan de tono y vocabulario

Verifique conformidad con [lex-tone](framework/es/_foundation/quality/lexis/lex-tone.md) y — cuando público — [lex-brand-voice](framework/es/design/brand/lexis/lex-brand-voice.md):
- Buzzwords prohibidas: "innovador", "disruptivo", "transformador", "revolucionario", "fintech" (para Guardia)
- Verbos modales RFC 2119 correctos: MUST/MUST NOT/SHOULD/MAY (en) o DEVE/NÃO DEVE/DEVERIA/PODE (pt-BR), DEBE/NO DEBE/DEBERÍA/PUEDE (es)
- Términos canónicos preservados: Lexis, Codex, Katas, Warriors, Cries, Ahrena

### Paso 7: Verificación de equivalencia multilingüe

Cuando el artefacto exista en múltiples idiomas (per [lex-framework-language](framework/es/_foundation/i18n/lexis/lex-framework-language.md)):
- Misma estructura y orden de secciones
- Mismo número de reglas numeradas
- Tablas con mismo número de filas
- Bloques de código (HARD-GATE, ejemplos) preservados sin traducción incorrecta de tag/sintaxis
- Términos canónicos preservados

### Paso 8: Reporte consolidado

```markdown
# Self-Review Report — {nombre del artefacto}

> **Reviewer:** kata-artifact-self-review · **Date:** YYYY-MM-DD · **Type:** {tipo}
> **Resultado:** APROBADO | DEVUELTO PARA CORRECCIÓN

## Hallazgos por categoría

### 1. Placeholders
- (vacío cuando 0 hallazgos)
- {línea N}: {descripción} → acción: {recomendación}

### 2. Contradicciones internas
### 3. Ambigüedades cuantificables
### 4. Scope drift
### 5. Secciones vacías / estructura
### 6. Tono y vocabulario
### 7. Equivalencia multilingüe

## Decisión

- [ ] APROBADO — puede someter para revisión humana
- [ ] DEVUELTO — corregir hallazgos arriba y re-ejecutar este Kata
```

Someta el artefacto al humano SOLO cuando el reporte indique APROBADO.

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Self-Review Report | Markdown estructurado | inline (chat) o `docs/.review/{artefacto}-{date}.md` |
| Decisión APROBADO / DEVUELTO | Boolean explícito | parte del reporte |

## Ejemplo de Ejecución

### Input

```
Artefacto: framework/es/_foundation/quality/lexis/lex-hard-gate-pattern.md
Tipo: lexis
Template: framework/templates/lex-sample.md
```

### Output

```markdown
# Self-Review Report — lex-hard-gate-pattern.md

> **Reviewer:** kata-artifact-self-review · **Date:** 2026-04-30 · **Type:** lexis
> **Resultado:** APROBADO

## Hallazgos por categoría

### 1. Placeholders
- (cero hallazgos)

### 2. Contradicciones internas
- (cero hallazgos)

### 3. Ambigüedades cuantificables
- (cero hallazgos — métricas declaradas tienen criterio verificable)

### 4. Scope drift
- (cero hallazgos)

### 5. Secciones vacías / estructura
- (cero hallazgos — sigue lex-sample.md)

### 6. Tono y vocabulario
- (cero hallazgos — RFC 2119 correctos; sin buzzwords)

### 7. Equivalencia multilingüe
- (cero hallazgos — pt-BR, en, es estructuralmente equivalentes)

## Decisión

- [x] APROBADO — puede someter para revisión humana
```

## Restricciones

- Este Kata **detecta**, no **corrige** — la corrección es responsabilidad del agente que produjo el artefacto.
- La auto-revisión **no reemplaza** la revisión humana — es fase pre-humana, complementaria.
- Si el artefacto falla en equivalencia multilingüe, el agente DEBE alinear todos los idiomas antes de someter — no someter parcialmente.
- Siempre que retorne DEVUELTO, el reporte DEBE ser preservado en `docs/.review/` para auditoría.
