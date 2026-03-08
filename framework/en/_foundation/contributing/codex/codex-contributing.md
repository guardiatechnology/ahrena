# Codex: Guardia Contribution Flow

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Contributing to Guardia repositories

## Overview

This Codex documents the complete Guardia contribution flow — from initial proposal to merge — including the two possible paths: external contributor (via PR) and codeowner (direct commit). It is consulted by `kata-contribute-pilar` during the submission flow.

## Context

- **Domain:** Open source contribution workflow
- **Target audience:** AI agents, developers, and community contributors
- **Update:** When Guardia contribution policies change

## Content

### Principles

1. **Discussion first:** Significant changes start with a discussion, not with code. Aligning expectations prevents rework.
2. **Traceability:** Every change must be connected to an issue. The only exception is trivial fixes (typos).
3. **Verifiable quality:** CI is mandatory. Code that does not pass tests is not accepted.
4. **Transparency:** The process is the same for everyone. Codeowners have a shorter path, not a different one.

### Flow for External Contributors

```
1. Open discussion in GitHub Discussions (category: Ideas)
   → Explain: WHAT, WHY, HOW (Golden Circle)
2. If approved, the discussion is converted to an issue
3. Fork the repository
4. Create branch from main
5. Implement the change (following commit Lexis)
6. Sign the CLA (Contributor License Agreement)
7. Open PR answering the standard questions
8. Keep CI green and respond to review
9. After approval, merge is performed by the maintainer
```

### Flow for Codeowners

Codeowners registered in `.github/CODEOWNERS` can:

```
1. Create branch directly (no fork)
2. Implement the change (following commit Lexis)
3. Push directly to the branch
4. For significant changes: open PR for visibility
5. For trivial or framework changes: direct commit on branch
```

The choice between PR and direct commit depends on impact:

| Change type | Path |
|-------------|------|
| New Pilar in the framework | Direct commit (if codeowner) or PR |
| Change affecting multiple Clades | PR (even for codeowner) |
| Trivial fix (typo) | Direct commit |
| New code feature | PR (always) |

### Codeowner Detection

To determine whether the contributor is a codeowner, check `.github/CODEOWNERS`:

```
# CODEOWNERS example
* @guardia/guardians
```

The agent can verify by running:
```
gh api repos/{owner}/{repo}/collaborators/{username}/permission
```

### Standards and Conventions

| Aspect | Standard |
|--------|----------|
| Discussions | GitHub Discussions, "Ideas" category |
| Issues | Created from approved discussions |
| Branches | `feat/name`, `fix/name`, `docs/name` |
| PRs | Title in Conventional Commits, body with context |
| CLA | Mandatory for external contributors |
| CI | Must pass before merge |

### PR Requirements

| Requirement | Details |
|-------------|---------|
| Signed commits | All "Verified" (`lex-signed-commits`) |
| Commit format | Conventional Commits (`lex-conventional-commits`) |
| Atomic commits | One change per commit (`lex-small-commits`) |
| Language | Subject in English (`lex-commit-language`) |
| No conflicts | Branch up to date with main |
| Green CI | All checks passing |
| Review | At least one approver |

### Active Decisions

| Decision | Status |
|----------|--------|
| Mandatory CLA for external contributors | Active |
| Official communication in English | Active |
| Issues may be in any language | Active |
| Open Core model with Apache 2.0 for Core Modules | Active |

### Technical Constraints

- PRs with unsigned commits are automatically rejected
- The `main` branch is protected — merge only via PR or by codeowners
- CI is mandatory — PRs with failing checks cannot be merged

## Glossary

| Term | Definition |
|------|-----------|
| Codeowner | Member of the `@guardia/guardians` team listed in `.github/CODEOWNERS` |
| CLA | Contributor License Agreement — legal agreement for contributors |
| Golden Circle | Communication framework: WHAT, WHY, HOW |
| Branch protection | GitHub rules that protect branches from direct changes |

## References

- [Guardia CONTRIBUTING](https://hub.guardia.finance/docs/community/CONTRIBUTING/)
- [Guardia CLA](https://hub.guardia.finance/docs/community/governance/CLA/)
- `.github/CODEOWNERS` — Repository codeowners file
- `lex-conventional-commits`, `lex-signed-commits`, `lex-small-commits`, `lex-commit-language` — Commit Lexis
- `codex-commit-standards` — Commit message standards
- `kata-contribute-pilar` — Procedure for contributing Pilars
