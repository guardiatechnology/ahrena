# Lexis: Tono y Estilo de Escritura Obligatorios

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Producción de artefatos y comunicación en el contexto Ahrena

## Propósito

El archivo `.ahrena/.directives` puede contener la sección `naming.tone_and_writing_style` con directrices de tono y estilo de escritura (claridad, objetividad, uso de evidencia, eliminación de buzzwords, entre otras). Esas directrices garantizan que artefatos y comunicación producidos en el contexto del Ahrena sean consistentes, profesionales y accionables. Sin una Ley que obligue a la aplicación de ese tono, los agentes pueden producir texto vago, ornamental o fuera del estándar definido por el proyecto.

Esta Lexis existe para garantizar que **todo agente aplique el tono y el estilo de escritura** definidos en `naming.tone_and_writing_style` (en `.ahrena/.directives`) al producir artefatos y comunicación en el contexto del Ahrena.

## Ley

> **Todo agente DEBE aplicar las directrices de tono y estilo de escritura definidas en `naming.tone_and_writing_style` en el archivo `.ahrena/.directives` al producir artefatos (Lexis, Codex, Katas, Warriors, Cries), documentación y comunicación en el contexto del Ahrena. Si la sección no existe, el agente DEBE adoptar tono directo, estratégico y basado en claridad y propósito.**

## Reglas

### 1. Consulta a las directrices

Al producir texto en el contexto del Ahrena, el agente **DEBE**:

1. Consultar `.ahrena/.directives` (conforme `lex-directives`).
2. Verificar si existe la sección `naming.tone_and_writing_style`.
3. Si existe, internalizar cada ítem de la lista y aplicarlo al redactar o revisar contenido.
4. Si no existe, adoptar principios equivalentes: estilo directo y estratégico, claridad, datos y propósito; evitar adornos y abstracciones que desvíen de lo esencial.

### 2. Alcance de aplicación

El tono y el estilo se aplican a:

- Contenido de artefatos del framework (Ley, Propósito, Contenido, Ejemplos, etc.).
- Documentación generada en el contexto del proyecto (README, ADRs, comentarios en código cuando sean documentación).
- Comunicación producida por el agente en respuesta a solicitudes en el contexto Ahrena (respuestas, resúmenes, instrucciones).

No se aplica a código fuente (variables, funciones) salvo cuando el usuario solicite que comentarios o documentación inline sigan el mismo estilo.

### 3. No modificación de la sección sin autorización

El agente **NO PUEDE** añadir o alterar la sección `naming.tone_and_writing_style` en `.ahrena/.directives` sin solicitud explícita del usuario.

## Alcance

- **Se aplica a:** toda producción de texto (artefatos, documentación, comunicación) en el contexto del Ahrena.
- **Agentes vinculados:** todos los Warriors y agentes genéricos que redactan o editan contenido.
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de violación

1. **Inconsistencia de tono:** artefatos con estilo divergente perjudican la experiencia de lectura y la autoridad del framework.
2. **Retrabajo:** contenido que no siga las directrices debe ser revisado para conformidad.
3. **Remediación:** el agente debe releer `naming.tone_and_writing_style` y `codex-tone` y reescribir el texto en conformidad.

## Ejemplos

### Alineado al tono (directrices típicas)

- Frase directa y con propósito: "Todo artefato DEBE usar el prefijo del Pilar."
- Evitar adornos: preferir "La Ley establece la obligación" a "Es importante destacar que la Ley viene a establecer la obligación."
- Apoyar en estructura lógica: usar Why/What/How o Problema/Causa/Solución cuando tenga sentido.

### Desalineado

- Texto vago: "La cosa debe hacerse de forma adecuada."
- Buzzword sin significado: "Solución disruptiva e innovadora."
- Exceso de guiones o dos puntos para contextualizar: "El framework — que es muy importante — debe usarse — siempre — de la siguiente forma:"

## Validación automatizada

- **Herramienta:** revisión humana o por el propio agente con checklist basado en `codex-tone`.
- **Momento:** en la creación o revisión de artefatos y en la entrega de comunicación.
- **Métrica:** el contenido producido debe estar en conformidad con las directrices de `tone_and_writing_style` cuando la sección exista.

## Referencias

- `lex-directives` — Consulta obligatoria al `.ahrena/.directives`
- `codex-tone` — Cómo interpretar y aplicar cada ítem de tone_and_writing_style
- `codex-directives` — Significado de la sección naming en el .directives
