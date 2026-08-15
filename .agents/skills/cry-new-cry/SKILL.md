---
name: cry-new-cry
description: "Criar Novo Cry. Criação de Cries (comandos recorrentes)"
---

# Cry: Criar Novo Cry

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Criação de Cries (comandos recorrentes)

## Uso

```
/cry-new-cry <ação> [kata] [--clade clade/subclade]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `ação` | Sim | O que o novo comando faz | `"gerar changelog"` |
| `kata` | Não | Kata que o Cry invocará. Se omitido, o agente identifica ou sugere criação | `kata-generate-changelog` |
| `--clade` | Não | Clade/subclade na taxonomia. Se omitido, o agente infere da ação | `--clade engineering/process` |

## O que o Comando Faz

1. Lê `.ahrena/.directives` para obter idiomas e convenções
2. Invoca `kata-create-cry` com os parâmetros fornecidos; o Kata consulta `codex-cries` e o template oficial e produz o Cry (e verifica se o Kata associado existe)
3. (O Kata) Cria o Cry no idioma padrão e traduz para os demais idiomas
4. Reporta os arquivos criados

## Prompt Template

```
Contexto:
- Ação: {{ação}}
- Kata associado: {{kata}} (ou identificar/sugerir)
- Clade/Subclade: {{clade}} (ou inferir da ação)

Tarefa:
Execute o kata-create-cry. O Kata consulta .ahrena/.directives, codex-cries
e templates/cry-sample.md. Verifique se o Kata associado existe. Crie o Cry
no idioma padrão e traduza para todos os idiomas de language.i18n.

Formato de saída:
Lista de arquivos criados com confirmação de que o Cry tem sintaxe clara,
parâmetros mínimos e prompt template referenciando o Kata.
```

## Restrições

- Todo Cry deve referenciar um Kata — se o Kata não existe, sinalizar como pendência
- Sempre executa `kata-create-cry` (nunca cria diretamente)
- Sempre cria nos três idiomas obrigatórios
