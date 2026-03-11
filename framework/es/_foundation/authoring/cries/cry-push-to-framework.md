# Cry: Push al Framework

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Incorporación de artefactos de proyecto al framework

## Descripción

Comando rápido para incorporar al framework canónico los artefactos creados en el espacio del proyecto (`.ahrena/artifacts/`). Invoca `kata-push-to-framework` en modo **--local** (copia a `framework/` en el repo actual) o **--remote** (sincronización con el repositorio del framework en GitHub vía MCP de GitHub). Garantiza traducciones en los idiomas obligatorios y opcionalmente elimina las copias del proyecto.

## Uso

```
/cry-push-to-framework [objetivo] [--local | --remote] [--remove]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `objetivo` | No | Ruta(s) en `.ahrena/artifacts/` o "todos". Si se omite, procesa todos los artefactos encontrados | `pt-BR/engineering/quality/lexis/lex-foo.md` o `todos` |
| `--local` | No | Incorporar al `framework/` del repositorio actual (copia en disco + i18n). | `--local` |
| `--remote` | No | Incorporar al repositorio del framework en GitHub usando **obligatoriamente el MCP de GitHub** (branch, push, apertura de PR). | `--remote` |
| `--remove` | No | Si está presente, elimina los artefactos de `.ahrena/artifacts/` tras copiar al framework (local) o tras envío correcto (remote) | `--remove` |

## Qué Hace el Comando

1. Determina el modo (local o remoto) a partir de los parámetros `--local` o `--remote`
2. Lee `.ahrena/.directives` para obtener `paths.project_artifacts`, `paths.framework` y `language.i18n`
3. Identifica los artefactos en `.ahrena/artifacts/` (todos o los indicados)
4. Ejecuta `kata-push-to-framework` con el modo y los parámetros proporcionados
5. En modo local: copia los artefactos a `framework/` y genera traducciones faltantes; en modo remote: envía al repositorio del framework vía MCP de GitHub (branch, push, PR)
6. Opcionalmente elimina los archivos del proyecto
7. Reporta los archivos incorporados (y en modo remote, enlace del PR)

## Plantilla de Prompt

```
Contexto:
- Modo: {{--local}} o {{--remote}}
- Objetivo: {{objetivo}} (o todos los artefactos en .ahrena/artifacts/)
- Eliminar del proyecto tras Push: {{--remove}}

Tarea:
Ejecute kata-push-to-framework en el modo indicado. Consulte .ahrena/.directives para
paths.project_artifacts, paths.framework y language.i18n. En modo remote, use
obligatoriamente el MCP de GitHub para sincronizar con el repositorio del framework.

Formato de salida:
Lista de archivos incorporados y traducciones creadas (modo local) o branch y enlace del PR (modo remote).
Si se usó --remove, confirmación de eliminación en .ahrena/artifacts/.
```

## Ejemplo de Invocación

**Incorporar todos los artefactos en el framework local:**

```
/cry-push-to-framework --local
```

**Incorporar y abrir PR en el repositorio del framework (vía MCP de GitHub):**

```
/cry-push-to-framework --remote todos
```

**Incorporar un artefacto específico en el framework local y eliminar del proyecto:**

```
/cry-push-to-framework pt-BR/engineering/quality/lexis/lex-code-review.md --local --remove
```

## Restricciones

- Solo incorpora artefactos que estén bajo `.ahrena/artifacts/` con estructura válida (lang/clade/subclade/pilar)
- Siempre ejecuta `kata-push-to-framework` (nunca hace la copia directamente sin el Kata)

## Referencias

- `kata-push-to-framework` — Procedimiento ejecutado por este Cry (el Kata consulta el flujo recomendado de artefactos; ver documentación del Kata)
