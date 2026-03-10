# Codex: Cómo Escribir Buenos Katas

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Creación de Katas (procedimientos repetibles)

## Visión General

Este Codex documenta cómo diseñar procedimientos estructurados eficaces en Ahrena. Aborda la descomposición de tareas, el diseño de inputs y outputs, los criterios de validación y cuándo usar Kata vs Cry. Es consultado por `kata-create-kata` durante la creación de nuevos Katas. El kata usa este Codex en el **Paso 1** (lectura de criterios) y en el **Paso 3** (redacción de secciones); la **Validación Final** del Kata verifica las Restricciones Técnicas y la Anatomía descritas abajo.

## Contexto

- **Dominio:** Diseño de procedimientos estandarizados para agentes de IA
- **Público objetivo:** Agentes de IA que ejecutan `kata-create-kata` y mantenedores del framework
- **Actualización:** Cuando se identifiquen nuevos estándares de calidad para Katas

## Contenido

### Principios

1. **Reproducibilidad:** Dos agentes que ejecuten el mismo Kata con los mismos inputs deben producir outputs equivalentes.
2. **Progresividad:** Cada paso debe ser verificable antes de avanzar al siguiente. Si un paso falla, debe ser posible corregirlo sin empezar desde cero.
3. **Completitud:** El Kata debe cubrir el flujo completo — del input al output validado. No debe depender de conocimiento implícito.
4. **Atomicidad de los pasos:** Cada paso ejecuta una única acción bien definida. Si un paso hace dos cosas, se debe dividir.

### Anatomía de un Buen Kata

| Sección | Propósito | Criterio de Calidad |
|---------|-----------|---------------------|
| **Objetivo** | Qué produce este procedimiento | Una frase clara sobre el output |
| **Cuándo Usar** | Condiciones de activación | Lista de disparadores específicos |
| **Inputs** | Qué necesita recibir el agente | Tabla con nombre, obligatoriedad y descripción |
| **Workflow** | Pasos numerados con checklist | Cada paso con sub-acciones detalladas |
| **Outputs** | Qué se produce | Tabla con formato y destino |
| **Restricciones** | Qué no puede hacer el Kata | Lista de límites explícitos |

### Diseño de Inputs

Buenas prácticas para definir inputs:

| Práctica | Ejemplo |
|----------|---------|
| Distinguir obligatorio vs opcional | "Archivo fuente (Sí) / Idioma destino (No)" |
| Definir defaults para opcionales | "Si se omite, traducir a todos los de `language.i18n`" |
| Especificar formato esperado | "Código BCP 47 (ej: pt-BR, en, es)" |
| Validar inputs en el primer paso | "Confirmar que el archivo existe y es .md" |

### Diseño de Workflow

Cada paso del workflow debe seguir esta estructura:

1. **Nombre descriptivo** — qué hace este paso (ej: "Lectura de las Directivas")
2. **Sub-acciones numeradas** — instrucciones específicas (1. Leer X, 2. Verificar Y)
3. **Checkpoint** — cómo saber que el paso se completó con éxito

El checklist de progreso al inicio del workflow permite rastrear la ejecución:

```
Progreso:
- [ ] 1. Nombre del paso 1
- [ ] 2. Nombre del paso 2
- [ ] 3. Validación final
```

### Diseño de Validación

La validación final es el último paso de todo Kata. Debe incluir:

- Checklist de criterios verificables (checkboxes)
- Criterios tanto de forma (estructura, formato) como de contenido (completitud, corrección)
- Referencia a las Lexis que deben obedecerse

### Estándares y Convenciones

| Aspecto | Estándar | Ejemplo |
|---------|----------|---------|
| Número de pasos | 4-8 (ideal) | Menos de 4: tal vez sea un Cry. Más de 8: descomponer |
| Referencias | Citar artefactos consultados | "Consultar `codex-lexis` para criterios de calidad" |
| Ejemplos | Incluir input y output de ejemplo | Bloque de código con datos reales |
| Idempotencia | Ejecutar el Kata 2 veces no debe generar duplicados | Verificar existencia antes de crear |

### Errores Comunes

| Error | Problema | Solución |
|-------|----------|----------|
| Kata demasiado genérico | "Crear documentación" — sin especificidad | Restringir alcance: "Crear un ADR" |
| Pasos vagos | "Analizar el código" — ¿cómo? | Detallar sub-acciones específicas |
| Sin validación | El output no se verifica | Siempre incluir paso de validación final |
| Inputs implícitos | El Kata asume contexto no declarado | Declarar todo input en la tabla |
| Dependencia circular | Kata A necesita Kata B que necesita Kata A | Refactorizar para eliminar el ciclo |

### Kata vs Cry — Cuándo Usar Cada Uno

| Característica | Kata | Cry |
|---------------|------|-----|
| Complejidad | Múltiples pasos (4-8) | 1-2 pasos |
| Inputs | Varios, con validación | Pocos, simples |
| ¿Configura agente? | Sí (define comportamiento) | No (solo invoca) |
| Output | Estructurado y validado | Rápido y directo |
| Ejemplo | Crear un ADR completo | Generar changelog |

### Restricciones Técnicas

- Todo Kata debe tener un **checklist de progreso** al inicio del Workflow (checkboxes `- [ ]` por paso)
- El **último paso** del Workflow debe ser "Validación Final" (o equivalente) y contener checkboxes verificables
- El nombre del archivo debe usar el prefijo definido en `naming.prefixes.katas` (consultar `.ahrena/.directives`) y kebab-case: `{prefijo}-{nombre-descriptivo}.md`
- La estructura debe seguir el template oficial: consultar `paths.samples.katas` en `.directives` (ej.: `templates/kata-sample.md`)
- Los inputs obligatorios deben validarse en el primer paso

## Glosario

| Término | Definición |
|---------|-----------|
| Reproducibilidad | Capacidad de obtener el mismo resultado en ejecuciones diferentes |
| Checkpoint | Verificación al final de un paso que confirma el éxito |
| Idempotencia | Propiedad de producir el mismo resultado incluso si se ejecuta múltiples veces |
| Descomposición | División de una tarea compleja en pasos atómicos |

## Referencias

- `lex-pilars` — Ley que define canónicamente los Pilares; Kata aplica Lexis y consulta Codex
- `codex-pilars` — Visión del sistema de Pilares y listas de validación (sección Validación de artefatos)
- `lex-directives` — Consulta obligatoria a `.ahrena/.directives` (paths, naming.prefixes)
- `codex-cries` — Manual sobre Cries (para entender la diferencia Kata vs Cry)
- `lex-template-usage` — Ley de uso obligatorio de templates
- `kata-create-kata` — Procedimiento para crear nuevos Katas (consulta este Codex en los pasos 1 y 3)
- `paths.samples.katas` en `.directives` — Ruta del template oficial (ej.: `templates/kata-sample.md`)
