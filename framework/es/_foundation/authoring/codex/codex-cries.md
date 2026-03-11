# Codex: Cómo Escribir Buenos Cries

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Creación de Cries (comandos recurrentes)

## Visión General

Este Codex documenta cómo diseñar comandos recurrentes eficaces en Ahrena. Aborda cuándo crear un Cry vs usar un Kata directamente, el diseño de prompt templates, parámetros y la cadena Cry → Kata/Warrior. Es consultado por `kata-create-cry` durante la creación de nuevos Cries. El kata usa este Codex en el **Paso 1** (lectura de criterios) y en el **Paso 3** (redacción de secciones); la **Validación Final** del Kata verifica las Restricciones Técnicas y la Anatomía descritas abajo.

## Contexto

- **Dominio:** Diseño de comandos de productividad para agentes de IA
- **Público objetivo:** Agentes de IA que ejecutan `kata-create-cry` y mantenedores del framework
- **Actualización:** Cuando se identifiquen nuevos estándares de calidad para Cries

## Contenido

### Principios

1. **Rapidez:** Un Cry existe para ahorrar tiempo. Si la invocación es tan compleja como ejecutar el Kata directamente, el Cry no tiene valor.
2. **Delegación:** El Cry no contiene lógica propia — delega a un Kata (opcionalmente vía un Warrior). El Cry es el punto de entrada, no el procedimiento.
3. **Parámetros mínimos:** El Cry debe exigir el mínimo de información al usuario, usando defaults inteligentes del `.directives` para el resto.
4. **Previsibilidad:** El mismo Cry con los mismos parámetros debe producir el mismo resultado.
5. **Regla de invocación (inquebrantable):** El Cry **NO PUEDE** invocar Lexis. El Cry **NO PUEDE** acceder al Codex directamente. El Cry invoca **SOLO** Katas y/o Warriors. La consulta a Lexis y Codex la realiza el Kata o Warrior invocado, nunca el Cry como acción directa.
6. **Sin comandos externos sin Kata:** El Cry **NO PUEDE** definir ni prescribir como procedimiento principal la ejecución de comandos externos (p. ej. `git`, `make`, `npm`, `pnpm`, `python`, scripts de shell) sin que exista un **Kata** que encapsule ese procedimiento y que el Cry invoque. Si el flujo del comando implica ejecutar herramientas externas, debe existir un Kata (p. ej. `kata-sync`, `kata-rebase`) que describa los pasos, y el Cry solo invoca ese Kata (o un Warrior que lo orqueste). Un Cry que describe "ejecuta git X, luego Y" en el cuerpo del artefacto, sin invocar un Kata existente, no es conforme — el procedimiento debe estar en el Kata; el Cry es solo el atajo de invocación.

### Anatomía de un Buen Cry

| Sección | Propósito | Criterio de Calidad |
|---------|-----------|---------------------|
| **Descripción** | Qué hace el comando en una frase | Clara y directa |
| **Uso** | Sintaxis de invocación | Formato: `/cry-nombre <obligatorio> [opcional]` |
| **Parámetros** | Tabla de argumentos | Nombre, obligatoriedad, descripción y ejemplo |
| **Qué Hace el Comando** | Lista numerada de acciones | 3-6 pasos de alto nivel |
| **Prompt Template** | Instrucciones enviadas al agente | Contexto + Tarea + Formato de salida |
| **Ejemplo de Invocación** | Input y output concretos | Demuestra uso real |
| **Diferencia con Kata** | Tabla comparativa | Cry vs Kata para este caso |

### Diseño de Parámetros

| Práctica | Ejemplo |
|----------|---------|
| Mínimo de parámetros obligatorios | Solo lo esencial que no puede tener default |
| Defaults inteligentes | Los idiomas provienen del `.directives`, no del usuario |
| Formato explícito | "Código BCP 47" es más claro que "idioma" |
| Consistencia con otros Cries | Mismo patrón de nomenclatura y orden |

### Diseño de Prompt Template

El prompt template es el corazón funcional del Cry. Estructura recomendada:

```
Contexto:
- {{parámetro1}}
- {{parámetro2}}

Tarea:
[Instrucción clara de qué hacer, referenciando Kata y/o Warrior]

Formato de salida:
[Cómo debe presentarse el resultado]
```

Buenas prácticas:
- Referenciar el Kata a ejecutar por nombre
- Si existe Warrior, instruir al agente para que asuma el papel
- Definir formato de salida explícitamente
- Usar variables con `{{dobles llaves}}` para parámetros

### Cadena de Invocación

Un Cry puede seguir dos patrones:

**Patrón 1: Cry → Kata (directo)**
```
/cry-new-lex "code review" → kata-create-lexis
```
Se usa cuando no existe un Warrior dedicado para el dominio.

**Patrón 2: Cry → Warrior → Kata**
```
/cry-translate archivo.md → warrior-translator → kata-translate
```
Se usa cuando existe un Warrior que agrega persona y contexto.

### Estándares y Convenciones

| Aspecto | Estándar | Ejemplo |
|---------|----------|---------|
| Nomenclatura | `cry-{verbo}-{sustantivo}` o `cry-new-{pilar}` | `cry-translate`, `cry-new-lex` |
| Sintaxis | `/cry-nombre <obligatorio> [opcional]` | `/cry-translate <archivo> [idioma]` |
| Parámetros posicionales | Obligatorios primero, opcionales después | `<archivo> [idioma] [--flag]` |
| Flags | Prefijadas con `--` | `--order en,es` |

### Errores Comunes

| Error | Problema | Solución |
|-------|----------|----------|
| Cry complejo | Muchos parámetros obligatorios | Reducir a 1-2 obligatorios, usar defaults |
| Cry sin Kata | Toda la lógica en el prompt template | Extraer procedimiento a un Kata |
| Cry con comandos externos sin Kata | El Cry describe "ejecuta git X", "ejecuta make Y" sin invocar un Kata que encapsule el flujo | Crear el Kata (p. ej. kata-sync, kata-rebase) y hacer que el Cry lo invoque; el Cry no puede ser el único lugar donde está definido el procedimiento |
| Cry redundante | Duplica otro Cry existente | Verificar Cries existentes antes de crear |
| Prompt vago | "Hacer algo con el archivo" | Referenciar Kata específico y formato de salida |
| Sin ejemplo | El usuario no sabe cómo usarlo | Siempre incluir ejemplo con input y output |

### Cry vs Kata — Cuándo Crear Cada Uno

| Característica | Cry | Kata |
|---------------|-----|------|
| Punto de entrada | El usuario lo invoca directamente | El agente lo ejecuta internamente |
| Complejidad | Invocación simple (1 comando) | Procedimiento de múltiples pasos |
| Parámetros | Del usuario (estilo CLI) | Validados y procesados |
| ¿Contiene lógica? | No — delega a Kata | Sí — define los pasos |
| Análogo | Comando shell | Script llamado por el comando |

### Restricciones Técnicas

- Todo Cry debe **referenciar e invocar al menos un Kata** (o Warrior que orquesta un Kata) que exista y ejecute el procedimiento — el Cry no contiene lógica propia. **Violación:** Cry que describe pasos con comandos externos (git, make, etc.) sin invocar un Kata que encapsule esos pasos; Cry con "Kata asociado: kata-X — Pendiente de creación" sigue siendo no conforme hasta que el Kata exista y el Cry lo invoque.
- Todo Cry que implique ejecución de herramientas externas (git, make, npm, etc.) **DEBE** invocar un Kata que documente y ejecute ese flujo; el Cry no puede ser el único lugar donde está definido el procedimiento.
- La sección **Prompt Template** debe usar `{{variables}}` para parámetros y referenciar explícitamente el Kata (y Warrior, si existe)
- El nombre del archivo debe usar el prefijo definido en `naming.prefixes.cries` (consultar `.ahrena/.directives`) y kebab-case: `{prefijo}-{nombre-descriptivo}.md`
- La estructura debe seguir el template oficial: consultar `paths.samples.cries` en `.directives` (ej.: `templates/cry-sample.md`)
- La sección **Diferencia con Kata** (o equivalente) debe contener tabla comparativa Cry vs Kata para este comando

## Glosario

| Término | Definición |
|---------|-----------|
| Prompt template | Texto parametrizado enviado al agente cuando se invoca el Cry |
| Default inteligente | Valor predeterminado derivado del `.directives` o del contexto |
| Cadena de invocación | Secuencia Cry → (Warrior) → Kata que define el flujo de ejecución |
| Parámetro posicional | Argumento identificado por la posición, no por nombre |

## Referencias

- `lex-pilars` — Ley que define canónicamente los Pilares; Cry invoca solo Kata(s) y/o Warrior(s), nunca Lexis ni Codex
- `codex-pilars` — Visión del sistema de Pilares y listas de validación (sección Validación de artefatos)
- `lex-directives` — Consulta obligatoria a `.ahrena/.directives` (paths, naming.prefixes)
- `codex-katas` — Manual sobre Katas (para entender la diferencia Cry vs Kata)
- `lex-template-usage` — Ley de uso obligatorio de templates
- `kata-create-cry` — Procedimiento para crear nuevos Cries (consulta este Codex en los pasos 1 y 3)
- `paths.samples.cries` en `.directives` — Ruta del template oficial (ej.: `templates/cry-sample.md`)
