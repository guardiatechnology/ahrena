# Lexis: Reglas para Traducir al Inglés

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Traducción de documentación técnica al inglés (en)

## Propósito

Esta Lexis define las reglas específicas para traducir documentación técnica **al Inglés (en)**. Complementa la `lex-language` (reglas transversales) con particularidades lingüísticas y estilísticas del inglés técnico.

## Ley

> **Toda traducción al inglés DEBE seguir las reglas transversales de `lex-language` Y las reglas específicas definidas en esta Lexis.**

## Reglas

### 1. Variante del inglés

Usar **American English** como estándar. Mantener consistencia en todo el documento:
- "color" (no "colour")
- "organization" (no "organisation")

### 2. Voz y tiempo verbal

Usar **voz activa** y **presente del indicativo** en instrucciones:
- "The agent reads the directives" (no "The directives are read by the agent")
- "Run the command" (no "The command should be run")

### 3. Concisión

Priorizar **frases cortas y directas**:
- Eliminar redundancia ("in order to" → "to")
- Evitar circunloquios
- Una idea por frase cuando sea posible

### 4. Terminología industry-standard

| Preferir | Evitar |
|----------|--------|
| execute | perform/carry out |
| create | generate/produce (genérico) |
| delete | remove/eliminate (acción técnica) |
| configure | set up (contexto formal) |

### 5. Tono

Tono **profesional-neutro**: claro, preciso, sin lenguaje coloquial.
- Evitar contracciones en documentación formal ("do not" en vez de "don't")
- Mantener consistencia de registro

### 6. Verbos modales (RFC 2119)

| Modal | Significado |
|-------|-------------|
| MUST | Obligatorio — sin excepción |
| MUST NOT | Prohibido — sin excepción |
| SHOULD | Recomendado — excepciones justificadas |
| MAY | Opcional |

### 7. Errores comunes al traducir desde pt-BR/es

| Error común | Correcto |
|-------------|----------|
| "realize" (≠ realizar) | "perform" o "carry out" |
| "actually" (≠ atualmente/actualmente) | "currently" |
| "pretend" (≠ pretender) | "intend" |

## Alcance

- **Se aplica a:** toda traducción cuyo idioma destino sea inglés (en)
- **Agentes vinculados:** `warrior-translator` y cualquier agente que traduzca al inglés
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Referencias

- `lex-language` — Reglas transversales (esta Lexis complementa)
- `codex-language-en` — Guía detallada para traducción al inglés
