# Lexis: Estrutura Padronizada de Erros nas Respostas

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Plataforma Guardia — tratamento de erros

## Lei

> **Erros retornados pela plataforma Guardia DEVEM seguir a estrutura padronizada (array errors com propriedades code, reason e message); códigos DEVEM ser prefixados com ERR e o código HTTP (ex.: ERR400_); reason DEVEM estar listados em Erros Conhecidos; retentativa e circuit breaker conforme especificação; erros de autenticação NUNCA DEVEM indicar se um usuário existe.**

## Exemplos

### Correto

Payload com `errors: [{ "code": "ERR402_INSUFFICIENT_FUNDS", "reason": "PAYMENT_IS_REQUIRED", "message": "..." }]`; reason em Erros Conhecidos; 401 sem indicar se o usuário existe.

### Incorreto

Erro sem array errors; code sem prefixo ERR + HTTP; reason não catalogado sem justificativa; mensagem de login diferenciando "usuário não encontrado" e "senha incorreta".

## Validação Automatizada

- **Ferramenta:** revisão de contrato (OpenAPI) e código; testes de erro.
- **Momento:** revisão de PR e testes de integração.
- **Métrica:** 0 respostas de erro fora da estrutura; 0 mensagens de autenticação que indiquem existência de usuário.
