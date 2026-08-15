---
name: cry-push-to-framework
description: "Push para o Framework. Incorporação de artefatos de projeto ao framework"
---

# Cry: Push para o Framework

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Incorporação de artefatos de projeto ao framework

## Uso

```
/cry-push-to-framework [alvo] [--local | --remote] [--remove]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `alvo` | Não | Caminho(s) em `.ahrena/artifacts/` ou "todos". Se omitido, processa todos os artefatos encontrados | `pt-BR/engineering/quality/lexis/lex-foo.md` ou `todos` |
| `--local` | Não | Incorporar ao `framework/` do repositório atual (cópia em disco + i18n). | `--local` |
| `--remote` | Não | Incorporar ao repositório do framework no GitHub usando **obrigatoriamente o MCP do GitHub** (branch, push, abertura de PR). | `--remote` |
| `--remove` | Não | Se presente, remove os artefatos de `.ahrena/artifacts/` após copiar para o framework (local) ou após envio bem-sucedido (remote) | `--remove` |

## O que o Comando Faz

1. Determina o modo (local ou remoto) a partir dos parâmetros `--local` ou `--remote`
2. Lê `.ahrena/.directives` para obter `paths.project_artifacts`, `paths.framework` e `language.i18n`
3. Identifica os artefatos em `.ahrena/artifacts/` (todos ou os indicados)
4. Executa `kata-push-to-framework` com o modo e os parâmetros fornecidos
5. Em modo local: copia os artefatos para `framework/` e gera traduções faltantes; em modo remote: envia ao repositório do framework via MCP do GitHub (branch, push, PR)
6. Opcionalmente remove os arquivos do projeto
7. Reporta os arquivos incorporados (e, em modo remote, link do PR)

## Prompt Template

```
Contexto:
- Modo: {{--local}} ou {{--remote}}
- Alvo: {{alvo}} (ou todos os artefatos em .ahrena/artifacts/)
- Remover do projeto após Push: {{--remove}}

Tarefa:
Execute o kata-push-to-framework no modo indicado. Consulte .ahrena/.directives para
paths.project_artifacts, paths.framework e language.i18n. Em modo remote, use
obrigatoriamente o MCP do GitHub para sincronizar com o repositório do framework.

Formato de saída:
Lista de arquivos incorporados e traduções criadas (modo local) ou branch e link do PR (modo remote).
Se --remove foi usado, confirmação de remoção em .ahrena/artifacts/.
```

## Restrições

- Só incorpora artefatos que estejam sob `.ahrena/artifacts/` com estrutura válida (lang/clade/subclade/pilar)
- Sempre executa `kata-push-to-framework` (nunca faz a cópia diretamente sem o Kata)
