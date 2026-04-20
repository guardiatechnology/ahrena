# Lexis: SLO Obligatorio para Servicios tier-1/2

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Service Level Objectives (SLO) para servicios tier-1 y tier-2 — definidos antes del go-live, medidos en producción, respetados como contrato interno

## Propósito

Sin SLO, "disponibilidad" y "performance" son opinión. Los clientes reclaman cuando algo está mal; ingeniería debate qué significa "suficientemente bueno"; la priorización de confiabilidad vs. features se vuelve política. El SLO hace la discusión objetiva: contratos numéricos con clientes (internos o externos) sobre lo que es aceptable, error budget consumido como moneda para decisiones.

Esta Lexis existe para garantizar que **todo servicio tier-1 o tier-2 tenga SLO explícito antes del primer deploy en producción**, que **el SLO sea medido por SLI observables** y que **el error budget consumido guíe la priorización entre confiabilidad y entrega de features**.

## Ley

> **Todo servicio tier-1 o tier-2 DEBE tener SLO declarado y acordado antes del primer deploy en producción. El SLO DEBE ser medido por SLI basado en telemetría real (métricas, logs). Cuando el error budget del período es consumido ≥ 80%, las nuevas features DEBEN ser pausadas en favor de trabajo de confiabilidad hasta que el budget sea recuperado.**

## Reglas

### 1. SLO declarado antes del go-live

Cada servicio nuevo de criticidad tier-1 o tier-2 tiene, en el repositorio:

```yaml
# docs/slo/{service}.yaml
service: refund-api
tier: 1
slos:
  - name: availability
    sli: "successful_http_requests / total_http_requests (excluding 4xx validation errors)"
    objective: 99.9%
    window: 30d
    error_budget_policy: "pause features if ≥80% consumed"
  - name: latency_p99
    sli: "http_request_duration_seconds{quantile=0.99} p99 in production"
    objective: 300ms
    window: 30d
  - name: freshness (for async processors)
    sli: "event_processing_lag_seconds"
    objective: "< 60s at p95"
    window: 7d
owners:
  - team: platform-payments
    escalation: "@payments-oncall"
```

### 2. SLI basado en telemetría real

El SLI **DEBE**:
- Ser medible en producción vía métrica existente o creada para ello.
- Reflejar la experiencia del usuario (los usuarios reclaman de 5xx y latencia, no de CPU interno).
- Excluir causas no relacionadas al servicio (ej.: 401 por credencial del cliente no cuenta contra disponibilidad).

### 3. Error budget como moneda

Para cada SLO:

- **Error budget** = 1 - SLO × window. Ej.: 99.9% en 30d → 43.2 minutos de downtime permitidos.
- **Consumido en tiempo real** vía dashboard dedicado.
- **≥ 80% consumido** → pausar nuevas features para ese servicio; priorizar confiabilidad (pruebas caóticas, refuerzo de retry, fix de bugs recurrentes).
- **100% consumido** = SLO violado en el período → post-mortem obligatorio; puede activar rollback de features recientes.

### 4. Revisión trimestral

El SLO no está esculpido en piedra:

- **Revisar trimestralmente** con stakeholders (producto, ingeniería, eventualmente cliente).
- Si SLO crónico (budget consumido > 3 períodos seguidos) → relajar SLO o invertir en reliability estructural.
- Si budget queda en cero crónicamente (nunca consume) → apretar SLO (el cliente merece más).

### 5. Tiers

| Tier | Criterio | SLO típico | Error budget |
|---|---|---|---|
| 1 | Ingreso directo, seguridad crítica (pago, auth) | 99.9%+ | 43min/mes |
| 2 | Importante (dashboards operacionales, integraciones externas) | 99.5% | 3.6h/mes |
| 3 | Business-hours (BFF interno, admin tools) | 99% | 7h/mes |
| 4 | Interno best-effort (experimental, interno pequeño) | opcional | — |

### 6. Dashboards y alertas derivados

Del SLO se deriva:

- **Dashboard de SLO**: gráfico de error budget a lo largo del período; forecast de agotamiento.
- **Alertas burn-rate**: disparar cuando el budget consume más rápido que linear (ej.: 2% del mes en 1h = burn rate 14x → page on-call).
- **Alertas de violación inminente**: 80% budget → warning; 100% → post-mortem.

## Alcance

- **Aplica a:** todo servicio nuevo tier-1 o tier-2; servicios existentes sin SLO tienen hasta 90 días para declarar después de que esta Lexis entre en vigor.
- **Agentes vinculados:** `warrior-hestia`, `warrior-atlas` (cuando hay infra nueva), `warrior-athena` (enforce pre-deploy).
- **Excepciones:** los servicios tier-3 y tier-4 quedan con SLO opcional; los experimentales (sandbox, prototype) quedan fuera del enforce.

## Consecuencias de Violación

1. **Sin SLO:** la discusión de priorización se vuelve política; la confiabilidad pierde frente a la novedad hasta que se rompe en el cliente.
2. **SLO ficticio:** número atractivo pero sin medición real; auditoría externa (SOC 2, ISO) detecta gap.
3. **Budget excedido ignorado:** el equipo sigue entregando features mientras la reliability se degrada; el churn del cliente crece silenciosamente.
4. **Remediación:**
   - Declarar SLO en `docs/slo/{service}.yaml` con revisión en squad.
   - Configurar dashboards (Grafana, Datadog SLO, CloudWatch).
   - Instituir ceremonia trimestral de review.

## Validación Automatizada

- **Herramienta:** scanner simple de `docs/slo/*.yaml` vs. lista de servicios declarados (puede ser en `infra/` o registry); alert si servicio tier-1/2 no tiene SLO.
- **Momento:** pre-deploy (go-live checklist); trimestral (review).
- **Métrica:** 100% de servicios tier-1/2 con SLO documentado; 0 servicios tier-1 con error budget crónicamente en cero (>3 períodos).

## Referencias

- `lex-runbook-for-every-alert` — los alertas enlazan a runbooks
- `lex-observability-required` — el SLI viene de la telemetría
- `codex-incident-response`
- `warrior-hestia`
- [Google SRE Workbook — Implementing SLOs](https://sre.google/workbook/implementing-slos/)
