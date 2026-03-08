# Tooling — Automatización y Herramientas

> Documentación de las herramientas de automatización del repositorio Ahrena.

## Visión General

El Subclade `tooling` contiene artefactos que automatizan tareas de desarrollo y mantenimiento del framework. Son herramientas específicas del repositorio Ahrena (no genéricas del framework) que facilitan instalación, build y operaciones del día a día.

## Inventario de Artefactos

### Cries (atajos)

| Artefacto | Descripción |
|-----------|-------------|
| `cry-make` | Ejecuta targets del Makefile del repositorio |

## Cómo Usar

### Ejecutar el Makefile

```
/cry-make <target> [variables]
```

Ejemplos:

```
/cry-make dev-install PLATFORM=cursor    # Instala usando fuentes locales
/cry-make bootstrap PLATFORM=cursor      # Primera instalación
/cry-make clean                          # Limpia artefactos temporales
```

### Targets Disponibles

| Target | Descripción |
|--------|-------------|
| `dev-install` | Instala usando fuentes locales (`framework/`) |
| `bootstrap` | Primera instalación (descarga de GitHub) |
| `install` | Reinstala a partir de `.ahrena/install.py` |
| `update` | Actualiza a la última versión |
| `uninstall` | Elimina la instalación del framework |
| `clean` | Elimina artefactos temporales |

## Referencias

- `Makefile` — Archivo de automatización en la raíz del repositorio
- `scripts/install.py` — Script de instalación del framework
