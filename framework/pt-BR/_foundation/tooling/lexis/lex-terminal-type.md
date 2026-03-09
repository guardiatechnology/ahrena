# Lexis: Uso Obrigatório do Tipo de Terminal Definido

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Execução de comandos em shell por agentes IA

## Propósito

Em projetos que adotam o Ahrena, os comandos de terminal podem ser executados em **bash** (Linux, macOS, WSL) ou **PowerShell** (Windows nativo). Scripts, exemplos de documentação e instruções geradas por agentes precisam usar a sintaxe e o interpretador corretos para o ambiente do projeto; do contrário, os comandos falham ou geram confusão.

Esta Lexis existe para garantir que **todo agente use o tipo de terminal (bash ou PowerShell) definido pelo projeto ou pelas diretivas canônicas** ao propor, gerar ou descrever comandos de shell.

## Lei

> **Todo agente DEVE usar o tipo de terminal (bash ou PowerShell) definido em `.ahrena/.directives` ao executar ou propor comandos de shell. Se a diretiva não existir, o agente DEVE inferir o tipo a partir do sistema operacional do usuário (por exemplo, Windows → PowerShell; Linux/macOS → bash) ou perguntar ao usuário.**

## Regras

### 1. Consulta à diretiva canônica

Ao executar ou sugerir comandos de terminal, o agente **DEVE**:

1. Consultar `.ahrena/.directives` (conforme `lex-directives`).
2. Verificar se existe a seção `terminal` com o valor `bash` ou `powershell`.
3. Usar esse valor como fonte da verdade para a sintaxe e o interpretador dos comandos.

### 2. Comportamento quando a seção não existir

Se a seção `terminal` não estiver presente em `.ahrena/.directives`:

- O agente **DEVE** inferir a partir do contexto quando possível (por exemplo, informação de que o ambiente é Windows → PowerShell; Linux ou macOS → bash).
- Se o contexto não for claro, o agente **DEVE** perguntar ao usuário qual tipo de terminal usar antes de executar ou gerar comandos que dependam do shell.

### 3. Consistência na sessão

Uma vez definido o tipo de terminal (por diretiva, inferência ou resposta do usuário), o agente **DEVE** manter esse tipo durante toda a sessão ao propor ou executar comandos, salvo instrução explícita em contrário do usuário.

### 4. Documentação e exemplos

Em artefatos que contenham exemplos de comandos (documentação, README, Katas, Cries), o agente **DEVE** gerar os exemplos no tipo de terminal definido pelo projeto ou indicar claramente qual shell está sendo usado (por exemplo, com comentário ou bloco identificado).

### 5. Não modificação sem autorização

O agente **NÃO PODE** adicionar ou alterar a seção `terminal` em `.ahrena/.directives` sem solicitação explícita do usuário.

## Abrangência

- **Aplica-se a:** todas as sessões em que o agente execute ou proponha comandos de shell (terminal) no contexto do Ahrena.
- **Agentes vinculados:** todos os Warriors e agentes genéricos.
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Consequências de Violação

1. **Comandos falhos:** uso de sintaxe bash em ambiente PowerShell (ou vice-versa) pode quebrar scripts e instruções.
2. **Inconsistência:** documentação e exemplos em um shell enquanto o usuário usa outro geram retrabalho e confusão.
3. **Remediação:** o agente deve reler as diretivas, identificar o tipo de terminal correto e regenerar ou corrigir os comandos conforme `codex-terminal-type`.

## Exemplos

### Correto

```
# .ahrena/.directives contém:
terminal: powershell

# Agente propõe comando no PowerShell:
Get-ChildItem -Path . -Filter "*.md" | Select-Object Name
```

```
# .ahrena/.directives contém:
terminal: bash

# Agente propõe comando em bash:
find . -name "*.md" -type f
```

### Incorreto

```
# Usuário em Windows; .directives não define terminal.
# Agente assume bash e sugere:
find . -name "*.md"

# ❌ Em PowerShell nativo, find não existe como comando.
# O agente deveria ter inferido PowerShell ou perguntado ao usuário.
```

## Validação Automatizada

- **Ferramenta:** verificação pelo próprio agente antes de executar ou propor comandos de shell.
- **Momento:** ao iniciar execução de comando e ao gerar documentação com exemplos de terminal.
- **Métrica:** 100% dos comandos de shell propostos ou executados devem respeitar o tipo de terminal definido ou inferido.
