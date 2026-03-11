# Lexis: Definición Canónica de los Pilares

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Estructura y validación de artefatos del framework Ahrena

## Propósito

El Ahrena organiza todo el conocimiento en cinco Pilares: Lexis, Codex, Katas, Warriors y Cries. Para que el framework sea autocontenido y autovalidable, es necesario que las definiciones y las reglas de cada Pilar sean explícitas e inquebrantables. Sin una Ley que defina qué es cada Pilar y qué puede o no hacer cada uno, no hay criterio objetivo para validar artefatos ni para garantizar consistencia entre creación, invocación y evolución del framework.

Esta Lexis existe para establecer las **definiciones y reglas canónicas de los cinco Pilares**, de forma que todo artefato pueda ser validado contra ella y toda invocación respete la jerarquía y las relaciones entre Pilares.

## Ley

> **Todo artefato del framework Ahrena DEBE pertenecer a exactamente un Pilar y DEBE satisfacer la definición y las reglas canónicas de ese Pilar establecidas en esta Lexis. Toda invocación entre artefatos DEBE respetar las reglas de invocación definidas en esta Lexis.**

### Identificación del Pilar por prefijo

La forma segura de identificar si un artefato es Lexis, Codex, Kata, Warrior o Cry es **observar el prefijo definido en la directiva**: el agente DEBE consultar `naming.prefixes` en `.ahrena/.directives` y usar los valores allí configurados (claves `lexis`, `codex`, `katas`, `warriors`, `cries`) para validar nombres y clasificar artefatos. El agente NO DEBE asumir que los prefijos serán siempre valores fijos (ej. `lex-`, `codex-`); quien define es el usuario o el proyecto en `.directives`.

## Reglas por Pilar

### 1. Lexis

- **Definición:** Lexis es ley inquebrantable; no admite excepción.
- **Prefijo obligatorio:** el valor definido en `naming.prefixes.lexis` en `.ahrena/.directives`. Quien define el prefijo es el usuario/proyecto; el agente identifica que un artefato es Lexis observando si el nombre del archivo usa el prefijo configurado para ese Pilar.
- **Estructura:** DEBE seguir el template oficial del Pilar (`paths.samples.lexis` en `.directives`).
- **Autoridad:** Lexis rige todos los demás Pilares; ningún artefato puede contradecir una Lexis.
- **Invocación:** Lexis no es invocada por Cries; es consultada por Codex, Katas y Warriors.

### 2. Codex

- **Definición:** Codex es manual de referencia; organiza conocimiento para orientar decisiones.
- **Prefijo obligatorio:** el valor definido en `naming.prefixes.codex` en `.ahrena/.directives`. La identificación del Pilar se hace por el prefijo configurado, no por valor fijo.
- **Estructura:** DEBE seguir el template oficial del Pilar (`paths.samples.codex`).
- **Papel:** Informa a Katas y Warriors; no se ejecuta directamente (no se invoca como procedimiento).
- **Invocación:** Codex no es invocado por Cries; es consultado por Katas y Warriors.

### 3. Katas

- **Definición:** Kata es procedimiento repetible (habilidad) que aplica Lexis y consulta Codex para ejecutar una tarea clara y reproducible.
- **Prefijo obligatorio:** el valor definido en `naming.prefixes.katas` en `.ahrena/.directives`. La identificación del Pilar se hace por el prefijo configurado.
- **Estructura:** DEBE seguir el template oficial del Pilar (`paths.samples.katas`).
- **Dependencia:** Kata aplica Lexis y consulta Codex; no contiene lógica que contradiga Lexis ni ignora Codex aplicable.
- **Invocación:** Kata es invocado por Cries (directamente o vía Warrior) o por Warriors.

### 4. Warriors

- **Definición:** Warrior es agente especializado que orquesta uno o más Katas y puede consultar Lexis y Codex.
- **Prefijo obligatorio:** el valor definido en `naming.prefixes.warriors` en `.ahrena/.directives`. La identificación del Pilar se hace por el prefijo configurado.
- **Estructura:** DEBE seguir el template oficial del Pilar (`paths.samples.warriors`).
- **Papel:** Orquesta Katas (selecciona, ordena, combina resultados); puede consultar Lexis y Codex.
- **Invocación:** Warrior es invocado por Cries o por usuarios; no es invocado por otro Warrior como artefato formal (salvo que el Cry instruya al agente a asumir el papel de otro Warrior).

### 5. Cries

- **Definición:** Cry es comando de ejecución de alto nivel que activa habilidades o agentes.
- **Prefijo obligatorio:** el valor definido en `naming.prefixes.cries` en `.ahrena/.directives`. La identificación del Pilar se hace por el prefijo configurado.
- **Estructura:** DEBE seguir el template oficial del Pilar (`paths.samples.cries`).
- **Regla de invocación (inquebrantable):** Cry **NO PUEDE** invocar Lexis. Cry **NO PUEDE** acceder a Codex directamente. Cry **SOLO** invoca Katas y/o Warriors.
- **Relación:** Un Cry puede invocar un Kata (relación uno a uno) o uno o más Warriors (uno a muchos). Si un Cry necesita invocar múltiples Katas, DEBE existir un Warrior que orqueste esos Katas.

## Jerarquía de autoridad

1. **Lexis** — autoridad máxima; no puede ser contradicha.
2. **Codex** — fuente de verdad para conocimiento; orienta a Katas y Warriors.
3. **Katas** — ejecutan aplicando Lexis y consultando Codex.
4. **Warriors** — orquestran Katas; consultan Lexis y Codex.
5. **Cries** — disparan Katas o Warriors; nunca Lexis ni Codex.

## Alcance

- **Se aplica a:** todo artefato creado o mantenido en el framework Ahrena y toda cadena de invocación (Cry → Warrior/Kata → Kata → Lex/Codex).
- **Agentes vinculados:** todos los Warriors y agentes genéricos que crean, validan o invocan artefatos del framework.
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de violación

1. **Artefato inválido:** artefato que no satisface la definición de su Pilar no debe ser aceptado en el framework; debe ser corregido o reclasificado.
2. **Invocación inválida:** Cry que invoque Lexis o acceda a Codex directamente viola la Ley; el diseño del Cry debe ser corregido para delegar a Kata o Warrior.
3. **Remediación:** el agente o revisor debe consultar `lex-pilars` y `codex-pilars` para validar el artefato y la cadena de invocación y corregir desvíos.

## Ejemplos

### Correcto

- Cry `cry-translate` invoca al Warrior `warrior-translator`, que ejecuta el Kata `kata-translate`; el Kata consulta Lexis y Codex de traducción.
- Cry `cry-new-lex` invoca el Kata `kata-create-lexis`; el Kata consulta `codex-lexis` y el template de Lexis; no hay invocación de Lexis por el Cry.

### Incorrecto

- Cry cuyo prompt instruye al agente a "leer la lex-directives y aplicar" sin invocar un Kata o Warrior que encapsule ese procedimiento — la lectura de la Lex es uso por el Kata/Warrior, no "invocación" del Cry a la Lex; el Cry debe invocar un Kata o Warrior. (Si el Cry solo dispara un Kata que a su vez consulta Lexis, es correcto.)
- Artefato nombrado `guide-api.md` sin el prefijo del Pilar Codex (definido en `naming.prefixes.codex`) en el directorio de codex — viola naming.

## Validación automatizada

- **Herramienta:** verificación por el agente o revisor con base en `lex-pilars` y `codex-pilars`; posible extensión futura con script de validación de naming y de referencias.
- **Momento:** en la creación de artefato (kata-create-*), en la revisión de PR y en la validación de Cries.
- **Métrica:** 0 artefatos fuera de la definición de su Pilar; 0 Cries que invoquen Lexis o accedan a Codex directamente.

## Referencias

- `codex-pilars` — Referencia central de los Pilares y listas de validación por Pilar
- `codex-pilars` — Referencia central del sistema de Pilares y relaciones
- `.ahrena/.directives` — Prefijos y paths (naming.prefixes, paths.samples)
- `lex-template-usage` — Uso obligatorio del template por Pilar
