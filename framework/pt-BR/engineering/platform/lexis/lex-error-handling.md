# Lexis: Estrutura Padronizada de Erros nas Respostas

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Plataforma Guardia — tratamento de erros

## Propósito

Garantir consistência, clareza e rastreabilidade na comunicação de falhas entre serviços, consumidores de API e interfaces. Erros padronizados permitem tratamento programático e diagnóstico; erros de autenticação que indiquem existência de usuário comprometem segurança.

## Lei

> **Erros retornados pela plataforma Guardia DEVEM seguir a estrutura padronizada (array errors com propriedades code, reason e message); códigos DEVEM ser prefixados com ERR e o código HTTP (ex.: ERR400_); reason DEVEM estar listados em Erros Conhecidos; retentativa e circuit breaker conforme especificação; erros de autenticação NUNCA DEVEM indicar se um usuário existe.**

## Abrangência

- **Aplica-se a:** APIs REST públicas e internas, comunicação entre microsserviços, integrações e UIs que consomem APIs da plataforma Guardia.
- **Agentes vinculados:** todos os implementadores de APIs e clientes que tratem respostas de erro.
- **Exceções:** Nenhuma para a estrutura de erro; novos reason devem ser justificados e registrados em Erros Conhecidos.

## Consequências de Violação

1. **Inconsistência:** clientes não conseguem tratar erros de forma uniforme.
2. **Segurança:** mensagens de autenticação que revelem existência de usuário facilitam enumeração.
3. **Remediação:** padronizar payload de erro e revisar mensagens sensíveis.

## Exemplos

### Correto

Payload com `errors: [{ "code": "ERR402_INSUFFICIENT_FUNDS", "reason": "PAYMENT_IS_REQUIRED", "message": "..." }]`; reason em Erros Conhecidos; 401 sem indicar se o usuário existe.

### Incorreto

Erro sem array errors; code sem prefixo ERR + HTTP; reason não catalogado sem justificativa; mensagem de login diferenciando "usuário não encontrado" e "senha incorreta".

## Validação Automatizada

- **Ferramenta:** revisão de contrato (OpenAPI) e código; testes de erro.
- **Momento:** revisão de PR e testes de integração.
- **Métrica:** 0 respostas de erro fora da estrutura; 0 mensagens de autenticação que indiquem existência de usuário.

## Referências

- [Especificação de Tratamento de Erros — Hub Guardia](https://hub.guardia.finance/docs/specifications/error-handling/)
- codex-error-handling (engineering/platform)
