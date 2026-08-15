# Codex: Standards de Commit

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Escrita de mensagens de commit em repositórios Guardia

## Conteúdo

### Princípios

1. **Clareza:** A mensagem deve comunicar o que mudou e por que, sem ambiguidade.
2. **Rastreabilidade:** Cada commit deve ser conectável a uma issue, decisão ou contexto.
3. **Automatização:** O formato deve permitir geração automática de changelogs e versionamento semântico.
4. **Acessibilidade:** Qualquer pessoa deve entender o commit sem ler o diff.

### Estrutura da Mensagem

```
<tipo>[escopo opcional]: <descrição>

[corpo opcional]

[rodapé(s) opcional(is)]
```

| Parte | Obrigatória | Regras |
|-------|:-----------:|--------|
| Tipo | Sim | Um dos tipos permitidos por `lex-conventional-commits` |
| Escopo | Não | Contexto entre parênteses (ex: `auth`, `api`, `db`) |
| Descrição (subject) | Sim | Imperativo, presente, max 72 caracteres, em inglês |
| Corpo (body) | Não | Detalha o "porquê", pode incluir tag `[idioma]` |
| Rodapé (footer) | Não | Referências, breaking changes, co-authors |

### Tipos — Quando Usar Cada Um

| Tipo | Uso | Impacto SemVer | Exemplo |
|------|-----|:--------------:|---------|
| `feat` | Nova funcionalidade para o usuário | MINOR | `feat(payments): add PIX support` |
| `fix` | Correção de bug | PATCH | `fix(auth): resolve token expiration race condition` |
| `docs` | Documentação | Nenhum | `docs(api): update rate limiting section` |
| `build` | Build system, dependências | Nenhum | `build: upgrade Go to 1.22` |
| `chore` | Manutenção sem impacto em produção | Nenhum | `chore: update .gitignore` |
| `ci` | Configuração de CI/CD | Nenhum | `ci: add coverage report to pipeline` |
| `style` | Formatação sem mudança de lógica | Nenhum | `style: fix indentation in handler` |
| `refactor` | Refatoração sem mudança de comportamento | Nenhum | `refactor(core): extract validation logic` |
| `perf` | Melhoria de performance | PATCH | `perf(query): add index for user lookup` |
| `test` | Adição ou correção de testes | Nenhum | `test(auth): add integration tests for OAuth2` |

### Como Escrever Bons Subjects

| Regra | Exemplo Bom | Exemplo Ruim |
|-------|-------------|-------------|
| Imperativo presente | `add user validation` | `added user validation` |
| Sem ponto final | `fix null pointer` | `fix null pointer.` |
| Máximo 72 caracteres | `feat(auth): add OAuth2 support` | `feat(auth): add OAuth2 support with Google, GitHub, and Microsoft providers including token refresh` |
| Letra minúscula após tipo | `feat: add support` | `feat: Add Support` |
| Em inglês | `fix: resolve timeout` | `fix: resolver timeout` |

### Como Usar Escopos

O escopo contextualiza a mudança. Boas práticas:

| Prática | Exemplo |
|---------|---------|
| Usar nome do módulo/domínio | `feat(payments): ...` |
| Consistência dentro do projeto | Sempre `auth`, nunca alternar com `authentication` |
| Omitir quando a mudança é transversal | `chore: update dependencies` |

### Como Estruturar o Body

```
feat(auth): implement OAuth2 authentication

[en]
Implement OAuth2 authentication flow with support for multiple providers:
- Add OAuth2 client configuration
- Create authentication handlers for Google and GitHub
- Implement token validation and refresh logic

[pt-BR]
Implementa fluxo de autenticação OAuth2 com suporte para múltiplos provedores:
- Adiciona configuração do cliente OAuth2
- Cria handlers de autenticação para Google e GitHub
- Implementa lógica de validação e refresh de tokens

Closes #123
```

Regras do body:
- Versão em inglês (`[en]`) primeiro
- Versão em idioma local com tag BCP 47 (`[pt-BR]`, `[es]`)
- Linha em branco entre subject e body
- Rodapés no final: `Closes #123`, `BREAKING CHANGE:`, `Co-authored-by:`

### Breaking Changes

Duas formas válidas de indicar breaking change:

```
# Forma 1: ! após tipo/escopo
feat(api)!: change authentication endpoint

BREAKING CHANGE: /auth/login moved to /v2/auth/login

# Forma 2: apenas no rodapé
feat(api): change authentication endpoint

BREAKING CHANGE: /auth/login moved to /v2/auth/login
```

### Padrões e Convenções

| Aspecto | Padrão | Referência |
|---------|--------|------------|
| Formato | Conventional Commits v1.0.0 | `lex-conventional-commits` |
| Assinatura | GPG obrigatória | `lex-signed-commits` |
| Granularidade | Atômico, uma mudança | `lex-small-commits` |
| Idioma | Subject em inglês | `lex-commit-language` |

### Restrições Técnicas

- Subject não pode exceder 72 caracteres
- Linha em branco obrigatória entre subject e body
- Tipo deve ser um dos 10 tipos permitidos
- Breaking changes devem usar `!` ou `BREAKING CHANGE:` no rodapé
