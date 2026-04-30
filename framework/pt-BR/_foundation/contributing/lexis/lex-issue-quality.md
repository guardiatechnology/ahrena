# Lexis: Requisitos de Qualidade da Issue

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrantável | **Escopo:** Todas as issues em repositórios Guardia

## Lei

> **Toda issue em um repositório Guardia DEVE usar um dos templates aprovados (feature-request, epic, user-story-for-api, user-story-for-frontend, simple-task), DEVE ter pelo menos uma label da lista aprovada correspondente ao seu tipo, DEVE ter um GitHub Issue Type definido (Feature, Task, Bug, Epic) compatível com o template usado, DEVE ter pelo menos um assignee — por padrão o autor da issue —, e DEVE responder explicitamente: por quê (motivação e impacto), o quê (objetivo e escopo) e como (abordagem de implementação ou definição de pronto). Nenhum branch PODE ser criado e nenhum PR PODE ser aberto para uma issue que não esteja em conformidade com esses requisitos.**

## Cobertura

- **Aplica-se a:** todas as issues em todos os repositórios Guardia.
- **Agentes vinculados:** desenvolvedores, agentes de IA (warrior-athena, warrior-apollo, warrior-hephaestus) que criam ou validam issues.
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
| `simple-task` | Tarefa pequena e bem definida: chore, refatoração, manutenção, correção de documentação, mudança de CI |

Issues sem template são incompletas e DEVEM ser atualizadas antes de qualquer branch ou PR referenciá-las.

### 2. Labels obrigatórias

Toda issue DEVE ter pelo menos uma label aplicada. A label DEVE corresponder ao tipo da issue:

| Template | Labels obrigatórias |
|----------|---------------------|
| `feature-request` | `feature request ➕` |
| `epic` | `epic` |
| `user-story-for-api` | `api`, `user story 🎯` |
| `user-story-for-frontend` | `frontend`, `user story 🎯` |
| `simple-task` | Pelo menos uma de: `documentation 📃`, `ci 🏗️`, `enhancement 🔝`, `evolvability ♻️` |

### 3. GitHub Issue Type obrigatório

Toda issue DEVE ter um **GitHub Issue Type** definido (campo nativo do GitHub, distinto de labels). O tipo DEVE corresponder ao template usado:

| Template | Issue Type |
|----------|------------|
| `feature-request` | `Feature` |
| `epic` | `Epic` |
| `user-story-for-api` | `Feature` |
| `user-story-for-frontend` | `Feature` |
| `simple-task` | `Task` |

Quando a issue é criada via formulário do template (`.github/ISSUE_TEMPLATE/*.yml`), o tipo é aplicado automaticamente pelo campo `type:` do template. Quando a issue é criada via CLI (`gh issue create`), o agente DEVE aplicar o tipo após a criação:

```bash
# Após criar a issue, aplicar o tipo via API REST
gh api -X PATCH "repos/$OWNER/$REPO/issues/$ISSUE_NUMBER" -f type=Task
```

Issues sem Issue Type definido NÃO satisfazem esta Lex e bloqueiam a criação de branch/PR.

### 4. Assignee obrigatório

Toda issue DEVE ter pelo menos um assignee. Por padrão, o assignee é **o autor da issue** (a pessoa que a abriu). Quando a issue é criada via CLI sem template, o agente DEVE aplicar o assignee na criação ou imediatamente após:

```bash
# Na criacao
gh issue create ... --assignee "@me"

# Ou apos a criacao
gh issue edit $ISSUE_NUMBER --add-assignee "@me"
```

Re-atribuição posterior para outra pessoa é permitida quando o trabalho é delegado, mas a issue NÃO PODE permanecer sem assignee.

### 5. Conteúdo obrigatório: Por quê / O quê / Como

Toda issue DEVE responder a três perguntas, explicitamente ou por meio das seções do template:

| Pergunta | O que cobre | Mapeamento no template |
|----------|-------------|------------------------|
| **Por quê** | Motivação, impacto, problema sendo resolvido | "Why is this important?" / seção "Why" |
| **O quê** | Objetivo, escopo, o que muda | "Objective" / seção "What" |
| **Como** | Abordagem de implementação, resultado esperado, definição de pronto | "How should it work?" / seção "How" |

Para `simple-task`: as três perguntas são as seções diretas do template.

Para os demais templates: as seções mapeiam para essas perguntas — o **Objective** (user story) responde O quê, **Why is this important** responde Por quê, e **How can it be implemented** / critérios de aceitação respondem Como.

### 6. Branch e PR bloqueados até a issue estar em conformidade

Conforme `lex-issue-first` e `lex-git-branches`, nenhum branch PODE ser criado e nenhum PR PODE ser aberto se a issue associada:

- Não usar um dos templates aprovados
- Não tiver pelo menos uma label obrigatória
- Não tiver Issue Type definido
- Não tiver assignee
- Não responder Por quê, O quê e Como

### 7. Agentes devem seguir as mesmas regras

Agentes de IA que criam issues (via MCP ou CLI) DEVEM:

1. Usar o template adequado via `kata-contributing-issue`
2. Aplicar as labels obrigatórias durante a criação
3. Aplicar o Issue Type correspondente ao template
4. Aplicar pelo menos um assignee (default: `@me`)
5. Preencher todas as seções obrigatórias (Por quê / O quê / Como) antes de submeter

## Exemplos

### Corretos

```
Issue: "Adicionar kata-setup-gpg-signing ao framework de contribuição"
Template: simple-task
Labels: documentation 📃
Por quê: Contribuidores precisam configurar a assinatura GPG para satisfazer lex-signed-commits; ainda não existe um guia passo a passo.
O quê: Criar kata-setup-gpg-signing cobrindo instalação do GPG, geração de chave, configuração do git e exportação para o GitHub.
Como: Seguir o fluxo de geração de chave GPG; cobrir macOS, Linux e Windows; adicionar etapa de verificação.
```

### Incorretos

```
Issue: "corrigir o bug de autenticação"
Template: nenhum
Labels: nenhuma
Conteúdo: uma linha, sem Por quê / O quê / Como

→ ❌ Criação de branch bloqueada por lex-git-branches
→ ❌ PR rejeitado por lex-issue-first
```

## Validação Automatizada

- **Ferramenta:** `kata-contributing-issue` aplica template, labels, Issue Type e assignee na criação; templates `.github/ISSUE_TEMPLATE/*.yml` declaram `type:` para auto-aplicar Issue Type; checklist de revisão do PR verifica se a issue associada está completa em todos os campos obrigatórios.
- **Quando:** na criação da issue (via kata ou template); na criação do PR (via verificação do lex-issue-first).
- **Métrica:** 0 PRs abertos referenciando uma issue sem template, labels, Issue Type ou assignee; 100% das issues criadas via kata em conformidade na primeira submissão.
