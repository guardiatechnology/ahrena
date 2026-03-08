# Lexis: Reglas para Traducir al Portugués Brasileño

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Traducción de documentación técnica al pt-BR

## Propósito

Esta Lexis define las reglas específicas para traducir documentación técnica **al Portugués Brasileño (pt-BR)**. Complementa la `lex-language` (reglas transversales) con particularidades lingüísticas, estilísticas y culturales del pt-BR.

## Ley

> **Toda traducción al pt-BR DEBE seguir las reglas transversales de `lex-language` Y las reglas específicas definidas en esta Lexis.**

## Reglas

### 1. Pronombre de tratamiento

Usar **"você"** como pronombre de tratamiento. Nunca usar "tu", "vós" o tratamiento excesivamente formal como "Vossa Senhoria". El tono es técnico-accesible.

### 2. Norma culta

La traducción **DEBE** seguir la norma culta del Portugués Brasileño:
- Acentuación rigurosa (é, á, ã, ç, etc.)
- Puntuación correcta
- Concordancia verbal y nominal
- Regencia verbal y nominal

### 3. Términos técnicos en inglés

Los términos técnicos consolidados en la comunidad tecnológica **DEBEN** mantenerse en inglés cuando no hay equivalente consolidado en pt-BR:

| Mantener en inglés | Traducir |
|--------------------|----------|
| deploy | implantar (cuando verbo genérico) |
| commit | — (nunca traducir) |
| merge | — (nunca traducir) |
| branch | — (nunca traducir) |
| pull request | — (nunca traducir) |
| framework | — (nunca traducir) |
| workflow | fluxo de trabalho |
| output | saída |
| input | entrada |

### 4. Anglicismos

Evitar anglicismos cuando hay equivalente consolidado en pt-BR:
- **"excluir"** y no "deletar"
- **"configurar"** y no "setar"

### 5. Tono

Tono **formal-accesible**: técnico sin ser rebuscado, directo sin ser coloquial.

### 6. Verbos modales

| Inglés | Portugués |
|--------|-----------|
| MUST | DEVE |
| MUST NOT | NÃO DEVE / NÃO PODE |
| SHOULD | DEVERIA / RECOMENDA-SE |
| MAY | PODE |

### 7. Estructuras formales

Para instrucciones y documentación técnica:
- "O agente **DEVE**..." (no "O agente tem que...")
- "É necessário..." (no "Precisa...")

## Alcance

- **Se aplica a:** toda traducción cuyo idioma destino sea pt-BR
- **Agentes vinculados:** `warrior-translator` y cualquier agente que traduzca al pt-BR
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Referencias

- `lex-language` — Reglas transversales (esta Lexis complementa)
- `codex-language-ptbr` — Guía detallada para traducción al pt-BR
