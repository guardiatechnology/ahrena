# Cry: Validar BDD (Fase 8)

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Ingeniería — Calidad. Atajo que invoca a `warrior-themis` para ejecutar la Fase 8 del flujo Issue-Driven (diseño de escenarios + validación contra la implementación) y devolver la decisión `go | no-go` del Gate 3.

## Descripción

Acciona la Fase 8 completa para una Issue: `warrior-themis` produce `07-bdd-scenarios.md` (ciego al código) y luego `08-bdd-validation-report.md` (con lectura de pruebas), cerrando con la decisión `go | no-go` para el Gate 3 de `kata-quality-gate`.

Este Cry es uno-a-uno con `warrior-themis` (per `lex-pilars` Regla 5: Cry → 1 Warrior o 1 Kata). El Warrior orquesta internamente `kata-bdd-scenarios-design` y `kata-bdd-validate-implementation`.

## Uso

```
/cry-bdd-validate <número de issue> [<owner>/<repo>]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `número de issue` | Sí | Número de la issue en GitHub | `42` |
| `<owner>/<repo>` | No | Repositorio de destino; predeterminado: detectado vía `git remote` | `guardiafinance/ahrena` |

## Prerrequisitos

- `github` listado en `mcp.servers` en `.ahrena/.directives` (per `lex-mcp`)
- `notion` en `mcp.servers` cuando la Issue referencia páginas Notion
- Variables de entorno: `GITHUB_PAT` (obligatorio), `NOTION_API_KEY` (cuando aplique)
- Fases 1-3 del flujo Issue-Driven concluidas: `01-brief.md`, `02-requirements.md`, `03-architecture.md` en `docs/issues/issue-{n}/`
- **Recomendado:** Gate 2 con decisión `go` (`06-quality-report.md`); si está ausente o `no-go`, el Cry alerta y pide confirmación antes de proceder

## Lo que el Comando Hace

1. Lee `.ahrena/.directives`.
2. Verifica los prerrequisitos (artefactos de las Fases 1-3 y estado del Gate 2).
3. Invoca a **warrior-themis** con el número de la issue y el repositorio.
4. `warrior-themis` ejecuta `kata-bdd-scenarios-design` (Fase 8.1) — ciego al código:
   - Lee fuentes permitidas (Issue, Notion, artefactos del flujo)
   - Produce `docs/issues/issue-{n}/07-bdd-scenarios.md`
5. `warrior-themis` ejecuta `kata-bdd-validate-implementation` (Fase 8.2) — con lectura de pruebas:
   - Mapea cada `SCN-{N}` a las pruebas existentes
   - Verifica acoplamiento a step-runner BDD en los manifiestos
   - Produce `docs/issues/issue-{n}/08-bdd-validation-report.md`
6. Reporta la decisión `go | no-go` del Gate 3 y, cuando es `no-go`, lista las próximas acciones con responsable y nivel.

## Prompt Template

```
Contexto:
- Issue: #{{número de issue}}
- Repositorio: {{<owner>/<repo>}} (o detectado vía git remote)

Tarea:
Actúa como warrior-themis y conduce la Fase 8 del flujo Issue-Driven para la issue
#{{número de issue}}, cerrando con la decisión go | no-go del Gate 3.

Ejecuta en orden estricto:

1. Verifica precondiciones: artefactos de las Fases 1-3 presentes en docs/issues/issue-{n}/.
2. Verifica el estado del Gate 2 (06-quality-report.md). Si está ausente o es no-go, alerta y pregunta si debe proseguir.
3. Fase 8.1 — kata-bdd-scenarios-design:
   - Lee exclusivamente fuentes permitidas (per lex-bdd-spec-only-sources).
   - Produce 07-bdd-scenarios.md con frontmatter declarando fuentes y cobertura por AC.
   - Aplica formato declarativo (per lex-bdd-gherkin-format) y auto-lint vía regex de codex-gherkin.
4. Fase 8.2 — kata-bdd-validate-implementation:
   - Indexa pruebas del repositorio por referencia SCN-{N}.
   - Verifica manifiestos contra la lista prohibida de step-runners (lex-bdd-no-framework-coupling).
   - Produce 08-bdd-validation-report.md con clasificación (covered | partial | missing).
   - Emite decisión go | no-go.
5. Actualiza el checkpoint en .ahrena/workflow/issue-{n}/checkpoint.md.
6. Reporta al usuario: decisión, conteos (covered/partial/missing) y tabla de próximas acciones.

Respeta rigurosamente las Lexis BDD: ciego al código en la Fase 8.1, formato Gherkin
declarativo, sin step-runner, trazabilidad SCN-{N} obligatoria.
```

## Ejemplo de Invocación

**Input:**

```
/cry-bdd-validate 42 guardiafinance/ahrena
```

**Output esperado:**

```
Phase 8 — Issue #42

Phase 8.1 (scenarios design, ciego al código):
✓ 07-bdd-scenarios.md producido (6 escenarios, 4 ACs cubiertas)

Phase 8.2 (mapeo de pruebas):
✓ 08-bdd-validation-report.md producido
  - covered: 4
  - partial: 1 (SCN-5 @nfr a nivel unit)
  - missing: 1 (SCN-6 @nfr idempotencia)
  - acoplamiento a framework: limpio

Decisión Gate 3: NO-GO

Próximas acciones:
| Gap   | Acción                                     | Responsable    | Nivel       |
| SCN-5 | Agregar prueba integration con latencia    | warrior-apollo | integration |
| SCN-6 | Crear prueba de idempotencia               | warrior-apollo | integration |

Checkpoint actualizado.
```

## Restricciones

- **No salta el Gate 2:** si el Gate 2 dio `no-go` o está ausente, el Cry alerta y pide confirmación antes de continuar (la Fase 8 tiene más sentido después de cerrar el Gate 2).
- **No implementa pruebas:** cuando hay gap, el Cry retorna `no-go` con acciones sugeridas — la implementación de las pruebas faltantes se delega en una iteración posterior.
- **Output canónico:** `07-bdd-scenarios.md` y `08-bdd-validation-report.md` en `docs/issues/issue-{n}/`; nunca en otra ruta.
- **Sin invención:** si la Issue está incompleta para alguna AC, el Cry retorna con ACs marcadas `BLOCKED` y devuelve a la fuente (no consulta código para completar).

## Diferencia con Kata

| Aspecto | Cry `cry-bdd-validate` | Katas `kata-bdd-*` |
|---|---|---|
| **Naturaleza** | Atajo de invocación | Procedimiento detallado |
| **Alcance** | Acciona `warrior-themis` | Ejecutados por el Warrior |
| **Complejidad** | Baja (una frase) | Alta (decenas de pasos) |

## Cries y Warriors Asociados

- **warrior-themis** — Warrior invocado por este Cry; orquesta los Katas de Fase 8
- **warrior-athena** — Cuando este Cry es parte del flujo Issue-Driven completo (`/cry-implement-issue`), Athena delega la Fase 8 y este Cry puede ser invocado aisladamente como atajo fuera del flujo
- **warrior-apollo / warrior-hephaestus / warrior-iris** — Reciben acciones de gap cuando el resultado es `no-go`

## Referencias

- `warrior-themis` — agente invocado
- `kata-bdd-scenarios-design` — Fase 8.1
- `kata-bdd-validate-implementation` — Fase 8.2
- `lex-bdd-spec-only-sources`, `lex-bdd-gherkin-format`, `lex-bdd-no-framework-coupling` — leyes del BDD
- `lex-issue-driven` — flujo Issue-Driven (Fase 8 y Gate 3)
- `codex-bdd`, `codex-gherkin` — manuales de referencia
