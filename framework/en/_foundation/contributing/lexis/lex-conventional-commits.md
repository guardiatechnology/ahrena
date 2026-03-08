# Lexis: Mandatory Conventional Commits

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** All commits in Guardia repositories

## Purpose

A readable and standardized commit history is fundamental for automatic semantic versioning, changelog generation, and understanding code evolution. Without a uniform format, the history becomes noisy and loses value as a traceability tool.

This Lexis ensures that every commit follows the Conventional Commits format, aligned with Guardia's CONTRIBUTING guidelines.

## Law

> **Every commit MUST follow the Conventional Commits format: `<type>[optional scope]: <description>`.**

## Rules

### 1. Mandatory format

Every commit must follow this structure:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### 2. Allowed types

| Type | When to use |
|------|-------------|
| `feat` | New feature (correlates with MINOR in SemVer) |
| `fix` | Bug fix (correlates with PATCH in SemVer) |
| `docs` | Documentation changes |
| `build` | Build system or external dependency changes |
| `chore` | Maintenance tasks that do not alter production code |
| `ci` | CI/CD configuration changes |
| `style` | Formatting, semicolons, spaces — no logic change |
| `refactor` | Refactoring that does not add features or fix bugs |
| `perf` | Performance improvement |
| `test` | Adding or fixing tests |

### 3. Breaking changes

Commits that introduce incompatible changes MUST:
- Add `!` after the type/scope: `feat(api)!: change auth endpoint`
- Or include `BREAKING CHANGE:` in the footer

### 4. Scope

The scope is optional and provides additional context in parentheses: `feat(auth): add OAuth2 support`.

## Scope

- **Applies to:** all Guardia repositories
- **Bound agents:** all
- **Exceptions:** None. Lexis do not admit exceptions.

## Consequences of Violation

1. **Automatic block:** commit rejected by hook or CI
2. **Alert:** PR marked as non-compliant
3. **Remediation:** rewrite the commit with `git commit --amend` or `git rebase -i`

## Examples

### Correct

```
feat(auth): implement OAuth2 authentication

[pt-BR]
Implementa fluxo de autenticação OAuth2 com suporte para múltiplos provedores.

Closes #123
```

```
fix: resolve null pointer in transaction processing
```

```
docs(api): update endpoint documentation for v2
```

### Incorrect

```
# No type — VIOLATES THE LAW
updated the login page

# Invalid type — VIOLATES THE LAW
feature: add new button

# Multiple mixed changes — VIOLATES lex-small-commits as well
feat: add login, fix header, update docs
```

## Automated Validation

- **Tool:** commitlint with `@commitlint/config-conventional`
- **Trigger:** pre-commit hook and CI pipeline
- **Metric:** 0 out-of-format commits tolerated

## References

- [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
- [Guardia CONTRIBUTING](https://hub.guardia.finance/docs/community/CONTRIBUTING/)
- `codex-commit-standards` — Complete guide on writing good messages
- `kata-commit` — Procedure for creating compliant commits
