# Contributing — Contribution Flow

> Documentation for the contribution system, commit standards, and Pull Request creation.

## Overview

The `contributing` Subclade defines Guardia's unified contribution flow. It covers commit Lexis through the PR opening procedure via MCP. The process is the same for all contributors (internal and external), ensuring transparency and traceability.

## Architecture

```mermaid
flowchart TD
    subgraph invocation ["Invocation"]
        CryCommit["/cry-commit"]
        CryContribute["/cry-contribute"]
        CryTag["/cry-tag"]
    end

    subgraph procedures ["Procedures"]
        KataCommit["kata-commit"]
        KataContribute["kata-contribute"]
        KataTag["kata-tag"]
    end

    subgraph knowledge ["Knowledge"]
        CdxContributing["codex-contributing"]
        CdxCommitStd["codex-commit-standards"]
        CdxSemVer["codex-semantic-version"]
    end

    subgraph laws ["Laws"]
        LexConventional["lex-conventional-commits"]
        LexSmall["lex-small-commits"]
        LexLanguage["lex-commit-language"]
        LexSigned["lex-signed-commits"]
        LexSemVer["lex-semantic-version"]
    end

    CryCommit -->|"invokes"| KataCommit
    CryContribute -->|"invokes"| KataContribute
    CryTag -->|"invokes"| KataTag
    KataContribute -->|"uses internally"| KataCommit
    KataContribute -->|"consults"| CdxContributing
    KataCommit -->|"consults"| CdxCommitStd
    KataCommit -->|"obeys"| LexConventional
    KataCommit -->|"obeys"| LexSmall
    KataCommit -->|"obeys"| LexLanguage
    KataCommit -->|"obeys"| LexSigned
    KataTag -->|"consults"| CdxSemVer
    KataTag -->|"obeys"| LexSemVer
    KataTag -->|"obeys"| LexSigned
```

## Artifact Inventory

### Lexis (laws)

| Artifact | Description |
|----------|-------------|
| `lex-conventional-commits` | Mandatory format `type(scope): description` |
| `lex-small-commits` | One purpose per commit, atomic changes |
| `lex-commit-language` | Subject in English |
| `lex-signed-commits` | Mandatory GPG signature |
| `lex-semantic-version` | Mandatory SemVer 2.0 for releases and tags |

### Codex (knowledge)

| Artifact | Description |
|----------|-------------|
| `codex-contributing` | Full contribution flow (from discussion to merge) |
| `codex-commit-standards` | Detailed structure of commit messages |
| `codex-semantic-version` | Reference for SemVer and git tags in releases |

### Katas (procedures)

| Artifact | Description |
|----------|-------------|
| `kata-commit` | Procedure to create compliant commits |
| `kata-contribute` | Procedure to open Pull Requests via MCP |
| `kata-tag` | Procedure to apply semantic versioning with git tags |

### Cries (shortcuts)

| Artifact | Description |
|----------|-------------|
| `cry-commit` | Shortcut to commit following the 4 commit Lexis |
| `cry-contribute` | Shortcut to open PR or contribute to the framework |
| `cry-tag` | Shortcut to create or list release tags (SemVer) |
| `cry-sync` | Shortcut to sync repository (fetch, pull, push) |
| `cry-rebase` | Shortcut to resolve conflicts via rebase |

## How to Use

### Commit changes

```
/cry-commit
```

The agent analyzes changes, creates atomic commits following Conventional Commits, with subject in English and GPG signature.

### Open a Pull Request

```
/cry-contribute pr
```

The agent executes `kata-contribute`, which creates the PR in the origin repository via GitKraken MCP tools.

### Version a release (tags)

```
/cry-tag [version] [message] [commit]
/cry-tag --list
```

The agent runs `kata-tag`: creates an annotated, signed tag in SemVer format or lists existing tags. Optionally provide the commit (ID or message) to point the tag at.

### Full contribution flow

The `codex-contributing` defines the step-by-step process:

1. Open discussion in GitHub Discussions (Ideas category)
2. Approved discussion becomes an issue
3. Create branch from main (`feat/name`, `fix/name`, `docs/name`)
4. Implement (following commit Lexis)
5. Open PR filling the template
6. Keep CI green and respond to review
7. Merge by maintainer

## References

- [Guardia CONTRIBUTING](https://hub.guardia.finance/docs/community/CONTRIBUTING/)
- `.github/pull_request_template.md` — PR template
- `.github/CODEOWNERS` — Codeowners file
