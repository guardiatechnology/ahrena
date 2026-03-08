# Cry: Contribuir para Repositório Guardia

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para contribuir com issues, PRs e discussões em repositórios Guardia

## Invocação

```
/cry-contribute <ação> [opções]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `ação` | Sim | Tipo de contribuição: `pr`, `issue`, `discuss` | `pr` |
| `opções` | Não | Parâmetros adicionais conforme a ação | `--type feature-request` |

## Ações Disponíveis

### `pr` — Criar Pull Request

```
/cry-contribute pr [--base main] [--title "..."]
```

Comportamento:
1. Executa `kata-commit` para garantir commits conformes (se houver mudanças pendentes)
2. Cria branch seguindo a convenção (`feat/nome`, `fix/nome`, `docs/nome`)
3. Push ao remote
4. Abre PR via `gh pr create` preenchendo o template `.github/pull_request_template.md`:
   - **Description:** resumo da mudança e issue resolvida
   - **Type of Change:** marca os checkboxes relevantes (bug fix, feature, breaking change, docs, security, performance, refactoring, tests, CI/CD)
   - **Prerequisites:** associa issue, milestone e labels corretas (breaking change, security, feature, bugfix, enhancement, evolvability, documentation)
   - **How Has This Been Tested:** descreve os testes executados
   - **Checklist:** valida estilo, self-review, documentação, testes
   - **Related Issues:** referencia issues com `Closes #N` ou `Related to #N`
   - **Breaking Changes:** descreve migrações se aplicável
   - **Security Considerations:** implicações de segurança
   - **Performance Impact:** benchmarks se aplicável
   - **Documentation:** links para documentação atualizada
5. Define o título em Conventional Commits (em inglês)
6. Valida que os commits estão assinados (`lex-signed-commits`)

### `issue` — Criar Issue

```
/cry-contribute issue [--type <template>]
```

Templates disponíveis (definidos em `.github/ISSUE_TEMPLATE/`):

| Template | Uso | Estrutura |
|----------|-----|-----------|
| `feature-request` | Nova funcionalidade | User story (As/I want/So that), comportamento atual vs desejado, valor de negócio, áreas de impacto |
| `epic` | Épico agrupando user stories | Por que é importante, o que é |
| `user-story-for-frontend` | Story de frontend detalhada | User story, critérios de aceite (Gherkin), entidades, métricas, diagramas de sequência, mockups |
| `user-story-for-api` | Story de API detalhada | User story, critérios de aceite (Gherkin), entidades, spec de API (método, path, headers, schemas), métricas, SLIs/SLOs |

Se `--type` for omitido, o agente pergunta qual template usar.

Comportamento:
1. Identifica o template correto
2. Coleta as informações necessárias do usuário (ou infere do contexto)
3. Cria a issue via `gh issue create` com o template preenchido

### `discuss` — Abrir Discussão

```
/cry-contribute discuss [--category Ideas]
```

Comportamento:
1. Verifica se a proposta justifica uma discussão (mudanças significativas)
2. Estrutura a discussão no formato Golden Circle (O QUÊ, POR QUÊ, COMO)
3. Abre no GitHub Discussions via `gh discussion create`

## Exemplos de Uso

```
# Criar PR a partir do branch atual
/cry-contribute pr

# Criar PR com título específico
/cry-contribute pr --title "feat(auth): implement OAuth2 authentication"

# Criar issue de feature request
/cry-contribute issue --type feature-request

# Criar epic
/cry-contribute issue --type epic

# Criar user story de API
/cry-contribute issue --type user-story-for-api

# Abrir discussão antes de uma mudança grande
/cry-contribute discuss
```

## Regras

- Blank issues estão desabilitadas — toda issue DEVE usar um template
- Mudanças significativas DEVEM começar com discussão antes de virar issue
- PRs DEVEM seguir todas as 4 Lexis de commit
- O título do PR DEVE seguir Conventional Commits em inglês

## Kata Associado

`kata-contribute` — Procedimento completo para contribuir via Pull Request

## Referências

- `codex-contributing` — Fluxo de contribuição Guardia
- `kata-commit` — Procedimento de commit (invocado por `pr`)
- `kata-contribute` — Procedimento para contribuir via PR
- `lex-conventional-commits`, `lex-signed-commits`, `lex-small-commits`, `lex-commit-language` — Lexis de commit
- `.github/ISSUE_TEMPLATE/` — Templates de issue do repositório
- `.github/pull_request_template.md` — Template de PR do repositório
