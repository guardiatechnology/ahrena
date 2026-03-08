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

## Comportamento

O comando executa, **nessa ordem**:

1. **Fetch:** `git fetch <remote>` — atualiza referências e objetos do remoto sem alterar a working tree.
2. **Pull:** `git pull <remote> <branch>` — traz e faz merge (ou rebase, conforme config) dos commits do remoto para a branch atual.
3. **Push:** `git push <remote> <branch>` — envia os commits locais para o remoto.

Se houver conflitos no pull, o agente informa e orienta o uso de `/cry-rebase` para resolver antes de tentar o push.

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

## Referências

- `cry-rebase` — Usar quando houver conflitos após o pull para resolver via rebase
- `codex-contributing` — Fluxo de contribuição
