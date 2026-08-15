# Lexis: Autenticação e Autorização nas APIs Guardia

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Plataforma Guardia — acesso às APIs

## Lei

> **O acesso às APIs da plataforma Guardia DEVE ser controlado por autenticação e autorização conforme a especificação de Autenticação e Autorização do Hub: OAuth 2.0 como padrão; APIs públicas com Client Credentials e extensões FAPI 2.0; APIs privadas com tokens JWT emitidos por IdP confiável e controle de acesso por funções (RBAC).**

## Exemplos

### Correto

API pública: Client Credentials, FAPI 2.0, RBAC/ABAC, rastreabilidade; API privada: JWT de IdP confiável, RBAC, isolamento (ex.: VPC).

### Incorreto

API sem mecanismo de autenticação; uso de API keys sem OAuth 2.0 quando a spec exige; APIs privadas sem JWT ou sem RBAC.

## Validação Automatizada

- **Ferramenta:** revisão de design e código; testes de autenticação e autorização.
- **Momento:** revisão de PR e auditoria de segurança.
- **Métrica:** 0 APIs protegidas sem conformidade com a spec de Auth.
