# Lexis: Requisitos de Calidad del Issue

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Todos los issues en repositorios Guardia

## Ley

> **Todo issue en un repositorio Guardia DEBE usar una de las plantillas aprobadas (feature-request, epic, user-story-for-api, user-story-for-frontend, simple-task), DEBE tener al menos una etiqueta de la lista aprobada que corresponda a su tipo, y DEBE responder explícitamente: por qué (motivación e impacto), qué (objetivo y alcance) y cómo (enfoque de implementación o definición de listo). No se PUEDE crear ninguna rama ni abrir ningún PR para un issue que no cumpla estos requisitos.**

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

### 3. Contenido obligatorio: Por qué / Qué / Cómo

Todo issue DEBE responder tres preguntas, de forma explícita o a través de las secciones de la plantilla:

| Pregunta | Qué cubre | Mapeo en la plantilla |
|----------|-----------|-----------------------|
| **Por qué** | Motivación, impacto, problema que se resuelve | "Why is this important?" / sección "Why" |
| **Qué** | Objetivo, alcance, qué cambia | "Objective" / sección "What" |
| **Cómo** | Enfoque de implementación, resultado esperado, definición de listo | "How should it work?" / sección "How" |

Para `simple-task`: las tres preguntas son las secciones directas de la plantilla.

Para las demás plantillas: las secciones se mapean a estas preguntas — el **Objective** (user story) responde Qué, **Why is this important** responde Por qué, y **How can it be implemented** / criterios de aceptación responden Cómo.

### 4. Rama y PR bloqueados hasta que el issue cumpla los requisitos

Según `lex-issue-first` y `lex-git-branches`, no se PUEDE crear ninguna rama ni abrir ningún PR si el issue asociado:

- No usa una de las plantillas aprobadas
- No tiene al menos una etiqueta obligatoria
- No responde Por qué, Qué y Cómo

### 5. Los agentes deben cumplir los mismos requisitos

Los agentes de IA que crean issues (via MCP o CLI) DEBEN:

1. Usar la plantilla adecuada mediante `kata-contributing-issue`
2. Aplicar las etiquetas obligatorias durante la creación
3. Completar todas las secciones obligatorias (Por qué / Qué / Cómo) antes de enviar

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

- **Herramienta:** `kata-contributing-issue` aplica la selección de plantilla y etiquetas en la creación; la lista de verificación del PR revisa que el issue asociado esté completo.
- **Cuándo:** al crear el issue (via kata); al crear el PR (via verificación de lex-issue-first).
- **Métrica:** 0 PRs abiertos que referencien un issue sin plantilla y etiquetas; 100% de los issues creados via kata en conformidad en el primer envío.
