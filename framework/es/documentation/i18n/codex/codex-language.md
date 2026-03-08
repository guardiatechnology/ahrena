# Codex: Guía Transversal de Traducción

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Orientaciones generales para traducción de documentación técnica

## Visión General

Este Codex proporciona orientaciones prácticas para traducir documentación técnica en cualquier combinación de idiomas. Es la guía transversal que complementa la `lex-language` (ley de traducción) y antecede las guías específicas por idioma (`codex-language-ptbr`, `codex-language-en`, `codex-language-es`).

## Contexto

- **Dominio:** Traducción de documentación técnica
- **Público objetivo:** `warrior-translator` (Hermes) y cualquier agente que ejecute traducciones
- **Actualización:** siempre que se establezcan nuevas convenciones transversales

## Contenido

### Cómo Identificar Idioma Fuente e Idioma Destino

1. **Idioma fuente:** determinado por la ruta del archivo. El primer segmento después de `framework/` indica el idioma (ej: `framework/pt-BR/...` → fuente es pt-BR).
2. **Idioma destino:** definido por el parámetro de la solicitud o por `language.i18n` en `.ahrena/.directives`.
3. **Idioma predeterminado:** definido en `language.default` — es la fuente de verdad cuando hay divergencia.

### Preservación de Estructura Markdown

Al traducir, preservar rigurosamente:

| Elemento | Acción |
|----------|--------|
| Headings (`#`, `##`, `###`) | Traducir el texto, mantener la jerarquía |
| Tablas | Traducir contenido de celdas, mantener estructura |
| Listas | Traducir ítems, mantener orden |
| Bloques de código (`` ``` ``) | **Nunca** traducir contenido |
| Blockquotes (`>`) | Traducir texto, mantener formato |
| Links y URLs | **Nunca** alterar URLs. Traducir texto del enlace si es necesario |
| Frontmatter YAML | **Nunca** traducir claves. Traducir valores de `description` |

### Glosario de Términos Intraducibles

Estos términos **NUNCA** se traducen:

**Términos de Ahrena:**
- Lexis, Codex, Katas, Warriors, Cries
- Ahrena, Clade, Subclade, Pilar

**Términos técnicos universales:**
- commit, merge, branch, pull request, push, pull
- deploy, rollback, hotfix
- framework, middleware, API, SDK, CLI
- Markdown, YAML, JSON, HTML, CSS

### Ejemplos de Buenas y Malas Traducciones

#### Buena traducción (pt-BR → en)

**Original (pt-BR):**
> O agente **DEVE** ler o `.ahrena/.directives` antes de iniciar qualquer atividade.

**Traducción (en):**
> The agent **MUST** read `.ahrena/.directives` before starting any activity.

#### Mala traducción (pt-BR → en)

**Original (pt-BR):**
> O agente **DEVE** ler o `.ahrena/.directives` antes de iniciar qualquer atividade.

**Traducción (en):**
> The agent should check the Ahrena directives file before it begins.

- "DEVE" (obligatorio) rebajado a "should" (recomendación)
- Ruta `.ahrena/.directives` sustituida por texto genérico

### Flujo de Consulta por Traducción

1. `lex-language` — reglas transversales obligatorias
2. `lex-language-{lang}` — reglas del idioma destino
3. `codex-language` — esta guía transversal
4. `codex-language-{lang}` — guía específica del idioma destino

## Referencias

- `lex-language` — Ley transversal de traducción
- `lex-language-ptbr`, `lex-language-en`, `lex-language-es` — Leyes por idioma destino
- `codex-language-ptbr`, `codex-language-en`, `codex-language-es` — Guías por idioma destino
- `kata-translate` — Procedimiento coordinador
- `warrior-translator` — Agente de traducción (Hermes)
