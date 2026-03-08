# Codex: Modelo de Entidades de la Plataforma Guardia

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Plataforma Guardia — estructura base de entidades

## Visión General

Este Codex describe el modelo estructural mínimo que todas las entidades de la plataforma Guardia deben seguir. Objetiva consistencia entre servicios, interoperabilidad entre dominios y adhesión a requisitos de seguridad, rastreabilidad y conformidad (Compliance by Design). Se aplica a APIs, bases de datos, eventos de dominio e integraciones externas.

## Contexto

- **Dominio:** modelo de entidades persistentes y rastreables de la plataforma Guardia.
- **Público objetivo:** implementadores, arquitectos y agentes de IA que modelan o consumen entidades.
- **Actualización:** cuando la especificación de Entidades en el Hub sea alterada o cuando un PDR apruebe una excepción.

## Contenido

### Estructura base obligatoria

| Propiedad | Tipo | Obligatorio | Descripción |
|-----------|------|-------------|-------------|
| entity_id | UUID v7 | Sí | Identificador único de la entidad, inmutable, generado por el sistema. RFC 9562 (ordenación temporal). |
| entity_type | string | Sí | Tipo de entidad; debe pertenecer a lista controlada conocida por el sistema. |
| external_entity_id | string | No | Identificador en sistema externo; máx. 36 caracteres; único por entity_type cuando esté presente. |
| created_at | datetime | Sí | Fecha y hora de creación en UTC (RFC 3339); generado en la creación; no alterable. |
| updated_at | datetime | Sí | Fecha y hora de la última actualización en UTC; actualizado en cada modificación; en la creación = created_at; en el descarte = discarded_at. |
| discarded_at | datetime | No | Soft delete; cuando esté rellenado, la entidad permanece para rastreabilidad. |
| metadata | JSON Object | No | Claves y valores string; ideal ≤ 4KB, máx. 10KB; actualizaciones vía JSON Merge Patch (RFC 7386); no contener datos sensibles sin previsión legal. |
| version | integer | Sí | Inicia en 1; incrementado con updated_at; nunca reiniciado (incluso tras restauración). Conflicto de versión: gana la última. |
| history | array | No | Snapshots de versiones anteriores; últimas 10 versiones, hasta 365 días; auditoría y rollback. Omitido en respuestas temporales y eventos; disponible en endpoint api/v1/<entity_type>/<entity_id>/history. |

### Principios

1. **Identificación única:** entity_id UUID v7 garantiza unicidad global y ordenación temporal.
2. **Rastreabilidad temporal:** created_at, updated_at y discarded_at permiten auditoría y sincronización.
3. **Integridad y concurrencia:** version permite control de concurrencia y detección de conflictos.
4. **Historial y reversibilidad:** history preserva las últimas versiones para auditoría y rollback.
5. **Interoperabilidad:** external_entity_id y metadata permiten integración con sistemas externos.

### Cuándo aplicar

Este modelo DEBE adoptarse siempre que:

- Se modele un nuevo recurso de dominio;
- Se expongan APIs interna o externamente;
- Se generen eventos de dominio;
- Los datos requieran unicidad, rastreabilidad, reversibilidad o interoperabilidad.

Las excepciones DEBEN ser justificadas y aprobadas por el Comité Directivo y registradas en PDR.

### Restricciones técnicas

- entity_id: UUID v7 (RFC 9562).
- Timestamps: UTC, RFC 3339.
- metadata: solo clave y valor string; actualización vía JSON Merge Patch (RFC 7386).
- history: omitido de create/update/delete/get por defecto; proporcionado solo en el endpoint de historial.

## Glosario

| Término | Definición |
|---------|------------|
| entity_id | Identificador único global de la entidad (UUID v7). |
| entity_type | Tipo catalogado de la entidad en el sistema. |
| soft delete | Descarte lógico vía discarded_at; la entidad se mantiene para rastreabilidad. |
| history | Array de snapshots de versiones anteriores para auditoría. |

## Referencias

- [Especificación de Entidades — Hub Guardia](https://hub.guardia.finance/docs/specifications/entities/)
- RFC 9562: UUID Version 7
- RFC 7386: JSON Merge Patch
- RFC 3339: Date and Time on the Internet: Timestamps
