# Lexis: Formato Gherkin Declarativo Obligatorio

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Ingeniería — Calidad. Formato y estilo de redacción de todo escenario Gherkin producido para validación BDD.

## Propósito

Un escenario acoplado a un selector de UI queda obsoleto en el siguiente rediseño y deja de describir comportamiento. Un escenario con `status code 201` prueba el protocolo, no la regla de negocio. BDD existe para proteger **la intención del comportamiento** (lenguaje ubicuo), no para duplicar pruebas unitarias o de contrato con prosa alrededor.

Esta Lexis existe para que **un escenario sobreviva a refactores de implementación** y **comunique inequívocamente el comportamiento esperado a cualquier lector de negocio o de ingeniería**.

## Ley

> **Todo escenario Gherkin producido para validación BDD DEBE seguir Gherkin declarativo estricto: estructurado con `Feature`/`Background`/`Scenario`/`Scenario Outline` usando pasos `Given`/`When`/`Then`/`And`; escrito en lenguaje de negocio (lenguaje ubicuo); libre de selectores de UI, status codes HTTP, nombres de función, nombres de tabla/columna, rutas de archivo y cualquier otro detalle de implementación. Los escenarios imperativos que narran clics de UI o artefactos técnicos están PROHIBIDOS. Cada escenario DEBE ser independiente (sin dependencia de orden de ejecución) y etiquetado con al menos una etiqueta de AC (`@AC-{N}`) y una etiqueta de tipo (`@happy-path` | `@alternative` | `@edge` | `@error` | `@nfr`).**

## Reglas

### 1. Estructura obligatoria

Cada archivo de escenarios **DEBE** contener:

```gherkin
# language: es (o en/pt-BR según el idioma elegido)
Característica: <título en lenguaje de negocio>

  Antecedentes:
    Dado que <precondición compartida de negocio>

  @AC-1 @happy-path
  Escenario: SCN-1 <comportamiento de negocio en una frase>
    Dado que <estado inicial>
    Cuando <acción de negocio>
    Entonces <resultado observable>

  @AC-2 @edge
  Esquema del escenario: SCN-2 <variación parametrizada>
    Dado que el saldo es <saldo>
    Cuando el usuario solicita <valor>
    Entonces el sistema responde con <resultado>

    Ejemplos:
      | saldo | valor | resultado          |
      | 100   | 50    | aprobado           |
      | 100   | 200   | rechazado por saldo |
```

La primera línea **PUEDE** declarar el idioma del Gherkin (`# language: es`); en su ausencia se asume `en`.

### 2. Lenguaje ubicuo, no técnico

Los pasos describen **lo que el negocio observa**, no cómo lo ejecuta el sistema.

| Permitido (declarativo) | Prohibido (imperativo/técnico) |
|---|---|
| "el cliente solicita un reembolso de $ 50,00" | "POST /api/refunds con payload {amount: 5000}" |
| "el sistema rechaza el reembolso como duplicado" | "la respuesta tiene status code 409" |
| "el cliente recibe confirmación de que la transferencia fue programada" | "el e-mail es enviado por la función `send_email_async`" |
| "el saldo disponible es insuficiente" | "la columna `available_balance` tiene valor < amount" |
| "la operación queda registrada en el historial del cliente" | "se inserta una fila en `audit_log`" |

### 3. Patrones prohibidos dentro de `Given`/`When`/`Then`

El lint **DEBE** rechazar escenarios que contengan:

- Selectores CSS/XPath: `#id`, `.clase`, `input[name=...]`, `//div[...]`
- Verbos de UI: "hace clic", "completa el campo", "espera el selector", "desplaza hasta"
- Métodos HTTP y status: `POST`, `GET`, `PUT`, `DELETE`, `200`, `201`, `400`, `404`, `409`, `500`
- Nombres de función/método: `calcula_fee()`, `processPayment(...)`, cualquier identificador con paréntesis
- Nombres de tabla/columna en snake_case o referencia SQL: `SELECT ... FROM`, `INSERT INTO`, `UPDATE ... SET`
- Rutas de archivo o módulo: `src/`, `app/`, `.py`, `.ts`, `.java`
- Headers HTTP, payloads JSON literales, bytes, hashes

### 4. Identificación y trazabilidad

Cada `Scenario` o `Scenario Outline` **DEBE**:

1. Tener un id único `SCN-{N}` en el título (o en un comentario inmediatamente arriba).
2. Tener al menos una etiqueta `@AC-{N}` referenciando un criterio de aceptación numerado en `02-requirements.md`.
3. Tener exactamente una etiqueta de tipo: `@happy-path`, `@alternative`, `@edge`, `@error` o `@nfr`.

Esta tripla (id + AC + tipo) es lo que `kata-bdd-validate-implementation` usa para mapear escenarios a las pruebas.

### 5. Independencia

Los escenarios del mismo archivo **NO PUEDEN** depender del orden de ejecución. Cada escenario parte del estado declarado en `Background` más su propio `Given`. Un escenario que asume "después del escenario anterior, ..." es una violación.

### 6. `Background` solo para precondición de negocio

`Background` **DEBE** declarar precondiciones compartidas en lenguaje de negocio (ej.: "Dado un cliente activo en la cartera X"). El setup técnico (base vacía, cola purgada, mock configurado) **NO PUEDE** aparecer en `Background` — pertenece al código de prueba, no al escenario.

### 7. Idioma del Gherkin

El idioma de los pasos sigue `language.default` en `.ahrena/.directives` para proyectos cuyo equipo habla ese idioma. Proyectos multi-equipo **PUEDEN** escribir escenarios en `en`. El idioma elegido **DEBE** ser consistente dentro del mismo archivo `.feature` (o `07-bdd-scenarios.md`).

## Alcance

- **Aplica a:** todo archivo `.feature` o `07-bdd-scenarios.md` producido en la Fase 8 del flujo Issue-Driven; también aplica a escenarios BDD producidos fuera del flujo (p. ej. discovery de dominio).
- **Agentes vinculados:** `warrior-themis` (produce), cualquier agente que edite escenarios, `kata-bdd-scenarios-design`, `kata-bdd-validate-implementation`.
- **Excepciones:** Ninguna. Los escenarios que fallan el formato se regeneran, no se parchean.

## Consecuencias de Violación

1. **Bloqueo del Gate 3:** `kata-quality-gate` Check 8 falla cuando el lint de escenarios encuentra patrones prohibidos o etiquetas ausentes.
2. **Escenario descartado:** los escenarios imperativos se regeneran a partir de las fuentes de especificación (per `lex-bdd-spec-only-sources`), no se reparan.
3. **Erosión de valor:** los escenarios acoplados a la implementación envejecen mal, se vuelven deuda y entrenan al equipo a ignorarlos — bloquear en el gate previene que ese hábito se instale.

## Ejemplos

### Correcto

```gherkin
# language: es
Característica: Programación de transferencia

  Antecedentes:
    Dado un cliente activo con cuenta corriente en la cartera "Operacional"

  @AC-1 @happy-path
  Escenario: SCN-1 El cliente programa una transferencia válida
    Dado que el saldo disponible es $ 1.000,00
    Cuando el cliente programa una transferencia de $ 100,00 para mañana
    Entonces la transferencia queda registrada como programada
    Y el cliente recibe confirmación con la fecha de ejecución prevista

  @AC-2 @error
  Escenario: SCN-2 El cliente intenta programar una transferencia sin saldo
    Dado que el saldo disponible es $ 50,00
    Cuando el cliente intenta programar una transferencia de $ 100,00
    Entonces el sistema rechaza la programación por saldo insuficiente
    Y ninguna transferencia queda registrada
```

### Incorrecto

```gherkin
Característica: Programación de transferencia

  Escenario: Éxito
    Dado un POST en /api/transfers con {"amount": 10000, "scheduled_for": "2026-04-30"}
    Cuando el usuario hace clic en #btn-confirm
    Entonces la respuesta tiene status code 201
    Y la columna status en la tabla transfers es "scheduled"
```

Violaciones: status code, método HTTP, payload JSON, selector de UI, nombre de tabla y columna, ausencia de `@AC-{N}` y etiqueta de tipo, ausencia de id `SCN-{N}`, ausencia de comportamiento de negocio observable.

## Validación Automatizada

- **Herramienta:** lint de escenarios (regex set) que rechaza los patrones prohibidos enumerados en la Regla 3; verificación obligatoria de etiquetas `@AC-{N}` + etiqueta de tipo en cada escenario; revisión manual en el Gate 3 (`kata-quality-gate` Check 8).
- **Momento:** al guardar `07-bdd-scenarios.md` en `kata-bdd-scenarios-design` y nuevamente en el Gate 3 antes de `kata-pr-prepare`.
- **Métrica:** 0 escenarios que contengan patrones técnicos prohibidos; 100% de los escenarios con etiqueta `@AC-{N}` y etiqueta de tipo; 100% de los escenarios con id `SCN-{N}` único.

## Referencias

- `lex-bdd-spec-only-sources` — fuentes permitidas para derivar los escenarios
- `lex-bdd-no-framework-coupling` — implementación de las pruebas sin framework BDD
- `codex-bdd` — principios de BDD en Guardia
- `codex-gherkin` — manual del Gherkin adoptado en Guardia
- `kata-bdd-scenarios-design` — procedimiento de producción de los escenarios
