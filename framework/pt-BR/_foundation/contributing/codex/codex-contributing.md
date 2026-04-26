# Codex: Fluxo de Contribuição Guardia

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Contribuição a repositórios Guardia

## Visão Geral

Este Codex documenta o fluxo de contribuição da Guardia, desde a proposta inicial até o merge. O processo é único para todos os contribuidores (internos e externos), garantindo transparência e rastreabilidade. É consultado pelos katas de contribuição (`kata-contributing-issue`, `kata-contributing-pr`, `kata-contributing-discuss`) e pelo `kata-contribute` durante o fluxo de submissão.

## Contexto

- **Domínio:** Fluxo de trabalho de contribuição open source
- **Público-alvo:** Agentes de IA, desenvolvedores e contribuidores da comunidade
- **Atualização:** Quando as políticas de contribuição da Guardia mudarem

## Conteúdo

### Princípios

1. **Discussão primeiro:** Mudanças significativas começam com uma discussão, não com código. O alinhamento de expectativas evita retrabalho.
2. **Rastreabilidade:** Toda mudança deve estar conectada a uma issue. A única exceção são correções triviais (typos).
3. **Qualidade verificável:** CI obrigatório. Código que não passa nos testes não é aceito.
4. **Transparência:** O processo é o mesmo para todos. Sem atalhos, sem exceções.

### Fluxo de Contribuição

```
1. Abrir discussão no GitHub Discussions (categoria: Ideas)
   → Explicar: O QUÊ, POR QUÊ, COMO (Golden Circle)
2. Se aprovada, a discussão é convertida em issue
3. Criar branch a partir de main
   → Convenção: feat/nome, fix/nome, docs/nome
4. Implementar a mudança (seguindo Lexis de commit)
5. Abrir PR preenchendo o template .github/pull_request_template.md
6. Manter CI verde e responder ao review
7. Após aprovação, merge é feito pelo maintainer
```

Para correções triviais (typos, formatação), os passos 1 e 2 podem ser omitidos (abrir PR direto com referência ao problema).

### Contribuição por tipo

Os templates de contribuição (issue e PR) ficam em **`.ahrena/contributing_templates/`** (5 arquivos .md), instalados pelo setup do Ahrena a partir de `framework/templates/contributing_templates/` e preservados se já existirem. Os **3 katas** (issue, PR, discussão) orientam o uso do **MCP do GitHub** (ou servidor equivalente) para criar issues, PRs e discussões; fallback para `gh` CLI quando o MCP não estiver disponível.

| Tipo                  | Kata                          | Cry (um por tipo)           | Template (em .ahrena/contributing_templates/)     | Labels obrigatórias |
| --------------------- | ----------------------------- | --------------------------- | ------------------------------------------------- | ------------------- |
| Feature Request       | kata-contributing-issue       | cry-new-feature-request     | `feature-request.md`                              | `feature request ➕` |
| Epic                  | kata-contributing-issue       | cry-new-epic                | `epic.md`                                         | `epic` |
| User Story (API)      | kata-contributing-issue       | cry-new-user-story-api      | `user-story-for-api.md`                           | `api`, `user story 🎯` |
| User Story (Frontend) | kata-contributing-issue       | cry-new-user-story-frontend | `user-story-for-frontend.md`                      | `frontend`, `user story 🎯` |
| Tarefa Simples        | kata-contributing-issue       | cry-new-simple-task         | `simple-task.md`                                  | uma de: `documentation 📃`, `ci 🏗️`, `enhancement 🔝`, `evolvability ♻️` |
| Pull Request          | kata-contributing-pr          | cry-new-pr                  | `pull_request_template.md`                        | — |
| Discussão             | kata-contributing-discuss     | cry-new-discuss             | (Golden Circle; sem .md)                          | — |

- **Cry genérico:** `cry-contribute` — para contribuições genéricas; pode delegar aos cries por tipo ou perguntar qual tipo.
- **Referências:** os 3 katas (`kata-contributing-issue`, `kata-contributing-pr`, `kata-contributing-discuss`) e os 7 cries (`cry-new-feature-request`, `cry-new-epic`, `cry-new-user-story-api`, `cry-new-user-story-frontend`, `cry-new-simple-task`, `cry-new-pr`, `cry-new-discuss`).

### Padrões e Convenções

| Aspecto | Padrão |
|---------|--------|
| Discussões | GitHub Discussions, categoria "Ideas" |
| Issues | Um dos 5 templates; com label; responde Por quê/O quê/Como (`lex-issue-quality`) |
| Branches | `{type}/{issue-number}-{slug}` (ex.: `feat/42-oauth2`) — veja `lex-git-branches` |
| PRs | Título em Conventional Commits; body inclui `Closes #N` ou `Refs #N` (`lex-issue-first`) |
| CI | Deve passar antes do merge |

### Requisitos de PR

| Requisito | Detalhes |
|-----------|----------|
| Commits assinados | Todos "Verified" (`lex-signed-commits`) |
| Formato de commits | Conventional Commits (`lex-conventional-commits`) |
| Commits atômicos | Uma mudança por commit (`lex-small-commits`) |
| Idioma | Subject em inglês (`lex-commit-language`) |
| Sem conflitos | Branch atualizado com main |
| CI verde | Todos os checks passando |
| Review | Pelo menos um aprovador |

### Decisões Vigentes

| Decisão | Status |
|---------|--------|
| Comunicação oficial em inglês | Ativa |
| Issues podem ser em qualquer idioma | Ativa |
| Modelo Open Core com Apache 2.0 para Core Modules | Ativa |

### Restrições Técnicas

- PRs com commits não-signed são automaticamente rejeitados
- O branch `main` é protegido — merge apenas via PR aprovado
- CI é obrigatório — PRs com checks falhando não podem ser merged

## Glossário

| Termo | Definição |
|-------|-----------|
| Golden Circle | Framework de comunicação: O QUÊ, POR QUÊ, COMO |
| Branch protection | Regras do GitHub que protegem branches de alterações diretas |

## Referências

- [CONTRIBUTING da Guardia](https://hub.guardia.finance/docs/community/CONTRIBUTING/)
- `.github/CODEOWNERS` — Arquivo de codeowners do repositório
- `lex-issue-quality` — Templates, labels e requisitos de conteúdo Por quê/O quê/Como
- `lex-issue-first` — Issue antes do branch; PR deve referenciar issue
- `lex-git-branches` — Nomenclatura de branch: `{type}/{issue-number}-{slug}`
- `lex-conventional-commits`, `lex-signed-commits`, `lex-small-commits`, `lex-commit-language` — Lexis de commit
- `codex-commit-standards` — Standards de mensagem de commit
- `codex-git-workflow` — Fluxo completo Issue → Branch → Commits → PR → Merge
- `kata-contribute` — Procedimento para contribuir via PR
- `kata-contributing-issue`, `kata-contributing-pr`, `kata-contributing-discuss` — Katas por tipo de contribuição
- Cries: cry-new-feature-request, cry-new-epic, cry-new-user-story-api, cry-new-user-story-frontend, cry-new-simple-task, cry-new-pr, cry-new-discuss
