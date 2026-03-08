# Lexis: Autenticación y Autorización en las APIs Guardia

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Plataforma Guardia — acceso a las APIs

## Propósito

Garantizar seguridad, rastreabilidad y conformidad regulatoria en el acceso a las APIs de la plataforma Guardia. El acceso sin autenticación y autorización estandarizadas (OAuth 2.0, modelo AAA) compromete el aislamiento, la auditoría y la adhesión a LGPD y PCI DSS.

## Ley

> **El acceso a las APIs de la plataforma Guardia DEBE ser controlado por autenticación y autorización conforme a la especificación de Autenticación y Autorización del Hub: OAuth 2.0 como estándar; APIs públicas con Client Credentials y extensiones FAPI 2.0; APIs privadas con tokens JWT emitidos por IdP confiable y control de acceso por funciones (RBAC).**

## Alcance

- **Se aplica a:** todas las APIs HTTP de la plataforma Guardia (públicas y privadas).
- **Agentes vinculados:** implementadores de APIs y consumidores que autentican.
- **Excepciones:** Ninguna para APIs que expongan recursos protegidos; endpoints públicos documentados (ej.: health) pueden ser excepción cuando justificado en ADR.

## Consecuencias de Violación

1. **Seguridad:** acceso no autorizado o no rastreable.
2. **Conformidad:** lagunas en LGPD, PCI DSS y auditoría.
3. **Remediación:** implementar OAuth 2.0 y AAA conforme a la spec; revisar accesos.

## Ejemplos

### Correcto

API pública: Client Credentials, FAPI 2.0, RBAC/ABAC, rastreabilidad; API privada: JWT de IdP confiable, RBAC, aislamiento (ej.: VPC).

### Incorrecto

API sin mecanismo de autenticación; uso de API keys sin OAuth 2.0 cuando la spec exige; APIs privadas sin JWT o sin RBAC.

## Validación Automatizada

- **Herramienta:** revisión de diseño y código; pruebas de autenticación y autorización.
- **Momento:** revisión de PR y auditoría de seguridad.
- **Métrica:** 0 APIs protegidas sin conformidad con la spec de Auth.

## Referencias

- codex-auth (engineering/platform) (engineering/platform)
- RFC 6749 (OAuth 2.0); FAPI 2.0 Security Profile
