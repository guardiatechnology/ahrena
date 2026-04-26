# Cry: Nova Tarefa Simples

> **Prefixo:** `cry-` | **Escopo:** Criar uma issue de tarefa simples no repositório

## O que faz

Cria uma Issue no GitHub usando o template `simple-task`, que responde Por quê / O quê / Como. Invoca `kata-contributing-issue` com o tipo `simple-task`. Segue `lex-issue-quality` e `lex-issue-first`.

## Uso

```
/cry-new-simple-task [título]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição |
|-----------|:-----------:|-----------|
| `título` | Não | Resumo breve da tarefa. Se omitido, o agente pergunta antes de prosseguir. |

## Exemplos

```
/cry-new-simple-task
/cry-new-simple-task update contributing guide with new branch naming rules
/cry-new-simple-task fix CI pipeline for Windows runners
```

## Invoca

`kata-contributing-issue` com `type: simple-task`
