# Lexis: Checkpoint de Sesión

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Todas las sesiones de trabajo con agentes IA

## Propósito

Las sesiones de trabajo con agentes de IA son efímeras: al cerrarse, todo el contexto acumulado (decisiones tomadas, progreso parcial, próximos pasos) se pierde. Esto genera retrabajo, inconsistencia y pérdida de continuidad.

El checkpoint es un mecanismo del Ahrena que persiste el contexto de una actividad en un archivo `.checkpoint`, permitiendo que cualquier agente — en la misma sesión o en sesiones futuras — retome el trabajo exactamente donde se dejó.

Esta Lexis existe para garantizar que **ningún contexto relevante se pierda entre sesiones** y que **ninguna actividad comience sin verificar antes si hay trabajo previo guardado**.

## Ley

> **Todo agente DEBE verificar el archivo `.checkpoint` antes de iniciar cualquier actividad y DEBE guardar el checkpoint al concluir cada actividad o al cerrar una sesión.**

## Reglas

### 1. Verificación obligatoria al iniciar

Antes de iniciar cualquier actividad, el agente **DEBE**:

1. Verificar si existe un archivo `.checkpoint` en la raíz del workspace.
2. Si existe, leer su contenido y presentar al usuario un resumen del contexto guardado.
3. Preguntar al usuario si desea **retomar** la actividad guardada o **iniciar una nueva** (descartando el checkpoint anterior).
4. Si no existe, proseguir con normalidad.

### 2. Guardado obligatorio al concluir

Al concluir una actividad o cerrar una sesión, el agente **DEBE**:

1. Preguntar al usuario su preferencia de guardado (solo la primera vez de la sesión):
   - **Automático:** el checkpoint se guarda automáticamente al final de cada actividad, sin preguntar de nuevo.
   - **Manual:** el agente pregunta antes de cada guardado si el usuario desea guardar.
2. Respetar la preferencia indicada durante el resto de la sesión.
3. Persistir el checkpoint en el archivo `.checkpoint` en la raíz del workspace.

### 3. Estructura del checkpoint

El archivo `.checkpoint` debe contener, como mínimo:

```markdown
# Checkpoint

- **Actividad:** [descripción breve de la actividad en curso]
- **Estado:** [en curso | concluido | bloqueado]
- **Fecha:** [fecha y hora del guardado]
- **Sesión:** [identificador de la sesión o chat]

## Contexto

[Resumen de lo discutido, decidido o producido]

## Progreso

- [x] [etapa concluida]
- [ ] [próxima etapa pendiente]

## Decisiones tomadas

- [decisión 1]
- [decisión 2]

## Próximos pasos

1. [acción pendiente]
2. [acción pendiente]

## Artefactos producidos

- [ruta/del/archivo-1]
- [ruta/del/archivo-2]
```

### 4. Responsabilidad compartida

- Cualquier agente (Warrior) que actúe en la sesión **hereda** esta obligación.
- El checkpoint es **agnóstico de disciplina** — se aplica a actividades de cualquier Clade.
- El archivo `.checkpoint` **no debe ser commiteado** en el repositorio (debe estar en `.gitignore`).

## Alcance

- **Se aplica a:** todas las sesiones de trabajo con agentes IA, en cualquier Clade y Subclade
- **Agentes vinculados:** todos los Warriors y agentes genéricos
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de Violación

1. **Pérdida de contexto:** sesiones sin checkpoint resultan en retrabajo y pérdida de decisiones ya tomadas.
2. **Alerta al usuario:** si el agente detecta que una sesión anterior no guardó checkpoint, debe alertar al usuario sobre la posible pérdida de contexto.
3. **Remediación:** el agente debe intentar reconstruir el contexto a partir del historial disponible (archivos modificados, git log, transcripts) y guardar un checkpoint retroactivo.

## Ejemplos

### Correcto

```
Agente: Encontré un checkpoint guardado:
  - Actividad: Implementación del módulo de autenticación
  - Estado: en curso
  - Última sesión: 2026-03-07 14:30
  - Progreso: 3 de 5 etapas concluidas

  ¿Desea retomar esta actividad o iniciar una nueva?

Usuario: Retomar.

Agente: Perfecto. Retomando desde donde quedamos...
  Próximos pasos pendientes:
  1. Implementar refresh token
  2. Añadir pruebas de integración
```

### Incorrecto

```
Agente: ¡Hola! ¿En qué puedo ayudarte?

Usuario: Sigamos con la implementación del módulo de autenticación.

Agente: ¡Claro! Empecemos de cero. ¿Cuál es el alcance?

# ❌ El agente ignoró el checkpoint existente y obligó al usuario
# a re-explicar todo el contexto de la sesión anterior.
```

## Validación Automatizada

- **Herramienta:** verificación por el propio agente al iniciar y finalizar cada sesión
- **Momento:** inicio de cada sesión (lectura) y fin de cada actividad (escritura)
- **Métrica:** 100 % de las sesiones deben tener el checkpoint verificado a la entrada y guardado a la salida
