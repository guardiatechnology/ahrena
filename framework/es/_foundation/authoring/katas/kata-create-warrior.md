# Kata: Crear Nuevo Warrior

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Creación de Warriors (agentes especializados)

## Objetivo

Este Kata define el procedimiento estandarizado para crear un nuevo Warrior en Ahrena — desde el diseño de identidad y persona hasta la creación del artefacto en los tres idiomas obligatorios.

## Cuándo Usar

- Cuando es necesario crear un agente especializado con identidad, alcance y responsabilidades definidos
- Cuando el usuario solicita explícitamente la creación de un nuevo Warrior
- Cuando es invocado por `cry-new-warrior`

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Rol | Sí | Función que el Warrior desempeña (ej: "Arquitecto de Software", "Revisor de Código") |
| Dominio | No | Área de actuación. Si se omite, el agente debe inferirlo del rol |
| Nombre | No | Nombre propio del Warrior. Si se omite, el agente debe sugerir un nombre temático |
| Clade/Subclade | No | Dónde guardar en la taxonomía. Si se omite, el agente debe inferirlo del dominio |

## Workflow

```
Progreso:
- [ ] 1. Lectura de directivas y referencias
- [ ] 2. Diseño de la identidad
- [ ] 3. Definición de responsabilidades y consulta
- [ ] 4. Redacción del artefacto
- [ ] 5. Guardado en la ruta correcta
- [ ] 6. Creación en los demás idiomas
- [ ] 7. Validación final
```

### Paso 1: Lectura de Directivas y Referencias

1. Leer `.ahrena/.directives` para obtener:
   - `language.default` — idioma por defecto
   - `language.i18n` — idiomas obligatorios
   - `naming.addressing` — patrón de direccionamiento
   - `naming.prefixes.warriors` — prefijo (`warrior-`)
2. Leer `codex-warriors` para internalizar los criterios de calidad
3. Leer `templates/warrior-sample.md` para obtener la estructura base
4. Verificar Warriors existentes para evitar superposición de responsabilidades

### Paso 2: Diseño de la Identidad

1. **Nombre:** Elegir un nombre memorable que evoque el rol (mitológico, histórico o simbólico)
2. **Rol:** Título profesional claro (ej: "Traductor Especialista de Documentación Técnica")
3. **Dominio:** Área específica de actuación con delimitación clara
4. **Persona:** 2-3 adjetivos que definen el tono (ej: "metódico, riguroso, centrado en trade-offs")
5. **Misión:** 1-2 frases en blockquote que resumen el propósito central

### Paso 3: Definición de Responsabilidades y Consulta

1. Listar responsabilidades positivas ("Hace") — acciones concretas y específicas
2. Listar exclusiones ("No Hace") — límites claros para evitar un alcance infinito
3. Mapear la cadena de consulta:
   - **Lexis:** qué leyes sigue el Warrior (siempre incluir `lex-directives`)
   - **Codex:** qué manuales consulta para tomar decisiones
   - **Katas:** qué procedimientos ejecuta
4. Definir criterios de escalamiento — cuándo el Warrior se detiene y solicita ayuda humana
5. Definir el flujo de actuación: Recibe → Consulta → Analiza → Produce → Valida

### Paso 4: Redacción del Artefacto

Usar `templates/warrior-sample.md` como base y completar todas las secciones:

1. **Título:** `# Warrior: [Nombre] — [Descripción Breve]`
2. **Blockquote:** Prefijo, tipo y alcance
3. **Identidad:** Nombre, rol, dominio y persona
4. **Misión:** Cita en blockquote
5. **Responsabilidades:** Listas "Hace" y "No Hace"
6. **Consulta:** Tablas de Lexis, Codex y Katas
7. **Comportamiento:** Tono, flujo de actuación y criterios de escalamiento
8. **Ejemplo de Interacción:** Input del usuario + respuesta estructurada del Warrior

### Paso 5: Guardado en la Ruta Correcta

1. Determinar el Clade y Subclade adecuados
2. Componer la ruta: `framework/{lang}/{clade}/{subclade}/warriors/warrior-{nombre}.md`
3. Usar kebab-case para el nombre del archivo (nombre del warrior)
4. Crear directorios intermedios si es necesario
5. Guardar el artefacto en el idioma por defecto (`language.default`)

### Paso 6: Creación en los Demás Idiomas

1. Para cada idioma en `language.i18n` (excepto el predeterminado):
   - Ejecutar `kata-translate` con el archivo creado en el Paso 5
   - O traducir directamente consultando `lex-language-{lang}` y `codex-language-{lang}`
2. Guardar cada traducción en la ruta equivalente bajo `framework/{lang}/`

### Paso 7: Validación Final

- [ ] El archivo sigue la estructura completa de `templates/warrior-sample.md`
- [ ] La identidad tiene nombre, rol, dominio y persona
- [ ] La misión está en blockquote con 1-2 frases
- [ ] "Hace" y "No Hace" son listas equilibradas y sin ambigüedad
- [ ] La cadena de consulta incluye al menos `lex-directives`
- [ ] Los criterios de escalamiento son concretos
- [ ] El ejemplo de interacción tiene input y output completos
- [ ] El archivo está guardado en la ruta correcta de la taxonomía
- [ ] Existen versiones en todos los idiomas de `language.i18n`
- [ ] El nombre del archivo usa el prefijo del Pilar definido en `naming.prefixes.warriors` (consultar `.directives`) y kebab-case

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Warrior en el idioma por defecto | Markdown (`.md`) | `framework/{lang}/{clade}/{subclade}/warriors/warrior-{nombre}.md` |
| Traducciones | Markdown (`.md`) | Misma ruta en cada `framework/{lang}/` |

## Restricciones

- Nunca crear un Warrior genérico sin alcance delimitado
- Nunca crear un Warrior sin cadena de consulta explícita
- Nunca crear un Warrior sin criterios de escalamiento
- Siempre consultar `codex-warriors` antes de redactar
- Siempre verificar Warriors existentes para evitar superposición de responsabilidades

## Referencias

- `lex-pilars` — Definición canónica de los Pilares; validar artefacto producido
- `codex-pilars` — Lista de validación para Warriors (sección Validación de artefatos)
- `codex-warriors` — Criterios de calidad para Warriors
- `codex-pilars` — Visión general del sistema de Pilares
- `lex-template-usage` — Ley de uso obligatorio de templates
- `lex-framework-language` — Ley de estructura de idiomas
- `kata-translate` — Procedimiento de traducción
- `templates/warrior-sample.md` — Template oficial
