# Lexis: Requisitos de Qualidade da Issue

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Todas as issues em repositórios Guardia

## Lei

> **Toda issue em um repositório Guardia DEVE usar um dos templates aprovados (feature-request, epic, user-story-for-api, user-story-for-frontend, tech-task, bug, plan), DEVE ter pelo menos uma label da lista aprovada correspondente ao seu tipo, DEVE ter um GitHub Issue Type definido (Feature, Task, Bug, Epic) compatível com o template usado, DEVE responder explicitamente: por quê (motivação e impacto), o quê (objetivo e escopo) e como (abordagem de implementação ou definição de pronto), e — para toda issue não-Epic — DEVE carregar a label `status: todo` imediatamente após a criação. O assignee é capturado na transição `todo → development` por `warrior-athena` (per `lex-agent-planning`), NÃO no momento da criação: issues em `status: todo` PODEM permanecer sem assignee. Nenhum branch PODE ser criado e nenhum PR PODE ser aberto para uma issue que não esteja em conformidade com esses requisitos.**

## Cobertura

- **Aplica-se a:** todas as issues em todos os repositórios Guardia.
- **Agentes vinculados:** desenvolvedores, agentes de IA (warrior-athena, warrior-apollo, warrior-hephaestus, warrior-eunomia) que criam ou validam issues.
- **Exceções:** issues geradas automaticamente pelo Dependabot ou por ferramentas de varredura de segurança, que seguem seu próprio formato. Toda outra exceção exige justificativa explícita registrada na própria issue.

## Regras

### 1. Templates aprovados

Toda issue DEVE usar um dos seguintes templates (localizados em `.ahrena/contributing_templates/`):

| Template | Quando usar |
|----------|-------------|
| `feature-request` | Nova funcionalidade, novo comportamento, nova capacidade voltada ao usuário |
| `epic` | Iniciativa grande que agrupa múltiplas histórias ou features |
| `user-story-for-api` | Feature de backend focada em API, com critérios de aceitação e especificação |
| `user-story-for-frontend` | Feature de UI/UX para a plataforma ou app |
| `bug` | Reporte de defeito em comportamento existente; reprodução + impacto + correção esperada |
| `tech-task` | Tarefa pequena e bem definida: chore, refatoração, manutenção, correção de documentação, mudança de CI |
| `plan` | Sub-issue de Plano executável sob uma Issue pai (User Story / Bug / Tech Task), por `lex-agent-planning` |

Issues sem template são incompletas e DEVEM ser atualizadas antes de qualquer branch ou PR referenciá-las.

### 2. Labels obrigatórias

Toda issue DEVE ter pelo menos uma label aplicada. A label DEVE corresponder ao tipo da issue:

| Template | Labels obrigatórias |
|----------|---------------------|
| `feature-request` | `feature request ➕` |
| `epic` | `epic` |
| `user-story-for-api` | `api`, `user story 🎯` |
| `user-story-for-frontend` | `frontend`, `user story 🎯` |
| `bug` | `bug 🐛` |
| `tech-task` | Pelo menos uma de: `documentation 📃`, `ci 🏗️`, `enhancement 🔝`, `evolvability ♻️` |
| `plan` | `plan 📋` (mais labels herdadas do contexto da Issue pai quando aplicável) |

### 3. GitHub Issue Type obrigatório

Toda issue DEVE ter um **GitHub Issue Type** definido (campo nativo do GitHub, distinto de labels). O tipo DEVE corresponder ao template usado:

| Template | Issue Type |
|----------|------------|
| `feature-request` | `Feature` |
| `epic` | `Epic` |
| `user-story-for-api` | `Feature` |
| `user-story-for-frontend` | `Feature` |
| `bug` | `Bug` |
| `tech-task` | `Task` |
| `plan` | `Task` |

> Orgs que customizam os Issue Types (e.g. `Tech Task` em vez de `Task`, `Plan` como type próprio) DEVEM manter a equivalência semântica. O mapeamento canônico desta Lex usa os nomes nativos do GitHub.

Quando a issue é criada via formulário do template (`.github/ISSUE_TEMPLATE/*.yml`), o tipo é aplicado automaticamente pelo campo `type:` do template. Quando a issue é criada via CLI (`gh issue create`), o agente DEVE aplicar o tipo após a criação:

```bash
# Após criar a issue, aplicar o tipo via API REST
gh api -X PATCH "repos/$OWNER/$REPO/issues/$ISSUE_NUMBER" -f type=Task
```

Issues sem Issue Type definido NÃO satisfazem esta Lex e bloqueiam a criação de branch/PR.

### 4. Assignee NÃO é requisito de criação

Issue em `status: todo` PODE permanecer sem assignee. O assignee captura **quem assume a execução** do trabalho e é aplicado na transição `todo → development` por `warrior-athena` (per `lex-agent-planning` HARD-GATE de execução):

```bash
# Quem pega o trabalho aplica o assignee na transição:
gh issue edit $ISSUE_NUMBER \
  --add-assignee "@me" \
  --remove-label "status: todo" \
  --add-label "status: development"
```

Casos em que o assignee PODE ser aplicado já na criação:
- Issue criada com intenção declarada de execução imediata pelo próprio autor.
- Issue derivada de incidente cujo on-call já está designado.

Em todos os outros casos, manter sem assignee até `todo → development` é o caminho canônico — evita ruído de "ownership fantasma" em issues que ficam dias na pilha sem ninguém realmente comprometido.

### 5. Conteúdo obrigatório: Por quê / O quê / Como

Toda issue DEVE responder a três perguntas, explicitamente ou por meio das seções do template:

| Pergunta | O que cobre | Mapeamento no template |
|----------|-------------|------------------------|
| **Por quê** | Motivação, impacto, problema sendo resolvido | "Why is this important?" / seção "Why" |
| **O quê** | Objetivo, escopo, o que muda | "Objective" / seção "What" |
| **Como** | Abordagem de implementação, resultado esperado, definição de pronto | "How should it work?" / seção "How" |

Para `tech-task`, `bug` e `plan`: as três perguntas são as seções diretas do template.

Para os demais templates: as seções mapeiam para essas perguntas — o **Objective** (user story) responde O quê, **Why is this important** responde Por quê, e **How can it be implemented** / critérios de aceitação respondem Como.

### 6. `status: todo` é invariante de criação (não-Epic)

Toda issue **não-Epic** DEVE carregar a label `status: todo` imediatamente após ser criada. Epic é decomposto em child Issues e não participa do Eixo A do `lex-issue-status` — ver `lex-issue-status` Regra 7.

A label é aplicada de uma das três formas:

1. **Via template `.github/ISSUE_TEMPLATE/*.yml`**: o campo `labels:` do template declara `status: todo` e o GitHub aplica na submissão. Caminho canônico para criação via UI.
2. **Via `kata-contributing-issue` (CLI/MCP)**: o kata aplica `status: todo` como passo final, depois de aplicar o type e as labels do template.
3. **Manualmente após `gh issue create`**:
   ```bash
   gh issue edit $ISSUE_NUMBER --add-label "status: todo"
   ```

Issues no fluxo Issue-Driven sem `status: todo` (excluindo Epic) violam esta Lex e bloqueiam qualquer transição subsequente — não há "limbo" entre criação e `todo`.

### 7. Agentes seguem as mesmas regras

Agentes de IA que criam issues (via MCP ou CLI) DEVEM:

1. Usar o template adequado via `kata-contributing-issue`
2. Aplicar as labels obrigatórias durante a criação
3. Aplicar o Issue Type correspondente ao template
4. Para issues não-Epic, aplicar a label `status: todo` como passo final da criação
5. Preencher todas as seções obrigatórias (Por quê / O quê / Como) antes de submeter

O assignee é deliberadamente omitido desta lista — é responsabilidade da transição `todo → development`, executada por `warrior-athena` per `lex-agent-planning`.

### 8. Branch e PR bloqueados até a issue estar em conformidade

Conforme `lex-issue-first` e `lex-git-branches`, nenhum branch PODE ser criado e nenhum PR PODE ser aberto se a issue associada:

- Não usar um dos templates aprovados
- Não tiver pelo menos uma label obrigatória
- Não tiver Issue Type definido
- Não carregar `status: todo` (excluindo Epic)
- Não responder Por quê, O quê e Como

Note que **assignee não está nesta lista** — é cobrado na transição `todo → development`, não na criação.

## HARD-GATE (criação)

Conforme [`lex-hard-gate-pattern`](framework/pt-BR/_foundation/quality/lexis/lex-hard-gate-pattern.md), o bloqueio textual de criação desta Lex é canonicamente expresso como:

```
<HARD-GATE>
warrior-athena, warrior-apollo, warrior-hephaestus, warrior-eunomia e
qualquer outro agente NÃO DEVE criar branch ou abrir PR para uma issue
sem que ela satisfaça TODOS os critérios canônicos:

  (a) Usa um dos templates aprovados (feature-request, epic,
      user-story-for-api, user-story-for-frontend, tech-task, bug, plan)
  (b) Tem pelo menos uma label obrigatória correspondente ao template
  (c) Tem GitHub Issue Type definido (Feature, Task, Bug, Epic)
      compatível com o template
  (d) Carrega a label `status: todo` (não-Epic) imediatamente após
      a criação
  (e) Responde explicitamente Por quê, O quê e Como

Esta regra se aplica a TODA issue, independentemente de:
  - tamanho percebido ("é uma mudança trivial")
  - urgência ("incêndio em produção")
  - quem solicitou ("o CEO pediu")
  - confiança do time ("já testamos")

Exceção única declarada: issues geradas automaticamente pelo
Dependabot ou ferramentas de varredura de segurança seguem seu
próprio formato e estão isentas. Toda outra exceção exige
justificativa explícita registrada na própria issue.
</HARD-GATE>
```

## HARD-GATE (transição `todo → development`)

A captura de assignee — anteriormente exigida no gate de criação — passa a ser cobrada na transição que sinaliza compromisso real de execução. Esta Lex declara o gate; `lex-agent-planning` o invoca operacionalmente.

```
<HARD-GATE>
warrior-athena e qualquer outro agente NÃO DEVE transicionar uma issue
não-Epic de `status: todo` para `status: development` sem aplicar
pelo menos um assignee na mesma operação.

Pré-condições obrigatórias para aplicar a transição:
  (a) Estado de origem é `status: todo`
  (b) Estado de destino é `status: development`
  (c) Pelo menos um assignee é adicionado na mesma operação
      (`gh issue edit --add-assignee` ou MCP equivalente)
  (d) Issue não é Epic (Epic não participa do Eixo A — ver
      `lex-issue-status` Regra 7)

Esta regra se aplica a TODA transição `todo → development`,
independentemente de:
  - tamanho percebido ("é uma mudança trivial")
  - urgência ("incêndio em produção")
  - quem solicitou ("o CEO pediu")
  - confiança do time ("já testamos")

Exceção declarada: Nenhuma. Assignee é invariante na entrada
de `development`.
</HARD-GATE>
```

## Exemplos

### Corretos

```
Issue: "Adicionar kata-setup-gpg-signing ao framework de contribuição"
Template: tech-task
Labels: documentation 📃, status: todo
Issue Type: Task
Assignee: (vazio — será aplicado em todo → development)
Por quê: Contribuidores precisam configurar a assinatura GPG para satisfazer lex-signed-commits; ainda não existe um guia passo a passo.
O quê: Criar kata-setup-gpg-signing cobrindo instalação do GPG, geração de chave, configuração do git e exportação para o GitHub.
Como: Seguir o fluxo de geração de chave GPG; cobrir macOS, Linux e Windows; adicionar etapa de verificação.
```

```
# Transição todo → development (assignee aplicado na mesma operação)
gh issue edit 42 \
  --add-assignee "@me" \
  --remove-label "status: todo" \
  --add-label "status: development"
```

### Incorretos

```
Issue: "corrigir o bug de autenticação"
Template: nenhum
Labels: nenhuma
Conteúdo: uma linha, sem Por quê / O quê / Como

→ ❌ Criação de branch bloqueada por lex-git-branches
→ ❌ PR rejeitado por lex-issue-first
→ ❌ Falha precondition (a), (b), (c), (d), (e) do HARD-GATE de criação
```

```
# ❌ Transição todo → development sem aplicar assignee
gh issue edit 42 --remove-label "status: todo" --add-label "status: development"
# Falha precondition (c) do HARD-GATE de transição — execução sem dono declarado
```

```
# ❌ Issue criada sem status: todo
gh issue create --title "feat: ..." --label "feature request ➕"
# Issue fica em limbo entre criação e o fluxo — falha precondition (d) do gate de criação
```

## Validação Automatizada

- **Ferramenta:** `kata-contributing-issue` aplica template, labels, Issue Type e `status: todo` na criação; templates `.github/ISSUE_TEMPLATE/*.yml` declaram `type:` e `labels:` para auto-aplicar Issue Type + `status: todo`; checklist de revisão do PR verifica se a issue associada está completa em todos os campos obrigatórios; `kata-quality-gate` no Gate 2 verifica presença de assignee na transição `todo → development` registrada no histórico da issue.
- **Quando:** na criação da issue (via kata ou template); na transição `todo → development` (cobrança do assignee); na criação do PR (via verificação do `lex-issue-first`).
- **Métrica:** 0 PRs abertos referenciando uma issue sem template, labels, Issue Type ou `status: todo`; 0 transições `todo → development` sem assignee; 100% das issues criadas via kata em conformidade na primeira submissão.
