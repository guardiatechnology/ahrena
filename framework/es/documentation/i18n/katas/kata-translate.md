# Kata: Traducción de Documentación

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Traducción de cualquier documentación técnica

## Objetivo

Este Kata define el procedimiento estandarizado para traducir documentación técnica de un idioma a otro. Es genérico — funciona para documentación de Ahrena, documentación de proyectos y cualquier otro contenido técnico en Markdown.

El diferencial de este Kata es la consulta obligatoria a las reglas y guías **específicas de cada idioma destino**, garantizando que cada traducción respete las particularidades lingüísticas del destino.

## Cuándo Usar

- Cuando un documento necesita ser traducido a uno o más idiomas
- Cuando un documento existente es actualizado y las traducciones necesitan sincronización
- Cuando el usuario solicita explícitamente la traducción de un archivo
- Cuando es invocado por `cry-translate` o por `warrior-translator`

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Archivo fuente | Sí | Ruta del documento en el idioma de origen |
| Idioma(s) destino | No | Código(s) BCP 47. Si se omite, traducir a todos los idiomas de `language.i18n` excepto el de origen |

## Workflow

```
Progreso:
- [ ] 1. Lectura de directivas y reglas
- [ ] 2. Identificación del contexto
- [ ] 3. Consulta de reglas del idioma destino
- [ ] 4. Traducción del contenido
- [ ] 5. Guardado en la ruta correcta
- [ ] 6. Validación final
```

### Paso 1: Lectura de Directivas y Reglas

1. Leer `.ahrena/.directives` para obtener:
   - `language.default` — idioma predeterminado (fuente de verdad)
   - `language.i18n` — lista de idiomas obligatorios
   - `naming.addressing` — patrón de direccionamiento
2. Confirmar que el/los idioma(s) destino están en `language.i18n`

### Paso 2: Identificación del Contexto

1. Leer el archivo fuente íntegramente
2. Identificar el idioma de origen (por la ruta o por el contenido)
3. Determinar si el documento es del framework Ahrena (está en `framework/`) o genérico
4. Si es del framework: verificar si `lex-framework-language` se aplica
5. Calcular la ruta de destino para cada idioma destino

### Paso 3: Consulta de Reglas del Idioma Destino

Para **cada idioma destino**, consultar en el siguiente orden:

1. `lex-language` — reglas transversales (siempre)
2. `lex-language-{lang}` — reglas específicas del idioma destino
3. `codex-language` — guía transversal
4. `codex-language-{lang}` — guía específica del idioma destino

### Paso 4: Traducción del Contenido

1. Traducir el contenido aplicando las reglas del idioma destino
2. **Preservar obligatoriamente:** estructura Markdown, nombres propios de Ahrena, bloques de código, rutas, URLs
3. **Traducir:** títulos, cuerpo de texto, descripciones en tablas
4. **Aplicar particularidades del idioma:** tono, formalidad, términos técnicos, falsos cognatos

### Paso 5: Guardado en la Ruta Correcta

1. Crear directorios intermedios si no existen
2. Guardar el archivo traducido en la ruta calculada
3. El nombre del archivo permanece inalterado

### Paso 6: Validación Final

- [ ] El archivo traducido existe en la ruta correcta
- [ ] Todas las secciones del original están presentes
- [ ] Los headings siguen la misma jerarquía
- [ ] Términos canónicos de Ahrena no fueron traducidos
- [ ] Rutas y referencias preservadas
- [ ] Idioma del contenido es correcto
- [ ] Formato Markdown intacto
- [ ] Reglas de `lex-language-{lang}` respetadas

## Restricciones

- Nunca alterar el archivo fuente durante la traducción
- Nunca traducir términos canónicos de Ahrena
- Nunca omitir o fusionar secciones del original
- Siempre consultar las reglas del idioma destino antes de traducir

## Referencias

- `lex-language`, `lex-language-ptbr`, `lex-language-en`, `lex-language-es`
- `codex-language`, `codex-language-ptbr`, `codex-language-en`, `codex-language-es`
- `warrior-translator` — Agente que ejecuta este Kata
- `cry-translate` — Comando que invoca este flujo
