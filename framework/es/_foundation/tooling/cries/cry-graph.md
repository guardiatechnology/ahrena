# Cry: Consultar el Grafo de la Base de Código

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Ingeniería — consulta rápida al grafo de conocimiento de código

## Descripción

Atajo para construir, actualizar o consultar el grafo de conocimiento de un repositorio. El comando invoca `kata-codebase-graph`, que ejecuta el procedimiento completo: verifica la habilitación, construye o actualiza el grafo, comprueba la desactualización y devuelve la respuesta con la procedencia declarada.

El uso más frecuente es responder "quién se rompe si se modifica esto", que es la pregunta de dependencia inversa que la lectura ad hoc del repositorio no responde.

## Uso

```
/cry-graph [pregunta o nodo] [--repo <ruta>] [--depth N] [--refresh]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `pregunta o nodo` | No | Etiqueta del nodo a analizar o pregunta abierta. Sin argumento, el comando construye o actualiza el grafo e informa los hubs | `VersionSeal` |
| `--repo` | No | Ruta del repositorio. Por omisión: repositorio actual | `--repo ../financial-context` |
| `--depth` | No | Profundidad del recorrido inverso. Por omisión: 2 | `--depth 3` |
| `--refresh` | No | Fuerza la actualización del grafo antes de consultar | `--refresh` |

## Qué Hace el Comando

1. Invoca `kata-codebase-graph` con los argumentos recibidos
2. El Kata verifica `graphify.enabled` y la presencia del binario; si está indisponible, informa y finaliza sin error
3. El Kata construye o actualiza el grafo en modo determinista y compara `built_at_commit` con el `HEAD`
4. El Kata ejecuta la consulta adecuada a la pregunta y devuelve la respuesta con el commit de origen, el modo de extracción y la confianza de las aristas

## Prompt Template

```
Ejecute kata-codebase-graph.

Contexto:
- Repositorio: {{--repo | repositorio actual}}
- Objetivo de la consulta: {{pregunta o nodo | ninguno — solo construir/actualizar
  e informar hubs}}
- Profundidad del recorrido inverso: {{--depth | 2}}
- Forzar actualización: {{--refresh | no}}

Tarea:
Siga el workflow de kata-codebase-graph del paso 1 al 6. Cuando exista
objetivo de consulta, priorice el recorrido inverso (impacto) sobre el
directo. Si el grafo está indisponible, deshabilitado o desactualizado,
declare la situación y devuelva el control sin error.

Formato de salida:
- Línea de procedencia: built_at_commit, modo de extracción, cantidad de
  nodos y aristas con la división EXTRACTED / INFERRED
- Tabla de componentes afectados en el formato de kata-architecture-brief
  (Componente | Tipo | Acción | AC cubiertos)
- Identificación explícita de los componentes provenientes de recorrido inverso
- Marcado de las filas sustentadas solo por aristas INFERRED
```

## Ejemplo de Invocación

**Input:**

```
/cry-graph VersionSeal --repo ../financial-context --depth 2
```

**Salida esperada:**

```
Grafo: built_at_commit 3b1c756 (igual al HEAD) · modo --code-only
20.882 nodos · 49.563 aristas · 45.782 EXTRACTED / 3.781 INFERRED

VersionSeal — grado 238, comunidad 1
Definido en components/commons/infra/data/version/seal.py:L34

Impacto inverso (profundidad 2):
| Componente | Tipo | Acción | AC cubiertos |
|---|---|---|---|
| components/commons/application/services/_lifecycle_test.py:L49 | prueba | revisar | — |
| components/commons/infra/data/contracts/version_record.py:L39 | módulo | evaluar (INFERRED) | — |

1 fila sustentada solo por arista INFERRED. Confirmar antes de tratarla
como frontera de alcance.
```

## Restricciones

- No construye el grafo por cuenta propia: delega íntegramente en `kata-codebase-graph`
- No instala el binario de Graphify
- No versiona `graph.json`
- No bloquea el flujo cuando el grafo está indisponible — informa y finaliza sin error
- No presenta un resultado sin la línea de procedencia

## Diferencia de Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Invocación rápida | Procedimiento completo |
| **Complejidad** | Baja: recibe argumentos y delega | Alta: 6 pasos con validación final |
| **¿Configura agente?** | No | Sí |
| **Ejemplo** | `/cry-graph VersionSeal` | `kata-codebase-graph` del paso 1 al 6 |
