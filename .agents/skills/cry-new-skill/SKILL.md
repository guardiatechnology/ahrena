---
name: cry-new-skill
description: "Novo Projeto de Skill. Inicialização de um novo projeto de skill no repositório, no formato Anthropic Agent Skills, com layout Ahrena"
---

# Cry: Novo Projeto de Skill

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Inicialização de um novo projeto de skill no repositório, no formato Anthropic Agent Skills, com layout Ahrena

## Uso

```
/cry-new-skill <slug> [opções]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `slug` | Sim | Nome do projeto em kebab-case (1-64 chars, `a-z`/`0-9`/hífen, sem hífen no início/fim, sem `--`) | `scheduled-payments-skill` |
| `description=` | Sim | Frase única do frontmatter (1-1024 chars), com **o que faz** + **quando usar** | `description="Schedules bank transfers when the user requests payment for a future date"` |
| `language=` | Não | BCP 47; default = `language.default` em `.directives` | `language=en` |
| `license=` | Não | Identificador (`Apache-2.0`, `MIT`) ou referência | `license=Apache-2.0` |
| `human_title=` | Não | Título humano para o `# H1` do `SKILL.md` | `human_title="Scheduled Payments"` |
| `with_widgets=` | Não | `true` (default) ou `false` | `with_widgets=false` |
| `with_tools=` | Não | `true` (default) ou `false` | `with_tools=false` |
| `with_scripts=` | Não | `python` (default), `js`, ou `false` | `with_scripts=js` |

## O que o Comando Faz

1. Valida slug e description contra a spec Anthropic Agent Skills (regex e limites)
2. Resolve `paths.skills_root` em `.ahrena/.directives` (default `skills`)
3. Verifica que o destino `{paths.skills_root}/{slug}/` não existe
4. Invoca `kata-init-skill` com os parâmetros recebidos
5. Reporta caminho criado, opt-outs aplicados, e próximos passos

## Prompt Template

```
Contexto:
- slug: {{slug}}
- description: {{description}}
- language: {{language}} (opcional)
- license: {{license}} (opcional)
- human_title: {{human_title}} (opcional)
- with_widgets: {{with_widgets}} (default true)
- with_tools: {{with_tools}} (default true)
- with_scripts: {{with_scripts}} (default python)

Tarefa:
Invoque kata-init-skill com os parâmetros acima. O kata:
1. Valida slug e description per codex-skill-anthropic-agent-skills
2. Copia framework/templates/skill-project-sample/ para
   {paths.skills_root}/{slug}/, substituindo placeholders
3. Aplica opt-outs (with_widgets, with_tools, with_scripts)
4. Garante .gitignore com .build/
5. Reporta resultado

Aborte se: slug inválido, destino já existe, ou template ausente.

Formato de saída:
Confirmação do projeto criado, lista de subdiretórios, próximos passos
para autoria. Em caso de erro, mensagem específica e correção sugerida.
```

## Restrições

- O Cry não modifica `.ahrena/.directives` (per `lex-directives`)
- O Cry não cria projeto se o destino já existir; o usuário decide remover ou escolher outro slug
- Mensagens ao usuário no idioma de `language.default`; identificadores técnicos (slug, frontmatter, placeholder) preservados
