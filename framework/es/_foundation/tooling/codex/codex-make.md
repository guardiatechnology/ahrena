# Codex: Makefile del repositorio Ahrena

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Variables, targets y equivalencia sin Make del Makefile en la raíz del repositorio Ahrena

## Visión general

Este Codex es la referencia para ejecutar targets del **Makefile** en la raíz del repositorio Ahrena. Define las variables disponibles, los targets, ejemplos de uso y la **equivalencia sin Make** (comandos PowerShell/Python) para cuando `make` no está disponible (ej.: Windows). Es consultado por los katas especializados de make (install, update, dev-install, bootstrap, sync-cursor, uninstall, clean) y por el agente al atender `/cry-make`.

## Contexto

- **Dominio:** Instalación, actualización, bootstrap y mantenimiento del framework Ahrena mediante Makefile o scripts equivalentes.
- **Público objetivo:** Agentes de IA que ejecutan `/cry-make` o el Kata asociado; desarrolladores que ejecutan `make` o los scripts en PowerShell.
- **Actualización:** Cuando se añadan nuevos targets o variables al Makefile o cuando cambie la equivalencia sin Make.

## Contenido

### Variables

| Variable | Descripción |
|----------|-------------|
| `PLATFORM` | Plataforma objetivo (ej.: `cursor`) |
| `TARGET` | Directorio del proyecto (default: `.`) |
| `VERSION` | Tag o rama para instalación/actualización remota (default: `main`) |
| `REPO` | URL del repositorio en GitHub |
| `SOURCE` | Ruta al clone local de Ahrena (instalar/actualizar desde local) |
| `LOCAL` | Si se define (ej.: `LOCAL=1`), instalar/actualizar desde el directorio actual como fuente |
| `LANGUAGE` | Sobrescribir idioma por defecto en `.directives` |
| `DIRECTIVES` | Ruta o URL al archivo `.directives` personalizado |
| `CLADES` | Clades separados por coma (default: todos) |

**Por defecto:** la instalación y la actualización son siempre desde **remoto** (GitHub). Para usar fuente local, use `SOURCE=/ruta/ahrena` o `LOCAL=1`.

### Targets disponibles

| Target | Descripción |
|--------|-------------|
| `bootstrap` | Primera instalación (descarga el instalador desde GitHub) |
| `install` | Instala el framework (por defecto: remoto). Con `LOCAL=1` o `SOURCE=...`: local |
| `dev-install` | Instala desde el directorio actual (ejecutar en la raíz del repo Ahrena) |
| `update` | Actualiza la instalación (por defecto: remoto). Tras dev-install use `update LOCAL=1` o `SOURCE=...` para traer lo más reciente del entorno de desarrollo |
| `sync-cursor` | Regenera `.cursor/` desde `.ahrena/framework/` y `.ahrena/artifacts/` (sin descarga) |
| `uninstall` | Elimina la instalación del framework |
| `clean` | Elimina archivos instalados por Ahrena (sin confirmación) |

### Ejemplos de uso

```powershell
# Instalación remota (por defecto)
make install PLATFORM=cursor
make install PLATFORM=cursor VERSION=1.0.0

# Instalación desde clone local
make install PLATFORM=cursor SOURCE=../ahrena
make install PLATFORM=cursor LOCAL=1

# Bootstrap del entorno
make bootstrap

# Actualización remota (por defecto)
make update

# Actualización desde local (ej.: tras dev-install)
make update LOCAL=1
make update SOURCE=../ahrena

# Limpiar artefactos
make clean
```

### Instalación guiada por preferencias

En la primera instalación, `scripts/install.py` materializa el `.directives` a partir de una selección de preferencias. Cuando stdin es TTY y no se pasa `--non-interactive`, el instalador pregunta al usuario qué MCPs, hooks y features opcionales activar (pre-marcado = perfil Full). Para ejecuciones no interactivas (CI, scripts), elija un perfil y ajuste:

```powershell
# Conocer el catálogo (MCPs, hooks, features opcionales)
python scripts/install.py --list-catalog

# Default Full (sin flag, sin prompt): todos los MCPs, todos los hooks, todas las features
python scripts/install.py --self --target . --platform claude-code --non-interactive

# Perfil minimal (solo MCP ahrena + hook rtk)
python scripts/install.py --self --target . --platform claude-code --non-interactive --profile=minimal

# Full menos MCPs específicos
python scripts/install.py --self --target . --platform claude-code --non-interactive --profile=full --without-mcp=notion,figma
```

Orden de resolución: `--with-*` / `--without-*` explícitos sobrescriben `--profile`, que sobrescribe el default Full. El MCP `ahrena` siempre se mantiene (servidor del propio framework). Los archivos `.directives` existentes se preservan en reinstalaciones.

### Equivalencia sin Make (Windows)

Cuando `make` no está disponible (ej.: PowerShell en Windows), use los scripts directamente:

**Instalación remota:**
```powershell
python .ahrena/install.py --target . --version main --repo https://github.com/guardiatechnology/ahrena --platform cursor
```

**Instalación local (en el repo Ahrena):**
```powershell
python scripts/install.py --local --target . --platform cursor
```

**Instalación local (ruta):**
```powershell
python .ahrena/install.py --target . --source C:\ruta\a\ahrena --platform cursor
```

**Actualización remota (por defecto):**
```powershell
python .ahrena/update.py --target .
```

**Actualización local:**
```powershell
python .ahrena/update.py --target . --local
# o
python .ahrena/update.py --target . --source C:\ruta\a\ahrena
```

**Bootstrap (primera instalación):** descargar el instalador desde GitHub y ejecutarlo; en PowerShell, por ejemplo:
```powershell
Invoke-WebRequest https://github.com/guardiatechnology/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py --platform cursor; Remove-Item install.py
```

**Sync-cursor (regenerar .cursor/):**
```powershell
python .ahrena/update.py --target . --sync-cursor
```

**Uninstall (eliminar instalación):**
```powershell
python .ahrena/uninstall.py --target .
```

**Clean (eliminar archivos sin confirmación):**
```powershell
python .ahrena/install.py --target . --clean
```

## Referencias

- `Makefile` — Archivo de automatización en la raíz del repositorio
- Katas de make (`kata-make-install-framework`, `kata-make-update-framework`, etc.) — Procedimientos por target (consultan este Codex)
- `lex-terminal-type` — Tipo de terminal definido en `.ahrena/.directives`
- [GNU Make Manual](https://www.gnu.org/software/make/manual/)
