# Codex: Modelado de Datos

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Patrones de modelado de datos para persistencia — entidades, value objects, aggregates, normalización, evolución de schema, elección entre relacional y NoSQL

## Visión general

Este Codex es la referencia para **decisiones de modelado de datos** en proyectos Ahrena. Consultado por `warrior-demeter` al diseñar schema nuevo, por `warrior-apollo` cuando necesita decidir estructura de tabla, y por `warrior-atlas` cuando elige entre RDS, Aurora, DynamoDB.

## Contexto

- **Dominio:** diseño de modelo de datos — relacional, NoSQL, mixtos
- **Público objetivo:** `warrior-demeter`, agentes que persisten datos, revisores de PR con migrations
- **Actualización:** cuando los patrones de DDD evolucionan, se adoptan nuevos servicios de DB, o cuando la regulación cambia (LGPD, GDPR)

## Contenido

### Entidad vs. Value Object vs. Aggregate

**Entidad**: tiene identidad única (`entity_id`), cambia a lo largo del tiempo.
- Ej.: `User`, `Refund`, `Account`.
- Tiene primary key; participa de FKs.

**Value Object**: inmutable, definido por sus valores.
- Ej.: `Money(amount, currency)`, `Address`, `Email`.
- Stored as embedded columns (`amount_cents` + `currency_code`) o JSON.

**Aggregate**: boundary de consistencia transaccional.
- Ej.: `Order` (raíz) con `OrderItems`.
- Cambios a partir de aggregate root; invariantes mantenidas juntas.
- Mapeo natural para transacción de DB.

Regla: preferir **aggregates pequeños** — un aggregate grande reduce concurrencia.

### Base de atributos en entidad Ahrena

Toda entidad persistente sigue `codex-entities`:

| Campo | Tipo | Propósito |
|---|---|---|
| `entity_id` | UUID v4 | Identificador estable (nunca reusar) |
| `entity_type` | string | Polimorfismo y auditoría |
| `version` | int | Optimistic locking; incrementa en cada update |
| `created_at` | timestamp | Inmutable después del create |
| `updated_at` | timestamp | Actualizado en cada cambio |
| `created_by` | UUID (ref user) | Actor que creó |
| `updated_by` | UUID (ref user) | Actor del último cambio |

Deleción lógica: campo `discarded_at` (timestamp nullable) en vez de DELETE físico, excepto cuando compliance exige purge.

### Normalización — cuándo y cuánto

- **3NF** como default para OLTP: evita inconsistencia, facilita UPDATE.
- **Desnormalización selectiva** para read paths críticos:
  - Contadores (`total_refunds`) materializados con trigger o job.
  - Vistas materializadas para reports.
  - Caché (Redis) para lookups frecuentes.
- **OLAP**: snowflake/star schema; diferente del OLTP.
- **Avoid**: campos CSV en string, arrays abusivos, JSON donde una columna explícita cabría.

### Relacional vs. NoSQL

**Relacional (Postgres, Aurora) cuando:**
- Transacciones ACID sobre múltiples entidades.
- Queries ad-hoc con JOINs.
- Consistencia fuerte es requisito.
- El dominio tiene relaciones complejas.

**DynamoDB cuando:**
- Access patterns conocidos y estables.
- Escala masiva y predecible.
- Latencia sub-10ms exigida.
- El dominio es clave-valor o jerárquico simple.

**DocumentDB / MongoDB cuando:**
- Schema evoluciona rápidamente (documentos flexibles).
- Datos agregados por naturaleza (un doc contiene el aggregate).
- Queries flexibles sobre documentos.

**Time-series DB (Timestream, InfluxDB) cuando:**
- Append-heavy, queries por ventana temporal.
- Métricas, eventos, IoT.

Documentar la elección en ADR (`kata-adr-write`) cuando no es trivial.

### Índices

- **Toda FK** tiene índice (a menos que haya prueba de que nunca se usa en query).
- **Queries frecuentes** definen índices compuestos; analizar `EXPLAIN`.
- **Índices en timestamps** para ranges (`created_at DESC`).
- **Índices parciales** para consultas filtradas (`WHERE status = 'active'`).
- **Límite**: 5-7 índices por tabla grande. Cada índice cuesta en writes.

Revisar índices trimestralmente: `pg_stat_user_indexes` para detectar no usados.

### Migrations (expand-contract)

Ver `lex-migrations-reversible`. Patrón típico:

1. **Expand**: ADD COLUMN nullable + código escribe en ambos (nuevo + viejo).
2. **Backfill**: job migra datos históricos en batches.
3. **Cut-over**: código pasa a leer solo del nuevo.
4. **Contract**: DROP COLUMN antiguo.

Migration destructiva sin ese patrón = downtime.

### Particionamiento

Cuando la tabla llega a ~100M+ rows o contiene series temporales largas:

- **Range partitioning** por `created_at` (month/year): queries recientes rápidas; archivo antiguo en particiones separadas.
- **Hash partitioning** por `tenant_id`: multi-tenant isolation.
- **List partitioning** por categoría cerrada.

Postgres Partitioning nativo > particionamiento en application layer.

### Soft delete vs. hard delete

**Soft delete** (`discarded_at` timestamp):
- Preserva histórico.
- Permite undo.
- Complica queries (todo WHERE filtra `discarded_at IS NULL`).

**Hard delete** (DELETE físico):
- Obligatorio para datos sujetos a LGPD con deletion request.
- Exige plan de auditoría (CloudTrail, audit log separado).

Elegir en función del dominio — documentar decisión.

### Eventual consistency

En sistemas distribuidos (CQRS, event sourcing, multi-region):

- Aceptar que el read model queda eventualmente consistente.
- Declarar **consistency guarantees** por use case (¿read-after-write en la misma cuenta? ¿o es aceptable leer versión anterior por algunos segundos?).
- Evitar mix sin intención: transacción escribe y evento es leído sync → riesgo de race.

### LGPD / GDPR desde el diseño

- **Clasificar datos** al crear tabla: ¿qué columna contiene PII?
- **Minimizar**: solo persistir lo necesario.
- **Cifrar en reposo** (default vía KMS en RDS/Aurora).
- **Acceso auditado**: queries sobre PII logged.
- **Retención**: declarada en `docs/data-retention.yaml` (`lex-data-retention`).
- **Exportación y exclusión**: endpoints listos desde el día 1.

## Referencias

- `lex-migrations-reversible`, `lex-data-retention`
- `codex-entities` — base de entidades Ahrena
- `codex-migrations-strategy` — playbooks de migration
- `warrior-demeter`
- [Domain-Driven Design (Eric Evans)](https://www.domainlanguage.com/ddd/)
- [PostgreSQL Indexes](https://www.postgresql.org/docs/current/indexes.html)
