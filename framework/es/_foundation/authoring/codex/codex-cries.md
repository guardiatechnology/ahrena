# Codex: Cómo Escribir Buenos Cries

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Creación de Cries (comandos recurrentes)

## Visión General

Este Codex documenta cómo diseñar comandos recurrentes eficaces en Ahrena. Aborda cuándo crear un Cry vs usar un Kata directamente, el diseño de prompt templates, parámetros y la cadena Cry → Kata. Es consultado por `kata-create-cry` durante la creación de nuevos Cries.

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

- Todo Cry debe referenciar al menos un Kata que ejecuta
- La sección "Prompt Template" debe usar `{{variables}}` para parámetros
- El nombre del archivo debe seguir el patrón `cry-{nombre-descriptivo}.md`
- La sección "Diferencia con Kata" debe contener tabla comparativa

## Glosario

| Término | Definición |
|---------|-----------|
| Prompt template | Texto parametrizado enviado al agente cuando se invoca el Cry |
| Default inteligente | Valor predeterminado derivado del `.directives` o del contexto |
| Cadena de invocación | Secuencia Cry → (Warrior) → Kata que define el flujo de ejecución |
| Parámetro posicional | Argumento identificado por la posición, no por nombre |

## Referencias

- `codex-pilars` — Visión general del sistema de Pilares
- `codex-katas` — Manual sobre Katas (para entender la diferencia Cry vs Kata)
- `lex-template-usage` — Ley de uso obligatorio de templates
- `kata-create-cry` — Procedimiento para crear nuevos Cries
- `templates/cry-sample.md` — Template oficial de Cries
