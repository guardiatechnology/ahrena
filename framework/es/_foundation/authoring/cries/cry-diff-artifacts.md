# Cry: Diff de Artefactos

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Comparación de artefactos del proyecto con el framework

## Descripción

Atajo para comparar artefactos del proyecto (`.ahrena/artifacts` y, cuando aplique, `.ahrena/framework`) con el framework en modo **--local** (vs framework en el repo) o **--remote** (vs versión más reciente del framework en GitHub, obtenida vía MCP de GitHub). Invoca `kata-diff-artifacts` y presenta el informe de diferencias.

## Uso

```
/cry-diff-artifacts [--local | --remote] [objetivo]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `--local` | No* | Comparar `.ahrena/artifacts` (y opcionalmente `.ahrena/framework`) con el framework local (`paths.framework`). | `--local` |
| `--remote` | No* | Comparar estado local con la versión más reciente del framework en el remoto; **obligatorio** usar el MCP de GitHub para obtener el contenido remoto. | `--remote` |
| `objetivo` | No | Ruta(s) en `paths.project_artifacts` o "todos". Si se omite, considerar todos los artefactos. | `pt-BR/engineering/quality/lexis/lex-foo.md` o `todos` |

*Debe indicarse uno de los modos (`--local` o `--remote`).

## Qué Hace el Comando

1. Determina el modo (local o remoto) a partir de `--local` o `--remote`
2. Invoca `kata-diff-artifacts` con el modo y el objetivo indicados
3. Presenta el informe de diferencias al usuario (solo lectura; no se modifica ningún archivo)

## Plantilla de Prompt

```
Contexto:
- Modo: {{--local}} o {{--remote}}
- Objetivo: {{objetivo}} (o todos los artefactos en .ahrena/artifacts/)

Tarea:
Ejecute kata-diff-artifacts en el modo indicado. En modo remote, use
obligatoriamente el MCP de GitHub para obtener el estado del framework en el remoto.

Formato de salida:
Informe con artefactos solo en artifacts, solo en el framework (local o remoto),
y los que difieren (con indicación de diff). Ningún cambio en archivos.
```

## Ejemplo de Invocación

**Comparar con el framework local:**

```
/cry-diff-artifacts --local
```

**Comparar con la versión más reciente en el remoto (vía MCP de GitHub):**

```
/cry-diff-artifacts --remote
```

**Comparar un artefacto específico con el framework local:**

```
/cry-diff-artifacts --local pt-BR/engineering/quality/lexis/lex-code-review.md
```

## Restricciones

- Solo lectura; el comando no modifica `.ahrena/` ni `framework/`.
- En modo **--remote**, es obligatorio usar el MCP de GitHub.

## Referencias

- `kata-diff-artifacts` — Procedimiento ejecutado por este Cry
- `codex-pilars` — Flujo y conceptos de artefactos en el proyecto y Push
