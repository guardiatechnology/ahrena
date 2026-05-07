# Codex: git-spice (gs) — automatización de stacked branches

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Instalación, setup, catálogo de comandos y mapeo operativo de `git-spice` cuando el proyecto adopta esta herramienta para Stacked Pull Requests

## Visión General

`git-spice` es una CLI escrita en Go (licencia GPL-3.0) que automatiza operaciones de stacked branches sobre git nativo. El caso de uso central en el contexto Ahrena es eliminar el cascade rebase manual: cuando una capa inferior recibe `commit create` o `commit amend` vía `git-spice`, todas las capas superiores se rebasean automáticamente. Otras facilidades incluyen trunk declarado una sola vez (`gs repo init --trunk`), `gs repo sync` que elimina branches mergeados y rebasea el resto, y `gs auth login` que reutiliza el token de `gh` mediante el método CLI.

Este Codex es la referencia de campo cuando `.ahrena/.directives` declara `stacked_prs.tool: gs`. Las decisiones estratégicas (stack vs PR único, descomposición en capas, naming, política bottom-up) permanecen en `codex-stacked-prs` — este documento cubre solo la operación con `gs`.

## Contexto

- **Dominio:** automatización de cadenas de branches stacked vía CLI dedicada; alternativa al camino vanilla (`git` + `gh`)
- **Audiencia:** agentes de IA (warriors y katas que ejecutan `kata-stacked-pr-create`, `kata-stacked-pr-rebase`, `kata-stacked-pr-merge`); contribuyentes humanos que ejecutan stacks manualmente
- **Actualización:** cuando los flags de `gs` cambian en una nueva release, cuando una versión de `gs` se adopta como mínimo testeado del framework, o cuando el troubleshooting recurrente justifica una nueva entrada

## Contenido

### 1. Versión mínima testeada

| Ítem | Valor |
|------|-------|
| `git-spice` mínimo testeado | `0.28.0` |
| `git` mínimo exigido por gs | `2.38` |
| Forges soportadas | GitHub, GitLab (desde gs 0.9.0), Bitbucket Cloud (desde gs 0.25.0) |

> **Importante:** el binario instalado por Homebrew se llama `git-spice`, no `gs`. El alias `gs` es una convención de shell (`alias gs='git-spice'`); la documentación oficial y este Codex usan `gs` por brevedad. Cada vez que un agente ejecuta el comando programáticamente, DEBE invocar `git-spice` para no depender de un alias del usuario.

### 2. Instalación

| Plataforma | Comando |
|------------|---------|
| macOS / Linux (Homebrew) | `brew install git-spice` |
| Cualquier SO con Go ≥ 1.22 | `go install go.abhg.dev/gs@latest` |
| Debian / Ubuntu | `.deb` en [releases](https://github.com/abhinav/git-spice/releases) |
| Fedora / RHEL | `.rpm` en releases |
| Alpine | `.apk` en releases |
| Arch Linux (AUR) | `git-spice-bin` |

Tras instalar, agregar el alias si se desea:

```bash
# bash / zsh
echo "alias gs='git-spice'" >> ~/.zshrc

# fish
abbr -a gs git-spice
```

Verificación:

```bash
git-spice --version
# git-spice 0.28.0 o superior
```

### 3. Setup por repositorio (una vez)

#### 3.1 Inicialización

Dentro del repositorio (en cualquier worktree, incluido el worktree compartido de un stack):

```bash
git-spice repo init --trunk main --remote origin
```

| Flag | Significado |
|------|-------------|
| `--trunk=BRANCH` | Branch protegida contra writes (`main`, `master`, `release/*`). Honra `lex-protected-trunk` |
| `--remote=NAME` | Remote para push de branches submitidas (default: `origin`) |
| `--upstream=NAME` | Remote contra el cual abrir CRs; difiere de `--remote` solo en fork mode |
| `--reset` | Olvida toda la metadata de `gs` para el repositorio (raro; usar cuando la metadata se corrompe) |

Si `--upstream` no se pasa, gs usa el mismo remote que `--remote`. Re-ejecutar `repo init` en un repo ya inicializado migra branches existentes al nuevo trunk si cambia.

La metadata vive en `.git/spice/` (dentro de `.git/`, sin tracking — no requiere `.gitignore`).

#### 3.2 Autenticación

```bash
git-spice auth login
```

El prompt ofrece:

| Método | Cuándo preferir |
|--------|-----------------|
| **CLI** | `gh` (o `glab`) ya autenticado en la máquina — `gs` reutiliza el token; opción más rápida en entorno Ahrena |
| **OAuth** | Flujo en navegador; sin `gh` instalado |
| **GitHub App** | Instalación per-repo; útil en organizaciones con SSO restrictivo |
| **Git Credential Manager** | Reutilización de credenciales ya almacenadas por Git |
| **Personal Access Token** | Token generado manualmente; menos seguro que OAuth |

El token se almacena en el keyring del SO (Keychain en macOS, Secret Service en Linux, Credential Manager en Windows). Para revalidar:

```bash
git-spice auth status            # consulta el estado
git-spice auth login --refresh   # renueva
git-spice auth logout            # elimina
```

> **Regla Ahrena:** no persistir tokens en archivos versionados ni en `.ahrena/.directives` (per `lex-mcp` regla 2 y prácticas equivalentes). Usar exclusivamente el keyring del SO.

### 4. Catálogo de comandos por categoría

Versión de referencia: gs 0.28.0. Cada subcomando tiene un alias corto entre paréntesis.

#### 4.1 Repositorio

| Comando | Función |
|---------|---------|
| `gs repo (r) init (i)` | Inicializa metadata de gs en el repo (define trunk, remotes) |
| `gs repo (r) sync (s)` | Pull del trunk + elimina branches ya mergeados + opcional `--restack` |
| `gs repo (r) restack (r)` | Restack de **todas** las branches rastreadas por gs |

#### 4.2 Branch

| Comando | Función |
|---------|---------|
| `gs branch (b) track (tr)` | Importa branch existente al gs (opcional `--base`) |
| `gs branch (b) untrack (untr)` | Quita branch del tracking sin eliminarla |
| `gs branch (b) checkout (co)` | Cambia de branch dentro del stack |
| `gs branch (b) create (c)` | Crea nueva branch encima de la actual; commitea el stage actual; acepta `--target`, `--insert`, `--below`, `-m`, `-a` |
| `gs branch (b) delete (d, rm)` | Elimina branch (local + tracking) |
| `gs branch (b) submit (s)` | Crea/actualiza CR solo de la branch actual |
| `gs branch (b) restack (r)` | Restack solo de la branch actual contra su base |
| `gs branch (b) onto (on)` | Mueve la branch a otra base (sustituye `git rebase --onto` en casos comunes) |
| `gs branch (b) rename (rn, mv)` | Renombra branch y actualiza metadata |
| `gs branch (b) fold (fo)` | Mergea la branch en su base (consolida capas) |
| `gs branch (b) split (sp)` | Divide la branch en múltiples branches por commit |
| `gs branch (b) squash (sq)` | Squash de la branch en un commit único |
| `gs branch (b) edit (e)` | `git rebase -i` consciente del stack |
| `gs branch (b) diff (di)` | Diff entre branch y base |

#### 4.3 Stack / Upstack / Downstack

| Comando | Función |
|---------|---------|
| `gs stack (s) submit (s)` | Submite **todo** el stack (crea/actualiza CR de cada capa) |
| `gs stack (s) restack (r)` | Restack de todo el stack |
| `gs stack (s) edit (e)` | Reordena o quita capas vía editor (uso esporádico) |
| `gs stack (s) delete (d)` | Elimina **todas** las branches del stack |
| `gs upstack (us) submit (s)` | Submite solo la branch actual y las superiores |
| `gs upstack (us) restack (r)` | Restack solo de la branch actual y las superiores |
| `gs upstack (us) onto (o)` | Mueve la branch actual + capas superiores a una nueva base |
| `gs upstack (us) delete (d)` | Elimina solo las branches superiores |
| `gs downstack (ds) track (tr)` | Importa branches por debajo en el grafo |
| `gs downstack (ds) submit (s)` | Submite solo la branch actual y las inferiores |
| `gs downstack (ds) edit (e)` | Reordena capas inferiores |

#### 4.4 Commit

| Comando | Función |
|---------|---------|
| `gs commit (c) create (c)` | Atajo para `git commit` + `gs upstack restack` (mantiene capas superiores sincronizadas) |
| `gs commit (c) amend (a)` | Atajo para `git commit --amend` + `gs upstack restack` |
| `gs commit (c) split (sp)` | Divide el último commit en múltiples |
| `gs commit (c) fixup (f)` | Crea commit fixup contra commit anterior |
| `gs commit (c) pick (p)` | Cherry-pick consciente del stack |

Flags relevantes (`commit create` / `commit amend`):

| Flag | Función |
|------|---------|
| `-a, --all` | Stage automático de archivos modificados (equivale a `git commit -a`) |
| `-m, --message=MSG` | Mensaje inline |
| `--no-verify` | Salta hooks `pre-commit`/`commit-msg` (usar con cautela; consultar `lex-conventional-commits`) |
| `--signoff` | Agrega `Signed-off-by:` (no es firma GPG; ver sección 7) |
| `--no-edit` (solo amend) | No abre el editor |

#### 4.5 Rebase

| Comando | Función |
|---------|---------|
| `gs rebase (rb) continue (c)` | Continúa rebase interrumpido por conflicto (sustituye `git rebase --continue`) |
| `gs rebase (rb) abort (a)` | Aborta rebase en curso |

#### 4.6 Log y navegación

| Comando | Función |
|---------|---------|
| `gs log (l) short (s)` | Lista branches rastreadas (visualización del stack) |
| `gs log (l) long (l)` | Lista branches + commits |
| `gs up (u)` | Sube una capa |
| `gs down (d)` | Baja una capa |
| `gs top (U)` | Va al tope del stack |
| `gs bottom (D)` | Va a la base del stack |
| `gs trunk` | Va al trunk (`main`) |

### 5. Mapeo operación → vanilla → gs

Tabla de equivalencia entre el camino vanilla descrito en `codex-stacked-prs` y el camino gs. Útil al alternar entre proyectos.

| Operación | Vanilla (`git` + `gh`) | git-spice |
|-----------|------------------------|-----------|
| Inicializar soporte de stacks en el repo | (sin setup) | `gs repo init --trunk main` (una vez) |
| Crear la primera capa del stack | `git checkout -b feat/N-stack-1-slug main` | `gs branch create feat/N-stack-1-slug` (con stage) |
| Crear capa superior | `git checkout -b feat/N-stack-2-slug feat/N-stack-1-slug` | `gs branch create feat/N-stack-2-slug` (estando en capa 1, con stage) |
| Commitear manteniendo capas superiores sincronizadas | `git commit && for i in superiores: git checkout {i} && git rebase {i-1} && git push --force-with-lease` | `gs commit create -m "..."` (auto-restack de las capas superiores) |
| Amendar commit ya submitido | `git commit --amend && cascade rebase manual` | `gs commit amend [--no-edit]` (auto-restack) |
| Rebasear contra trunk avanzado | `git fetch && git rebase origin/main && cascade rebase manual` | `gs repo sync --restack` |
| Submitir PR solo de la capa actual | `gh pr create --base $PREV --head $THIS ...` | `gs branch submit` |
| Submitir PRs de todo el stack | loop de N `gh pr create` | `gs stack submit [--draft] [--fill]` |
| Actualizar PRs tras push | (auto vía push del head) | `gs branch submit` o `gs stack submit` (idempotente) |
| Force-push seguro | `git push --force-with-lease` | gs ya usa lease por default; `--force` lo bypassa |
| Eliminar branches mergeados | manual: `git push origin --delete` + `git branch -D` | `gs repo sync` (cleanup local; `--delete-branch` en el merge cuida el remoto) |
| Actualizar `base` del PR tras merge de la capa inferior | `gh pr edit $PR --base main` | `gs repo sync` rebasea automáticamente; `gs branch submit` recrea con nueva base |
| Resolver conflicto en rebase | `git rebase --continue` / `--abort` | `gs rebase continue` / `gs rebase abort` |
| Reordenar capas en el medio | recrear manualmente | `gs stack edit` |

### 6. Force-push: lease por default

A diferencia de `git push`, `gs branch submit` y `gs stack submit` aplican `--force-with-lease` automáticamente — el push se rechaza si un revisor commiteó por encima desde el último fetch.

| Flag | Comportamiento |
|------|----------------|
| (default) | `--force-with-lease` implícito |
| `--force` | Bypass del lease — equivale a `git push --force` ciego |
| `--no-verify` | Salta hooks `pre-push` |

> **Regla Ahrena:** nunca pasar `--force` sin justificación registrada. El default cubre el 99% de los casos. `--no-verify` requiere autorización explícita del usuario (la misma disciplina aplicada al camino vanilla).

### 7. Interacción con hooks y GPG

#### 7.1 Hooks pre-commit / commit-msg

`gs commit create` y `gs commit amend` ejecutan hooks como lo haría `git commit`. Para hooks pesados (linters, tests), el auto-restack puede ser lento porque cada capa superior repite el ciclo del hook. Mitigaciones:

1. **Optimizar hooks** — mover validación pesada al CI; mantener pre-commit rápido (≤ 1s).
2. **Hook condicional al estado del stack** — un hook que detecta `.git/spice/` activo puede elegir modo lite.
3. **`--no-verify` deliberado** — en casos extremos, con autorización del usuario y justificación registrada (idealmente en el body del PR).

#### 7.2 Firma GPG (lex-signed-commits)

`gs` respeta la config global de git (`commit.gpgsign=true`, `user.signingkey`). Como `gs commit create/amend` llama a `git commit` por debajo, la firma se preserva normalmente; no hay flag específico en `gs`. En el rebase de auto-restack, git re-aplica los commits y — si `commit.gpgsign=true` — firma los nuevos commits resultantes con la clave configurada.

Verificación:

```bash
git log --show-signature -3
# esperado: "Good signature from ..." en cada commit de las capas
```

> **Atención:** `--signoff` (`Signed-off-by:`) es un trailer en texto plano, no firma criptográfica. `lex-signed-commits` exige firma GPG verificable; el trailer es opcional y ortogonal.

### 8. Workflow recomendado (resumen)

1. `gs repo init --trunk main` — una vez por repo.
2. `gs auth login` (método **CLI** si `gh` está logueado).
3. Worktree compartido del stack (per `codex-stacked-prs` sección 4): `git worktree add .worktrees/{N}-{slug}-stack -b feat/{N}-stack-1-{slug} main`.
4. `cd .worktrees/{N}-{slug}-stack`
5. Editar archivos, `git add`, `gs commit create -m "feat(scope): capa 1 — schema (1/N)"`.
6. `gs branch create feat/{N}-stack-2-{slug}` (estando en stage con archivos de la capa 2). Repetir hasta la última capa.
7. `gs stack submit --draft` para abrir todos los PRs como borrador de una sola vez (o `--fill` para completar título/body desde el commit).
8. Para cada PR creado, espejar labels/assignee/reviewers vía `gh pr edit` (ver `kata-stacked-pr-create` sección "Variant: git-spice"). `gs stack submit` acepta `--label`, `--reviewer`, `--assign` pero no diferencia por capa — para mirror exacto usar `gh pr edit`.
9. Iteración de review: `gs commit amend` en la capa cuestionada, después `gs branch submit` (idempotente).
10. Merge bottom-up: `gh pr merge --squash` de la capa base; después `gs repo sync` para rebasear el resto y eliminar la capa mergeada localmente.

### 9. Limitaciones conocidas

| Limitación | Origen |
|------------|--------|
| Cross-fork PR (forks con upstream y push remotes diferentes) solo crea CR para branches directamente sobre el trunk | Doc oficial — `guide/limits/` |
| Squash-merge upstream borra historia unsquashed; capas superiores requieren `gs repo sync` (a veces `gs upstack restack`) para reflejar | Doc oficial |
| Bitbucket Cloud sin soporte de labels, assignees o template enumeration vía `gs submit` | Doc oficial |
| Repositorios que descartan approval al cambiar la base del PR son incompatibles con stacks (limitación de GitHub, no de `gs`) | Doc oficial |
| El reorder de capas vía `gs stack edit` está bien soportado, pero hooks que dependen de un orden específico de commits pueden confundir el restack — testear primero en sandbox | Operativo |

### 10. Troubleshooting

| Síntoma | Causa probable | Resolución |
|---------|----------------|------------|
| `gs commit create` falla con "branch is not tracked" | Branch creada con `git checkout -b` en lugar de `gs branch create` | `gs branch track` para importar |
| `gs stack submit` rechaza el push | `--force-with-lease` detectó divergencia (alguien commiteó en la branch remota) | `git fetch origin {branch}` e investigar; nunca `--force` sin entender |
| Auto-restack entra en loop con hook pesado | Hook re-disparando rebase | Optimizar el hook o usar `--no-verify` con autorización |
| `gs auth status` muestra "not logged in" pero `gh` está | Método de auth seleccionado fue distinto de **CLI** la primera vez | `gs auth login --refresh` y elegir **CLI** |
| Squash merge upstream genera "artificial conflicts" en el rebase | Historia squashed no coincide con lo que `gs` esperaba | `gs repo sync` resuelve la mayoría; si no, `gs upstack onto main` |
| `gs repo init --trunk main` falla con "trunk does not exist" | Branch trunk aún no existe localmente | `git fetch origin && git checkout main && gs repo init --trunk main` |
| Confusión entre `gs` y `git-spice` | Alias no configurado | Usar `git-spice` directo en scripts; `gs` solo en shell interactivo |

### 11. Directiva relacionada

La elección entre `vanilla` y `gs` se controla por `.ahrena/.directives`:

```yaml
stacked_prs:
  tool: gs        # vanilla (default) | gs
```

| Valor | Comportamiento |
|-------|----------------|
| `vanilla` (o ausente) | Las katas ejecutan el procedimiento `git` + `gh` clásico |
| `gs` | Las katas ejecutan la sección "Variant: git-spice" — pre-condición: `git-spice` instalado y `gs repo init` ejecutado |

Cambiar de `vanilla` a `gs` en un proyecto con stacks activos exige importación manual vía `gs branch track` para cada branch existente. No hay automatización para esa migración.

## Glosario

| Término | Definición |
|---------|------------|
| Trunk | Branch protegida contra writes, objetivo final del stack (`main`, `master`, `release/*`). Declarada una vez en `gs repo init --trunk` |
| Stack | Cadena ordenada de branches donde cada una tiene la anterior como base; en git-spice, el conjunto rastreado por gs |
| Upstack / Downstack | Capas por encima / por debajo de la branch actual en el stack |
| Restack | Re-rebase de una o más capas contra sus bases actualizadas; en gs es automático tras `commit create`/`amend` |
| Track | Importar una branch git existente al tracking de gs |
| CR (Change Request) | Término agnóstico de gs para Pull Request (GitHub) / Merge Request (GitLab) / Pull Request (Bitbucket) |
| `--force-with-lease` | Variante de `git push --force` que rechaza overwrite de commits remotos no fetchados localmente; default en `gs submit` |

## Referencias

- [git-spice — sitio oficial](https://abhinav.github.io/git-spice/)
- [git-spice — repositorio (GPL-3.0)](https://github.com/abhinav/git-spice)
- `codex-stacked-prs` — modelo conceptual y Decision Checklist canónica (compartida entre vanilla y gs)
- `kata-stacked-pr-create` sección "Variant: git-spice" — pasos operativos de creación
- `kata-stacked-pr-rebase` sección "Variant: git-spice" — auto-restack y resolución de conflictos
- `kata-stacked-pr-merge` sección "Variant: git-spice" — merge bottom-up con `gs repo sync`
- `cry-new-stacked-pr` — atajo que despacha kata-create por `stacked_prs.tool`
- `lex-protected-trunk` — protección del trunk preservada (`gs` la respeta)
- `lex-git-branches` — `gs` acepta el naming `{type}/{N}-stack-{layer}-{slug}`
- `lex-signed-commits` — firma GPG preservada vía `commit.gpgsign=true` global
- `lex-pr-quality` — labels/assignee/reviewers aún se aplican vía `gh pr edit` por PR
