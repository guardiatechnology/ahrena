# Cry: Push al Framework

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Incorporación de artefactos de proyecto al framework

## Descripción

Comando rápido para incorporar al framework canónico los artefactos creados en el espacio del proyecto (`.ahrena/artifacts/`). Invoca `kata-push-to-framework`, que copia los archivos a `framework/`, garantiza traducciones en los idiomas obligatorios y opcionalmente elimina las copias del proyecto.

## Uso

```
/cry-push-to-framework [objetivo] [--remove]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `objetivo` | No | Ruta(s) en `.ahrena/artifacts/` o "todos". Si se omite, procesa todos los artefactos encontrados | `pt-BR/engineering/quality/lexis/lex-foo.md` o `todos` |
| `--remove` | No | Si está presente, elimina los artefactos de `.ahrena/artifacts/` tras copiar al framework | `--remove` |

## Qué Hace el Comando

1. Lee `.ahrena/.directives` para obtener `paths.project_artifacts`, `paths.framework` y `language.i18n`
2. Identifica los artefactos en `.ahrena/artifacts/` (todos o los indicados)
3. Ejecuta `kata-push-to-framework` con los parámetros proporcionados
4. Copia los artefactos a `framework/` y genera traducciones faltantes
5. Opcionalmente elimina los archivos del proyecto
6. Reporta los archivos incorporados

## Plantilla de Prompt

```
Contexto:
- Objetivo: {{objetivo}} (o todos los artefactos en .ahrena/artifacts/)
- Eliminar del proyecto tras Push: {{--remove}}

Tarea:
Ejecute kata-push-to-framework. Consulte .ahrena/.directives para
paths.project_artifacts y language.i18n. Incorpore los artefactos al
framework y garantice versiones en todos los idiomas obligatorios.

Formato de salida:
Lista de archivos copiados a framework/ y traducciones creadas (si las hay).
Si se usó --remove, confirmación de eliminación en .ahrena/artifacts/.
```

## Ejemplo de Invocación

**Incorporar todos los artefactos del proyecto:**

```
/cry-push-to-framework
```

**Incorporar un artefacto específico:**

```
/cry-push-to-framework pt-BR/engineering/quality/lexis/lex-code-review.md
```

**Incorporar y eliminar del proyecto:**

```
/cry-push-to-framework todos --remove
```

## Restricciones

- Solo incorpora artefactos que estén bajo `.ahrena/artifacts/` con estructura válida (lang/clade/subclade/pilar)
- Siempre ejecuta `kata-push-to-framework` (nunca hace la copia directamente sin el Kata)

## Referencias

- `kata-push-to-framework` — Procedimiento ejecutado por este Cry
- `codex-pilars` — Flujo recomendado (crear en proyecto → validar → Push)
