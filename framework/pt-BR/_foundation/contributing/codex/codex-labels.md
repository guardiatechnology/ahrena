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
| **Task** | `IT_kwDOED9Qy84B7pBh` | `tech-task` |
| **Bug** | `IT_kwDOED9Qy84B7pBi` | `bug-report` *(futuro)* |
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
| `documentation 📃` | `tech-task` | Melhorias ou adições de documentação |
| `ci 🏗️` | `tech-task` | Mudanças em CI/CD ou pipeline |
| `enhancement 🔝` | `tech-task` | Melhoria em uma funcionalidade existente |
| `evolvability ♻️` | `tech-task` | Refatoração, código limpo, manutenção |

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

## Glossário

| Termo | Definição |
|-------|-----------|
| Issue Type | Classificação no nível da organização GitHub: Task, Bug, Feature |
| Label de tamanho | Label auto-aplicado que reflete o tamanho do diff do PR (ignorando arquivos gerados) |
| Label atribuído por ferramenta | Label auto-aplicado indicando qual ferramenta de IA ou bot criou o PR |
| Espelhamento de labels | Aplicar os mesmos labels de um issue no PR correspondente |

## Referências

- `lex-issue-quality` — Lei que exige templates, labels e conteúdo Why/What/How para todos os issues
- `kata-contributing-issue` — Procedimento para criar issues (aplica labels obrigatórios e Issue Type)
- `kata-contributing-pr` — Procedimento para criar PRs (espelha labels do issue)
- `codex-contributing` — Referência completa do fluxo de contribuição
- `labels.yml` — Definições canônicas de labels (`guardiatechnology/project-automations-experiments`)
