# Kata: Sincronizar .cursor/ (Make sync-cursor)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Regenerar `.cursor/` desde `.ahrena/framework/` y `.ahrena/artifacts/` mediante el target `sync-cursor`

## Objetivo

Regenerar el directorio `.cursor/` (rules, skills, commands, agents) desde `.ahrena/framework/` y `.ahrena/artifacts/`, **sin descargar** nada del remoto. Equivalente al target `sync-cursor` del Makefile — o al comando equivalente en PowerShell/Python cuando `make` no esté disponible.

## Cuándo usar

- Cuando el usuario invoca `/cry-make sync-cursor` (con o sin variables, ej.: TARGET)
- Cuando se modificó el contenido de `.ahrena/framework/` o `.ahrena/artifacts/` y es necesario reflejarlo en `.cursor/`
- Tras crear o editar artefactos en el proyecto que deben aparecer en Cursor

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Variables | No | Ej.: `TARGET=.`. Consultar `codex-make` |

## Workflow

```
Progreso:
- [ ] 1. Consultar codex-make (equivalencia sin Make para sync-cursor)
- [ ] 2. Verificar .ahrena/update.py y .ahrena/.directives
- [ ] 3. Determinar terminal
- [ ] 4. Ejecutar sync-cursor (make o equivalente)
- [ ] 5. Reportar resultado
```

### Paso 1: Consultar codex-make

1. Leer `codex-make` (target `sync-cursor` y sección **Equivalencia sin Make**)
2. Identificar el comando: `make sync-cursor [variables]` o `python .ahrena/update.py --target . --sync-cursor`

### Paso 2: Verificar .ahrena/update.py y .ahrena/.directives

1. Verificar que el proyecto tiene `.ahrena/update.py` y `.ahrena/.directives` (instalación previa de Ahrena)
2. Si no existen, informar que es necesario instalar antes (`/cry-make install` o bootstrap)

### Paso 3: Determinar terminal

1. Leer `.ahrena/.directives` (sección `terminal`) conforme `lex-terminal-type`; si falta, inferir del SO

### Paso 4: Ejecutar sync-cursor

1. Si `make` está disponible: ejecutar `make sync-cursor [variables]` en el directorio del proyecto
2. Si `make` no está disponible: ejecutar `python .ahrena/update.py --target <TARGET> --sync-cursor` conforme codex-make
3. Capturar salida y código de salida

### Paso 5: Reportar resultado

1. Presentar la salida al usuario; si falla, indicar error y sugerir corrección

## Salidas

| Salida | Formato |
|--------|---------|
| Éxito | Salida del comando sync-cursor |
| Fallo | Mensaje de error y sugerencia de corrección |

## Referencias

- `codex-make` — Target sync-cursor y equivalencia sin Make
- `lex-terminal-type` — Tipo de terminal
- `cry-make` — Comando que puede invocar este Kata (target `sync-cursor`)
