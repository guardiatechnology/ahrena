# Codex: Modelo de Entidades de la Plataforma Guardia

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Plataforma Guardia — estructura base de entidades

## Visión General

Esta especificación define el modelo estructural mínimo que todas las entidades de la plataforma Guardia DEBEN seguir. El objetivo es garantizar consistencia entre servicios, interoperabilidad entre dominios y adhesión a requisitos de seguridad, rastreabilidad y conformidad desde el diseño.

Esta estructura base se aplica a cualquier objeto persistente y rastreable de la plataforma, abarcando APIs, bases de datos, eventos de dominio, integraciones externas y demás mecanismos de representación de entidades.

Al adoptar este estándar, toda entidad:

- Posee un identificador único y global;
- Es versionada con control explícito de cambios;
- Mantiene historial completo y auditable;
- Puede integrarse y eventualmente descartarse sin pérdida de rastreabilidad.

La aplicación de esta estructura reduce inconsistencias, facilita integraciones y elimina lagunas de auditoría que podrían comprometer la conformidad con normas como **LGPD**, **SOC 2** e **ISO 27001**.

Además, el modelo refuerza los principios de **Compliance by Design**, asegurando:

- Identificación única (`entity_id`);
- Rastreabilidad temporal (`created_at`, `updated_at`, `discarded_at`);
- Integridad y control de concurrencia (`version`);
- Preservación de historial y reversibilidad (`history`);
- Integración e interoperabilidad con sistemas externos (`external_entity_id`, `metadata`).

## Contexto

- **Dominio:** modelo de entidades persistentes y rastreables de la plataforma Guardia.
- **Público objetivo:** implementadores, arquitectos y agentes de IA que modelan o consumen entidades.
- **Actualización:** cuando la especificación de Entidades sea alterada o cuando un PDR apruebe excepción.

## Contenido

### Estructura base

La estructura base de una entidad en Guardia DEBE contener las siguientes propiedades:

| Propiedad | Tipo | Obligatorio | Descripción |
|-----------|------|-------------|-------------|
| entity_id | {entity_id_prefix}:{uuid_v7} | Sí | Identificador único de la entidad. El prefijo es una cadena alfanumérica en minúsculas de 2–5 chars definida antes del desarrollo; UUID v7 garantiza ordenación temporal. |
| entity_type | string (UPPER_SNAKE_CASE) | Sí | Tipo de entidad. Siempre UPPER_SNAKE_CASE (ej.: `TRANSACTION`). |
| external_entity_id | string | No | Identificador único de la entidad en un sistema externo. |
| created_at | datetime | Sí | Fecha y hora de creación de la entidad. |
| updated_at | datetime | Sí | Fecha y hora de la última actualización de la entidad. |
| discarded_at | datetime | No | Fecha y hora de descarte de la entidad. |
| metadata | JSON Object | No | Metadatos de la entidad. |
| version | integer | Sí | Versión de la entidad. |
| history | array | No | Historial de versiones de la entidad. |

### Propiedades detalladas

#### entity_id

- DEBE formatearse como `{entity_id_prefix}:{uuid_v7}` donde:
  - `entity_id_prefix` es una cadena alfanumérica en minúsculas de 2–5 caracteres definida antes del inicio del desarrollo (ej.: `txn`, `rec`, `org`, `per`, `doc`).
  - `uuid_v7` implementa UUID v7 conforme a la [RFC 9562](https://datatracker.ietf.org/doc/html/rfc9562#name-uuid-version-7), asegurando ordenación temporal.
- DEBE ser único, inmutable y generado por el sistema.
- El prefijo DEBE declararse en el documento de diseño de la entidad antes de comenzar la codificación. Cambiarlo es un cambio breaking que requiere ADR.

#### entity_type

- DEBE usar UPPER_SNAKE_CASE (ej.: `TRANSACTION`, `SCHEDULED_TRANSFER`, `LEDGER_ENTRY`).
- DEBE pertenecer a una lista controlada de entidades conocidas por el sistema.
- La forma en minúsculas se usa solo en segmentos `type` de CloudEvents y segmentos de path de URL — ver `lex-entity-naming`.

#### Nomenclatura del campo de identificador

Al referenciar una entidad por su identificador en el payload JSON de otra entidad:
- Usar `{entity_name}_id`, donde `{entity_name}` es la forma en minúsculas de `entity_type`.
- Ejemplo: una referencia a una entidad `TRANSACTION` usa el campo `transaction_id`.
- El sufijo `_entity_id` está PROHIBIDO: nunca usar `transaction_entity_id`.
- Excepción: dentro del propio payload de la entidad, el campo de identificador canónico es siempre `entity_id`.

#### external_entity_id

- PUEDE ser nulo.
- DEBE tener como máximo 36 caracteres.
- CUANDO esté presente, DEBE ser único dentro del `entity_type`.
- Ideal para referencias cruzadas con sistemas legacy o externos.

#### created_at

- DEBE ser un datetime en UTC formateado conforme a la [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339).
- DEBE generarse automáticamente en la creación.
- NO PUEDE alterarse tras la creación.

#### updated_at

- DEBE ser un datetime en UTC formateado conforme a la [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339).
- DEBE actualizarse en cada modificación persistente.
- En la creación, DEBE asumir el mismo valor que `created_at`.
- En el descarte, DEBE asumir el mismo valor que `discarded_at`.
- Utilizado para control de concurrencia y sincronización.

#### discarded_at

- DEBE ser un datetime en UTC formateado conforme a la [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339).
- PUEDE ser nulo.
- Cuando esté rellenado, indica soft delete. La entidad permanece en el sistema para fines de rastreabilidad.

#### metadata

- DEBE ser un JSON Object.
- Clave y valor DEBEN ser strings.
- DEBE seguir el tamaño ideal de 4KB siempre que sea posible y NO DEBE superar 10KB.
- Las actualizaciones DEBEN hacerse vía JSON Merge Patch [RFC 7386](https://datatracker.ietf.org/doc/html/rfc7386).
- NO DEBE contener datos sensibles o personales sin previsión legal.
- Los valores PUEDEN almacenarse cifrados, con impacto en el rendimiento.

#### version

- Inicializa en 1 y se incrementa automáticamente junto con `updated_at`.
- NUNCA se reinicia, ni siquiera tras restauración de entidad descartada.
- En caso de conflicto de versión, se preserva la última versión, descartando la que confligió.

#### history

- Almacena snapshots de versiones anteriores.
- Utilizado para auditoría, rollback e investigación.
- Por defecto, almacena las últimas 10 versiones más recientes hasta 365 días.
- El historial DEBE omitirse de las respuestas temporales (create, update, delete y get).
- DEBE omitirse de los eventos de dominio.
- El historial DEBE proporcionarse en las respuestas de lectura (get) cuando lo solicite el cliente en el endpoint `api/v1/<entity_type>/<entity_id>/history`.
- El endpoint de historial devuelve una lista de hasta 10 registros históricos de la misma entidad.
- Los valores PUEDEN almacenarse cifrados, con impacto en el rendimiento.

### Cuándo aplicar

Este modelo DEBE adoptarse siempre que:

- Se modele un nuevo recurso de dominio;
- Se expongan APIs interna o externamente;
- Se generen eventos de dominio;
- Los datos requieran unicidad, rastreabilidad, reversibilidad o interoperabilidad.

**IMPORTANTE:** Las excepciones DEBEN estar justificadas y aprobadas por el Comité Directivo y registradas en un Registro de Decisión de Producto (PDR).

## Glosario

| Término | Definición |
|---------|------------|
| entity_id | Identificador único global de la entidad (formato `{entity_id_prefix}:{uuid_v7}`). |
| entity_type | Tipo catalogado de la entidad en el sistema; siempre UPPER_SNAKE_CASE. |
| soft delete | Descarte lógico vía discarded_at; la entidad se mantiene para rastreabilidad. |
| history | Array de snapshots de versiones anteriores para auditoría. |

## Referencias

- [RFC 3339: Date and Time on the Internet: Timestamps](https://datatracker.ietf.org/doc/html/rfc3339)
- [RFC 7386: JSON Merge Patch](https://datatracker.ietf.org/doc/html/rfc7386)
- [RFC 9562: UUID Version 7](https://datatracker.ietf.org/doc/html/rfc9562)
