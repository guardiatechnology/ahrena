---
name: cry-sync
description: "Sincronizar Repositório. Atalho para sincronizar o repositório local com o remoto (fetch, pull, push)"
---

# Cry: Sincronizar Repositório

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para sincronizar o repositório local com o remoto (fetch, pull, push)

## Invocação

```
/cry-sync [remote] [branch]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `remote` | Não | Nome do remoto (padrão: `origin`) | `origin`, `upstream` |
| `branch` | Não | Branch a sincronizar (padrão: branch atual) | `main`, `develop` |

## O que o Comando Faz

1. Invoca o **kata-sync**, que encapsula o procedimento de sincronização do repositório (fetch, pull, push e tratamento de conflitos).
2. O procedimento detalhado está no Kata; o Cry não define passos com comandos externos — apenas invoca o Kata.
3. Enquanto o `kata-sync` estiver pendente de criação, o agente pode orientar o usuário com base em `codex-contributing`; ao ser criado, o Cry passará a invocá-lo exclusivamente.

## Exemplos de Uso

```
# Sincronizar branch atual com origin
/cry-sync

# Sincronizar main com origin
/cry-sync origin main

# Sincronizar com remoto upstream
/cry-sync upstream main
```

## Kata Associado

`kata-sync` — Procedimento completo de sincronização (fetch, pull, push e tratamento de conflitos). **Pendente de criação.**
