# Cry: Nueva Tarea Simple

> **Prefijo:** `cry-` | **Alcance:** Crear un issue de tarea simple en el repositorio

## Qué hace

Crea un Issue en GitHub usando la plantilla `simple-task`, que responde Por qué / Qué / Cómo. Invoca `kata-contributing-issue` con el tipo `simple-task`. Sigue `lex-issue-quality` y `lex-issue-first`.

## Uso

```
/cry-new-simple-task [título]
```

## Parámetros

| Parámetro | Requerido | Descripción |
|-----------|:---------:|-------------|
| `título` | No | Breve resumen de la tarea. Si se omite, el agente pregunta antes de continuar. |

## Ejemplos

```
/cry-new-simple-task
/cry-new-simple-task update contributing guide with new branch naming rules
/cry-new-simple-task fix CI pipeline for Windows runners
```

## Invoca

`kata-contributing-issue` con `type: simple-task`
