# Lexis: Checkpoint de Sessão

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Todas as sessões de trabalho com agentes IA

## Propósito

Sessões de trabalho com agentes de IA são efêmeras — quando encerradas, todo o contexto acumulado (decisões tomadas, progresso parcial, próximos passos) é perdido. Isso gera retrabalho, inconsistência e perda de continuidade.

O checkpoint é um mecanismo do Ahrena que persiste o contexto de uma atividade em um arquivo `.checkpoint`, permitindo que qualquer agente — na mesma sessão ou em sessões futuras — retome o trabalho exatamente de onde parou.

Esta Lexis existe para garantir que **nenhum contexto relevante seja perdido entre sessões** e que **nenhuma atividade comece sem antes verificar se há trabalho prévio salvo**.

## Lei

> **Todo agente DEVE verificar o arquivo `.checkpoint` antes de iniciar qualquer atividade e DEVE salvar o checkpoint ao concluir cada atividade ou encerrar uma sessão.**

## Regras

### 1. Verificação obrigatória ao iniciar

Antes de iniciar qualquer atividade, o agente **DEVE**:

1. Verificar se existe um arquivo `.checkpoint` na raiz do workspace.
2. Se existir, ler seu conteúdo e apresentar ao usuário um resumo do contexto salvo.
3. Perguntar ao usuário se deseja **retomar** a atividade salva ou **iniciar uma nova** (descartando o checkpoint anterior).
4. Se não existir, prosseguir normalmente.

### 2. Salvamento obrigatório ao concluir

Ao concluir uma atividade ou encerrar uma sessão, o agente **DEVE**:

1. Perguntar ao usuário sua preferência de salvamento (apenas na primeira vez da sessão):
   - **Automático:** o checkpoint é salvo automaticamente ao final de cada atividade, sem perguntar novamente.
   - **Manual:** o agente pergunta antes de cada salvamento se o usuário deseja salvar.
2. Respeitar a preferência indicada pelo resto da sessão.
3. Persistir o checkpoint no arquivo `.checkpoint` na raiz do workspace.

### 3. Estrutura do checkpoint

O arquivo `.checkpoint` deve conter, no mínimo:

```markdown
# Checkpoint

- **Atividade:** [descrição breve da atividade em andamento]
- **Status:** [em andamento | concluído | bloqueado]
- **Data:** [data e hora do salvamento]
- **Sessão:** [identificador da sessão ou chat]

## Contexto

[Resumo do que foi discutido, decidido ou produzido]

## Progresso

- [x] [etapa concluída]
- [ ] [próxima etapa pendente]

## Decisões tomadas

- [decisão 1]
- [decisão 2]

## Próximos passos

1. [ação pendente]
2. [ação pendente]

## Artefatos produzidos

- [caminho/do/arquivo-1]
- [caminho/do/arquivo-2]
```

### 4. Responsabilidade compartilhada

- Qualquer agente (Warrior) que atue na sessão **herda** esta obrigação.
- O checkpoint é **agnóstico de disciplina** — aplica-se a atividades de qualquer Clade.
- O arquivo `.checkpoint` **não deve ser commitado** no repositório (deve estar no `.gitignore`).

## Abrangência

- **Aplica-se a:** todas as sessões de trabalho com agentes IA, em qualquer Clade e Subclade
- **Agentes vinculados:** todos os Warriors e agentes genéricos
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Consequências de Violação

1. **Perda de contexto:** sessões sem checkpoint resultam em retrabalho e perda de decisões já tomadas.
2. **Alerta ao usuário:** se o agente detectar que uma sessão anterior não salvou checkpoint, deve alertar o usuário sobre a possível perda de contexto.
3. **Remediação:** o agente deve tentar reconstruir o contexto a partir do histórico disponível (arquivos modificados, git log, transcripts) e salvar um checkpoint retroativo.

## Exemplos

### Correto

```
Agente: Encontrei um checkpoint salvo:
  - Atividade: Implementação do módulo de autenticação
  - Status: em andamento
  - Última sessão: 2026-03-07 14:30
  - Progresso: 3 de 5 etapas concluídas

  Deseja retomar esta atividade ou iniciar uma nova?

Usuário: Retomar.

Agente: Perfeito. Retomando de onde paramos...
  Próximos passos pendentes:
  1. Implementar refresh token
  2. Adicionar testes de integração
```

### Incorreto

```
Agente: Olá! Em que posso ajudar?

Usuário: Vamos continuar a implementação do módulo de autenticação.

Agente: Claro! Vamos começar do zero. Qual é o escopo?

# ❌ O agente ignorou o checkpoint existente e forçou o usuário
# a re-explicar todo o contexto da sessão anterior.
```

## Validação Automatizada

- **Ferramenta:** verificação pelo próprio agente ao iniciar e finalizar cada sessão
- **Momento:** início de cada sessão (leitura) e fim de cada atividade (escrita)
- **Métrica:** 100% das sessões devem ter checkpoint verificado na entrada e salvo na saída
