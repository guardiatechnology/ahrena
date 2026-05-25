# Lexis: Todo Alerta tiene Runbook

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Alertas de monitoreo que activan humanos (page, Slack on-call) — cada uno necesita runbook enlazado

## Propósito

Alertas sin runbook son crueldad operacional: despiertan ingenieros a las 3 de la mañana sin indicación de qué hacer. El on-call gasta tiempo descubriendo qué significa el alerta, dónde ver dashboards, qué pasos de mitigación aplicar — tiempo en el cual el incidente se agrava. Peor: alertas recurrentes sin runbook normalizan "ignorar alerta hasta que realmente se rompa", destruyendo el valor del sistema de monitoreo.

Esta Lexis existe para garantizar que **todo alerta que activa un humano tenga runbook versionado y enlazado**, que **los runbooks tengan pasos accionables**, y que **los alertas sin runbook sean silenciados o removidos hasta que tengan uno**.

## Ley

> **Todo alerta que activa un humano (page, on-call) DEBE tener runbook versionado en `docs/runbooks/{service}-{alert-name}.md`, enlazado directamente en la annotation del alerta. El runbook DEBE contener: síntomas, impacto en el usuario, diagnóstico inicial (dashboards y queries), acciones de mitigación, pasos de escalación. Los alertas sin runbook DEBEN ser silenciados o removidos.**

## Reglas

### 1. Estructura mínima del runbook

```markdown
# Runbook: {service} — {alert-name}

- **Severity:** P1 | P2 | P3
- **Owner:** team-{name} (on-call: @handle)
- **Last reviewed:** YYYY-MM-DD

## Síntomas (lo que el alerta indica)

{descripción objetiva: métrica, threshold, duración}

## Impacto en el usuario

{quién siente el problema, qué no puede hacer}

## Diagnóstico

1. Dashboard: {link}
2. Logs: `{query or link to log aggregator}`
3. Traces: {link to APM/tracing para servicio}
4. Hipótesis comunes en orden de prevalencia:
   - Hipótesis A: causa → señal típica
   - Hipótesis B: causa → señal típica

## Mitigación

### Mitigación rápida (rollback, feature flag)
1. Paso 1
2. Paso 2

### Mitigación profunda (fix real)
1. Identificar causa raíz
2. Fijar y deploy
3. Verificar recovery en los dashboards

## Escalación

Si la mitigación no resuelve en 15 min:
- Activar @team-escalation-list
- Abrir incident sev-X conforme `codex-incident-response`

## Histórico (últimos 3 incidentes relacionados)

- {link 1}
- {link 2}
- {link 3}
```

### 2. Link obligatorio en el alert config

Todo alert config (Prometheus, CloudWatch, Datadog) **DEBE** tener annotation:

```yaml
annotations:
  runbook_url: "https://github.com/guardiatechnology/{repo}/blob/main/docs/runbooks/refund-api-p99-breach.md"
  summary: "refund-api p99 > 300ms for 5 min"
```

### 3. Runbook revisado trimestralmente

Cada runbook tiene `Last reviewed: YYYY-MM-DD`:
- Si > 6 meses sin revisar → warning en CI/dashboard.
- Revisión mínima: confirmar que los links aún funcionan, hipótesis aún relevantes, dueños correctos.
- Incidente relacionado → el runbook **DEBE** ser actualizado en el post-mortem.

### 4. Alert sin runbook = silenciar o remover

Nuevo alert creado sin runbook pareado:
- Bloqueado en el PR del alert config (lint rule).
- Alerts existentes sin runbook: listados mensualmente en reporte; fix en 30 días o silenciar.

Silenciar no es solución permanente. Silenciado por >60 días → remover.

### 5. Sin alertas que nadie entienda

Regla de oro: **el on-call debe poder actuar con el runbook incluso sin tener familiaridad profunda con el servicio**. Runbook escrito para "tú dentro de 6 meses" o "el nuevo on-call".

Si el runbook requiere conocimiento tribal exclusivo, está incompleto.

## Alcance

- **Aplica a:** todo alert que page/notifica humano en cualquier canal (PagerDuty, Opsgenie, Slack on-call).
- **Agentes vinculados:** `warrior-hestia` (ownership), `warrior-atlas` (cuando configura alarmas vía IaC).
- **Excepciones:** los alerts informacionales (dashboard only, sin notification activa) quedan fuera del alcance — pero se recomienda tener documentación igualmente.

## Consecuencias de Violación

1. **El tiempo de resolución se infla:** el on-call gasta 30min descubriendo qué significa el alerta antes de actuar.
2. **Alert fatigue:** los alertas recurrentes sin runbook se vuelven ruido; la real emergency pierde urgencia.
3. **Fallo de compliance:** auditoría SOC 2 CC7.3 exige procedimientos de incident response; sin runbook, falla.
4. **Remediación:**
   - Inventario de alerts existentes; cada uno recibe ticket de runbook en 30 días.
   - Alerts críticos (P1) sin runbook: silenciar hasta documentar.
   - CI lint bloquea merge de alert config sin `runbook_url`.

## Validación Automatizada

- **Herramienta:**
  - Lint en archivos de alert config (Prometheus rules, Terraform CloudWatch): require `annotations.runbook_url`.
  - Cronjob verifica que la URL en `runbook_url` existe (no 404).
  - Dashboard: alerts activos vs. runbooks existentes → gap report.
- **Momento:** en cada PR que agrega/modifica alert; semanalmente (URL health).
- **Métrica:** 100% de alerts activos con `runbook_url` válido; 0 alerts silenciados hace > 60 días sin deleción.

## Referencias

- `lex-slo-required` — los burn-rate alerts derivados de SLO necesitan runbook igual
- `lex-observability-required`
- `codex-incident-response` — procedimientos mayores; el runbook es el paso inicial
- `warrior-hestia`
- [Google SRE Book — Effective Alerting](https://sre.google/sre-book/monitoring-distributed-systems/)
