# Kata: Crear Nuevo Cry

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Creación de Cries (comandos recurrentes)

## Objetivo

Este Kata define el procedimiento estandarizado para crear un nuevo Cry en Ahrena — desde el diseño del comando y sus parámetros hasta la creación del artefacto en los tres idiomas obligatorios.

## Cuándo Usar

- Cuando es necesario crear un atajo rápido para una tarea recurrente
- Cuando el usuario solicita explícitamente la creación de un nuevo Cry
- Cuando es invocado por `cry-new-cry`
- Cuando un Kata existente necesita un punto de entrada simplificado

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Acción | Sí | Lo que el comando hace (ej: "traducir documento", "generar changelog") |
| Kata asociado | No | Kata que el Cry invoca. Si se omite, el agente debe identificar o sugerir la creación de un Kata |
| Warrior asociado | No | Warrior que ejecuta el Kata, si existe |
| Clade/Subclade | No | Dónde guardar en la taxonomía. Si se omite, el agente debe inferirlo de la acción |

## Workflow

```
Progreso:
- [ ] 1. Lectura de directivas y referencias
- [ ] 2. Diseño del comando
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
   - `naming.prefixes.cries` — prefijo (`cry-`)
2. Leer `codex-cries` para internalizar los criterios de calidad
3. Leer `templates/cry-sample.md` para obtener la estructura base
4. Verificar Cries existentes para evitar duplicidad
5. Confirmar que el Kata asociado existe (o marcar como pendiente de creación)

### Paso 2: Diseño del Comando

1. Definir la **sintaxis de invocación**: `/cry-{nombre} <obligatorio> [opcional]`
2. Definir **parámetros**:
   - Mínimo de obligatorios (solo lo esencial)
   - Valores por defecto inteligentes para opcionales (de `.directives` cuando sea posible)
   - Formato explícito para cada parámetro
3. Definir la **cadena de invocación**:
   - Patrón 1: Cry → Kata (cuando no hay Warrior)
   - Patrón 2: Cry → Warrior → Kata (cuando existe Warrior dedicado)
4. Elaborar el **prompt template**:
   - Contexto con variables `{{param}}`
   - Tarea referenciando el Kata por nombre
   - Formato de salida explícito
5. Preparar **ejemplo de invocación** con input y output concretos

### Paso 3: Redacción del Artefacto

Usar `templates/cry-sample.md` como base y completar todas las secciones:

1. **Título:** `# Cry: [Nombre del Comando]`
2. **Blockquote:** Prefijo, tipo y alcance
3. **Descripción:** Una frase sobre lo que el comando hace
4. **Uso:** Sintaxis con `/cry-{nombre}`
5. **Parámetros:** Tabla con nombre, obligatoriedad, descripción y ejemplo
6. **Lo que el Comando Hace:** Lista numerada de 3-6 acciones de alto nivel
7. **Prompt Template:** Bloque de código con contexto, tarea y formato
8. **Ejemplo de Invocación:** Input y output concretos
9. **Restricciones:** Límites del comando
10. **Diferencia con Kata:** Tabla comparativa Cry vs Kata para este caso

### Paso 4: Guardado en la Ruta Correcta

1. Determinar el Clade y Subclade adecuados
2. Componer la ruta: `framework/{lang}/{clade}/{subclade}/cries/cry-{nombre}.md`
3. Usar kebab-case para el nombre del archivo
4. Crear directorios intermedios si es necesario
5. Guardar el artefacto en el idioma por defecto (`language.default`)

### Paso 5: Creación en los Demás Idiomas

1. Para cada idioma en `language.i18n` (excepto el predeterminado):
   - Ejecutar `kata-translate` con el archivo creado en el Paso 4
   - O traducir directamente consultando `lex-language-{lang}` y `codex-language-{lang}`
2. Guardar cada traducción en la ruta equivalente bajo `framework/{lang}/`

### Paso 6: Validación Final

- [ ] El archivo sigue la estructura completa de `templates/cry-sample.md`
- [ ] La sintaxis de invocación es clara (`/cry-{nombre} <args>`)
- [ ] Los parámetros obligatorios son mínimos (1-2 idealmente)
- [ ] El prompt template usa `{{variables}}` y referencia el Kata
- [ ] El ejemplo de invocación tiene input y output concretos
- [ ] La tabla "Diferencia con Kata" está completada
- [ ] El Kata asociado existe o está marcado como pendiente
- [ ] El archivo está guardado en la ruta correcta de la taxonomía
- [ ] Existen versiones en todos los idiomas de `language.i18n`
- [ ] El nombre del archivo usa el prefijo del Pilar definido en `naming.prefixes.cries` (consultar `.directives`) y kebab-case

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Cry en el idioma por defecto | Markdown (`.md`) | `framework/{lang}/{clade}/{subclade}/cries/cry-{nombre}.md` |
| Traducciones | Markdown (`.md`) | Misma ruta en cada `framework/{lang}/` |

## Restricciones

- Todo Cry debe referenciar al menos un Kata — los Cries sin Kata delegan mal
- Nunca crear un Cry con muchos parámetros obligatorios — si necesita muchos inputs, el usuario debería usar el Kata directamente
- Siempre consultar `codex-cries` antes de redactar
- Siempre verificar Cries existentes para evitar duplicidad

## Referencias

- `lex-pilars` — Definición canónica de los Pilares; validar artefacto producido (Cry invoca solo Kata/Warrior)
- `codex-pilars` — Lista de validación para Cries (sección Validación de artefatos)
- `codex-cries` — Criterios de calidad para Cries
- `codex-pilars` — Visión general del sistema de Pilares
- `lex-template-usage` — Ley de uso obligatorio de templates
- `lex-framework-language` — Ley de estructura de idiomas
- `kata-translate` — Procedimiento de traducción
- `templates/cry-sample.md` — Template oficial
