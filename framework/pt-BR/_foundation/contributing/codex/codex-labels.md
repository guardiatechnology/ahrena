# Codex: Taxonomia de Labels

> **Prefix:** `codex-` | **Type:** Manual de Referência | **Scope:** Labels e GitHub Issue Types em repositórios Guardia

## Visão Geral

Este Codex documenta todos os labels usados nos repositórios Guardia e os GitHub Issue Types configurados para a organização. Serve como fonte única de verdade para: quais labels se aplicam a qual tipo de artefato, quais são aplicados automaticamente versus manualmente, e como o tamanho de um PR é calculado. É consultado por `kata-contributing-issue`, `kata-contributing-pr` e `lex-issue-quality`.

## Contexto

- **Domínio:** Fluxo de contribuição — governança de labels
- **Público-alvo:** Agentes de IA, desenvolvedores e colaboradores da comunidade
- **Fonte canônica:** `.github/labeling/labels.yml` em `guardiatechnology/project-automations-experiments`
- **Atualização:** Quando labels são adicionados, removidos ou redefinidos em `labels.yml`

## Conteúdo

### GitHub Issue Types

A organização Guardia configura três Issue Types no nível do repositório. Todo issue DEVE ter um Issue Type definido no momento da criação via API GraphQL (o CLI `gh issue create` não expõe `--type`).

| Issue Type | ID | Templates que o mapeiam |
|------------|----|--------------------------|
| **Task** | `IT_kwDOED9Qy84B7pBh` | `tech-task`, `plan` |
| **Bug** | `IT_kwDOED9Qy84B7pBi` | `bug` |
| **Feature** | `IT_kwDOED9Qy84B7pBj` | `feature-request`, `epic`, `user-story-for-api`, `user-story-for-frontend` |

**Definindo o Issue Type após a criação:**

```bash
# Obter o node ID do issue
ISSUE_ID=$(gh issue view $NUMBER --repo $OWNER/$REPO --json id -q .id)

# Definir o Issue Type (exemplo: Task)
gh api graphql -f query="
  mutation {
    updateIssue(input: {id: \"$ISSUE_ID\", issueTypeId: \"IT_kwDOED9Qy84B7pBh\"}) {
      issue { number }
    }
  }
"
```

### Categorias de Labels

#### 1. Labels de Tipo de Issue (Obrigatórios — aplicados na criação)

Obrigatórios conforme `lex-issue-quality`. Aplicados manualmente na criação do issue pelo agente de contribuição.

| Label | Template | Descrição |
|-------|----------|-----------|
| `feature request ➕` | `feature-request` | Nova solicitação de funcionalidade (antes da aprovação) |
| `epic` | `epic` | Grande iniciativa agrupando múltiplas histórias |
| `api` | `user-story-for-api` | Escopo de design ou implementação de API |
| `user story 🎯` | `user-story-for-api`, `user-story-for-frontend` | História com escopo voltada ao usuário |
| `frontend` | `user-story-for-frontend` | Escopo de implementação de frontend (UI/UX) |
| `documentation 📃` | `tech-task`, `plan` | Melhorias ou adições de documentação |
| `ci 🏗️` | `tech-task`, `plan` | Mudanças em CI/CD ou pipeline |
| `enhancement 🔝` | `tech-task`, `plan` | Melhoria em uma funcionalidade existente |
| `evolvability ♻️` | `tech-task`, `plan` | Refatoração, código limpo, manutenção |

#### 2. Labels de Conteúdo e Natureza

Aplicados manualmente para descrever a natureza da mudança. Podem ser aplicados a issues ou PRs.

| Label | Quando usar |
|-------|-------------|
| `bug report 🐞` | Para relatar um novo bug (somente em issue) |
| `bugfix 🔧` | PR ou issue que corrige um bug |
| `compliance 📜` | Mudança necessária para conformidade regulatória ou com padrões |
| `deprecate 🪦` | Marcando uma funcionalidade para descontinuação |
| `feature ➕` | PR de implementação após aprovação de um `feature request ➕` |
| `security 🛡️` | PR que resolve uma vulnerabilidade de segurança |
| `vulnerability 🚨` | Vulnerabilidade de segurança detectada (issue) |
| `breaking change 💥` | Mudança que introduz alteração incompatível de API; requer incremento de versão major |
| `question ✋` | Issue solicitando mais informações |
| `good first issue 🧠` | Issue adequado para novos colaboradores |

#### 3. Labels de Status

Aplicados para rastrear o estado do ciclo de vida do issue ou PR.

| Label | Quando aplicar |
|-------|----------------|
| `blocked 🚧` | Issue ou PR está bloqueado e não pode avançar |
| `duplicate !!` | Issue ou PR duplica um existente |
| `rejected ❌` | Issue ou PR foi rejeitado (fechado sem merge) |
| `wontfix 🤷‍♀️` | Issue reconhecido, mas não será tratado |
| `triage 🔍` | Issue requer triagem antes de iniciar o trabalho |

#### 4. Labels Exclusivos de PR

Aplicados exclusivamente a Pull Requests.

| Label | Quando aplicar |
|-------|----------------|
| `release ↗️` | PR de release (incremento de versão + changelog) — somente mantenedores |
| `breaking change 💥` | PR que introduz breaking change exigindo incremento de versão major |
| `security 🛡️` | PR que resolve um problema de segurança |

#### 5. Labels de Tamanho (Auto-aplicados pelo GitHub Actions)

Aplicados automaticamente pela ação de labels de tamanho de PR. **Nunca aplique manualmente.** O tamanho é calculado contando as linhas líquidas alteradas (adições + exclusões), ignorando arquivos gerados (arquivos de lock, migrations, artefatos de build).

| Label | Linhas alteradas | Descrição |
|-------|:----------------:|-----------|
| `size/XS` | 0–9 | Mudança mínima |
| `size/S` | 10–29 | Mudança pequena |
| `size/M` | 30–99 | Mudança média |
| `size/L` | 100–499 | Mudança grande |
| `size/XL` | 500–999 | Mudança extra-grande |
| `size/XXL` | 1.000+ | Mudança massiva — considere dividir |

**Orientação de tamanho de PR:**

| Tamanho | Orientação |
|---------|-----------|
| XS / S | Ideal. Ciclo de revisão rápido. |
| M | Aceitável. Mantenha o escopo focado. |
| L | Aceitável para branches de feature. Adicione contexto na descrição do PR. |
| XL | Requer justificativa. Considere dividir. |
| XXL | Deve ser dividido em PRs menores sempre que possível. |

#### 6. Labels Atribuídos por Ferramenta (Auto-aplicados)

Aplicados automaticamente com base em quem ou o quê abriu o PR.

| Label | Aplicado quando |
|-------|----------------|
| `codex ✨` | PR aberto pelo GitHub Copilot (Codex legado) |
| `copilot ✨` | PR aberto pelo GitHub Copilot |
| `cursor ✨` | PR aberto pelo Cursor AI |
| `dependabot 🤖` | PR aberto pelo Dependabot |

### Regras de Labels para PR

Ao criar um PR, o agente DEVE:

1. **Espelhar todos os labels do issue associado** — se o issue tem `documentation 📃` e `evolvability ♻️`, o PR recebe os mesmos labels.
2. **Não aplicar labels de tamanho manualmente** — o labeler do GitHub Actions os aplica automaticamente na criação e atualização do PR.
3. **Aplicar labels específicos de PR quando aplicável** — `breaking change 💥`, `security 🛡️`, `release ↗️`.
4. **Assignee** — sempre definir `--assignee "@me"` para que o PR seja atribuído ao colaborador que o criou.

**Aplicando labels a um PR via CLI:**

```bash
# Obter labels do issue associado
LABELS=$(gh issue view $ISSUE_NUMBER --repo $OWNER/$REPO --json labels --jq '[.labels[].name] | join(",")')

# Espelhar no PR (repita --label para cada um)
gh pr edit $PR_NUMBER --repo $OWNER/$REPO --add-label "$LABELS"
```

### Catálogo Completo de Labels

Catálogo completo semeado por `scripts/bootstrap_labels.sh` e por `make bootstrap-labels`. O script é idempotente (usa `gh label create --force`) e pula graciosamente quando o CLI `gh` está ausente ou não autenticado. As cores são hexadecimais sem o `#` inicial.

#### Workflow status (7 labels)

Rastream o ciclo de vida de Issue e PR. Veja `lex-issue-status`.

| Label | Cor | Descrição | Artefato dependente |
|-------|-----|-----------|---------------------|
| `status: todo` | `cccccc` | Plan criado, Issue aberta, branch ligada, worktree pronta | `lex-issue-status`, `lex-agent-planning` |
| `status: development` | `83d2ff` | Implementação em andamento — Athena Fase 4 | `lex-issue-status`, `warrior-athena` |
| `status: to review` | `fff3a3` | PR aberto, aguardando reviewer | `lex-issue-status`, `warrior-athena` |
| `status: review` | `fbca04` | Argos ou humano revisando ativamente | `lex-issue-status`, `warrior-argos` |
| `status: to release` | `ffb178` | Revisão aprovada, aguardando início do release | `lex-issue-status`, `warrior-janus` |
| `status: release` | `e07400` | Release em execução — Janus rodando tag/build/deploy | `lex-issue-status`, `warrior-janus` |
| `status: done` | `0e8a16` | Release concluído, PR merged, ciclo encerrado | `lex-issue-status` |

#### Tipos de Issue (10 labels)

Obrigatórios por `lex-issue-quality` Regra 2. Mapeiam para templates em `.github/ISSUE_TEMPLATE/`.

| Label | Cor | Descrição | Artefato dependente |
|-------|-----|-----------|---------------------|
| `feature request ➕` | `5319E7` | Nova solicitação de funcionalidade | `feature-request.yml` |
| `feature ➕` | `7828E5` | Nova funcionalidade adicionada. Usar somente após aprovar uma feature request | Escopo de PR |
| `epic` | `5319E7` | Grande iniciativa agrupando múltiplas histórias ou features | `epic.yml` |
| `user story 🎯` | `6A42EB` | Uma nova user story | `user-story-for-api.yml`, `user-story-for-frontend.yml` |
| `bug report 🐞` | `fc2803` | Reportar um novo bug | `bug.yml` |
| `plan 📋` | `7c4dff` | Sub-issue: unidade executável sob uma Issue pai (User Story / Bug / Tech Task) | `plan.yml`, `kata-plan-task` |
| `evolvability ♻️` | `008672` | Issue ou PR para garantir a evolvability do projeto (refatoração, código limpo) | `tech-task.yml` |
| `documentation 📃` | `0075ca` | Issue ou PR relacionado a melhorias ou adições em documentação | `tech-task.yml` |
| `ci 🏗️` | `ff7a0e` | Issue ou PR relacionado a melhorias no pipeline de CI/CD | `tech-task.yml` |
| `enhancement 🔝` | `D5BBED` | Issue ou PR relacionado a melhoria em uma funcionalidade existente | `tech-task.yml` |

#### Transversais e ciclo de vida (14 labels)

Descrevem a natureza do trabalho ou estado fora do fluxo de desenvolvimento.

| Label | Cor | Descrição | Artefato dependente |
|-------|-----|-----------|---------------------|
| `bugfix 🔧` | `fc4e03` | Issue ou PR relacionado a algo que não está funcionando | Escopo de PR |
| `compliance 📜` | `ae6b09` | Issue ou PR relacionado a melhoria para conformidade com algum padrão | Escopo de PR |
| `security 🛡️` | `D93F0B` | Este PR resolve algum problema de segurança | `lex-pr-quality` |
| `vulnerability 🚨` | `B60205` | Vulnerabilidade detectada | Workflow de segurança |
| `breaking change 💥` | `925845` | Issue ou PR introduzindo breaking change. Incremento de versão major requerido | `lex-pr-quality`, `lex-semantic-version` |
| `release ↗️` | `81A5DC` | Definir somente em PR de release | `lex-pr-quality`, `warrior-janus` |
| `deprecate 🪦` | `5f6a70` | Issue para descontinuar alguma funcionalidade existente | Workflow de descontinuação |
| `blocked 🚧` | `e99695` | Issue ou PR tem algum bloqueio para avançar | Triagem manual |
| `hold` | `fbca04` | Pausado / não está sendo perseguido ativamente | Triagem manual |
| `question ✋` | `d876e3` | Informação adicional é solicitada | Triagem manual |
| `rejected ❌` | `b52816` | Issue ou pull request rejeitado | Triagem manual |
| `wontfix 🤷‍♀️` | `ffffff` | Este issue não será trabalhado | Triagem manual |
| `duplicate !!` | `cfd3d7` | Este issue ou pull request já existe | Triagem manual |
| `good first issue 🧠` | `CA3AC2` | Issue adequado para newcomers | Onboarding de código aberto |

#### Plataforma / escopo (2 labels)

Indicam a superfície técnica afetada.

| Label | Cor | Descrição | Artefato dependente |
|-------|-----|-----------|---------------------|
| `api` | `0075ca` | Issue ou PR relacionado a design ou implementação de API | `user-story-for-api.yml` |
| `frontend` | `D5BBED` | Issue ou PR relacionado a implementação de frontend (UI/UX) | `user-story-for-frontend.yml` |

#### Atribuídos por ferramenta (3 labels)

Auto-aplicados por integrações quando um PR é aberto por uma ferramenta de IA.

| Label | Cor | Descrição | Artefato dependente |
|-------|-----|-----------|---------------------|
| `codex ✨` | `111112` | PR aberto pelo Codex | Integração |
| `copilot ✨` | `111112` | PR aberto pelo Copilot | Integração |
| `cursor ✨` | `111112` | PR aberto pelo Cursor | Integração |

#### Tamanho de PR (6 labels)

Auto-aplicados pelo labeler do GitHub Actions. Obrigatórios por `lex-pr-quality` Regra 2.

| Label | Cor | Descrição | Artefato dependente |
|-------|-----|-----------|---------------------|
| `size/XS` | `9b770a` | PR altera 0-9 linhas, ignorando arquivos gerados. Definido automaticamente | `lex-pr-quality` |
| `size/S` | `e1b207` | PR altera 10-29 linhas, ignorando arquivos gerados. Definido automaticamente | `lex-pr-quality` |
| `size/M` | `f3c511` | PR altera 30-99 linhas, ignorando arquivos gerados. Definido automaticamente | `lex-pr-quality` |
| `size/L` | `ffdb4d` | PR altera 100-499 linhas, ignorando arquivos gerados. Definido automaticamente | `lex-pr-quality` |
| `size/XL` | `cb9e0a` | PR altera 500-999 linhas, ignorando arquivos gerados. Definido automaticamente | `lex-pr-quality` |
| `size/XXL` | `7a6600` | PR altera mais de 1.000 linhas, ignorando arquivos gerados. Definido automaticamente | `lex-pr-quality` |

#### Procedimento de bootstrap

Executar uma vez por repositório consumidor. O catálogo também é semeado automaticamente por `make install` e `make update` quando o alvo tem remote no GitHub.

```bash
# Execução manual no repositório atual
make bootstrap-labels

# Execução manual em um repositório explícito
bash scripts/bootstrap_labels.sh owner/repo
```

O script requer o CLI `gh` autenticado com acesso de escrita ao repositório alvo. É idempotente — re-execuções atualizam cor e descrição sem erros.

## Glossário

| Termo | Definição |
|-------|-----------|
| Issue Type | Classificação no nível da organização GitHub: Task, Bug, Feature |
| Label de tamanho | Label auto-aplicado que reflete o tamanho do diff do PR (ignorando arquivos gerados) |
| Label atribuído por ferramenta | Label auto-aplicado indicando qual ferramenta de IA ou bot criou o PR |
| Espelhamento de labels | Aplicar os mesmos labels de um issue no PR correspondente |

## Referências

- `lex-issue-quality` — Lei que exige templates, labels e conteúdo Why/What/How para todos os issues
- `lex-pr-quality` — Lei que exige espelhamento de labels, label de tamanho, assignee e reviewers em PRs
- `lex-issue-status` — Lei que define as labels canônicas de workflow status
- `kata-contributing-issue` — Procedimento para criar issues (aplica labels obrigatórios e Issue Type)
- `kata-contributing-pr` — Procedimento para criar PRs (espelha labels do issue)
- `codex-contributing` — Referência completa do fluxo de contribuição
- `scripts/bootstrap_labels.sh` — Script idempotente que semeia o catálogo acima
