# Codex: Guardia Contribution Flow

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Contributing to Guardia repositories

## Overview

This Codex documents the Guardia contribution flow, from the initial proposal to merge. The process is the same for all contributors (internal and external), ensuring transparency and traceability. It is consulted by `kata-contribute` during the submission flow.

## Context

- **Domain:** Open source contribution workflow
- **Target audience:** AI agents, developers, and community contributors
- **Update:** When Guardia contribution policies change

## Content

### Principles

1. **Discussion first:** Significant changes start with discussion, not code. Aligning expectations avoids rework.
2. **Traceability:** Every change MUST be linked to an issue. The only exception is trivial fixes (typos).
3. **Verifiable quality:** CI is mandatory. Code that does not pass tests is not accepted.
4. **Transparency:** The process is the same for everyone. No shortcuts, no exceptions.

### Contribution Flow

```
1. Open discussion in GitHub Discussions (category: Ideas)
   → Explain: WHAT, WHY, HOW (Golden Circle)
2. If approved, the discussion is converted to an issue
3. Create branch from main
   → Convention: feat/name, fix/name, docs/name
4. Implement the change (following commit Lexis)
5. Open PR filling the template .github/pull_request_template.md
6. Keep CI green and respond to review
7. After approval, merge is done by the maintainer
```

For trivial fixes (typos, formatting), steps 1 and 2 MAY be omitted (open PR directly with reference to the problem).

### Standards and Conventions

| Aspect | Standard |
|--------|----------|
| Discussions | GitHub Discussions, category "Ideas" |
| Issues | Created from approved discussions |
| Branches | `feat/name`, `fix/name`, `docs/name` |
| PRs | Title in Conventional Commits, body with template filled |
| CI | MUST pass before merge |

### PR Requirements

| Requirement | Details |
|-------------|---------|
| Signed commits | All "Verified" (`lex-signed-commits`) |
| Commit format | Conventional Commits (`lex-conventional-commits`) |
| Atomic commits | One change per commit (`lex-small-commits`) |
| Language | Subject in English (`lex-commit-language`) |
| No conflicts | Branch updated with main |
| Green CI | All checks passing |
| Review | At least one approver |

### Active Decisions

| Decision | Status |
|----------|--------|
| Official communication in English | Active |
| Issues MAY be in any language | Active |
| Open Core model with Apache 2.0 for Core Modules | Active |

### Technical Restrictions

- PRs with unsigned commits are automatically rejected
- The `main` branch is protected — merge only via approved PR
- CI is mandatory — PRs with failing checks cannot be merged

## Glossary

| Term | Definition |
|------|------------|
| Golden Circle | Communication framework: WHAT, WHY, HOW |
| Branch protection | GitHub rules that protect branches from direct changes |

## References

- [Guardia CONTRIBUTING](https://hub.guardia.finance/docs/community/CONTRIBUTING/)
- `.github/CODEOWNERS` — Repository codeowners file
- `lex-conventional-commits`, `lex-signed-commits`, `lex-small-commits`, `lex-commit-language` — Commit Lexis
- `codex-commit-standards` — Commit message standards
- `kata-contribute` — Procedure for contributing via PR
