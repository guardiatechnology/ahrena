# Lexis: Migraciones Reversibles o con Plan de Rollback

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Migraciones de schema de base de datos (relacional o NoSQL) en cualquier ambiente persistente

## Propósito

Las migraciones sin rollback se vuelven bombas de tiempo: cuando el deploy correspondiente falla o retrocede, el schema avanzó pero el código anterior ya no entiende. El equipo queda atrapado — puede solo avanzar, nunca retroceder. Peor: migraciones destructivas (DROP COLUMN, DROP TABLE) sin backup o plan detallado pueden borrar datos irrecuperables en minutos.

Esta Lexis existe para garantizar que **toda migración sea reversible automáticamente** (vía `down` en Alembic, `migrate:rollback` en Django etc.) **O tenga plan de rollback manual documentado** con verificación de backup antes de cualquier cambio destructivo.

## Ley

> **Toda migración de schema DEBE ser reversible automáticamente por el framework de migraciones O tener plan de rollback manual documentado y probado. Las migraciones destructivas (DROP, ALTER que pierde datos) DEBEN tener backup validado en las 24h anteriores y ventana de mantenimiento declarada. Los deploys de código DEBEN ser compatibles con schema anterior Y nuevo (expand-contract) en sistemas con rolling deploy.**

## Reglas

### 1. Reversibilidad automática por default

Las migraciones aditivas (CREATE TABLE, ADD COLUMN NULLABLE, CREATE INDEX CONCURRENTLY) **DEBEN** tener `down` implementado:

```python
# Alembic
def upgrade():
    op.add_column("refund", sa.Column("notes", sa.String(500), nullable=True))

def downgrade():
    op.drop_column("refund", "notes")
```

Si el framework de migraciones genera `down` automáticamente, aceptar; si no, escribir manualmente.

### 2. Migraciones destructivas: plan + backup

Para `DROP TABLE`, `DROP COLUMN`, `ALTER TYPE` con loss of data, `RENAME` en producción:

1. **Backup point-in-time** confirmado en las últimas 24h (vía AWS Backup, pg_dump, etc.).
2. **Ventana de mantenimiento** declarada con stakeholders cuando tier-1.
3. **Plan de rollback manual** escrito:
   - Cómo restaurar a partir del backup.
   - Cuánto tiempo toma.
   - Cuál es el punto sin retorno (after this, rollback is only via restore-from-backup).
4. **Prueba en staging** con volumen representativo, midiendo duración.

### 3. Expand-Contract para rolling deploys

Cuando el sistema usa rolling deploy (N pods, deploy gradual):

- **Fase Expand**: migration agrega estructura nueva manteniendo la antigua. Deploy de código usa ambas.
- **Fase Contract**: migration remueve estructura antigua. Deploy usa solo la nueva.

Ej.: renombrar columna `status` → `state`:

| Paso | Migration | Código |
|---|---|---|
| 1 (expand) | `ADD COLUMN state` + trigger copia `status` → `state` | Lee de `state`, escribe en `state` Y `status` |
| 2 | — | Lee y escribe solo en `state` |
| 3 (contract) | `DROP COLUMN status` + trigger | — |

Un deploy atómico que cambia schema + código simultáneamente **se rompe** en rolling deploy.

### 4. Migraciones de larga duración requieren estrategia

Los queries que escanean tablas grandes (> 1M rows) pueden bloquear:

- `ADD COLUMN NOT NULL DEFAULT 'x'` en PostgreSQL bloquea tabla → usar `ADD COLUMN` nullable, backfill en batches, después `SET NOT NULL`.
- `CREATE INDEX` sin `CONCURRENTLY` bloquea writes → siempre usar `CONCURRENTLY` (fuera de transacción).
- `ALTER COLUMN TYPE` (con rewrite) en tabla grande → evaluar pg_repack, tablas shadow, o aceptar ventana.

Migration larga **DEBE** declarar estimación de duración y estrategia en comentario al inicio.

### 5. Sin DDL en transacción compartida con DML

Nunca poner DDL (CREATE, ALTER) y DML (INSERT, UPDATE) masivo en la misma migration. El DDL puede ser reversible; el DML de datos reales exige plan separado.

### 6. Prueba de restore periódica

Backup sin prueba de restore es backup inútil. **Trimestralmente** (o por SOX/SOC 2):
- Ejecutar restore en ambiente de staging a partir de backup de producción.
- Medir tiempo; validar datos.
- Si falla → P0; backup strategy quebrado.

## Alcance

- **Aplica a:** toda migración en ambiente compartido (staging, producción). Sandbox personal queda fuera del enforce.
- **Agentes vinculados:** `warrior-demeter`, `warrior-apollo` (cuando escribe migration), `warrior-atlas` (cuando configura backup).
- **Excepciones:** Ninguna. Las migraciones en sandbox deben aún seguir la estructura incluso sin enforcement.

## Consecuencias de Violación

1. **Lock inesperado en producción:** tabla bloqueada 30min en horario pico → downtime visible al cliente.
2. **Pérdida de datos:** `DROP COLUMN` sin backup o con backup viejo → datos irrecuperables.
3. **Deploy irreversible:** feature deploy se rompe, pero el schema avanzó; no hay cómo retroceder; fix emergencial.
4. **Remediación:**
   - Audit trail: `pg_locks`, CloudTrail, logs del migration tool.
   - Restore de backup si hay datos perdidos.
   - Post-mortem blameless (`kata-postmortem-write`).
   - Acción correctiva: checklist en PR de migration; approval automatizado bloquea hasta checklist completo.

## Validación Automatizada

- **Herramienta:**
  - Lint en migrations (ej.: `squawk` para PostgreSQL): detecta patterns peligrosos (`ADD COLUMN NOT NULL DEFAULT`, `CREATE INDEX` sin CONCURRENTLY).
  - Check en PR de que `down` está implementado en toda migration.
  - Test run en CI: `upgrade` + `downgrade` en test DB.
- **Momento:** en cada PR que contiene migration; trimestral (restore test).
- **Métrica:** 100% de migrations con `down` o plan documentado; 0 `ADD COLUMN NOT NULL DEFAULT` en tablas > 10k rows sin estrategia multi-step.

## Referencias

- `codex-data-modeling` — patrones de diseño previo
- `codex-migrations-strategy` — playbooks detallados
- `warrior-demeter` — conduce migraciones complejas
- [Safer ActiveRecord Migrations](https://github.com/ankane/strong_migrations)
- [Alembic Best Practices](https://alembic.sqlalchemy.org/en/latest/tutorial.html#running-our-first-migration)
