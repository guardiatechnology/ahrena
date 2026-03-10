# Codex: Tono y Estilo de Escritura

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Aplicación de tone_and_writing_style en el Ahrena

## Visión general

Este Codex detalla cómo interpretar y aplicar las directrices de tono y estilo de escritura definidas en `naming.tone_and_writing_style` en el archivo `.ahrena/.directives`. Complementa la `lex-tone` (que establece la obligación) con ejemplos de texto alineado y desalineado y orientaciones por tipo de contenido. Use este Codex al redactar o revisar artefatos y comunicación en el contexto del Ahrena.

## Contexto

- **Dominio:** Tono, estilo y claridad en la producción de texto del framework
- **Público objetivo:** Agentes de IA que redactan artefatos o comunicación; revisores de contenido
- **Actualización:** Cuando las directrices en el `.directives` sean alteradas o se necesiten nuevos ejemplos

## Contenido

### Origen de las directrices

Las directrices están en `.ahrena/.directives`, sección `naming.tone_and_writing_style`, en general como una lista de frases. Cada ítem es una regla de estilo que el agente debe seguir. La `lex-tone` exige que todo agente las aplique; este Codex explica cómo.

### Interpretación de las directrices típicas

| Directriz (ejemplo) | Interpretación | Aplicación |
|---------------------|----------------|------------|
| Estilo directo y estratégico, guiado por claridad, datos y propósito | Evitar rodeos; estructurar argumentos con lógica; usar Why/What/How o Problema/Causa/Solución cuando sea útil | Introducciones y conclusiones objetivas; secciones con tópicos claros |
| Evitar adornos o abstracciones que desvíen de lo esencial | Cortar frases decorativas; cada frase debe añadir información o acción | Eliminar "Es importante notar que...", "Cabe destacar..." cuando no sean necesarios |
| Apoyar afirmaciones con números, evidencia o referencias verificables | Cuando tenga sentido, citar métricas, fuentes o criterios concretos | En secciones de Validación, Consecuencias, Ejemplos |
| Tono que combine confianza, accesibilidad y visión práctica | Escribir con seguridad sin ser arrogante; ser útil y accionable | Instrucciones en imperativo ("DEBE", "Consulte"); evitar hesitación innecesaria |
| Ambición ligada a viabilidad | Grandes ideas acompañadas de pasos concretos | En propósitos y objetivos: no solo "qué" sino "cómo" cuando sea relevante |
| Evitar guiones o dos puntos para contextualizar (salvo que se pida) | Usar paréntesis para matices dentro de la frase; reservar puntos suspensivos para interrupción o continuación | Preferir "El agente debe consultar el archivo (conforme lex-directives)" a "El agente debe — conforme lex-directives — consultar el archivo" |
| Eliminar buzzwords sin significado | Usar vocabulario técnico solo cuando sea necesario y con concepto claro | Evitar "solución disruptiva", "innovación" vaga; preferir términos precisos |
| Respuestas que ayuden a decidir y avanzar | El texto debe orientar decisión o acción, no solo informar | Incluir "Próximo paso", "Recomendación" o conclusión accionable cuando tenga sentido |
| Para correos, posts o contenido para terceros: entregar solo el texto final | Cuando el usuario pida redacción para compartir, no añadir comentario ni introducción; solo el contenido listo | Respetar peticiones explícitas de "solo el texto" o "listo para enviar" |

### Ejemplos: alineado vs desalineado

**Alineado:**

- "Todo artefato DEBE usar el prefijo del Pilar definido en `.directives`."
- "Si la sección `terminal` no existe, el agente infiere por el sistema operativo o pregunta al usuario."
- "La cadena de invocación es: Cry → (Warrior) → Kata. Lexis y Codex son consultados, no invocados por el Cry."

**Desalineado:**

- "Es fundamental que los artefatos utilicen el prefijo correcto." (menos imperativo; preferir "DEBE")
- "Cuando no haya terminal, puede inferirse o preguntar." (vago; especificar agente y acción)
- "La cosa toda funciona así: el Cry llama algo, y ahí Lexis y Codex entran en la historia." (informal e impreciso)

### Por tipo de artefato

| Tipo | Foco del tono |
|------|----------------|
| Lexis | Declaración imperativa clara; consecuencias concretas; sin excepciones |
| Codex | Referencia objetiva; tablas y listas; gatillos de actualización explícitos |
| Katas | Pasos accionables; inputs/outputs claros; validación verificable |
| Warriors | Identidad y alcance nítidos; "Hace" y "No hace" concretos |
| Cries | Descripción en una frase; prompt template con tarea y formato de salida |

### Restricciones técnicas

- El agente no debe inventar directrices; debe aplicar solo las listadas en `naming.tone_and_writing_style` (o el equivalente por defecto cuando la sección no exista).
- En caso de conflicto entre dos directrices, priorizar claridad y acción (lo que ayuda más al lector a decidir o ejecutar).

## Glosario

| Término | Definición |
|---------|------------|
| tone_and_writing_style | Sección opcional en `.ahrena/.directives` (bajo `naming`) que lista directrices de tono y estilo |
| Estilo directo | Frases objetivas, sin rodeos ni adornos innecesarios |
| Accionable | Contenido que lleva a una decisión o acción clara |

## Referencias

- `lex-tone` — Ley que obliga a la aplicación del tono y estilo
- `lex-directives` — Consulta obligatoria al `.ahrena/.directives`
- `codex-directives` — Manual del archivo .directives (sección naming)
