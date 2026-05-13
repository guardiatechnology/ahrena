# Kata: Decompor Issue em Sub-issues Plan

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Decomposição de uma Issue parent (User Story, Bug, Tech Task) em N sub-issues Plan executáveis, conforme `lex-agent-planning`

## Objetivo

Quebrar uma Issue parent em **1..N sub-issues Plan** (Issue Type Task), cada uma representando uma unidade executável de trabalho com body canônico (Summary + Plan section) e label `status: todo`. Procedimento canônico de `warrior-eunomia` quando o escopo da Issue parent não cabe em um único PR ou quando o trabalho precisa ser distribuído entre múltiplos agentes/sessões.

A decomposição **invoca `kata-plan-task` por sub-issue** — toda a lógica de criação canônica (template, labels, Issue Type, body, vinculação sub-issue) é delegada à kata de criação individual. Este kata adiciona a camada de **estratégia de decomposição** (como dividir o escopo) e a camada de **orquestração** (criar N sub-issues consistentes em sequência).

## Quando Usar

- Issue parent (User Story, Bug ou Tech Task) cujo escopo evidentemente não cabe em um único PR.
- Trabalho que envolve múltiplas camadas (ex.: backend + frontend + migração) onde cada camada é um PR independente.
- Trabalho com **dependências sequenciais** entre etapas onde cada etapa merece audit próprio.
- Quando Eunomia entra na fila de planejamento de uma Issue recém-criada e identifica que precisa de mais de um Plan.
- Quando o usuário diz "decompõe a #N" ou "quebra a #N em Plans".

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `parent_issue_number` | Sim | Número `{N}` da Issue parent a decompor |
| `decomposition_strategy` | Não | Estratégia explícita do usuário (ex.: "por camada", "por endpoint", "por feature flag"). Se ausente, o agente infere da estrutura da Issue parent e da análise de scope |
| `plan_drafts` | Não | Lista pré-rascunhada de Plans (cada item com `summary`, `objective`, `steps`). Se ausente, o agente rascunha em sessão com o usuário |
| `owner/repo` | Não | Repo onde a Issue parent vive. Default: repo corrente do worktree |

## Workflow

```
Progresso:
- [ ] 1. Confirmar Issue parent existe e está bem formada
- [ ] 2. Determinar a estratégia de decomposição
- [ ] 3. Rascunhar N Plans com o usuário e confirmar a decomposição
- [ ] 4. Para cada Plan: invocar kata-plan-task
- [ ] 5. Apresentar o resumo da decomposição ao usuário
```

### Passo 1: Confirmar Issue parent existe e está bem formada

Antes de decompor, verificar que a Issue parent `{N}` existe e satisfaz `lex-issue-first` e `lex-issue-quality`:

```bash
# Preferido — via MCP
mcp.github.get_issue(owner=owner, repo=repo, issue_number=N)

# Fallback — via gh
gh issue view {N} --repo {owner}/{repo} --json number,title,state,labels,body,assignees
```

Validar:

- Issue parent existe e está aberta (state `open`).
- Body contém Why/What/How (per `lex-issue-quality`).
- Labels obrigatórias do template estão presentes.
- Issue Type compatível (`Feature`, `Bug` ou `Task`).

Se algum critério falhar, abortar com mensagem orientando a invocar `kata-contributing-issue` para corrigir a Issue parent antes de decompor.

### Passo 2: Determinar a estratégia de decomposição

Se `decomposition_strategy` foi passada explicitamente, usar.

Senão, **inferir** a partir da análise do escopo da Issue parent. Estratégias comuns:

| Estratégia | Quando preferir | Exemplo de quebra |
|---|---|---|
| Por camada | Trabalho atravessa stack (backend + frontend + infra) | Plan 1: backend; Plan 2: frontend; Plan 3: migration |
| Por endpoint/feature flag | Múltiplos endpoints REST ou múltiplas flags independentes | Plan 1: POST endpoint; Plan 2: GET endpoint; Plan 3: PATCH endpoint |
| Por fase do fluxo | Trabalho tem fases sequenciais (design → impl → docs) | Plan 1: design + ADR; Plan 2: implementação; Plan 3: documentação |
| Por bounded context | Trabalho cruza contextos no DDD | Plan 1: context A; Plan 2: context B |
| Por dependência | Cadeia de pré-requisitos clara | Plan 1: spike; Plan 2: refactor de base; Plan 3: feature em cima |

Apresentar a estratégia ao usuário e pedir confirmação antes de rascunhar os Plans.

### Passo 3: Rascunhar N Plans com o usuário e confirmar a decomposição

Se `plan_drafts` foi passado, usar como ponto de partida.

Senão, rascunhar com o usuário. Para cada Plan, preencher:

| Campo | Conteúdo |
|---|---|
| `plan_summary` | 2-4 frases — fatia executável do escopo da Issue parent |
| `plan_objective` | 1-3 frases — o que este Plan entrega ao final |
| `plan_steps` | Lista atômica e verificável (mínimo 1 step) |
| `plan_dependencies` | Outros Plans desta decomposição, Issues, PRs, ou `"None"` |
| `plan_risks` | Riscos + mitigações, ou `"None identified"` |
| `plan_open_questions` | Perguntas em aberto, ou `"None"` |

Atenção especial a **dependências entre Plans da mesma decomposição**: o Plan 2 da decomposição da Issue #N pode depender do Plan 1; o Plan 3, dos Plans 1 e 2. Documentar explicitamente — vai virar `plan_dependencies` no `kata-plan-task`.

Apresentar o conjunto de Plans rascunhados ao usuário:

> "Esta é a decomposição da #{N} em {len(plans)} Plans. Quer ajustar a divisão, mesclar Plans, ou separar mais antes de eu criar as sub-issues?"

Aguardar confirmação. Incorporar ajustes. **Não criar nenhuma sub-issue antes da confirmação do conjunto completo.**

### Passo 4: Para cada Plan: invocar kata-plan-task

Para cada `plan_draft` confirmado, invocar `kata-plan-task` passando os campos preenchidos:

```python
for draft in plan_drafts:
    result = invoke("kata-plan-task",
        parent_issue_number=N,
        plan_summary=draft.summary,
        plan_objective=draft.objective,
        plan_steps=draft.steps,
        plan_dependencies=draft.dependencies,
        plan_risks=draft.risks,
        plan_open_questions=draft.open_questions,
        owner=owner,
        repo=repo,
    )
    created_plans.append(result.subissue_number)
```

`kata-plan-task` executa, por Plan, os 6 passos canônicos: confirma a Issue parent, rascunha (já confirmado), cria a sub-issue, preenche o body, verifica Issue Type, aplica `status: todo`. Cada invocação é independente — se uma falhar, as anteriores já criadas permanecem (não é transacional).

Se uma invocação falhar:

1. Capturar o erro.
2. Reportar ao usuário com a lista de Plans já criados (`created_plans`) e o Plan que falhou.
3. Oferecer: (a) tentar de novo só o que falhou, (b) pausar para investigação, (c) abortar a decomposição (Plans já criados permanecem como sub-issues órfãs até decisão manual).

### Passo 5: Apresentar o resumo da decomposição ao usuário

Após criar todas as sub-issues, apresentar:

> "Decomposição da #{N} completa. {len(created_plans)} Plans criados:
> - #{M1} — {summary truncado do Plan 1}
> - #{M2} — {summary truncado do Plan 2}
> - ...
>
> Todos com `status: todo`. Pronto para Athena iniciar `todo → development` em cada um, na ordem das dependências mapeadas."

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| N sub-issues Plan | GitHub Issues (Task) | `{owner}/{repo}#{M_i}`, cada uma sub-issue de `#{N}` |
| Bodies canônicos | Markdown (Summary + Plan section) | Body de cada sub-issue |
| Labels `status: todo` | GitHub label | Em cada sub-issue criada |
| Issue Types `Task` | GitHub Issue Type | Em cada sub-issue criada |
| Resumo da decomposição | Mensagem ao usuário com URLs | Sessão do agente |

## Exemplo de Execução

### Input de Exemplo

```
parent_issue_number: 200
decomposition_strategy: "por camada do event sourcing"
plan_drafts: (será rascunhado em sessão)
```

### Após Passo 2 (estratégia confirmada)

Estratégia: "por camada do event sourcing" — separar aggregate write-side, projection read-side, e migração legacy.

### Após Passo 3 (3 Plans rascunhados e confirmados)

```
Plan 1: Refatorar Ledger aggregate para event sourcing (write-side)
Plan 2: Implementar projection read-side
Plan 3: Migration helper legacy state → events

Dependências:
- Plan 2 depende de Plan 1
- Plan 3 depende de Plans 1 e 2
```

### Após Passo 4 (3 sub-issues Plan criadas)

```
#201 — Refatorar Ledger aggregate para event sourcing (write-side) [status: todo]
#202 — Implementar projection read-side [status: todo, depends on #201]
#203 — Migration helper legacy state → events [status: todo, depends on #201, #202]
```

### Resumo apresentado ao usuário

```
Agente: "Decomposição da #200 completa. 3 Plans criados:
  - #201 — Refatorar Ledger aggregate para event sourcing (write-side)
  - #202 — Implementar projection read-side
  - #203 — Migration helper legacy state → events

  Todos com `status: todo`. Pronto para Athena iniciar
  `todo → development` em cada um, na ordem: #201 → #202 → #203."
```

## Restrições

- **Nunca decompor sem Issue parent confirmada** — Issue parent precede qualquer Plan; sem Issue, não há decomposição.
- **Nunca pular a confirmação do conjunto completo no Passo 3** — apresentar a decomposição inteira ao usuário antes de criar a primeira sub-issue evita meia-decomposição inconsistente.
- **Nunca criar branch, worktree ou aplicar assignee neste kata** — delegado ao `kata-plan-task` (que também não os cria — pertencem a `todo → development`).
- **Nunca decompor uma Issue parent já decomposta sem checar sub-issues existentes** — antes de criar, listar sub-issues atuais (`gh api repos/{owner}/{repo}/issues/{N}/sub_issues`) e apresentar ao usuário; decisão manual para criar mais, mesclar, ou abandonar a operação.
- **Documentar dependências entre Plans da mesma decomposição** — `plan_dependencies` deve listar explicitamente os outros Plans desta decomposição quando aplicável; Athena usa essa ordem para sequenciar `todo → development`.
- **Não é transacional** — se a 3a invocação de `kata-plan-task` falhar, as 2 anteriores permanecem; recuperação é manual.

## Referências

- `lex-agent-planning` — modelo hierárquico Issue → Plan → PR; Gate 1 owned por Eunomia
- `lex-issue-quality` — requisitos da Issue parent
- `lex-issue-status` — labels canônicas; `status: todo` aplicado por `kata-plan-task`
- `lex-issue-first` — Issue parent precede a sub-issue Plan
- `lex-mcp` — preferência MCP + fallback CLI
- `codex-agent-planning` — manual operacional
- `kata-plan-task` — invocado por Plan; cria cada sub-issue
- `kata-contributing-issue` — criação da Issue parent (precondition)
- `kata-load-plan-from-subissue` — materializa cache local após decomposição (chamado depois, por Plan)
- `warrior-eunomia` — owner top-level deste kata
