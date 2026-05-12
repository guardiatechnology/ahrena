# Kata: Seleccionar Herramientas de PoV

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Ingeniería — Agents (etapa pre-operacional): selección del subconjunto mínimo de herramientas Anthropic para alimentar el caso de uso primario

## Objetivo

Producir `docs/{context}/agents-pov/tools.md` con el subconjunto mínimo de tools Anthropic (web search, code execution, file write) necesarias para el caso de uso primario del PoV. Cero MCP custom, cero ML especializado, cero tooling fuera del ecosistema Anthropic nativo. Aplica la Directriz 03 de `lex-agent-construction-directives` (Herramientas Concretas) en la óptica de PoV: búsqueda + ejecución simple basta para probar valor; sofisticación queda para Mêtis.

## Cuándo Usar

- Después de `kata-pov-scope-define` (overview listo)
- Como paso paralelo a `kata-pov-system-prompt` (sin dependencia fuerte)
- Cuando una capacidad del prompt depende de tooling no declarado en `tools.md` (reactiva este kata)

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `docs/{context}/agents-pov/overview.md` | Sí | Define el caso de uso primario |
| `codex-skill-tools-and-widgets` | Sí | Convención Ahrena para `tools/` y widgets dentro de Skills |
| `codex-skill-anthropic-agent-skills` | Sí | Spec Anthropic para tools declaradas en SKILL.md |

## Workflow

```
Progreso:
- [ ] 1. Leer overview.md y listar capacidades requeridas
- [ ] 2. Mapear capacidades → tools Anthropic nativas
- [ ] 3. Rechazar tooling fuera del alcance
- [ ] 4. Documentar parámetros mínimos y ejemplos
- [ ] 5. Persistir tools.md
```

### Paso 1: Leer overview.md y listar capacidades requeridas

1. Se lee `docs/{context}/agents-pov/overview.md`.
2. Para cada capacidad implícita en el caso de uso primario, se lista la operación concreta (ej.: "buscar asientos del ERP" → lectura de archivo CSV; "validar conciliación" → ejecución de script Python).

### Paso 2: Mapear capacidades → tools Anthropic nativas

Catálogo permitido en PoV:

| Tool Anthropic | Cuándo usar |
|---|---|
| `web_search` | Cuando el PoV necesita información pública (regulación, FX, tasas) |
| `str_replace_editor` / file write | Cuando necesita leer/editar archivos del proyecto |
| `code execution` (sandbox Anthropic) | Cuando necesita ejecutar Python para validar regla de negocio |
| `bash` (sandbox) | Cuando necesita orquestar comandos shell idempotentes |

Para cada ítem de la lista del Paso 1, se apunta exactamente 1 tool del catálogo. Si ninguno cubre, **se reescopa el caso de uso** (volver a `kata-pov-scope-define`) — no se intente custom.

### Paso 3: Rechazar tooling fuera del alcance

Vetado en PoV:

- MCP servers custom (los MCP servers oficiales de Anthropic son OK si ya están listados en `.ahrena/.directives::mcp.servers`)
- Bibliotecas de ML entrenadas (transformers, scikit-learn) — queda para `warrior-apollo-agents` (plan-013) cuando Mêtis proyecte producción
- Integración con API externa **paga** sin sandbox público
- Caché persistente entre sesiones — la Directriz 02 en PoV es solo corto-plazo

Si el caso de uso primario **exige** algo de la lista vetada, es señal fuerte de que el PoV está prematuro: se documenta el gap en `overview.md::Fuera de alcance` y se prosigue sin el tool.

### Paso 4: Documentar parámetros mínimos y ejemplos

Para cada tool seleccionada, se documenta:

- Operación (verbo + objeto)
- Parámetros mínimos requeridos
- Ejemplo de invocación real (no ficticia)
- Límite (ej.: "web_search ≤ 3 llamadas por turn")

### Paso 5: Persistir tools.md

Se graba `docs/{context}/agents-pov/tools.md` con secciones: Capacidades requeridas, Mapping capacidad→tool, Tools seleccionadas (una sección por tool), Tools rechazadas (con justificación), Límites por turn.

### Validación Final

- [ ] Todas las capacidades del caso de uso primario tienen tool mapeada
- [ ] Cero MCP custom
- [ ] Cero biblioteca ML
- [ ] Ejemplos de invocación reales (no inventados)
- [ ] Límites por turn declarados

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `tools.md` | Markdown | `docs/{context}/agents-pov/tools.md` |

## Ejemplo de Ejecución

### Input (overview.md, extracto)

```
Caso de uso primario: sugerir pareo extracto↔asiento contable por valor + fecha + descripción.
```

### Output (tools.md, extracto)

```markdown
## Capacidades requeridas

1. Leer extracto bancario (CSV/OFX) del proyecto
2. Leer asientos contables (CSV exportado del ERP)
3. Ejecutar lógica de comparación (similitud de strings)

## Mapping capacidad → tool

| Capacidad | Tool Anthropic |
|---|---|
| Leer extracto + asientos | str_replace_editor (read) |
| Ejecutar similitud | code execution (Python sandbox) |

## Tools seleccionadas

### str_replace_editor (read)

- Operación: lectura de archivo
- Parámetros mínimos: `command=view, path=<file>`
- Ejemplo: lectura de `inputs/statement-2026-04.csv`
- Límite: ≤ 5 lecturas por turn

### code execution (Python sandbox)

- Operación: ejecutar comparación de strings
- Parámetros: `code=<python>`, con `rapidfuzz` permitido como dependencia ligera
- Ejemplo: `compare("Pago alquiler", "ALQUILER REF MAR/26") -> 0.82`
- Límite: ≤ 1 ejecución por turn (caro)

## Tools rechazadas

- MCP custom para ERP: gap declarado en overview.md::Fuera de alcance
- Modelo NER entrenado: prematuro para PoV
```

## Restricciones

- **Nunca** introducir MCP custom en PoV. Si es necesario, es señal de que el caso de uso ya pasó la etapa pre-operacional.
- **Nunca** declarar tool sin ejemplo real de invocación.
- **Nunca** más de 3 tools por PoV. Más que eso indica alcance demasiado amplio.

---

**Modelo:** Este Kata aplica la Directriz 03 (`lex-agent-construction-directives`) en el rigor pre-operacional. Tooling sofisticado queda para Mêtis (plan-032) cuando el agent sea promovido.
