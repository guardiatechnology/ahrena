# Codex: Commit Standards

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Writing commit messages in Guardia repositories

## Content

### Principles

1. **Clarity:** The message must communicate what changed and why, without ambiguity.
2. **Traceability:** Each commit must be connectable to an issue, decision, or context.
3. **Automation:** The format must enable automatic changelog generation and semantic versioning.
4. **Accessibility:** Anyone must understand the commit without reading the diff.

### Message Structure

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

| Part | Required | Rules |
|------|:--------:|-------|
| Type | Yes | One of the types allowed by `lex-conventional-commits` |
| Scope | No | Context in parentheses (e.g., `auth`, `api`, `db`) |
| Description (subject) | Yes | Imperative, present tense, max 72 characters, in English |
| Body | No | Details the "why", may include `[language]` tag |
| Footer | No | References, breaking changes, co-authors |

### Types — When to Use Each One

| Type | Use | SemVer Impact | Example |
|------|-----|:-------------:|---------|
| `feat` | New user-facing feature | MINOR | `feat(payments): add PIX support` |
| `fix` | Bug fix | PATCH | `fix(auth): resolve token expiration race condition` |
| `docs` | Documentation | None | `docs(api): update rate limiting section` |
| `build` | Build system, dependencies | None | `build: upgrade Go to 1.22` |
| `chore` | Maintenance with no production impact | None | `chore: update .gitignore` |
| `ci` | CI/CD configuration | None | `ci: add coverage report to pipeline` |
| `style` | Formatting with no logic change | None | `style: fix indentation in handler` |
| `refactor` | Refactoring with no behavior change | None | `refactor(core): extract validation logic` |
| `perf` | Performance improvement | PATCH | `perf(query): add index for user lookup` |
| `test` | Adding or fixing tests | None | `test(auth): add integration tests for OAuth2` |

### Writing Good Subjects

| Rule | Good Example | Bad Example |
|------|-------------|-------------|
| Imperative present tense | `add user validation` | `added user validation` |
| No trailing period | `fix null pointer` | `fix null pointer.` |
| Maximum 72 characters | `feat(auth): add OAuth2 support` | `feat(auth): add OAuth2 support with Google, GitHub, and Microsoft providers including token refresh` |
| Lowercase after type | `feat: add support` | `feat: Add Support` |
| In English | `fix: resolve timeout` | `fix: resolver timeout` |

### Using Scopes

The scope contextualizes the change. Best practices:

| Practice | Example |
|----------|---------|
| Use module/domain name | `feat(payments): ...` |
| Consistency within the project | Always `auth`, never alternate with `authentication` |
| Omit when the change is cross-cutting | `chore: update dependencies` |

### Structuring the Body

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

Body rules:
- English version (`[en]`) first
- Local language version with BCP 47 tag (`[pt-BR]`, `[es]`)
- Blank line between subject and body
- Footers at the end: `Closes #123`, `BREAKING CHANGE:`, `Co-authored-by:`

### Breaking Changes

Two valid ways to indicate a breaking change:

```
# Method 1: ! after type/scope
feat(api)!: change authentication endpoint

BREAKING CHANGE: /auth/login moved to /v2/auth/login

# Method 2: footer only
feat(api): change authentication endpoint

BREAKING CHANGE: /auth/login moved to /v2/auth/login
```

### Standards and Conventions

| Aspect | Standard | Reference |
|--------|----------|-----------|
| Format | Conventional Commits v1.0.0 | `lex-conventional-commits` |
| Signature | Mandatory GPG | `lex-signed-commits` |
| Granularity | Atomic, single change | `lex-small-commits` |
| Language | Subject in English | `lex-commit-language` |

### Technical Constraints

- Subject must not exceed 72 characters
- Blank line is mandatory between subject and body
- Type must be one of the 10 allowed types
- Breaking changes must use `!` or `BREAKING CHANGE:` in the footer
