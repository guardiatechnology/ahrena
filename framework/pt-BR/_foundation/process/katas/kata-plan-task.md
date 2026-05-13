# Kata: Planejar Tarefa

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Criação e manutenção de planos de tarefa por agentes, conforme `lex-agent-planning` (modelo de 3 camadas — ADR-002)

## Objetivo

Criar o plano canônico de uma tarefa antes da execução, garantindo que objetivo, escopo, etapas e dependências estejam no **body da Issue do GitHub** (canonical per ADR-002) e confirmados pelo usuário antes de qualquer ação irreversível começar. Este é o procedimento que **`warrior-eunomia` executa em modo top-level** (per plan-046 / absorção de plan-044) e que o agente da sessão segue como fallback enquanto Eunomia não estiver disponível.

Per `lex-agent-planning` HARD-GATE, o label `status: todo` só pode ser aplicado à Issue quando os 5 passos canônicos forem concluídos: (1) Issue aberta per `lex-issue-quality`; (2) Issue Type verificado per `lex-issue-type-verified`; (3) branch remota criada via `gh issue develop` e linkada à Issue; (4) worktree criado per `lex-git-worktrees`; (5) **body da Issue preenchido com o plano canônico** (Summary + Plan section).

## Quando Usar

- No início de qualquer tarefa multi-etapa.
- Antes de invocar warriors, katas em sequência, ou cries.
- Antes de modificar múltiplos arquivos em uma única sessão.
- Quando o usuário pede "faça X" e X tem mais de uma etapa discernível.

## Inputs

| Entrada | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Descrição da tarefa | Sim | O que o agente precisa fazer (pode ser vaga — o kata clarifica) |
| Repo (`owner/repo`) | Não | Default: repo corrente do worktree |
| Template de Issue | Não | `feature-request` (default), `tech-task`, `user-story-for-api`, `user-story-for-frontend` |

## Fluxo de Trabalho

```
Progresso:
- [ ] 1. Rascunhar o plano com o usuário
- [ ] 2. Abrir Issue com body canônico (Summary + Plan)
- [ ] 3. Verificar Issue Type
- [ ] 4. Criar branch via `gh issue develop`
- [ ] 5. Criar worktree
- [ ] 6. Materializar cache local via kata-load-plan-from-issue
- [ ] 7. Aplicar label `status: todo` e confirmar ao usuário
```

### Passo 1: Rascunhar o plano com o usuário

Com base na descrição da tarefa:

1. Identificar o **Objective** (por que esta tarefa existe — 1-3 frases).
2. Decompor em **Steps** atômicos e verificáveis.
3. Identificar **Dependencies** (outros planos, Issues, decisões pendentes; "None" se não houver).
4. Listar **Risks** conhecidos (mitigações; "None identified" se não houver).
5. Listar **Open Questions** (decisões pendentes que afetam execução; "None" se não houver).

Apresentar o rascunho com:

> "Este é o plano para a tarefa. Quer ajustar alguma coisa antes de eu abrir a Issue?"

Aguardar resposta. Incorporar ajustes. **Não abrir Issue antes da confirmação.**

### Passo 2: Abrir Issue com body canônico (Summary + Plan)

Construir o body conforme o schema de `lex-agent-planning`:

```markdown
## Summary

{2-4 frases descrevendo o objetivo. Costuma herdar do template.}

## Plan

### Objective
{Objective do rascunho — 1-3 frases.}

### Steps
- [ ] Step 1
- [ ] Step 2
...

### Dependencies
{Lista ou "None".}

### Risks
{Lista ou "None identified".}

### Open Questions
{Lista ou "None".}
```

Abrir a Issue (preferir MCP `create_issue` per `lex-mcp` regra 1, fallback `gh issue create`):

```bash
# MCP preferido
mcp.github.create_issue(
    owner=owner, repo=repo,
    title="{type}: {summary}",
    body=body_content,
    labels=["feature request ➕"],  # ou label do template aplicável
    assignees=["@me"],
)

# Fallback CLI
gh issue create \
  --title "{type}: {summary}" \
  --body-file /tmp/plan-body.md \
  --label "feature request ➕" \
  --assignee "@me"
```

Capturar o número `{N}` retornado.

### Passo 3: Verificar Issue Type

Per `lex-issue-type-verified`, conferir que o tipo nativo foi aplicado pelo template:

```bash
gh api repos/{owner}/{repo}/issues/{N} --jq '.type.name'
```

Se vazio (criação via CLI sem template), aplicar manualmente:

```bash
gh api -X PATCH repos/{owner}/{repo}/issues/{N} -f type={Feature|Task|Bug|Epic}
```

### Passo 4: Criar branch via `gh issue develop`

```bash
gh issue develop {N} --base main --name {type}/{N}-{slug}
```

`{slug}` é a versão kebab-case do summary (máx. 50 chars). Esse comando registra a branch como "Development" na sidebar do GitHub, satisfazendo HARD-GATE precondition (c).

### Passo 5: Criar worktree

Per `lex-git-worktrees`:

```bash
git fetch origin {type}/{N}-{slug}
git worktree add .worktrees/{N}-{slug} {type}/{N}-{slug}
```

### Passo 6: Materializar cache local via kata-load-plan-from-issue

Rodar `kata-load-plan-from-issue` passando `{N}` — materializa `.plans/{N}.md` espelhando o body recém-gravado. Isso garante que edições subsequentes da IA tenham um cache local de referência (preenche `<!-- not-flushed -->` blocks com working notes durante execução).

### Passo 7: Aplicar label `status: todo` e confirmar ao usuário

```bash
gh issue edit {N} --add-label "status: todo"
```

Confirmar ao usuário:

> "Plano registrado em #{N} (body canônico). Branch `{type}/{N}-{slug}` e worktree `.worktrees/{N}-{slug}/` prontos. Cache local em `.plans/{N}.md`. Status: todo. Posso iniciar?"

Aguardar OK do usuário antes de qualquer execução irreversível subsequente.

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Issue body canônico | Markdown (Summary + Plan section) | GitHub Issue `{N}` |
| Branch remota | git ref | `origin/{type}/{N}-{slug}` |
| Worktree | git worktree | `.worktrees/{N}-{slug}/` |
| Cache local | Markdown | `.plans/{N}.md` (gitignored) |
| Label | GitHub label | `status: todo` na Issue |

## Exemplo de Execução

### Input

```
Tarefa: migrar armazenamento do plano para o modelo Issue-as-plan
(3-layer: Issue body + .plans/ cache + .ahrena/issues/ artifacts)
```

### Passo 2 — Body gravado na Issue #96

```markdown
## Summary

**As** an Ahrena framework contributor,
**I want** to migrate plan storage to a 3-layer model,
**So that** plans live where they belong (audit in GitHub Issue,
scratch in .plans/ cache, Phase artifacts in .ahrena/issues/).

## Plan

### Objective
Refatorar a camada de armazenamento do plano para que viva em três
camadas com papéis claros: Issue body (canonical) + .plans/{N}.md
(working memory da IA, gitignored) + .ahrena/issues/{N}/ (committed Phase
artifacts).

### Steps
- [ ] Step 1 — Open Issue + branch + worktree (HARD-GATE)
- [ ] Step 2 — ADR-002
- [ ] Step 3 — Rewrite lex-agent-planning (3 langs)
- [ ] Step 3.5 — Split lex-issue-status (3 langs)
...

### Dependencies
plan-043 (PR #93) merged.

### Risks
- .plans/ perdida em fresh clone — mitigado por kata-load-plan-from-issue.
- Flush conflitante entre sessões — preflight detecta drift.
...

### Open Questions
Todas resolvidas em 2026-05-11 (ver draft).
```

### Passo 4 — Branch criada

```
$ gh issue develop 96 --base main --name feat/96-issue-as-plan-and-issues-folder
github.com/guardiatechnology/ahrena/tree/feat/96-issue-as-plan-and-issues-folder
```

### Passo 7 — Confirmação ao usuário

```
Agente: "Plano registrado em #96 (body canônico).
  Branch feat/96-issue-as-plan-and-issues-folder e worktree
  .worktrees/96-issue-as-plan-and-issues-folder/ prontos.
  Cache local em .plans/96.md.
  Status: todo. Posso iniciar?"
```

## Restrições

- **Nunca aplicar `status: todo` antes do Passo 7** — HARD-GATE de `lex-agent-planning` exige todos os 5 passos canônicos concluídos.
- **Nunca criar arquivo `.claude/plans/*.md` como canônico** — modelo legado pré-ADR-002. Body da Issue é canonical; `.plans/{N}.md` é cache regenerável.
- **Nunca pular o user OK no Passo 7** — execução irreversível subsequente exige confirmação explícita.
- **Nunca omitir Summary ou seções do Plan** — body sem Summary, Steps, Risks, Dependencies, Open Questions não satisfaz HARD-GATE precondition (e).
- **Preferir MCP > CLI** — per `lex-mcp` regra 1.

## Referências

- `lex-agent-planning` — Lei (modelo de 3 camadas)
- `lex-issue-status` — labels canônicas (`status: todo` aplicado no Passo 7)
- `lex-issue-quality` — requisitos do body da Issue
- `lex-issue-type-verified` — verificação do Issue Type
- `lex-issue-first`, `lex-git-branches`, `lex-git-worktrees` — preconditions
- `lex-mcp` — preferência MCP + fallback CLI
- `codex-agent-planning` — manual operacional
- ADR-002 — modelo de armazenamento em 3 camadas
- `kata-load-plan-from-issue` — Passo 6 (materializa cache local)
- `kata-flush-plan-to-issue` — usado em transições posteriores (não neste kata)
- `kata-create-subtasks` — modo subtask de Eunomia (decomposição de child Issue)
- `warrior-eunomia` — owner top-level deste kata
