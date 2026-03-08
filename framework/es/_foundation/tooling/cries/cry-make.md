# Cry: Ejecutar Makefile

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Ejecución de targets del Makefile del repositorio Ahrena

## Invocación

```
/cry-make <target> [variables]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `target` | Sí | Target del Makefile a ejecutar | `install`, `bootstrap`, `clean` |
| `variables` | No | Variables de entorno para make | `PLATFORM=cursor VERSION=1.0.0` |

## Targets Disponibles

| Target | Descripción |
|--------|-------------|
| `bootstrap` | Configura el entorno de desarrollo |
| `install` | Instala el framework en la plataforma especificada |
| `update` | Actualiza una instalación existente |
| `uninstall` | Elimina la instalación del framework |
| `clean` | Limpia artefactos temporales |

## Ejemplos de Uso

```
# Instalar para Cursor
/cry-make install PLATFORM=cursor

# Bootstrap del entorno
/cry-make bootstrap

# Limpiar artefactos
/cry-make clean

# Instalar versión específica
/cry-make install PLATFORM=cursor VERSION=1.0.0
```

## Comportamiento

1. Verifica que el `Makefile` existe en la raíz del repositorio
2. Valida que el target solicitado existe
3. Ejecuta `make <target> [variables]`
4. Reporta la salida del comando al usuario
5. Si el comando falla, presenta el error y sugiere corrección

## Nota

Este Cry es **específico del repositorio Ahrena** — no es un artefacto genérico del framework. Existe para facilitar la ejecución de tareas de desarrollo y mantenimiento dentro del propio proyecto del Ahrena.

## Referencias

- `Makefile` — Archivo de automatización en la raíz del repositorio
- [GNU Make Manual](https://www.gnu.org/software/make/manual/)
