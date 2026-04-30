# Lexis: Requisitos de Calidad del Issue

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Todos los issues en repositorios Guardia

## Ley

> **Todo issue en un repositorio Guardia DEBE usar una de las plantillas aprobadas (feature-request, epic, user-story-for-api, user-story-for-frontend, simple-task), DEBE tener al menos una etiqueta de la lista aprobada que corresponda a su tipo, DEBE tener un GitHub Issue Type definido (Feature, Task, Bug, Epic) compatible con la plantilla usada, DEBE tener al menos un assignee — por defecto el autor del issue —, y DEBE responder explícitamente: por qué (motivación e impacto), qué (objetivo y alcance) y cómo (enfoque de implementación o definición de listo). No se PUEDE crear ninguna rama ni abrir ningún PR para un issue que no cumpla estos requisitos.**

## Cobertura

- **Se aplica a:** todos los issues en todos los repositorios Guardia.
- **Agentes vinculados:** desarrolladores, agentes de IA (warrior-athena, warrior-apollo, warrior-hephaestus) que crean o validan issues.
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
| `simple-task` | Tarea pequeña y bien definida: chore, refactorización, mantenimiento, corrección de documentación, cambio de CI |

Los issues sin plantilla son incompletos y DEBEN actualizarse antes de que cualquier rama o PR pueda referenciarlos.

### 2. Etiquetas obligatorias

Todo issue DEBE tener al menos una etiqueta aplicada. La etiqueta DEBE corresponder al tipo del issue:

| Plantilla | Etiquetas obligatorias |
|-----------|------------------------|
| `feature-request` | `feature request ➕` |
| `epic` | `epic` |
| `user-story-for-api` | `api`, `user story 🎯` |
| `user-story-for-frontend` | `frontend`, `user story 🎯` |
| `simple-task` | Al menos una de: `documentation 📃`, `ci 🏗️`, `enhancement 🔝`, `evolvability ♻️` |

### 3. GitHub Issue Type obligatorio

Todo issue DEBE tener un **GitHub Issue Type** definido (campo nativo de GitHub, distinto de las etiquetas). El tipo DEBE corresponder a la plantilla usada:

| Plantilla | Issue Type |
|-----------|------------|
| `feature-request` | `Feature` |
| `epic` | `Epic` |
| `user-story-for-api` | `Feature` |
| `user-story-for-frontend` | `Feature` |
| `simple-task` | `Task` |

Cuando el issue se crea via formulario de plantilla (`.github/ISSUE_TEMPLATE/*.yml`), el tipo se aplica automáticamente por el campo `type:` de la plantilla. Cuando el issue se crea via CLI (`gh issue create`), el agente DEBE aplicar el tipo después de la creación:

```bash
# Después de crear el issue, aplicar el tipo via API REST
gh api -X PATCH "repos/$OWNER/$REPO/issues/$ISSUE_NUMBER" -f type=Task
```

Los issues sin Issue Type definido NO cumplen esta Lex y bloquean la creación de rama/PR.

### 4. Assignee obligatorio

Todo issue DEBE tener al menos un assignee. Por defecto, el assignee es **el autor del issue** (la persona que lo abrió). Cuando el issue se crea via CLI sin plantilla, el agente DEBE aplicar el assignee en la creación o inmediatamente después:

```bash
# En la creacion
gh issue create ... --assignee "@me"

# O despues de la creacion
gh issue edit $ISSUE_NUMBER --add-assignee "@me"
```

La reasignación posterior a otra persona está permitida cuando el trabajo se delega, pero el issue NO PUEDE permanecer sin assignee.

### 5. Contenido obligatorio: Por qué / Qué / Cómo

Todo issue DEBE responder tres preguntas, de forma explícita o a través de las secciones de la plantilla:

| Pregunta | Qué cubre | Mapeo en la plantilla |
|----------|-----------|-----------------------|
| **Por qué** | Motivación, impacto, problema que se resuelve | "Why is this important?" / sección "Why" |
| **Qué** | Objetivo, alcance, qué cambia | "Objective" / sección "What" |
| **Cómo** | Enfoque de implementación, resultado esperado, definición de listo | "How should it work?" / sección "How" |

Para `simple-task`: las tres preguntas son las secciones directas de la plantilla.

Para las demás plantillas: las secciones se mapean a estas preguntas — el **Objective** (user story) responde Qué, **Why is this important** responde Por qué, y **How can it be implemented** / criterios de aceptación responden Cómo.

### 6. Rama y PR bloqueados hasta que el issue cumpla los requisitos

Según `lex-issue-first` y `lex-git-branches`, no se PUEDE crear ninguna rama ni abrir ningún PR si el issue asociado:

- No usa una de las plantillas aprobadas
- No tiene al menos una etiqueta obligatoria
- No tiene Issue Type definido
- No tiene assignee
- No responde Por qué, Qué y Cómo

### 7. Los agentes deben cumplir los mismos requisitos

Los agentes de IA que crean issues (via MCP o CLI) DEBEN:

1. Usar la plantilla adecuada mediante `kata-contributing-issue`
2. Aplicar las etiquetas obligatorias durante la creación
3. Aplicar el Issue Type correspondiente a la plantilla
4. Aplicar al menos un assignee (por defecto: `@me`)
5. Completar todas las secciones obligatorias (Por qué / Qué / Cómo) antes de enviar

## HARD-GATE

Conforme [`lex-hard-gate-pattern`](framework/es/_foundation/quality/lexis/lex-hard-gate-pattern.md), el bloqueo textual de esta Lex se expresa canónicamente como:

```
<HARD-GATE>
warrior-athena, warrior-apollo, warrior-hephaestus y cualquier otro
agente NO DEBE crear branch o abrir PR para una issue sin que ella
satisfaga TODOS los 5 criterios canónicos:

  (a) Usa una de las plantillas aprobadas (feature-request, epic,
      user-story-for-api, user-story-for-frontend, simple-task)
  (b) Tiene al menos una etiqueta obligatoria correspondiente a la plantilla
  (c) Tiene Issue Type definido (Feature, Task, Bug, Epic)
      compatible con la plantilla
  (d) Tiene al menos un assignee (por defecto: autor de la issue)
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

## Ejemplos

### Correctos

```
Issue: "Añadir kata-setup-gpg-signing al framework de contribución"
Plantilla: simple-task
Etiquetas: documentation 📃
Por qué: Los contribuidores necesitan configurar la firma GPG para cumplir lex-signed-commits; aún no existe una guía paso a paso.
Qué: Crear kata-setup-gpg-signing que cubra instalación de GPG, generación de clave, configuración de git y exportación a GitHub.
Cómo: Seguir el flujo de generación de clave GPG; cubrir macOS, Linux y Windows; añadir paso de verificación.
```

### Incorrectos

```
Issue: "arreglar el bug de autenticación"
Plantilla: ninguna
Etiquetas: ninguna
Contenido: una sola línea, sin Por qué / Qué / Cómo

→ ❌ Creación de rama bloqueada por lex-git-branches
→ ❌ PR rechazado por lex-issue-first
```

## Validación Automatizada

- **Herramienta:** `kata-contributing-issue` aplica plantilla, etiquetas, Issue Type y assignee en la creación; las plantillas `.github/ISSUE_TEMPLATE/*.yml` declaran `type:` para auto-aplicar Issue Type; la lista de verificación del PR revisa que el issue asociado esté completo en todos los campos obligatorios.
- **Cuándo:** al crear el issue (via kata o plantilla); al crear el PR (via verificación de lex-issue-first).
- **Métrica:** 0 PRs abiertos que referencien un issue sin plantilla, etiquetas, Issue Type o assignee; 100% de los issues creados via kata en conformidad en el primer envío.
