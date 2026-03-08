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

- Fluxo **Client Credentials** com extensões de segurança do **FAPI 2.0 Security Profile**.
- Garantias: autorização granular (RBAC e ABAC), rastreabilidade de operações, proteção contra fraudes, autenticação mútua entre cliente e servidor.

### APIs privadas

- OAuth 2.0 com **tokens JWT emitidos por IdP confiável**.
- Garantias: comunicação segura entre módulos internos, controle de acesso por funções (RBAC), isolamento de rede (ex.: Virtual Private Cloud — VPC).

### Interoperabilidade e conformidade

- Abordagem unificada permite interoperabilidade entre componentes, compatibilidade com regulações (LGPD, PCI DSS) e aderência a OpenID e FAPI.

## Referências

- [Autenticação e Autorização — Hub Guardia](https://hub.guardia.finance/docs/specifications/auth/)
- FAPI 2.0 Security Profile
- RFC 2906 (AAA Authorization Requirements); RFC 6749 (OAuth 2.0 Authorization Framework)
