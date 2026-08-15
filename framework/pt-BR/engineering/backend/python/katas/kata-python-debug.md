# Kata: Diagnóstico de Bugs Python

> **Prefix:** `kata-` | **Type:** Habilidade Repetível | **Scope:** Engineering — Backend: depuração sistemática de aplicações Python

## Objective

Esta Kata define o procedimento para diagnosticar e corrigir bugs em aplicações Python backend: reproduzir o problema com um teste falhando, isolar a causa raiz, aplicar a correção e adicionar um teste de regressão. Sem suposições — cada correção é comprovada por um teste que falhava antes e passa depois.

## When to Use

- Quando um bug é reportado em um serviço Python backend
- Quando invocado pelo Warrior Apollo para tarefas de depuração
- Quando um teste está falhando e a causa não é imediatamente óbvia
- Quando o comportamento em produção diverge do comportamento esperado

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Descrição do bug | Sim | O que está acontecendo vs. o que é esperado |
| Passos de reprodução | Não | Como disparar o bug (chamada de API, dados de entrada, sequência de eventos) |
| Saída de erro | Não | Stack trace, entradas de log, mensagens de erro |
| Ambiente | Não | Onde o bug ocorre (local, staging, produção) |

## Workflow

```
Progress:
- [ ] 1. Reproduzir com um teste falhando
- [ ] 2. Isolar a causa raiz
- [ ] 3. Aplicar a correção
- [ ] 4. Verificar a correção
- [ ] 5. Verificar problemas relacionados
```

### Step 1: Reproduzir com um Teste Falhando

1. Ler a descrição do bug, o stack trace e qualquer contexto fornecido
2. Identificar o **ponto de entrada**: qual endpoint, função ou evento dispara o bug?
3. Escrever um teste que exercite o cenário exato e **afirme o comportamento esperado**
4. Executar o teste — DEVE falhar. Se passar, a reprodução está errada; refiná-la
5. Se a reprodução não estiver clara, **perguntar ao usuário** por mais detalhes: entrada exata, sequência, ambiente

**Regras:**
- Um bug sem um teste falhando ainda não foi compreendido
- O teste deve ser mínimo — a menor entrada que dispara o bug
- Marcar o teste claramente: `test_<descrição>_regression`

### Step 2: Isolar a Causa Raiz

1. Ler o stack trace para identificar o ponto de falha
2. Rastrear o fluxo de dados do ponto de entrada até a falha:
   - Qual valor está errado?
   - Onde foi produzido ou transformado?
   - Qual condição não foi atendida?
3. Restringir: um **teste unitário** consegue reproduzi-lo? (iteração mais rápida)
   - Se sim, escrever um teste unitário focado
   - Se não (dependente de infraestrutura), manter o teste de integração
4. Identificar a causa raiz: é um erro de lógica, uma validação ausente, uma condição de corrida, um problema de mapeamento de dados ou um problema de infraestrutura?

### Step 3: Aplicar a Correção

1. Corrigir a causa raiz — não um sintoma
2. A correção deve ser **mínima**: mudar apenas o que é necessário para fazer o teste falhando passar
3. Não refatorar código vizinho no mesmo commit (kata-python-refactor é separado)
4. Garantir que a correção segue todos os Lexis aplicáveis:
   - Type hints completos (lex-python-typing)
   - Tratamento de erros específico (lex-python-error-handling)
   - Sem regressões de segurança (lex-python-security)

### Step 4: Verificar a Correção

1. Executar o teste de regressão — DEVE passar agora
2. Executar a **suite de testes completa** — nenhum teste existente deve quebrar
3. Executar `ruff check .` e `mypy .` — sem novos problemas
4. Verificar que a correção endereça a descrição original do bug, não apenas o teste

### Step 5: Verificar Problemas Relacionados

1. O mesmo padrão está presente em outro lugar do codebase? (mesmo bug em código similar)
2. Se sim, corrigir todas as instâncias ou criar uma tarefa de acompanhamento
3. Este bug poderia ter sido prevenido por uma validação ausente, um tipo mais estrito ou um teste melhor? Considerar adicionar uma salvaguarda

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Correção | Mudanças no código fonte Python | Arquivos afetados |
| Teste de regressão | Arquivo de teste Python | `tests/unit/` ou `tests/integration/` |
| Análise de causa raiz | Breve explicação textual | Mensagem de commit ou conversa |

## Execution Example

### Example Input

```
Bug: POST /v1/transactions retorna 500 quando a moeda está em minúsculas ("brl" em vez de "BRL").
Stack trace: ValidationError no modelo Pydantic — o padrão de moeda ^[A-Z]{3}$ rejeita minúsculas.
Expected: 422 com erro descritivo, não 500.
```

### Example Output (summary)

1. **Teste de reprodução:** `test_create_transaction_lowercase_currency_returns_422` — envia `{"amount": 1000, "currency": "brl"}`, afirma 422 com código de erro `VALIDATION_ERROR`
2. **Causa raiz:** `ValidationError` do Pydantic não é capturado pelo exception handler; FastAPI retorna 500 genérico em vez da response 422 estruturada
3. **Correção:** Adicionado handler de `RequestValidationError` em `register_exception_handlers()` que mapeia erros de validação Pydantic para o formato padrão de response 422
4. **Verificação:** o teste de regressão passa; todos os 47 testes existentes passam; Ruff e mypy limpos
5. **Relacionado:** o mesmo handler ausente afetaria todos os endpoints — a correção é global (uma mudança, cobertura completa)

## Constraints

- Nunca adivinhar a correção sem reproduzir primeiro — escrever o teste falhando
- Nunca corrigir sintomas — encontrar e corrigir a causa raiz
- Nunca mudar código não relacionado no commit de correção
- Escalar para humano se o bug envolve corrupção de dados, violação de segurança ou problemas entre serviços

## References

- codex-python-testing (engineering/backend)
- lex-python-error-handling, lex-python-testing (engineering/backend)
