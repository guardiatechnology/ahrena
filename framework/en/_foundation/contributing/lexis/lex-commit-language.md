# Lexis: Commit Language

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** All commits in Guardia repositories

## Purpose

English is the lingua franca of software engineering. Commit messages in English ensure that any contributor — regardless of native language — can understand the project history. At the same time, allowing the body in a local language with a tag helps mitigate translation errors.

This Lexis ensures that the main commit message is in English, with an optional body in a local language, as defined by Guardia's CONTRIBUTING guidelines.

## Law

> **The main message (subject) of every commit MUST be written in English. The body MAY include text in a local language, provided it is preceded by the `[language]` tag.**

## Rules

### 1. Subject in English

The first line of the commit (subject) MUST be written in English, following the Conventional Commits format.

### 2. Body with language tag

If the contributor wants to include a description in a local language, the language tag MUST be used in brackets in the body:
- `[pt-BR]` for Brazilian Portuguese
- `[es]` for Spanish
- Any valid BCP 47 code

### 3. English translation first

If the body contains text in a local language, the English version MUST appear first (with the `[en]` tag), followed by the local version.

### 4. Translation tools

The use of tools such as DeepL or Google Translate is encouraged to ensure quality of the English message. Keeping the original text alongside the translation helps mitigate errors.

## Scope

- **Applies to:** all Guardia repositories
- **Bound agents:** all
- **Exceptions:** None. Lexis do not admit exceptions.

## Consequences of Violation

1. **Automatic block:** commit with a non-English subject is flagged
2. **Alert:** reviewer requests subject correction
3. **Remediation:** rewrite with `git commit --amend`

## Examples

### Correct

```
feat(auth): implement OAuth2 authentication

[en]
Implement OAuth2 authentication flow with support for multiple providers:
- Add OAuth2 client configuration
- Create authentication handlers for Google and GitHub
- Implement token validation and refresh logic
- Add unit tests for auth flow

[pt-BR]
Implementa fluxo de autenticação OAuth2 com suporte para múltiplos provedores:
- Adiciona configuração do cliente OAuth2
- Cria handlers de autenticação para Google e GitHub
- Implementa lógica de validação e refresh de tokens
- Adiciona testes unitários para o fluxo de auth

Closes #123
```

```
fix: resolve null pointer in transaction processing
```

### Incorrect

```
# Subject in Portuguese — VIOLATES THE LAW
feat(auth): implementar autenticação OAuth2

# Body without language tag — VIOLATES THE LAW
feat(auth): implement OAuth2

Implementa fluxo de autenticação OAuth2.
(Missing the [pt-BR] tag before the Portuguese text)
```

## Automated Validation

- **Tool:** commitlint with custom rule for subject language
- **Trigger:** pre-commit hook and CI pipeline
- **Metric:** 100% of subjects in English

## References

- [Guardia CONTRIBUTING — Languages](https://hub.guardia.finance/docs/community/CONTRIBUTING/)
- `lex-conventional-commits` — Mandatory commit format
- `codex-commit-standards` — Complete guide on commit standards
