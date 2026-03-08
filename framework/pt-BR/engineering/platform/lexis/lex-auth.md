# Lexis: Autenticação e Autorização nas APIs Guardia

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Plataforma Guardia — acesso às APIs

## Propósito

Garantir segurança, rastreabilidade e conformidade regulatória no acesso às APIs da plataforma Guardia. Acesso sem autenticação e autorização padronizados (OAuth 2.0, modelo AAA) compromete isolamento, auditoria e aderência a LGPD e PCI DSS.

## Lei

> **O acesso às APIs da plataforma Guardia DEVE ser controlado por autenticação e autorização conforme a especificação de Autenticação e Autorização do Hub: OAuth 2.0 como padrão; APIs públicas com Client Credentials e extensões FAPI 2.0; APIs privadas com tokens JWT emitidos por IdP confiável e controle de acesso por funções (RBAC).**

## Abrangência

- **Aplica-se a:** todas as APIs HTTP da plataforma Guardia (públicas e privadas).
- **Agentes vinculados:** implementadores de APIs e consumidores que autenticam.
- **Exceções:** Nenhuma para APIs que exponham recursos protegidos; endpoints públicos documentados (ex.: health) podem ser exceção quando justificado em ADR.

## Consequências de Violação

1. **Segurança:** acesso não autorizado ou não rastreável.
2. **Conformidade:** lacunas em LGPD, PCI DSS e auditoria.
3. **Remediação:** implementar OAuth 2.0 e AAA conforme spec; revisar acessos.

## Exemplos

### Correto

API pública: Client Credentials, FAPI 2.0, RBAC/ABAC, rastreabilidade; API privada: JWT de IdP confiável, RBAC, isolamento (ex.: VPC).

### Incorreto

API sem mecanismo de autenticação; uso de API keys sem OAuth 2.0 quando a spec exige; APIs privadas sem JWT ou sem RBAC.

## Validação Automatizada

- **Ferramenta:** revisão de design e código; testes de autenticação e autorização.
- **Momento:** revisão de PR e auditoria de segurança.
- **Métrica:** 0 APIs protegidas sem conformidade com a spec de Auth.

## Referências

- codex-auth (engineering/platform) (engineering/platform)
- RFC 6749 (OAuth 2.0); FAPI 2.0 Security Profile
