# Lexis: Behavioral Testing in Frontend

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Testing strategy for frontend applications (unit, component, integration, E2E)

## Law

> **Every component with business logic or user interaction MUST have behavioral tests written from the user's point of view. Tests MUST use accessible queries (`getByRole`, `getByLabelText`) instead of structural selectors (`getByTestId` only as last resort). Mocks MUST be limited to external boundaries: API, Date, timers, storage, browser APIs.**

## Rules

### 1. Test behavior, not implementation

The agent **MUST**:

1. Write tests that simulate user actions (click, type, submit, navigate).
2. Assert on the observable result: what changes on the screen, what request is made, what message appears.
3. Avoid assertions about internal component state (`state.loading`), internal method calls, or hook implementation.

```typescript
// ❌ Tests implementation
expect(component.state.loading).toBe(true);

// ✅ Tests behavior
expect(screen.getByRole("status", { name: /loading/i })).toBeInTheDocument();
```

### 2. Prefer accessible queries

Order of preference (per Testing Library):

1. `getByRole` with `name` — priority; reflects how screen readers see the UI
2. `getByLabelText` — for inputs with labels
3. `getByPlaceholderText`, `getByText` — when there is no semantic role
4. `getByDisplayValue`, `getByAltText`, `getByTitle`
5. `getByTestId` — **last resort**, when no semantic query works

Using `getByTestId` without justification indicates non-accessible UI (see `lex-frontend-accessibility`).

### 3. Mocks only at boundaries

The agent **MAY** mock:

- HTTP calls (MSW, `fetch`, axios) — API boundary
- `Date.now()`, `setTimeout` — timing boundary
- `localStorage`, `sessionStorage`, `indexedDB` — persistence boundary
- `navigator.clipboard`, `navigator.geolocation` — browser API boundary
- `crypto.randomUUID` — when determinism is needed

The agent **MUST NOT**:

- Mock internal application hooks (`useAuth`, `useCart`) — render with a real provider
- Mock child components — test the real tree
- Mock internal utility functions — use them with test data

### 4. Coverage by test type

| Type | When to use | Target coverage |
|---|---|---|
| Unit (pure) | Pure functions, utils, formatters | 100% |
| Component | Components with logic or interaction | Coverage of visible states + user flows |
| Integration | Multiple components together (form + submit, list + filter) | Main flows |
| E2E (Playwright, Cypress) | Critical journeys (login, checkout, onboarding) | 3-7 main journeys |

### 5. No snapshots without review

Snapshot tests (`toMatchSnapshot`) **MUST**:

- Be reviewed on every change — the snapshot diff needs to be read and approved
- Be small and focused (not a snapshot of the entire page)
- Have a message explaining why the snapshot exists

Large and blindly accepted snapshots have zero value.

## Applicability

- **Applies to:** all frontend code with business logic or interaction (components, hooks, stores)
- **Linked agents:** `warrior-hephaestus`
- **Exceptions:** purely decorative components (e.g., `<Divider />`, icons) may not require tests — document the decision

## Automated Validation

- **Tool:** Jest, Vitest, Testing Library; E2E with Playwright or Cypress
- **Moment:** locally in dev (watch mode), CI on PR, `kata-quality-gate` Check 4 in `engineering/workflow`
- **Metric:** tests pass; coverage per `quality.coverage_threshold` in `.ahrena/.directives`
