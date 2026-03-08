# Codex: Autenticación y Autorización en la Plataforma Guardia

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Plataforma Guardia — acceso a las APIs

## Visión General

Este Codex describe los modelos de autenticación y autorización adoptados por la plataforma Guardia para garantizar seguridad, rastreabilidad y conformidad en el acceso a las APIs. Basado en OAuth 2.0 y en el modelo AAA (Authentication, Authorization, Accounting).

## Contexto

- **Dominio:** autenticación y autorización para APIs HTTP de la plataforma Guardia.
- **Público objetivo:** implementadores de APIs e integradores.
- **Actualización:** cuando la especificación de Auth en el Hub sea alterada.

## Contenido

### Modelo AAA (Triple A)

1. **Authentication (Autenticación):** verificación de la identidad de usuarios o sistemas por credenciales (contraseñas, certificados, tokens).
2. **Authorization (Autorización):** definición de los permisos de la identidad autenticada con base en políticas y alcances.
3. **Accounting (Responsabilización):** registro de las acciones (accesos, uso de recursos) para auditoría y rendición de cuentas.

El modelo sustenta la seguridad y la gobernanza y orienta los flujos de autenticación.

### OAuth 2.0

Protocolo adoptado como estándar para autenticación y autorización entre sistemas. Tokens emitidos por Authorization Server; flujos distintos según el tipo de API.

### APIs públicas

- **Definición:** APIs expuestas a sistemas externos (socios, integraciones, aplicaciones de terceros).
- Flujo **Client Credentials** (RFC 6749) con extensiones de seguridad del **FAPI 2.0 Security Profile**.
- Garantías: autorización granular (RBAC y ABAC), rastreabilidad de operaciones, protección contra fraudes, autenticación mutua entre cliente y servidor.

### APIs privadas

- **Definición:** APIs consumidas solo por componentes internos de la plataforma (microservicios, jobs, gateways).
- OAuth 2.0 con **tokens JWT emitidos por un IdP (Identity Provider) confiable**.
- Garantías: comunicación segura entre módulos internos, control de acceso por funciones (RBAC), aislamiento de red cuando aplique (ej.: **VPC — Virtual Private Cloud**).

### Interoperabilidad y conformidad

- Enfoque unificado permite interoperabilidad entre componentes, compatibilidad con regulaciones (LGPD, PCI DSS) y adhesión a OpenID y FAPI.

## Glosario

| Término | Definición |
|---------|------------|
| API pública | API expuesta a sistemas externos; autenticación vía Client Credentials y FAPI 2.0. |
| API privada | API consumida por componentes internos; JWT del IdP, RBAC, opcionalmente VPC. |
| VPC | Virtual Private Cloud; aislamiento de red para tráfico interno. |
| IdP | Identity Provider; emisor confiable de tokens de identidad. |

## Referencias

- [FAPI 2.0 Security Profile](https://openid.net/specs/openid-financial-api-part-2-1_0.html)
- RFC 2906 (AAA Authorization Requirements); RFC 6749 (OAuth 2.0 Authorization Framework)
