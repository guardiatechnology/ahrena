# Getting Started

Ahrena es un **framework de capacidades AI-first** — una colección de Lexis (leyes), Codex (guías), Katas (skills) y Warriors (agentes) que transforma cualquier IDE con soporte para AI en un entorno de ingeniería estandarizado y auditable.

Instalar Ahrena en un proyecto significa que todos los agentes de AI que operan en él comparten las mismas reglas, el mismo vocabulario y los mismos flujos de trabajo.

---

## Requisitos previos

| Requisito | Versión mínima |
|---|---|
| Python | 3.9+ |
| make | cualquier versión moderna |
| IDE con soporte para AI | Cursor o Claude Code |

=== "macOS / Linux"

    ```bash
    python3 --version
    make --version
    ```

=== "Windows"

    ```powershell
    python --version
    # make via chocolatey o winget
    winget install GnuWin32.Make
    ```

---

## Instalación

### Bootstrap (primer uso)

El comando `bootstrap` descarga el instalador directamente desde la última release de GitHub y ejecuta la instalación en el proyecto actual.

=== "macOS / Linux"

    ```bash
    make bootstrap
    ```

=== "Windows"

    ```powershell
    make bootstrap
    ```

Esto crea la carpeta `.ahrena/` en la raíz del proyecto con el framework instalado y genera los archivos de configuración para la plataforma detectada (Cursor o Claude Code).

### Plataforma explícita

Por defecto, el instalador detecta automáticamente qué IDE está presente. Para forzar una plataforma:

```bash
# Cursor
make bootstrap PLATFORM=cursor

# Claude Code
make bootstrap PLATFORM=claude-code
```

### Idioma

El idioma predeterminado es `pt-BR`. Para instalar en otro idioma:

```bash
make bootstrap LANGUAGE=en
make bootstrap LANGUAGE=es
```

### Clades selectivos

Para instalar solo los clades relevantes al proyecto (reduce el ruido de reglas irrelevantes):

```bash
# Solo backend y platform
make bootstrap CLADES=engineering/backend,engineering/platform

# Solo workflow y contributing
make bootstrap CLADES=_foundation/contributing,engineering/workflow
```

---

## Actualización

Después del bootstrap inicial, se debe usar `update` para obtener la versión más reciente del framework:

```bash
make update
```

Para actualizar a una versión específica:

```bash
make update VERSION=v1.2.0
```

---

## Sincronización

Si ya se tiene Ahrena instalado y solo se necesita regenerar los archivos de configuración del IDE (sin descargar nada):

```bash
# Regenera .cursor/
make sync-cursor

# Regenera .claude/ y CLAUDE.md
make sync-claude-code
```

Útil después de editar manualmente los directives o después de un `git pull` que trajo cambios en el framework.

---

## Eliminación

```bash
# Con confirmación interactiva
make uninstall

# Sin confirmación (CI, scripts)
make clean
```

---

## Modo Dev

El modo dev es para quienes desean **contribuir con el propio Ahrena** — probar cambios locales en el framework antes de enviar un PR.

### Por qué existe

`make bootstrap` y `make install` siempre descargan el framework desde GitHub. `make dev-install` ignora la red y usa el código local del repositorio como fuente — permite iterar sin hacer commit/push.

### Configuración

Se debe clonar el repositorio de Ahrena y, dentro de él, ejecutar:

```bash
# Instala el framework desde el código local en el proyecto actual
make dev-install
```

Para instalar en otro proyecto desde esta copia local:

```bash
make install-to TARGET=/ruta/al/proyecto
```

### Flujo de trabajo típico de contribución

```
1. fork + clone de guardiafinance/ahrena
2. crear la branch: feat/{issue}-{slug}
3. editar los artefactos en framework/
4. make dev-install           ← instala localmente para probar
5. probar en los IDEs configurados
6. make validate              ← valida estructura y cobertura
7. commit (GPG-signed, Conventional Commits)
8. /cry-new-pr                ← abre el PR siguiendo los estándares
```

### Variables disponibles en dev

```bash
make dev-install PLATFORM=cursor LANGUAGE=en CLADES=engineering/backend
make dev-install TARGET=../mi-otro-proyecto
```

---

## Referencia de comandos

| Comando | Qué hace |
|---|---|
| `make bootstrap` | Primera instalación (descarga el instalador desde GitHub) |
| `make install` | Reinstala desde `.ahrena/install.py` |
| `make dev-install` | Instala desde el código local (modo dev) |
| `make install-to TARGET=…` | Instala este repo en otro proyecto (offline) |
| `make update` | Actualiza a la versión más reciente |
| `make sync-cursor` | Regenera `.cursor/` sin descargar nada |
| `make sync-claude-code` | Regenera `.claude/` y `CLAUDE.md` |
| `make validate` | Valida estructura y consistencia del framework |
| `make uninstall` | Elimina Ahrena con confirmación |
| `make clean` | Elimina los archivos instalados sin confirmación |

---

## Próximos pasos

- [Conceptos fundamentales](ahrena/concepts.md) — entender Lexis, Codex, Katas, Warriors y Cries
- [Catálogo de Cries](ahrena/cries.md) — todos los comandos disponibles en los IDEs
- [Catálogo de Katas](ahrena/katas.md) — todas las skills ejecutables
- [Contribuir](https://github.com/guardiafinance/ahrena/blob/main/CONTRIBUTING.md) — cómo contribuir con el framework
