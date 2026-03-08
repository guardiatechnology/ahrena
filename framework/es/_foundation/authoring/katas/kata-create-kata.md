# Kata: Crear Nuevo Kata

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Creación de Katas (procedimientos repetibles)

## Objetivo

Este Kata define el procedimiento estandarizado para crear un nuevo Kata en Ahrena — desde la descomposición de la tarea en pasos hasta la creación del artefacto en los tres idiomas obligatorios. Este es el Kata que crea Katas — el mecanismo de autorreplicación del framework.

## Cuándo Usar

- Cuando es necesario estandarizar una tarea recurrente en un procedimiento estructurado
- Cuando el usuario solicita explícitamente la creación de un nuevo Kata
- Cuando es invocado por `cry-new-kata`

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Tarea | Sí | Descripción de la tarea a estandarizar (ej: "crear ADR", "hacer code review") |
| Contexto | No | Información adicional sobre el dominio o restricciones de la tarea |
| Clade/Subclade | No | Dónde guardar en la taxonomía. Si se omite, el agente debe inferirlo de la tarea |

## Workflow

```
Progreso:
- [ ] 1. Lectura de directivas y referencias
- [ ] 2. Descomposición de la tarea
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
   - `naming.prefixes.katas` — prefijo (`kata-`)
2. Leer `codex-katas` para internalizar los criterios de calidad
3. Leer `templates/kata-sample.md` para obtener la estructura base
4. Verificar Katas existentes para evitar duplicidad

### Paso 2: Descomposición de la Tarea

1. Identificar los **inputs** necesarios:
   - ¿Qué es obligatorio?
   - ¿Qué puede tener un valor por defecto?
   - ¿Cuál es el formato esperado de cada input?
2. Descomponer la tarea en **pasos atómicos** (4-8 pasos ideal):
   - Cada paso realiza una única acción
   - Cada paso tiene subacciones numeradas
   - Cada paso es verificable antes de avanzar
3. Identificar los **outputs**:
   - ¿Qué se produce?
   - ¿En qué formato?
   - ¿Dónde se guarda?
4. Definir **criterios de validación**:
   - Checklist de forma (estructura, formato)
   - Checklist de contenido (completitud, corrección)
5. Si la tarea tiene menos de 4 pasos, considerar si debería ser un Cry en lugar de Kata

### Paso 3: Redacción del Artefacto

Usar `templates/kata-sample.md` como base y completar todas las secciones:

1. **Título:** `# Kata: [Nombre del Procedimiento]`
2. **Blockquote:** Prefijo, tipo y alcance
3. **Objetivo:** Una frase sobre lo que el procedimiento produce
4. **Cuándo Usar:** Lista de condiciones de activación (3-4 ítems)
5. **Inputs:** Tabla con nombre, obligatoriedad y descripción
6. **Workflow:**
   - Checklist de progreso al inicio (checkboxes)
   - Cada paso con título descriptivo y subacciones numeradas
   - Último paso siempre "Validación Final"
7. **Outputs:** Tabla con formato y destino
8. **Restricciones:** Lista de límites de lo que el Kata no puede hacer

### Paso 4: Guardado en la Ruta Correcta

1. Determinar el Clade y Subclade adecuados para la tarea
2. Componer la ruta: `framework/{lang}/{clade}/{subclade}/katas/kata-{nombre}.md`
3. Usar kebab-case para el nombre del archivo
4. Crear directorios intermedios si es necesario
5. Guardar el artefacto en el idioma por defecto (`language.default`)

### Paso 5: Creación en los Demás Idiomas

1. Para cada idioma en `language.i18n` (excepto el predeterminado):
   - Ejecutar `kata-translate` con el archivo creado en el Paso 4
   - O traducir directamente consultando `lex-language-{lang}` y `codex-language-{lang}`
2. Guardar cada traducción en la ruta equivalente bajo `framework/{lang}/`

### Paso 6: Validación Final

- [ ] El archivo sigue la estructura completa de `templates/kata-sample.md`
- [ ] El Objetivo describe el output en una frase clara
- [ ] Los Inputs tienen obligatoriedad y valores por defecto definidos
- [ ] El Workflow tiene checklist de progreso al inicio
- [ ] Cada paso realiza una única acción (atómico)
- [ ] El último paso es "Validación Final" con checkboxes
- [ ] El número de pasos está entre 4 y 8
- [ ] Los Outputs especifican formato y destino
- [ ] El archivo está guardado en la ruta correcta de la taxonomía
- [ ] Existen versiones en todos los idiomas de `language.i18n`
- [ ] El nombre del archivo usa el prefijo `kata-` y kebab-case

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Kata en el idioma por defecto | Markdown (`.md`) | `framework/{lang}/{clade}/{subclade}/katas/kata-{nombre}.md` |
| Traducciones | Markdown (`.md`) | Misma ruta en cada `framework/{lang}/` |

## Restricciones

- Si la tarea tiene menos de 4 pasos, considerar crear un Cry en lugar de Kata
- Si la tarea tiene más de 8 pasos, considerar dividir en Katas más pequeños
- Nunca crear un Kata con pasos vagos — cada paso debe tener subacciones concretas
- Siempre consultar `codex-katas` antes de redactar
- Siempre incluir validación final como último paso

## Referencias

- `codex-katas` — Criterios de calidad para Katas
- `codex-pilars` — Visión general del sistema de Pilares
- `lex-template-usage` — Ley de uso obligatorio de templates
- `lex-framework-language` — Ley de estructura de idiomas
- `kata-translate` — Procedimiento de traducción
- `templates/kata-sample.md` — Template oficial
