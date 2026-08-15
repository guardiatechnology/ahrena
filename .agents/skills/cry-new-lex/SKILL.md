---
name: cry-new-lex
description: "Criar Nova Lexis. Criação de Lexis (leis inquebráveis)"
---

# Cry: Criar Nova Lexis

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Criação de Lexis (leis inquebráveis)

## Uso

```
/cry-new-lex <assunto> [escopo] [--clade clade/subclade]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `assunto` | Sim | Tema da lei a ser criada | `"code review obrigatório"` |
| `escopo` | Não | Onde a lei se aplica. Se omitido, o agente infere do assunto | `"todos os repositórios"` |
| `--clade` | Não | Clade/subclade na taxonomia. Se omitido, o agente infere do assunto | `--clade engineering/quality` |

## O que o Comando Faz

1. Lê `.ahrena/.directives` para obter idiomas e convenções
2. Invoca `kata-create-lexis` com os parâmetros fornecidos; o Kata consulta `codex-lexis` e o template oficial e produz a Lexis
3. (O Kata) Cria a Lexis no idioma padrão e traduz para os demais idiomas
4. Reporta os arquivos criados

## Prompt Template

```
Contexto:
- Assunto: {{assunto}}
- Escopo: {{escopo}} (ou inferir do assunto)
- Clade/Subclade: {{clade}} (ou inferir do assunto)

Tarefa:
Execute o kata-create-lexis. O Kata consulta .ahrena/.directives, codex-lexis
e templates/lex-sample.md. Crie a Lexis no idioma padrão e traduza para
todos os idiomas de language.i18n.

Formato de saída:
Lista de arquivos criados com confirmação de que a lei é clara, unívoca
e testável.
```

## Restrições

- Não cria Lexis que admitam exceções — se precisa de exceção, sugere criar um Codex
- Sempre executa `kata-create-lexis` (nunca cria diretamente)
- Sempre cria nos três idiomas obrigatórios
