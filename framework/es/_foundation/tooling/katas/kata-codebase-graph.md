# Kata: Grafo de Conocimiento de la Base de Código

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Ingeniería — construcción, actualización y consulta del grafo de código para mapeo de impacto

## Objetivo

Construir o actualizar el grafo de conocimiento de un repositorio con Graphify y consultarlo para producir la tabla de componentes afectados en el formato que consume `kata-architecture-brief`. El procedimiento entrega dependencias directas **e inversas**, que es la carencia de la lectura ad hoc del repositorio.

El grafo es insumo consultivo. Este Kata nunca bloquea un flujo: cuando Graphify está ausente, deshabilitado o el grafo está desactualizado, registra la indisponibilidad y devuelve el control al agente invocador.

## Cuándo Usar

- En el paso 2 de `kata-architecture-brief`, al mapear los componentes afectados por un conjunto de criterios de aceptación
- En la verificación de scope creep de `kata-quality-gate`, al comparar el diff del PR con la frontera de alcance declarada
- Al evaluar el radio de impacto de un cambio en un contrato público, antes de modificarlo
- Al investigar una base de código desconocida y necesitar identificar hubs arquitectónicos

No se debe usar cuando la respuesta exige una única lectura de un archivo ya conocido. El costo de construir el grafo no se justifica.

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Ruta del repositorio | Sí | Raíz del repositorio a indexar |
| Nodos de interés | No | Etiquetas o ID a consultar (`affected`, `explain`, `path`) |
| Criterios de aceptación | No | Necesarios cuando la salida alimenta la tabla de componentes de `kata-architecture-brief` |
| Modo de extracción | No | `code-only` (por omisión) o semántico. Ver `codex-graphify` |

## Workflow

Copie esta lista de verificación y acompañe el progreso:

```
Progreso:
- [ ] 1. Verificar habilitación y disponibilidad del binario
- [ ] 2. Construir o actualizar el grafo
- [ ] 3. Verificar desactualización mediante built_at_commit
- [ ] 4. Consultar el grafo
- [ ] 5. Armar la tabla de componentes afectados
- [ ] 6. Validación final
```

### Paso 1: Verificar habilitación y disponibilidad del binario

1. Leer `graphify.enabled` en `.ahrena/.directives`. Si es `false`, registrar "grafo deshabilitado por directriz" y finalizar el Kata sin error.
2. Verificar que el binario exista en el PATH. Si está ausente, registrar "Graphify no instalado" y finalizar sin error — el agente invocador continúa con el comportamiento anterior.
3. No instalar el binario dentro de este Kata. La instalación es responsabilidad de la vía de instalación del framework.

### Paso 2: Construir o actualizar el grafo

1. Si no existe grafo para el repositorio, ejecutar la extracción determinista:

   ```
   graphify extract <ruta> --code-only --out <caché>
   ```

   El modo `--code-only` ejecuta AST local, no exige clave de API y no realiza llamadas de red.

2. Si ya existe grafo, se prefiere la actualización incremental:

   ```
   graphify update <ruta>
   ```

3. Ejecutar la etapa semántica **solo** cuando la pregunta dependa de documentos, PDF o imágenes. En ese caso, usar `--backend claude-cli`, que cobra a la suscripción Pro/Max y no exige clave de API separada. Se debe invocar desde un directorio de trabajo neutro: cada llamada carga el contexto local de Claude Code, y la concurrencia se fuerza a 1. Ver "Restricciones Técnicas" en `codex-graphify`.
4. En grafos por encima de aproximadamente 5.000 nodos, desactivar la visualización con `--no-viz`.

### Paso 3: Verificar desactualización mediante `built_at_commit`

1. Leer el campo `built_at_commit` de `graph.json`.
2. Compararlo con el `HEAD` actual del repositorio.
3. Si divergen, ejecutar `graphify check-update <ruta>` y decidir:
   - divergencia pequeña y la consulta no toca los archivos modificados: continuar y **declarar** que el grafo está en el commit anterior;
   - divergencia relevante: actualizar con `graphify update` antes de consultar.
4. Nunca presentar un resultado de grafo desactualizado sin declarar el commit de origen. Una respuesta vieja con apariencia de precisión es peor que la ausencia de respuesta.

### Paso 4: Consultar el grafo

Se elige el comando según la pregunta:

| Pregunta | Comando |
|----------|---------|
| ¿Quién se rompe si se modifica X? | `graphify affected "X" --depth N` |
| ¿Qué es X y con qué se conecta? | `graphify explain "X"` |
| ¿Cómo se enlaza A con B? | `graphify path "A" "B"` |
| ¿Cuáles son los hubs arquitectónicos? | `graphify god-nodes --top N` |
| Pregunta abierta sobre la base de código | `graphify query "<pregunta>" --budget N` |

1. `affected` exige una etiqueta única. Si devuelve `No unique node match`, se debe obtener el ID calificado del nodo con `explain` o inspeccionando `graph.json`, y repetir con el ID.
2. Registrar la confianza de las aristas que sustentan la respuesta. `EXTRACTED` es una relación explícita en el código; `INFERRED` es resolución por heurística de Graphify — y ocurre también en el modo `--code-only`.
3. Usar `--budget` en `query` para limitar la salida en tokens.

### Paso 5: Armar la tabla de componentes afectados

Se consolida el resultado en el formato que consume `kata-architecture-brief`:

| Componente | Tipo | Acción | AC cubiertos |
|---|---|---|---|

1. Cada fila derivada del grafo DEBE traer el origen `archivo:línea` que provee Graphify.
2. Separar explícitamente los componentes encontrados por recorrido **inverso** — son justamente los que la lectura ad hoc no encontraría.
3. Marcar las filas sustentadas solo por aristas `INFERRED`. Exigen confirmación humana antes de convertirse en frontera de alcance.
4. No incluir en el alcance componentes que aparecieron solo en el grafo y no tienen relación con ningún criterio de aceptación.

### Paso 6: Validación Final

Antes de entregar la salida, se debe verificar:

- [ ] El commit de origen del grafo (`built_at_commit`) está declarado en la salida
- [ ] Los componentes provenientes de recorrido inverso están identificados como tales
- [ ] Las filas sustentadas solo por aristas `INFERRED` están marcadas
- [ ] Cada fila de la tabla referencia al menos un criterio de aceptación
- [ ] Si el grafo estaba indisponible o desactualizado, eso está declarado de forma explícita

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Tabla de componentes afectados | Markdown | Paso 2 de `kata-architecture-brief` |
| Declaración de procedencia | Markdown | Misma salida: commit de origen, modo de extracción, confianza de las aristas |
| Caché del grafo | JSON | `.ahrena/` (fuera del control de versiones) |

## Ejemplo de Ejecución

### Input de Ejemplo

```
Repositorio: financial-context
Nodo de interés: VersionSeal
Pregunta: ¿quién resulta impactado si se modifica VersionSeal?
```

### Salida de Ejemplo

```
Grafo: built_at_commit 3b1c756 (igual al HEAD) · modo --code-only
20.882 nodos · 49.563 aristas · 45.782 EXTRACTED / 3.781 INFERRED

graphify affected "VersionSeal" --depth 2
Relaciones recorridas: calls, references, imports, uses, inherits, implements (+7)

Impacto inverso:
| Componente | Tipo | Acción | AC cubiertos |
|---|---|---|---|
| components/commons/application/services/_lifecycle_test.py:L49 | prueba | revisar | AC-1 |
| components/commons/application/services/archive_entity_service_test.py:L35 | prueba | revisar | AC-1 |
| components/commons/infra/data/contracts/version_record.py:L39 | módulo | evaluar (INFERRED) | AC-1 |

VersionSeal: grado 238, comunidad 1, definido en
components/commons/infra/data/version/seal.py:L34.

Nota: version_record.py entra solo por arista INFERRED (relación `uses`
resuelta por heurística). Confirmar antes de tratarla como frontera de alcance.
```

## Restricciones

- Nunca bloquear el flujo invocador. La ausencia del binario, `graphify.enabled: false` o un grafo desactualizado resultan en un registro explícito y la devolución del control, no en un error
- Nunca presentar un resultado sin declarar `built_at_commit` y el modo de extracción
- Nunca tratar una arista `INFERRED` como hecho confirmado al definir una frontera de alcance
- Nunca versionar `graph.json`. La caché queda bajo `.ahrena/`, fuera del control de versiones, según la decisión registrada en `codex-graphify`
- Nunca ejecutar la etapa semántica cuando la pregunta se puede responder desde el código. El modo `--code-only` es gratuito y determinista
- Nunca instalar el binario dentro de este Kata
- Consultar `codex-graphify` antes de usar cualquier comando no listado en el paso 4
