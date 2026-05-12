# Cry: Scaffold de Subagent Anthropic Aislado

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Ingeniería — Agents (etapa pre-operacional): creación rápida de un subagent Anthropic standalone sin el ciclo POV completo

## Descripción

Atajo para invocar `kata-agent-author` directamente y crear un subagent Anthropic aislado en `.claude/agents/<slug>.md` (o dentro de un plugin, delegado a plan-034). Para casos triviales donde el ciclo POV completo (`cry-pov`) es overhead — basta un archivo `.md` con frontmatter Anthropic e identidad declarada. El subagent generado **siempre** declara `stage: pre-operational` por construcción; si el PoV madura, la promoción a `operational-concrete` pasa por la DoOC (`lex-agent-construction-directives`).

## Invocación

```
/cry-agent --slug <name> --description "..." [--persona <warrior>] [--target <path>] [--from-pov <path>]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `--slug` | Sí | Identificador en kebab-case (1-64 chars, `[a-z0-9-]`) | `reconciliation-assistant` |
| `--description` | Sí | Descripción corta (1-2 frases) — va al frontmatter | `"Sugiere pareos extracto↔asiento contable"` |
| `--persona` | No | Importa identidad base de un warrior existente | `warrior-apollo` |
| `--target` | No | Path destino. Default `.claude/agents/<slug>.md` | `.claude/agents/`, `plugins/foo/agents/` |
| `--from-pov` | No | Importa de un PoV existente | `docs/reconciliation/agents-pov/rec-pov-classifier/` |
| `--force` | No | Sobreescribe archivo existente | (flag) |

## Lo que el Comando Hace

1. Valida `--slug` (kebab-case, sin `--` consecutivos)
2. Resuelve `--target` (default `.claude/agents/`)
3. Invoca `kata-agent-author` con los parámetros recibidos
4. Persiste archivo `<slug>.md` con frontmatter Anthropic + cuerpo mínimo (Identidad + `stage: pre-operational` + Capacidades + Restricciones)
5. Reporta el path final y validaciones aplicadas

## Prompt Template

```
Crea un subagent Anthropic standalone invocando kata-agent-author.

Slug: {{slug}}
Description: {{description}}
{% if persona %}Persona base: {{persona}}{% endif %}
{% if from_pov %}Origen PoV: {{from_pov}}{% endif %}
{% if target %}Destino: {{target}}{% endif %}

Garantiza:
- Frontmatter Anthropic correcto (`name`, `description`)
- Línea `stage: pre-operational` literal en el cuerpo
- Sin placeholders remanentes

Reporta el path final y el tree del archivo generado.
```

## Ejemplo de Invocación

**Input:**

```
/cry-agent --slug reconciliation-assistant \
           --description "Sugiere pareos extracto↔asiento contable en etapa pre-operacional"
```

**Output esperado:**

```
🛠  cry-agent — scaffold standalone
   slug: reconciliation-assistant
   target: .claude/agents/reconciliation-assistant.md

→ kata-agent-author
   ✅ frontmatter validado
   ✅ stage: pre-operational declarado
   ✅ archivo creado

Contenido (extracto):
   ---
   name: reconciliation-assistant
   description: Sugiere pareos extracto↔asiento contable en etapa pre-operacional
   ---
   # Reconciliation Assistant
   ## Identidad
   stage: pre-operational
   ...

Próximos pasos:
   - Iterar el cuerpo del subagent según el uso
   - Cuando necesite ciclo PoV estructurado, considere /cry-pov --kind subagent
```

**Input (importando de PoV existente):**

```
/cry-agent --slug reconciliation-assistant \
           --description "Sugiere pareos extracto↔asiento contable" \
           --from-pov docs/reconciliation/agents-pov/rec-pov-classifier/
```

**Output esperado:**

```
🛠  cry-agent — scaffold standalone (--from-pov)
   slug: reconciliation-assistant
   importando de: docs/reconciliation/agents-pov/rec-pov-classifier/

→ kata-agent-author
   ✅ persona importada de pov.md
   ✅ Capacidades y Restricciones copiadas de system-prompt.md
   ✅ stage: pre-operational mantenido
   ✅ archivo creado en .claude/agents/reconciliation-assistant.md
```

## Restricciones

- `--slug` debe seguir las restricciones de la spec Anthropic Agent Skills (kebab-case; sin `--` consecutivos; sin guión al inicio/al final).
- `--description` debe ser concreto (no placeholder).
- El subagent generado **siempre** tiene `stage: pre-operational` — promoción a `operational-concrete` requiere DoOC.
- El Cry **no** invoca `lex-*` ni `codex-*` directamente (`lex-pilars`); la orquestación es responsabilidad del kata.
- Cuando `--target` apunta a dentro de un plugin, **plan-034** es responsable por registrar el subagent en el manifest del plugin; este cry solo crea el archivo.

## Diferencia de `cry-pov`

| Aspecto | `cry-agent` | `cry-pov` |
|---|---|---|
| **Naturaleza** | Scaffold trivial | Ciclo POV completo |
| **Output** | 1 archivo `.md` | `docs/{context}/agents-pov/{agent}/` + implementación |
| **Cuándo usar** | Ya hay claridad de alcance y tooling; basta el archivo | Inicio de un PoV real con cliente |
| **Directrices** | Identidad declarada (Directriz 01 mínima) | Las 6 Directrices aplicadas en rigor pre-operacional |

---

**Modelo:** Este Cry es el atajo para creación trivial. Para PoVs estructurados, prefiera `cry-pov` (ciclo completo).
