# Codex: Fluxo de Contribuição Guardia

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Contribuição a repositórios Guardia

## Visão Geral

Este Codex documenta o fluxo completo de contribuição da Guardia — desde a proposta inicial até o merge — incluindo os dois caminhos possíveis: contribuidor externo (via PR) e codeowner (commit direto). É consultado pelo `kata-contribute-pilar` durante o fluxo de submissão.

## Contexto

- **Domínio:** Fluxo de trabalho de contribuição open source
- **Público-alvo:** Agentes de IA, desenvolvedores e contribuidores da comunidade
- **Atualização:** Quando as políticas de contribuição da Guardia mudarem

## Conteúdo

### Princípios

1. **Discussão primeiro:** Mudanças significativas começam com uma discussão, não com código. O alinhamento de expectativas evita retrabalho.
2. **Rastreabilidade:** Toda mudança deve estar conectada a uma issue. A única exceção são correções triviais (typos).
3. **Qualidade verificável:** CI obrigatório. Código que não passa nos testes não é aceito.
4. **Transparência:** O processo é o mesmo para todos. Codeowners têm um caminho mais curto, não um caminho diferente.

### Fluxo para Contribuidores Externos

```
1. Abrir discussão no GitHub Discussions (categoria: Ideas)
   → Explicar: O QUE, POR QUÊ, COMO (Golden Circle)
2. Se aprovada, a discussão é convertida em issue
3. Fork do repositório
4. Criar branch a partir de main
5. Implementar a mudança (seguindo Lexis de commit)
6. Assinar o CLA (Contributor License Agreement)
7. Abrir PR respondendo às perguntas padrão
8. Manter CI verde e responder ao review
9. Após aprovação, merge é feito pelo maintainer
```

### Fluxo para Codeowners

Codeowners registrados no `.github/CODEOWNERS` podem:

```
1. Criar branch diretamente (sem fork)
2. Implementar a mudança (seguindo Lexis de commit)
3. Push direto ao branch
4. Para mudanças significativas: abrir PR para visibilidade
5. Para mudanças triviais ou de framework: commit direto em branch
```

A decisão entre PR e commit direto depende do impacto:

| Tipo de mudança | Caminho |
|----------------|---------|
| Novo Pilar no framework | Commit direto (se codeowner) ou PR |
| Mudança que afeta múltiplos Clades | PR (mesmo para codeowner) |
| Correção trivial (typo) | Commit direto |
| Nova feature em código | PR (sempre) |

### Detecção de Codeowner

Para determinar se o contribuidor é codeowner, verificar `.github/CODEOWNERS`:

```
# Exemplo de CODEOWNERS
* @guardia/guardians
```

O agente pode verificar executando:
```
gh api repos/{owner}/{repo}/collaborators/{username}/permission
```

### Padrões e Convenções

| Aspecto | Padrão |
|---------|--------|
| Discussões | GitHub Discussions, categoria "Ideas" |
| Issues | Criadas a partir de discussões aprovadas |
| Branches | `feat/nome`, `fix/nome`, `docs/nome` |
| PRs | Título em Conventional Commits, body com contexto |
| CLA | Obrigatório para contribuidores externos |
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
| CLA obrigatório para contribuidores externos | Ativa |
| Comunicação oficial em inglês | Ativa |
| Issues podem ser em qualquer idioma | Ativa |
| Modelo Open Core com Apache 2.0 para Core Modules | Ativa |

### Restrições Técnicas

- PRs com commits não-signed são automaticamente rejeitados
- O branch `main` é protegido — merge apenas via PR ou por codeowners
- CI é obrigatório — PRs com checks falhando não podem ser merged

## Glossário

| Termo | Definição |
|-------|-----------|
| Codeowner | Membro do time `@guardia/guardians` listado em `.github/CODEOWNERS` |
| CLA | Contributor License Agreement — acordo legal para contribuidores |
| Golden Circle | Framework de comunicação: O QUÊ, POR QUÊ, COMO |
| Branch protection | Regras do GitHub que protegem branches de alterações diretas |

## Referências

- [CONTRIBUTING da Guardia](https://hub.guardia.finance/docs/community/CONTRIBUTING/)
- [CLA da Guardia](https://hub.guardia.finance/docs/community/governance/CLA/)
- `.github/CODEOWNERS` — Arquivo de codeowners do repositório
- `lex-conventional-commits`, `lex-signed-commits`, `lex-small-commits`, `lex-commit-language` — Lexis de commit
- `codex-commit-standards` — Standards de mensagem de commit
- `kata-contribute-pilar` — Procedimento para contribuir Pilares
