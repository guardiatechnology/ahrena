# Lexis: Requisitos de Qualidade do Pull Request

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrantável | **Escopo:** Todos os Pull Requests em repositórios Guardia

## Lei

> **Todo PR em um repositório Guardia DEVE: (1) espelhar todas as labels da issue associada; (2) ter exatamente uma label de tamanho (`size/XS` a `size/XXL`), aplicada automaticamente pelo GitHub Actions ou manualmente quando a automação ainda não estiver configurada; (3) aplicar labels específicos de PR quando aplicável (`breaking change 💥`, `security 🛡️`, `release ↗️`); (4) ser atribuído ao autor com `--assignee @me`. PRs que não atendam a esses requisitos NÃO DEVEM ser mesclados.**

## Cobertura

- **Aplica-se a:** todos os Pull Requests em todos os repositórios Guardia.
- **Agentes vinculados:** desenvolvedores, agentes de IA (warrior-athena, warrior-apollo, warrior-hephaestus) que criam ou revisam PRs.
- **Exceções:** PRs automáticos do Dependabot e ferramentas de varredura de segurança, que seguem seu próprio fluxo. Toda outra exceção exige justificativa explícita no PR.

## Regras

### 1. Espelhamento de labels da issue

Ao criar um PR, o agente DEVE:

1. Obter todas as labels da issue associada.
2. Aplicar as mesmas labels ao PR.
3. Adicionar labels específicos de PR quando aplicável (ver Regra 3).

```bash
# Obter labels da issue associada
LABELS=$(gh issue view $ISSUE_NUMBER --repo $OWNER/$REPO --json labels --jq '[.labels[].name] | join(",")')

# Espelhar no PR
gh pr edit $PR_NUMBER --repo $OWNER/$REPO --add-label "$LABELS"
```

### 2. Label de tamanho obrigatória

Todo PR DEVE ter exatamente uma label de tamanho (`size/XS`, `size/S`, `size/M`, `size/L`, `size/XL` ou `size/XXL`):

- **Quando o GitHub Actions está configurado:** a label é aplicada automaticamente ao criar ou atualizar o PR. Não aplicar manualmente.
- **Quando o GitHub Actions não está configurado ou ainda não executou:** o agente DEVE calcular o tamanho manualmente e aplicar a label antes de abrir o PR para revisão.

**Cálculo manual do tamanho:**

```bash
# Contar linhas alteradas em relação à branch base (ignorando arquivos gerados)
git diff main...HEAD --stat | tail -1
```

| Label | Linhas alteradas |
|-------|:----------------:|
| `size/XS` | 0–9 |
| `size/S` | 10–29 |
| `size/M` | 30–99 |
| `size/L` | 100–499 |
| `size/XL` | 500–999 |
| `size/XXL` | 1.000+ |

### 3. Labels específicos de PR

Aplicar adicionalmente quando aplicável:

| Label | Quando aplicar |
|-------|----------------|
| `breaking change 💥` | PR introduz mudança incompatível de API; requer incremento de versão major |
| `security 🛡️` | PR resolve uma vulnerabilidade de segurança |
| `release ↗️` | PR de release — somente mantenedores |

### 4. Atribuição ao autor

Todo PR DEVE ser atribuído ao autor:

```bash
gh pr create ... --assignee "@me"
# ou após a criação:
gh pr edit $PR_NUMBER --add-assignee "@me"
```

### 5. Pré-requisitos antes de criar o PR

O agente DEVE verificar, nesta ordem, antes de executar `gh pr create`:

1. Issue associada existe e está em conformidade com `lex-issue-quality`.
2. Branch segue o formato definido em `lex-git-branches`.
3. PR body inclui `Closes #N` ou `Refs #N` conforme `lex-issue-first`.
4. Labels da issue foram espelhadas.
5. Label de tamanho foi aplicada (manualmente se necessário).

## Exemplos

### Correto

```bash
# Issue #42 com labels: documentation 📃, ci 🏗️
# Diff: 4.516 adições + 2.877 exclusões → size/XXL

gh pr create \
  --title "docs: create public documentation site with MkDocs" \
  --body "Closes #42" \
  --base main \
  --assignee "@me"

gh pr edit 42 --add-label "documentation 📃,ci 🏗️,size/XXL"
```

### Incorreto

```bash
# ❌ PR criado sem labels
gh pr create --title "docs: add site" --body "Closes #42"
# Faltam: labels espelhadas da issue, label de tamanho, assignee

# ❌ Label de tamanho não aplicada porque "o Actions vai fazer"
# Quando o Actions não está configurado, o agente DEVE aplicar manualmente
```

## Validação Automatizada

- **Ferramenta:** GitHub Actions PR size labeler (auto-aplica `size/*`); checklist de revisão verifica labels espelhadas e assignee; `kata-contributing-pr` aplica todas as regras desta Lexis ao criar PRs.
- **Quando:** na criação e atualização do PR; no checklist de revisão.
- **Métrica:** 0 PRs mesclados sem label de tamanho; 0 PRs mesclados sem espelhamento das labels da issue; 0 PRs sem assignee.
