# Codex: Gherkin en Guardia

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Ingeniería — Calidad. Subset de Gherkin adoptado, layout de archivos, etiquetas y patrones concretos para `07-bdd-scenarios.md` y `*.feature`.

## Visión General

Este Codex es el **manual operativo del Gherkin** en Guardia. Define exactamente qué palabras clave usamos, dónde viven los archivos, cómo se etiquetan y qué patrones aplicar para cada tipo de escenario. Junto con `lex-bdd-gherkin-format`, es lo que `warrior-themis` consulta línea por línea al escribir escenarios.

## Contexto

- **Dominio:** sintaxis Gherkin aplicada a la Fase 8 del flujo Issue-Driven.
- **Público:** `warrior-themis`, autores y revisores de `07-bdd-scenarios.md` o `*.feature`.
- **Actualización:** cuando los patrones de escenario se vuelven repetitivos (oportunidad de nueva plantilla), cuando los linters detectan nuevos anti-patterns frecuentes, cuando el stack de pruebas cambia y afecta la convención de nomenclatura.

## Contenido

### 1. Subset adoptado

Usamos un subset acotado. Todo lo que esté fuera de esta lista **no es aceptado** en revisión:

| Adoptado | Uso |
|---|---|
| `Feature:` (`Característica:`) | Encabezado del bloque; nombre como frase nominal |
| `Background:` (`Antecedentes:`) | Precondición de negocio compartida |
| `Scenario:` (`Escenario:`) | Comportamiento concreto |
| `Scenario Outline:` (`Esquema del escenario:`) + `Examples:` (`Ejemplos:`) | Escenario paramétrico |
| `Given` (`Dado`) / `When` (`Cuando`) / `Then` (`Entonces`) | Pasos principales |
| `And` (`Y`) / `But` (`Pero`) | Continuación del paso anterior |
| Doc strings `"""..."""` | Solo cuando el paso necesita texto largo (ej.: mensaje que recibe el cliente) |
| Data tables `| col | col |` | Solo para datos de ejemplo paramétricos |
| Etiquetas `@AC-{N}`, `@happy-path`, etc. | Trazabilidad y taxonomía |
| Comentarios `# ...` | Para id `SCN-{N}` cuando no esté en el título |

| Excluido | Por qué |
|---|---|
| `Rule:` | Introduce jerarquía que no usamos; agrupa vía Feature o etiquetas |
| `*` como paso libre | Reduce la claridad del rol del paso (Given/When/Then) |
| Custom keywords / extensiones | Cada plugin acoplaría a un runner — prohibido por `lex-bdd-no-framework-coupling` |

### 2. Layout de archivos

**Estándar (preferido):** consolidado en `07-bdd-scenarios.md`.

```
docs/
└── issues/
    └── issue-42/
        ├── 01-brief.md
        ├── 02-requirements.md
        ├── 03-architecture.md
        ├── 07-bdd-scenarios.md      ← consolidado
        └── 08-bdd-validation-report.md
```

**El volumen justifica split:** cuando hay > 3 Features o > 30 escenarios en la misma issue, separar:

```
docs/issues/issue-42/
├── 07-bdd-scenarios.md              ← índice + frontmatter
└── scenarios/
    ├── transfer-scheduling.feature
    ├── transfer-cancellation.feature
    └── transfer-execution.feature
```

En ese caso, `07-bdd-scenarios.md` contiene solo el frontmatter y la lista de archivos `.feature`.

### 3. Frontmatter de `07-bdd-scenarios.md`

YAML obligatorio en el tope del archivo, declarando origen y cobertura:

```yaml
---
issue: 42
repo: guardiafinance/ahrena
generated_at: "2026-04-29T14:00:00Z"
generated_by: warrior-themis
sources:
  github_issue: "guardiafinance/ahrena#42"
  notion_pages:
    - "https://www.notion.so/page-id-1"
  flow_artifacts:
    - docs/issues/issue-42/01-brief.md
    - docs/issues/issue-42/02-requirements.md
    - docs/issues/issue-42/03-architecture.md
ac_coverage:
  - ac: AC-1
    scenarios: [SCN-1]
  - ac: AC-2
    scenarios: [SCN-2, SCN-3]
  - ac: AC-3
    scenarios: [SCN-4, SCN-5, SCN-6]
---
```

Rutas bajo `src/`, `app/`, `lib/`, `tests/` en `sources` invalidan el artefacto (per `lex-bdd-spec-only-sources`).

### 4. Idioma del bloque Gherkin

Primera línea del bloque Gherkin (después del frontmatter):

```gherkin
# language: es
```

Obligatorio cuando el idioma no es `en`. Consistente dentro del mismo archivo. Idiomas soportados: `pt-BR`, `es`, `en`. Para proyectos multi-equipo, `en` es el estándar pragmático.

### 5. Taxonomía de etiquetas

| Categoría | Etiquetas | Cantidad por escenario |
|---|---|---|
| AC | `@AC-1`, `@AC-2`, ... | **≥ 1** (obligatoria) |
| Tipo | `@happy-path` \| `@alternative` \| `@edge` \| `@error` \| `@nfr` | **exactamente 1** (obligatoria) |
| Área (opcional) | `@backend`, `@frontend`, `@mobile`, `@api`, `@worker` | 0..1 |
| Prioridad (opcional) | `@critical`, `@regression`, `@smoke` | 0..1 |

Las etiquetas van en **una línea inmediatamente arriba** del `Scenario:` o `Scenario Outline:`. Las etiquetas en la Feature aplican a todos los escenarios del archivo (ej.: `@backend` en el tope de la Feature evita repetición).

### 6. Id `SCN-{N}` — dónde colocarlo

**Preferido:** en el título del escenario.

```gherkin
@AC-1 @happy-path
Scenario: SCN-1 Cliente programa transferencia válida
```

**Aceptado:** en comentario inmediatamente arriba.

```gherkin
# SCN-1
@AC-1 @happy-path
Scenario: Cliente programa transferencia válida
```

Reglas:

- Único dentro del archivo.
- Estable: al editar el texto del escenario, el id permanece (mantiene la trazabilidad a la prueba).
- La numeración contigua no es obligatoria; `SCN-1`, `SCN-2`, `SCN-4` se acepta (`SCN-3` fue removido en revisión).

### 7. Uso de `Background`

`Background` declara **precondición de negocio** compartida por todos los escenarios del archivo.

**Bueno:**

```gherkin
Antecedentes:
  Dado un cliente activo con cuenta corriente en la cartera "Operacional"
  Y el cliente tiene el perfil de aprobador habilitado
```

**Malo:**

```gherkin
Antecedentes:
  Dada una base de datos Postgres limpia
  Y la cola de eventos fue purgada
  Y el servicio fue reiniciado
```

El setup técnico vive en el código de prueba (fixture, contenedor), no en el escenario. Per `lex-bdd-gherkin-format` Regla 6.

### 8. `Scenario Outline` — cuándo usar

Use **solo** cuando hay ≥ 3 variaciones paramétricas del mismo trío Given/When/Then.

**Bueno:**

```gherkin
@AC-2 @edge
Esquema del escenario: SCN-3 Límites de saldo en la programación
  Dado que el saldo disponible es $ <saldo>
  Cuando el cliente solicita una transferencia de $ <valor>
  Entonces el sistema responde con <resultado>

  Ejemplos:
    | saldo  | valor  | resultado                |
    | 100.00 | 50.00  | aprobación               |
    | 100.00 | 100.00 | aprobación               |
    | 100.00 | 100.01 | rechazo por saldo        |
    | 100.00 | 0.00   | rechazo por valor inválido |
```

**Malo:** 1 o 2 ejemplos en outline (use escenarios separados; outline con 1-2 filas es overhead sin ganancia).

Encabezados de la tabla de Examples en snake_case cortos. Valores monetarios con formato consistente ($ X.XX en es; R$ X,XX en pt-BR).

### 9. Convenciones de nomenclatura

| Elemento | Patrón | Ejemplo |
|---|---|---|
| Feature | Frase nominal capitalizada | `Característica: Programación de transferencia` |
| Scenario | `SCN-{N} <frase verbal en tercera persona>` | `Scenario: SCN-1 Cliente programa transferencia válida` |
| Steps | Tercera persona, voz activa, presente | `Cuando el cliente programa una transferencia` (no "Tú programas...") |
| Doc string | Comillas triples, indentación consistente | dentro del `Then` cuando hay que citar mensaje literal |
| Etiqueta | `@kebab-case` o `@AC-{N}` | `@happy-path`, `@AC-3` |

### 10. Patrones comunes

#### 10.1 Escenario negativo (`@error`)

Mismo `Given` del happy-path, `When` alterado, `Then` opuesto:

```gherkin
@AC-3 @error
Escenario: SCN-4 El cliente intenta programar sin saldo
  Dado que el saldo disponible es $ 50.00
  Cuando el cliente intenta programar una transferencia de $ 100.00
  Entonces el sistema rechaza la programación por saldo insuficiente
  Y ninguna transferencia queda registrada
```

#### 10.2 Escenario de borde (`@edge`)

`Given` con el valor exacto del borde:

```gherkin
@AC-3 @edge
Escenario: SCN-5 Saldo igual al monto más la tarifa
  Dado que el saldo disponible es $ 100.00
  Y la tarifa de transferencia es $ 1.00
  Cuando el cliente intenta programar una transferencia de $ 100.00
  Entonces el sistema rechaza la programación por saldo insuficiente
```

#### 10.3 Escenario NFR (`@nfr`)

Comportamiento observable de presupuesto, latencia, idempotencia:

```gherkin
@AC-4 @nfr
Escenario: SCN-6 Respuesta dentro del presupuesto de latencia
  Dado un cliente activo
  Cuando el cliente solicita el saldo disponible
  Entonces la respuesta se entrega en hasta 1 segundo
```

#### 10.4 Idempotencia (`@nfr`)

```gherkin
@AC-5 @nfr
Escenario: SCN-7 Reenvío de la misma programación no duplica
  Dado un cliente que ya programó la transferencia X
  Cuando el cliente reenvía exactamente la misma programación X
  Entonces el sistema retorna la misma programación previamente registrada
  Y ninguna transferencia adicional se crea
```

### 11. Anti-patterns (referencia cruzada)

Lista canónica de patrones prohibidos: `lex-bdd-gherkin-format` Regla 3. Resumen de los más frecuentes:

- Selectores de UI: `#id`, `.clase`, `input[name=...]`
- Métodos HTTP / status codes: `POST /api/...`, `status code 201`
- Nombres de función: `calcula_fee()`, `processPayment(...)`
- Nombres de tabla / SQL: `SELECT ...`, `INSERT INTO refunds`
- Rutas de archivo: `src/`, `app/`, `.py`, `.ts`
- JSON literal, headers HTTP, hashes

### 12. Lint — regex del verificador

Conjunto base usado por el lint (y por `warrior-themis` en la auto-revisión):

```
# prohibiciones
\b(POST|GET|PUT|DELETE|PATCH)\s+/        # método HTTP + path
\bstatus\s+code\s+\d+                    # status code numérico
\b\d{3}\b\s+(OK|Created|Bad Request)     # status nombrado
\b[a-z_][a-z0-9_]*\([^)]*\)              # nombres de función/método
SELECT\s+|INSERT\s+INTO|UPDATE\s+\w+\s+SET   # SQL
src/|app/|lib/|tests/|spec/              # rutas de implementación
#[a-zA-Z][\w-]+|\.[a-zA-Z][\w-]+         # selectores CSS
input\[[^\]]+\]                          # selector de atributo
\.(py|ts|tsx|js|jsx|java|go)\b           # extensión de archivo

# obligatorios (por escenario)
@AC-\d+                                  # ≥ 1
@(happy-path|alternative|edge|error|nfr) # exactamente 1
SCN-\d+                                  # único en el archivo
```

`warrior-themis` aplica este check antes de guardar `07-bdd-scenarios.md`. El PR que falle el lint queda bloqueado por el Gate 3 (`kata-quality-gate` Check 8).

### 13. Ejemplo completo

```yaml
---
issue: 42
repo: guardiafinance/ahrena
generated_at: "2026-04-29T14:00:00Z"
generated_by: warrior-themis
sources:
  github_issue: "guardiafinance/ahrena#42"
  notion_pages:
    - "https://www.notion.so/transfer-spec"
  flow_artifacts:
    - docs/issues/issue-42/01-brief.md
    - docs/issues/issue-42/02-requirements.md
    - docs/issues/issue-42/03-architecture.md
ac_coverage:
  - ac: AC-1
    scenarios: [SCN-1]
  - ac: AC-2
    scenarios: [SCN-2]
  - ac: AC-3
    scenarios: [SCN-3, SCN-4]
  - ac: AC-4
    scenarios: [SCN-5]
---
```

```gherkin
# language: es
@backend
Característica: Programación de transferencia

  Antecedentes:
    Dado un cliente activo con cuenta corriente en la cartera "Operacional"

  @AC-1 @happy-path
  Escenario: SCN-1 Cliente programa transferencia válida
    Dado que el saldo disponible es $ 1.000,00
    Cuando el cliente programa una transferencia de $ 100,00 para mañana
    Entonces la transferencia queda registrada como programada
    Y el cliente recibe confirmación con la fecha de ejecución prevista

  @AC-2 @alternative
  Escenario: SCN-2 Cliente programa usando perfil aprobador
    Dado que el cliente tiene el perfil de aprobador habilitado
    Y el saldo disponible es $ 1.000,00
    Cuando el cliente programa una transferencia de $ 100,00 con aprobación inmediata
    Entonces la transferencia queda registrada como programada y pre-aprobada

  @AC-3 @error
  Escenario: SCN-3 El cliente intenta programar sin saldo
    Dado que el saldo disponible es $ 50,00
    Cuando el cliente intenta programar una transferencia de $ 100,00
    Entonces el sistema rechaza la programación por saldo insuficiente
    Y ninguna transferencia queda registrada

  @AC-3 @edge
  Esquema del escenario: SCN-4 Límites del saldo en la programación
    Dado que el saldo disponible es $ <saldo>
    Cuando el cliente solicita una transferencia de $ <valor>
    Entonces el sistema responde con <resultado>

    Ejemplos:
      | saldo    | valor    | resultado                |
      | 100,00   | 100,00   | aprobación               |
      | 100,00   | 100,01   | rechazo por saldo        |
      | 0,00     | 1,00     | rechazo por saldo        |

  @AC-4 @nfr
  Escenario: SCN-5 Respuesta dentro del presupuesto de latencia
    Dado un cliente activo
    Cuando el cliente solicita el saldo disponible
    Entonces la respuesta se entrega en hasta 1 segundo
```

## Referencias

- `lex-bdd-spec-only-sources` — fuentes permitidas
- `lex-bdd-gherkin-format` — formato declarativo (ley aplicada por este Codex)
- `lex-bdd-no-framework-coupling` — sin step-runner
- `codex-bdd` — principios de BDD en Guardia
- `kata-bdd-scenarios-design` — producción de escenarios
- `kata-bdd-validate-implementation` — validación escenario↔prueba
- [Cucumber: Gherkin Reference](https://cucumber.io/docs/gherkin/reference/)
