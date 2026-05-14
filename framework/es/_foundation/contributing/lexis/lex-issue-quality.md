# Lexis: Requisitos de Calidad del Issue

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Todos los issues en repositorios Guardia

## Ley

> **Todo issue en un repositorio Guardia DEBE usar una de las plantillas aprobadas (feature-request, epic, user-story-for-api, user-story-for-frontend, tech-task, bug, plan), DEBE tener al menos una etiqueta de la lista aprobada que corresponda a su tipo, DEBE tener un GitHub Issue Type definido (Feature, Task, Bug, Epic) compatible con la plantilla usada, DEBE responder explícitamente: por qué (motivación e impacto), qué (objetivo y alcance) y cómo (enfoque de implementación o definición de listo), y — para todo issue no-Epic — DEBE llevar la etiqueta `status: todo` inmediatamente tras la creación. El assignee se captura en la transición `todo → development` por `warrior-athena` (per `lex-agent-planning`), NO en el momento de la creación: los issues en `status: todo` PUEDEN permanecer sin assignee. No se PUEDE crear ninguna rama ni abrir ningún PR para un issue que no cumpla estos requisitos.**

## Cobertura

- **Se aplica a:** todos los issues en todos los repositorios Guardia.
- **Agentes vinculados:** desarrolladores, agentes de IA (warrior-athena, warrior-apollo, warrior-hephaestus, warrior-eunomia) que crean o validan issues.
- **Excepciones:** issues generados automáticamente por Dependabot o herramientas de análisis de seguridad, que siguen su propio formato. Cualquier otra excepción requiere justificación explícita registrada en el propio issue.

## Reglas

### 1. Plantillas aprobadas

Todo issue DEBE usar una de las siguientes plantillas (ubicadas en `.ahrena/contributing_templates/`):

| Plantilla | Cuándo usar |
|-----------|-------------|
| `feature-request` | Nueva funcionalidad, nuevo comportamiento, nueva capacidad orientada al usuario |
| `epic` | Iniciativa grande que agrupa múltiples historias o funcionalidades |
| `user-story-for-api` | Funcionalidad de backend orientada a API, con criterios de aceptación y especificación |
| `user-story-for-frontend` | Funcionalidad de UI/UX para la plataforma o app |
| `bug` | Reporte de defecto en comportamiento existente; reproducción + impacto + corrección esperada |
| `tech-task` | Tarea pequeña y bien definida: chore, refactorización, mantenimiento, corrección de documentación, cambio de CI |
| `plan` | Sub-issue de Plan ejecutable bajo un Issue padre (User Story / Bug / Tech Task), per `lex-agent-planning` |

Los issues sin plantilla son incompletos y DEBEN actualizarse antes de que cualquier rama o PR pueda referenciarlos.

### 2. Etiquetas obligatorias

Todo issue DEBE tener al menos una etiqueta aplicada. La etiqueta DEBE corresponder al tipo del issue:

| Plantilla | Etiquetas obligatorias |
|-----------|------------------------|
| `feature-request` | `feature request ➕` |
| `epic` | `epic` |
| `user-story-for-api` | `api`, `user story 🎯` |
| `user-story-for-frontend` | `frontend`, `user story 🎯` |
| `bug` | `bug 🐛` |
| `tech-task` | Al menos una de: `documentation 📃`, `ci 🏗️`, `enhancement 🔝`, `evolvability ♻️` |
| `plan` | `plan 📋` (más etiquetas heredadas del contexto del Issue padre cuando aplicable) |

### 3. GitHub Issue Type obligatorio

Todo issue DEBE tener un **GitHub Issue Type** definido (campo nativo de GitHub, distinto de las etiquetas). El tipo DEBE corresponder a la plantilla usada:

| Plantilla | Issue Type |
|-----------|------------|
| `feature-request` | `Feature` |
| `epic` | `Epic` |
| `user-story-for-api` | `Feature` |
| `user-story-for-frontend` | `Feature` |
| `bug` | `Bug` |
| `tech-task` | `Task` |
| `plan` | `Task` |

> Las organizaciones que personalizan los Issue Types (ej. `Tech Task` en lugar de `Task`, `Plan` como tipo propio) DEBEN mantener la equivalencia semántica. El mapeo canónico de esta Lex usa los nombres nativos de GitHub.

Cuando el issue se crea via formulario de plantilla (`.github/ISSUE_TEMPLATE/*.yml`), el tipo se aplica automáticamente por el campo `type:` de la plantilla. Cuando el issue se crea via CLI (`gh issue create`), el agente DEBE aplicar el tipo después de la creación:

```bash
# Después de crear el issue, aplicar el tipo via API REST
gh api -X PATCH "repos/$OWNER/$REPO/issues/$ISSUE_NUMBER" -f type=Task
```

Los issues sin Issue Type definido NO cumplen esta Lex y bloquean la creación de rama/PR.

### 4. El assignee NO es requisito de creación

Un issue en `status: todo` PUEDE permanecer sin assignee. El assignee captura **quién asume la ejecución** del trabajo y se aplica en la transición `todo → development` por `warrior-athena` (per HARD-GATE de ejecución de `lex-agent-planning`):

```bash
# Quien toma el trabajo aplica el assignee en la transición:
gh issue edit $ISSUE_NUMBER \
  --add-assignee "@me" \
  --remove-label "status: todo" \
  --add-label "status: development"
```

Casos en que el assignee PUEDE aplicarse ya en la creación:
- Issue creado con intención declarada de ejecución inmediata por el propio autor.
- Issue derivado de incidente cuyo on-call ya está designado.

En todos los demás casos, mantener sin assignee hasta `todo → development` es el camino canónico — evita el ruido de "ownership fantasma" en issues que quedan días en la pila sin nadie realmente comprometido.

### 5. Contenido obligatorio: Por qué / Qué / Cómo

Todo issue DEBE responder tres preguntas, de forma explícita o a través de las secciones de la plantilla:

| Pregunta | Qué cubre | Mapeo en la plantilla |
|----------|-----------|-----------------------|
| **Por qué** | Motivación, impacto, problema que se resuelve | "Why is this important?" / sección "Why" |
| **Qué** | Objetivo, alcance, qué cambia | "Objective" / sección "What" |
| **Cómo** | Enfoque de implementación, resultado esperado, definición de listo | "How should it work?" / sección "How" |

Para `tech-task`, `bug` y `plan`: las tres preguntas son las secciones directas de la plantilla.

Para las demás plantillas: las secciones se mapean a estas preguntas — el **Objective** (user story) responde Qué, **Why is this important** responde Por qué, y **How can it be implemented** / criterios de aceptación responden Cómo.

### 6. `status: todo` es invariante de creación (no-Epic)

Todo issue **no-Epic** DEBE llevar la etiqueta `status: todo` inmediatamente tras ser creado. Epic se descompone en child Issues y no participa del Eje A de `lex-issue-status` — ver `lex-issue-status` Regla 7.

La etiqueta se aplica de una de tres formas:

1. **Via plantilla `.github/ISSUE_TEMPLATE/*.yml`**: el campo `labels:` de la plantilla declara `status: todo` y GitHub la aplica en la submisión. Camino canónico para creación via UI.
2. **Via `kata-contributing-issue` (CLI/MCP)**: el kata aplica `status: todo` como paso final, después de aplicar el type y las etiquetas de la plantilla.
3. **Manualmente tras `gh issue create`**:
   ```bash
   gh issue edit $ISSUE_NUMBER --add-label "status: todo"
   ```

Los issues en el flujo Issue-Driven sin `status: todo` (excluyendo Epic) violan esta Lex y bloquean cualquier transición subsiguiente — no hay "limbo" entre creación y `todo`.

### 7. Los agentes siguen las mismas reglas

Los agentes de IA que crean issues (via MCP o CLI) DEBEN:

1. Usar la plantilla adecuada mediante `kata-contributing-issue`
2. Aplicar las etiquetas obligatorias durante la creación
3. Aplicar el Issue Type correspondiente a la plantilla
4. Para issues no-Epic, aplicar la etiqueta `status: todo` como paso final de la creación
5. Completar todas las secciones obligatorias (Por qué / Qué / Cómo) antes de enviar

El assignee se omite deliberadamente de esta lista — es responsabilidad de la transición `todo → development`, ejecutada por `warrior-athena` per `lex-agent-planning`.

### 8. Rama y PR bloqueados hasta que el issue cumpla los requisitos

Según `lex-issue-first` y `lex-git-branches`, no se PUEDE crear ninguna rama ni abrir ningún PR si el issue asociado:

- No usa una de las plantillas aprobadas
- No tiene al menos una etiqueta obligatoria
- No tiene Issue Type definido
- No lleva `status: todo` (excluyendo Epic)
- No responde Por qué, Qué y Cómo

Nótese que **el assignee no está en esta lista** — se exige en la transición `todo → development`, no en la creación.

## HARD-GATE (creación)

Conforme [`lex-hard-gate-pattern`](framework/es/_foundation/quality/lexis/lex-hard-gate-pattern.md), el bloqueo textual de creación de esta Lex se expresa canónicamente como:

```
<HARD-GATE>
warrior-athena, warrior-apollo, warrior-hephaestus, warrior-eunomia y
cualquier otro agente NO DEBE crear rama ni abrir PR para un issue
sin que ella satisfaga TODOS los criterios canónicos:

  (a) Usa una de las plantillas aprobadas (feature-request, epic,
      user-story-for-api, user-story-for-frontend, tech-task, bug, plan)
  (b) Tiene al menos una etiqueta obligatoria correspondiente a la plantilla
  (c) Tiene GitHub Issue Type definido (Feature, Task, Bug, Epic)
      compatible con la plantilla
  (d) Lleva la etiqueta `status: todo` (no-Epic) inmediatamente tras
      la creación
  (e) Responde explícitamente Por qué, Qué y Cómo

Esta regla se aplica a TODA issue, independientemente de:
  - tamaño percibido ("es un cambio trivial")
  - urgencia ("incendio en producción")
  - quién solicitó ("el CEO pidió")
  - confianza del equipo ("ya probamos")

Excepción única declarada: issues generadas automáticamente por
Dependabot o herramientas de escaneo de seguridad siguen su propio
formato y están exentas. Toda otra excepción exige justificación
explícita registrada en la propia issue.
</HARD-GATE>
```

## HARD-GATE (transición `todo → development`)

La captura del assignee — anteriormente exigida en el gate de creación — pasa a exigirse en la transición que señaliza compromiso real de ejecución. Esta Lex declara el gate; `lex-agent-planning` lo invoca operacionalmente.

```
<HARD-GATE>
warrior-athena y cualquier otro agente NO DEBE transicionar un issue
no-Epic de `status: todo` a `status: development` sin aplicar
al menos un assignee en la misma operación.

Precondiciones obligatorias para aplicar la transición:
  (a) Estado de origen es `status: todo`
  (b) Estado de destino es `status: development`
  (c) Al menos un assignee se añade en la misma operación
      (`gh issue edit --add-assignee` o MCP equivalente)
  (d) Issue no es Epic (Epic no participa del Eje A — ver
      `lex-issue-status` Regla 7)

Esta regla se aplica a TODA transición `todo → development`,
independientemente de:
  - tamaño percibido ("es un cambio trivial")
  - urgencia ("incendio en producción")
  - quién solicitó ("el CEO pidió")
  - confianza del equipo ("ya probamos")

Excepción declarada: Ninguna. El assignee es invariante en la entrada
a `development`.
</HARD-GATE>
```

## Ejemplos

### Correctos

```
Issue: "Añadir kata-setup-gpg-signing al framework de contribución"
Plantilla: tech-task
Etiquetas: documentation 📃, status: todo
Issue Type: Task
Assignee: (vacío — se aplicará en todo → development)
Por qué: Los contribuidores necesitan configurar la firma GPG para cumplir lex-signed-commits; aún no existe una guía paso a paso.
Qué: Crear kata-setup-gpg-signing que cubra instalación de GPG, generación de clave, configuración de git y exportación a GitHub.
Cómo: Seguir el flujo de generación de clave GPG; cubrir macOS, Linux y Windows; añadir paso de verificación.
```

```
# Transición todo → development (assignee aplicado en la misma operación)
gh issue edit 42 \
  --add-assignee "@me" \
  --remove-label "status: todo" \
  --add-label "status: development"
```

### Incorrectos

```
Issue: "arreglar el bug de autenticación"
Plantilla: ninguna
Etiquetas: ninguna
Contenido: una sola línea, sin Por qué / Qué / Cómo

→ ❌ Creación de rama bloqueada por lex-git-branches
→ ❌ PR rechazado por lex-issue-first
→ ❌ Falla precondición (a), (b), (c), (d), (e) del HARD-GATE de creación
```

```
# ❌ Transición todo → development sin aplicar assignee
gh issue edit 42 --remove-label "status: todo" --add-label "status: development"
# Falla precondición (c) del HARD-GATE de transición — ejecución sin owner declarado
```

```
# ❌ Issue creado sin status: todo
gh issue create --title "feat: ..." --label "feature request ➕"
# Issue queda en limbo entre creación y el flujo — falla precondición (d) del gate de creación
```

## Validación Automatizada

- **Herramienta:** `kata-contributing-issue` aplica plantilla, etiquetas, Issue Type y `status: todo` en la creación; las plantillas `.github/ISSUE_TEMPLATE/*.yml` declaran `type:` y `labels:` para auto-aplicar Issue Type + `status: todo`; la lista de verificación del PR revisa que el issue asociado esté completo en todos los campos obligatorios; `kata-quality-gate` en el Gate 2 verifica la presencia de assignee en la transición `todo → development` registrada en el historial del issue.
- **Cuándo:** al crear el issue (via kata o plantilla); en la transición `todo → development` (exigencia del assignee); al crear el PR (via verificación de `lex-issue-first`).
- **Métrica:** 0 PRs abiertos que referencien un issue sin plantilla, etiquetas, Issue Type o `status: todo`; 0 transiciones `todo → development` sin assignee; 100% de los issues creados via kata en conformidad en el primer envío.
