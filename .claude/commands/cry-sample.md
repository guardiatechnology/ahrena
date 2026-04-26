[Nome do Comando]. [Etapa do SDLC]

# Cry: [Nome do Comando]

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** [Etapa do SDLC]

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

## Restrições

- [Restrição 1 — ex: não modifica arquivos existentes, apenas gera output]
- [Restrição 2 — ex: output sempre em português brasileiro]
- [Restrição 3 — ex: máximo de 500 palavras no output]
