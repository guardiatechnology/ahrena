# Codex: Diseño de Código y Clean Code

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Decisiones de diseño, legibilidad y refactorización en cualquier stack

## Resumen

Este Codex convierte Clean Code en criterios de decisión. No prescribe una estética universal: ayuda a equilibrar intención, cohesión, acoplamiento, simplicidad, evolución y riesgo operativo.

## Contexto

- **Dominio:** diseño interno de software y refactorización segura
- **Público objetivo:** agentes y personas que implementan o revisan código
- **Actualización:** cuando cambien analizadores, arquitectura canónica o el diccionario de patterns de Ahrena

## Contenido

### Principios

1. **Intención antes que brevedad:** el lector entiende la decisión de negocio sin reconstruir detalles accidentales.
2. **Cohesión antes que tamaño:** una unidad menor puede empeorar el diseño si separa datos y comportamiento relacionados.
3. **Abstracción con evidencia:** extraer ante variación real, política estable o repetición semántica; no por conteo mecánico.
4. **SOLID como diagnóstico:** usar los principios para formular riesgos, no como checklist para agregar interfaces.
5. **Cambio protegido:** la refactorización preserva comportamiento y comienza con evidencia ejecutable.

### Preguntas de Decisión

| Señal | Pregunta | Respuesta preferida |
|---|---|---|
| Función extensa | ¿Tiene más de una razón de negocio para cambiar? | Separar por responsabilidad observable |
| Duplicación | ¿Las copias representan la misma regla y cambian juntas? | Extraer; en otro caso tolerar semánticas distintas |
| Nueva interfaz | ¿Existe segundo consumidor o variación con evidencia? | Crear solo con evidencia |
| Muchos parámetros | ¿Forman un concepto de dominio? | Value Object o Parameter Object con invariantes |
| Condicional creciente | ¿Las ramas son políticas reemplazables? | Strategy/polimorfismo; no para un caso simple y estable |
| Dependencia externa | ¿El modelo externo se filtra al dominio? | Adapter o Anti-Corruption Layer |

### Los Smells Son Hipótesis

Un smell inicia una investigación; no prueba un defecto. Antes de elegir un pattern, registrar problema, presión de cambio, opción simple, opción estructural, trade-offs y criterio de reversión. Incluir siempre **cuándo no usarlo**.

### Refactorización Segura

1. Capturar el comportamiento actual con pruebas de caracterización cuando no esté protegido.
2. Establecer baseline de pruebas, análisis estático y performance relevante.
3. Hacer una transformación por vez y ejecutar las verificaciones confiables mínimas.
4. Preservar contratos públicos, datos, telemetría y semántica de fallos.
5. Separar cambio de comportamiento de reorganización estructural cuando facilite la revisión.

### Decisiones Vigentes

| Decisión | Estado | Consecuencia |
|---|---|---|
| Los límites objetivos viven en `lex-clean-code` | Confirmada | Este Codex conserva los trade-offs contextuales |
| Los patterns requieren `use_when`, `avoid_when` y trade-offs | Propuesta para Ahrena v2 | Evita cargo cult y prepara el diccionario consultable |

### Restricciones Técnicas

- No introducir un pattern sin nombrar el problema y cuándo evitarlo o retirarlo.
- No cambiar contratos, schemas o semántica de errores bajo el nombre de refactorización.
- No usar cobertura, complejidad o tamaño aislados como prueba de calidad.
- No incluir información sensible en comentarios, nombres, pruebas o telemetría.

## Glosario

| Término | Definición |
|---|---|
| Presión de cambio | Evidencia de que un área cambia por razones diferentes o recurrentes |
| Smell | Señal que merece investigación, no diagnóstico definitivo |
| Falsa abstracción | Compartir estructura entre conceptos con semánticas diferentes |

## Referencias

- `lex-clean-code`, `lex-dry`, `lex-no-silent-tech-debt`, `kata-safe-refactoring`
