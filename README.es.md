# Ahrena: AI-First Capability Framework

**Ahrena** es un Capability Framework AI-first que estructura conocimiento, procesos y comportamiento de agentes de IA mediante una **taxonomía unificada** (Clade → Subclade → Pilar). Lexis, Codex, Katas, Warriors y Cries se organizan por disciplina y área, orientando cómo humanos e IA colaboran en cualquier dominio.

**Principios:** IA como copiloto (no piloto); proceso sobre herramienta; artefactos versionados como código; `framework/` como fuente de verdad, agnóstico de plataforma.

---

## Instalación

### Requisitos previos

- **Python 3.8+** — necesario para el instalador
- **Make** (opcional) — para bootstrap y actualizaciones
  - **Windows:** `choco install make` o `winget install GnuWin32.Make`
  - **macOS:** Xcode Command Line Tools (`xcode-select --install`)
  - **Linux:** incluido en la mayoría de distros (`sudo apt install make`)

### Plataformas

| Nombre | Descripción |
|--------|-------------|
| **Cursor** | IDE con soporte integrado: el instalador genera `.cursor/` (rules, skills, commands, agents) a partir del framework. [Soporte para Cursor](#soporte-para-cursor) |

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
```

```bash
# macOS / Linux — framework + Cursor
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/install.py | python3 - --platform cursor
```

**Opciones del instalador:**

| Flag | Descripción |
|------|-------------|
| `--platform cursor` | Generar `.cursor/` (rules, skills, commands, agents) |
| `--clades X,Y` | Instalar solo los clades indicados (ej.: `_foundation,documentation`) |
| `--version v0.1.0` | Versión específica (tag o rama) |
| `--language en` | Sobrescribir idioma por defecto en `.directives` |
| `--directives PATH` | Usar `.directives` personalizado (ruta local o URL) |
| `--target PATH` | Instalar en otro directorio |
| `--dry-run` | Simular sin realizar cambios |
| `--clean` | Eliminar archivos instalados por Ahrena |

Cuando se usa `--clades`, la selección se guarda en `.ahrena/.installed-clades` y es respetada por `update.py`.

### Actualización y desinstalación

| Acción | Makefile | Script directo |
|--------|----------|----------------|
| **Actualizar** | `make update` o `make update VERSION=v0.2.0` | `python .ahrena/update.py` |
| **Desinstalar** | `make uninstall` | `python .ahrena/uninstall.py` (u `--force` sin confirmación) |

**Desarrollo local (contribuidores):** `make dev-install PLATFORM=cursor` — usa los fuentes locales de `framework/` en lugar de descargar de GitHub.

### Qué se instala

| Comando | `.ahrena/` | `.cursor/` |
|---------|------------|------------|
| Sin `--platform` | framework, directives, scripts, Makefile | — |
| `--platform cursor` | idem | rules, skills, commands, agents |

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
| **engineering** | platform, backend, frontend, devops, security, quality | [Platform (Guardia)](framework/es/engineering/platform/README.md) |
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

Para la arquitectura del framework (paths, diagramas, correspondencia con `.cursor/`), consulte la [Guía del desarrollador](./framework/es/README.md#arquitectura-del-framework).

---

## Soporte para Cursor

Ahrena ofrece **soporte integrado para Cursor IDE**. Con `--platform cursor` (o `PLATFORM=cursor` en el Makefile), el instalador genera el directorio `.cursor/` a partir del `framework/`, de modo que Lexis, Codex, Katas, Warriors y Cries se utilicen directamente en el editor:

| Recurso Cursor | Origen en el framework |
|----------------|------------------------|
| **Rules** (`.mdc`) | Lexis y Codex — contexto inyectado en el agente |
| **Skills** (`SKILL.md`) | Katas y Warriors — capacidades bajo demanda |
| **Commands** (`.md`) | Cries — comandos rápidos vía `/cry-nombre` |
| **Agents** (`.md`) | Warriors — subagentes especializados |

Las reglas se aplican automáticamente según el alcance del proyecto; skills y commands están disponibles en el chat. Para instalar con Cursor, use `make bootstrap PLATFORM=cursor` o `python install.py --platform cursor`.
