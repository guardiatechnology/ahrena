---
name: kata-python-review
description: "Revisão de Código Python. Engineering — Backend: revisão sistemática de código para PRs Python"
---

# Kata: Revisão de Código Python

> **Prefix:** `kata-` | **Type:** Habilidade Repetível | **Scope:** Engineering — Backend: revisão sistemática de código para PRs Python

## Workflow

```
Progress:
- [ ] 1. Entender a mudança
- [ ] 2. Verificar corretude
- [ ] 3. Verificar segurança de tipos
- [ ] 4. Avaliar cobertura de testes
- [ ] 5. Revisar segurança
- [ ] 6. Revisar tratamento de erros
- [ ] 7. Verificar conformidade de arquitetura
- [ ] 8. Entregar revisão
```

### Step 1: Entender a Mudança

1. Ler a descrição do PR, mensagens de commit e issue/spec relacionada
2. Entender a **intenção** — que problema isso resolve?
3. Identificar o escopo: quais camadas são afetadas (domínio, infraestrutura, HTTP)?

### Step 2: Verificar Corretude

1. O código faz o que a descrição diz?
2. Os casos extremos são tratados? (valores nulos, listas vazias, valores de borda, acesso concorrente)
3. A lógica está correta para todos os caminhos de código?
4. Há erros de off-by-one, condições de corrida ou vazamentos de recursos?

### Step 3: Verificar Segurança de Tipos

1. Todas as funções, parâmetros e valores de retorno são tipados? (lex-python-typing)
2. Os tipos são precisos? (sem `Any` sem justificativa, não excessivamente amplos)
3. mypy strict passaria nas mudanças?
4. Modelos Pydantic são usados para validação nas fronteiras?

### Step 4: Avaliar Cobertura de Testes

1. Todo novo comportamento tem um teste? (lex-python-testing)
2. Os testes estão no nível certo? (unitário para lógica, integração para BD, HTTP para endpoints)
3. Mocks são usados apenas nas fronteiras do sistema? (não mockear colaboradores internos)
4. Os casos extremos e caminhos de erro são testados?
5. As afirmações são significativas? (testando comportamento, não implementação)
6. Para invariantes de domínio: testes de propriedade com Hypothesis agregariam valor?

### Step 5: Revisar Segurança

1. Sem segredos hardcoded? (lex-python-security)
2. Entrada validada nas fronteiras? (modelos Pydantic com restrições)
3. SQL usa queries parametrizadas? (sem interpolação de strings)
4. Mensagens de erro não expõem dados sensíveis?
5. Novas dependências foram auditadas por vulnerabilidades?

### Step 6: Revisar Tratamento de Erros

1. Sem `except:` nu ou `except Exception:` genérico sem contexto? (lex-python-error-handling)
2. As exceções são específicas ao modo de falha?
3. Os erros são logados com contexto suficiente para depuração?
4. As responses de erro não vazam detalhes internos?

### Step 7: Verificar Conformidade de Arquitetura

1. Camada de domínio livre de imports de framework? (codex-python-architecture)
2. Dependências apontam para dentro? (infraestrutura → domínio, nunca o contrário)
3. Dataclasses são frozen? (lex-python-immutability)
4. Sem abstrações prematuras? (sem interface para uma única implementação sem necessidade de teste)
5. Segue os padrões do codebase existente?

### Step 8: Entregar Revisão

Estruturar a revisão como:

1. **Resumo:** avaliação em uma frase (aprovar, solicitar mudanças ou comentar)
2. **Problemas críticos:** bugs, vulnerabilidades de segurança, testes ausentes (obrigatório corrigir)
3. **Sugestões:** melhorias que fortaleceriam o código (opcional)
4. **Notas positivas:** o que foi feito bem (reconhecer bons padrões)

**Regras:**
- Ser específico — referenciar arquivo, linha e o problema
- Explicar o **porquê**, não apenas o quê — citar o Lexis ou Codex relevante
- Sugerir uma correção quando possível, não apenas apontar problemas
- Não comentar sobre estilo — Ruff cuida da formatação
- Não solicitar mudanças por preferência pessoal — apenas por violações de Lexis, bugs ou testes ausentes

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Revisão | Feedback estruturado (resumo, críticos, sugestões, positivos) | Inline na conversa ou como comentários de revisão do PR |

## Constraints

- Esta Kata revisa código — não implementa correções (kata-python-implement cuida disso)
- Focar em substância (corretude, segurança, testes) sobre estilo (Ruff cuida do estilo)
- Não bloquear PRs por sugestões não críticas
- Escalar para humano quando a mudança tem implicações arquiteturais além do escopo do revisor
