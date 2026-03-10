# Kata: Instalar framework (Make install)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Instalación del framework Ahrena mediante el target `install` del Makefile

## Objetivo

Instalar el framework Ahrena en el proyecto (remoto o local), ejecutando el target `install` del Makefile — o el comando equivalente en PowerShell/Python cuando `make` no esté disponible. Soporta variables PLATFORM, TARGET, SOURCE, LOCAL, VERSION, REPO y demás (ver `codex-make`).

## Cuándo usar

- Cuando el usuario invoca `/cry-make install` (con o sin variables)
- Cuando sea necesario instalar el framework por primera vez o reinstalar (remoto o desde clone local)

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Variables | No | Ej.: `PLATFORM=cursor`, `TARGET=.`, `SOURCE=../ahrena`, `LOCAL=1`, `VERSION=main`, `REPO=...`. Consultar `codex-make` para la lista completa |

## Workflow

```
Progreso:
- [ ] 1. Consultar codex-make (variables y equivalencia sin Make para install)
- [ ] 2. Verificar Makefile o .ahrena/install.py
- [ ] 3. Determinar terminal
- [ ] 4. Ejecutar install (make o equivalente)
- [ ] 5. Reportar resultado
```

### Paso 1: Consultar codex-make

1. Leer `codex-make` (variables y sección **Equivalencia sin Make**) para el target `install`
2. Identificar el comando a ejecutar según las variables pasadas (remoto vs LOCAL/SOURCE)

### Paso 2: Verificar Makefile o .ahrena/install.py

1. Si en la raíz del repo Ahrena: verificar que existen `Makefile` y `scripts/install.py`
2. Si en proyecto que ya tiene Ahrena: verificar que existe `.ahrena/install.py` (o que existe `Makefile` en la raíz del repo para dev-install)
3. Si falta algo, informar al usuario y sugerir corrección

### Paso 3: Determinar terminal

1. Leer `.ahrena/.directives` (sección `terminal`) conforme `lex-terminal-type`; si falta, inferir del SO
2. Usar el tipo para elegir la sintaxis del comando equivalente (PowerShell en Windows, conforme codex-make)

### Paso 4: Ejecutar install

1. Si `make` está disponible: ejecutar `make install [variables]` en el directorio correcto (raíz del repo o conforme TARGET)
2. Si `make` no está disponible: ejecutar el comando de la sección "Equivalencia sin Make" de `codex-make` para instalación remota, local (en el repo) o local (ruta), según variables
3. Capturar salida y código de salida

### Paso 5: Reportar resultado

1. Presentar la salida al usuario; si falla, indicar error y sugerir corrección (ej.: equivalencia sin Make, verificación de ruta)

## Salidas

| Salida | Formato |
|--------|---------|
| Éxito | Salida del comando de instalación |
| Fallo | Mensaje de error y sugerencia de corrección |

## Referencias

- `codex-make` — Variables y equivalencia sin Make para `install`
- `lex-terminal-type` — Tipo de terminal
- `cry-make` — Comando que puede invocar este Kata (target `install`)
