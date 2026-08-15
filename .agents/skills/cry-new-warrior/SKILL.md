---
name: cry-new-warrior
description: "Criar Novo Warrior. Criação de Warriors (agentes especializados)"
---

# Cry: Criar Novo Warrior

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Criação de Warriors (agentes especializados)

## Uso

```
/cry-new-warrior <papel> [domínio] [--name nome] [--clade clade/subclade]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `papel` | Sim | Função que o Warrior desempenha | `"Arquiteto de Software"` |
| `domínio` | Não | Área de atuação. Se omitido, o agente infere do papel | `"decisões arquiteturais"` |
| `--name` | Não | Nome próprio do Warrior. Se omitido, o agente sugere um nome temático | `--name Athena` |
| `--clade` | Não | Clade/subclade na taxonomia. Se omitido, o agente infere do domínio | `--clade engineering/architecture` |

## O que o Comando Faz

1. Lê `.ahrena/.directives` para obter idiomas e convenções
2. Invoca `kata-create-warrior` com os parâmetros fornecidos; o Kata consulta `codex-warriors` e o template oficial e produz o Warrior
3. (O Kata) Cria o Warrior no idioma padrão e traduz para os demais idiomas
4. Reporta os arquivos criados

## Prompt Template

```
Contexto:
- Papel: {{papel}}
- Domínio: {{domínio}} (ou inferir do papel)
- Nome: {{name}} (ou sugerir nome temático)
- Clade/Subclade: {{clade}} (ou inferir do domínio)

Tarefa:
Execute o kata-create-warrior. O Kata consulta .ahrena/.directives, codex-warriors
e templates/warrior-sample.md. Crie o Warrior no idioma padrão e traduza para
todos os idiomas de language.i18n.

Formato de saída:
Lista de arquivos criados com confirmação de que o Warrior tem identidade
completa, responsabilidades delimitadas e cadeia de consulta definida.
```

## Restrições

- Não cria Warriors genéricos sem escopo delimitado
- Sempre executa `kata-create-warrior` (nunca cria diretamente)
- Sempre cria nos três idiomas obrigatórios
