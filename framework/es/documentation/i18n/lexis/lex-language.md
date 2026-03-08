# Lexis: Reglas Transversales de Traducción

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Toda traducción de documentación técnica

## Propósito

Esta Lexis define las reglas universales que gobiernan cualquier traducción, independientemente del idioma destino. Son reglas transversales que se aplican **antes** de las reglas específicas de cada idioma (`lex-language-ptbr`, `lex-language-en`, `lex-language-es`).

El objetivo es garantizar que toda traducción preserve la fidelidad al contenido original, la integridad estructural del documento y la consistencia terminológica.

## Ley

> **Toda traducción DEBE preservar la equivalencia estructural y semántica del documento original, respetando las reglas transversales definidas en esta Lexis Y las reglas específicas del idioma destino definidas en `lex-language-{lang}`.**

## Reglas

### 1. Equivalencia estructural

La traducción **DEBE** mantener exactamente la misma estructura del original:
- Mismas secciones y headings (traducidos, pero en el mismo orden y jerarquía)
- Misma formatación Markdown (tablas, listas, bloques de código, blockquotes)
- Misma cantidad de secciones — nunca omitir, fusionar o reordenar

### 2. Fidelidad semántica

La traducción **DEBE** preservar el sentido original del texto. No es paráfrasis libre — es traducción técnica:
- El significado de cada frase debe ser equivalente al original
- Los matices técnicos deben preservarse
- Las instrucciones imperativas ("DEBE", "NO PUEDE") deben mantener la misma fuerza en el idioma destino

### 3. Preservación de elementos técnicos

Los siguientes elementos **NUNCA** deben ser traducidos o alterados:
- Bloques de código y sus contenidos
- Rutas de archivo (ej: `framework/pt-BR/`, `.ahrena/.directives`)
- URLs y enlaces
- Nombres de variables, funciones y comandos
- Nombres de archivos (ej: `lex-framework-language.md`)

### 4. Términos canónicos de Ahrena

Los nombres propios del framework **NUNCA** se traducen:
- **Lexis**, **Codex**, **Katas**, **Warriors**, **Cries**
- **Ahrena**, **Clade**, **Subclade**, **Pilar**
- Nombres de Warriors (ej: **Hermes**)

### 5. Jerarquía de reglas

Para cada traducción, el agente **DEBE** consultar:
1. Esta `lex-language` (reglas transversales — se aplican siempre)
2. `lex-language-{lang}` del idioma destino (reglas específicas — complementan las transversales)
3. `codex-language` (guía transversal de referencia)
4. `codex-language-{lang}` del idioma destino (guía específica)

Las reglas específicas del idioma **complementan** las transversales, pero **no las contradicen**.

### 6. Idioma fuente agnóstico

El traductor **NO** asume cuál es el idioma fuente. El idioma predeterminado se determina por `language.default` en `.ahrena/.directives`. El traductor sabe traducir **hacia** idiomas, no **desde** un idioma fijo.

### 7. Completitud de la traducción

Toda traducción **DEBE** ser completa. No se permite:
- Dejar fragmentos en el idioma original
- Usar marcadores como "TODO: traducir"
- Omitir secciones por complejidad

## Alcance

- **Se aplica a:** toda traducción de documentación técnica
- **Agentes vinculados:** `warrior-translator` y cualquier agente que ejecute traducción
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de Violación

1. **Traducción incompleta:** una traducción con secciones faltantes o fragmentos en el idioma original es rechazada.
2. **Pérdida de fidelidad:** una traducción que altera el sentido del original compromete la confiabilidad.
3. **Remediación:** el agente debe rehacer la traducción, consultando esta Lexis y la `lex-language-{lang}` del idioma destino.

## Referencias

- `lex-language-ptbr` — Reglas para traducir al Portugués Brasileño
- `lex-language-en` — Reglas para traducir al Inglés
- `lex-language-es` — Reglas para traducir al Español
- `codex-language` — Guía transversal de traducción
- `kata-translate` — Procedimiento coordinador de traducción
