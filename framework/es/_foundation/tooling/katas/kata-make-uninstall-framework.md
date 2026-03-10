# Kata: Desinstalar framework (Make uninstall)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Eliminación de la instalación del framework Ahrena mediante el target `uninstall` del Makefile

## Objetivo

Eliminar la instalación del framework Ahrena del proyecto, con confirmación del usuario (salvo uso de flag de fuerza). Equivalente al target `uninstall` del Makefile — o al comando equivalente en PowerShell/Python cuando `make` no esté disponible.

## Cuándo usar

- Cuando el usuario invoca `/cry-make uninstall` (con o sin variables, ej.: TARGET)
- Cuando sea necesario desinstalar Ahrena del proyecto (elimina `.ahrena/` y archivos de Ahrena en `.cursor/`)

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Variables | No | Ej.: `TARGET=.`. Consultar `codex-make` |

## Workflow

```
Progreso:
- [ ] 1. Consultar codex-make (equivalencia sin Make para uninstall)
- [ ] 2. Verificar .ahrena/uninstall.py
- [ ] 3. Determinar terminal
- [ ] 4. Ejecutar uninstall (make o equivalente)
- [ ] 5. Reportar resultado
```

### Paso 1: Consultar codex-make

1. Leer `codex-make` (target `uninstall` y sección **Equivalencia sin Make**)
2. Identificar el comando: `make uninstall [variables]` o `python .ahrena/uninstall.py --target .` (y opcionalmente `--force` para omitir confirmación)

### Paso 2: Verificar .ahrena/uninstall.py

1. Verificar que el proyecto tiene `.ahrena/uninstall.py`
2. Si no existe, informar que Ahrena puede estar ya eliminado o que la instalación está incompleta

### Paso 3: Determinar terminal

1. Leer `.ahrena/.directives` (sección `terminal`) conforme `lex-terminal-type`; si falta, inferir del SO

### Paso 4: Ejecutar uninstall

1. Si `make` está disponible: ejecutar `make uninstall [variables]` en el directorio del proyecto
2. Si `make` no está disponible: ejecutar `python .ahrena/uninstall.py --target <TARGET>` conforme codex-make (el script puede pedir confirmación)
3. Capturar salida y código de salida

### Paso 5: Reportar resultado

1. Presentar la salida al usuario; si falla, indicar error y sugerir corrección

## Salidas

| Salida | Formato |
|--------|---------|
| Éxito | Salida del comando uninstall (confirmación de eliminación) |
| Fallo | Mensaje de error y sugerencia de corrección |

## Referencias

- `codex-make` — Target uninstall y equivalencia sin Make
- `lex-terminal-type` — Tipo de terminal
- `cry-make` — Comando que puede invocar este Kata (target `uninstall`)
