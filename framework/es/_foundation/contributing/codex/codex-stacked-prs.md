# Codex: Stacked Pull Requests en el Contexto Ahrena

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Concepto, modelo de decisión y operación de Pull Requests encadenados (stacked) para features grandes en cualquier repositorio Guardia

## Visión General

Stacked Pull Requests son una cadena de PRs donde cada branch apunta al anterior, permitiendo que una feature grande se descomponga en capas revisables en aislamiento. En lugar de un único PR de 2 mil líneas que recibe rubber-stamp, son N PRs de 200-400 líneas cada uno, encadenados, mergeados de abajo hacia arriba.

Este Codex es el manual canónico para decidir **cuándo** apilar y **cómo** operar la cadena. La operación descrita aquí usa exclusivamente `git` + `gh` CLI (camino **vanilla**), funcionando en cualquier repositorio GitHub. Los caminos con herramientas (git-spice, gh-stack) reutilizan los conceptos definidos aquí y agregan automatización por encima.

La adopción es **opcional** y se gobierna por la directiva `stacked_prs.tool` en `.ahrena/.directives` (default `vanilla`).

## Contexto

- **Dominio:** descomposición de features grandes en PRs encadenados
- **Audiencia:** todos los contribuyentes (humanos y agentes); Athena en el flujo Issue-Driven (futuro)
- **Actualización:** cuando las Lexis referenciadas cambian, cuando entran nuevos caminos de tool (plan-005, plan-006), o cuando la Decision Checklist se refina con base en uso real

---

## 1. Modelo conceptual

### 1.1 Cadena de branches

```
main
 └── feat/{N}-stack-1-{slug}     ← PR #X (base: main)
      └── feat/{N}-stack-2-{slug}  ← PR #Y (base: feat/{N}-stack-1-{slug})
           └── feat/{N}-stack-3-{slug}  ← PR #Z (base: feat/{N}-stack-2-{slug})
```

Cada capa es un PR real en GitHub, con base apuntando a la capa anterior. La capa base apunta a `main`. Todos los PRs comparten un único worktree compartido (ver sección 4).

### 1.2 Modelo de issue (1 → N)

Una única issue paraguas gobierna toda la stack. Las capas referencian:

| Capa | Body del PR |
|---|---|
| 1..N-1 (intermedias) | `Refs #N` |
| N (última) | `Closes #N` |

Cuando la última capa mergea, GitHub cierra la issue automáticamente. **No crear issues hijas** por capa — el modelo es umbrella issue + ACs numerados que mapean a capas. Ver `lex-issue-first` para la regla base.

### 1.3 Naming pattern

Compatible con `lex-git-branches`:

```
{type}/{N}-stack-{layer}-{slug}
```

| Campo | Regla |
|---|---|
| `type` | Uno de los tipos Conventional Commits: `feat`, `fix`, `docs`, `build`, `chore`, `ci`, `style`, `refactor`, `perf`, `test` |
| `N` | Número de la issue paraguas |
| `layer` | Entero 1, 2, 3, ... (capa en la stack, base→tope) |
| `slug` | kebab-case, máximo 50 caracteres en total |

Ejemplos válidos:
- `feat/42-stack-1-schema`
- `feat/42-stack-2-api`
- `feat/42-stack-3-ui`

La presencia del segmento literal `stack-{layer}` en el slug es la señal canónica de que la branch forma parte de una stack.

> **Importante:** `{slug}` es único y compartido por toda la stack — es el mismo `{slug}` usado en el directorio del worktree (`.worktrees/{N}-{slug}-stack/`); solamente `{layer}` distingue capas. Los nombres `schema`/`api`/`ui` en los ejemplos de arriba son valores de `{layer}`, no de `{slug}`.

---

## 2. Decision Checklist (canónica)

Esta sección es la **fuente de verdad** consultada por `kata-stacked-pr-create` en la Fase 0 (Pre-flight) y por `cry-new-stacked-pr` en invocación explícita. No duplicar criterios en otros artefactos.

### 2.1 Señales altas (cada una cuenta 1 punto)

| Señal | Threshold |
|---|---|
| Tamaño estimado del diff | > 500 líneas modificadas |
| ACs independientes en la issue | ≥ 4 ACs |
| Pilares técnicos atravesados | ≥ 2 (ej.: backend + frontend) |
| Capas obvias presentes | schema → API → UI; data → service → handler; o equivalente |
| Independencia de review | reviewer A puede evaluar capa X sin necesitar el contexto de Y |
| Riesgo de rollback por capa | cambio con migración + feature visible en la misma issue |

### 2.2 Anti-señales (presencia de cualquiera veta la stack)

| Anti-señal | Razón |
|---|---|
| Hotfix / respuesta a incidente | velocidad > granularidad; cascade rebase atrasa el fix |
| Cross-fork PR | herramientas de stack no soportan bien; manualmente es frágil |
| Refactor monolítico | cambio que no se descompone en capas independientes (ej.: rename atravesando todo el módulo) |

### 2.3 Heurística

- **≥ 3 señales altas AND 0 anti-señales** → proponer stack con descomposición concreta
- **Caso contrario** → redirigir a PR único (`kata-contributing-pr`)

La decisión final siempre es del humano. El agente **propone**, el usuario **confirma**.

### 2.4 Descomposición típica

| Tipo de feature | Capas sugeridas |
|---|---|
| API nueva con persistencia | 1) migration + entity, 2) repository + use case, 3) router + DTOs, 4) tests + observability |
| UI feature con backend | 1) schema + migration, 2) API endpoints, 3) frontend components, 4) E2E + telemetry |
| Refactor con extracción de módulo | 1) nuevo módulo aislado, 2) puntos de uso migrados, 3) cleanup del código antiguo |
| Adopción de Lexis nueva | 1) Lexis + Codex, 2) Kata operacional, 3) Cry y actualizaciones en platforms.yaml |

---

## 3. Mapeo por Lexis afectadas

Stacked PRs conviven con las Lexis existentes. La tabla siguiente es referencia rápida:

| Lexis | Estado | Cómo Stacked PRs respeta |
|---|---|---|
| `lex-protected-trunk` | ✅ | Force-push solo en branches de la stack, nunca en trunk; PRs mergean por flujo normal |
| `lex-issue-first` | ✅ | Issue paraguas existe antes de la branch base; cada PR referencia vía `Refs #N` o `Closes #N` |
| `lex-issue-quality` | ✅ | Issue paraguas atiende los 5 criterios canónicos una vez; capas heredan |
| `lex-git-branches` | ✅ | Naming `{type}/{N}-stack-{layer}-{slug}` sigue el regex `^(feat\|fix\|...)\/[0-9]+-[a-z0-9][a-z0-9-]{0,49}$` |
| `lex-git-worktrees` | ⚠️ excepción | Stack ocupa **un único** worktree compartido: `.worktrees/{N}-{slug}-stack/`. Cláusula declarada en "Excepciones permitidas" de la Lexis |
| `lex-pr-quality` | ✅ | HARD-GATE de 8 criterios aplica **por PR de la stack** (cada capa es un PR real); labels del issue se espejan en cada uno |
| `lex-conventional-commits` | ✅ | Cada capa usa commits convencionales normalmente |
| `lex-small-commits` | ✅ | Capas refuerzan atomicidad — un cambio lógico por capa |
| `lex-signed-commits` | ✅ | Rebase preserva firma GPG cuando `commit.gpgsign=true` |
| `lex-commit-language` | ✅ | Sin cambio |
| `lex-issue-driven` | 🔄 follow-up | Athena aún no orquesta stacks; cubierto por plan-006 (futuro) |

---

## 4. Worktree compartido

A diferencia del flujo estándar (1 branch = 1 worktree), una stack entera ocupa **un único** worktree:

```
.worktrees/{N}-{slug}-stack/
```

| Campo | Regla |
|---|---|
| `N` | Número de la issue paraguas |
| `slug` | Slug descriptivo, sin el segmento `stack-{layer}` |

Ejemplo: para la issue #42 (scheduled payments), el worktree es `.worktrees/42-scheduled-payments-stack/`. Dentro de él, el agente alterna entre las branches de la stack vía `git checkout`.

Razón técnica: el cascade rebase opera leyendo y reescribiendo las branches en secuencia; un worktree por branch rompe el supuesto de working dir único.

La excepción está declarada en `lex-git-worktrees` en la sección "Excepciones permitidas" (Regla 5).

---

## 5. Ciclo de vida de la stack

```
issue paraguas existe
    ↓
Decision Checklist (Fase 0 del kata-create)  →  reprobado: PR único
    ↓ aprobado
crear worktree compartido
    ↓
para cada capa i de 1..N:
    git checkout -b feat/{N}-stack-{i}-{slug}
    work
    commit firmado
    push
    gh pr create --base {capa anterior}
    gh pr edit (espejo de labels/assignee/reviewers)
    ↓
review ocurre en paralelo (capa inferior primero)
    ↓
¿cambio en capa inferior?  →  cascade rebase (kata-rebase)
    ↓
merge bottom-up (kata-merge):
    merge layer 1
    gh pr edit layer 2 --base main
    rebase layer 2 onto main
    repite para capas superiores
    ↓
después de la última capa mergeada:
    git worktree remove
    cleanup branches locales
```

Detalles operacionales quedan en los katas dedicados:

- `kata-stacked-pr-create` — Fase 0 (Decision Checklist) y creación de la cadena
- `kata-stacked-pr-rebase` — cascade rebase manual tras cambio en capa inferior
- `kata-stacked-pr-merge` — política bottom-up y cleanup

---

## 6. Límites recomendados

| Aspecto | Límite vanilla | Cuándo sobrepasar |
|---|---|---|
| Número de capas | 3-4 | Considerar git-spice (plan-005) que automatiza cascade rebase |
| Tamaño promedio por capa | 200-500 líneas | Capas muy pequeñas indican descomposición artificial; muy grandes cancelan el beneficio de review |
| Duración de la stack viva | ≤ 2 semanas | Stacks largas acumulan conflicto con `main`; preferir mergear capas bajas y abrir nueva stack |
| ACs por capa | 1-3 ACs | Más que eso indica capa muy amplia; refinar la descomposición |

---

## 7. Trade-offs del camino vanilla

| Ventaja | Trade-off |
|---|---|
| Cero dependencia externa — funciona en cualquier repositorio GitHub hoy | Cascade rebase es manual; cada cambio en capa inferior exige 1 rebase + 1 push por capa superior |
| Flujo transparente — cada comando es un `git`/`gh` legible | Más propenso a error humano (rebase contra branch errada, force-push sin lease) |
| Compatible con cualquier hook/lint/CI existente | Sin UI nativa de "stack map"; revisores deben navegar PR a PR |
| Auditable paso a paso | Reorder de capas en el medio es caro (recrear manualmente) |

Para stacks de 4+ capas o alta frecuencia de iteración, considerar `git-spice` cuando plan-005 mergee.

---

## 8. Buenas prácticas

1. **Descomponer por contrato, no por archivo.** Las capas deben representar interfaces estables (schema, API, UI), no directorios. El reviewer de la capa N+1 confía en el contrato cerrado por la capa N.
2. **`--force-with-lease` siempre.** Nunca `--force` ciego. El lease evita sobrescribir commits de otra persona que estaba revisando la capa.
3. **Mergear capas bajas rápido.** No esperar la stack entera para mergear la base — cuanto más tiempo viva, más conflicto acumula.
4. **Actualizar `base` del PR siguiente explícitamente tras cada merge.** GitHub no migra automáticamente; ver `kata-stacked-pr-merge`.
5. **Espejar labels en cada capa.** `lex-pr-quality` aplica por PR; `kata-stacked-pr-create` automatiza vía `gh pr edit`.
6. **Escribir en el body de cada PR qué fracción cubre.** Ej.: `Refs #42 (2/3 — API endpoints)`. Ayuda al reviewer a entender la posición.

---

## 9. Cuándo NO usar stacked PRs

- Cambio trivial (typo, docs minor, single-file refactor) — overhead de N PRs supera la ganancia
- Hotfix de incidente — velocidad > granularidad
- Stack propuesta sin capas naturales (forzar descomposición artificial)
- Equipo no familiarizado con `git rebase` — riesgo de error de cascade
- Cross-fork — limitación técnica de las herramientas de stack

En cualquiera de estos casos, el agente redirige a `kata-contributing-pr` (PR único).

---

## 10. Directiva `stacked_prs.tool`

En `.ahrena/.directives`:

```yaml
stacked_prs:
  tool: vanilla   # vanilla | gs
```

| Valor | Comportamiento |
|---|---|
| `vanilla` | Default; sigue los procedimientos descritos en este codex y en los katas correspondientes |
| `gs` | Disponible tras plan-005 mergee; activa las secciones "Variant: git-spice" de los katas |

Ausencia de la directiva = `vanilla` implícito.

---

## Referencias

- `lex-issue-first` — issue obligatoria antes de la branch
- `lex-issue-quality` — 5 criterios canónicos del issue
- `lex-git-branches` — naming pattern de branches
- `lex-git-worktrees` — excepción declarada para stacks
- `lex-pr-quality` — HARD-GATE aplicado por PR de la stack
- `lex-protected-trunk` — protección del trunk preservada
- `lex-conventional-commits`, `lex-small-commits`, `lex-signed-commits` — disciplinas de commit mantenidas
- `kata-stacked-pr-create` — Pre-flight (Fase 0) + creación de la cadena
- `kata-stacked-pr-rebase` — cascade rebase manual
- `kata-stacked-pr-merge` — merge bottom-up
- `cry-new-stacked-pr` — atajo que invoca el kata-create
- `kata-contributing-pr` — flujo de PR único (fallback cuando Decision Checklist reprueba)
