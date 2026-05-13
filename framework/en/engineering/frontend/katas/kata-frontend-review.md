# Kata: Review Frontend Code

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Systematic review of frontend code for correctness, accessibility, types, tests, security, and performance

## Objective

Perform a review of frontend code (typically on a PR or diff), verifying adherence to applicable Lexis and identifying improvements. Produces a structured report with findings categorized by severity (blocking, recommendation, note), applicable as a human review or as part of `kata-quality-gate` in the Issue-Driven flow.

## When to Use

- Frontend PR review before merge
- Periodic quality review of existing code
- Complement to `kata-quality-gate` when the focus is frontend

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Diff to review | Yes | `git diff {base}..HEAD` or specific PR |
| Context | No | Issue, ACs, expected architecture (coming from `.ahrena/issues/{n}/` if applicable) |
| Scope | No | Specific components or complete diff review |

## Workflow

```
Progress:
- [ ] 1. Collect diff and context
- [ ] 2. Review typing (lex-frontend-typing)
- [ ] 3. Review tests (lex-frontend-testing)
- [ ] 4. Review accessibility (lex-frontend-accessibility)
- [ ] 5. Review security (lex-frontend-security)
- [ ] 6. Review architecture and composition
- [ ] 7. Review performance
- [ ] 8. Consolidate report by severity
```

### Step 1: Collect diff and context

1. Get the diff: `git diff {base}..HEAD`.
2. List touched files by type (`.tsx`, `.ts`, `.css`, tests, config).
3. If there are ACs (Issue-Driven flow), read `.ahrena/issues/{n}/02-requirements.md`.

### Step 2: Review typing

Against `lex-frontend-typing`:

- [ ] Explicit `any`? Justified in a comment?
- [ ] Component props typed?
- [ ] Hooks with typed state when not inferable?
- [ ] API contracts typed (OAS or Zod)?
- [ ] `unknown` used where `any` would be laziness?
- [ ] Does `tsc --noEmit` pass?

### Step 3: Review tests

Against `lex-frontend-testing`:

- [ ] Does each component with logic or interaction have a test?
- [ ] Do tests use `getByRole`/`getByLabelText` instead of `getByTestId`?
- [ ] Do tests verify behavior, not implementation?
- [ ] Mocks only at boundaries (API, Date, storage)?
- [ ] Are snapshots small and reviewed?
- [ ] Are happy path + error + loading + empty covered?
- [ ] If Issue-Driven flow: does each test mark the corresponding AC-N?

### Step 4: Review accessibility

Against `lex-frontend-accessibility`:

- [ ] Semantic HTML (no `<div>` where `<button>` would fit)?
- [ ] Images with appropriate `alt`?
- [ ] Forms with associated labels?
- [ ] Does keyboard navigation work? (test mentally or with Tab)
- [ ] Visible focus?
- [ ] Adequate contrast (4.5:1 for normal text)?
- [ ] Modals with focus trap + `aria-modal`?
- [ ] Dynamic content announced (`role="status"`, `aria-live`)?
- [ ] Run `axe`/`jest-axe` on modified components.

### Step 5: Review security

Against `lex-frontend-security`:

- [ ] `dangerouslySetInnerHTML` / `innerHTML` without sanitization?
- [ ] Secrets in the bundle? (search for API keys, tokens in `.ts`/`.tsx` code)
- [ ] Tokens in `localStorage` vs HttpOnly cookie?
- [ ] Two-level input validation (client + server)?
- [ ] `target="_blank"` with `rel="noopener noreferrer"`?
- [ ] Audited dependencies (`yarn audit`)?

### Step 6: Review architecture and composition

Against `codex-frontend-architecture`:

- [ ] Components with single responsibility?
- [ ] Feature isolated in `features/` with barrel export?
- [ ] Clear presentational/container separation?
- [ ] Server state via TanStack Query (or project equivalent), not `useState` + `useEffect`?
- [ ] No obvious logic duplication (hooks extracted when appropriate)?
- [ ] No `useEffect` doing manual data fetching when a query library exists?
- [ ] Design tokens respected (no magic color/spacing values)?

### Step 7: Review performance

- [ ] Large lists virtualized?
- [ ] Images with `next/image` or equivalent srcset?
- [ ] Code splitting on routes?
- [ ] `useMemo`/`useCallback` used with justification (not defensively)?
- [ ] Reasonable bundle size? (run analysis if deps changed)
- [ ] No unnecessary re-renders (verify via React DevTools Profiler if suspected)?

### Step 8: Consolidate report by severity

Structure findings:

```markdown
# Frontend Review — {PR or issue} #{n}

- **Date:** {YYYY-MM-DD}
- **Files reviewed:** {n}
- **Findings:** {B} blocking, {R} recommendations, {N} notes

## Blocking (prevent merge)

### F-1: {title}
- **Category:** {Typing | Testing | A11y | Security | Architecture | Performance}
- **Location:** `src/features/refunds/RefundForm.tsx:42`
- **Problem:** {what is wrong}
- **Recommendation:** {proposed fix with code example}
- **Reference:** `lex-frontend-{...}`

## Recommendations (improvements)

### F-2: ...

## Notes (informational)

### F-3: ...

## Positive Summary

{2-3 well-executed points worth highlighting}
```

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Review report | Structured Markdown | Response to user or `docs/reviews/` |
| PR comments | Line-by-line comments via GitHub MCP | PR on GitHub (optional) |

## Restrictions

- **Review ≠ rewrite:** this kata points out problems; does not modify code directly.
- **Objective severity:** blocking = violates Lexis; recommendation = quality improvement; note = observation.
- **No guesswork:** every finding has a reference to the applicable Lexis or Codex.
- **Constructive tone:** point out the problem with a suggested solution, not merely criticize.

## References

- `lex-frontend-typing`, `lex-frontend-testing`, `lex-frontend-accessibility`, `lex-frontend-security`
- `codex-frontend-architecture`
- `kata-quality-gate` — in the Issue-Driven flow, integrates the findings
- `kata-mcp-github-read` — to review diff on remote PR
