# Lexis: Patrón HARD-GATE para Bloqueos en Lexis

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Sintaxis de bloqueos textuales en Lexis del framework Ahrena

## Propósito

Las Lexis frecuentemente requieren bloqueo de flujo: acciones prohibidas, precondiciones no negociables, gates que no admiten excepción. Sin sintaxis canónica, el `MUST` textual es fácil de ignorar — los humanos racionalizan ("este caso es diferente"), los agentes interpretan ambiguamente.

Esta Lexis establece el **bloque `<HARD-GATE>` literal** como sintaxis canónica para hacer los bloqueos inequívocos. El bloque enumera explícitamente: (a) sujeto prohibido, (b) acción en infinitivo, (c) precondiciones numeradas, (d) alcance de aplicabilidad, (e) anti-pretextos comunes, (f) excepciones declaradas (o "Ninguna").

Inspirado en el [patrón HARD-GATE textual](https://github.com/obra/superpowers) usado en skills del framework `obra/superpowers`.

## Ley

> **Toda Lexis que requiera bloqueo de flujo — acción prohibida con precondiciones no negociables — DEBE contener un bloque `<HARD-GATE>` literal explicitando sujeto, acción, precondiciones, alcance, anti-pretextos y excepciones. Las Lexis que declaran "MUST" textual sin este bloque, cuando hay bloqueo efectivo, son consideradas incompletas y DEBEN ser revisadas para incluirlo.**

## Reglas

### 1. Cuándo aplicar HARD-GATE

Aplique cuando la Lexis:

- Bloquea acción concreta (crear issue, mergear PR, iniciar rollout, deployar agente)
- Tiene precondiciones verificables programáticamente o por checklist
- No admite excepciones implícitas o negociables caso por caso

NO aplique cuando la Lexis:

- Define solo convención (nomenclatura, casing) — basta el `MUST` textual
- Tiene múltiples excepciones legítimas y contextuales sin checklist único
- Describe atributo cualitativo sin acción concreta de bloqueo

### 2. Sintaxis canónica

```
<HARD-GATE>
{Sujeto} NO MAY {acción prohibida en infinitivo} {objetivo de la acción}
sin que {precondición mínima inicial}.

Precondiciones obligatorias:
  (a) {condición 1 — específica y verificable}
  (b) {condición 2 — específica y verificable}
  (c) {condición 3 — específica y verificable}
  ...

Esta regla se aplica a {alcance: TODA feature / agentes de la plataforma / etc.},
independientemente de:
  - {anti-pretexto 1 — ej: tamaño percibido}
  - {anti-pretexto 2 — ej: urgencia declarada}
  - {anti-pretexto 3 — ej: confianza del equipo}

Excepción {única / declarada}: {descripción literal o "Ninguna"}.
</HARD-GATE>
```

Los 6 elementos (sujeto, acción, precondiciones, alcance, anti-pretextos, excepción) son **obligatorios**. Omitir cualquiera produce bloqueo débil.

### 3. Posicionamiento en la Lexis

El bloque `<HARD-GATE>` DEBE estar:

- **Después** de la sección `Ley` (o sección `Reglas` cuando exista), y antes de `Ejemplos`
- Dentro de bloque de código fenced, con tag `HARD-GATE` literal en las líneas de apertura y cierre
- En la **misma sección** que define los criterios verificados — no en apéndice o nota al pie

### 4. Anti-pretextos

La lista `independientemente de` enumera de 2 a 4 racionalizaciones comunes que los humanos invocan para saltarse la ley. Forzarlas en el texto hace que el pretexto sea explícito y más difícil de usar.

Ejemplos canónicos de anti-pretextos:

- "tamaño percibido ('esto es trivial')"
- "urgencia ('es un incendio')"
- "quién solicitó ('el CEO pidió')"
- "confianza del equipo ('ya probamos mucho')"
- "presión de plazo"
- "tiempo ajustado de release"

### 5. Excepciones declaradas

Cuando exista excepción legítima, ella DEBE estar dentro del bloque `<HARD-GATE>` con:

- Tag explícito (ej: `incident:p0`, `prototype/*`, `sandbox`)
- Compensación retroactiva cuando aplicable (ej: "DoR retroactivo en hasta 5 días")
- Justificación que **no** sea pretexto disfrazado

Las excepciones implícitas o negociables caso por caso son FORBIDDEN en el bloque. Si la Lexis admite múltiples excepciones no enumerables, ella no es candidata a HARD-GATE — es Lexis declarativa convencional.

### 6. Aplicabilidad multilingüe

Las Lexis traducidas (per [lex-framework-language](framework/es/_foundation/i18n/lexis/lex-framework-language.md)) DEBEN tener el bloque `<HARD-GATE>` traducido **en todos los idiomas en `language.i18n`**, manteniendo equivalencia estructural — mismas precondiciones, mismos anti-pretextos, mismas excepciones.

El tag `<HARD-GATE>` en sí **no es traducido** — es literal en los 3 idiomas. Solo el contenido dentro del bloque se localiza.

## Alcance

- **Aplica a:** todas las Lexis del framework Ahrena que bloquean acción concreta
- **Agentes vinculados:** todos los agentes que crean o modifican Lexis (humanos y IA), incluyendo Hécate cuando ella exista
- **Excepciones:** Lexis declarativas (sin bloqueo efectivo) quedan fuera del alcance; pueden ser refinadas en revisiones futuras si se identifica necesidad de bloqueo

## Consecuencias de Violación

1. **Detección en revisión de PR:** revisor humano o linter (a desarrollar) identifica cláusula de bloqueo sin bloque `<HARD-GATE>` correspondiente
2. **PR rechazado:** Lexis nueva o modificada con cláusula de bloqueo sin el patrón no pasa la revisión
3. **Remediación:** actualizar la Lexis aplicando el patrón en los 3 idiomas soportados (`pt-BR`, `en`, `es`); inclusión en la próxima ronda de sync de `.cursor/` y `.claude/`

## Ejemplos

### Correcto

Lexis aplicando HARD-GATE textual completo:

```markdown
## Ley

> Toda issue de feature MUST cumplir DoR canónico antes de existir.

<HARD-GATE>
warrior-athena NO MAY iniciar flujo Issue-Driven sin que
kata-dor-validate retorne ✅ en TODOS los 9 criterios.

Precondiciones obligatorias:
  (a) Discovery referenciada (docs/discovery/{topic}/insights.md)
  (b) PRD en docs/product/{feature}/prd.md aprobado
  (c) Capability Spec en docs/product/{feature}/capability-spec.md aprobado
  (d) Paquete técnico aprobado por Mômos
  (e) Wireframes aprobados cuando UI
  (f) ACs numeradas presentes
  (g) Métricas leading + lagging declaradas
  (h) Dependencias mapeadas
  (i) Búsqueda anti-duplicación ejecutada

Esta regla se aplica a TODA feature, independientemente de:
  - tamaño percibido ("esto es trivial")
  - urgencia ("es un incendio")
  - quién solicitó ("el CEO pidió")

Excepción única: hotfix con label `incident:p0` — exige
DoR retroactivo en hasta 5 días.
</HARD-GATE>
```

### Incorrecto

Bloqueo implícito sin sintaxis canónica:

```markdown
## Ley

> Toda issue de feature MUST cumplir DoR antes de existir.
> warrior-athena rechaza issues incompletas.
```

Problemas:
- "rechaza issues incompletas" es vago — no enumera las precondiciones
- No declara alcance ("TODA feature" vs. subconjunto)
- No enumera anti-pretextos
- No declara excepciones

Resultado: los humanos invocan "este caso es diferente"; los agentes interpretan ambiguamente.

## Validación Automatizada

- **Herramienta:** revisión de PR humana mientras no exista linter dedicado; futuramente `kata-design-validation` aplicado por warrior-momos parametrizado para tipo `lexis` debe verificar la presencia y conformidad del bloque
- **Momento:** revisión de PR de toda Lexis nueva o modificada
- **Métrica:** 100% de las Lexis con cláusula de bloqueo tienen bloque `<HARD-GATE>` correspondiente en los 3 idiomas (`language.i18n`)
