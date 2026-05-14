# Ahrena: AI-First Capability Framework

**Ahrena** es un Capability Framework AI-first que estructura conocimiento, procesos y comportamiento de agentes de IA mediante una **taxonomía unificada** (Clade → Subclade → Pilar). Lexis, Codex, Katas, Warriors y Cries se organizan por disciplina y área, orientando cómo humanos e IA colaboran en cualquier dominio.

**Principios:** IA como copiloto (no piloto); proceso sobre herramienta; artefactos versionados como código; `framework/` como fuente de verdad, agnóstico de plataforma.

---

## Instalación

### Requisitos previos

Ahrena verifica el host en tres niveles durante `make bootstrap` / `make install` (preflight). Use `make preflight` para ejecutar los checks de forma aislada.

**Hard (bloquea el install si falta):**
- **Python 3.8+** — intérprete para los scripts
- **git** — control de versión
- **make** — entrypoint del Makefile

**Soft (avisa y ofrece instalar):**
- **gh** (GitHub CLI) — usado por el flujo Issue-Driven, stacked PRs y el cost-stamp
- **gpg** — exigido por `lex-signed-commits`

**Lazy (instalado bajo demanda cuando el MCP correspondiente se activa vía `make mcp-enable`):**
- **Node.js** — solo para el servidor MCP de Figma (nivel npx). GitHub y Notion usan HTTP remoto, sin dependencia local.

**Cómo instalar manualmente:**
- **Windows:** `winget install --id Git.Git -e`, `winget install --id GnuWin32.Make -e`, `winget install --id GitHub.cli -e`, `winget install --id GnuPG.Gpg4win -e`, `winget install --id OpenJS.NodeJS.LTS -e`.
- **macOS:** `xcode-select --install` cubre git y make (vía Command Line Tools); `brew install gh gnupg node` para el resto.
- **Linux (Debian/Ubuntu):** `sudo apt-get install -y git build-essential gh gnupg nodejs npm`. RHEL/Fedora: `sudo dnf install -y git gh gnupg2 nodejs npm` + `sudo dnf groupinstall -y 'Development Tools'`.

### Plataformas

| Nombre | Descripción |
|--------|-------------|
| **Cursor** | IDE con soporte integrado: el instalador genera `.cursor/` (rules, skills, commands, agents) a partir del framework. [Soporte para Cursor](#soporte-para-cursor) |
| **Claude Code** | Soporte para Claude Code: el instalador genera `.claude/` (docs, skills, commands, agents) y `CLAUDE.md` a partir del framework. [Soporte para Claude Code](#soporte-para-claude-code) |

### Primera instalación

El instalador descarga el framework desde GitHub y configura el proyecto (no es necesario clonar el repositorio).

**Por Makefile (recomendado):**

```powershell
# Windows (PowerShell)
Invoke-WebRequest https://github.com/guardiafinance/ahrena/releases/latest/download/Makefile -OutFile Makefile
make bootstrap PLATFORM=cursor
```

```bash
# macOS / Linux
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/Makefile -o Makefile
make bootstrap PLATFORM=cursor
```

**Por one-liner (sin Make):**

```powershell
# Windows — solo framework
Invoke-WebRequest https://github.com/guardiafinance/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py; Remove-Item install.py

# Windows — framework + Cursor IDE
Invoke-WebRequest https://github.com/guardiafinance/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py --platform cursor; Remove-Item install.py

# Windows — framework + Claude Code
Invoke-WebRequest https://github.com/guardiafinance/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py --platform claude-code; Remove-Item install.py
```

```bash
# macOS / Linux — framework + Cursor
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/install.py | python3 - --platform cursor

# macOS / Linux — framework + Claude Code
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/install.py | python3 - --platform claude-code
```

**Opciones del instalador:**

| Flag | Descripción |
|------|-------------|
| `--platform cursor` | Generar `.cursor/` (rules, skills, commands, agents) |
| `--platform claude-code` | Generar `.claude/` (docs, skills, commands, agents) y `CLAUDE.md` |
| `--clades X,Y` | Instalar solo los clades indicados (ej.: `_foundation,documentation`) |
| `--version v0.1.0` | Versión específica (tag o rama) — instalación remota |
| `--local` | Usar el directorio actual como fuente (ejecutar en la raíz del repo Ahrena) |
| `--source PATH` | Usar un clon local de Ahrena en PATH en lugar de descargar de GitHub |
| `--self` | Usar el repo Ahrena que contiene este script como fuente — instalación offline |
| `--language en` | Sobrescribir idioma por defecto en `.directives` |
| `--directives PATH` | Usar `.directives` personalizado (ruta local o URL) |
| `--target PATH` | Instalar en otro directorio |
| `--dry-run` | Simular sin realizar cambios |
| `--clean` | Eliminar archivos instalados por Ahrena |

Cuando se usa `--clades`, la selección se guarda en `.ahrena/.installed-clades` y es respetada por `update.py`.

### Instalación offline

Si no hay acceso a internet, o desea distribuir Ahrena en entornos restringidos, use la flag `--self` desde un clon local del repositorio:

```bash
# Clonar el repo una vez (con acceso a red)
git clone https://github.com/guardiafinance/ahrena.git

# Instalar en cualquier proyecto, desde cualquier directorio, sin red
python /ruta/a/ahrena/scripts/install.py --self --target /ruta/al/proyecto --platform cursor
python /ruta/a/ahrena/scripts/install.py --self --target /ruta/al/proyecto --platform claude-code
```

**Por Makefile** (desde la raíz del repo Ahrena):

```bash
make install-to TARGET=/ruta/al/proyecto PLATFORM=cursor
make install-to TARGET=/ruta/al/proyecto PLATFORM=claude-code LANGUAGE=en
```

`--self` detecta automáticamente la raíz del repo Ahrena desde la ubicación del propio script, independientemente del directorio de trabajo actual.

### Actualización y desinstalación

| Acción | Makefile | Script directo |
|--------|----------|----------------|
| **Actualizar (remoto)** | `make update` o `make update VERSION=v0.2.0` | `python .ahrena/update.py` |
| **Actualizar (local)** | `make update LOCAL=1` o `make update SOURCE=../ahrena` | `python .ahrena/update.py --local` o `--source /ruta/a/ahrena` |
| **Re-sincronizar Cursor** | `make sync-cursor` | `python .ahrena/update.py --sync-cursor` |
| **Re-sincronizar Claude Code** | `make sync-claude-code` | `python .ahrena/update.py --sync-claude-code` |
| **Desinstalar** | `make uninstall` | `python .ahrena/uninstall.py` (u `--force` sin confirmación) |

**Por defecto:** la instalación y actualización vienen del **remoto** (GitHub). Para fuente local use `--local` / `--source` o en el Makefile `LOCAL=1` / `SOURCE=...`.

**Desarrollo local (contribuidores):** `make dev-install PLATFORM=cursor` — usa los fuentes locales de `framework/` en lugar de descargar de GitHub.

### Qué se instala

| Comando | `.ahrena/` | `.cursor/` | `.claude/` + `CLAUDE.md` |
|---------|------------|------------|--------------------------|
| Sin `--platform` | framework, directives, scripts, Makefile | — | — |
| `--platform cursor` | idem | rules, skills, commands, agents | — |
| `--platform claude-code` | idem | — | docs, skills, commands, agents + CLAUDE.md + RTK hook |

### RTK (Rust Token Killer)

Al instalar con `--platform claude-code`, Ahrena también vincula el **hook `PreToolUse` de RTK** en `.claude/settings.json`. RTK reescribe comandos comunes (`git`, `gh`, `tsc`, `pytest`, `jest`, etc.) hacia versiones con salida compacta, reduciendo el consumo de tokens en 60–90%.

Comportamiento:

- **Por defecto `rtk.enabled: true`** en `.directives`: cada `make install` / `make dev-install` / `make update` reconcilia el hook de forma idempotente. Cuando `rtk.auto_install_binary: true` (también el default), el instalador detecta el binario e intenta instalarlo cuando está ausente (`brew` en macOS, `curl install.sh | sh` en Linux/macOS, WSL o `cargo` en Windows). Las fallas de instalación del binario no son fatales.
- **Opt-out total**: define `rtk.enabled: false` en `.ahrena/.directives` — install/update no tocan ningún artefacto RTK.
- **Opt-out granular**: define `rtk.auto_install_binary: false` para mantener el wire del hook pero saltar el intento automático de instalación del binario.
- **Fallback estricto**: el comando escrito en `settings.json` es `if command -v rtk >/dev/null 2>&1; then rtk hook claude; fi`. Cuando el binario está ausente del PATH el hook termina vacío y Claude Code procede con la entrada original — sin errores.

Binario y documentación: <https://github.com/rtk-ai/rtk>.

---

## MCP (Model Context Protocol)

Ahrena admite servidores MCP para GitHub, Notion y Figma. Cuando se activan, el instalador genera automáticamente las entradas correspondientes en `.cursor/mcp.json` y `.claude/settings.json`.

### Activar servidores MCP

Agregue la sección `mcp` a su `.ahrena/.directives`:

```yaml
mcp:
  servers:
    - github
    - notion
    - figma
```

En la próxima ejecución de `make sync-cursor`, `make sync-claude-code` o `make install-to`, las entradas MCP se fusionarán de forma **aditiva** — los servidores que usted gestione fuera de Ahrena se conservan.

### Servidores disponibles

| Servidor | Variable de entorno | Uso |
|----------|---------------------|-----|
| `github` | `GITHUB_PAT` | Crear issues, PRs, push de archivos, listar commits |
| `notion` | `NOTION_API_KEY` | Crear y sincronizar páginas, buscar databases |
| `figma` | `FIGMA_API_KEY` | Extraer design tokens, specs de componentes, exportar frames |

Las credenciales siempre se referencian mediante variables de entorno — **nunca** hardcodeadas en archivos versionados.

### Katas MCP

| Kata | Plataforma | Descripción |
|------|-----------|-------------|
| `kata-mcp-github-read` | GitHub | Consulta repositorios, issues, PRs, commits y código (solo lectura) |
| `kata-mcp-notion-read` | Notion | Consulta páginas, databases y bloques de Notion (solo lectura) |
| `kata-mcp-figma-extract` | Figma | Extrae design tokens y specs de componentes de Figma |

---

## Pilares (tipos de capacidad)

| Pilar | Función | Prefijo | Detalles |
|-------|---------|---------|----------|
| **Lexis** | Leyes inquebrantables (seguridad, calidad, proceso) | `lex-` | [Plantillas y convenciones](./framework/es/README.md#estructura) |
| **Codex** | Manuales de referencia para decisiones contextualizadas | `codex-` | [Plantillas y convenciones](./framework/es/README.md#estructura) |
| **Katas** | Procedimientos repetibles (skills) | `kata-` | [Plantillas y convenciones](./framework/es/README.md#estructura) |
| **Warriors** | Agentes especializados (persona + alcance) | `warrior-` | [Plantillas y convenciones](./framework/es/README.md#estructura) |
| **Cries** | Comandos recurrentes (atajos) | `cry-` | [Plantillas y convenciones](./framework/es/README.md#estructura) |

Descripción completa de cada Pilar y cuándo usarlo: [Framework — Guía del desarrollador](./framework/es/README.md).

### Clades y Subclades

**Clade** = disciplina de negocio. **Subclade** = área de conocimiento dentro de la disciplina. Detalle por Clade y enlaces a READMEs:

| Clade | Subclades | Documentación |
|-------|-----------|---------------|
| **product** | discovery, strategy, analytics, delivery | Extensible por organización |
| **engineering** | platform, backend, frontend, devops, security, quality, workflow | [Platform (Guardia)](framework/es/engineering/platform/README.md) · [Workflow (Issue-Driven)](framework/es/engineering/workflow/README.md) · Backend (Apollo) · Frontend (Hephaestus) · DevOps (Atlas) |
| **finance** | accounting, treasury, controllership | Extensible por organización |
| **operations** | support, infrastructure, monitoring | Extensible por organización |
| **documentation** | i18n (traducción) | [Sistema de traducción / Hermes](framework/es/documentation/i18n/README.md) |
| **_foundation** | authoring, contributing, process, quality, security, tooling, i18n | Transversal a todos los Clades; [Contributing](framework/es/_foundation/contributing/README.md), [Authoring](framework/es/_foundation/authoring/README.md), [Tooling](framework/es/_foundation/tooling/README.md) |

Clades y Subclades son **extensibles**: cada organización define los que tengan sentido.

### Warriors disponibles

| Warrior | Nombre | Clade | Uso |
|---------|--------|-------|-----|
| `warrior-translator` | Hermes | documentation/i18n | Traducción de documentación técnica; [detalles](framework/es/documentation/i18n/README.md) |
| `warrior-daedalus` | Daedalus | engineering/platform | Diseño de API RESTful (OAS); `/cry-api-design`, `/cry-full-design` |
| `warrior-kronos` | Kronos | engineering/platform | Event Storm y CloudEvents; `/cry-event-storm`, `/cry-full-design` |
| `warrior-apollo` | Apollo | engineering/backend | Implementación Python con Clean Architecture; `/cry-python-implement` |
| `warrior-hephaestus` | Hephaestus | engineering/frontend | Implementación Frontend (React/TS) con a11y y pruebas comportamentales |
| `warrior-atlas` | Atlas | engineering/devops | Arquitectura de soluciones AWS; Well-Architected; IaC y costo |
| `warrior-hera` | Hera | engineering/quality | Estrategia de pruebas, plan de cobertura, auditoría de suite |
| `warrior-hestia` | Hestia | engineering/sre | SLO, runbooks, respuesta a incidentes, post-mortem blameless |
| `warrior-demeter` | Demeter | engineering/data | Modelado de datos, migrations seguras, retención LGPD/GDPR |
| `warrior-iris` | Iris | engineering/mobile | Implementación iOS/Android paritaria, offline-first, accesibilidad |
| `warrior-athena` | Athena | engineering/workflow | Orquestadora del flujo Issue-Driven; `/cry-implement-issue` |

Para la arquitectura del framework (paths, diagramas, correspondencia con `.cursor/`), consulte la [Guía del desarrollador](./framework/es/README.md#arquitectura-del-framework).

---

## Flujo Issue-Driven Development

Ahrena ofrece un **flujo completo de desarrollo orientado por issues de GitHub**, conducido por `warrior-athena`. Partiendo de una issue, el flujo pasa por 7 fases (análisis → requisitos → arquitectura → implementación → seguridad → quality gate → PR), con 2 gates humano/automático, generación de ADRs (`docs/adr/`) y documentación estructurada en `docs/issues/issue-{n}/`.

```bash
# Requisito previo: mcp.servers incluye github (y opcionalmente notion) en .ahrena/.directives
/cry-implement-issue 42 guardiafinance/ahrena
```

**Gate 1 (Alcance):** el humano aprueba brief + ACs + arquitectura antes de la implementación.
**Gate 2 (Calidad):** automatizado con 6 checks — trazabilidad AC↔prueba (bidireccional), scope creep, best practices, pruebas, cobertura, tipos.

Guía completa: [engineering/workflow/README.md](framework/es/engineering/workflow/README.md).

---

## Workflow Status

Per ADR-002 (modelo Issue-as-plan), el plan canónico vive en tres capas:

1. **Body de la Issue de GitHub** — canonical. Summary + Plan (Objective, Steps, Risks, Dependencies, Open Questions). Audit log = timeline nativo de GitHub.
2. **`.plans/{N}.md`** (gitignored) — working memory de la IA. Superset del body de la Issue + bloques `<!-- not-flushed -->` para scratch. Materializado por `kata-load-plan-from-issue`; flushed por `kata-flush-plan-to-issue`.
3. **`.issues/{N}/`** (committed) — Phase artifacts (`01-brief.md` … `06-quality-report.md`) del flujo Issue-Driven.

El enum de `status:` vive como **label** en la Issue (y en el PR a partir de `to review`), dividido en dos ejes disjuntos (`lex-issue-status`):

**Eje A — Dev cycle** (Issues/PRs de feature/fix/chore):
```
todo → development → to review → review → done
                          ↘
                          abandoned (terminal alternativo)
```

**Eje B — Release cycle** (release Issue dedicada creada por Janus):
```
to release → release → done
                  ↘
                  abandoned
```

Mutex es **intra-artefacto** (cada Issue/PR carga exactamente una label `status:*`); cross-cycle labeling está prohibido por el HARD-GATE de `lex-issue-status`.

Owners de las transiciones (`lex-agent-planning`):

| Transición | Owner | Eje |
|---|---|---|
| `— → todo` | `warrior-eunomia` (fallback: agente de la sesión) | A |
| `todo → development → to review` | `warrior-athena` | A |
| `to review ↔ review` | `warrior-argos` | A |
| `to review → done` | `warrior-athena` (en el merge) | A |
| `— → to release → release → done` | `warrior-janus` (release Issue dedicada con `Tracks: #N1, ...`) | B |

Cree las labels del framework con `scripts/bootstrap_labels.sh [owner/repo]` o `make bootstrap-labels`.

**Cadencia de load/flush:** sincronización entre `.plans/{N}.md` y el body de la Issue ocurre en 3 disparadores canónicos: (a) cada transición de label `status:`, (b) cada Step marcado como concluido, (c) fin de sesión (heartbeat finaliza). Toggles intermedios y ediciones de scratch (`<!-- not-flushed -->`) son libres. Documentación operacional en `codex-agent-planning`.

**Loop 3×15min:** tras abrir el PR, Athena agenda 3 ciclos de 15 min y cobra al reviewer humano vía MCP de notificación (`notifications.provider` en `.ahrena/.directives`, canal `notifications.channels.pr_review_timeout`) si no hay aprobación en el tercer ciclo. Manuales: `codex-notifications` (provider-agnóstico) y `codex-mcp-slack` (provider inicial).

---

## Soporte para Cursor

Ahrena ofrece **soporte integrado para Cursor IDE**. Con `--platform cursor` (o `PLATFORM=cursor` en el Makefile), el instalador genera el directorio `.cursor/` a partir del `framework/`, de modo que Lexis, Codex, Katas, Warriors y Cries se utilicen directamente en el editor:

| Recurso Cursor | Origen en el framework |
|----------------|------------------------|
| **Rules** (`.mdc`) | Lexis y Codex — contexto inyectado en el agente |
| **Skills** (`SKILL.md`) | Katas y Warriors — capacidades bajo demanda |
| **Commands** (`.md`) | Cries — comandos rápidos vía `/cry-nombre` |
| **Agents** (`.md`) | Warriors — subagentes especializados |

Las reglas se aplican automáticamente según el alcance del proyecto; skills y commands están disponibles en el chat.

**Configuración por plataforma:** la transposición (qué Pilar se convierte en qué recurso) y la aplicación de rules (alwaysApply, globs, description) se definen en **`platforms.yaml`** (por defecto en `framework/platforms.yaml`, override en `.ahrena/platforms.yaml`). Más detalles en [codex-platforms](framework/es/_foundation/process/codex/codex-platforms.md).

---

## Soporte para Claude Code

Ahrena ofrece **soporte integrado para Claude Code**. Con `--platform claude-code`, el instalador genera `.claude/` y `CLAUDE.md` a partir del `framework/`:

| Recurso Claude Code | Origen en el framework |
|---------------------|------------------------|
| **Docs** (`.md`) | Lexis y Codex — documentación de referencia inyectada en el contexto |
| **Skills** (`SKILL.md`) | Katas — procedimientos repetibles bajo demanda |
| **Commands** (`.md`) | Cries — comandos rápidos vía `/cry-nombre` |
| **Agents** (`.md`) | Warriors — subagentes especializados |
| **CLAUDE.md** | Lexis esenciales inyectadas directamente en el contexto de sesión |

La configuración `claude-code.docs` en `platforms.yaml` controla qué artefactos se inyectan directamente en `CLAUDE.md` (`essential: true`) frente a los que se listan como referencias (`essential: false`).

---

## Validador de estructura

Ahrena incluye un validador para garantizar que el contenido del framework sigue las convenciones antes de una transposición.

```bash
# Validar todo
make validate
# o
python scripts/validate.py

# Validar checks específicos
python scripts/validate.py --check naming,platforms
```

| Check | Qué valida |
|-------|-----------|
| `naming` | Todo `.md` comienza con prefijo de Pilar o es `README.md` |
| `path` | El archivo está en el directorio correcto del Pilar (`lexis/`, `katas/`, etc.) |
| `sections` | Secciones obligatorias presentes (ley en Lexis, workflow en Kata, etc.) |
| `i18n` | Todo archivo en `pt-BR/` tiene su contraparte en `en/` y `es/` |
| `platforms` | Todo `lex-` y `codex-` tiene entrada en `cursor.rules` de `platforms.yaml` |

Código de salida `0` = todo pasó; `1` = violaciones encontradas. Puede usarse como hook de pre-commit.
