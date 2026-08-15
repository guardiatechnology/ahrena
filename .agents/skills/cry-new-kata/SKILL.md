---
name: cry-new-kata
description: "Criar Novo Kata. Criação de Katas (procedimentos repetíveis)"
---

# Cry: Criar Novo Kata

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Criação de Katas (procedimentos repetíveis)

## Uso

```
/cry-new-kata <tarefa> [contexto] [--clade clade/subclade]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `tarefa` | Sim | Tarefa a ser padronizada em procedimento | `"criar ADR"` |
| `contexto` | Não | Informações adicionais sobre o domínio ou restrições | `"projetos com microsserviços"` |
| `--clade` | Não | Clade/subclade na taxonomia. Se omitido, o agente infere da tarefa | `--clade engineering/architecture` |

## O que o Comando Faz

1. Lê `.ahrena/.directives` para obter idiomas e convenções
2. Invoca `kata-create-kata` com os parâmetros fornecidos; o Kata consulta `codex-katas` e o template oficial e produz o Kata
3. (O Kata) Cria o Kata no idioma padrão e traduz para os demais idiomas
4. Reporta os arquivos criados

## Prompt Template

```
Contexto:
- Tarefa: {{tarefa}}
- Contexto adicional: {{contexto}} (ou nenhum)
- Clade/Subclade: {{clade}} (ou inferir da tarefa)

Tarefa:
Execute o kata-create-kata. O Kata consulta .ahrena/.directives, codex-katas
e templates/kata-sample.md. Crie o Kata no idioma padrão e traduza para
todos os idiomas de language.i18n.

Formato de saída:
Lista de arquivos criados com confirmação de que o Kata tem inputs definidos,
passos atômicos e validação final.
```

## Restrições

- Se a tarefa tem menos de 4 passos, sugere criar um Cry em vez de Kata
- Sempre executa `kata-create-kata` (nunca cria diretamente)
- Sempre cria nos três idiomas obrigatórios
