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

## Consecuencias de Violación

1. **Traducción inconsistente:** texto que no siga las reglas de esta Lexis puede generar mezcla de tratamiento, anglicismos innecesarios o desvío de la norma culta.
2. **Rechazo en revisión:** traducciones al pt-BR que violen las reglas deben corregirse antes de ser aceptadas en el framework.
3. **Remediación:** el agente debe consultar `codex-language-ptbr` y esta Lexis y reaplicar las reglas al texto traducido.

## Ejemplos

### Correcto

- "El agente **DEBE** consultar el .directives." (voz activa, DEBE en mayúsculas, término técnico en inglés preservado)
- "Se recomienda usar el flujo de trabajo definido." (workflow traducido; construcción impersonal)

### Incorrecto

- "El agente tiene que consultar el .directives." (evitar "tiene que"; usar "DEBE")
- "Deletar el archivo" (usar "Excluir el archivo")

## Referencias

- `lex-language` — Reglas transversales (esta Lexis complementa)
- `codex-language-ptbr` — Guía detallada para traducción al pt-BR
