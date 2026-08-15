---
name: kata-python-refactor
description: "Refactoring Seguro Python. Engineering — Backend: refactoring seguro de código Python com cobertura de testes como rede de segurança"
---

# Kata: Refactoring Seguro Python

> **Prefix:** `kata-` | **Type:** Habilidade Repetível | **Scope:** Engineering — Backend: refactoring seguro de código Python com cobertura de testes como rede de segurança

## Workflow

```
Progress:
- [ ] 1. Avaliar cobertura de testes atual
- [ ] 2. Adicionar cobertura ausente se necessário
- [ ] 3. Planejar passos de refactoring
- [ ] 4. Executar transformações incrementais
- [ ] 5. Validação final
```

### Step 1: Avaliar Cobertura de Testes Atual

1. Executar a suite de testes para o módulo alvo: `pytest tests/ -v --cov=<module>`
2. Identificar quais comportamentos estão cobertos e quais não estão
3. Se a cobertura for insuficiente para refatorar com segurança, **parar e adicionar testes primeiro** (Passo 2)
4. Se a cobertura for adequada, prosseguir para o Passo 3

### Step 2: Adicionar Cobertura Ausente

1. Escrever testes para o comportamento existente **antes** de mudá-lo — estes são testes de caracterização
2. Testar o comportamento atual, não o comportamento desejado
3. Executar a suite para confirmar que todos os novos testes passam contra o código atual
4. Commitar os novos testes separadamente: "test: add coverage for <module> before refactoring"

### Step 3: Planejar Passos de Refactoring

1. Dividir o refactoring em **pequenas transformações independentes**
2. Cada passo deve ser:
   - Uma única mudança lógica (renomear, extrair, mover, simplificar)
   - Commitável independentemente
   - Verificável executando a suite de testes
3. Ordenar passos para minimizar risco: renomeamentos antes de reestruturação, internos antes de externos

### Step 4: Executar Transformações Incrementais

Para cada passo:

1. Fazer a mudança
2. Executar `ruff check .` e `ruff format .`
3. Executar `mypy .`
4. Executar `pytest` — todos os testes devem passar
5. Se os testes falharem, o refactoring introduziu uma mudança de comportamento — corrigir ou reverter
6. Commitar com uma mensagem descritiva: "refactor: <o que mudou>"

**Regras:**
- **Nunca** mudar comportamento e interface no mesmo commit
- **Nunca** pular a execução de testes entre passos
- Se um passo for grande demais para verificar com confiança, dividi-lo em passos menores
- Se os testes começarem a falhar inesperadamente, reverter e reavaliar

### Step 5: Validação Final

Após todas as transformações:

- [ ] Todos os testes passam (`pytest`)
- [ ] Ruff passa (`ruff check .` e `ruff format --check .`)
- [ ] mypy strict passa (`mypy .`)
- [ ] Comportamento não mudou (os mesmos testes passam, os mesmos contratos de API, os mesmos outputs)
- [ ] Código está mais limpo, legível ou melhor estruturado do que antes
- [ ] Sem novas abstrações a menos que justificadas por 3+ usos concretos

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Código refatorado | Arquivos fonte Python | Mesmas localizações de arquivo (ou novas localizações se movidos) |
| Testes de caracterização (se adicionados) | Arquivos de teste Python | `tests/` |
| Histórico de commits | Commits Git | Um commit por transformação lógica |

## Execution Example

### Example Input

```
Target: Classe TransactionService — atualmente uma god class com 15 métodos misturando lógica de domínio e infraestrutura.
Motivation: Separar lógica de domínio de infraestrutura conforme codex-python-architecture.
Constraint: Todos os endpoints existentes devem continuar funcionando identicamente.
```

### Example Output (summary)

1. Adicionados 22 testes de caracterização cobrindo o comportamento existente (commit separado)
2. Extraída lógica de domínio em `TransactionUseCase` (3 commits: extract, wire, cleanup)
3. Movidos métodos de repositório para `SqlAlchemyTransactionRepository` implementando o Protocol `TransactionRepository` (2 commits)
4. Atualizadas dependências FastAPI para usar o novo grafo de injeção (1 commit)
5. Todos os 47 testes passam; mypy e Ruff limpos

## Constraints

- Nunca mudar comportamento durante o refactoring — se o comportamento precisa mudar, isso é uma tarefa separada
- Nunca refatorar sem cobertura de testes — adicionar testes primeiro
- Nunca fazer commits de refactoring grandes e monolíticos — passos pequenos com validação
- Escalar para humano se o refactoring revela decisões arquiteturais que precisam de alinhamento
