# Codex: Autenticação e Autorização na Plataforma Guardia

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Plataforma Guardia — acesso às APIs

## Visão Geral

Este Codex descreve os modelos de autenticação e autorização adotados pela plataforma Guardia para garantir segurança, rastreabilidade e conformidade no acesso às APIs. Baseado em OAuth 2.0 e no modelo AAA (Authentication, Authorization, Accounting).

## Contexto

- **Domínio:** autenticação e autorização para APIs HTTP da plataforma Guardia.
- **Público-alvo:** implementadores de APIs e integradores.
- **Atualização:** quando a especificação de Auth no Hub for alterada.

## Conteúdo

### Modelo AAA (Triple A)

1. **Authentication (Autenticação):** verificação da identidade de usuários ou sistemas por credenciais (senhas, certificados, tokens).
2. **Authorization (Autorização):** definição das permissões da identidade autenticada com base em políticas e escopos.
3. **Accounting (Responsabilização):** registro das ações (acessos, uso de recursos) para auditoria e prestação de contas.

O modelo sustenta segurança e governança e orienta os fluxos de autenticação.

### OAuth 2.0

Protocolo adotado como padrão para autenticação e autorização entre sistemas. Tokens emitidos por Authorization Server; fluxos distintos conforme o tipo de API.

### APIs públicas

- **Definição:** APIs expostas a sistemas externos (parceiros, integrações, aplicações de terceiros).
- Fluxo **Client Credentials** (RFC 6749) com extensões de segurança do **FAPI 2.0 Security Profile**.
- Garantias: autorização granular (RBAC e ABAC), rastreabilidade de operações, proteção contra fraudes, autenticação mútua entre cliente e servidor.

### APIs privadas

- **Definição:** APIs consumidas apenas por componentes internos da plataforma (microsserviços, jobs, gateways).
- OAuth 2.0 com **tokens JWT emitidos por IdP (Identity Provider) confiável**.
- Garantias: comunicação segura entre módulos internos, controle de acesso por funções (RBAC), isolamento de rede quando aplicável (ex.: **VPC — Virtual Private Cloud**).

### Interoperabilidade e conformidade

- Abordagem unificada permite interoperabilidade entre componentes, compatibilidade com regulações (LGPD, PCI DSS) e aderência a OpenID e FAPI.

## Glossário

| Termo | Definição |
|-------|-----------|
| API pública | API exposta a sistemas externos; autenticação via Client Credentials e FAPI 2.0. |
| API privada | API consumida por componentes internos; JWT do IdP, RBAC, opcionalmente VPC. |
| VPC | Virtual Private Cloud; isolamento de rede para tráfego interno. |
| IdP | Identity Provider; emissor confiável de tokens de identidade. |

## Referências

- [FAPI 2.0 Security Profile](https://openid.net/specs/openid-financial-api-part-2-1_0.html)
- RFC 2906 (AAA Authorization Requirements); RFC 6749 (OAuth 2.0 Authorization Framework)
