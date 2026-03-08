# Codex: Cómo Escribir Buenos Warriors

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Creación de Warriors (agentes especializados)

## Visión General

Este Codex documenta cómo diseñar agentes especializados eficaces en Ahrena. Aborda el diseño de identidad y persona, el alcance de responsabilidades, la cadena de consulta y los criterios de escalamiento. Es consultado por `kata-create-warrior` durante la creación de nuevos Warriors.

## Contexto

- **Dominio:** Diseño de agentes de IA con identidad y alcance definidos
- **Público objetivo:** Agentes de IA que ejecutan `kata-create-warrior` y mantenedores del framework
- **Actualización:** Cuando se identifiquen nuevos estándares de calidad para Warriors

## Contenido

### Principios

1. **Identidad clara:** Un Warrior debe tener nombre, papel y persona que lo distingan. La identidad no es cosmética — ancla el comportamiento esperado.
2. **Alcance delimitado:** Lo que un Warrior "Hace" es tan importante como lo que "No Hace". Las responsabilidades vagas llevan a superposición y conflicto entre Warriors.
3. **Consulta explícita:** Todo Warrior debe declarar qué Lexis sigue, qué Codex consulta y qué Katas ejecuta. Sin esto, el comportamiento es impredecible.
4. **Escalamiento definido:** Un Warrior debe saber cuándo detenerse y solicitar ayuda humana. La autonomía sin límites es un riesgo.

### Anatomía de un Buen Warrior

| Sección | Propósito | Criterio de Calidad |
|---------|-----------|---------------------|
| **Identidad** | Nombre, papel, dominio y persona | Nombres memorables; persona que informa el tono |
| **Misión** | Propósito central en 1-2 frases | Específica y accionable |
| **Responsabilidades** | Hace / No Hace | Listas equilibradas y sin ambigüedad |
| **Consulta** | Lexis, Codex y Katas referenciados | Tablas con identificador y descripción |
| **Comportamiento** | Tono, flujo de actuación, escalamiento | Concreto y verificable |
| **Ejemplo de Interacción** | Escenario de uso real | Input del usuario + respuesta del Warrior |

### Diseño de Identidad

La identidad de un Warrior orienta su comportamiento:

| Elemento | Función | Directriz |
|----------|---------|-----------|
| **Nombre** | Identificación y memorabilidad | Nombres mitológicos, históricos o simbólicos que evoquen el papel |
| **Papel** | Qué hace en términos profesionales | Título claro (ej: "Arquitecto de Software", "Traductor Especialista") |
| **Dominio** | Dónde actúa | Área específica (ej: "decisiones arquitectónicas y calidad de código") |
| **Persona** | Cómo se comporta | 2-3 adjetivos que definen el tono (ej: "metódico, riguroso, enfocado en trade-offs") |

### Diseño de Responsabilidades

La sección "Hace" / "No Hace" define el contorno del Warrior:

**Buen "Hace":**
- Elabora ADRs con análisis de trade-offs
- Revisa PRs con enfoque en arquitectura

**Mal "Hace":**
- Ayuda con código (demasiado vago)
- Hace todo lo relacionado con backend (alcance infinito)

**Buen "No Hace":**
- No toma decisiones de producto (eso corresponde al PM)
- No hace deploy en producción (eso corresponde a DevOps)

**Mal "No Hace":**
- No hace cosas malas (obvio e inútil)

### Diseño de la Cadena de Consulta

Todo Warrior declara tres tablas de referencia:

1. **Lexis** — las leyes que obedece (siempre `lex-directives` + otras)
2. **Codex** — los manuales que consulta para tomar decisiones
3. **Katas** — los procedimientos que ejecuta

La cadena debe ser completa: si el Warrior ejecuta una tarea, debe existir un Kata correspondiente. Si toma decisiones sobre un dominio, debe existir un Codex correspondiente.

### Diseño de Escalamiento

Los criterios de escalamiento definen cuándo el Warrior se detiene y solicita ayuda:

| Tipo | Ejemplo |
|------|---------|
| Impacto alto | "La decisión impacta más de 3 módulos" |
| Costo financiero | "El trade-off involucra un costo significativo" |
| Conflicto de reglas | "Conflicto entre Lexis y requisito de negocio" |
| Incertidumbre | "Información insuficiente para tomar una decisión" |

### Estándares y Convenciones

| Aspecto | Estándar | Ejemplo |
|---------|----------|---------|
| Nomenclatura | `warrior-{nombre-en-kebab-case}` | `warrior-spartacus` |
| Nombre del Warrior | Sustantivo propio memorable | Hermes, Spartacus, Athena |
| Misión | Máximo 2 frases en blockquote | > "Garantizar que toda decisión arquitectónica sea documentada..." |
| Ejemplo de interacción | Input real del usuario + respuesta estructurada | Demuestra el tono y el flujo del Warrior |

### Errores Comunes

| Error | Problema | Solución |
|-------|----------|----------|
| Warrior genérico | "Asistente de código" — sin identidad | Definir papel, dominio y persona específicos |
| Alcance ilimitado | Hace todo, no se especializa en nada | Usar "No Hace" para delimitar |
| Sin cadena de consulta | Comportamiento impredecible | Declarar Lexis, Codex y Katas explícitamente |
| Sin escalamiento | El Warrior decide cosas que no debería | Definir criterios claros de cuándo detenerse |
| Persona decorativa | Nombre mitológico sin conexión con el papel | Elegir nombre que evoque la especialidad |

### Warrior vs Agente Genérico — Cuándo Crear

| Situación | Respuesta | Por qué |
|-----------|----------|---------|
| Tarea recurrente con alcance continuo | Warrior | Necesita identidad y contexto persistente |
| Tarea puntual ejecutada por cualquier agente | Kata | El procedimiento es suficiente |
| Múltiples agentes con la misma especialidad | Warrior | Evita reconfigurar contexto cada vez |
| Dominio con tono y comportamiento específicos | Warrior | La persona garantiza consistencia |

### Restricciones Técnicas

- Todo Warrior debe incluir al menos una Lexis en la cadena de consulta (`lex-directives` como mínimo)
- La sección "Ejemplo de Interacción" debe contener un escenario completo (input + output)
- El nombre del archivo debe seguir el patrón `warrior-{nombre}.md`
- La misión debe ser una cita en blockquote

## Glosario

| Término | Definición |
|---------|-----------|
| Persona | Conjunto de características de comportamiento que definen el tono del Warrior |
| Cadena de consulta | Conjunto de Lexis, Codex y Katas que el Warrior referencia |
| Escalamiento | Transferencia de decisión a un humano cuando el Warrior alcanza sus límites |
| Alcance | Delimitación de lo que el Warrior hace y no hace |

## Referencias

- `codex-pilars` — Visión general del sistema de Pilares
- `lex-template-usage` — Ley de uso obligatorio de templates
- `kata-create-warrior` — Procedimiento para crear nuevos Warriors
- `templates/warrior-sample.md` — Template oficial de Warriors
