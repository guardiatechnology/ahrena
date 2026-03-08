# Lexis: Estructura Base de Entidades

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Plataforma Guardia — modelo de entidades

## Propósito

Garantizar que toda entidad persistente y rastreable de la plataforma Guardia siga un modelo estructural mínimo, asegurando consistencia entre servicios, interoperabilidad entre dominios y adhesión a requisitos de seguridad, rastreabilidad y conformidad (LGPD, SOC 2, ISO 27001). Las excepciones sin este estándar generan lagunas de auditoría y quiebre de interoperabilidad.

## Ley

> **Toda entidad persistente y rastreable de la plataforma Guardia DEBE seguir la estructura base definida en la especificación de Entidades del Hub y referenciada en el Codex de entidades (entity_id, entity_type, version, history, created_at, updated_at, discarded_at y demás propiedades obligatorias).**

## Alcance

- **Se aplica a:** modelado y exposición de entidades en APIs, bases de datos, eventos de dominio e integraciones de la plataforma Guardia.
- **Agentes vinculados:** todos los agentes e implementadores que creen o alteren entidades en la plataforma.
- **Excepciones:** Solo cuando estén justificadas y aprobadas por el Comité Directivo y registradas en un Registro de Decisión de Producto (PDR).

## Consecuencias de Violación

1. **Inconsistencia:** los servicios y consumidores no pueden asumir la estructura mínima de las entidades.
2. **Auditoría:** lagunas en rastreabilidad e historial comprometen la conformidad.
3. **Remediación:** las entidades fuera del estándar deben ser migradas o documentadas en PDR antes de ser aceptadas.

## Ejemplos

### Correcto

Entidad con entity_id (UUID v7), entity_type, created_at, updated_at, version y demás propiedades de la spec; history omitido en respuestas temporales; endpoint de historial disponible cuando aplique.

### Incorrecto

Recurso de API o evento que represente entidad persistente sin entity_id, sin version o sin timestamps (created_at/updated_at) conforme a la especificación de Entidades.

## Validação Automatizada

- **Herramienta:** revisión de diseño y código contra codex-entities; validación de contrato (OpenAPI/schema) cuando esté disponible.
- **Momento:** revisión de PR y diseño de nuevos recursos.
- **Métrica:** 0 entidades persistentes fuera de la estructura base, salvo excepciones documentadas en PDR.

## Referencias

- codex-entities (engineering/platform) (engineering/platform)
- RFC 9562 (UUID v7), RFC 7386 (JSON Merge Patch), RFC 3339 (timestamps)
