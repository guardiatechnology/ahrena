# Kata: Instalar framework desde desarrollo (Make dev-install)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Instalación del framework Ahrena desde el directorio actual (raíz del repo), target `dev-install`

## Objetivo

Instalar el framework Ahrena desde el **directorio actual** (que debe ser la raíz del repositorio Ahrena), ejecutando el target `dev-install` del Makefile — o el equivalente en PowerShell/Python cuando `make` no esté disponible. Usado por contribuidores que desarrollan el framework y quieren instalar en otro proyecto usando los fuentes locales.

## Cuándo usar

- Cuando el usuario invoca `/cry-make dev-install` (con o sin variables, ej.: PLATFORM, TARGET)
- Cuando sea necesario instalar el framework desde el clone local de desarrollo (sin descargar de GitHub)

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Variables | No | Ej.: `PLATFORM=cursor`, `TARGET=../otro-proyecto`. Consultar `codex-make` |

## Workflow

```
Progreso:
- [ ] 1. Consultar codex-make (equivalencia sin Make para dev-install)
- [ ] 2. Verificar que está en la raíz del repo Ahrena (framework/, scripts/)
- [ ] 3. Determinar terminal
- [ ] 4. Ejecutar dev-install (make o equivalente)
- [ ] 5. Reportar resultado
```

### Paso 1: Consultar codex-make

1. Leer `codex-make` (target `dev-install` y sección **Equivalencia sin Make** para instalación local en el repo Ahrena)
2. Identificar el comando: `make dev-install [variables]` o `python scripts/install.py --local --target . [--platform cursor]` etc.

### Paso 2: Verificar raíz del repo Ahrena

1. Confirmar que existen `framework/` y `scripts/install.py` en el directorio actual (o en el directorio de trabajo)
2. Si no existen, informar que dev-install debe ejecutarse en la raíz del repositorio Ahrena

### Paso 3: Determinar terminal

1. Leer `.ahrena/.directives` (sección `terminal`) conforme `lex-terminal-type`; si falta, inferir del SO

### Paso 4: Ejecutar dev-install

1. Si `make` está disponible: ejecutar `make dev-install [variables]` en la raíz del repo Ahrena
2. Si `make` no está disponible: ejecutar `python scripts/install.py --local --target <TARGET> [--platform cursor]` conforme codex-make (sin --repo/--version)
3. Capturar salida y código de salida

### Paso 5: Reportar resultado

1. Presentar la salida al usuario; si falla, indicar error y sugerir corrección

## Salidas

| Salida | Formato |
|--------|---------|
| Éxito | Salida del comando dev-install |
| Fallo | Mensaje de error y sugerencia de corrección |

## Referencias

- `codex-make` — Target dev-install y equivalencia sin Make
- `lex-terminal-type` — Tipo de terminal
- `cry-make` — Comando que puede invocar este Kata (target `dev-install`)
