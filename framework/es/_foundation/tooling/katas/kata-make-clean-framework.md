# Kata: Limpiar framework (Make clean)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Eliminación de los archivos instalados por Ahrena (sin confirmación) mediante el target `clean` del Makefile

## Objetivo

Eliminar **todos** los archivos instalados por Ahrena en el proyecto (`.ahrena/` y archivos de Ahrena en `.cursor/`), **sin pedir confirmación**. Equivalente al target `clean` del Makefile — o al comando equivalente en PowerShell/Python cuando `make` no esté disponible. Diferente de `uninstall`, que puede solicitar confirmación.

## Cuándo usar

- Cuando el usuario invoca `/cry-make clean` (con o sin variables, ej.: TARGET)
- Cuando sea necesario eliminar la instalación de Ahrena de forma no interactiva (ej.: scripts, CI)
- Cuando se desee "resetear" el proyecto respecto al framework sin interacción

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Variables | No | Ej.: `TARGET=.`. Consultar `codex-make` |

## Workflow

```
Progreso:
- [ ] 1. Consultar codex-make (equivalencia sin Make para clean)
- [ ] 2. Verificar .ahrena/install.py (usado para --clean)
- [ ] 3. Determinar terminal
- [ ] 4. Ejecutar clean (make o equivalente)
- [ ] 5. Reportar resultado
```

### Paso 1: Consultar codex-make

1. Leer `codex-make` (target `clean` y sección **Equivalencia sin Make**)
2. Identificar el comando: `make clean [variables]` o `python .ahrena/install.py --target . --clean`

### Paso 2: Verificar .ahrena/install.py

1. Para clean vía equivalente: el script `install.py` con `--clean` elimina los archivos; si `.ahrena/` ya fue eliminado, el comando puede fallar — en ese caso, informar que ya está limpio
2. Si `make` está disponible, el Makefile llama a `.ahrena/install.py --clean`; por tanto `.ahrena/install.py` debe existir antes del clean (o el Makefile está en la raíz del repo)

### Paso 3: Determinar terminal

1. Leer `.ahrena/.directives` (sección `terminal`) conforme `lex-terminal-type`; si falta, inferir del SO

### Paso 4: Ejecutar clean

1. Si `make` está disponible: ejecutar `make clean [variables]` en el directorio del proyecto
2. Si `make` no está disponible: ejecutar `python .ahrena/install.py --target <TARGET> --clean` conforme codex-make
3. Capturar salida y código de salida

### Paso 5: Reportar resultado

1. Presentar la salida al usuario; si falla, indicar error y sugerir corrección

## Salidas

| Salida | Formato |
|--------|---------|
| Éxito | Salida del comando clean (confirmación de eliminación) |
| Fallo | Mensaje de error y sugerencia de corrección |

## Referencias

- `codex-make` — Target clean y equivalencia sin Make
- `lex-terminal-type` — Tipo de terminal
- `cry-make` — Comando que puede invocar este Kata (target `clean`)
