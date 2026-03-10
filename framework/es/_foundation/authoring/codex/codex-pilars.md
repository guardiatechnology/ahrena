# Codex: Sistema de Pilares de Ahrena

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Creación, validación y evolución de artefactos del framework

## Visión General

Este Codex es la referencia central sobre el sistema de Pilares de Ahrena. Describe la naturaleza de cada Pilar, cómo se relacionan entre sí, cómo validar artefatos y cómo el framework utiliza sus propios artefatos para evolucionar — el concepto de autosuficiencia. Operacionaliza la `lex-pilars` con criterios verificables y checklists de validación por Pilar. Para documentación detallada de cada Pilar (cómo escribir bien, criterios de calidad), consulte los Codex específicos: `codex-lexis`, `codex-codex`, `codex-katas`, `codex-warriors`, `codex-cries`.

## Contexto

- **Dominio:** Taxonomía, arquitectura y validación del framework Ahrena
- **Público objetivo:** Agentes de IA que crean o validan artefatos; mantenedores del framework; revisores de PR
- **Actualización:** Siempre que se cree un nuevo Pilar, cambien las relaciones entre Pilares o se altere la `lex-pilars`

## Contenido

### Los Cinco Pilares

Ahrena organiza todo el conocimiento en cinco Pilares, cada uno con un papel distinto. El prefijo de cada Pilar es el valor definido en `naming.prefixes` en `.ahrena/.directives` (claves: `lexis`, `codex`, `katas`, `warriors`, `cries`); quien define es el usuario o el proyecto.

| Pilar | Clave en naming.prefixes | Naturaleza | Pregunta que responde |
|-------|--------------------------|------------|----------------------|
| **Lexis** | `lexis` | Ley inquebrantable | "¿Qué está prohibido u obligatorio?" |
| **Codex** | `codex` | Manual de referencia | "¿Qué se necesita saber sobre este dominio?" |
| **Katas** | `katas` | Procedimiento repetible | "¿Cómo se ejecuta esta tarea paso a paso?" |
| **Warriors** | `warriors` | Agente especializado | "¿Quién es responsable de este dominio?" |
| **Cries** | `cries` | Comando recurrente | "¿Cómo se invoca esta acción rápidamente?" |

### Jerarquía de Autoridad

Los Pilares poseen una jerarquía implícita de autoridad:

1. **Lexis** — autoridad máxima. Ningún otro artefato puede contradecir una Lexis. Son absolutas.
2. **Codex** — fuente de verdad para conocimiento de dominio. Orienta decisiones.
3. **Katas** — procedimientos que obedecen Lexis y consultan Codex.
4. **Warriors** — agentes que siguen Lexis, consultan Codex y ejecutan Katas.
5. **Cries** — atajos que disparan Katas o invocan Warriors.

### Relaciones entre Pilares

```
Lexis ─────────── gobierna ─────────► todos los demás
Codex ─────────── informa ──────────► Katas, Warriors
Katas ─────────── ejecutado por ────► Warriors, agentes genéricos
Warriors ─────── invocado por ──────► Cries, usuarios
Cries ──────────── dispara ─────────► Katas (vía Warriors o directamente)
```

Cada Pilar puede referenciar artefatos de otros Pilares:

| Pilar | Referencia | Es referenciado por |
|-------|------------|--------------------|
| Lexis | — | Codex, Katas, Warriors |
| Codex | Lexis | Katas, Warriors |
| Katas | Lexis, Codex | Warriors, Cries |
| Warriors | Lexis, Codex, Katas | Cries |
| Cries | Katas, Warriors | — |

**Reglas de invocación (resumen):**

| De (quien invoca) | Puede invocar / acceder |
|-------------------|-------------------------|
| Cry | Solo Kata(s) y/o Warrior(s) |
| Warrior | Kata(s); puede consultar Lexis y Codex |
| Kata | Ningún artefato como "invocación"; aplica Lexis y consulta Codex |

### Kit de Creación

Para que el framework sea autosuficiente, cada Pilar posee un **Kit de Creación** compuesto por:

| Pieza | Pilar | Función |
|-------|-------|---------|
| Codex del Pilar | Codex | Conocimiento sobre qué es y cómo escribir bien |
| Kata de creación | Kata | Procedimiento paso a paso para crear un nuevo artefato |
| Cry de invocación | Cry | Atajo rápido para disparar la creación |

La cadena de ejecución es:

```
/cry-new-{pilar} → kata-create-{pilar} → codex-{pilar} + template + lexis
```

### Cómo Decidir qué Pilar Usar

| Situación | Pilar | Justificación |
|-----------|-------|---------------|
| Se necesita establecer una regla absoluta que nadie puede violar | **Lexis** | Las leyes no admiten excepciones |
| Se necesita documentar conocimiento de dominio para consulta | **Codex** | Base de conocimiento estructurada |
| Se necesita estandarizar cómo se ejecuta una tarea recurrente | **Kata** | Procedimiento con inputs, pasos y outputs |
| Se necesita un agente dedicado con identidad y alcance | **Warrior** | Especialista con persona y responsabilidades |
| Se necesita un atajo rápido para una acción del día a día | **Cry** | Invocación rápida de 1-2 pasos |

Preguntas de refinamiento:

- **¿Es una restricción absoluta?** → Lexis
- **¿Es conocimiento para consulta?** → Codex
- **¿Es un procedimiento de múltiples pasos?** → Kata
- **¿Necesita persona y alcance continuo?** → Warrior
- **¿Es una invocación simple y rápida?** → Cry

### Estándares y Convenciones

| Aspecto | Estándar | Ejemplo |
|---------|----------|---------|
| Nomenclatura de archivo | `{prefijo}-{nombre}.md` (prefijo en `naming.prefixes`) | Conforme `.directives` |
| Casing | kebab-case | `codex-framework-language.md` |
| Direccionamiento | `{lang}/{clade}/{subclade}/{pilar}/{archivo}` | `pt-BR/engineering/quality/lexis/lex-code-review.md` |
| Creación dual | framework (`.md`) + IDE (formato de la plataforma) | `.md` + `.mdc` (Cursor) |

### Restricciones Técnicas

- Todo artefato **DEBE** seguir el template oficial de su Pilar (`paths.samples` en `.directives`)
- Todo artefato **DEBE** existir en los idiomas definidos en `language.i18n`
- El idioma predeterminado (`language.default`) es la fuente de verdad
- Los nombres de archivo usan el prefijo del Pilar definido en `naming.prefixes` y kebab-case
- Los términos canónicos (Lexis, Codex, Katas, Warriors, Cries, Clade, Subclade, Pilar) nunca se traducen

---

### Validación de artefatos

Consulte siempre la `lex-pilars` como Ley; los criterios siguientes operacionalizan la validación.

**Cómo validar:**

1. **Identificar el Pilar pretendido** del artefato (por nombre, directorio o declaración del autor).
2. **Consultar la `lex-pilars`** para las reglas inquebrantables de ese Pilar.
3. **Aplicar el checklist** siguiente para el Pilar correspondiente.
4. **Verificar relaciones de invocación:** si el artefato es un Cry, confirmar que solo invoca Kata(s) y/o Warrior(s); si es un Kata, confirmar que aplica Lexis y Codex; si es un Warrior, confirmar que orquesta Katas.

#### Lexis

**Definición en una frase:** Lexis es ley inquebrantable que rige el framework; no admite excepción.

| Criterio | Obligatorio |
|----------|-------------|
| Nombre del archivo usa el prefijo definido en `naming.prefixes.lexis` (consultar `.directives`) y kebab-case | Sí |
| Contiene sección **Ley** con declaración imperativa (DEBE/NO PUEDE) | Sí |
| Contiene sección **Alcance** y **Excepciones: Ninguna** (o equivalente) | Sí |
| Estructura sigue el template oficial (paths.samples.lexis) | Sí |
| No es invocada por Cry como "acción" — Cry invoca Kata/Warrior que consultan Lexis | Sí |

**No conformidad:** Archivo de Lexis que describe recomendación en vez de obligación; Lexis con cláusula de excepción; Cry cuyo flujo incluye "invocar" o "ejecutar" una Lexis directamente.

**Ejemplo válido:** `lex-directives` — declara que todo agente DEBE leer `.ahrena/.directives`; sin excepciones; consultada por otros artefatos, no invocada por Cry.

#### Codex

**Definición en una frase:** Codex es manual de referencia que organiza conocimiento para orientar decisiones; es consultado, no ejecutado.

| Criterio | Obligatorio |
|----------|-------------|
| Nombre del archivo usa el prefijo definido en `naming.prefixes.codex` (consultar `.directives`) y kebab-case | Sí |
| Contiene **Visión general**, **Contexto** y **Contenido** (o equivalente al template) | Sí |
| Naturaleza es referencia/consulta; no describe procedimiento de ejecución paso a paso como foco principal | Sí |
| Estructura sigue el template oficial (paths.samples.codex) | Sí |
| No es invocado por Cry como "acción" — Cry invoca Kata/Warrior que consultan Codex | Sí |

**No conformidad:** Artefato de Codex que es en la práctica un procedimiento numerado (debería ser Kata); Cry que "lee" o "aplica" un Codex directamente como única acción, en vez de invocar un Kata/Warrior.

**Ejemplo válido:** `codex-lexis` — manual de cómo escribir buenas Lexis; consultado por `kata-create-lexis`; no es invocado por Cry.

#### Katas

**Definición en una frase:** Kata es procedimiento repetible que aplica Lexis y consulta Codex para ejecutar una tarea con entradas, pasos y salidas definidos.

| Criterio | Obligatorio |
|----------|-------------|
| Nombre del archivo usa el prefijo definido en `naming.prefixes.katas` (consultar `.directives`) y kebab-case | Sí |
| Contiene objetivo, contexto de aplicación, entradas, proceso (pasos) y salidas (o equivalente al template) | Sí |
| Referencia Lexis y/o Codex aplicables en la sección de Referencias o en el cuerpo | Sí |
| Es invocado por Cries y/o Warriors; no invoca otro Kata directamente como "comando" (Warrior orquesta múltiples Katas) | Sí |
| Estructura sigue el template oficial (paths.samples.katas) | Sí |

**No conformidad:** Artefato de Kata sin pasos claros o sin referencia a Lex/Codex; Cry que ejecuta lógica detallada sin delegar a un Kata.

**Ejemplo válido:** `kata-create-lexis` — pasos numerados; consulta `codex-lexis` y template; invocado por `cry-new-lex`.

#### Warriors

**Definición en una frase:** Warrior es agente especializado que orquesta uno o más Katas y puede consultar Lexis y Codex; tiene identidad (persona) y alcance definidos.

| Criterio | Obligatorio |
|----------|-------------|
| Nombre del archivo usa el prefijo definido en `naming.prefixes.warriors` (consultar `.directives`) y kebab-case | Sí |
| Contiene identidad (nombre, dominio), responsabilidades y Katas que orquesta (o equivalente al template) | Sí |
| Referencia al menos una Lexis (en general `lex-directives`) y Codex/Katas aplicables | Sí |
| Es invocado por Cries o usuarios; orquesta Katas (no sustituye la definición de un Kata) | Sí |
| Estructura sigue el template oficial (paths.samples.warriors) | Sí |

**No conformidad:** Artefato de Warrior que no orquesta ningún Kata; Cry que invoca un Warrior inexistente o que describe lógica que debería estar en un Kata.

**Ejemplo válido:** `warrior-translator` — orquesta `kata-translate`; consulta Lexis y Codex de i18n; invocado por `cry-translate`.

#### Cries

**Definición en una frase:** Cry es comando de ejecución de alto nivel que invoca solo Katas y/o Warriors; nunca invoca Lexis ni accede a Codex directamente.

| Criterio | Obligatorio |
|----------|-------------|
| Nombre del archivo usa el prefijo definido en `naming.prefixes.cries` (consultar `.directives`) y kebab-case | Sí |
| Documenta claramente qué Kata y/o qué Warrior(es) es/son invocado(s) | Sí |
| No contiene instrucción para "invocar" o "ejecutar" una Lexis | Sí |
| No contiene instrucción para "aplicar" o "leer" un Codex como acción única del comando (el Codex es consultado por el Kata/Warrior invocado) | Sí |
| Si invoca múltiples Katas, hay un Warrior que orquesta esos Katas o el Cry describe el orden y delega a un Warrior | Sí |
| Estructura sigue el template oficial (paths.samples.cries) | Sí |

**No conformidad:** Cry cuyo prompt dice "lea la lex-X y aplique"; Cry que "consulte el codex-Y y haga X" sin invocar un Kata o Warrior que encapsule esa consulta y acción.

**Ejemplo válido:** `cry-new-lex` — invoca `kata-create-lexis`; el Kata, a su vez, consulta `codex-lexis` y Lexis. El Cry no accede a Codex ni Lexis directamente.

---

### Artefactos en el proyecto (.ahrena)

Los artefatos pueden crearse primero en el **espacio del proyecto** (`.ahrena/artifacts/`), específicos de ese repositorio. Así se puede iterar y validar antes de incorporarlos al framework canónico.

| Aspecto | Proyecto (`.ahrena/artifacts/`) | Framework (`framework/`) |
|---------|--------------------------------|--------------------------|
| **Uso** | Específico del proyecto; validación local | Parte del repositorio Ahrena; compartido |
| **Estructura** | Igual que el framework: `{lang}/{clade}/{subclade}/{pilar}/{prefijo}-{nombre}.md` | `framework/{lang}/{clade}/{subclade}/{pilar}/` |
| **Idiomas** | Puede existir solo en el idioma por defecto; al hacer Push, se generan los demás si faltan | **DEBE** existir en todos los idiomas de `language.i18n` |
| **Cuándo crear aquí** | Reglas o procedimientos aún en validación; artefatos que quizá no pasen al framework | Artefatos estables y aprobados para el framework |

**Flujo recomendado:**

1. **Crear en el proyecto:** use los Katas de creación (`kata-create-lexis`, `kata-create-codex`, etc.) con destino **proyecto** — el artefato se guarda en `.ahrena/artifacts/{lang}/{clade}/{subclade}/{pilar}/`.
2. **Sincronizar .cursor local:** ejecute `python .ahrena/update.py --sync-cursor` (o `make sync-cursor`). El update regenera `.cursor/` a partir de `.ahrena/framework/` y `.ahrena/artifacts/`.
3. **Validar y comparar (opcional):** use `kata-diff-artifacts --local` para ver diferencias entre `.ahrena/artifacts` y `framework/` local; use `kata-diff-artifacts --remote` para comparar con la versión más reciente del framework en el remoto.
4. **Push al framework:** ejecute `kata-push-to-framework` (o `cry-push-to-framework`) con **--local** (copia a `framework/` en el repo actual) o **--remote** (sincronización con el repositorio del framework en GitHub).
5. **Actualizar instalación:** ejecute `python .ahrena/update.py` (y opcionalmente `--sync-cursor`) para traer la versión más reciente del framework.

**Push: modo local y modo remoto**

- **Local:** el repo actual contiene (o tiene acceso a) la carpeta `framework/`. Push = copiar `.ahrena/artifacts/` a `paths.framework`, completar i18n y opcionalmente eliminar del proyecto. No usa red.
- **Remoto:** en proyecto consumidor, el framework está en GitHub. Push = enviar cambios al repositorio del framework usando **obligatoriamente el MCP de GitHub** (branch, push, apertura de PR). El agente **DEBE** usar las herramientas MCP de GitHub para todas las operaciones remotas.

La ruta canónica del espacio de proyecto se define en `paths.project_artifacts` en `.ahrena/.directives` (valor por defecto: `.ahrena/artifacts/`).

## Glosario

| Término | Definición |
|---------|-----------|
| Pilar | Una de las cinco categorías de artefato de Ahrena |
| Clade | Primer nivel de organización temática (ej: engineering, documentation) |
| Subclade | Segundo nivel de organización dentro de un Clade (ej: quality, i18n) |
| Kit de Creación | Conjunto Codex + Kata + Cry que permite crear nuevos artefatos de un Pilar |
| Creación dual | Patrón de crear el artefato canónico (`.md`) y la versión derivada para la IDE |
| Direccionamiento | Ruta completa de un artefato en la taxonomía del framework |
| Artefactos de proyecto | Artefactos creados en `.ahrena/artifacts/`, específicos del repositorio, antes de incorporarse al framework |
| Push al framework | Procedimiento (kata-push-to-framework) que incorpora artefatos de `.ahrena/artifacts/` al framework, en modo **local** (copia a `framework/` en el repo) o **remoto** (sincronización con el repositorio del framework en GitHub). |
| Diff de artefatos | Procedimiento (kata-diff-artifacts) que compara `.ahrena/artifacts` y framework en modo **local** (vs framework local) o **remoto** (vs versión más reciente del framework en el remoto). |
| Validación de Pilar | Verificación de que un artefato satisface la definición y los criterios del Pilar al que pertenece |
| Cadena de invocación | Secuencia Cry → (Warrior) → Kata; Lexis y Codex son consultados, no invocados por el Cry |
| Definición canónica | Definición establecida en la `lex-pilars` y operacionalizada en este Codex |

## Referencias

- `lex-pilars` — Ley que define canónicamente los cinco Pilares y las reglas de invocación (fuente de verdad para validación)
- `.ahrena/.directives` — Directivas canónicas del framework (paths, naming.prefixes)
- `lex-template-usage` — Ley de uso obligatorio de templates
- `lex-framework-language` — Ley de estructura de idiomas
- `codex-lexis`, `codex-codex`, `codex-katas`, `codex-warriors`, `codex-cries` — Documentación detallada de cada Pilar (cómo escribir bien, criterios de calidad)
