# Cry: Nova Tech Task

> **Prefixo:** `cry-` | **Escopo:** Criar uma issue de tech task no repositório

## O que faz

Cria uma Issue no GitHub usando o template `tech-task`, que responde Por quê / O quê / Como. Invoca `kata-contributing-issue` com o tipo `tech-task`. Segue `lex-issue-quality` e `lex-issue-first`.

## Uso

```
/cry-new-tech-task [título]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição |
|-----------|:-----------:|-----------|
| `título` | Não | Resumo breve da tarefa. Se omitido, o agente pergunta antes de prosseguir. |

## Exemplos

```
/cry-new-tech-task
/cry-new-tech-task update contributing guide with new branch naming rules
/cry-new-tech-task fix CI pipeline for Windows runners
```

## Invoca

`kata-contributing-issue` com `type: tech-task`
