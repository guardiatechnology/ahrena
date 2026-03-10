# Kata: Crear Nuevo Codex

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Creación de Codex (manuales de referencia)

## Objetivo

Este Kata define el procedimiento estandarizado para crear un nuevo Codex en Ahrena — desde la definición del dominio de conocimiento hasta la creación del artefacto en los tres idiomas obligatorios.

## Cuándo Usar

- Cuando es necesario documentar conocimiento de dominio para consulta por agentes de IA
- Cuando el usuario solicita explícitamente la creación de un nuevo Codex
- Cuando es invocado por `cry-new-codex`

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Dominio | Sí | Área de conocimiento a documentar (ej: "arquitectura del sistema", "patrones de API") |
| Público objetivo | No | Quién consultará este Codex. Si se omite, se asume "agentes de IA y desarrolladores" |
| Clade/Subclade | No | Dónde guardar en la taxonomía. Si se omite, el agente debe inferirlo del dominio |

## Workflow

```
Progreso:
- [ ] 1. Lectura de directivas y referencias
- [ ] 2. Estructuración del conocimiento
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
   - `naming.prefixes.codex` — prefijo (`codex-`)
2. Leer `codex-codex` para internalizar los criterios de calidad
3. Leer `templates/codex-sample.md` para obtener la estructura base
4. Verificar Codex existentes en el Clade/Subclade destino para evitar duplicidad

### Paso 2: Estructuración del Conocimiento

1. Delimitar el alcance: qué cubre este Codex y qué no cubre
2. Identificar los principios fundamentales del dominio (3-5 principios)
3. Mapear patrones y convenciones relevantes (tabla: aspecto, patrón, ejemplo)
4. Listar decisiones vigentes, si corresponde
5. Identificar restricciones técnicas del dominio
6. Definir el disparador de actualización (cuándo el Codex necesita ser revisado)

### Paso 3: Redacción del Artefacto

Usar `templates/codex-sample.md` como base y completar todas las secciones:

1. **Título:** `# Codex: [Nombre del Manual]`
2. **Blockquote:** Prefijo, tipo y alcance
3. **Visión General:** Una descripción concisa del dominio cubierto (máximo 2 párrafos)
4. **Contexto:** Dominio, público objetivo y disparador de actualización
5. **Contenido:**
   - Principios: lista numerada con descripción y justificación
   - Patrones y Convenciones: tabla estructurada
   - Decisiones Vigentes: tabla con ADR, decisión y estado (si corresponde)
   - Restricciones Técnicas: lista de límites concretos
6. **Diagrama de Referencia:** Cuando el dominio se beneficia de visualización
7. **Glosario:** Términos del dominio con definiciones contextuales
8. **Referencias:** Enlaces a artefactos relacionados

### Paso 4: Guardado en la Ruta Correcta

1. Determinar el Clade y Subclade adecuados para el dominio
2. Componer la ruta: `framework/{lang}/{clade}/{subclade}/codex/codex-{nombre}.md`
3. Usar kebab-case para el nombre del archivo
4. Crear directorios intermedios si es necesario
5. Guardar el artefacto en el idioma por defecto (`language.default`)

### Paso 5: Creación en los Demás Idiomas

1. Para cada idioma en `language.i18n` (excepto el predeterminado):
   - Ejecutar `kata-translate` con el archivo creado en el Paso 4
   - O traducir directamente consultando `lex-language-{lang}` y `codex-language-{lang}`
2. Guardar cada traducción en la ruta equivalente bajo `framework/{lang}/`

### Paso 6: Validación Final

- [ ] El archivo sigue la estructura completa de `templates/codex-sample.md`
- [ ] La Visión General delimita el alcance en un máximo de 2 párrafos
- [ ] El Contexto incluye un disparador de actualización concreto
- [ ] Los principios son accionables (no generalidades genéricas)
- [ ] Se usan tablas para información estructurada
- [ ] El Glosario define términos en el contexto de este Codex
- [ ] El archivo está guardado en la ruta correcta de la taxonomía
- [ ] Existen versiones en todos los idiomas de `language.i18n`
- [ ] El nombre del archivo usa el prefijo del Pilar definido en `naming.prefixes.codex` (consultar `.directives`) y kebab-case

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Codex en el idioma por defecto | Markdown (`.md`) | `framework/{lang}/{clade}/{subclade}/codex/codex-{nombre}.md` |
| Traducciones | Markdown (`.md`) | Misma ruta en cada `framework/{lang}/` |

## Restricciones

- Nunca crear un Codex enciclopédico — si el alcance es muy amplio, dividir en Codex más pequeños
- Nunca crear un Codex sin disparador de actualización — los Codex estáticos se vuelven obsoletos
- Siempre consultar `codex-codex` antes de redactar
- Siempre verificar Codex existentes para evitar duplicidad o superposición

## Referencias

- `lex-pilars` — Definición canónica de los Pilares; validar artefacto producido
- `codex-pilars` — Lista de validación para Codex (sección Validación de artefatos)
- `codex-codex` — Criterios de calidad para Codex
- `codex-pilars` — Visión general del sistema de Pilares
- `lex-template-usage` — Ley de uso obligatorio de templates
- `lex-framework-language` — Ley de estructura de idiomas
- `kata-translate` — Procedimiento de traducción
- `templates/codex-sample.md` — Template oficial
