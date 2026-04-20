# Kata: Triaje de Incidente

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Procedimiento de los primeros 15 minutos de un incidente — declarar severity, activar roles, orquestar diagnóstico inicial, decidir mitigación

## Objetivo

Al recibir un alerta (o reporte humano) de incidente en producción, ejecutar procedimiento estructurado de triaje en los primeros 15 minutos: acknowledge del alerta, declaración de severity, apertura de war room, activación de roles, diagnóstico inicial vía runbook, y decisión entre mitigación rápida (rollback/feature flag) o investigación profunda. Produce línea de tiempo inicial y comunicación estructurada.

## Cuándo Usar

- Respuesta a alerta sev-1 o sev-2 disparando al on-call
- Reporte humano de degradación significativa en producción
- Incidente de seguridad detectado (credencial filtrada, intrusión sospechosa)

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-----------|
| Señal inicial | Sí | Alerta (PagerDuty ticket), mensaje Slack, reporte humano |
| Servicio afectado | Sí | Nombre del servicio (para encontrar runbook y owner) |
| Canal de comunicación | Sí | Slack o equivalente para war room |

## Workflow

```
Progreso:
- [ ] 1. Acknowledge en <5 min
- [ ] 2. Declarar severity
- [ ] 3. Abrir war room + activar roles
- [ ] 4. Consultar runbook del alerta
- [ ] 5. Diagnóstico inicial vía dashboards/logs
- [ ] 6. Decidir mitigación vs. debug
- [ ] 7. Aplicar mitigación (si se decide) y verificar recovery
- [ ] 8. Comunicar status (interno + externo si aplica)
- [ ] 9. Entregar línea de tiempo inicial al IC
```

### Paso 1: Acknowledge en <5 min

1. Abrir el alerta en el sistema de paging (PagerDuty etc.), acknowledgment formal.
2. Registrar timestamp t+0 (cuando el alerta disparó).
3. Si el on-call está en otra task: pausar, escalar al backup si es necesario.

### Paso 2: Declarar severity

Consultar `codex-incident-response` §Severidad:

- SEV-1: producción tier-1 down O datos corruptos O >30% usuarios
- SEV-2: degradación significativa tier-1/2 O >5% usuarios
- SEV-3: parcial; workaround existe
- SEV-4: aislado; sin impacto inmediato

Declarar severity en el canal de incident (Slack) explícitamente:

```
🚨 SEV-2 declarada
Servicio: refund-api
Síntoma: p99 > 500ms sustained 5min, error rate 2%
```

### Paso 3: Abrir war room + activar roles

**SEV-1:**
- Crear Zoom/Meet dedicado (si está configurado, link automático del sistema de incidente).
- Crear canal Slack `#inc-YYYY-MM-DD-{service}-{short-desc}`.
- Activar: IC (incident commander), Technical Lead, Comms Lead, Scribe.

**SEV-2:**
- Canal Slack suficiente; war room en call opcional.
- Activar: IC + Technical Lead (el on-call puede acumular).

**SEV-3:**
- Canal Slack; el on-call acumula todos los roles.

Si el on-call es el **Hestia-spawn** (agente IA): el rol de Scribe/Comms es ideal (mantiene timeline estructurado); las decisiones quedan con humano.

### Paso 4: Consultar runbook del alerta

1. Abrir `runbook_url` del alerta (ver `lex-runbook-for-every-alert`).
2. Leer Síntomas, Impacto, Diagnóstico.
3. Compartir link en el canal:
   ```
   📘 Runbook: {url}
   ```

### Paso 5: Diagnóstico inicial

Conforme runbook:

1. **Dashboards**: abrir los links; capturar screenshots en el canal Slack con timestamps.
2. **Logs**: query estructurado en CloudWatch Logs / Datadog / Loki; filtrar por correlation_id si está disponible.
3. **Traces**: abrir APM/X-Ray; identificar operaciones lentas o fallos.
4. **Hipótesis**: listar 2-3 en orden de prevalencia conforme runbook. Marcar cuál está siendo probada.

Compartir hallazgos en el canal en tiempo real — el scribe garantiza que todo tenga timestamp.

### Paso 6: Decidir mitigación vs. debug

Conforme `codex-incident-response` §Rollback vs. forward-fix:

| Situación | Acción |
|---|---|
| Deploy reciente (< 2h) + sin migración de datos | Rollback |
| Problema en datos ya persistidos | Forward-fix |
| Causa raíz clara y fix trivial | Forward-fix rápido |
| Causa raíz oscura + impacto alto | Rollback + investigación en staging |

En duda: **rollback**. Mitigar primero, entender después.

### Paso 7: Aplicar mitigación + verificar recovery

Ejecutar acción decidida:

- **Rollback de deploy**: revert en el pipeline, confirmar vía dashboard.
- **Feature flag off**: vía sistema de flags (LaunchDarkly, Unleash).
- **Scale up**: agregar instancias si hay saturación de recursos.
- **Bloquear input malicioso**: WAF rule, rate limit.

**Verificar recovery**: esperar 5-10 min observando:
- Error rate vuelve al baseline.
- Latency p99 vuelve a lo normal.
- Alertas cesan de disparar.

Si NO recupera en 10 min → escalar severity o hipótesis errada; volver al Paso 5.

### Paso 8: Comunicar status

**Interno** (canal del incidente):
```
✅ Mitigation applied — rolling back to v1.34.2
[15:42] Error rate dropping; p99 recovering
[15:47] Stable — monitoring for 10 min before declaring resolved
```

**Externo** (si SEV-1 o SEV-2 con impacto al cliente):
- Actualizar status page en cada estado: Investigating → Identified → Monitoring → Resolved.
- El Comms Lead escribe; el IC aprueba; nadie más publica.

**Ejecutivo** (si SEV-1 o duración >1h):
- Email/Slack DM a liderazgo cada hora o en cambio de estado.

### Paso 9: Entregar línea de tiempo inicial

Antes de salir del "modo triaje" y entrar en "modo investigación":

1. Consolidar timeline estructurado en documento central:
   ```markdown
   # Timeline — {service} {date}

   | Horario (UTC) | Evento |
   |---|---|
   | 14:32 | Alert dispara — p99 > 500ms |
   | 14:35 | On-call acknowledge, SEV-2 declarada |
   | 14:38 | War room abierto |
   | ... |
   ```

2. Este documento alimenta el post-mortem (`kata-postmortem-write`).

## Salidas

| Salida | Formato | Destino |
|-------|---------|---------|
| Severity declarada + activaciones | Mensaje estructurado | Canal del incidente |
| Timeline inicial | Markdown | Documento central (Notion, Google Docs, repo) |
| Mitigación aplicada + recovery confirmado | Observación en dashboards | Print/link en el canal |
| Status page updates | Texto estructurado | statuspage.io o equivalente |

## Restricciones

- **La severity NO es opinión**: aplicar criterios de `codex-incident-response` objetivamente.
- **No se culpa durante incidente**: lenguaje factual ("el deploy X causó degradación"), nunca ("el dev Y deployó bug"). El post-mortem blameless comienza aquí.
- **El comms tiene un dueño**: el Comms Lead es el único que publica externamente; evita contradicciones.
- **La mitigación viene antes del entendimiento completo**: restaurar servicio > descubrir por qué; debug después.

## Referencias

- `codex-incident-response` — severity, roles, comms templates
- `lex-runbook-for-every-alert` — el runbook es base del Paso 4
- `lex-slo-required` — el incidente consume error budget
- `kata-postmortem-write` — procedimiento después del incidente
- `warrior-hestia`
