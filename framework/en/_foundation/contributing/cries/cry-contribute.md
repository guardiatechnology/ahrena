# Cry: Contribute to Guardia Repository

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut for contributing issues, PRs, and discussions to Guardia repositories

## Invocation

```
/cry-contribute <action> [options]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `action` | Yes | Contribution type: `pr`, `issue`, `discuss` | `pr` |
| `options` | No | Additional parameters for the action | `--type feature-request` |

## Available Actions

### `pr` — Create Pull Request

```
/cry-contribute pr [--base main] [--title "..."]
```

Behavior:
1. Run `kata-commit` to ensure compliant commits (if there are pending changes)
2. Create branch following the convention (`feat/name`, `fix/name`, `docs/name`)
3. Push to remote
4. Open PR via `gh pr create` filling the `.github/pull_request_template.md`:
   - **Description:** summary of the change and resolved issue
   - **Type of Change:** check relevant boxes (bug fix, feature, breaking change, docs, security, performance, refactoring, tests, CI/CD)
   - **Prerequisites:** associate issue, milestone, and correct labels (breaking change, security, feature, bugfix, enhancement, evolvability, documentation)
   - **How Has This Been Tested:** describe executed tests
   - **Checklist:** validate style, self-review, documentation, tests
   - **Related Issues:** reference issues with `Closes #N` or `Related to #N`
   - **Breaking Changes:** describe migrations if applicable
   - **Security Considerations:** security implications
   - **Performance Impact:** benchmarks if applicable
   - **Documentation:** links to updated documentation
5. Set the title in Conventional Commits (in English)
6. Validate that commits are signed (`lex-signed-commits`)

### `issue` — Create Issue

```
/cry-contribute issue [--type <template>]
```

Available templates (defined in `.github/ISSUE_TEMPLATE/`):

| Template | Use | Structure |
|----------|-----|-----------|
| `feature-request` | New feature | User story (As/I want/So that), current vs desired behavior, business value, impact areas |
| `epic` | Epic grouping user stories | Why it is important, what it is about |
| `user-story-for-frontend` | Detailed frontend story | User story, acceptance criteria (Gherkin), entities, metrics, sequence diagrams, mockups |
| `user-story-for-api` | Detailed API story | User story, acceptance criteria (Gherkin), entities, API spec (method, path, headers, schemas), metrics, SLIs/SLOs |

If `--type` is omitted, the agent asks which template to use.

Behavior:
1. Identify the correct template
2. Collect required information from the user (or infer from context)
3. Create the issue via `gh issue create` with the filled template

### `discuss` — Open Discussion

```
/cry-contribute discuss [--category Ideas]
```

Behavior:
1. Verify whether the proposal justifies a discussion (significant changes)
2. Structure the discussion in Golden Circle format (WHAT, WHY, HOW)
3. Open in GitHub Discussions via `gh discussion create`

## Usage Examples

```
# Create PR from current branch
/cry-contribute pr

# Create PR with specific title
/cry-contribute pr --title "feat(auth): implement OAuth2 authentication"

# Create feature request issue
/cry-contribute issue --type feature-request

# Create epic
/cry-contribute issue --type epic

# Create API user story
/cry-contribute issue --type user-story-for-api

# Open discussion before a large change
/cry-contribute discuss
```

## Delegation to per-type cries

For type-guided flow, the user MAY invoke the corresponding cry directly: **cry-new-feature-request**, **cry-new-epic**, **cry-new-user-story-api**, **cry-new-user-story-frontend** (issues), **cry-new-pr** (PR), **cry-new-discuss** (discussion). `cry-contribute` MAY delegate to these cries when the user selects a specific action/type (e.g., `cry-contribute issue` → ask type and delegate to the corresponding cry-new-*, or invoke `kata-contributing-issue` with the type).

## Rules

- Blank issues are disabled — every issue MUST use a template
- Significant changes MUST start with a discussion before becoming an issue
- PRs MUST follow all 4 commit Lexis
- The PR title MUST follow Conventional Commits in English

## Associated Katas

- `kata-contribute` — Complete procedure for contributing via Pull Request (`pr` action)
- `kata-contributing-issue` — Procedure for opening an issue (issue actions; invoked by cries cry-new-feature-request, cry-new-epic, cry-new-user-story-api, cry-new-user-story-frontend)
- `kata-contributing-pr` — Procedure for PR (invoked by cry-new-pr)
- `kata-contributing-discuss` — Procedure for discussion (`discuss` action; invoked by cry-new-discuss)

## References

- `codex-contributing` — Guardia contribution flow (Cry context)
- `kata-commit` — Commit procedure (invoked by `pr`; the Kata consults commit Lexis; see Kata documentation)
- `kata-contribute`, `kata-contributing-pr`, `kata-contributing-issue`, `kata-contributing-discuss` — Contributing katas
- Per-type cries: cry-new-feature-request, cry-new-epic, cry-new-user-story-api, cry-new-user-story-frontend, cry-new-pr, cry-new-discuss
- `.ahrena/contributing_templates/` — Issue and PR templates (after install)
- `.github/ISSUE_TEMPLATE/`, `.github/pull_request_template.md` — Fallback when .ahrena does not exist
