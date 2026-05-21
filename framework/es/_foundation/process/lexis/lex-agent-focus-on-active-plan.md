# Lexis: Foco del Agente en el Plan Activo

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Comportamiento del agente cuando una sub-issue Plan está en `status: development` y la sesión actual es la owner declarada

## Propósito

Las sesiones de IA son contextos costosos: cada context-switch destruye cache, fragmenta atención y degrada la calidad de la ejecución. Cuando un Plan está en `status: development` con la sesión actual como owner declarada (assignee), aceptar requisiciones no relacionadas drena la velocidad de entrega y diluye el foco que el framework Ahrena optimiza.

El agente actúa como guardián de disciplina contra el context-switching. No le toca al usuario recordar mantener el foco — le toca al agente rechazar educadamente y volver a la ejecución. Esta Lex codifica ese rechazo como obligación, no cortesía.

## Ley

> **Cuando una sub-issue Plan está en `status: development` y la sesión actual es la owner declarada (assignee), el agente DEBE rechazar requisiciones del usuario para trabajo no relacionado hasta que el Plan transicione a `status: to review`. El rechazo DEBE mencionar el Plan activo (número, status actual, ETA estimada para `to review` cuando se conozca) y ofrecer al usuario la alternativa explícita: tratar la requisición como (a) hallazgo tangencial al Plan actual, (b) nuevo Plan sub-issue bajo el mismo parent Issue, (c) nueva Issue parent, o (d) bloqueador crítico declarado.**

## Alcance

- **Aplica a:** todas las sesiones de agente operando sobre un Plan sub-issue en `status: development` con assignee igual al identificador de la sesión actual (humano o agente)
- **Agentes vinculados:** `warrior-athena` (orquestador principal), `warrior-apollo`, `warrior-hephaestus`, `warrior-iris`, `warrior-claudionor`, y cualquier warrior en ejecución durante un Plan activo
- **Excepciones declaradas:** tres y solo tres — (a) bloqueador crítico declarado (CI rota en `main`, incidente P0 declarado, seguridad crítica); (b) pregunta directa sobre el Plan activo (aclaración, consulta de status, próximo paso); (c) ajuste de alcance del propio Plan activo (expandir, contraer, replanificar)

```
<HARD-GATE>
Todo agente NO DEBE iniciar trabajo no relacionado con el Plan activo
cuando existe una sub-issue Plan en `status: development` con la sesión
actual como assignee declarado.

Precondiciones obligatorias para aceptar la requisición:
  (a) La requisición se relaciona directamente con el alcance declarado del Plan activo
  (b) O encaja en una de las 3 excepciones declaradas (bloqueador crítico, pregunta sobre el Plan, ajuste de alcance del Plan)
  (c) Y el agente declara explícitamente qué excepción aplica antes de proceder
  (d) Y el agente se compromete a retomar el Plan tras tratar la excepción

Esta regla se aplica a TODA sesión con Plan activo, independientemente de:
  - "es rápido, solo una cosita"
  - "mientras tanto, ¿también puedes...?"
  - "espera, antes de continuar..."
  - "ah, olvidé pedirte algo antes"

Excepciones declaradas (3, exhaustivas):
  - Bloqueador crítico declarado (CI rota en `main`, incidente P0, seguridad crítica)
  - Pregunta directa sobre el Plan activo (aclaración, status, próximo paso)
  - Ajuste de alcance del propio Plan activo (expandir, contraer, replanificar)
</HARD-GATE>
```

## Protocolo de Rechazo

Al recibir una requisición no relacionada con un Plan activo, el agente DEBE:

1. Identificar el Plan activo: número de la sub-issue, título, status, ETA estimada para `to review` cuando se conozca
2. Declarar el rechazo de forma directa: "Hay un Plan activo en `status: development` (Plan #{N}: {título}); no puedo iniciar trabajo no relacionado hasta `to review`."
3. Presentar al usuario las cuatro opciones discretas:
   - **(a)** La requisición es hallazgo tangencial al Plan activo → aplicar `lex-no-silent-tech-debt` (Protocolo de Hallazgo Tangencial)
   - **(b)** Es nuevo Plan sub-issue bajo el mismo parent Issue → registrar y tratar tras `to review`
   - **(c)** Es nueva Issue parent (capability nueva) → registrar y tratar tras `to review`
   - **(d)** Es bloqueador crítico declarado → tratar ahora, retomar Plan al concluir
4. Esperar la elección del usuario antes de cualquier acción
5. Retomar el Plan activo tras tratar la excepción (cuando aplique), con checkpoint explícito del punto de retomada

## Ejemplos

### Correcto

```
Usuario: Antes de continuar, ¿puedes revisar este otro repo aquí?
Agente: Hay un Plan activo: #163 (codify 3 Lexis HARD-GATE rules), en
        `status: development`, ETA para `to review` ~10min.
        No puedo iniciar trabajo en otro repo ahora. Prefieres:
        (a) ¿Registrar como Plan nuevo bajo el parent #140 y tratar tras esta PR?
        (b) ¿Abrir Issue parent nueva si es capability separada?
        (c) ¿Declarar como bloqueador crítico (CI rota / P0)?
        (d) ¿Esperar `to review` (~10min)?
Usuario: (a)
Agente: Ok, registrado. Retomando #163.
```

```
Usuario: Espera, ¿este Plan va a tocar el archivo X realmente?
Agente: [Excepción (b): pregunta directa sobre el Plan activo]
        Sí, el archivo X forma parte del alcance declarado porque {razón}.
        Continuando la implementación.
```

### Incorrecto

```
Usuario: Antes de continuar, ¿también puedes actualizar esta Lex aquí?
Agente: Claro, déjame hacer eso primero.            # FORBIDDEN — context switch silencioso
        [edita archivo no relacionado, contamina diff del PR]
```

```
Usuario: Aprovecha y arregla este otro bug también
Agente: [silenciosamente expande el alcance sin registrar]   # FORBIDDEN — scope creep silencioso
```

## Validación Automatizada

- **Herramienta:** auto-verificación del agente antes de aceptar nueva instrucción durante Plan activo; auditoría de Argos durante review de PR detectando archivos modificados fuera del alcance declarado del Plan (compara diff del PR con alcance en el cuerpo de la sub-issue)
- **Momento:** en cada nueva instrucción recibida durante Plan en `status: development`; review del PR por Argos
- **Métrica:** 0 PRs con archivos modificados fuera del alcance declarado del Plan; 100% de las requisiciones no relacionadas rechazadas con referencia explícita al Plan activo
