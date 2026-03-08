# Lexis: Estructura de Idiomas del Framework

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Estructura de carpetas y navegación por idioma dentro de `framework/`

## Propósito

Ahrena adopta un enfoque de i18n basado en carpetas: el idioma es el **primer nivel de navegación** dentro de `framework/`. Cada idioma tiene su propio árbol completo, reflejando la estructura de clades, subclades y pilares.

Esta Lexis gobierna exclusivamente la **organización estructural** de idiomas en el framework — cómo las carpetas se crean, nombran y reflejan. Para reglas sobre **cómo traducir contenido**, consulte `lex-language` y los artefactos por idioma en `documentation/i18n/`.

## Ley

> **El idioma DEBE ser el primer nivel de navegación dentro de `framework/`, siguiendo el direccionamiento `{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.{ext}`. Todo artefacto DEBE existir en todos los idiomas definidos en `language.i18n`.**

## Reglas

### 1. Idioma como raíz de navegación

Dentro de `framework/`, el primer nivel de directorio es **siempre** el código del idioma conforme BCP 47 (ej: `pt-BR`, `es`, `en`). Todo el árbol de clades, subclades y pilares se replica dentro de cada carpeta de idioma:

```
framework/
├── pt-BR/
│   └── _foundation/process/lexis/lex-directives.md
├── es/
│   └── _foundation/process/lexis/lex-directives.md
└── en/
    └── _foundation/process/lexis/lex-directives.md
```

### 2. Completitud obligatoria

Todo artefacto creado en el idioma predeterminado (`language.default`) **DEBE** tener versiones correspondientes en todos los demás idiomas listados en `language.i18n`. Un artefacto se considera incompleto mientras no exista en todos los idiomas obligatorios.

### 3. Equivalencia estructural

Las versiones en diferentes idiomas **DEBEN** mantener la misma estructura de directorios. Si un artefacto existe en `pt-BR/_foundation/process/lexis/lex-directives.md`, **DEBE** existir en la misma ruta relativa en cada idioma.

### 4. Cursor en idioma único

Los archivos `.mdc` en el directorio `.cursor/` **DEBEN** estar escritos exclusivamente en el idioma definido en `language.cursor` en `.ahrena/.directives`. Cursor **NO** utiliza carpetas de idioma — solo se mantiene un idioma.

### 5. Propagación de cambios

Cuando un artefacto en el idioma predeterminado es modificado, las versiones en los demás idiomas **DEBEN** ser actualizadas. El agente que realiza la modificación **DEBE** señalar la necesidad de actualización de las traducciones.

### 6. Idioma predeterminado como fuente de verdad

El artefacto en el idioma definido en `language.default` es la **fuente de verdad**. En caso de divergencia entre versiones, el contenido en el idioma predeterminado prevalece.

### 7. Sin contenido suelto en la raíz

Ningún artefacto `.md` debe existir directamente en `framework/` fuera de las carpetas de idioma, excepto archivos de meta-configuración como `.directives.sample`.

## Alcance

- **Se aplica a:** estructura de directorios dentro de `framework/`
- **Agentes vinculados:** todos los Warriors y agentes genéricos
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de Violación

1. **Artefacto incompleto:** un artefacto que no exista en todos los idiomas obligatorios se considera incompleto.
2. **Navegación rota:** artefactos fuera de la estructura `{lang}/` quiebran la navegabilidad del framework.
3. **Remediación:** el agente debe crear las carpetas y versiones faltantes, utilizando el `warrior-translator` de `documentation/i18n/`.

## Referencias

- `codex-framework-language` — Manual estructural complementario a esta Lexis
- `documentation/i18n/` — Artefactos de traducción (lex/codex por idioma, kata, warrior, cry)
- `.ahrena/.directives` — Fuente de verdad para configuración de idiomas
