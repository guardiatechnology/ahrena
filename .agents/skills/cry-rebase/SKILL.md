---
name: cry-rebase
description: "Fazer Rebase. Atalho para resolver conflitos e atualizar a branch via rebase"
---

# Cry: Fazer Rebase

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para resolver conflitos e atualizar a branch via rebase

## Invocação

```
/cry-rebase [base]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `base` | Não | Referência sobre a qual fazer rebase (padrão: branch de rastreamento ou `origin/main`) | `origin/main`, `upstream/develop` |

## O que o Comando Faz

1. Invoca o **kata-rebase**, que encapsula o procedimento de rebase e resolução de conflitos.
2. O procedimento detalhado (verificar estado, executar rebase, resolver conflitos, verificação final) está no Kata; o Cry não define passos com comandos externos — apenas invoca o Kata.
3. Enquanto o `kata-rebase` estiver pendente de criação, o agente pode orientar o usuário com base em `codex-contributing`; ao ser criado, o Cry passará a invocá-lo exclusivamente.

## Exemplos de Uso

```
# Rebase da branch atual em cima de origin/main
/cry-rebase

# Rebase em cima de upstream/develop
/cry-rebase upstream/develop

# Após conflito no sync: rebase e depois push
/cry-rebase origin/main
```

## Kata Associado

`kata-rebase` — Procedimento completo de rebase com resolução de conflitos. **Pendente de criação.**
