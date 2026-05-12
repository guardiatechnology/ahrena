# Kata: Scaffolding de Subagent Anthropic Aislado

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Ingeniería — Agents (etapa pre-operacional): creación de un Claude Code subagent standalone con frontmatter Anthropic correcto

## Objetivo

Scaffold rápido de un subagent Anthropic aislado en `agents/<name>.md` con frontmatter compatible con la spec Claude Code subagents. Útil para casos triviales de PoV donde la estructura completa de Skill es excesiva (sin widgets, sin tools/, sin references/) — basta un archivo `.md` con identidad + tooling declarado. Puede ser **standalone** (en `.claude/agents/`) o **dentro de un plugin** (delegado a plan-034).

A diferencia de los 7 katas POV que producen el **dossier documental** en `docs/{context}/agents-pov/{agent}/`, este kata produce el **artefacto ejecutable** (el subagent en sí). Se usa cuando `cry-pov --kind subagent` necesita instanciar el agent, o cuando el usuario invoca `cry-agent` directamente para creación trivial.

## Cuándo Usar

- `cry-pov --kind subagent` despacha aquí para crear el subagent después de que el dossier POV esté listo
- `cry-agent --slug <name>` invoca directamente para creación standalone (sin ciclo POV completo)
- Cuando un PoV existente quiere derivar un subagent simple a partir de una persona aprobada

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `--slug <name>` | Sí | Identificador en kebab-case (ej.: `reconciliation-assistant`) |
| `--target <path>` | No | Destino. Default: `.claude/agents/<slug>.md`. Puede ser `<plugin>/agents/<slug>.md` (plan-034) |
| `--persona <warrior>` | No | Importa identidad base de un warrior existente |
| `--from-pov <path>` | No | Si se invoca dentro de `cry-pov --kind subagent`, importa de `docs/{context}/agents-pov/{agent}/` |
| `--description <text>` | Sí | Descripción corta para el frontmatter (1-2 frases) |

## Workflow

```
Progreso:
- [ ] 1. Validar slug y path destino
- [ ] 2. Componer frontmatter Anthropic
- [ ] 3. Componer cuerpo del subagent
- [ ] 4. Persistir archivo
- [ ] 5. Verificar conformidad mínima
```

### Paso 1: Validar slug y path destino

- `--slug` debe ser kebab-case, 1-64 chars, `[a-z0-9-]`, sin `--` consecutivos, sin guión al inicio o al final.
- Se resuelve `--target`. Default: `.claude/agents/<slug>.md`. Si se pasa otro path (ej.: `<plugin-root>/agents/<slug>.md`), se garantiza que el directorio existe.
- Si ya existe archivo en el destino, se exige `--force`.

### Paso 2: Componer frontmatter Anthropic

Frontmatter mínimo conforme spec Claude Code subagents:

```yaml
---
name: <slug>
description: <descripción literal de --description>
---
```

Si se pasó `--from-pov`, se lee `docs/{context}/agents-pov/{agent}/pov.md` y se popula `description` con la persona declarada allí (1 frase).

### Paso 3: Componer cuerpo del subagent

Estructura mínima del cuerpo (el usuario puede expandirlo después):

```markdown
# <Nombre legible derivado del slug>

## Identidad

stage: pre-operational

<contenido de la persona; si --from-pov, copia bloque persona de pov.md; si --persona, importa identidad del warrior referenciado>

## Capacidades

- <capacidad 1>
- <capacidad 2>

## Restricciones

- No persiste datos más allá de la ventana de contexto actual
- No ejecuta fuera del alcance declarado en `description`

## Notas

- Creado por kata-agent-author en <ISO date>
- Origen: <`--from-pov path` | standalone | warrior reference>
```

Si se pasó `--from-pov`, se copian los bloques `Identidad`, `Capacidades`, `Restricciones` literalmente del `system-prompt.md` correspondiente.

### Paso 4: Persistir archivo

1. Se graba en el `--target`.
2. Se verifica que el archivo fue escrito con permisos correctos.
3. Si el destino es `<plugin>/agents/`, **no** se registra en el `manifest.skill.subagents` del plugin (responsabilidad de plan-034).

### Paso 5: Verificar conformidad mínima

- [ ] Frontmatter tiene `name` y `description`
- [ ] Línea `stage: pre-operational` aparece literalmente en el cuerpo
- [ ] Slug del frontmatter == nombre del archivo (sin `.md`)
- [ ] Descripción es frase concreta (no placeholder)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `<slug>.md` | Markdown con frontmatter YAML | `.claude/agents/<slug>.md` (default) o `<plugin>/agents/<slug>.md` |

## Ejemplo de Ejecución

### Input

```
cry-agent --slug reconciliation-assistant \
          --description "Sugiere pareos extracto↔asiento contable en etapa pre-operacional"
```

### Output (`.claude/agents/reconciliation-assistant.md`)

```markdown
---
name: reconciliation-assistant
description: Sugiere pareos extracto↔asiento contable en etapa pre-operacional
---

# Reconciliation Assistant

## Identidad

stage: pre-operational

Asistente especializado en sugerir pareos entre transacciones de extracto bancario
y asientos contables del ERP de la misma ventana temporal.

## Capacidades

- Sugerir el pareo más probable por valor + fecha + descripción similar
- Indicar nivel de confianza (alto / medio / bajo) por sugerencia

## Restricciones

- No persiste datos más allá de la ventana de contexto actual
- No ejecuta fuera del alcance declarado en `description`
- No crea asientos en el ERP (solo sugiere)

## Notas

- Creado por kata-agent-author en 2026-05-12
- Origen: standalone
```

## Restricciones

- **Nunca** scaffold sin `stage: pre-operational` literal — bloquea conformidad con `lex-agent-construction-directives`.
- **Nunca** placeholder remanente (`<...>`) en el archivo final.
- **Nunca** el kata invoca a Hephaestus o a Apollo — el subagent Anthropic es markdown puro; no hay código que delegar.
- **Siempre** cuando el destino está dentro de un plugin, **plan-034** es responsable por el registro en el manifest del plugin; este kata solo crea el archivo.

---

**Modelo:** Este Kata es el atajo de scaffold trivial. Para PoVs estructurados, prefiera `cry-pov` (ciclo completo). Cuando el subagent es parte de un plugin, plan-034 retoma el relevo.
