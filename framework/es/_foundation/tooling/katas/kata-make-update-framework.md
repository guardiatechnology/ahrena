# Kata: Actualizar framework (Make update)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Actualización de la instalación del framework Ahrena mediante el target `update` del Makefile

## Objetivo

Actualizar la instalación del framework Ahrena en el proyecto (remoto o local), ejecutando el target `update` del Makefile — o el comando equivalente en PowerShell/Python cuando `make` no esté disponible. Soporta variables TARGET, SOURCE, LOCAL, VERSION, REPO (ver `codex-make`).

## Cuándo usar

- Cuando el usuario invoca `/cry-make update` (con o sin variables)
- Cuando sea necesario traer la versión más reciente del framework (remoto o desde el entorno de desarrollo local)

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Variables | No | Ej.: `TARGET=.`, `SOURCE=../ahrena`, `LOCAL=1`, `VERSION=main`, `REPO=...`. Consultar `codex-make` para la lista completa |

## Workflow

```
Progreso:
- [ ] 1. Consultar codex-make (variables y equivalencia sin Make para update)
- [ ] 2. Verificar .ahrena/update.py
- [ ] 3. Determinar terminal
- [ ] 4. Ejecutar update (make o equivalente)
- [ ] 5. Reportar resultado
```

### Paso 1: Consultar codex-make

1. Leer `codex-make` (variables y sección **Equivalencia sin Make**) para el target `update`
2. Identificar el comando a ejecutar según las variables (remoto vs LOCAL/SOURCE)

### Paso 2: Verificar .ahrena/update.py

1. Verificar que el proyecto tiene `.ahrena/update.py` (instalación previa de Ahrena)
2. Si no existe, informar que es necesario instalar antes (`/cry-make install` o equivalente)

### Paso 3: Determinar terminal

1. Leer `.ahrena/.directives` (sección `terminal`) conforme `lex-terminal-type`; si falta, inferir del SO
2. Usar el tipo para el comando equivalente (PowerShell en Windows, conforme codex-make)

### Paso 4: Ejecutar update

1. Si `make` está disponible: ejecutar `make update [variables]` en el directorio del proyecto (o conforme TARGET)
2. Si `make` no está disponible: ejecutar el comando de la sección "Equivalencia sin Make" de `codex-make` para actualización remota o local
3. Capturar salida y código de salida

### Paso 5: Reportar resultado

1. Presentar la salida al usuario; si falla, indicar error y sugerir corrección

## Salidas

| Salida | Formato |
|--------|---------|
| Éxito | Salida del comando de actualización |
| Fallo | Mensaje de error y sugerencia de corrección |

## Referencias

- `codex-make` — Variables y equivalencia sin Make para `update`
- `lex-terminal-type` — Tipo de terminal
- `cry-make` — Comando que puede invocar este Kata (target `update`)
