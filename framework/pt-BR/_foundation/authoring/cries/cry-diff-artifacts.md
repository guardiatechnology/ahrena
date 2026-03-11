# Cry: Diff de Artefatos

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Comparação de artefatos do projeto com o framework

## Descrição

Atalho para comparar artefatos do projeto (`.ahrena/artifacts` e, quando aplicável, `.ahrena/framework`) com o framework em modo **--local** (vs framework no repo) ou **--remote** (vs versão mais recente do framework no GitHub, obtida via MCP do GitHub). Invoca o `kata-diff-artifacts` e apresenta o relatório de diferenças.

## Uso

```
/cry-diff-artifacts [--local | --remote] [alvo]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `--local` | Não* | Comparar `.ahrena/artifacts` (e opcionalmente `.ahrena/framework`) com o framework local (`paths.framework`). | `--local` |
| `--remote` | Não* | Comparar estado local com a versão mais recente do framework no remoto; **obrigatório** usar o MCP do GitHub para obter o conteúdo remoto. | `--remote` |
| `alvo` | Não | Caminho(s) em `paths.project_artifacts` ou "todos". Se omitido, considerar todos os artefatos. | `pt-BR/engineering/quality/lexis/lex-foo.md` ou `todos` |

*Um dos modos (`--local` ou `--remote`) deve ser informado.

## O que o Comando Faz

1. Determina o modo (local ou remoto) a partir de `--local` ou `--remote`
2. Invoca `kata-diff-artifacts` com o modo e o alvo indicados
3. Apresenta o relatório de diferenças ao usuário (somente leitura; nenhum arquivo é alterado)

## Prompt Template

```
Contexto:
- Modo: {{--local}} ou {{--remote}}
- Alvo: {{alvo}} (ou todos os artefatos em .ahrena/artifacts/)

Tarefa:
Execute o kata-diff-artifacts no modo indicado. Em modo remote, use
obrigatoriamente o MCP do GitHub para obter o estado do framework no remoto.

Formato de saída:
Relatório com artefatos só em artifacts, só no framework (local ou remoto),
e os que diferem (com indicação de diff). Nenhuma alteração em arquivos.
```

## Exemplo de Invocação

**Comparar com o framework local:**

```
/cry-diff-artifacts --local
```

**Comparar com a versão mais recente no remoto (via MCP do GitHub):**

```
/cry-diff-artifacts --remote
```

**Comparar um artefato específico com o framework local:**

```
/cry-diff-artifacts --local pt-BR/engineering/quality/lexis/lex-code-review.md
```

## Restrições

- Somente leitura; o comando não modifica `.ahrena/` nem `framework/`.
- Em modo **--remote**, é obrigatório usar o MCP do GitHub.

## Referências

- `kata-diff-artifacts` — Procedimento executado por este Cry (o Kata consulta fluxo e conceitos de artefatos; ver documentação do Kata)
