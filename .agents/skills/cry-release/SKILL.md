---
name: cry-release
description: "Publicar Release. Atalho para invocar warrior-janus e fechar o ciclo de entrega — análise de commits, proposta de bump SemVer, aprovação humana e publicação de tag anotada/assinada + GitHub Release"
---

# Cry: Publicar Release

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para invocar `warrior-janus` e fechar o ciclo de entrega — análise de commits, proposta de bump SemVer, aprovação humana e publicação de tag anotada/assinada + GitHub Release

## Invocação

```
/cry-release [--type major|minor|patch] [--dry-run]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `--type` | Não | Sobrescreve a heurística de bump SemVer calculada a partir dos commits. Valores: `major`, `minor`, `patch` | `--type minor` |
| `--dry-run` | Não | Apresenta a proposta sem persistir nada (sem criar arquivo de changelog draft, sem criar tag, sem empurrar) | `--dry-run` |

Se `--type` for fornecido, `warrior-janus` exibe **tanto a heurística calculada quanto o override** para que o humano compare antes de aprovar. Sem flags, Janus usa apenas a heurística.

Se `--dry-run` for fornecido, o comando encerra após apresentar a proposta — nenhuma escrita persistente acontece.

## Exemplos de Uso

```
# Fluxo completo: análise + gate humano + publicação
/cry-release

# Override de bump (humano sabe que merece major mesmo sem BREAKING CHANGE)
/cry-release --type major

# Preview sem efeitos colaterais
/cry-release --dry-run

# Override + dry-run combinados
/cry-release --type minor --dry-run
```

## Comportamento

1. Invoca `warrior-janus`.
2. Janus executa `kata-release-prepare`:
   - `git fetch --tags`, identifica última tag SemVer
   - Coleta e classifica commits desde a última tag (Conventional Commits)
   - Calcula bump heurístico; aplica override (`--type`) quando presente
   - Gera changelog draft (em arquivo, exceto em `--dry-run`)
   - Verifica CI do trunk e lista PRs abertos
3. Janus apresenta a proposta estruturada e aguarda **aprovação humana explícita** ("sim" / "editar" / "cancelar").
4. Em `--dry-run`, encerra após apresentar a proposta.
5. Após "sim", Janus executa `kata-release-publish`:
   - Cria tag anotada + assinada via `kata-tag`
   - Empurra para `origin`
   - Aguarda `validate-tag.yml` (server-side, `lex-annotated-tags`)
   - Detecta workflow de release no repo-alvo; aguarda Release auto-gerada OU faz fallback `gh release create`
   - Sobrescreve notas somente se draft for substancialmente mais informativo
6. Reporta URL da Release, caminho seguido e estado final.

## Warrior Associado

`warrior-janus` — orquestra os dois Katas com gate humano explícito entre eles.
