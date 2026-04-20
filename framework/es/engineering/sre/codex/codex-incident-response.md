# Codex: Respuesta a Incidentes

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Procedimiento de respuesta a incidentes en producción — severity levels, comunicación, estructura de war room, decisiones de rollback, post-mortem blameless

## Visión general

Este Codex es la referencia operacional para **incidentes en producción**. Define niveles de severidad, a quién activar en cada nivel, cómo estructurar la comunicación (interna y externa), cuándo rollback vs. forward-fix, y cómo conducir post-mortem blameless. Consultado por `warrior-hestia` al orquestar una respuesta, por on-call engineers durante el incidente, y por liderazgo en comunicación con stakeholders.

## Contexto

- **Dominio:** incidentes en producción afectando servicios críticos (tier-1/2).
- **Público objetivo:** `warrior-hestia`, on-call engineers, incident commanders, stakeholders
- **Actualización:** después de cada incidente sev-1 (lecciones aprendidas); trimestralmente (revisión de procedimiento)

## Contenido

### Severidad

| Sev | Criterio | Tiempo de respuesta | A quién activar |
|---|---|---|---|
| **SEV-1** | Producción tier-1 down o datos corruptos; impacto masivo (>30% usuarios) o seguridad | < 5 min | On-call + IC + Eng lead + Executive comms |
| **SEV-2** | Degradación significativa; impacto a >5% usuarios O SLO en riesgo grave | < 15 min | On-call + IC |
| **SEV-3** | Degradación parcial; los usuarios tienen workaround; SLO aún dentro del budget | < 1h | On-call |
| **SEV-4** | Bug aislado; sin impacto inmediato en producción | Horario comercial | Engineering ticket |

### Roles durante el incidente

- **Incident Commander (IC)**: coordina, decide rollback, comunica. NO es quien debuggea — es quien orquesta.
- **Technical Lead**: líder del debugging, elige hipótesis para investigar.
- **Communications Lead**: actualiza canales internos (Slack), status page externa, email a clientes si aplica.
- **Scribe**: mantiene timeline de la investigación en documento central (para post-mortem).

En incidentes pequeños (sev-3/4), el on-call acumula IC + Tech + Comms.

### Flujo de respuesta (primeros 30 minutos)

```
t+0    Alert dispara / humano reporta
        → on-call acknowledge en 5 min
        → IC declara severity

t+5    War room abierto (Zoom/Google Meet + canal Slack dedicado)
        → Técnicos entran; triage inicial
        → Scribe inicia timeline

t+10   Hipótesis primaria definida
        → Dashboards abiertos (ver runbook)
        → Decisión: mitigar rápido vs. debuggear

t+15   Mitigación aplicada (rollback, feature flag off, scale up, etc.)
        → Confirmar recovery vía métricas

t+20   Comms actualiza status page + Slack interno
        → "Identified, mitigating"

t+30   Mitigación confirmada recovery en métricas
        → IC declara "stable, monitoring"
        → Comienza investigación de causa raíz (con calma)
```

### Decisión: rollback vs. forward-fix

**Rollback cuando:**
- Deploy reciente (< 2h) es sospechoso principal.
- Mitigación rápida disponible (la versión anterior funciona).
- Costo de rollback es bajo (no hay migración de datos irreversible).

**Forward-fix cuando:**
- El cambio es en datos (no código) — rollback de código no resuelve.
- Rollback requiere migración de base de datos reversa compleja.
- Causa raíz ya identificada y el fix es trivial.

**Default:** en caso de duda, **rollback** — el debug puede continuar en staging sin impacto en el cliente.

### Comunicación

**Interna (Slack/Teams):**
- Canal dedicado (`#inc-YYYY-MM-DD-refund-outage`).
- Updates cada 15 min incluso cuando no cambia nada ("aún investigando hipótesis X").
- Lenguaje técnico OK; la audiencia son ingenieros.

**Externa (status page, email a clientes):**
- Mensajes objetivos sin detalles técnicos.
- Template:
  ```
  {HH:MM UTC} — Investigating
    We're investigating reports of elevated errors on {feature}.
    Affected users may see {symptom}.

  {HH:MM UTC} — Identified
    We identified the cause and are applying a fix.

  {HH:MM UTC} — Monitoring
    Fix deployed. Monitoring for recovery.

  {HH:MM UTC} — Resolved
    Service is fully restored. Total duration: {X}. Post-mortem coming in {N} days.
  ```
- NUNCA especular sobre la causa al cliente antes de confirmar.

**Ejecutivo (cuando sev-1 o duración > 1h):**
- Actualización horaria hasta resolved.
- Se enfoca en impacto de negocio, no detalle técnico.

### Post-mortem blameless

Después de cada sev-1 y sev-2 (sev-3/4 opcional):

1. **En hasta 5 días hábiles**, redactar documento:
   - Timeline factual (horarios, acciones, decisiones).
   - Impacto medido (usuarios afectados, ingresos, SLA).
   - Causa raíz (sin apuntar personas; apuntar sistemas y decisiones).
   - Contribuidores (factores que agravaron; ej.: runbook desactualizado, alert tardío).
   - Acciones correctivas (específicas, con owner y deadline).
   - Lo que funcionó bien (rollback rápido, comms clara) — reforzar.

2. **Revisión en reunión**: 1h con equipo involucrado + líderes; preguntas y críticas a la decisión de proceso, no a la persona.

3. **Acciones correctivas** entran en backlog con prioridad P1-P2; revisadas 30 días después.

### Anti-patterns en incident response

| Anti-pattern | Problema |
|---|---|
| Debuggear sin declarar severity | Falta de IC; el comms se vuelve caos; los stakeholders quedan a oscuras |
| Rollback sin escribir timeline | Pérdida de datos para post-mortem |
| Culpar al autor del deploy en el post-mortem | Mata la psicológico safety; la próxima vez el autor esconde el error |
| "Monitoreando" indefinidamente sin recovery confirmado | El comms queda parado; el cliente pierde confianza |
| Ignorar incidentes menores (sev-3) sin post-mortem | Patrón emerge; sev-1 en el futuro con causa ya vista |

### Herramientas típicas

- **Alerting/paging:** PagerDuty, Opsgenie, Grafana OnCall
- **Status page:** statuspage.io, Atlassian Statuspage, auto-hosteada
- **War room:** Zoom, Google Meet, Slack Huddle
- **Incident management:** Incident.io, Rootly, FireHydrant
- **Post-mortem:** Markdown en repo, Notion, Confluence

## Referencias

- `lex-slo-required` — SLO y error budget guían priorización post-incidente
- `lex-runbook-for-every-alert` — el runbook es el paso 1 del diagnóstico
- `warrior-hestia` — conduce respuesta
- `kata-incident-triage`, `kata-postmortem-write` — procedimientos detallados
- [Google SRE Book — Managing Incidents](https://sre.google/sre-book/managing-incidents/)
- [Blameless PostMortems](https://www.etsy.com/codeascraft/blameless-postmortems)
