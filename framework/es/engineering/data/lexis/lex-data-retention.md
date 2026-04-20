# Lexis: Política de Retención de Datos

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Almacenamiento persistente de datos personales, transaccionales, logs y artefactos — política de retención definida por clase y enforced

## Propósito

Los datos se acumulan indefinidamente cuando nadie define cuándo borrar. Los buckets S3 crecen a TB, las tablas quedan con años de rows huérfanas, los logs de acceso mantienen histórico que viola regulación (LGPD derecho al olvido, GDPR storage limitation). El costo crece, la performance se degrada, el riesgo legal sube silenciosamente.

Esta Lexis existe para garantizar que **toda clase de dato tenga política de retención declarada antes del primer almacenamiento**, que **purges automáticos sean configurados** y que **el compliance legal (LGPD, GDPR) sea respetado** — incluyendo el derecho al olvido del titular de los datos.

## Ley

> **Toda clase de dato persistente DEBE tener política de retención declarada en `docs/data-retention.yaml` con valor, justificación legal/negocio, y mecanismo de enforcement. Los datos personales DEBEN ser eliminables por solicitud del titular (LGPD Art. 18 / GDPR Art. 17) dentro del plazo legal. Los logs que contienen PII DEBEN tener retención específica, nunca `indefinite`.**

## Reglas

### 1. Política declarada por clase

Estructura en `docs/data-retention.yaml`:

```yaml
classes:
  - name: transactional-core
    description: "Transacciones de pago, refunds, ledger"
    retention: "7 years"
    legal_basis: "Lei 12.846/2013 (BR), SOX 17 CFR 240.17a-4 (if US)"
    storage: "Postgres primary; S3 Glacier after 1y for archive"
    enforcement: "postgres lifecycle job + S3 lifecycle policy"
    
  - name: pii-customer
    description: "Nombre, CPF, email, teléfono del cliente"
    retention: "while active + 5 years after last transaction"
    legal_basis: "LGPD Art. 16 — tratamiento durante necesidad + defensa de derechos"
    deletion_policy: "upon user request OR auto after 5y inactivity"
    erasure_sla: "15 days from request (LGPD)"
    storage: "Postgres customer schema"
    
  - name: operational-logs
    description: "Logs de aplicación sin PII"
    retention: "90 days"
    storage: "CloudWatch Logs"
    
  - name: audit-logs
    description: "CloudTrail, application audit logs"
    retention: "7 years (SOC 2 / SOX)"
    storage: "S3 bucket inmutable (Object Lock)"
    
  - name: cache
    description: "Redis / Memcached"
    retention: "ephemeral, TTL 24h default"
    storage: "ElastiCache"
```

### 2. Enforcement automatizado

Para cada clase, **DEBE** existir mecanismo automático de expiración:

- **Postgres**: `DELETE ... WHERE created_at < NOW() - INTERVAL 'X'` en cron/job.
- **S3**: Lifecycle policy con transición y expiration.
- **CloudWatch Logs**: `retentionInDays` en el log group.
- **Redis**: TTL por key.

Retención sin enforcement es política de estante.

### 3. Derecho al olvido (LGPD / GDPR)

El sistema **DEBE** soportar, para datos personales:

- **Exportación** (LGPD Art. 18 inciso VI): formato estructurado (JSON) consumible.
- **Exclusión** (LGPD Art. 18 inciso VI): anonimización o hard delete.
  - Si borrar viola otro requisito (ej.: el ledger necesita permanecer): anonimizar PII manteniendo estructura transaccional.
- **SLA**: respetado en todas las fuentes (DB, backups de largo plazo, logs, analytics, cachés).

La exclusión en backups es compleja: documentar política (ej.: "PII en backup está cifrado; las llaves se destruyen en la expiración del backup") con legal.

### 4. Retención de PII en logs

Los logs **DEBEN** no contener PII cuando sea posible (ver `lex-observability-required`). Si contienen:
- Retención máxima: 90 días (o el plazo legal más corto aplicable).
- Redaction aplicada antes de persistir cuando sea viable.

Los logs en sistemas de terceros (Datadog, Splunk) siguen la misma regla.

### 5. Sin `retention: indefinite` sin justificación

Categoría válida solo para:
- **Audit logs exigidos por ley** (SOX 7 años es "indefinite" desde el punto de vista de la app).
- **Datos de sistema** sin PII y con costo controlado (config, feature flags history).

Todo otro caso exige justificación legal/negocio explícita.

### 6. Auditoría trimestral

Trimestralmente:
- Verificar que el enforcement funcionó (muestras borradas en el plazo).
- Revisar crecimiento de cada clase (storage = costo).
- Revalidar legal basis (cambios en LGPD, contratos, políticas internas).

## Alcance

- **Aplica a:** todo sistema que persiste datos más allá de memoria de proceso.
- **Agentes vinculados:** `warrior-demeter` (diseño), `warrior-atlas` (S3/RDS lifecycle), `warrior-apollo`/`warrior-hephaestus` (implementación de endpoints de exportación/exclusión).
- **Excepciones:** Ninguna. El sandbox puede tener retención más corta; el compliance legal es universal.

## Consecuencias de Violación

1. **Multa LGPD:** hasta 2% de la facturación por no respetar el derecho al olvido.
2. **Costo explotando:** TB acumulados en S3 Standard sin lifecycle; la cuenta mensual crece.
3. **Performance degradada:** tablas con años de rows huérfanas vuelven queries lentas, backups pesados.
4. **Remediación:**
   - Inventario de clases de dato → `docs/data-retention.yaml`.
   - Configurar enforcement (lifecycle policies, cron jobs).
   - Implementar endpoints de exportación/exclusión.
   - Auditoría trimestral en calendario.

## Validación Automatizada

- **Herramienta:**
  - Linter valida que `docs/data-retention.yaml` existe y lista todas las clases declaradas en schema de DB.
  - Check mensual: tamaño de cada clase vs. crecimiento esperado.
  - Prueba end-to-end: crear usuario sintético, solicitar exclusión, verificar remoción en todas las fuentes dentro del SLA.
- **Momento:** pre-deploy de nuevo dominio de dato; mensual/trimestral.
- **Métrica:** 100% de clases documentadas; 100% de solicitudes de exclusión dentro del SLA; crecimiento mensual compatible con baseline.

## Referencias

- `codex-data-modeling`
- `lex-aws-cost` — la retención impacta el costo AWS
- `warrior-demeter`
- [LGPD Art. 16 y 18](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [GDPR Art. 17 (right to erasure)](https://gdpr-info.eu/art-17-gdpr/)
