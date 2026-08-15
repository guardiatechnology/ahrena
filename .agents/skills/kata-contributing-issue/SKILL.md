---
name: kata-contributing-issue
description: "Abrir issue no repositório (template por tipo). Criar issue no repositório de origem via GitHub MCP"
---

# Kata: Abrir issue no repositório (template por tipo)

> **Prefix:** `kata-` | **Type:** Skill Repetível | **Scope:** Criar issue no repositório de origem via GitHub MCP

## Entradas

| Entrada | Obrigatório | Descrição |
|---------|:-----------:|-----------|
| Tipo | Sim* | `feature-request` \| `epic` \| `user-story-for-api` \| `user-story-for-frontend` \| `tech-task`. *Inferido do cry invocante se não fornecido.* |
| Título (resumo) | Não | Resumo breve do issue. Se omitido, o agente o compõe a partir do contexto. |
| Contexto do usuário | Não | Informações adicionais para preencher os placeholders do template. |

### Tabela: tipo → template → labels obrigatórios → Issue Type

| Tipo | Arquivo de template | Labels obrigatórios | GitHub Issue Type |
|------|---------------------|---------------------|-------------------|
| feature-request | `feature-request.md` | `feature request ➕` | Feature |
| epic | `epic.md` | `epic` | Feature |
| user-story-for-api | `user-story-for-api.md` | `api`, `user story 🎯` | Feature |
| user-story-for-frontend | `user-story-for-frontend.md` | `frontend`, `user story 🎯` | Feature |
| tech-task | `tech-task.md` | Pelo menos um de: `documentation 📃`, `ci 🏗️`, `enhancement 🔝`, `evolvability ♻️` | Task |

## Fluxo de Trabalho

```
Progresso:
- [ ] 1. Resolver o tipo do issue
- [ ] 2. Carregar template .md
- [ ] 3. Preencher seções/placeholders com o usuário
- [ ] 4. Criar issue via GitHub MCP (ou gh)
- [ ] 5. Definir GitHub Issue Type via GraphQL
- [ ] 6. Aplicar label `status: todo` (Gate 1 de lex-agent-planning)
- [ ] 7. Verificação final
```

### Passo 1: Resolver o tipo do issue

1. Se o tipo foi passado explicitamente (por exemplo, pelo cry), usá-lo.
2. Caso contrário, perguntar ao usuário qual tipo deseja: feature request, epic, user story (API), user story (frontend) ou simple task.
3. Mapear para o nome do arquivo de template, labels obrigatórios e GitHub Issue Type conforme a tabela acima.

### Passo 2: Carregar template .md

1. Caminho canônico: `.ahrena/contributing_templates/<arquivo>.md` (por exemplo, `feature-request.md`).
2. Se não existir em `.ahrena/`, usar fallback: `framework/templates/contributing_templates/<arquivo>.md` ou `.github/ISSUE_TEMPLATE/` quando aplicável.
3. Ler o conteúdo e identificar seções e placeholders (por exemplo, `{user_role}`, `{specific_objective}`).

### Passo 3: Preencher seções/placeholders com o usuário

1. Para cada seção obrigatória do template, obter as informações necessárias do usuário ou do contexto.
2. Substituir placeholders e preencher checkboxes quando aplicável.
3. Compor o título do issue (por exemplo, "feat/ resumo" para feature request; resumo breve para epic/user story).
4. Construir o corpo em Markdown com o template preenchido.

### Passo 4: Criar issue via GitHub MCP (ou gh)

1. Determinar os labels obrigatórios conforme a tabela acima. Para `tech-task`, perguntar ao usuário qual label se aplica se não estiver claro pelo contexto.
2. **Preferencial:** Usar GitHub MCP (servidor que expõe a criação de issues). Por exemplo, servidor `project-0-ahrena-github`, ferramenta `issue_write` com: `method`: `create`; `owner`; `repo`; `title`; `body`; `labels` — **obrigatório**, conforme `lex-issue-quality`. **Não** definir `assignees` — assignee é aplicado em `todo → development` per Gate 2 de `lex-agent-planning`.
3. **Fallback:** Se o MCP estiver indisponível, usar:
   ```bash
   gh issue create \
     --title "..." \
     --body "..." \
     --label "nome-do-label"
   ```
4. Registrar o número do issue e o node ID retornados pela API — necessários para o Passo 5.

### Passo 5: Definir GitHub Issue Type via GraphQL

O CLI `gh issue create` não suporta `--type`. Defina o Issue Type imediatamente após a criação usando a API GraphQL.

```bash
# Obter o node ID do issue (se não retornado pelo Passo 4)
ISSUE_ID=$(gh issue view $ISSUE_NUMBER --repo $OWNER/$REPO --json id -q .id)

# Definir Issue Type (substituir ISSUE_TYPE_ID pelo valor da tabela abaixo)
gh api graphql -f query="
  mutation {
    updateIssue(input: {id: \"$ISSUE_ID\", issueTypeId: \"$ISSUE_TYPE_ID\"}) {
      issue { number }
    }
  }
"
```

**IDs de Issue Type** (específicos do repositório — verificar via `codex-labels`):

| GitHub Issue Type | ID |
|-------------------|----|
| Task | `IT_kwDOED9Qy84B7pBh` |
| Bug | `IT_kwDOED9Qy84B7pBi` |
| Feature | `IT_kwDOED9Qy84B7pBj` |

### Passo 6: Aplicar label `status: todo` (Gate 1 de lex-agent-planning)

Per `lex-agent-planning`, toda Issue recém-criada DEVE receber a label `status: todo` como passo final do gate de criação. Aplicar via `gh`:

```bash
gh issue edit $ISSUE_NUMBER --repo $OWNER/$REPO --add-label "status: todo"
```

Confirmar que a label foi aplicada:

```bash
gh issue view $ISSUE_NUMBER --repo $OWNER/$REPO --json labels --jq '[.labels[].name] | join(", ")'
```

Este passo é a **trilha procedural** do invariante de auto-aplicação. A kata é o caminho canônico para criar Issue; sem este passo, a Issue nasce sem `status: todo` e fica fora do ciclo de vida unificado de `lex-agent-planning`.

### Passo 7: Verificação final

- [ ] O issue foi criado com sucesso
- [ ] Título e corpo refletem o template preenchido
- [ ] Labels obrigatórios foram aplicados conforme `lex-issue-quality`
- [ ] O GitHub Issue Type está definido (Task ou Feature conforme o template)
- [ ] A label `status: todo` foi aplicada per `lex-agent-planning` (Gate 1)
- [ ] **Nenhum** assignee aplicado (assignee é commitment de `todo → development`, owned por Athena)
- [ ] O link do issue foi apresentado ao usuário

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Issue | GitHub Issue | Repositório de origem |
| URL do issue | Link | Apresentado ao usuário |

## Restrições

- Sempre usar um dos 5 tipos e o template correspondente; não criar um issue sem o template ou sem os labels obrigatórios.
- **Nunca aplicar assignee neste kata.** Assignee é commitment de execução, aplicado em `todo → development` por warrior-athena per Gate 2 de `lex-agent-planning`.
- Sempre definir o GitHub Issue Type no Passo 5 imediatamente após a criação.
- Sempre aplicar `status: todo` no Passo 6 como trilha procedural do invariante de auto-aplicação per `lex-agent-planning`.
- Se nem `.ahrena/contributing_templates/` nem o fallback existirem, informar o usuário e sugerir executar o install do Ahrena ou criar o template manualmente.
- Em caso de falha do MCP, apresentar o erro e sugerir criação manual via `gh issue create` ou pela UI do GitHub.
