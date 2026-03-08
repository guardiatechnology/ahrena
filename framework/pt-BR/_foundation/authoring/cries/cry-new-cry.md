# Cry: Criar Novo Cry

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Criação de Cries (comandos recorrentes)

## Descrição

Comando rápido para criar um novo Cry no Ahrena. Invoca o `kata-create-cry`, que consulta `codex-cries` e o template oficial para produzir um comando recorrente completo nos três idiomas obrigatórios. Este é o Cry que cria Cries — o atalho para o mecanismo de autorreplicação.

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
2. Consulta `codex-cries` para critérios de qualidade
3. Lê `templates/cry-sample.md` como base estrutural
4. Verifica se o Kata associado existe
5. Executa `kata-create-cry` com os parâmetros fornecidos
6. Cria o Cry no idioma padrão e traduz para os demais idiomas
7. Reporta os arquivos criados

## Prompt Template

```
Contexto:
- Ação: {{ação}}
- Kata associado: {{kata}} (ou identificar/sugerir)
- Clade/Subclade: {{clade}} (ou inferir da ação)

Tarefa:
Execute o kata-create-cry. Consulte .ahrena/.directives para obter os
idiomas obrigatórios. Consulte codex-cries para critérios de qualidade.
Use templates/cry-sample.md como base. Verifique se o Kata associado
existe. Crie o Cry no idioma padrão e traduza para todos os idiomas de
language.i18n.

Formato de saída:
Lista de arquivos criados com confirmação de que o Cry tem sintaxe clara,
parâmetros mínimos e prompt template referenciando o Kata.
```

## Exemplo de Invocação

**Criar Cry com ação:**

```
/cry-new-cry "gerar changelog"
```

**Output:**

```
Cry criado com sucesso.

Comando: /cry-changelog
Ação: Gerar changelog a partir dos commits
Kata associado: kata-generate-changelog (sugerido — ainda não existe)

Arquivos criados:
1. framework/pt-BR/engineering/process/cries/cry-changelog.md ✓
2. framework/es/engineering/process/cries/cry-changelog.md ✓
3. framework/en/engineering/process/cries/cry-changelog.md ✓

Pendência: kata-generate-changelog precisa ser criado.
Sugestão: /cry-new-kata "gerar changelog"
```

**Com Kata explícito:**

```
/cry-new-cry "traduzir documento" kata-translate --clade documentation/i18n
```

## Restrições

- Todo Cry deve referenciar um Kata — se o Kata não existe, sinalizar como pendência
- Sempre executa `kata-create-cry` (nunca cria diretamente)
- Sempre cria nos três idiomas obrigatórios

## Diferença de Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Natureza** | Invocação rápida (1 comando) | Procedimento completo (6 passos) |
| **Complexidade** | Baixa (ação + kata) | Alta (design de comando, prompt, validação) |
| **Configura agente?** | Não | Sim (define comportamento) |
| **Exemplo** | `/cry-new-cry "gerar changelog"` | Workflow de 6 passos com checklist |

## Referências

- `kata-create-cry` — Procedimento executado por este Cry
- `codex-cries` — Critérios de qualidade consultados
- `templates/cry-sample.md` — Template base
