# Lexis: Los Planes No Viven Bajo `docs/`

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Rutas canónicas para archivos de plan (`plan-*.md`) en proyectos Ahrena

## Propósito

El directorio `docs/` está reservado para artefactos canónicos de documentación: fases del flujo Issue-Driven (`docs/issues/issue-{N}/`), feature design docs (`docs/{context}/{entities,oas,events,agents,metrics}/`), ADRs (`docs/adr/`) y runbooks (`docs/runbooks/`).

Los planes de ejecución (`plan-*.md`) siguen el modelo jerárquico Issue → Plan → PR descrito en `lex-agent-planning`: el cuerpo de la sub-issue Plan en GitHub es la fuente de verdad canónica; los provider caches locales (`.claude/plans/` o `.cursor/plans/`) materializan el contenido durante la sesión y están gitignored.

Mezclar planes bajo `docs/` rompe esa separación: confunde la navegación del proyecto, contamina los artefactos de fase con estado operacional y abre la puerta a múltiples fuentes de verdad no sincronizadas. Violación observada en consumidores downstream del Ahrena: archivos del tipo `docs/skills/{slug}/plans/plan-{M}-{slug}.md` materializados junto a specs.

## Ley

> **Materializar archivos de plan (`plan-*.md`) bajo `docs/`, bajo cualquier ruta que combine `docs/` con `plans/` como segmentos del path, o en cualquier subdirectorio de `docs/` está FORBIDDEN. Las rutas canónicas para planes son exactamente tres: (a) `.claude/plans/plan-{M}-{slug}.md` (provider cache de Claude Code, gitignored); (b) `.cursor/plans/plan-{M}-{slug}.md` (provider cache de Cursor, gitignored); (c) cuerpo de la sub-issue Plan en GitHub (canónico, committed vía API GitHub). Ninguna otra ruta es válida.**

## Alcance

- **Aplica a:** todos los repositorios que adoptan el framework Ahrena, incluyendo el repositorio del propio framework y proyectos consumidores downstream
- **Agentes vinculados:** todos los agentes que materializan, mueven o proponen crear archivos de plan — `warrior-athena`, `warrior-eunomia`, `warrior-apollo`, `warrior-hephaestus`, `warrior-claudionor`, y cualquier Kata de plan (`kata-plan-task`, `kata-load-plan-from-subissue`, `kata-flush-plan-to-subissue`, `kata-decompose-issue-into-plans`)
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones

## Aplicabilidad Prospectiva

Esta Lex aplica prospectivamente: los archivos de plan legados detectados bajo `docs/` en proyectos que adoptaron Ahrena antes de esta Lex DEBEN ser migrados a la ruta canónica (cuerpo de la sub-issue + provider cache) en la próxima sesión que toque ese plan. No hay bloqueo retroactivo ciego — el agente que detecte el plan huérfano DEBE señalar la migración al humano antes de proceder con cualquier otro trabajo en ese plan.

```
<HARD-GATE>
Todo agente NO DEBE crear, mover o aceptar instrucción para materializar
un archivo de plan (`plan-*.md`) en cualquier ruta que combine `docs/`
y `plans/` como segmentos del path.

Precondiciones obligatorias para crear/materializar un plan:
  (a) La ruta comienza con `.claude/plans/` o `.cursor/plans/` (provider cache local, gitignored)
  (b) O el destino es el cuerpo de la sub-issue Plan en GitHub vía API
  (c) Ningún segmento del path contiene `docs/`
  (d) Ningún segmento del path contiene `plans/` bajo `docs/`

Esta regla se aplica a TODO proyecto Ahrena, independientemente de:
  - tamaño percibido ("es solo un archivo de plan de skill")
  - urgencia ("necesito documentar ahora")
  - quién solicitó ("el usuario pidió ponerlo ahí")
  - patrón histórico del proyecto ("siempre lo hicimos así")

Excepción única declarada: Ninguna. Los planes huérfanos legados
bajo `docs/` DEBEN ser migrados; nunca normalizados.
</HARD-GATE>
```

## Protocolo de Detección

Al encontrar un archivo `plan-*.md` bajo `docs/` durante cualquier operación (lectura, búsqueda, listado), el agente DEBE:

1. PAUSAR la operación actual
2. Señalar al humano: ruta del archivo huérfano, parent Issue (si es identificable), recomendación de migración
3. Esperar dirección humana antes de tocar el archivo (no migrar unilateralmente — el contenido puede tener contexto de fase o ser candidato a otra categoría de documento)

## Ejemplos

### Correcto

```
.claude/plans/plan-163-codify-3-lexis-hard-gate-rules.md   # provider cache Claude (gitignored)
.cursor/plans/plan-163-codify-3-lexis-hard-gate-rules.md   # provider cache Cursor (gitignored)
GitHub Issue #163 body (canónico)                           # vía lex-agent-planning
```

### Incorrecto

```
docs/skills/guardia-hello/plans/plan-001-init.md           # FORBIDDEN — combina docs/ + plans/
docs/issues/issue-163/plans/plan-execution.md              # FORBIDDEN — plans/ bajo docs/
docs/plans/plan-163.md                                      # FORBIDDEN — plans/ bajo docs/
docs/{context}/plans/plan-design.md                         # FORBIDDEN — combina docs/ + plans/
```

## Validación Automatizada

- **Herramienta:** CI lint script (extensión de `lint-paths.yml`) que ejecuta `find docs/ -name 'plan-*.md' -o -path '*/plans/*'` y falla el pipeline cuando encuentra cualquier match
- **Momento:** pre-commit hook local + CI en todo PR + auditoría mensual en proyectos downstream
- **Métrica:** 0 archivos `plan-*.md` bajo `docs/` en cualquier repositorio Ahrena; 0 segmentos `docs/**/plans/**` en cualquier árbol del proyecto
