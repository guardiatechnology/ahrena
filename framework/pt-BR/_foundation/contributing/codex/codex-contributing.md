# Codex: Fluxo de Contribuição Guardia

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Contribuição a repositórios Guardia

## Visão Geral

Este Codex documenta o fluxo de contribuição da Guardia, desde a proposta inicial até o merge. O processo é único para todos os contribuidores (internos e externos), garantindo transparência e rastreabilidade. É consultado pelo `kata-contribute` durante o fluxo de submissão.

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

### Padrões e Convenções

| Aspecto | Padrão |
|---------|--------|
| Discussões | GitHub Discussions, categoria "Ideas" |
| Issues | Criadas a partir de discussões aprovadas |
| Branches | `feat/nome`, `fix/nome`, `docs/nome` |
| PRs | Título em Conventional Commits, body com template preenchido |
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
- `lex-conventional-commits`, `lex-signed-commits`, `lex-small-commits`, `lex-commit-language` — Lexis de commit
- `codex-commit-standards` — Standards de mensagem de commit
- `kata-contribute` — Procedimento para contribuir via PR
