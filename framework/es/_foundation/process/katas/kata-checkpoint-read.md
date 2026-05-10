# Kata: Leer Checkpoint de Sesión

> **Prefijo:** `kata-` | **Tipo:** Habilidad Repetible | **Alcance:** Inicio de sesión con agente de IA, conforme a `lex-checkpoint`

## Objetivo

Localizar `.checkpoint` en la raíz del workspace, validar el schema, presentar resumen al usuario y preguntar si desea retomar el contexto guardado. Cuando el schema es antiguo, emitir warning de deprecation y proseguir como si no hubiera checkpoint.

## Cuándo Usar

- Al inicio de cada sesión con agente de IA, antes de cualquier otra actividad (disparador automático según `lex-checkpoint` regla 1)
- Cuando el usuario invoca explícitamente para revisar el contexto guardado
- Tras `git pull` que pueda haber traído alteraciones en el workspace (raro — `.checkpoint` es gitignored, pero los paths configurados pueden cambiar)

## Entradas

| Entrada | Obligatorio | Descripción |
|---------|:-----------:|-------------|
| Workspace root | Sí | Directorio donde buscar `.checkpoint` (default: `pwd` en la inicialización de la sesión) |
| Modo de presentación | No | `summary` (default — resumen corto) o `full` (contenido completo del checkpoint) |

## Flujo de Trabajo

```
Progreso:
- [ ] 1. Localizar .checkpoint
- [ ] 2. Detectar schema (nuevo, antiguo, ausente)
- [ ] 3. Presentar al usuario (resumen o warning)
- [ ] 4. Capturar decisión (retomar, descartar, ignorar)
- [ ] 5. Aplicar decisión en el contexto de la sesión
```

### Paso 1: Localizar `.checkpoint`

1. Buscar `.checkpoint` en la raíz del workspace (workspace = `pwd` o directorio pasado como entrada).
2. Si no existe: estado `absent` → proseguir al Paso 5 sin lectura.
3. Si existe: estado `present` → proseguir al Paso 2.

### Paso 2: Detectar schema

1. Leer la primera línea del archivo:
   - `# Session checkpoint` → schema nuevo
   - `# Checkpoint` (sin "Session") → schema antiguo
   - Otro contenido → schema desconocido (tratar como antiguo: warning + ignorar)
2. Para schema nuevo: validar la presencia de al menos `## Session focus` o `## Active plans` o `## Open threads` o `## Notes`. Si ninguna de las 4 secciones existe, downgrade a schema desconocido.
3. Para schema antiguo o desconocido: NO parsear contenido. Solo registrar el estado para el Paso 3.

### Paso 3: Presentar al usuario

**Caso schema nuevo:**

```
Encontré un `.checkpoint` (schema actual):
  - Session focus: {primera línea de Session focus, max 100 chars}
  - Active plans: {lista compacta de plan-IDs}
  - Open threads: {N ítems}
  - Last update: {timestamp en formato relativo, ej.: "hace 2h"}

¿Desea retomar este contexto o iniciar una nueva ventana?
```

En modo `full`, presentar el contenido completo de las 4 secciones.

**Caso schema antiguo:**

```
⚠️  Encontré un `.checkpoint` en schema antiguo (pre-issue #73).
   El contenido será ignorado y sobrescrito en la próxima invocación de
   `cry-checkpoint` o al cerrar la sesión.

   Para descartar ahora: `rm .checkpoint`
   Para preservar como Notes: copie el contenido manualmente antes de guardar.

Prosiguiendo como si no hubiera checkpoint.
```

NO ofrecer la opción de retomar — el schema antiguo no es parseable de forma segura.

**Caso ausente:**

No emitir nada. Proseguir silenciosamente. La ausencia de `.checkpoint` es un escenario válido (según `lex-checkpoint` regla 1.5).

### Paso 4: Capturar decisión (solo para schema nuevo)

Esperar respuesta del usuario:

- **"retomar" / "yes" / "r"** → estado `resume`; el agente carga el contexto en la memoria de la sesión y lo deja disponible para próximas decisiones.
- **"nueva" / "descartar" / "n"** → estado `discard`; el agente marca `.checkpoint` para sobrescritura en la próxima invocación de save (no lo elimina aún — el usuario puede cambiar de idea).
- **"ignorar" / silencio por timeout** → estado `ignore`; el agente prosigue sin aplicar contexto, pero NO marca para sobrescritura; el checkpoint actual permanece intacto.

### Paso 5: Aplicar decisión

- `resume`: poner Active plans, Open threads, Session focus en el contexto activo de la sesión. Notes quedan disponibles bajo demanda pero no se presentan automáticamente.
- `discard`: limpiar contexto de la sesión, marcar `.checkpoint` para sobrescritura.
- `ignore`: proseguir sin aplicar.
- `absent` / `schema antiguo`: proseguir sin aplicar.

### Paso 6: Validación Final

- [ ] La decisión del usuario fue capturada (o inferida vía timeout)
- [ ] El contexto de la sesión refleja la decisión (resume = aplicado; otros = sin aplicación)
- [ ] El schema antiguo emitió warning visible al usuario
- [ ] El checkpoint ausente NO emitió warning (silencioso es correcto)

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Resumen del checkpoint presentado al usuario | Texto markdown | Terminal/IDE |
| Estado de la operación (`resume`, `discard`, `ignore`, `absent`, `deprecated_schema`) | Enum interno | Contexto de la sesión |
| Contexto cargado (solo si `resume`) | Estructurado (Session focus, Active plans, Open threads, Notes) | Memoria de la sesión |

## Ejemplo de Ejecución

### Entrada

Workspace root: `/Users/dev/workspace/guardia/tooling/ahrena`
Modo: `summary` (default)

### Contenido de `.checkpoint`

```markdown
# Session checkpoint

- **Last update:** 2026-05-09T22:30:00Z
- **Session id:** abc1234

## Session focus

Reposicionando lex-checkpoint en paralelo con revisión de plan-026.

## Active plans

- `plan-026` — commit-readiness-observer; aguardando ajuste
- `plan-040` — reposicionamiento del `.checkpoint`; en redacción

## Open threads

- Evaluar absorción de "Risks de la sesión" en lex-agent-planning
- Decidir clade de los Brand-related cries

## Notes

Enlace de la discusión sobre kata-quality-gate: https://...
```

### Salida

```
Encontré un `.checkpoint` (schema actual):
  - Session focus: Reposicionando lex-checkpoint en paralelo con revisión de plan-026
  - Active plans: plan-026, plan-040
  - Open threads: 2 ítems
  - Last update: hace 2h

¿Desea retomar este contexto o iniciar una nueva ventana?
```

## Restricciones

- NO modifica `.checkpoint` en ningún escenario (operación read-only)
- NO intenta parsear schema antiguo — solo detecta y emite warning
- NO falla si `.checkpoint` está ausente — la ausencia es un escenario válido
- NO escribe en logs verbosos detalles del contenido (Notes pueden tener información sensible personal)
- El modo de presentación respeta la preferencia declarada — no invadir el terminal con contenido completo si el modo es `summary`
