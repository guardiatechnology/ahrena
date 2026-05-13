# Codex: Guardia Contribution Flow

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Contributing to Guardia repositories

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

### Contribution by type

Contribution templates (issue and PR) live in **`.ahrena/contributing_templates/`** (5 .md files), installed by the Ahrena setup from `framework/templates/contributing_templates/` and preserved if they already exist. The **3 katas** (issue, PR, discussion) guide the use of **GitHub MCP** (or equivalent server) to create issues, PRs, and discussions; fallback to `gh` CLI when MCP is unavailable.

| Type                  | Kata                          | Cry (one per type)           | Template (in .ahrena/contributing_templates/)     | Required labels |
| --------------------- | ----------------------------- | --------------------------- | ------------------------------------------------- | --------------- |
| Feature Request       | kata-contributing-issue       | cry-new-feature-request     | `feature-request.md`                              | `feature request ➕` |
| Epic                  | kata-contributing-issue       | cry-new-epic                | `epic.md`                                         | `epic` |
| User Story (API)      | kata-contributing-issue       | cry-new-user-story-api      | `user-story-for-api.md`                           | `api`, `user story 🎯` |
| User Story (Frontend) | kata-contributing-issue       | cry-new-user-story-frontend | `user-story-for-frontend.md`                      | `frontend`, `user story 🎯` |
| Tech Task           | kata-contributing-issue       | cry-new-tech-task         | `tech-task.md`                                  | one of: `documentation 📃`, `ci 🏗️`, `enhancement 🔝`, `evolvability ♻️` |
| Pull Request          | kata-contributing-pr          | cry-new-pr                  | `pull_request_template.md`                        | — |
| Discussion            | kata-contributing-discuss     | cry-new-discuss             | (Golden Circle; no .md)                           | — |

- **Generic cry:** `cry-contribute` — for generic contributions; MAY delegate to the per-type cries or ask which type.
- **References:** the 3 katas (`kata-contributing-issue`, `kata-contributing-pr`, `kata-contributing-discuss`) and the 7 cries (`cry-new-feature-request`, `cry-new-epic`, `cry-new-user-story-api`, `cry-new-user-story-frontend`, `cry-new-tech-task`, `cry-new-pr`, `cry-new-discuss`).

### Standards and Conventions

| Aspect | Standard |
|--------|----------|
| Discussions | GitHub Discussions, category "Ideas" |
| Issues | One of 5 templates; labeled; answers Why/What/How (`lex-issue-quality`) |
| Branches | `{type}/{issue-number}-{slug}` (e.g. `feat/42-oauth2`) — see `lex-git-branches` |
| PRs | Title in Conventional Commits; body includes `Closes #N` or `Refs #N` (`lex-issue-first`) |
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
