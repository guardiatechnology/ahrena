# Cry: Nueva Tech Task

> **Prefijo:** `cry-` | **Alcance:** Crear un issue de tech task en el repositorio

## Qué hace

Crea un Issue en GitHub usando la plantilla `tech-task`, que responde Por qué / Qué / Cómo. Invoca `kata-contributing-issue` con el tipo `tech-task`. Sigue `lex-issue-quality` y `lex-issue-first`.

## Uso

```
/cry-new-tech-task [título]
```

## Parámetros

| Parámetro | Requerido | Descripción |
|-----------|:---------:|-------------|
| `título` | No | Breve resumen de la tarea. Si se omite, el agente pregunta antes de continuar. |

## Ejemplos

```
/cry-new-tech-task
/cry-new-tech-task update contributing guide with new branch naming rules
/cry-new-tech-task fix CI pipeline for Windows runners
```

## Invoca

`kata-contributing-issue` con `type: tech-task`
