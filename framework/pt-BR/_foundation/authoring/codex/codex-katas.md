# Codex: Como Escrever Bons Katas

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Criação de Katas (procedimentos repetíveis)

## Visão Geral

Este Codex documenta como projetar procedimentos estruturados eficazes no Ahrena. Aborda decomposição de tarefas, design de inputs e outputs, critérios de validação e quando usar Kata vs Cry. É consultado pelo `kata-create-kata` durante a criação de novos Katas.

## Contexto

- **Domínio:** Design de procedimentos padronizados para agentes de IA
- **Público-alvo:** Agentes de IA executando `kata-create-kata` e mantenedores do framework
- **Atualização:** Quando novos padrões de qualidade forem identificados para Katas

## Conteúdo

### Princípios

1. **Reprodutibilidade:** Dois agentes executando o mesmo Kata com os mesmos inputs devem produzir outputs equivalentes.
2. **Progressividade:** Cada passo deve ser verificável antes de avançar para o próximo. Se um passo falha, deve ser possível corrigir sem recomeçar do zero.
3. **Completude:** O Kata deve cobrir o fluxo inteiro — do input ao output validado. Não deve depender de conhecimento implícito.
4. **Atomicidade dos passos:** Cada passo executa uma única ação bem definida. Se um passo faz duas coisas, divida-o.

### Anatomia de um Bom Kata

| Seção | Propósito | Critério de Qualidade |
|-------|-----------|----------------------|
| **Objetivo** | O que este procedimento produz | Uma frase clara sobre o output |
| **Quando Usar** | Condições de ativação | Lista de gatilhos específicos |
| **Inputs** | O que o agente precisa receber | Tabela com nome, obrigatoriedade e descrição |
| **Workflow** | Passos numerados com checklist | Cada passo com sub-ações detalhadas |
| **Outputs** | O que é produzido | Tabela com formato e destino |
| **Restrições** | O que o Kata não pode fazer | Lista de limites explícitos |

### Design de Inputs

Boas práticas para definir inputs:

| Prática | Exemplo |
|---------|---------|
| Distinguir obrigatório vs opcional | "Arquivo-fonte (Sim) / Idioma-alvo (Não)" |
| Definir defaults para opcionais | "Se omitido, traduzir para todos de `language.i18n`" |
| Especificar formato esperado | "Código BCP 47 (ex: pt-BR, en, es)" |
| Validar inputs no primeiro passo | "Confirmar que o arquivo existe e é .md" |

### Design de Workflow

Cada passo do workflow deve seguir esta estrutura:

1. **Nome descritivo** — o que este passo faz (ex: "Leitura das Diretivas")
2. **Sub-ações numeradas** — instruções específicas (1. Ler X, 2. Verificar Y)
3. **Checkpoint** — como saber que o passo foi concluído com sucesso

O checklist de progresso no início do workflow permite rastrear a execução:

```
Progresso:
- [ ] 1. Nome do passo 1
- [ ] 2. Nome do passo 2
- [ ] 3. Validação final
```

### Design de Validação

A validação final é o último passo de todo Kata. Deve incluir:

- Checklist de critérios verificáveis (checkboxes)
- Critérios tanto de forma (estrutura, formatação) quanto de conteúdo (completude, correção)
- Referência às Lexis que devem ser obedecidas

### Padrões e Convenções

| Aspecto | Padrão | Exemplo |
|---------|--------|---------|
| Número de passos | 4-8 (ideal) | Menos de 4: talvez seja um Cry. Mais de 8: decompor |
| Referências | Citar artefatos consultados | "Consultar `codex-lexis` para critérios de qualidade" |
| Exemplos | Incluir input e output de exemplo | Bloco de código com dados reais |
| Idempotência | Executar o Kata 2x não deve gerar duplicatas | Verificar existência antes de criar |

### Armadilhas Comuns

| Armadilha | Problema | Solução |
|-----------|----------|---------|
| Kata genérico demais | "Crie documentação" — sem especificidade | Restringir escopo: "Crie um ADR" |
| Passos vagos | "Analise o código" — como? | Detalhar sub-ações específicas |
| Sem validação | Output não é verificado | Sempre incluir passo de validação final |
| Inputs implícitos | O Kata assume contexto não declarado | Declarar todo input na tabela |
| Dependência circular | Kata A precisa de Kata B que precisa de Kata A | Refatorar para eliminar o ciclo |

### Kata vs Cry — Quando Usar Cada Um

| Característica | Kata | Cry |
|---------------|------|-----|
| Complexidade | Múltiplos passos (4-8) | 1-2 passos |
| Inputs | Vários, com validação | Poucos, simples |
| Configura agente? | Sim (define comportamento) | Não (apenas invoca) |
| Output | Estruturado e validado | Rápido e direto |
| Exemplo | Criar um ADR completo | Gerar changelog |

### Restrições Técnicas

- Todo Kata deve ter um checklist de progresso no início do Workflow
- A seção "Validação Final" deve ser o último passo e conter checkboxes
- O nome do arquivo deve seguir o padrão `kata-{nome-descritivo}.md`
- Inputs obrigatórios devem ser validados no primeiro passo

## Glossário

| Termo | Definição |
|-------|-----------|
| Reprodutibilidade | Capacidade de obter o mesmo resultado em execuções diferentes |
| Checkpoint | Verificação ao final de um passo que confirma sucesso |
| Idempotência | Propriedade de produzir o mesmo resultado mesmo se executado múltiplas vezes |
| Decomposição | Divisão de uma tarefa complexa em passos atômicos |

## Referências

- `codex-pilars` — Visão geral do sistema de Pilares
- `codex-cries` — Manual sobre Cries (para entender a diferença Kata vs Cry)
- `lex-template-usage` — Lei de uso obrigatório de templates
- `kata-create-kata` — Procedimento para criar novos Katas
- `templates/kata-sample.md` — Template oficial de Katas
