# Codex: Sistema de Pilares de Ahrena

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Creación y evolución de artefactos del framework

## Visión General

Este Codex es la referencia central sobre el sistema de Pilares de Ahrena. Describe la naturaleza de cada Pilar, cómo se relacionan entre sí y cómo el framework utiliza sus propios artefactos para evolucionar — el concepto de autosuficiencia.

## Contexto

- **Dominio:** Taxonomía y arquitectura del framework Ahrena
- **Público objetivo:** Agentes de IA y mantenedores del framework
- **Actualización:** Siempre que se cree un nuevo Pilar o cambien las relaciones entre Pilares

## Contenido

### Los Cinco Pilares

Ahrena organiza todo el conocimiento en cinco Pilares, cada uno con un papel distinto:

| Pilar | Prefijo | Naturaleza | Pregunta que responde |
|-------|---------|------------|----------------------|
| **Lexis** | `lex-` | Ley inquebrantable | "¿Qué está prohibido u obligatorio?" |
| **Codex** | `codex-` | Manual de referencia | "¿Qué se necesita saber sobre este dominio?" |
| **Katas** | `kata-` | Procedimiento repetible | "¿Cómo se ejecuta esta tarea paso a paso?" |
| **Warriors** | `warrior-` | Agente especializado | "¿Quién es responsable de este dominio?" |
| **Cries** | `cry-` | Comando recurrente | "¿Cómo se invoca esta acción rápidamente?" |

### Jerarquía de Autoridad

Los Pilares poseen una jerarquía implícita de autoridad:

1. **Lexis** — autoridad máxima. Ningún otro artefacto puede contradecir una Lexis. Son absolutas.
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

Cada Pilar puede referenciar artefactos de otros Pilares:

| Pilar | Referencia | Es referenciado por |
|-------|------------|--------------------|
| Lexis | — | Codex, Katas, Warriors |
| Codex | Lexis | Katas, Warriors |
| Katas | Lexis, Codex | Warriors, Cries |
| Warriors | Lexis, Codex, Katas | Cries |
| Cries | Katas, Warriors | — |

### Kit de Creación

Para que el framework sea autosuficiente, cada Pilar posee un **Kit de Creación** compuesto por:

| Pieza | Pilar | Función |
|-------|-------|---------|
| Codex del Pilar | Codex | Conocimiento sobre qué es y cómo escribir bien |
| Kata de creación | Kata | Procedimiento paso a paso para crear un nuevo artefacto |
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
| Nomenclatura de archivo | `{prefijo}-{nombre}.md` | `lex-no-secrets.md` |
| Casing | kebab-case | `codex-framework-language.md` |
| Direccionamiento | `{lang}/{clade}/{subclade}/{pilar}/{archivo}` | `pt-BR/engineering/quality/lexis/lex-code-review.md` |
| Creación dual | framework (`.md`) + IDE (formato de la plataforma) | `.md` + `.mdc` (Cursor) |

### Restricciones Técnicas

- Todo artefacto **DEBE** seguir el template oficial de su Pilar (`templates/{pilar}-sample.md`)
- Todo artefacto **DEBE** existir en los idiomas definidos en `language.i18n`
- El idioma predeterminado (`language.default`) es la fuente de verdad
- Los nombres de archivo usan el prefijo del Pilar y kebab-case
- Los términos canónicos (Lexis, Codex, Katas, Warriors, Cries, Clade, Subclade, Pilar) nunca se traducen

## Glosario

| Término | Definición |
|---------|-----------|
| Pilar | Una de las cinco categorías de artefacto de Ahrena |
| Clade | Primer nivel de organización temática (ej: engineering, documentation) |
| Subclade | Segundo nivel de organización dentro de un Clade (ej: quality, i18n) |
| Kit de Creación | Conjunto Codex + Kata + Cry que permite crear nuevos artefactos de un Pilar |
| Creación dual | Patrón de crear el artefacto canónico (`.md`) y la versión derivada para la IDE |
| Direccionamiento | Ruta completa de un artefacto en la taxonomía del framework |

## Referencias

- `.ahrena/.directives` — Directivas canónicas del framework
- `lex-template-usage` — Ley de uso obligatorio de templates
- `lex-framework-language` — Ley de estructura de idiomas
- `codex-lexis`, `codex-codex`, `codex-katas`, `codex-warriors`, `codex-cries` — Codex individuales de cada Pilar
