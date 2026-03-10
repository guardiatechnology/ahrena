# Codex: Cómo Escribir Buenos Codex

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Creación de Codex (manuales de referencia)

## Visión General

Este Codex documenta cómo estructurar bases de conocimiento eficaces en Ahrena. Aborda cómo organizar información de dominio, qué incluir y excluir, y cómo mantener un Codex actualizado a lo largo del tiempo. Es consultado por `kata-create-codex` durante la creación de nuevos Codex. El kata usa este Codex en el **Paso 1** (lectura de criterios) y en el **Paso 3** (redacción de secciones); la **Validación Final** del Kata verifica las Restricciones Técnicas y la Anatomía descritas abajo.

## Contexto

- **Dominio:** Diseño de bases de conocimiento estructuradas para agentes de IA
- **Público objetivo:** Agentes de IA que ejecutan `kata-create-codex` y mantenedores del framework
- **Actualización:** Cuando se identifiquen nuevos estándares de calidad para Codex

## Contenido

### Principios

1. **Consulta, no lectura:** Un Codex está diseñado para consulta puntual, no para lectura secuencial. Cada sección debe funcionar de forma independiente.
2. **Decisión, no información:** El valor de un Codex está en ayudar al agente a tomar decisiones, no en acumular información. Cada sección debe responder "qué hacer cuando...".
3. **Actualidad:** Un Codex desactualizado es peor que ningún Codex. Cada Codex debe incluir criterios claros de cuándo necesita ser actualizado.
4. **Alcance delimitado:** Un Codex cubre un dominio. Si el alcance crece demasiado, se debe dividir en Codex separados.

### Anatomía de un Buen Codex

| Sección | Propósito | Criterio de Calidad |
|---------|-----------|---------------------|
| **Visión General** | Orienta si este es el Codex correcto a consultar | Una frase que delimita el alcance |
| **Contexto** | Dominio, público y frecuencia de actualización | Específico y verificable |
| **Principios** | Fundamentos que guían decisiones | Principios accionables, no generalidades |
| **Estándares y Convenciones** | Reglas prácticas con ejemplos | Tabla con aspecto, estándar y ejemplo |
| **Decisiones Vigentes** | Estado actual de las elecciones técnicas | Rastreable (ADR, fecha, estado) |
| **Restricciones Técnicas** | Límites que no deben sobrepasarse | Concretas y justificadas |
| **Glosario** | Términos del dominio | Definiciones en el contexto de este Codex |

### Estándares y Convenciones

| Aspecto | Estándar | Ejemplo |
|---------|----------|---------|
| Granularidad | Un dominio por Codex | `codex-api-patterns` (no `codex-todo-sobre-backend`) |
| Tono | Técnico y directo | Evitar explicaciones extensas; preferir tablas y listas |
| Ejemplos | Concretos y del proyecto | Código real, no pseudocódigo genérico |
| Referencias cruzadas | Citar otros artefactos por identificador | "Consultar `codex-architecture`" |
| Actualización | Incluir disparador de actualización en Contexto | "Actualización: con cada ADR aprobado" |

### Errores Comunes

| Error | Problema | Solución |
|-------|----------|----------|
| Codex enciclopédico | Cubre todo, consulta imposible | Dividir en Codex menores por dominio |
| Codex narrativo | Escrito como artículo, no como referencia | Reestructurar en tablas, listas y secciones independientes |
| Codex estático | Nunca actualizado tras la creación | Definir disparador de actualización en Contexto |
| Codex duplicado | Repite información de otro Codex | Referenciar el otro Codex en lugar de duplicar |
| Codex opinativo sin justificación | "Use X porque es mejor" | Incluir trade-offs y justificación técnica |

### Codex vs Otros Pilares

| Situación | Pilar correcto | Por qué |
|-----------|---------------|---------|
| "Nunca se debe hacer X" | **Lexis** | Restricción absoluta, no recomendación |
| "Al hacer X, considerar Y y Z" | **Codex** | Conocimiento de dominio para decisión |
| "Para hacer X, seguir estos pasos" | **Kata** | Procedimiento, no conocimiento |
| "Hacer X rápidamente" | **Cry** | Atajo, no referencia |

### Restricciones Técnicas

- La sección **Visión General** debe describir el alcance en máximo dos párrafos
- La sección **Contexto** debe incluir **Actualización** con un disparador concreto (cuándo el Codex debe ser revisado)
- El **Contenido** debe incluir: Principios, Estándares y Convenciones, Decisiones Vigentes (si aplica), Restricciones Técnicas
- Las tablas son preferibles a párrafos extensos para información estructurada
- El nombre del archivo debe usar el prefijo definido en `naming.prefixes.codex` (consultar `.ahrena/.directives`) y kebab-case: `{prefijo}-{nombre-descriptivo}.md`
- La estructura debe seguir el template oficial: consultar `paths.samples.codex` en `.directives` (ej.: `templates/codex-sample.md`)

## Glosario

| Término | Definición |
|---------|-----------|
| Dominio | Área de conocimiento delimitada que un Codex cubre |
| Consulta puntual | Acceso a una sección específica para responder una duda |
| Referencia cruzada | Cita a otro artefacto del framework por su identificador |
| Disparador de actualización | Evento que indica que el Codex necesita ser revisado |

## Referencias

- `lex-pilars` — Ley que define canónicamente los Pilares; Codex como manual consultado, no invocado por Cry
- `codex-pilars` — Visión del sistema de Pilares y listas de validación (sección Validación de artefatos)
- `lex-directives` — Consulta obligatoria a `.ahrena/.directives` (paths, naming.prefixes)
- `lex-template-usage` — Ley de uso obligatorio de templates
- `kata-create-codex` — Procedimiento para crear nuevos Codex (consulta este Codex en los pasos 1 y 3)
- `paths.samples.codex` en `.directives` — Ruta del template oficial (ej.: `templates/codex-sample.md`)
