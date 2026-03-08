# Codex: Estructura de Idiomas del Framework

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Organización de carpetas por idioma dentro de `framework/`

## Visión General

Este Codex documenta cómo funciona la estructura de carpetas de idioma en Ahrena. El framework adopta un enfoque donde el idioma es el primer nivel de navegación dentro de `framework/`, con cada idioma teniendo un árbol completo y reflejado de artefactos.

Este manual trata exclusivamente de la **estructura de carpetas**. Para orientaciones sobre **cómo traducir contenido**, consulte los artefactos en `documentation/i18n/`.

## Contexto

- **Dominio:** Organización estructural de idiomas en el framework
- **Público objetivo:** Todos los agentes IA, Warriors y mantenedores del framework
- **Actualización:** siempre que un nuevo idioma sea agregado a `language.i18n` o la estructura de carpetas cambie

## Contenido

### Principios

1. **Idioma como raíz:** el código del idioma (ej: `pt-BR`, `es`, `en`) es siempre el primer directorio dentro de `framework/`.
2. **Reflejo total:** cada carpeta de idioma replica íntegramente el árbol de clades, subclades y pilares.
3. **Fuente de verdad:** el idioma definido en `language.default` (actualmente `pt-BR`) es la fuente de verdad.
4. **Cursor monolingüe:** los archivos `.mdc` en `.cursor/` usan exclusivamente el idioma de `language.cursor`.

### Estructura de Carpetas

```
framework/
├── .directives.sample
├── pt-BR/                          # Idioma predeterminado (fuente de verdad)
│   ├── _foundation/
│   │   └── i18n/
│   │       ├── lexis/lex-framework-language.md
│   │       └── codex/codex-framework-language.md
│   └── documentation/i18n/
│       ├── lexis/
│       ├── codex/
│       ├── katas/kata-translate.md
│       ├── warriors/warrior-translator.md
│       └── cries/cry-translate.md
├── es/                             # Español (misma estructura)
│   └── ...
└── en/                             # Inglés (misma estructura)
    └── ...
```

### Patrones y Convenciones

| Aspecto | Patrón | Ejemplo |
|---------|--------|---------|
| Direccionamiento framework | `{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.md` | `es/_foundation/i18n/lexis/lex-framework-language.md` |
| Direccionamiento Cursor | `{clade}/{subclade}/{prefix}-{name}.mdc` | `_foundation/i18n/lex-framework-language.mdc` |
| Idioma predeterminado | Definido en `language.default` | `pt-BR` |
| Idiomas obligatorios | Listados en `language.i18n` | `pt-BR`, `es`, `en` |
| Idioma del Cursor | Definido en `language.cursor` | `en` |
| Nombres de carpeta | Código BCP 47 | `pt-BR`, `es`, `en` |

### Flujo de Creación de Artefactos

1. Crear el artefacto en el idioma predeterminado (`language.default`)
2. Traducir para cada idioma de `language.i18n` (usando `warrior-translator` de `documentation/i18n/`)
3. Crear la versión `.mdc` para Cursor en el idioma de `language.cursor`
4. Validar que el artefacto existe en todos los idiomas obligatorios

### Flujo de Actualización

1. Modificar el artefacto en el idioma predeterminado
2. Señalar que las traducciones necesitan actualización
3. Usar `cry-translate` o `warrior-translator` para actualizar cada traducción
4. Actualizar la versión `.mdc` si es necesario

### Separación de Responsabilidades

| Clade | Alcance | Artefactos |
|-------|---------|------------|
| `_foundation/i18n/` | **Estructura** de carpetas y reglas de navegación por idioma | `lex-framework-language`, `codex-framework-language` |
| `documentation/i18n/` | **Traducción** de contenido — reglas por idioma, procedimientos, agente | `lex-language`, `lex-language-{lang}`, `codex-language`, `codex-language-{lang}`, `kata-translate`, `warrior-translator`, `cry-translate` |

## Glosario

| Término | Definición |
|---------|------------|
| i18n | Abreviación de "internationalization" (18 letras entre la "i" y la "n") |
| BCP 47 | Estándar para códigos de idioma (ej: `pt-BR`, `en-US`, `es`) |
| Idioma predeterminado | El idioma definido en `language.default`, usado como fuente de verdad |
| Reflejo | Replicación de la misma estructura de directorios en cada carpeta de idioma |

## Referencias

- `lex-framework-language` — Ley estructural que este Codex complementa
- `documentation/i18n/` — Artefactos de traducción genéricos
- `.ahrena/.directives` — Fuente de verdad para configuración de idiomas
