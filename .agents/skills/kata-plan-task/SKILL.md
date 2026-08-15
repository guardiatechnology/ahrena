---
name: kata-plan-task
description: "Planejar Tarefa. Criação de uma sub-issue Plan vinculada a uma Issue parent, conforme lex-agent-planning (modelo hierárquico Issue → Plan → PR)"
---

# Kata: Planejar Tarefa

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Criação de uma sub-issue Plan vinculada a uma Issue parent, conforme `lex-agent-planning` (modelo hierárquico Issue → Plan → PR)

## Workflow

```
Progresso:
- [ ] 1. Confirmar Issue parent existe e está bem formada
- [ ] 2. Rascunhar o Plan com o usuário e confirmar
- [ ] 3. Criar a sub-issue Plan (Task) vinculada à Issue parent
- [ ] 4. Preencher o body da sub-issue com o plano canônico
- [ ] 5. Verificar Issue Type pós-criação
- [ ] 6. Aplicar label `status: todo` e confirmar ao usuário
```

### Passo 1: Confirmar Issue parent existe e está bem formada

Antes de criar a sub-issue Plan, verificar que a Issue parent `{N}` existe e satisfaz `lex-issue-first` e `lex-issue-quality`:

```bash
# Preferido — via MCP
mcp.github.get_issue(owner=owner, repo=repo, issue_number=N)

# Fallback — via gh
gh issue view {N} --repo {owner}/{repo} --json number,title,state,labels,body,assignees
```

Verificar:

- Issue parent existe e está aberta (state `open`).
- Body contém Why/What/How preenchidos (per `lex-issue-quality`).
- Labels obrigatórias do template estão presentes.
- Issue Type compatível (`Feature` para User Story; `Bug` para bug; `Task` para Tech Task).

Se algum critério falhar, **abortar** com mensagem orientando a invocar `kata-contributing-issue` para abrir/corrigir a Issue parent primeiro.

### Passo 2: Rascunhar o Plan com o usuário e confirmar

Com base nos inputs (`plan_summary`, `plan_objective`, `plan_steps`, `plan_dependencies`, `plan_risks`, `plan_open_questions`), montar o body candidato (per schema da seção *Schema do body da sub-issue Plan* em `lex-agent-planning`):

```markdown
## Summary

{plan_summary — 2-4 frases}

Parent: #{N}

## Plan

### Objective
{plan_objective — 1-3 frases}

### Steps
- [ ] Step 1
- [ ] Step 2
...

### Dependencies
{plan_dependencies ou "None"}

### Risks
{plan_risks ou "None identified"}

### Open Questions
{plan_open_questions ou "None"}
```

Apresentar o rascunho ao usuário:

> "Este é o Plan vinculado à #{N}. Quer ajustar algo antes de eu abrir a sub-issue?"

Aguardar confirmação. Incorporar ajustes. **Não criar a sub-issue antes da confirmação.**

### Passo 3: Criar a sub-issue Plan (Task) vinculada à Issue parent

Preferir MCP `create_issue` per `lex-mcp` regra 1:

```python
# Preferido — via MCP
result = mcp.github.create_issue(
    owner=owner,
    repo=repo,
    title="plan: {short title derivado de plan_summary}",
    body=body_content,
    labels=["plan 📋"] + parent_labels_mirror,
    type="Task",
)
M = result["number"]
M_db_id = result["id"]  # node ID necessário para sub-issue link
```

Fallback CLI per `lex-mcp` regra 4:

```bash
# Fallback CLI — capturar number e database ID atomicamente da resposta do create
result=$(gh issue create \
  --repo {owner}/{repo} \
  --title "plan: {short title}" \
  --body-file /tmp/plan-{M}-body.md \
  --label "plan 📋" \
  --label "{mirror parent labels}" \
  --json number,id)

M=$(echo "$result" | jq -r .number)
M_db_id=$(echo "$result" | jq -r .id)
```

Vincular a sub-issue como sub-issue da Issue parent:

```bash
gh api -X POST repos/{owner}/{repo}/issues/{N}/sub_issues -F sub_issue_id={M_db_id}
```

Capturar `{M}` (número da sub-issue Plan) para os próximos passos.

### Passo 4: Preencher o body da sub-issue com o plano canônico

Se o body já foi gravado no Passo 3 via MCP `create_issue` com `body=body_content`, este passo é confirmatório. Caso o template Plan padrão tenha sido aplicado pelo GitHub (em vez do body candidato), gravar via update:

```python
# Preferido — via MCP
mcp.github.update_issue(
    owner=owner, repo=repo, issue_number=M,
    body=body_content,
)

# Fallback CLI
gh issue edit {M} --repo {owner}/{repo} --body-file /tmp/plan-{M}-body.md
```

Validar que o body gravado contém as 5 seções canônicas: Summary, Plan → Objective, Steps, Risks, Dependencies, Open Questions.

### Passo 5: Verificar Issue Type pós-criação

Per `lex-issue-type-verified`, conferir que o tipo nativo é `Task`:

```bash
gh api repos/{owner}/{repo}/issues/{M} --jq '.type.name'
```

Se vazio ou diferente de `Task`, aplicar manualmente:

```bash
gh api -X PATCH repos/{owner}/{repo}/issues/{M} -f type=Task
```

### Passo 6: Aplicar label `status: todo` e confirmar ao usuário

```bash
gh issue edit {M} --repo {owner}/{repo} --add-label "status: todo"
```

Confirmar ao usuário:

> "Plan registrado em #{M} (sub-issue de #{N}). Body canônico, label `status: todo` aplicada, Issue Type `Task` verificado. Pronto para `todo → development` quando você decidir iniciar a execução."

Branch, worktree e assignee **não** são aplicados neste kata — pertencem a `todo → development`, owned por Athena.

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Sub-issue Plan | GitHub Issue (Task) | `{owner}/{repo}#{M}`, sub-issue de `#{N}` |
| Body canônico | Markdown (Summary + Plan section) | Body da sub-issue `{M}` |
| Label `status: todo` | GitHub label | Sub-issue `{M}` |
| Issue Type `Task` | GitHub Issue Type | Sub-issue `{M}` |
| URL da sub-issue | Link | Apresentado ao usuário |

## Exemplo de Execução

### Input de Exemplo

```
parent_issue_number: 200
plan_summary: "Refatorar o agregado Ledger para event sourcing, separando
  comandos (write-side) de leitura (read-side projection)."
plan_objective: "Entregar a primeira fatia executável da User Story #200:
  Ledger reescrito como aggregate event-sourced, com factory + repository."
plan_steps:
  - "Step 1 — Modelar LedgerEvent base class"
  - "Step 2 — Reescrever Ledger.apply() como event projection"
  - "Step 3 — Repository persistindo events em vez de state"
  - "Step 4 — Migration helper para legacy state → events"
  - "Step 5 — Testes de aggregate"
plan_dependencies: "None"
plan_risks: "- migration helper pode falhar em datasets com inconsistência
  histórica — mitigado por dry-run + checksum."
plan_open_questions: "None"
```

### Sub-issue Plan #201 criada

```markdown
## Summary

Refatorar o agregado Ledger para event sourcing, separando comandos
(write-side) de leitura (read-side projection).

Parent: #200

## Plan

### Objective
Entregar a primeira fatia executável da User Story #200: Ledger
reescrito como aggregate event-sourced, com factory + repository.

### Steps
- [ ] Step 1 — Modelar LedgerEvent base class
- [ ] Step 2 — Reescrever Ledger.apply() como event projection
- [ ] Step 3 — Repository persistindo events em vez de state
- [ ] Step 4 — Migration helper para legacy state → events
- [ ] Step 5 — Testes de aggregate

### Dependencies
None

### Risks
- migration helper pode falhar em datasets com inconsistência
  histórica — mitigado por dry-run + checksum.

### Open Questions
None
```

### Confirmação ao usuário

```
Agente: "Plan registrado em #201 (sub-issue de #200).
  Body canônico, label `status: todo` aplicada, Issue Type `Task` verificado.
  Pronto para `todo → development` quando você decidir iniciar a execução."
```

## Restrições

- **Nunca aplicar `status: todo` antes do Passo 6** — HARD-GATE de Gate 1 em `lex-agent-planning` exige os 4 passos canônicos concluídos.
- **Nunca criar a sub-issue Plan sem Issue parent confirmada** — sem Issue parent aberta e em conformidade, não há Plan a criar; invocar `kata-contributing-issue` antes.
- **Nunca criar branch, worktree ou aplicar assignee neste kata** — pertencem a `todo → development` (Athena, Gate 2 de `lex-agent-planning`).
- **Nunca criar arquivo em `.claude/plans/` ou `.cursor/plans/` neste kata** — cache local é materializado por `kata-load-plan-from-subissue` em momento posterior, e a kata de load recusa se a sub-issue não existir.
- **Nunca omitir Summary, Parent ou seções do Plan no body** — body sem Summary, Objective, Steps, Risks, Dependencies, Open Questions não satisfaz Gate 1 precondition (c).
- **Preferir MCP > CLI** — per `lex-mcp` regra 1; CLI `gh issue create` é fallback per regra 4.
