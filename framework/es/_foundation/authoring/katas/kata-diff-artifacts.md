# Kata: Diff de Artefactos

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Comparación de artefactos del proyecto con el framework

## Objetivo

Comparar `.ahrena/artifacts` (y, cuando aplique, `.ahrena/framework`) con el framework en modo **local** (vs framework en el repo) o **remoto** (vs versión más reciente del framework en GitHub). Identificar qué se incorporaría, qué difiere o qué está desactualizado respecto al remoto.

## Cuándo Usar

- Antes del push, para ver qué se incorporará o qué difiere entre proyecto y framework
- Para inspeccionar divergencia entre artefactos del proyecto y el framework (local o remoto)
- Cuando se invoca mediante `cry-diff-artifacts`

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Modo | Sí | `local` o `remote`. Local: compara con `paths.framework` en el repo. Remote: compara con la versión más reciente del framework en el repositorio remoto (obtenida vía MCP de GitHub). |
| Objetivo | No | Ruta(s) relativa(s) en `paths.project_artifacts` o "todos". Si se omite, considerar todos los artefactos. |

## Workflow

```
Progreso:
- [ ] 1. Lectura de directivas
- [ ] 2. Modo local: comparación con framework local
- [ ] 3. Modo remote: comparación con versión más reciente (vía MCP de GitHub)
- [ ] 4. Validación final e informe
```

### Paso 1: Lectura de Directivas

1. Leer `.ahrena/.directives` para obtener:
   - `paths.project_artifacts` — raíz de los artefactos de proyecto
   - `paths.framework` — raíz del framework (para modo local)
   - En modo **remote:** URL o ref del repositorio del framework / branch de comparación (ej.: `paths.framework_repo` o `repo.framework`), si existe

### Paso 2: Modo local — Comparación con Framework Local

1. Listar archivos `.md` en `paths.project_artifacts` por ruta relativa `{lang}/{clade}/{subclade}/{pilar}/{archivo}`.
2. Para cada ruta lógica de artefacto, comparar con `paths.framework/{lang}/{clade}/{subclade}/{pilar}/{archivo}`:
   - existe solo en artifacts;
   - existe solo en el framework;
   - existe en ambos (en ese caso, producir diff de contenido, ej.: diferencia de líneas).
3. Opcional: incluir `.ahrena/framework/` en la comparación con `paths.framework/` (misma estructura) para ver divergencias entre la copia instalada y el framework del repo.
4. Salida: tabla o lista con columnas "Artefacto", "En artifacts", "En framework", "Diff (sí/no o resumen)".

### Paso 3: Modo remote — Comparación con Versión Más Reciente

1. **Obligatorio:** usar el **MCP de GitHub** para obtener el contenido de la versión más reciente del framework en el repositorio remoto (branch principal, ej.: `main`). El agente **DEBE** usar las herramientas MCP de GitHub (ej.: lectura de contenido de archivos en el repo, listado de árbol, comparación) para obtener los artefactos del framework en el remoto.
2. Comparar: (a) archivos en `.ahrena/artifacts/` vs misma ruta en la versión remota del framework (obtenida vía MCP); (b) archivos en `paths.framework` local (si existe) vs misma ruta en la versión remota. Salida: "solo local", "solo remoto", "diferente" (con resumen de diff cuando sea posible).
3. En modo remote **no** sustituir el MCP de GitHub por solo `git fetch`/clone en línea de comandos; el diff remoto **DEBE** basarse en datos obtenidos vía MCP de GitHub.

### Paso 4: Validación Final

- [ ] Informe entregado al usuario con las diferencias encontradas
- [ ] No se realizó ningún cambio en los archivos (solo lectura)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Informe de diff | Texto (y opcionalmente estructurado) | Respuesta al usuario |

Contenido del informe: artefactos solo en artifacts, solo en el framework (local o remoto), y los que difieren (con indicación de diff).

## Restricciones

- Solo lectura; no modificar `.ahrena/` ni `framework/`.
- En modo **remote**, es **obligatorio** usar el MCP de GitHub para obtener el estado del framework en el remoto; no usar solo git local para comparación.

## Referencias

- `codex-pilars` — Flujo y conceptos de artefactos en el proyecto y Push
- `.ahrena/.directives` — paths.project_artifacts, paths.framework
- `kata-push-to-framework` — Procedimiento de incorporación al framework
- Modo remote: MCP de GitHub (servidor configurado para el repositorio del framework)
