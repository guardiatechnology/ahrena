# Sistema de Traducción de Ahrena

> Documentación completa del sistema de internacionalización y traducción de documentación técnica.

## Visión General

El sistema de traducción de Ahrena es un conjunto de artefactos que permite traducir cualquier documentación técnica en Markdown de forma consistente, con reglas y guías específicas por idioma. Fue diseñado para ser **genérico** — funciona para documentación del framework Ahrena, de proyectos y de cualquier otro contenido técnico.

El sistema está compuesto por **Lexis** (leyes), **Codex** (guías), un **Kata** (procedimiento), un **Warrior** (agente) y un **Cry** (comando), organizados en el Clade `documentation/i18n/`.

## Arquitectura

```mermaid
flowchart TD
    subgraph invocation ["Invocación"]
        Cry["cry-translate\n(comando rápido)"]
    end

    subgraph agent ["Agente"]
        Warrior["warrior-translator\n(Hermes)"]
    end

    subgraph procedure ["Procedimiento"]
        Kata["kata-translate\n(6 pasos)"]
    end

    subgraph rules ["Reglas por Idioma"]
        LexTrans["lex-language\n(transversal)"]
        LexPtBR["lex-language-ptbr"]
        LexEn["lex-language-en"]
        LexEs["lex-language-es"]
    end

    subgraph guides ["Guías por Idioma"]
        CodexTrans["codex-language\n(transversal)"]
        CodexPtBR["codex-language-ptbr"]
        CodexEn["codex-language-en"]
        CodexEs["codex-language-es"]
    end

    subgraph structure ["Estructura (foundation)"]
        LexFwk["lex-framework-language"]
        CodexFwk["codex-framework-language"]
    end

    Cry -->|"invoca"| Warrior
    Warrior -->|"ejecuta"| Kata
    Kata -->|"consulta"| LexTrans
    Kata -->|"consulta por idioma"| LexPtBR
    Kata -->|"consulta por idioma"| LexEn
    Kata -->|"consulta por idioma"| LexEs
    Kata -->|"consulta"| CodexTrans
    Kata -->|"consulta por idioma"| CodexPtBR
    Kata -->|"consulta por idioma"| CodexEn
    Kata -->|"consulta por idioma"| CodexEs
    Warrior -->|"en contexto Ahrena"| LexFwk
```

## Inventario de Artefactos

### `documentation/i18n/` (traducción genérica)

| Artefacto | Tipo | Descripción |
|-----------|------|-------------|
| `lex-language` | Lexis | Reglas **transversales** de traducción |
| `lex-language-ptbr` | Lexis | Reglas para traducir **al pt-BR** |
| `lex-language-en` | Lexis | Reglas para traducir **al inglés** |
| `lex-language-es` | Lexis | Reglas para traducir **al español** |
| `codex-language` | Codex | Guía **transversal** de traducción |
| `codex-language-ptbr` | Codex | Guía para traducir **al pt-BR** |
| `codex-language-en` | Codex | Guía para traducir **al inglés** |
| `codex-language-es` | Codex | Guía para traducir **al español** |
| `kata-translate` | Kata | Procedimiento de traducción en **6 pasos** |
| `warrior-translator` | Warrior | Agente **Hermes** — traductor especialista |
| `cry-translate` | Cry | Comando rápido con **orden de traducción** |

### `_foundation/i18n/` (estructura del framework)

| Artefacto | Tipo | Descripción |
|-----------|------|-------------|
| `lex-framework-language` | Lexis | Idioma como raíz de navegación en `framework/` |
| `codex-framework-language` | Codex | Manual de organización de carpetas por idioma |

## Cómo Usar

### Traducir un documento a todos los idiomas

```
/cry-translate framework/pt-BR/_foundation/process/lexis/lex-directives.md
```

### Traducir a un idioma específico

```
/cry-translate docs/architecture.md en
```

### Traducir con orden personalizado

```
/cry-translate docs/api.md es,en --order en,es
```

## Extensibilidad: Agregando un Nuevo Idioma

Para agregar un nuevo idioma (ej: japonés `ja`):

1. **Actualizar `.ahrena/.directives`:** agregar `ja` a `language.i18n`
2. **Crear artefactos de traducción:** `lex-language-ja` y `codex-language-ja`
3. **Crear la carpeta de idioma:** `framework/ja/` con estructura reflejada
4. **Traducir artefactos existentes:** usar `cry-translate` para cada documento

Los artefactos transversales **no necesitan ser alterados** — ya soportan cualquier idioma via `lex-language-{lang}`.

## Relación con `_foundation/i18n/`

| Clade | Responsabilidad |
|-------|-----------------|
| `_foundation/i18n/` | **Estructura:** cómo las carpetas de idioma se organizan |
| `documentation/i18n/` | **Traducción:** cómo traducir contenido con calidad |

## Referencias

- `.ahrena/.directives` — Fuente de verdad para idiomas
- `lex-framework-language` — Ley estructural de idiomas del framework
- `codex-framework-language` — Manual estructural de idiomas del framework
