# Codex: Autenticação e Autorização na Plataforma Guardia

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Plataforma Guardia — acesso às APIs

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
