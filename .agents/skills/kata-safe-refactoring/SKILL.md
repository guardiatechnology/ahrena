---
name: kata-safe-refactoring
description: "Refatoração Segura. Melhorar design interno sem alterar comportamento observável"
---

# Kata: Refatoração Segura

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Melhorar design interno sem alterar comportamento observável

## Workflow

```
Progresso:
- [ ] 1. Delimitar comportamento e risco
- [ ] 2. Criar baseline e proteção
- [ ] 3. Escolher a menor transformação
- [ ] 4. Executar em passos reversíveis
- [ ] 5. Validar comportamento e operação
- [ ] 6. Validação final
```

### Passo 1: Delimitar Comportamento e Risco

Descrever comportamento observável, consumidores, invariantes, contratos e modos de falha. Classificar cada afirmação como confirmada, hipótese ou decisão proposta.

### Passo 2: Criar Baseline e Proteção

Executar testes e análise estática existentes. Quando faltarem testes, adicionar caracterização no nível mais barato que capture o risco. Medir performance somente quando ela fizer parte da motivação.

### Passo 3: Escolher a Menor Transformação

Consultar `codex-code-design` e, quando houver domínio, `codex-domain-driven-design`. Registrar problema, opção escolhida, **quando não usar**, trade-offs e critério de reversão.

### Passo 4: Executar em Passos Reversíveis

Separar mudança estrutural de mudança comportamental, preservar interfaces e executar verificações focadas após cada passo. Não ampliar escopo para limpezas adjacentes.

### Passo 5: Validar Comportamento e Operação

Reexecutar baseline, testes de integração/contrato aplicáveis e verificar logs, métricas, migrações, concorrência e segurança quando tocados.

### Passo 6: Validação Final

- [ ] O comportamento observável e os contratos foram preservados
- [ ] O smell inicial ficou menor e não apenas mudou de lugar
- [ ] A abstração tem evidência e critério de remoção
- [ ] `lex-clean-code`, `lex-dry` e Lexis da stack passam
- [ ] Riscos residuais e verificações executadas estão no handoff

## Outputs

| Output | Formato | Destino |
|---|---|---|
| Código refatorado | Código da stack | Arquivos originais |
| Proteção comportamental | Testes | Suite apropriada |
| Registro de decisão | Resumo/ADR quando necessário | Handoff ou caminho canônico do projeto |

## Exemplo de Execução

### Input de Exemplo

`PaymentService` mistura regra de autorização, chamada ao gateway e retry; uma nova bandeira precisa de política diferente.

### Output de Exemplo

Testes de caracterização preservam respostas e idempotência; a política variável vira Strategy; retry permanece no adapter; não se cria Factory porque a construção continua simples.

## Restrições

- Não chamar alteração de comportamento, contrato ou schema de refatoração.
- Não aplicar pattern apenas para satisfazer métrica.
- Não remover telemetria ou tratamento de falha durante a reorganização.
