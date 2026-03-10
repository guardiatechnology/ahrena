# Codex: Cómo Escribir Buenas Lexis

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Creación de Lexis (leyes inquebrantables)

## Visión General

Este Codex documenta qué hace que una Lexis sea eficaz: cómo redactar una ley clara, cómo definir un alcance verificable y cómo garantizar que la ley sea aplicable en la práctica. Es consultado por `kata-create-lexis` durante la creación de nuevas Lexis. El kata usa este Codex en el **Paso 1** (lectura de criterios de calidad) y en el **Paso 3** (redacción de secciones); la **Validación Final** del Kata verifica las Restricciones Técnicas y la Anatomía descritas abajo.

## Contexto

- **Dominio:** Diseño de leyes inquebrantables para gobernanza de agentes y procesos
- **Público objetivo:** Agentes de IA que ejecutan `kata-create-lexis` y mantenedores del framework
- **Actualización:** Cuando se identifiquen nuevos estándares de calidad para Lexis

## Contenido

### Principios

1. **Univocidad:** Una Lexis debe tener una única interpretación posible. Si dos personas pueden leer la ley y llegar a conclusiones diferentes, es necesario reescribirla.
2. **Verificabilidad:** Debe ser posible verificar automáticamente si la ley se está cumpliendo. Si no puede verificarse, no es una buena Lexis.
3. **Necesidad:** Cada Lexis debe resolver un problema real. Las leyes innecesarias generan burocracia sin valor.
4. **Inmutabilidad:** Las Lexis no admiten excepciones. Si la ley necesita excepciones, probablemente debería ser un Codex (recomendación) en lugar de una Lexis (obligación).

### Anatomía de una Buena Lexis

| Sección | Propósito | Criterio de Calidad |
|---------|-----------|---------------------|
| **Propósito** | Explica por qué existe la ley | Debe conectar la ley con un riesgo o problema real |
| **Ley** | Declaración imperativa de la regla | Una frase, clara, sin ambigüedad, usando "DEBE" o "NO PUEDE" |
| **Alcance** | Define dónde y a quién se aplica | Lo suficientemente específica para no generar dudas |
| **Consecuencias** | Qué ocurre si se viola | Acciones concretas (bloqueo, alerta, remediación) |
| **Ejemplos** | Correcto vs incorrecto | Casos reales, no hipotéticos |
| **Validación** | Cómo verificar conformidad | Herramienta, momento y métrica específicos |

### Cómo Redactar la Declaración de la Ley

La declaración de la ley es el corazón de la Lexis. Debe ser:

**Buena declaración:**
> "Todo PR DEBE tener al menos un revisor aprobado antes del merge."

- Sujeto claro (todo PR)
- Verbo imperativo (DEBE)
- Acción específica (tener revisor aprobado)
- Condición temporal (antes del merge)

**Mala declaración:**
> "Los code reviews son importantes y deben realizarse cuando sea posible."

- Sin sujeto específico
- "Cuando sea posible" crea una brecha
- "Son importantes" es opinión, no ley

### Estándares y Convenciones

| Aspecto | Estándar | Ejemplo |
|---------|----------|---------|
| Verbos imperativos | DEBE, NO PUEDE, NO DEBE | "Todo agente DEBE consultar el .directives" |
| Excepciones | Ninguna — las Lexis son absolutas | "Excepciones: Ninguna. Las Lexis no admiten excepciones." |
| Alcance | Siempre explícito | "Se aplica a: todos los repositorios" |
| Validación | Siempre automatizable | "Herramienta: gitleaks; Momento: pre-commit" |

### Errores Comunes

| Error | Problema | Solución |
|-------|----------|----------|
| Ley vaga | "El código debe ser de calidad" — ¿qué es calidad? | Definir criterios medibles |
| Ley inviable | "La cobertura de tests debe ser 100%" — irrealista en muchos contextos | Calibrar con la realidad del proyecto |
| Ley redundante | Repetir lo que otra Lexis ya cubre | Verificar Lexis existentes antes de crear |
| Ley opinativa | "Se debe usar TypeScript" — es preferencia, no seguridad/calidad | Mover a Codex como recomendación |
| Excepción incorporada | "Excepto cuando lo apruebe el Tech Lead" — invalida la ley | Si necesita excepción, no es Lexis |

### Lexis vs Codex — Cuándo Usar Cada Uno

| Característica | Lexis | Codex |
|---------------|-------|-------|
| Naturaleza | Obligatorio | Recomendado |
| Excepciones | Nunca | Puede tener |
| Verificación | Automatizada | Manual o automatizada |
| Ejemplo | "Ningún secret en repositorio" | "Se prefiere PostgreSQL para datos transaccionales" |

### Restricciones Técnicas

- La sección **Ley** debe contener exactamente una declaración imperativa en blockquote (`> **[declaración]**`)
- La sección **Alcance** debe incluir "Excepciones: Ninguna" (o equivalente) — las Lexis no admiten excepciones
- La sección **Validación Automatizada** debe especificar herramienta, momento y métrica
- El nombre del archivo debe usar el prefijo definido en `naming.prefixes.lexis` (consultar `.ahrena/.directives`) y kebab-case: `{prefijo}-{nombre-descriptivo}.md`
- La estructura debe seguir el template oficial: consultar `paths.samples.lexis` en `.directives` (ej.: `templates/lex-sample.md`)

## Glosario

| Término | Definición |
|---------|-----------|
| Declaración de la ley | Frase imperativa que define la regla absoluta |
| Univocidad | Propiedad de tener una única interpretación |
| Verificabilidad | Capacidad de verificar conformidad automáticamente |
| Validación automatizada | Mecanismo técnico que verifica el cumplimiento de la ley |

## Referencias

- `lex-pilars` — Ley que define canónicamente los Pilares; Lexis como ley inquebrantable
- `codex-pilars` — Visión del sistema de Pilares y listas de validación (sección Validación de artefatos)
- `lex-directives` — Consulta obligatoria a `.ahrena/.directives` (paths, naming.prefixes)
- `lex-template-usage` — Ley de uso obligatorio de templates
- `kata-create-lexis` — Procedimiento para crear nuevas Lexis (consulta este Codex en los pasos 1 y 3)
- `paths.samples.lexis` en `.directives` — Ruta del template oficial (ej.: `templates/lex-sample.md`)
