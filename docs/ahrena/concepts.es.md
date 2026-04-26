# Ahrena — Conceptos

## Los Cinco Pilares

Ahrena organiza todo el conocimiento y las capacidades en cinco Pilares. Cada Pilar tiene un papel diferenciado, un prefijo canónico y una posición en la jerarquía de autoridad.

```
Lexis  (autoridad)
  └── gobierna todos
Codex  (conocimiento)
  └── orienta Katas y Warriors
Katas  (ejecución)
  └── aplicados por Warriors; invocados por Cries
Warriors  (orquestación)
  └── orquestan Katas; invocados por Cries
Cries  (puntos de entrada)
  └── invocan Katas o Warriors; nunca Lexis o Codex directamente
```

### Lexis

> **"Ley inviolable. No admite excepción."**

| Propiedad | Valor |
|---|---|
| Prefijo | `lex-` |
| Autoridad | Máxima — gobierna todos los demás Pilares |
| Puede ser invocado por | Nunca se invoca directamente; es consultado por Codex, Katas, Warriors |
| Excepciones | Ninguna. Una Lexis es absoluta. |

Una Lexis establece una regla que todo agente, humano o AI, DEBE seguir en cualquier contexto. Violar una Lexis no es un problema técnico — es una violación de gobernanza. Ejemplos: `lex-signed-commits`, `lex-issue-driven`, `lex-brand-colors`.

---

### Codex

> **"Manual de referencia. Organiza el conocimiento para orientar decisiones."**

| Propiedad | Valor |
|---|---|
| Prefijo | `codex-` |
| Autoridad | Segunda — fuente de verdad para el conocimiento |
| Puede ser invocado por | Consultado por Katas y Warriors; no invocado por Cries |
| Excepciones | N/A — Codex orienta, no impone |

Un Codex es un documento de referencia detallado. Explica *cómo* funcionan las cosas, *por qué* están estructuradas de determinada manera y *cuándo* aplicar diferentes enfoques. Ejemplos: `codex-restful-apis`, `codex-python-architecture`, `codex-brand-voice`.

---

### Katas

> **"Skill reproducible. Aplica Lexis y consulta Codex para ejecutar una tarea clara y reproducible."**

| Propiedad | Valor |
|---|---|
| Prefijo | `kata-` |
| Autoridad | Tercera — ejecuta aplicando Lexis y consultando Codex |
| Puede ser invocado por | Cries (directamente o vía Warrior); Warriors |
| Excepciones | N/A |

Un Kata es una skill ejecutable — un procedimiento que el agente sigue paso a paso. Cuando se invoca, un Kata tiene una entrada definida, una secuencia de pasos y una salida definida. Ejemplos: `kata-contributing-issue`, `kata-api-design-oas`, `kata-quality-gate`.

---

### Warriors

> **"Agente especializado. Orquesta uno o más Katas."**

| Propiedad | Valor |
|---|---|
| Prefijo | `warrior-` |
| Autoridad | Cuarta — orquesta Katas; consulta Lexis y Codex |
| Puede ser invocado por | Cries o usuarios |
| Excepciones | N/A |

Un Warrior es un agente de AI especializado con experiencia en un dominio. Selecciona, secuencia y combina Katas para alcanzar objetivos complejos. Los Warriors se declaran con un papel, una persona y un conjunto de herramientas. Ejemplos: `warrior-athena` (workflow), `warrior-apollo` (backend), `warrior-hephaestus` (frontend).

---

### Cries

> **"Comando de alto nivel. Activa un Kata o Warrior."**

| Propiedad | Valor |
|---|---|
| Prefijo | `cry-` |
| Autoridad | Quinta — puntos de entrada; solo invocan Katas o Warriors |
| Puede ser invocado por | Usuarios |
| Excepciones | Los Cries NO DEBEN invocar Lexis ni acceder a Codex directamente |

Un Cry es un comando orientado al usuario — los comandos `/` que los usuarios escriben para activar una capacidad. Un Cry es el punto de entrada al framework. Ejemplos: `/cry-implement-issue`, `/cry-new-lex`, `/cry-api-design`.

---

## Reglas de Invocación

```
Usuario
  → invoca → Cry
               → invoca → Kata (uno a uno)
               → invoca → Warrior (uno a varios Katas)
                            → orquesta → Katas
                                         → aplican → Lexis
                                         → consultan → Codex
```

**Restricción crítica:** Un Cry que necesita múltiples Katas DEBE invocar un Warrior que los orqueste. Un Cry no debe invocar Katas directamente si se necesita más de uno.

---

## Clades y Subclades

El framework organiza los artefactos por **disciplina** mediante una taxonomía de dos niveles:

```
Clade (disciplina)
  └── Subclade (área dentro de la disciplina)
        └── Directorio del Pilar (lexis/ codex/ katas/ warriors/ cries/)
              └── artefactos
```

### Clade `_foundation`

El clade `_foundation` es **transversal** — sus reglas se aplican a todos los demás clades. Se prefija con `_` para aparecer primero en orden alfabético y señalar su naturaleza transversal.

| Subclade | Foco |
|---|---|
| `authoring` | Creación y gestión de artefactos del framework (Lexis, Codex, Katas, Warriors, Cries) |
| `contributing` | Proceso de contribución de código — commits, branches, issues, PRs, versionado |
| `i18n` | Estructura de idiomas del framework y navegación |
| `process` | Gestión de sesiones de agentes — directives, checkpoint, convenciones de nomenclatura |
| `quality` | Reglas de calidad transversales — observabilidad, templates, tono |
| `tooling` | Herramientas de plataforma — Makefile, servidores MCP, tipo de terminal |

### Clade `design`

| Subclade | Foco |
|---|---|
| `brand` | Identidad visual de Guardia — colores, logo, tipografía, voz |
| `system` | Sistema de diseño de producto — experiencia AI-First, biblioteca de componentes |

### Clade `documentation`

| Subclade | Foco |
|---|---|
| `i18n` | Reglas de traducción de documentación y estándares específicos por idioma |

### Clade `engineering`

| Subclade | Foco |
|---|---|
| `backend` | Servicios Python — arquitectura, FastAPI, SQLAlchemy, pruebas, tooling |
| `data` | Modelado de datos, diseño de schema, migrations, políticas de retención |
| `devops` | Infraestructura AWS — Well-Architected, IaC, seguridad, costo |
| `frontend` | Interfaces web — React/TypeScript, accesibilidad, pruebas, seguridad |
| `mobile` | iOS y Android — React Native/Flutter, offline-first, paridad de plataforma |
| `platform` | Estándares de la plataforma Guardia — REST APIs, entidades, eventos, auth, manejo de errores |
| `quality` | Estrategia de pruebas — pirámide, aislamiento, cobertura |
| `sre` | Site Reliability — SLO, alertas, respuesta a incidentes |
| `workflow` | Flujo de desarrollo — Issue-Driven Development, Gates, ADRs |

---

## Taxonomía de Direccionamiento

Todo artefacto del framework reside en una ruta canónica:

```
framework/{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.md
```

| Segmento | Ejemplos |
|---|---|
| `{lang}` | `en`, `pt-BR`, `es` |
| `{clade}` | `_foundation`, `design`, `documentation`, `engineering` |
| `{subclade}` | `authoring`, `contributing`, `backend`, `platform`, ... |
| `{pilar}` | `lexis`, `codex`, `katas`, `warriors`, `cries` |
| `{prefix}-{name}` | `lex-issue-driven`, `codex-restful-apis`, `kata-quality-gate` |

**Ejemplo:** La ley que gobierna el flujo Issue-Driven reside en:
```
framework/en/engineering/workflow/lexis/lex-issue-driven.md
framework/pt-BR/engineering/workflow/lexis/lex-issue-driven.md
framework/es/engineering/workflow/lexis/lex-issue-driven.md
```

El idioma es siempre el primer nivel de navegación. Todo artefacto DEBE existir en los tres idiomas.

---

## `.ahrena/.directives`

El archivo `.ahrena/.directives` es el archivo de configuración del proyecto. Define:

| Sección | Controla |
|---|---|
| `paths` | Rutas canónicas para artefactos del framework, templates y configuraciones generadas |
| `language.default` | Idioma predeterminado para la creación de artefactos (`pt-BR` en Guardia) |
| `language.i18n` | Versiones de idioma requeridas (`["pt-BR", "es", "en"]`) |
| `naming.prefixes` | Prefijos de los Pilares (`lex-`, `codex-`, `kata-`, `warrior-`, `cry-`) |
| `naming.casing` | Convención de nomenclatura de archivos y directorios (kebab-case) |
| `naming.addressing` | Patrón de direccionamiento canónico |
| `naming.reserved_clades` | Nombres de clades especiales (`_foundation`) |
| `naming.tone_and_writing_style` | Reglas de tono y estilo para artefactos y comunicación |
| `terminal` | Tipo de shell para comandos (`bash` o `powershell`) |
| `mcp.servers` | Servidores MCP autorizados (`github`, `notion`, `figma`) |

Todo agente DEBE leer `.ahrena/.directives` antes de producir cualquier artefacto — aplicado por `lex-directives`.
