# Kata: Crear Nueva Lexis

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Creación de Lexis (leyes inquebrantables)

## Objetivo

Este Kata define el procedimiento estandarizado para crear una nueva Lexis en Ahrena — desde la concepción de la ley hasta la creación del artefacto en los tres idiomas obligatorios.

## Cuándo Usar

- Cuando es necesario establecer una restricción absoluta que ningún agente puede violar
- Cuando el usuario solicita explícitamente la creación de una nueva Lexis
- Cuando es invocado por `cry-new-lex`

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Asunto | Sí | Tema de la ley (ej: "code review obligatorio", "no secrets en repositorio") |
| Alcance | No | Dónde se aplica la ley (ej: "todos los repositorios", "pipeline CI/CD"). Si se omite, el agente debe inferirlo del asunto |
| Clade/Subclade | No | Dónde guardar el artefacto en la taxonomía. Si se omite, el agente debe inferirlo del asunto |

## Workflow

```
Progreso:
- [ ] 1. Lectura de directivas y referencias
- [ ] 2. Concepción de la ley
- [ ] 3. Redacción del artefacto
- [ ] 4. Guardado en la ruta correcta
- [ ] 5. Creación en los demás idiomas
- [ ] 6. Validación final
```

### Paso 1: Lectura de Directivas y Referencias

1. Leer `.ahrena/.directives` para obtener:
   - `language.default` — idioma por defecto
   - `language.i18n` — idiomas obligatorios
   - `naming.addressing` — patrón de direccionamiento
   - `naming.prefixes.lexis` — prefijo (`lex-`)
2. Leer `codex-lexis` para internalizar los criterios de calidad
3. Leer `templates/lex-sample.md` para obtener la estructura base
4. Verificar Lexis existentes en el Clade/Subclade destino para evitar duplicidad

### Paso 2: Concepción de la Ley

1. Formular la declaración de la ley siguiendo los criterios de `codex-lexis`:
   - Sujeto claro
   - Verbo imperativo (DEBE, NO PUEDE)
   - Acción específica
   - Condición temporal (si corresponde)
2. Verificar univocidad: ¿la ley tiene una única interpretación?
3. Verificar testabilidad: ¿es posible verificarla automáticamente?
4. Verificar necesidad: ¿resuelve un problema real?
5. Verificar inmutabilidad: ¿necesita excepciones? Si es así, considerar un Codex en lugar de Lexis

### Paso 3: Redacción del Artefacto

Usar `templates/lex-sample.md` como base y completar todas las secciones:

1. **Título:** `# Lexis: [Nombre Descriptivo]`
2. **Blockquote:** Prefijo, tipo y alcance
3. **Propósito:** Por qué existe esta ley — conectar con un riesgo o problema real
4. **Ley:** Declaración imperativa en blockquote (`> **[declaración]**`)
5. **Alcance:**
   - Se aplica a: alcance específico
   - Agentes vinculados: todos o Warriors específicos
   - Excepciones: Ninguna (siempre)
6. **Consecuencias de Violación:**
   - Bloqueo automático: acción técnica
   - Alerta: quién es notificado
   - Remediación: cómo corregir
7. **Ejemplos:** Correcto e Incorrecto con bloques de código
8. **Validación Automatizada:** Herramienta, momento y métrica

### Paso 4: Guardado en la Ruta Correcta

1. Determinar el Clade y Subclade adecuados para el asunto
2. Componer la ruta: `framework/{lang}/{clade}/{subclade}/lexis/lex-{nombre}.md`
3. Usar kebab-case para el nombre del archivo
4. Crear directorios intermedios si es necesario
5. Guardar el artefacto en el idioma por defecto (`language.default`)

### Paso 5: Creación en los Demás Idiomas

1. Para cada idioma en `language.i18n` (excepto el predeterminado):
   - Ejecutar `kata-translate` con el archivo creado en el Paso 4
   - O, si el agente domina el idioma, traducir directamente consultando `lex-language-{lang}` y `codex-language-{lang}`
2. Guardar cada traducción en la ruta equivalente bajo `framework/{lang}/`

### Paso 6: Validación Final

- [ ] El archivo sigue la estructura completa de `templates/lex-sample.md`
- [ ] La declaración de la ley es clara, unívoca e imperativa
- [ ] La sección "Excepciones" dice "Ninguna"
- [ ] La sección "Validación Automatizada" especifica herramienta, momento y métrica
- [ ] Los ejemplos (Correcto/Incorrecto) son concretos
- [ ] El archivo está guardado en la ruta correcta de la taxonomía
- [ ] Existen versiones en todos los idiomas de `language.i18n`
- [ ] El nombre del archivo usa el prefijo del Pilar definido en `naming.prefixes.lexis` (consultar `.directives`) y kebab-case

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Lexis en el idioma por defecto | Markdown (`.md`) | `framework/{lang}/{clade}/{subclade}/lexis/lex-{nombre}.md` |
| Traducciones | Markdown (`.md`) | Misma ruta en cada `framework/{lang}/` |

## Restricciones

- Nunca crear una Lexis que admita excepciones — si necesita excepciones, debe ser un Codex
- Nunca crear una Lexis sin validación automatizada — si no puede ser verificada, replantear la formulación
- Siempre consultar `codex-lexis` antes de redactar
- Siempre verificar Lexis existentes para evitar duplicidad o contradicción

## Referencias

- `lex-pilars` — Definición canónica de los Pilares; validar artefacto producido
- `codex-pilars` — Lista de validación para Lexis (sección Validación de artefatos)
- `codex-lexis` — Criterios de calidad para Lexis
- `codex-pilars` — Visión general del sistema de Pilares
- `lex-template-usage` — Ley de uso obligatorio de templates
- `lex-framework-language` — Ley de estructura de idiomas
- `kata-translate` — Procedimiento de traducción
- `templates/lex-sample.md` — Template oficial
