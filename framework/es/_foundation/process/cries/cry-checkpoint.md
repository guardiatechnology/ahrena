# Cry: Guardar Checkpoint de Sesión

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Atajo del usuario para escribir `.checkpoint` bajo demanda, conforme a `lex-checkpoint`

## Descripción

Atajo del usuario que invoca `kata-checkpoint-save` para escribir el `.checkpoint` de la sesión actual. Útil cuando hay contexto fuera del plan (Open threads, Notes, hand-off entre múltiples planes activos) que vale la pena preservar antes de pausar o cerrar la ventana.

Leer `.checkpoint` es responsabilidad automática del agente al inicio de la sesión (vía `kata-checkpoint-read`) — `cry-checkpoint` cubre solo el disparador de **escritura** bajo demanda.

## Uso

```
/cry-checkpoint
```

Sin argumentos por defecto. El agente recolecta el contexto de la sesión y lo escribe.

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `--focus "<frase>"` | No | Sobrescribe el Session focus inferido por el agente | `--focus "Revisando plan-026"` |
| `--add-thread "<línea>"` | No | Agrega una Open thread al checkpoint actual | `--add-thread "Evaluar X"` |
| `--note "<texto>"` | No | Agrega texto a las Notes | `--note "Enlace: https://..."` |
| `--dry-run` | No | Muestra el contenido que se escribiría sin persistir | — |

Sin flags, el agente infiere todos los campos del contexto de la sesión.

## Lo que el Comando Hace

1. Invoca `kata-checkpoint-save`
2. El kata recolecta Session focus, Active plans, Open threads y Notes del contexto de la sesión
3. Valida que el contenido no duplique el plan
4. Escribe `.checkpoint` en la raíz del workspace con schema canónico
5. Presenta confirmación al usuario

## Plantilla de Prompt

```
Invocar kata-checkpoint-save con:

- Workspace root: {{pwd}}
- Session focus: {{--focus si se proporciona, si no inferir del contexto de la sesión}}
- Active plans: {{inferir de los planes con status: in-progress en el provider cache (.claude/plans/ para Claude Code; .cursor/plans/ para Cursor)}}
- Open threads: {{recolectar del contexto + agregar --add-thread si se proporciona}}
- Notes: {{recolectar del contexto + agregar --note si se proporciona}}
- Dry-run: {{flag --dry-run}}

Tras la escritura, presentar confirmación al usuario en el formato:

✅ Checkpoint guardado en `.checkpoint`:
   - Session focus: {primera frase, max 100 chars}
   - Active plans: {N}
   - Open threads: {N}
   - Notes: {presente | vacío}
```

## Ejemplo de Invocación

**Entrada:**

```
/cry-checkpoint
```

**Salida esperada:**

```
Recolectando contexto de la sesión...

Session focus: Reposicionando lex-checkpoint en paralelo con revisión de plan-026.
Active plans: plan-026, plan-040
Open threads:
  - Evaluar absorción de "Risks de la sesión" en lex-agent-planning
  - Decidir clade de los Brand-related cries
Notes: Enlace discusión kata-quality-gate: https://...

✅ Checkpoint guardado en `.checkpoint`:
   - Session focus: Reposicionando lex-checkpoint en paralelo con revisión de plan-026.
   - Active plans: 2
   - Open threads: 2
   - Notes: presente
```

**Entrada con flags:**

```
/cry-checkpoint --add-thread "Validar con PM antes del PR" --note "Slack: #ahrena"
```

**Salida:**

```
Agregando 1 hilo y 1 nota al contexto.

✅ Checkpoint guardado en `.checkpoint`:
   - Session focus: {inferido}
   - Active plans: 2
   - Open threads: 3 (1 nuevo)
   - Notes: presente
```

## Restricciones

- NO modifica planes (`plan-*.md` en el provider cache `.claude/plans/` o `.cursor/plans/`) — `cry-checkpoint` cubre solo `.checkpoint`
- NO escribe contenido que duplica el plan — kata-checkpoint-save valida y bloquea
- La salida respeta el tono Guardia (`lex-tone`, `lex-brand-voice`) — directo, sin buzzwords
- No commitea `.checkpoint` — sigue gitignore según `lex-checkpoint` regla 4
- `--dry-run` muestra pero no escribe

## Diferencia con el Kata

| Aspecto | `cry-checkpoint` | `kata-checkpoint-save` |
|---------|------------------|------------------------|
| **Naturaleza** | Atajo del usuario | Procedimiento completo |
| **Invocación** | `/cry-checkpoint` (1 línea) | Invocado por `cry-checkpoint` o por otros warriors |
| **¿Configura agente?** | No | Sí — define disparadores, validación, formato |
| **Salida** | Escritura + confirmación | Escritura + estado + confirmación |
