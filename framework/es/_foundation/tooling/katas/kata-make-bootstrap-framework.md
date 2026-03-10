# Kata: Bootstrap del framework (Make bootstrap)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Primera instalación del framework Ahrena mediante el target `bootstrap` del Makefile

## Objetivo

Realizar la **primera instalación** del framework Ahrena: descargar el instalador desde GitHub y ejecutarlo con las variables deseadas (ej.: PLATFORM, TARGET, VERSION, REPO). Equivalente al target `bootstrap` del Makefile — o al comando equivalente en PowerShell cuando `make` no esté disponible.

## Cuándo usar

- Cuando el usuario invoca `/cry-make bootstrap` (con o sin variables)
- Cuando el proyecto aún no tiene `.ahrena/` y es la primera vez que se instala el framework

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Variables | No | Ej.: `PLATFORM=cursor`, `TARGET=.`, `VERSION=main`, `REPO=...`. Consultar `codex-make` |

## Workflow

```
Progreso:
- [ ] 1. Consultar codex-make (equivalencia sin Make para bootstrap)
- [ ] 2. Determinar terminal
- [ ] 3. Ejecutar bootstrap (make o equivalente)
- [ ] 4. Reportar resultado
```

### Paso 1: Consultar codex-make

1. Leer `codex-make` (target `bootstrap` y sección **Equivalencia sin Make** para bootstrap)
2. Identificar el comando: `make bootstrap [variables]` o el one-liner en PowerShell (descargar install.py, ejecutar, eliminar)

### Paso 2: Determinar terminal

1. Leer `.ahrena/.directives` (sección `terminal`) conforme `lex-terminal-type`; si falta, inferir del SO (en bootstrap puede no existir aún `.ahrena/`; inferir del SO)

### Paso 3: Ejecutar bootstrap

1. Si `make` está disponible: ejecutar `make bootstrap [variables]` en el directorio del proyecto
2. Si `make` no está disponible: ejecutar el comando de la sección "Equivalencia sin Make" de `codex-make` para bootstrap (descargar install.py de GitHub, ejecutar con variables, eliminar el script)
3. Capturar salida y código de salida

### Paso 4: Reportar resultado

1. Presentar la salida al usuario; si falla, indicar error y sugerir corrección

## Salidas

| Salida | Formato |
|--------|---------|
| Éxito | Salida del comando de bootstrap |
| Fallo | Mensaje de error y sugerencia de corrección |

## Referencias

- `codex-make` — Target bootstrap y equivalencia sin Make
- `lex-terminal-type` — Tipo de terminal
- `cry-make` — Comando que puede invocar este Kata (target `bootstrap`)
