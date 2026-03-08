# Cry: [Nome do Comando]

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** [Etapa do SDLC]

## Descrição

Descreva o que este comando faz. Cries são prompts recorrentes e atalhos de produtividade que automatizam tarefas repetitivas do dia a dia. Diferem dos Katas por não configurarem características de agente, mas sim por serem invocações rápidas.

## Uso

```
/cry-[nome]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `[param1]` | Sim | [descrição] | [ex: caminho do arquivo] |
| `[param2]` | Não | [descrição] | [ex: idioma de saída] |

## O que o Comando Faz

1. [Ação 1 — ex: lê o arquivo indicado]
2. [Ação 2 — ex: analisa o conteúdo]
3. [Ação 3 — ex: gera output formatado]

## Prompt Template

```
[Instruções que o Cry envia ao agente quando invocado]

Contexto:
- {{param1}}
- {{param2}}

Tarefa:
[Descrição da tarefa que o agente deve executar]

Formato de saída:
[Formato esperado do output]
```

## Exemplo de Invocação

**Input:**

```
/cry-[nome] [argumentos de exemplo]
```

**Output esperado:**

```
[Exemplo concreto do que o comando produz]
```

## Restrições

- [Restrição 1 — ex: não modifica arquivos existentes, apenas gera output]
- [Restrição 2 — ex: output sempre em português brasileiro]
- [Restrição 3 — ex: máximo de 500 palavras no output]

## Diferença de Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Natureza** | Invocação rápida | Procedimento completo |
| **Complexidade** | Baixa (1-2 passos) | Alta (múltiplos passos) |
| **Configura agente?** | Não | Sim |
| **Exemplo** | Gerar changelog | Elaborar ADR completo |

---

**Modelo:** Este arquivo é um template. Para criar um novo Cry, copie este arquivo e substitua os campos entre colchetes.
