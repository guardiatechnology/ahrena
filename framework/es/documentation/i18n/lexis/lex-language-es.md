# Lexis: Reglas para Traducir al Español

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Traducción de documentación técnica al español (es)

## Propósito

Esta Lexis define las reglas específicas para traducir documentación técnica **al Español neutro (es)**. Complementa la `lex-language` (reglas transversales) con particularidades lingüísticas, estilísticas y culturales del español.

## Ley

> **Toda traducción al español DEBE seguir las reglas transversales de `lex-language` Y las reglas específicas definidas en esta Lexis.**

## Reglas

### 1. Variante del español

Usar **español neutro** — sin regionalismos de España, México, Argentina ni ningún otro país. El objetivo es producir documentación comprensible para cualquier hablante de español.

### 2. Formalidad

Mantener formalidad implícita adecuada a documentación técnica:
- Voz impersonal cuando sea apropiado ("Se debe configurar..." en vez de "Tú debes configurar...")
- Evitar lenguaje coloquial
- Tono profesional y accesible

### 3. Consistencia de tratamiento

**NO** mezclar "tú" y "usted" en el mismo documento. Elegir uno y mantener consistencia. Para documentación técnica, preferir construcciones impersonales.

### 4. Falsos cognatos con pt-BR

Atención especial a falsos cognatos entre pt-BR y español:

| Portugués | Español (CORRECTO) | Falso cognato (INCORRECTO) |
|-----------|--------------------|-----------------------------|
| esquisito (extraño) | extraño, raro | exquisito (= refinado) |
| polvo (molusco) | pulpo | polvo (= polvo/partículas) |
| largo (amplio) | amplio, ancho | largo (= largo/extenso) |
| escritório (oficina) | oficina | escritorio (= mueble) |
| sobrenome (apellido) | apellido | sobrenombre (= apodo) |
| acordar (despertar) | despertar | acordar (= acordar/recordar) |
| vaso (recipiente) | jarrón, florero | vaso (= vaso para beber) |

### 5. Términos técnicos en inglés

Los términos técnicos universales **DEBEN** mantenerse en inglés:
- commit, merge, branch, pull request, framework, deploy
- Cuando traducir: workflow → flujo de trabajo, output → salida, input → entrada

### 6. Verbos modales

| Inglés | Español |
|--------|---------|
| MUST | DEBE |
| MUST NOT | NO DEBE / NO PUEDE |
| SHOULD | DEBERÍA / SE RECOMIENDA |
| MAY | PUEDE |

### 7. Puntuación y ortografía

- Usar correctamente los signos de apertura de interrogación (¿) y exclamación (¡)
- Acentuación conforme las reglas de la RAE
- Atención al uso correcto de "solo" (sin tilde según norma vigente)

## Alcance

- **Se aplica a:** toda traducción cuyo idioma destino sea español (es)
- **Agentes vinculados:** `warrior-translator` y cualquier agente que traduzca al español
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de Violación

1. **Traducción inconsistente:** texto que no siga las reglas de esta Lexis puede generar mezcla de tratamiento, falsos cognatos o desvío del español neutro.
2. **Rechazo en revisión:** traducciones al español que violen las reglas deben corregirse antes de ser aceptadas en el framework.
3. **Remediación:** el agente debe consultar `codex-language-es` y esta Lexis y reaplicar las reglas al texto traducido.

## Ejemplos

### Correcto

- "El agente **DEBE** consultar el .directives." (voz impersonal, DEBE en mayúsculas)
- "Se recomienda usar el flujo de trabajo definido." (workflow → flujo de trabajo; construcción impersonal)

### Incorrecto

- "El agente tiene que consultar el .directives." (evitar "tiene que"; usar "DEBE")
- "Configurar el escritorio" cuando el contexto es "office" (usar "oficina", no "escritorio")
- Mezclar "tú" y "usted" en el mismo documento.

## Referencias

- `lex-language` — Reglas transversales (esta Lexis complementa)
- `codex-language-es` — Guía detallada para traducción al español
