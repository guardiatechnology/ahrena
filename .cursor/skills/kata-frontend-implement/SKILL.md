---
name: kata-frontend-implement
description: "Implement Frontend Feature. Frontend feature implementation from requirement to tested, typed, and accessible code"
---

# Kata: Implement Frontend Feature

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Frontend feature implementation from requirement to tested, typed, and accessible code

## Workflow

```
Progress:
- [ ] 1. Clarify requirements and contracts
- [ ] 2. Consult codebase patterns
- [ ] 3. Plan structure (components, hooks, layers)
- [ ] 4. Implement types and contracts
- [ ] 5. Implement components with accessibility
- [ ] 6. Implement data integration
- [ ] 7. Write behavioral tests
- [ ] 8. Validate (lint, typecheck, test, a11y)
```

### Step 1: Clarify requirements and contracts

1. Consult `.ahrena/.directives` per `lex-directives`.
2. If ACs are numbered (Issue-Driven flow), map each AC to a testable behavior.
3. Batched questions to the user (up to 5 per round):
   - Loading, error, and empty states: how do they behave?
   - Form validations: client-only or with server feedback?
   - Behavior on mobile vs desktop?
   - Authentication required to access?
   - Feature flag or A/B test applicable?

### Step 2: Consult codebase patterns

1. Read `codex-frontend-architecture` and identify:
   - Where features live (`src/features/`, `app/`, etc.)
   - Where the UI kit lives (`src/components/`)
   - Which server state library (TanStack Query, SWR, etc.)
   - Which forms library (react-hook-form, Formik)
   - Which styling approach (Tailwind, CSS Modules, etc.)
2. Follow existing conventions before introducing new ones.

### Step 3: Plan structure

For the feature, decide:

1. **New routes** (if applicable): path, layout, loading/error states.
2. **Components** to create or modify — list with each one's responsibility.
3. **Hooks/composables** to create — reusable logic.
4. **API integration** — which endpoints will be consumed.
5. **State** — server, client, URL, form.
6. **Tests** — which behaviors to test and at which level (unit, component, integration, E2E).

Present the plan to the user before coding large features (> 200 lines).

### Step 4: Implement types and contracts

1. If an OAS exists, generate types via `openapi-typescript` or validate with Zod.
2. Define entity types and component props.
3. Define custom event types (if any).
4. Apply `lex-frontend-typing`: strict, no `any` without justification.

### Step 5: Implement components with accessibility

For each component:

1. Use semantic HTML (`<button>`, `<form>`, `<nav>`, etc.) — `lex-frontend-accessibility`.
2. Labels associated with inputs, `aria-*` when necessary.
3. Visible focus states.
4. Test keyboard navigation during development.
5. Apply existing design tokens for spacing, colors, typography.

### Step 6: Implement data integration

1. **Server state:** use the project's library (TanStack Query, SWR, etc.) — automatic cache, error, loading.
2. **Mutations:** include `onSuccess` to invalidate queries or update cache; optimistic update where appropriate.
3. **Forms:** validate with Zod/Yup on the client; reuse schema for types.
4. **Security:** never expose secrets in the bundle (`lex-frontend-security`); sanitize any dynamic HTML.

### Step 7: Write behavioral tests

For each AC (or behavior, if there is no structured flow):

1. Write test from the user's point of view (`lex-frontend-testing`).
2. Use accessible queries (`getByRole`, `getByLabelText`).
3. Mark each test with the corresponding AC (if Issue-Driven flow):

```typescript
describe("Refund form", () => {
  it("creates refund on submit AC-1", async () => {
    render(<RefundForm paymentId="p123" />);
    await userEvent.type(screen.getByLabelText(/amount/i), "100");
    await userEvent.click(screen.getByRole("button", { name: /submit/i }));
    expect(await screen.findByText(/refund processing/i)).toBeInTheDocument();
  });
});
```

4. Cover: happy path, validation error, API error, loading state, empty state.
5. Add automated a11y tests with `jest-axe` or `axe-core/playwright`.

### Step 8: Validate

Run locally:

1. `yarn typecheck` (or `tsc --noEmit`) — 0 errors.
2. `yarn lint` — including `eslint-plugin-jsx-a11y`.
3. `yarn test` — all tests pass.
4. `yarn test:e2e` if there is relevant E2E.
5. Manual Lighthouse on an affected page (accessibility ≥ 95, performance ≥ 80).

If on the Issue-Driven flow, `kata-quality-gate` will run these checks systematically at Gate 2.

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Feature code | `.ts`, `.tsx`, `.css`, etc. | Per project architecture |
| Tests | `.test.ts`, `.test.tsx` | Next to components or in `__tests__/` |
| Types | Interfaces and schemas | In `types/` or alongside components |
| Component documentation (if reusable) | Storybook or JSDoc | Per project standard |

## Restrictions

- **Follow existing patterns:** before introducing a new pattern, check if there is no equivalent already used in the codebase.
- **Do not break accessibility:** no commit may degrade a11y (Lighthouse, axe must remain green).
- **No implicit `any`:** `lex-frontend-typing` is mandatory.
- **Behavior tests, not implementation tests:** `lex-frontend-testing`.
- **Small commits:** separate structure/skeleton from logic; forms from integration; tests from production code.
