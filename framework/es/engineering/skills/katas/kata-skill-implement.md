# Kata: Implementar Skill

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Orquestación de la fase de autoría de un proyecto de skill en `{paths.skills_root}/{slug}/`, delegando widgets a `warrior-hephaestus` y tools/scripts Python a `warrior-apollo`, y redactando `SKILL.md` + `references/` directamente

## Objetivo

Conducir la fase `implement` del ciclo de skill: dado un proyecto ya scaffolded por `kata-init-skill`, identificar los gaps (widgets sin implementación, tools sin handler, scripts sin entry, `SKILL.md` aún con placeholders) y delegar cada gap al especialista correcto, con `warrior-claudionor` consolidando el resultado. Este kata **no** implementa código propio fuera de `SKILL.md` y `references/` — su disciplina es orquestar.

## Cuándo Usar

- Inmediatamente después de `cry-new-skill` cuando el scaffold aún tiene placeholders y directorios vacíos
- Cuando el usuario pide "implementar" una skill existente con widgets/tools/scripts incompletos
- Como paso 2 del flujo `cry-skill --mode all` (entre el validate inicial y el package final)

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `slug` | Sí | Nombre del proyecto (idéntico al nombre del directorio en `{paths.skills_root}/`) |
| `gaps` | No | Lista de gaps ya identificados; si está ausente, el kata hace el escaneo |

## Workflow

```
Progreso:
- [ ] 1. Cargar contexto del proyecto (SKILL.md, skill.config.json)
- [ ] 2. Escaneo de gaps (widgets, tools, scripts, SKILL.md, references)
- [ ] 3. Plan de delegación (quién hace qué)
- [ ] 4. Delegar widgets → warrior-hephaestus
- [ ] 5. Delegar tools + scripts Python → warrior-apollo
- [ ] 6. Redactar/actualizar SKILL.md (cuerpo) y references/ in-house
- [ ] 7. Reconciliación (verificar SKILL.md ↔ archivos reales)
- [ ] 8. Reportar progreso al llamador
```

### Paso 1: Cargar contexto

1. Leer `{skills_root}/{slug}/SKILL.md` y `{skills_root}/{slug}/skill.config.json`
2. Identificar el idioma declarado en `metadata.language` (se usa para los mensajes humanos; los identificadores técnicos permanecen en inglés)
3. Identificar los subdirectorios presentes (`widgets/`, `tools/`, `scripts/`, `references/`)

### Paso 2: Escaneo de gaps

Se considera gap, por convención:

| Ubicación | Señal de gap |
|-----------|--------------|
| `SKILL.md` | placeholders `__...__` remanentes; cuerpo solo con headings sin contenido; lista de tools/widgets fuera de sincronía con el filesystem |
| `widgets/` | `package.json` presente pero `src/` vacío o sin `index.tsx`; ningún test; componentes sin props tipados |
| `tools/` | directorio presente pero sin `mcp.config.json` o sin handler para cada tool declarada |
| `scripts/` (Python) | sin `pyproject.toml`; ningún módulo en `src/`; ausencia de test para función pública |
| `scripts/` (JS/TS) | mismo criterio traducido para el stack JS |
| `references/` | listado en `SKILL.md` pero archivo ausente, o existe pero está vacío |

El kata puede recibir la lista vía `gaps`; cuando está ausente, hace el escaneo. Cuando la ambigüedad es irrecuperable, preguntar al usuario antes de delegar.

### Paso 3: Plan de delegación

Componer explícitamente, para cada gap, el par (gap, agente responsable):

| Gap | Agente | Lexis relevantes |
|-----|--------|------------------|
| Widget React/TS | `warrior-hephaestus` | `lex-frontend-typing`, `lex-frontend-accessibility`, `lex-frontend-security`, `lex-frontend-testing` |
| Tool MCP (handler en Python) | `warrior-apollo` | `lex-mcp`, `lex-python-typing`, `lex-python-testing`, `lex-python-error-handling`, `lex-python-result-type`, `lex-python-error-object` |
| Tool MCP (handler en JS/TS) | `warrior-hephaestus` (frontend lead conserva TS) | `lex-frontend-typing`, `lex-mcp` |
| Script Python | `warrior-apollo` | `lex-python-typing`, `lex-python-testing`, `lex-python-security`, `lex-python-immutability` |
| Script JS/TS | `warrior-hephaestus` | `lex-frontend-typing` |
| `SKILL.md` cuerpo + `references/` | **este kata** (Claudionor escribe) | `lex-tone`, `codex-skill-anthropic-agent-skills` |

Presentar el plan al usuario en formato compacto y esperar confirmación cuando el alcance es sustantivo (≥3 delegaciones). Para gaps triviales (un único widget), avanzar sin gate.

### Paso 4: Delegar widgets

Invocar `warrior-hephaestus` vía el subsistema de agentes con un prompt mínimo que contenga:

1. `skills_root/{slug}/widgets/` es el directorio destino (no tocar fuera de él)
2. Lista de componentes a crear/completar (del Paso 2)
3. Lexis aplicables explícitas
4. Solicitud de retorno: lista de archivos producidos + estado (creados, modificados, aún pendientes)
5. Restricción: usar `@guardia/design-system` cuando la skill renderice en una superficie Guardia (`lex-design-system-library`)

Recoger el retorno; **no inferir** éxito — solo el retorno explícito del agente cuenta.

### Paso 5: Delegar tools/scripts Python

Invocar `warrior-apollo` de forma análoga, con:

1. `skills_root/{slug}/tools/` y/o `skills_root/{slug}/scripts/` como directorios destino
2. Lista de handlers/scripts a crear
3. Lexis Python aplicables (`lex-python-*`, `lex-mcp`)
4. Contrato de retorno idéntico al Paso 4

### Paso 6: Redactar SKILL.md y references in-house

Este kata escribe directamente:

1. **Cuerpo de `SKILL.md`:**
   - Resolver placeholders `__...__` remanentes
   - Sincronizar la sección "Tools, scripts, and widgets" con el filesystem real tras los Pasos 4-5
   - Asegurar que las descripciones de uso sean concretas (intent + keywords) según `codex-skill-anthropic-agent-skills`
   - Aplicar `lex-tone` (directo, estratégico, sin buzzwords)
2. **`references/`:**
   - Para cada referencia citada en `SKILL.md`, garantizar existencia y contenido coherente
   - Los snapshots de Lexis/Codex referenciados se pueden extraer del árbol `framework/` cuando aplique; documentar `source_commit` para uso futuro por `kata-skill-package`

### Paso 7: Reconciliación

1. Releer `SKILL.md` y compararlo con el filesystem:
   - Todo widget declarado tiene archivo correspondiente en `widgets/src/`
   - Toda tool declarada tiene handler en `tools/handlers/` (o equivalente declarado en `mcp.config.json`)
   - Toda referencia tiene archivo en `references/`
2. Invocar `kata-skill-validate` como verificación de cierre
3. Si la validación aún falla, generar un sub-plan (gaps remanentes) y volver al Paso 3 — máximo 3 iteraciones antes de escalar al humano

### Paso 8: Reportar

1. Lista de gaps atendidos en esta ejecución
2. Lista de archivos producidos por cada delegación
3. Estado final de `kata-skill-validate`
4. Próximo paso sugerido (`cry-skill --mode package` cuando esté listo, o nueva ronda de `--mode implement` si queda gap residual)

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Implementación de widgets | Archivos bajo `widgets/` | filesystem (producidos por Hephaestus) |
| Implementación de tools/scripts | Archivos bajo `tools/` y `scripts/` | filesystem (producidos por Apollo) |
| `SKILL.md` consolidado + `references/` | Markdown | filesystem (producido por este kata) |
| Reporte de progreso | Texto humano | `stdout` |

## Ejemplo de Ejecución

### Input

```
kata-skill-implement slug=scheduled-payments-skill
```

### Salida esperada (resumen)

```
Gaps identificados (5):
  - SKILL.md: 3 placeholders __...__ remanentes
  - widgets/: TransferForm sin implementación
  - widgets/: ApprovalReview sin implementación
  - tools/: handler validate_amount sin código
  - scripts/: validate_amount.py sin tests

Plan:
  - Hephaestus → widgets/TransferForm, widgets/ApprovalReview
  - Apollo → tools/handlers/validate_amount.py, scripts/tests/test_validate_amount.py
  - Claudionor (este kata) → resolver placeholders + sincronizar SKILL.md

Resultado:
  - 4 archivos creados por Hephaestus
  - 2 archivos creados por Apollo
  - SKILL.md consolidado, placeholders resueltos
  - kata-skill-validate: ✅ no violations

Próximo paso sugerido: cry-skill --mode package --slug scheduled-payments-skill
```

## Restricciones

- El kata **no** implementa widgets, tools ni scripts propios — delega; violar esa frontera viola la división de responsabilidades entre `warrior-claudionor`, `warrior-hephaestus`, `warrior-apollo`
- El kata **escribe directamente** solo `SKILL.md` y `references/`; nada más
- El kata **no** modifica `.directives`, `.gitignore`, `framework/` ni ningún archivo fuera de `{skills_root}/{slug}/`
- Cada delegación retorna explícitamente la lista de archivos producidos; el kata **no infiere** la conclusión de una delegación sin retorno explícito
- Tras 3 iteraciones sin cerrar todos los gaps, el kata escala al humano en lugar de entrar en bucle infinito

## Referencias

- `kata-skill-validate` — verificación de cierre al final
- `kata-skill-package` — sucesor invocado cuando la implementación está lista
- `warrior-claudionor` — orquestador que invoca este kata
- `warrior-hephaestus` — delegación de widgets
- `warrior-apollo` — delegación de tools/scripts Python
- `codex-skill-anthropic-agent-skills` — frontmatter y disclosure
- `codex-skill-project-architecture` — layout del proyecto
- `codex-skill-tools-and-widgets` — convención `tools/` + `widgets/`
- `lex-skill-project-structure` — ley del layout
- `lex-tone` — tono aplicado a `SKILL.md` y `references/`
