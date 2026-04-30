# Kata: Validar Cobertura BDD en la Suite de Pruebas

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Independiente — confirma que cada escenario BDD de negocio en un issue de GitHub esté cubierto por al menos una prueba, mediante marcador canónico o fallback

## Objetivo

Leer el bloque `bdd:scenarios` de un issue de GitHub, escanear la suite de pruebas en busca de marcadores BDD canónicos y patrones fallback, y producir un reporte bidireccional de cobertura (escenarios → pruebas, pruebas → escenarios) clasificado como `complete`, `gaps`, `drift` o `gaps+drift`. La kata no ejecuta pruebas; inspecciona mapeos.

## Cuándo Usar

- Después de que comience la implementación, para confirmar que los escenarios están siendo cubiertos a medida que aterrizan las pruebas.
- En la revisión del PR, para confirmar que un cambio coincide con la intención BDD registrada en el issue.
- Invocada a través de `/cry-bdd-validate-scenarios <issue>`.
- Independiente — independiente de `kata-quality-gate`. Ambas pueden ejecutarse sobre el mismo cambio sin acoplamiento.

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Número de issue | Sí | Issue de GitHub que contiene el bloque `bdd:scenarios` |
| Repositorio | Sí | `owner/repo` (por defecto: detectado vía git remote) |
| Raíz de pruebas | No | Path(s) a escanear; por defecto: raíces comunes por stack |
| Stack | No | Detectado a partir de las extensiones de archivo en el working tree |

## Workflow

```
Progreso:
- [ ] 1. Verificar MCP y directivas
- [ ] 2. Leer el issue y extraer el bloque bdd:scenarios
- [ ] 3. Parsear escenarios en pares (title, slug)
- [ ] 4. Detectar stack(s) y escanear pruebas
- [ ] 5. Construir mapa escenario → prueba
- [ ] 6. Construir mapa prueba → escenario
- [ ] 7. Clasificar gaps y drift
- [ ] 8. Emitir reporte de cobertura
```

### Paso 1: Verificar MCP y directivas

Igual que el Paso 1 de `kata-bdd-create-scenarios`. El MCP `github` es obligatorio; Notion no se usa aquí.

### Paso 2: Leer el issue

Usar `kata-mcp-github-read` para obtener el cuerpo del issue. Localizar el bloque `<!-- bdd:scenarios:start -->` ... `<!-- bdd:scenarios:end -->`. Si está ausente, reportar "no BDD scenarios authored in this issue" y detenerse. La kata es un no-op cuando no hay nada que validar; nunca inventa la ausencia de bloque como un hallazgo.

### Paso 3: Parsear escenarios

Para cada línea `Scenario: <title>` en el bloque:

1. Extraer el título (verbatim, recortado).
2. Calcular el slug: minúsculas, reemplazar secuencias de no alfanuméricos por `-`, colapsar `-` repetidos, recortar `-` al inicio y al final.

Producir una lista `[(title, slug)]`.

### Paso 4: Detectar stack y escanear pruebas

Detectar stacks a partir del working tree:

- `*.py` → Python
- `*.ts|*.tsx|*.js|*.jsx` → JS/TS
- `*.go` → Go

Raíces de prueba por defecto cuando no se especifican:

- Python: `tests/`, `**/test_*.py`, `**/*_test.py`
- JS/TS: `tests/`, `__tests__/`, `**/*.test.{ts,tsx,js,jsx}`, `**/*.spec.{ts,tsx,js,jsx}`
- Go: `**/*_test.go`

Para cada prueba, recolectar:

- `markers`: lista de slugs declarados vía marcador canónico
  - Python: decorador `@bdd_scenario("...")` arriba de la función de prueba (regex; tolerar tanto el helper desnudo como `@pytest.mark.bdd_scenario("...")` cuando el helper envuelve un mark de pytest)
  - JS/TS: etiqueta JSDoc `// @bdd_scenario <slug>` inmediatamente arriba de la prueba, o llamada `bddScenario("<slug>", ...)` envolviendo la prueba
  - Go: comentario `// bdd_scenario: <slug>` inmediatamente arriba de `func TestXxx`
- `fallbacks`: lista de slugs/títulos encontrados vía nombre de prueba o docstring que coincidan con `BDD:\s*<title-or-slug>`

Una sola prueba puede mapear a múltiples escenarios.

### Paso 5: mapa escenario → prueba

Para cada escenario `(title, slug)`:

1. Listar pruebas con marcador canónico que coincida con `slug`.
2. Listar pruebas con fallback que coincida con `title` o `slug` (insensible a mayúsculas/minúsculas en el título; exacto en el slug).
3. Estado: `covered` si ≥1 prueba en cualquiera de los dos grupos; `gap` en caso contrario.

### Paso 6: mapa prueba → escenario

Para cada prueba que tenga al menos un marcador BDD o fallback:

1. Resolver el slug a un escenario en la lista parseada.
2. Si no existe escenario coincidente en el issue → `drift` (marcador huérfano).

### Paso 7: Clasificar

- **`complete`**: cada escenario cubierto, sin marcadores huérfanos.
- **`gaps`**: al menos un escenario sin cobertura.
- **`drift`**: al menos una prueba reclama un escenario ausente del issue.
- Una ejecución puede ser ambos (`gaps+drift`).

### Paso 8: Emitir reporte de cobertura

Tabla Markdown al usuario:

```markdown
# BDD Coverage — Issue #{n}

- **Result:** {complete | gaps | drift | gaps+drift}
- **Scenarios in issue:** {count}
- **Covered:** {count}  | **Uncovered:** {count}  | **Orphan markers:** {count}

## Scenario → Test

| Scenario | Slug | Tests | Status |
|---|---|---|:-:|
| Customer requests a refund for an eligible payment | customer-requests-a-refund-for-an-eligible-payment | tests/refunds/test_create.py::test_pending_refund | ✅ |
| Concurrent refunds deduplicate by idempotency key | concurrent-refunds-deduplicate-by-idempotency-key | — | ❌ |

## Drift (markers without scenarios)

- tests/legacy/test_old.py::test_a — claims `legacy-scenario-removed`
```

Cuando `result != complete`, recomendar correcciones explícitas por hallazgo:

- **Gaps:** agregar una prueba que cubra (cualquier nivel) marcada con el slug del escenario o con `BDD: <title>` en el docstring; alternativamente, eliminar el escenario del issue si la regla ya no está en alcance.
- **Drift:** eliminar el marcador, renombrarlo a un slug válido o restaurar el escenario en el issue.

Si el usuario lo solicita explícitamente, guardar el reporte en `docs/bdd-coverage/{issue-n}.md`. De lo contrario, emitir solo en línea.

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Reporte de cobertura | Respuesta en Markdown | Cara al usuario |
| Reporte guardado opcional | Archivo Markdown | `docs/bdd-coverage/{issue-n}.md` (solo cuando el usuario lo solicita) |

## Restricciones

- **Solo lectura.** No modifica el issue, las pruebas ni ningún otro archivo.
- **No ejecuta pruebas.** La cobertura aquí es estructural (mapeo), no comportamental.
- **No infiere escenarios desde las pruebas.** Una prueba sin marcador no es cobertura.
- **Sin pasadas silenciosas.** Cuando el issue no tiene bloque `bdd:scenarios`, la kata lo dice explícitamente.

## Referencias

- `lex-bdd-coverage` — ley de cobertura
- `codex-bdd` — metodología y convenciones de marcador
- `kata-bdd-create-scenarios` — procedimiento predecesor
- `lex-test-pyramid`, `codex-test-strategy` — decisiones de nivel para las pruebas que cubren
