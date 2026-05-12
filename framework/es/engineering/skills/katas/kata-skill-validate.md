# Kata: Validar Proyecto de Skill

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Validación determinística de un proyecto de skill en `{paths.skills_root}/{slug}/` contra `lex-skill-project-structure` y los requisitos de frontmatter de `codex-skill-anthropic-agent-skills`

## Objetivo

Ejecutar una verificación determinística del proyecto de skill que rechace, antes del commit, cualquier divergencia respecto a `lex-skill-project-structure` y al frontmatter mínimo de `SKILL.md`. El resultado es una lista estructurada de violaciones (regla, severidad, archivo, mensaje) consumible por humano (texto) o por agente (JSON). Este kata **no** modifica archivos — solo reporta.

## Cuándo Usar

- Inmediatamente después de `cry-new-skill` / `kata-init-skill`, antes de la primera autoría sustantiva
- Al concluir `kata-skill-implement`, antes de invocar `kata-skill-package`
- En un pre-commit hook del repositorio que aloja skills
- Cuando `warrior-claudionor` debe decidir si una skill está lista para empaquetado

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `skill_path` | Sí | Ruta del directorio raíz del proyecto (`{paths.skills_root}/{slug}/`); idéntica al nombre del directorio (slug) |
| `format` | No | `text` (por defecto, humano) o `json` (consumible por agente) |

## Workflow

```
Progreso:
- [ ] 1. Resolver la ruta y confirmar la existencia
- [ ] 2. Invocar scripts/skills/validate.py
- [ ] 3. Recolectar violaciones (regla, severidad, archivo, mensaje)
- [ ] 4. Clasificar el resultado (ok / con warnings / con errores)
- [ ] 5. Reportar al llamador
```

### Paso 1: Resolver la ruta y confirmar la existencia

1. Aceptar la ruta como argumento absoluto o relativo a la raíz del repositorio
2. Verificar que `skill_path` existe y es un directorio; en caso contrario reportar `lex-skill-project-structure#location` y detener

### Paso 2: Invocar `scripts/skills/validate.py`

1. Ejecutar `python3 scripts/skills/validate.py <skill_path> --format json`
2. Capturar stdout y exit code
3. No filtrar la salida — el validador es la fuente de la verdad; el kata solo orquesta

El validador cubre, en una sola pasada:

| Regla | Severidad | Verificación |
|-------|:---------:|--------------|
| `lex-skill-project-structure#slug-regex` | error | El nombre del directorio cumple el regex de Anthropic |
| `lex-skill-project-structure#slug-reserved` | error | El slug no contiene `anthropic` ni `claude` |
| `lex-skill-project-structure#required-files` | error | `SKILL.md` y `skill.config.json` están presentes |
| `lex-skill-project-structure#frontmatter` | error | `SKILL.md` tiene un bloque YAML `---` |
| `lex-skill-project-structure#frontmatter-name` | error | El frontmatter tiene `name` no-vacío |
| `lex-skill-project-structure#name-matches-slug` | error | El `name` del frontmatter es igual al nombre del directorio |
| `codex-skill-anthropic-agent-skills#description` | error | `description` presente |
| `codex-skill-anthropic-agent-skills#description-length` | error | `description` en `[1, 1024]` chars |
| `lex-semantic-version` | error | `metadata.version` es SemVer (cuando se declara) |
| `lex-skill-project-structure#cross-references` | error | Los enlaces relativos en `SKILL.md` resuelven dentro del proyecto |
| `lex-skill-project-structure#optional-subdirs` | warning | Subdirectorios fuera de la allow-list (`references/`, `scripts/`, `tools/`, `widgets/`, `assets/`) |

### Paso 3: Recolectar violaciones

1. Cada ítem de la salida JSON tiene la forma `{rule, severity, file, message}`
2. Separar errores (severidad `error`) de warnings (severidad `warning`)
3. No inferir nada más allá de lo reportado — el kata es "thin": la lógica de la regla pertenece al validador

### Paso 4: Clasificar el resultado

| Resultado | Criterio |
|-----------|----------|
| ✅ `ok` | cero violaciones |
| ⚠️ `ok-with-warnings` | solo warnings |
| ❌ `failed` | una o más violaciones de severidad `error` |

`warrior-claudionor` solo avanza a `kata-skill-package` cuando el resultado es `ok` u `ok-with-warnings` (los warnings no bloquean el empaquetado pero deben reportarse).

### Paso 5: Reportar al llamador

1. **Formato `text` (por defecto):** imprimir el reporte legible por humanos (encabezado + una línea por violación)
2. **Formato `json`:** retornar el array de violaciones tal cual, sin encapsulamiento, para consumo programático
3. En cualquier formato, retornar exit code `0` cuando todos los ítems sean `warning`, `1` cuando haya al menos un `error`

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Reporte humano | Texto multilínea | `stdout` |
| Reporte para agente | JSON `[{rule, severity, file, message}, ...]` | `stdout` |
| Exit code | `0` (ok o warnings) / `1` (errores) | shell |

## Ejemplo de Ejecución

### Input

```
kata-skill-validate skills/scheduled-payments-skill --format text
```

### Salida (éxito)

```
✅ no violations
```

### Salida (con errores)

```
❌ 2 violation(s):
  [error] lex-skill-project-structure#name-matches-slug
      file:    skills/scheduled-payments-skill/SKILL.md
      message: frontmatter name 'scheduled-payments' does not match directory slug 'scheduled-payments-skill'
  [error] lex-skill-project-structure#cross-references
      file:    skills/scheduled-payments-skill/SKILL.md
      message: reference 'references/missing.md' does not exist at ...
```

## Restricciones

- El kata **no modifica** archivos — solo reporta violaciones
- El kata **no interpreta** el resultado más allá de lo que el validador retorna; las reglas nuevas nacen en la Lex y descienden al script, nunca al revés
- El kata invoca el validador como subproceso para preservar aislamiento (el drift del intérprete Python de la sesión no afecta el resultado)
- Todos los mensajes en pt-BR, es o en según `language.default`; los identificadores técnicos (rutas, nombres de regla) se preservan

## Referencias

- `scripts/skills/validate.py` — implementación determinística invocada
- `lex-skill-project-structure` — ley verificada
- `codex-skill-anthropic-agent-skills` — reglas de frontmatter
- `lex-semantic-version` — formato de `metadata.version`
- `warrior-claudionor` — orquestador que invoca este kata
- `cry-skill` — atajo `--mode validate`
- `kata-skill-package` — sucesor invocado tras que validate retorne `ok`
