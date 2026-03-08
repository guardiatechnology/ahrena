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

## Comportamento

O comando orienta a resolução de conflitos usando rebase:

1. **Verificar estado:** confirmar que há conflitos ou que a branch está atrás do remoto (ex.: após um pull com divergência).
2. **Executar rebase:** `git rebase <base>` — reaplica os commits locais em cima de `<base>`.
3. **Resolver conflitos (se houver):** para cada conflito, o agente auxilia a editar os arquivos, `git add` e `git rebase --continue`; ou `git rebase --abort` para cancelar.
4. **Verificação final:** após rebase concluído, informar que o usuário pode fazer `git push` (possivelmente `--force-with-lease` se a branch já tinha sido enviada).

Se o usuário invocou `/cry-sync` e houve conflito no pull, usar este Cry para rebase em cima do remoto e depois concluir o push.

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

## Referências

- `cry-sync` — Sincronização do repositório (fetch, pull, push); usar rebase quando houver conflitos
- `codex-contributing` — Fluxo de contribuição
