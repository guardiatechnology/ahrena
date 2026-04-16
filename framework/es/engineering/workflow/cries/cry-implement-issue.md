# Cry: Implementar Issue (Issue-Driven Development)

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Punto de entrada del flujo Issue-Driven Development — invoca a `warrior-athena` para conducir la issue de GitHub a través de las 7 fases hasta la creación del PR

## Descripción

Este comando dispara el flujo completo de desarrollo orientado por issue: desde la lectura de la issue en GitHub hasta la creación del PR revisable, pasando por requisitos, arquitectura, Gate 1 de alcance, implementación (delegada), seguridad, Gate 2 de calidad y preparación del PR. El orquestador es el **Warrior Athena**, que coordina todos los Katas del clade `engineering/workflow/` y delega a especialistas (Apollo, Daedalus, Kronos) cuando corresponde.

## Uso

```
/cry-implement-issue <número de issue> [<owner>/<repo>]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `número de issue` | Sí | Número de la issue en GitHub | `42` |
| `<owner>/<repo>` | No | Repositorio de destino; por defecto: repo actual (vía git remote) | `guardiafinance/ahrena` |

## Requisitos previos

- `github` listado en `mcp.servers` en `.ahrena/.directives`
- `notion` listado en `mcp.servers` (opcional — enriquece con contexto Notion cuando está disponible)
- Variables de entorno: `GITHUB_PAT` (obligatoria) y `NOTION_API_KEY` (opcional)
- Issue existente en el repositorio indicado

## Qué Hace el Comando

Invoca a **warrior-athena** para conducir las 7 fases del flujo:

1. **Fase 1 — Análisis de la Issue** (`kata-issue-analysis`): lee la issue en GitHub y busca contexto en Notion → `docs/issues/issue-{n}/01-brief.md`
2. **Fase 2 — Requisitos** (`kata-requirements-brief`): elicita ACs numerados con perspectiva PO → `docs/issues/issue-{n}/02-requirements.md`
3. **Fase 3 — Arquitectura** (`kata-architecture-brief`): mapea componentes, delega diseño de API/eventos a Daedalus/Kronos si aplica, invoca `kata-adr-write` para decisiones relevantes → `docs/issues/issue-{n}/03-architecture.md` + ADRs en `docs/adr/`
4. **Gate 1 — Aprobación de Alcance:** Athena presenta los artefactos al humano y espera aprobación explícita
5. **Fase 4 — Implementación:** Athena delega a `warrior-apollo` (o warrior del stack) vía `kata-python-implement`; las pruebas marcan `AC-N` para trazabilidad
6. **Fase 5 — Revisión de Seguridad** (`kata-security-review`): OWASP + CVE scan → `docs/issues/issue-{n}/05-security-review.md`
7. **Fase 6 — Gate 2 Calidad** (`kata-quality-gate`): 6 checks (trazabilidad AC↔prueba, scope creep, best practices, pruebas, cobertura, tipos) → `docs/issues/issue-{n}/06-quality-report.md`; `no-go` regresa a la Fase 4
8. **Fase 7 — Preparar PR** (`kata-pr-prepare`): crea branch + push + PR vía GitHub MCP; transiciona ADRs `proposed → accepted`

## Prompt Template

```
Contexto:
- Issue: #{{número de issue}}
- Repositorio: {{<owner>/<repo>}} (o detectado vía git remote)

Tarea:
Actúa como **warrior-athena** y conduce el flujo Issue-Driven Development completo para la issue #{{número de issue}}.

Ejecuta las 7 fases en orden estricto según `codex-issue-workflow`:

1. **Fase 1:** kata-issue-analysis — lee la issue vía GitHub MCP y busca contexto vía Notion MCP; produce el brief en docs/issues/issue-{n}/01-brief.md.

2. **Fase 2:** kata-requirements-brief — elicita criterios de aceptación numerados (AC-1, AC-2, ...); haz preguntas de aclaración al usuario si es necesario; produce 02-requirements.md.

3. **Fase 3:** kata-architecture-brief — mapea los componentes afectados; delega a warrior-daedalus (API) o warrior-kronos (eventos) cuando corresponda; invoca kata-adr-write para decisiones arquitectónicas relevantes; produce 03-architecture.md + ADRs en docs/adr/.

4. **Gate 1:** Presenta brief + ACs + arquitectura + ADRs propuestos al usuario y **espera aprobación explícita** antes de avanzar.

5. **Fase 4:** Delega a warrior-apollo (o equivalente) para implementar. Cada prueba debe referenciar `AC-N` según la convención en codex-issue-workflow.

6. **Fase 5:** kata-security-review — revisa el diff contra OWASP Top 10 y CVE scan.

7. **Fase 6:** kata-quality-gate — ejecuta los 6 checks. `no-go` regresa a la Fase 4; `go` avanza.

8. **Fase 7:** kata-pr-prepare — crea branch, push de archivos y PR vía GitHub MCP; transiciona ADRs proposed → accepted; entrega URL del PR.

Respeta rigurosamente lex-issue-driven: sin saltar gates, con trazabilidad AC↔prueba, con ADRs para decisiones relevantes, con documentación en docs/.
```

## Ejemplo de Invocación

**Input:**

```
/cry-implement-issue 42 guardiafinance/ahrena
```

**Output esperado (flujo secuencial con pausas para humano):**

- Athena lee la issue #42, produce `docs/issues/issue-42/01-brief.md`
- Athena hace preguntas de aclaración al usuario (si es necesario)
- Athena produce `02-requirements.md` con 5 ACs
- Athena produce `03-architecture.md` + crea `docs/adr/ADR-008-*.md`
- **Gate 1:** Athena presenta resumen; el usuario aprueba
- Apollo implementa; cada prueba marca el AC correspondiente
- `kata-security-review` aprueba (0 hallazgos críticos)
- `kata-quality-gate`: 6 checks ✅ → `go`
- Athena crea el PR e informa URL: `https://github.com/guardiafinance/ahrena/pull/123`

## Restricciones

- **El Gate 1 es inviolable:** el comando no avanza a la implementación sin aprobación humana explícita
- **El Gate 2 es inviolable:** el comando no crea PR si el Gate 2 resultó en `no-go`
- **Solo issues existentes:** el comando rehúsa si la issue no existe o está vacía (según `lex-issue-driven`)
- **Documentación en `docs/`:** todos los artefactos públicos del flujo quedan en `docs/issues/issue-{n}/` y `docs/adr/`
- **El comando orquesta, no implementa:** el propio comando no escribe código ni contratos — delega a Katas y warriors especialistas

## Cries y Warriors Asociados

- **warrior-athena** — Orquestadora, invocada por este Cry
- **warrior-apollo** — Delegada en la Fase 4 para implementación Python
- **warrior-daedalus** — Delegada en la Fase 3 para diseño de API
- **warrior-kronos** — Delegada en la Fase 3 para diseño de eventos
- **cry-api-design**, **cry-event-storm**, **cry-python-implement** — Cries relacionados (flujos aislados; este Cry los orquesta en un flujo unificado partiendo de la issue)

## Referencias

- `warrior-athena` — orquestadora del flujo
- `lex-issue-driven` — leyes inquebrantables
- `codex-issue-workflow` — estructura completa del flujo
- `engineering/workflow/README.md` — guía narrativa para humanos
