# Kata: Gate de Calidad (Gate 2)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Fase 6 del flujo Issue-Driven — validación final con 7 checks que incluyen trazabilidad AC↔prueba, scope creep, best practices, pruebas, cobertura, tipos y performance budget

## Objetivo

Ejecutar el Gate 2 del flujo Issue-Driven: 7 verificaciones stack-aware sobre la implementación completada en la Fase 4 (y revisada por la Fase 5). Produce informe `go`/`no-go`/`unverifiable` en `docs/issues/issue-{n}/06-quality-report.md`. Cualquier falla regresa a la Fase 4 con contexto detallado; solo `go` permite avanzar a la Fase 7. Los checks que no puedan ejecutarse en el entorno actual (herramienta ausente, sin archivos aplicables) reportan `unverifiable` y se presentan al humano en lugar de pasar silenciosamente.

Esta kata es la **guardiana de la calidad** del flujo — garantiza que la implementación cubre todos los ACs, no sobrepasó el alcance, aplicó las best practices definidas en las Lexis y no regresó la performance más allá de los budgets declarados.

## Cuándo Usar

- Fase 6 del flujo orquestado por `warrior-athena`, tras que `kata-security-review` resulte en `approved`
- Cuando es necesario validar rigurosamente una implementación antes de abrir PR

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Requisitos Fase 2 | Sí | `docs/issues/issue-{n}/02-requirements.md` (ACs numerados) |
| Arquitectura Fase 3 | Sí | `docs/issues/issue-{n}/03-architecture.md` (tabla de componentes — alcance) |
| Implementación Fase 4 | Sí | Código + pruebas en el working tree |
| Revisión Fase 5 | Sí | `docs/issues/issue-{n}/05-security-review.md` (debe estar `approved`) |
| Coverage threshold | No | `quality.coverage_threshold` en `.directives` (por defecto: 80) |
| Stack | Sí | Lenguaje del código implementado (detectado vía archivos tocados) |

## Workflow

```
Progreso:
- [ ] 1. Recolectar contexto (ACs, alcance, diff, stack)
- [ ] 2. Check 1 — Trazabilidad bidireccional AC ↔ prueba
- [ ] 3. Check 2 — Scope creep
- [ ] 4. Check 3 — Best practices (Lexis aplicables por stack)
- [ ] 5. Check 4 — Pruebas ejecutadas
- [ ] 6. Check 5 — Cobertura
- [ ] 7. Check 6 — Tipos
- [ ] 8. Check 7 — Performance budget
- [ ] 9. Consolidar resultado go/no-go/unverifiable
- [ ] 10. Persistir en docs/issues/issue-{n}/06-quality-report.md
- [ ] 11. Actualizar checkpoint
```

### Paso 1: Recolectar contexto

1. Leer ACs de `02-requirements.md` (extraer `AC-1`, `AC-2`, ...).
2. Leer tabla de componentes de `03-architecture.md` (extraer lista de archivos previstos).
3. Ejecutar `git diff --name-only {base}...HEAD` para lista de archivos modificados.
4. Detectar stack (`*.py` → Python; `*.ts` → Node/TS; etc.).
5. Leer `quality.coverage_threshold` de `.ahrena/.directives` (por defecto: `80`).
6. **Detectar modo de ejecución** leyendo el front-matter de `.ahrena/workflow/issue-{n}/checkpoint.md`:
   - Si `stack.approved: true` está presente, el modo es **por capa** (ver sección dedicada abajo); identificar la capa actual (`stack.decomposition[i].status: in-progress`) y filtrar `covers_acs` + `components`.
   - En caso contrario, el modo es **PR único** (comportamiento por defecto; los pasos 2-8 corren sobre el conjunto completo de ACs y componentes).

### Modo por capa (Stacked PRs)

Cuando el checkpoint contiene `stack.approved: true`, esta kata se invoca **una vez por capa** antes de que la capa someta su PR. Cada ejecución opera sobre subsets, no sobre el conjunto completo:

| Check | Alcance en modo por capa |
|---|---|
| Check 1 — AC ↔ prueba | Filtrar por el subset `stack.decomposition[i].covers_acs`. Los ACs fuera de la capa **no** se evalúan en esta corrida; aparecerán en una capa posterior |
| Check 2 — Scope creep | Comparar archivos modificados desde la capa anterior contra `stack.decomposition[i].components` (no contra la tabla completa de la Fase 3) |
| Check 3 — Best practices | Aplicar Lexis sobre archivos modificados en la capa actual (mismas reglas; alcance menor) |
| Check 4 — Pruebas | Ejecutar la suite completa (las pruebas no son particionables por capa con seguridad) |
| Check 5 — Cobertura | Evaluar contra el threshold sobre el conjunto completo del diff hasta la capa actual (acumulado base→capa N) |
| Check 6 — Tipos | Misma regla; alcance = archivos de la capa |
| Check 7 — Performance budget | Misma regla; aplicar cuando la capa toca código sensible a performance |

**Transiciones de status:**
- La capa empieza en `pending`; Athena la promueve a `in-progress` al iniciar la Fase 4 de esa capa.
- Cuando los 7 checks retornan ✅ para la capa, esta kata actualiza `stack.decomposition[i].status: submitted` en el checkpoint.
- Tras el merge del PR de la capa, Athena (o `kata-stacked-pr-merge`) actualiza a `merged`.

**Validación agregada final:** disparada automáticamente al **final de la ejecución de la última capa** — es decir, en la misma invocación de `kata-quality-gate` que promueve la última capa `pending` a `submitted`. Después de que los 7 checks con alcance de capa retornan ✅, la kata corre una pasada agregada adicional que confirma:
1. Todo AC numerado en la Fase 2 fue cubierto por **alguna** capa (sin AC huérfano).
2. Todo componente declarado en la Fase 3 fue tocado por **alguna** capa (sin componente huérfano).

Si la validación agregada falla, el resultado general de la capa se rebaja a `no-go` y el informe apunta los elementos huérfanos. En flujo PR único (sin `stack`), la validación agregada es trivialmente equivalente al Check 1 del conjunto completo y no genera pasada extra.

### Paso 2: Check 1 — Trazabilidad bidireccional AC ↔ prueba

**AC → Prueba:**
1. Para cada AC identificado en el Paso 1, buscar en archivos de prueba (vía regex) por:
   - Nombre conteniendo `AC_{N}` o `AC-{N}`
   - Docstring conteniendo `AC-{N}`
   - Marker `@pytest.mark.ac("AC-{N}")` o equivalente
2. Cada AC debe tener al menos 1 prueba correspondiente.
3. ACs sin prueba → ❌ `Check 1 — AC→Test`.

**Prueba → AC:**
1. Para cada prueba nueva/modificada en el diff, verificar si referencia al menos un AC.
2. Pruebas sin AC referenciado → ❌ `Check 1 — Test→AC` (indica scope creep).

Resultado del Check 1: ✅ si ambas direcciones están completas; ❌ caso contrario.

### Paso 3: Check 2 — Scope creep

1. Comparar lista de archivos modificados (Paso 1) con tabla de componentes de la Fase 3.
2. Archivos fuera de la tabla → candidatos a scope creep.
3. **Excepciones legítimas** (no flagear):
   - Archivos de prueba correspondientes a componentes declarados (ej.: si `service.py` está en la tabla, `test_service.py` es implícito).
   - Archivos de configuración automática (ej.: `requirements.lock`, `yarn.lock`).
   - Documentación generada por el propio flujo (ej.: `docs/issues/issue-{n}/*`).
4. Funciones/clases públicas nuevas en archivos tocados que no mapean a ningún AC → flagear.

Resultado del Check 2: ✅ si solo archivos declarados + excepciones fueron modificados; ❌ si hay scope creep no justificado.

Si ❌: **opciones presentadas al usuario**:
- (a) Ampliar ACs (regresar a Fase 2/3 y reejecutar Gate 1).
- (b) Revertir código fuera de alcance y abrir nueva issue para él.

### Paso 4: Check 3 — Best practices (Lexis aplicables)

Seleccionar Lexis aplicables al stack y ejecutar la verificación de cada una:

**Python (`*.py` en el diff):**

| Lexis | Verificación | Comando / Heurística |
|---|---|---|
| `lex-python-typing` | Sin errores de tipo | `mypy --strict {archivos-tocados}` |
| `lex-python-testing` | Funciones públicas testeadas | Para cada función pública nueva/modificada, buscar prueba que la llama |
| `lex-python-security` | Sin credenciales hardcoded | Regex por patrones de credencial |
| `lex-python-immutability` | Sin mutación en estructuras compartidas | Análisis estático (ast): mutación en parámetros o globals |
| `lex-python-error-handling` | Sin `except: pass` o swallowing | Regex por `except` sin re-raise y sin log |
| `lex-conventional-commits` | Commits en formato correcto | `git log {base}..HEAD --format=%s` + regex `^(feat\|fix\|chore\|docs\|refactor\|test\|build\|ci)(\(.+\))?: .+` |

Registrar violaciones con archivo/línea. Cualquier violación → ❌ `Check 3 — {lex-name}`.

### Paso 5: Check 4 — Pruebas ejecutadas

1. Ejecutar comando de prueba detectado por stack:
   - Python: `pytest`
   - Node/TS: `yarn test` (o `npm test` según `.directives`)
2. Capturar exit code y output.
3. Cualquier falla → ❌ `Check 4 — Tests`.

### Paso 6: Check 5 — Cobertura

1. Ejecutar pruebas con coverage:
   - Python: `pytest --cov={paquete} --cov-report=term-missing`
2. Extraer porcentaje de cobertura total.
3. Comparar con `quality.coverage_threshold` (por defecto: 80).
4. `% < threshold` → ❌ `Check 5 — Coverage ({%}% < {threshold}%)`.

### Paso 7: Check 6 — Tipos

1. Ejecutar verificador de tipos específico del stack:
   - Python: `mypy --strict` sobre paquetes modificados
   - TS: `tsc --noEmit`
2. Capturar errores.
3. Errores nuevos (en archivos modificados en este PR) → ❌ `Check 6 — Types`.
4. Errores preexistentes en archivos no modificados → no bloquear (registrar como nota).

### Paso 8: Consolidar resultado go/no-go

1. Si todos los 6 checks ✅ → resultado `go`.
2. Si cualquier check ❌ → resultado `no-go`.

Para cada ❌, registrar:
- Qué check falló
- Detalles (archivos, líneas, comandos, output)
- Recomendación de corrección

### Paso 9: Persistir en `docs/issues/issue-{n}/06-quality-report.md`

Estructura:

```markdown
# Quality Gate — Issue #{n}: {título}

- **Referencias:** [Requisitos](./02-requirements.md) · [Arquitectura](./03-architecture.md) · [Seguridad](./05-security-review.md)
- **Fecha:** {YYYY-MM-DD}
- **Resultado:** {✅ go | ❌ no-go}

## Matriz de Trazabilidad AC ↔ Prueba

| AC | Descripción | Pruebas que cubren | Status |
|---|---|---|:-:|
| AC-1 | ... | `test_foo_AC_1`, `test_bar_AC_1` | ✅ |
| AC-2 | ... | `test_baz_AC_2` | ✅ |
| AC-3 | ... | — | ❌ |

### Pruebas sin AC referenciado (candidatas a scope creep)

- `test_helper_utility` en `tests/test_utils.py:42` — {recomendación}

## Resultado por Check

| # | Check | Status | Detalles |
|:-:|---|:-:|---|
| 1 | Trazabilidad AC ↔ Prueba | {✅/❌} | {resumen} |
| 2 | Scope Creep | {✅/❌} | {resumen} |
| 3 | Best Practices | {✅/❌} | {resumen} |
| 4 | Pruebas Ejecutadas | {✅/❌} | {resumen} |
| 5 | Cobertura | {✅/❌} | {actual}% / {threshold}% |
| 6 | Tipos | {✅/❌} | {resumen} |

## Detalles de las Fallas

### Check {n}: {nombre}

{descripción detallada, archivos, líneas, output del comando}

**Recomendación:** {cómo corregir}

## Conclusión

- Si `go`: seguir a la Fase 7 (`kata-pr-prepare`).
- Si `no-go`: regresar a la Fase 4 con las correcciones anteriores.
```

### Paso 10: Actualizar checkpoint

1. Actualizar `.ahrena/workflow/issue-{n}/checkpoint.md`:
   - fase completada: 6
   - resultado: `go` o `no-go`
   - Si `go`: siguiente fase = 7
   - Si `no-go`: siguiente fase = 4 (regresar para correcciones)
   - **Modo por capa:** actualizar adicionalmente `stack.decomposition[i].status` de la capa actual — `submitted` cuando `go`; mantener `in-progress` cuando `no-go`. `phase_next` permanece en 4 mientras haya capa pendiente.
2. Informar a `warrior-athena`:
   - Si `go` (PR único): avanzar a `kata-contributing-pr` (según Regla 12 de `lex-issue-driven`).
   - Si `go` (modo por capa): liberar la capa para someter vía `kata-stacked-pr-create`; si aún hay capa pendiente, regresar a la Fase 4 para la siguiente.
   - Si `no-go`: presentar informe al humano y esperar dirección (corregir o ampliar ACs).

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Informe del Gate | Markdown con 6 checks + matriz de trazabilidad | `docs/issues/issue-{n}/06-quality-report.md` |
| Resultado | `go` / `no-go` | Retorno al orquestador |
| Checkpoint actualizado | Markdown | `.ahrena/workflow/issue-{n}/checkpoint.md` |

## Restricciones

- **Los checks se ejecutan, no se simulan:** `pytest`, `mypy`, coverage y scans son comandos reales; la kata no puede "marcar como pasado" sin ejecución efectiva.
- **El orden de los checks es obligatorio:** checks 1-3 (análisis estático) antes de 4-6 (ejecución); si el análisis falla, aún ejecutar los demás para reportar panorama completo.
- **Threshold configurable pero no opcional:** `quality.coverage_threshold` puede ajustarse en `.directives`, pero el Check 5 siempre se ejecuta.
- **Sin override para `no-go`:** la única salida legítima de `no-go` es corregir la implementación o renegociar los ACs (vía Gate 1). Ningún humano o agente puede marcar como `go` manualmente.
- **Destino fijo:** `docs/issues/issue-{n}/06-quality-report.md` (según `lex-issue-driven`). En modo por capa, el informe acumula una sección por capa más una sección agregada final.
- **El subset por capa no relaja criterios:** el filtro de ACs/componentes solo reduce el alcance de la ejecución; los thresholds (cobertura, performance) y la estrictez de los checks permanecen idénticos.

## Referencias

- `lex-issue-driven` — leyes del flujo, en particular las reglas de trazabilidad, scope creep y la Regla 11 (Gate 2 por capa cuando hay stack aprobada)
- `codex-issue-workflow` — detallado completo de los 7 checks
- `codex-stacked-prs` — modelo conceptual y Decision Checklist para stacked PRs
- `kata-stacked-pr-create` — invocado por la Fase 7 cuando hay stack aprobada
- `lex-python-typing`, `lex-python-testing`, `lex-python-security`, `lex-python-immutability`, `lex-python-error-handling`, `lex-conventional-commits` — Lexis verificadas en el Check 3
