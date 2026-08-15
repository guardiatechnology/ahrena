# Codex: Graphify — Grafo de Conocimiento de Código

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Ingeniería — comprensión de código, mapeo de impacto y apoyo al diseño técnico

## Visión General

Graphify es una herramienta de línea de comandos que transforma un repositorio en un grafo de conocimiento consultable. La extracción de código se realiza por AST mediante tree-sitter, de forma local y sin llamadas de API. Los documentos, PDF, imágenes y esquemas de base de datos pasan por una etapa semántica opcional que utiliza un modelo de lenguaje.

El valor para Guardia es específico: responder preguntas de dependencia inversa. El paso 2 de `kata-architecture-brief` produce la tabla de componentes afectados, y esa tabla es la frontera de alcance que `kata-quality-gate` consume en su verificación de scope creep. Hoy la tabla se arma leyendo el repositorio de forma ad hoc, lo cual encuentra dependencias directas y no encuentra las inversas. El comando `graphify affected` responde "quién se rompe si se modifica esto" con precisión de `archivo:línea`.

Este Codex documenta la superficie real de la versión medida (0.9.33), el modelo de costo medido en un repositorio de Guardia y las limitaciones observadas. No reemplaza la documentación del proveedor; registra lo que fue verificado.

## Contexto

- **Dominio:** comprensión de bases de código, mapeo de impacto, apoyo al diseño técnico
- **Público objetivo:** warriors de ingeniería (`warrior-apollo`, `warrior-hephaestus`, `warrior-athena`), desarrolladores, revisores de PR
- **Actualización:** en cada cambio de versión de Graphify que altere comandos, el formato de `graph.json` o el modelo de costo

## Contenido

### Principios

1. **La extracción de código es determinista; la etapa semántica no lo es.** El modo `--code-only` ejecuta AST local, sin clave de API y sin red. Es reproducible y se puede usar en automatización. La etapa semántica depende de un modelo de lenguaje y no ofrece esa garantía.
2. **El grafo es insumo consultivo, nunca gate de CI.** El agente decide; el grafo informa. `scripts/validate.py` es determinista por diseño y NO DEBE pasar a depender de una etapa semántica.
3. **`INFERRED` no significa "generado por un LLM".** La confianza de la arista describe cómo se resolvió la relación, no qué motor la produjo. Ver "Patrones y Convenciones".
4. **El grafo envejece con cada commit.** `graph.json` contiene `built_at_commit`. Consultar un grafo desactualizado sin verificar ese campo produce respuestas erróneas con apariencia de precisión.
5. **La herramienta es opcional.** Todo consumo del grafo DEBE degradar de forma limpia cuando el binario está ausente, `graphify.enabled` es `false` o el grafo está desactualizado.

### Patrones y Convenciones

#### Confianza de las aristas

| Confianza | Significado | Ejemplo de relación |
|-----------|-------------|---------------------|
| `EXTRACTED` | La relación está explícita en el código fuente | `imports`, `calls`, `contains` |
| `INFERRED` | La relación fue resuelta por una heurística de Graphify | `uses` derivado de resolución de tipo |

Medición en `financial-context`: de las 49.563 aristas, **45.782 son `EXTRACTED` y 3.781 son `INFERRED`** — y **todas** contienen `_origin: ast`. Es decir, las aristas `INFERRED` aparecen en el modo `--code-only`, sin ninguna llamada de API. El modo sigue siendo determinista; simplemente no está libre de `INFERRED`.

#### Estructura de `graph.json`

| Campo | Tipo | Observación |
|-------|------|-------------|
| `nodes` | lista | Claves: `label`, `file_type`, `source_file`, `source_location`, `_origin`, `id`, `community`, `norm_label` |
| `links` | lista | Aristas. Claves: `relation`, `confidence`, `source_file`, `source_location`, `weight`, `_origin`, `source`, `target`, `confidence_score` |
| `hyperedges` | lista | Vacía en la extracción medida |
| `built_at_commit` | cadena | Commit de origen del grafo — base canónica para detectar desactualización |
| `directed` | booleano | `false` en la extracción medida |
| `multigraph` | booleano | `false` en la extracción medida |

La lista de aristas se llama `links`, no `edges` (convención D3).

#### Catálogo de comandos verificado

| Comando | Función |
|---------|---------|
| `extract <ruta>` | Extracción completa headless (AST y semántica) para CI y scripts |
| `extract --code-only` | Indexa solo código por AST local; omite documentos, artículos e imágenes |
| `update <ruta>` | Reextrae archivos de código y actualiza el grafo, sin LLM |
| `affected "X"` | Recorrido inverso: nodos impactados por X. Acepta `--relation` y `--depth` |
| `explain "X"` | Nodo y vecindad en lenguaje simple, con grado y aristas de entrada y salida |
| `path "A" "B"` | Camino más corto entre dos nodos |
| `query "<pregunta>"` | Recorrido BFS del grafo para una pregunta. `--budget` limita la salida en tokens |
| `god-nodes` | Nodos más conectados (hubs arquitectónicos) |
| `check-update <ruta>` | Verifica la marca `needs_update`; seguro para cron |
| `cluster-only <ruta>` | Reejecuta la agrupación y regenera el informe. `--no-label` evita llamadas de LLM |
| `benchmark [graph.json]` | Mide la reducción de tokens frente al enfoque de corpus completo |
| `diagnose multigraph` | Informa el riesgo de colapso de aristas con los mismos extremos |
| `watch <ruta>` | Observa una carpeta y reconstruye el grafo en cada cambio |
| `install --platform P` | Instala Graphify como skill en el directorio de configuración de la plataforma |
| `hook install` | Instala hooks de git post-commit y post-checkout |
| `merge-driver` | Driver de merge de git que une dos archivos `graph.json` |

`graphify-mcp` es un segundo ejecutable que se instala junto al primero. Sirve el grafo por MCP en transporte `stdio` o HTTP Streamable, con `--api-key`, `--host`, `--port` y `--stateless`. Según `lex-mcp` regla 5, esto corresponde al **tier 2 (binario nativo stdio)**; el tier 1 (HTTP remoto alojado por el proveedor) no existe para este proveedor. La decisión de declarar el servidor en `mcp.servers` corresponde a la vía de instalación, no a este Codex.

#### Backends del modelo de lenguaje

`--backend` acepta `gemini`, `kimi`, `claude`, `openai`, `deepseek`, `ollama` y `claude-cli`.

El backend **`claude-cli`** es la vía recomendada en Guardia. Enruta por la CLI de Claude Code instalada localmente, mediante `claude -p --output-format json`, y autentica con la suscripción Pro/Max existente. Su tabla de precio es literalmente `{"input": 0.0, "output": 0.0}`: el consumo se cobra al plan, no a crédito de API pay-as-you-go. No se requiere ninguna clave de API separada.

Dos consecuencias prácticas: `--max-concurrency` se fuerza a 1 para `claude-cli`, y cada invocación carga el contexto local de Claude Code. Ver "Restricciones Técnicas".

### Decisiones Vigentes

| Decisión | Situación |
|----------|-----------|
| `graph.json` queda fuera del control de versiones, en caché bajo `.ahrena/`, y `graphify-out/` entra en el bloque gestionado de `.gitignore` | Activa |
| La detección de desactualización usa `built_at_commit` y `graphify check-update`, sin marca paralela de SHA | Activa |
| El consumo del grafo es consultivo; ningún gate de CI depende de una etapa semántica | Activa |

Sobre la primera decisión: el proveedor ofrece `graphify merge-driver` precisamente para equipos que **versionan** `graph.json`, resolviendo conflictos por unión. Guardia divergió de esa práctica porque un `graph.json` versionado es una segunda representación de la estructura del código, propensa a divergir del código real — lo cual `lex-dry` prohíbe. La divergencia es deliberada y queda registrada aquí.

### Restricciones Técnicas

- **El costo real es cuota del plan, no dólares.** En la medición semántica se consumieron 178.164 tokens de entrada para procesar cerca de 18.400 tokens de contenido — una amplificación de aproximadamente 10 veces. La causa está en el código de Graphify (`llm.py`): las CLI de Claude Code a partir de la versión 2.1 no tratan `--system-prompt` como autoridad única y siguen cargando `CLAUDE.md`, `AGENTS.md`, skills y MCP locales en cada invocación. Un `claude -p "reply OK"` trivial en la raíz del repositorio informó `total_cost_usd: 0.82` con 82.453 tokens de creación de caché.
- **Mitigación:** invocar Graphify desde un directorio de trabajo neutro, no desde la raíz de un repositorio con un `CLAUDE.md` grande. El costo de arranque se cobra por llamada y `claude-cli` no paraleliza.
- **`affected` exige una etiqueta única.** `graphify affected "EntityId"` falló con `No unique node match for EntityId`. Las etiquetas ambiguas requieren el ID calificado del nodo.
- **SQL exige un extra de instalación.** Los archivos `.sql` no contribuyen al grafo sin `tree_sitter_sql`. Instalar con `pip install "graphifyy[sql]"` (issue upstream #1745). Relevante para contextos financieros y fiscales.
- **Algunos archivos JSON producen cero nodos.** En la medición, 22 archivos no generaron nodos, entre ellos `ahrena.json`, `figma.json`, `github.json`, `notion.json` y `slack.json` (issue upstream #1666).
- **Los grafos grandes exigen `--no-viz`.** Por encima de aproximadamente 5.000 nodos, se debe desactivar la generación de `graph.html`.
- **El grafo medido es no dirigido** (`directed: false`), lo cual afecta la interpretación del recorrido inverso. Usar `diagnose multigraph` para evaluar el riesgo de colapso de aristas.
- **`.gitignore` se respeta por omisión.** En la medición se extrajeron 1.707 archivos de 4.168 versionados, y las dependencias de entorno virtual quedaron correctamente fuera. `--no-gitignore` invierte ese comportamiento.

#### Modelo de costo medido

Medición en `financial-context` en el commit `3b1c756`, Graphify 0.9.33, 16 workers de AST.

| | `--code-only` | Semántico (`--backend claude-cli`) |
|---|---|---|
| Tiempo de reloj | 359 s para 1.707 archivos (**0,21 s por archivo**) | 322 s para 22 documentos (**14,6 s por archivo**) |
| Nodos / aristas | 20.882 / 49.563 | 36 / 163 |
| Comunidades | 738 | no aplicable (`--no-cluster`) |
| Tokens | 0 | 178.164 entrada / 40.517 salida |
| Clave de API | no exigida | no exigida (CLI local y suscripción) |
| Costo de API informado | US$ 0,00 | US$ 0,0000 (cobrado al plan) |
| Concurrencia | 16 workers | forzada a 1 |

`graphify benchmark` sobre el grafo de código: corpus de 1.044.100 palabras, cerca de 1.392.133 tokens en el enfoque ingenuo, contra aproximadamente 12.841 tokens por consulta — **reducción de 108,4 veces**. El rango por pregunta fue de 83,2 veces ("what connects the data layer to the api") a 171,0 veces ("how does authentication work").

## Diagrama de Referencia

```
                    ┌─────────────────────────┐
   repositorio ───► │ extract --code-only     │  AST local, tree-sitter
                    │ (determinista, gratis)  │  0 llamadas de API
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
   docs, PDF ─────► │ etapa semántica         │  --backend claude-cli
   imágenes         │ (opcional, cuota plan)  │  concurrencia forzada a 1
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │ graph.json              │
                    │  nodes / links          │
                    │  built_at_commit  ──────┼──► base de desactualización
                    └───────────┬─────────────┘
                                │
        ┌───────────────┬───────┴───────┬────────────────┐
        ▼               ▼               ▼                ▼
    affected "X"    explain "X"    path "A" "B"     graphify-mcp
   (impacto        (nodo y        (enlace entre    (stdio o HTTP)
    inverso)        vecindad)      dos nodos)
```

## Glosario

| Término | Definición |
|---------|------------|
| AST | Árbol sintáctico abstracto. Base de la extracción determinista de código, mediante tree-sitter |
| `EXTRACTED` | Arista explícita en el código fuente |
| `INFERRED` | Arista resuelta por una heurística de Graphify, no necesariamente por un modelo de lenguaje |
| Comunidad | Agrupación de nodos detectada por el algoritmo de Leiden; aproxima la noción de subsistema |
| God node | Nodo de alta conectividad; hub arquitectónico |
| `built_at_commit` | Commit a partir del cual se construyó el grafo |
| Etapa semántica | Fase opcional que usa un modelo de lenguaje para documentos, PDF e imágenes |
| `claude-cli` | Backend que enruta por la CLI local de Claude Code y cobra a la suscripción, no a crédito de API |

## Referencias

- `kata-codebase-graph` — procedimiento operativo que aplica este Codex
- `cry-graph` — atajo de invocación
- `kata-architecture-brief` — consumidor del grafo en el paso 2 (tabla de componentes afectados)
- `kata-quality-gate` — consume la frontera de alcance en la verificación de scope creep
- `lex-mcp` — regla 1 (preferencia por la herramienta MCP) y regla 5 (jerarquía de transporte)
- `lex-dry` — fundamento de la decisión de no versionar `graph.json`
- `codex-git-spice` — precedente de Codex para una herramienta externa de línea de comandos
- Repositorio del proveedor: https://github.com/Graphify-Labs/graphify
