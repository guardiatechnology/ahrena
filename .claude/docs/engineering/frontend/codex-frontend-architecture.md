# Codex: Frontend Architecture

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Architectural patterns for modern frontend applications (React/Next.js as reference; adaptable to Vue/Angular/Svelte)

## Content

### Layers of a frontend application

```
┌─────────────────────────────────────────────────┐
│  Pages / Routes                                 │  (Next.js app/, Vue router, Angular routes)
│  - Composition of features into a page          │
├─────────────────────────────────────────────────┤
│  Features                                       │
│  - Self-contained functionality blocks          │
│  - (e.g., refund-form, transaction-list)        │
├─────────────────────────────────────────────────┤
│  Components (UI kit)                            │
│  - Reusable primitives: Button, Input,          │
│    Modal, Table. No business logic.             │
├─────────────────────────────────────────────────┤
│  Hooks / Composables                            │
│  - Reusable logic: useAuth, useQuery,           │
│    useForm. No UI.                              │
├─────────────────────────────────────────────────┤
│  Services / API clients                         │
│  - HTTP API access layer                        │
│  - Types derived from OAS                       │
├─────────────────────────────────────────────────┤
│  State (server + client)                        │
│  - Server state: React Query / SWR / TanStack   │
│  - Client state: Zustand / Jotai / Context      │
└─────────────────────────────────────────────────┘
```

### Component composition principles

1. **Single Responsibility:** a component does one thing well. If the file exceeds 200 lines or has more than 3 visual responsibilities, split it.
2. **Presentational vs Container:**
   - **Presentational:** receives data via props, does no I/O. Easy to test and reuse.
   - **Container:** fetches data, combines hooks, passes to presentational.
   - In modern React with hooks, the separation is more fluid, but the principle remains: keep composition clear.
3. **Minimal and typed props:** do not pass large objects when 2-3 fields suffice.
4. **Composition over configuration:** `<Card><CardHeader/><CardBody/></Card>` is more flexible than `<Card variant="big" showHeader />`.
5. **No side effects in rendering:** `useEffect` for side effects; pure render for UI.

### State management

**Fundamental rule:** separate **server state** from **client state**.

| Type | Example | Tool |
|---|---|---|
| **Server state** | List of refunds, user profile | **TanStack Query (React Query)**, SWR, RTK Query |
| **Global client state** | Theme, language, cart (pre-checkout) | **Zustand**, Jotai, Context API |
| **Form state** | Form fields being edited | **react-hook-form**, Formik, VeeValidate |
| **URL state** | Filters, pagination, open modal | **searchParams** (Next.js), `useSearchParams` |
| **Local state** | Ephemeral component state | `useState`, `useReducer` |

**Antipatterns to avoid:**
- Redux for everything — local useState is sufficient in 70% of cases
- Context for frequently changing state — causes cascading re-renders
- Duplicating server state in client state — keep the query as source of truth

### Data layer (HTTP)

1. **Centralized HTTP client:** an `apiClient` configured with baseURL, interceptors, auth.
2. **Types derived from OAS:** use `openapi-typescript` or `orval` to generate types from the spec (produced by `warrior-daedalus`).
3. **Queries and mutations:**
   - `useQuery` for reads; automatic caching, background refetch.
   - `useMutation` for writes; optimistic updates when applicable.
4. **Error handling:** `error boundary` for unexpected errors; `onError` on queries for expected errors.

### Routing

1. **File-based (Next.js app/):** pages defined by folder structure.
2. **Shared layout:** headers, sidebars in `layout.tsx` to avoid duplication.
3. **Loading and error states:** `loading.tsx`, `error.tsx` in Next.js app router.
4. **Automatic code splitting:** each route in a separate chunk; lazy load non-critical features.

### Styling

Main options (pick one and keep it consistent):

| Approach | When to use |
|---|---|
| **Tailwind CSS** | Rapid prototyping; large teams; consistent design system |
| **CSS Modules** | Per-component encapsulation; no runtime overhead |
| **CSS-in-JS (Emotion, Styled)** | Dynamic themes; value sharing with JS |
| **Vanilla Extract** | Zero runtime; types in CSS |

**Cross-cutting rule:** define **design tokens** (colors, spacing, typography) in a single place, referenced by all components.

### Performance

1. **Code splitting:** React.lazy, dynamic import, route-based splits.
2. **Memoization:** `useMemo`/`useCallback` only when profiling shows real gain.
3. **Virtualization:** large lists (>100 visible items) use `react-window` or TanStack Virtual.
4. **Images:** `next/image` (Next.js) or equivalent for srcset, lazy load, WebP/AVIF.
5. **Prefetching:** `<Link prefetch>` for likely routes.
6. **Core Web Vitals as target metric:**
   - LCP < 2.5s
   - FID/INP < 200ms
   - CLS < 0.1

### Directory structure (Next.js app router)

```
src/
├── app/                        # Routes (Next.js)
│   ├── layout.tsx
│   ├── page.tsx
│   └── refunds/
│       ├── page.tsx
│       └── [id]/page.tsx
├── features/                   # Business features
│   └── refunds/
│       ├── components/
│       ├── hooks/
│       ├── services/
│       └── index.ts
├── components/                 # UI kit
│   ├── Button/
│   ├── Input/
│   └── Modal/
├── hooks/                      # Global hooks
├── lib/                        # Utils, apiClient, helpers
├── types/                      # Shared types
└── styles/                     # Global CSS, tokens
```

### Internationalization (i18n)

For projects with multiple languages:

1. **Library:** `next-intl`, `react-i18next`, `formatjs`.
2. **Semantic keys:** `button.submit`, not `Submit`.
3. **Pluralization and format:** use ICU MessageFormat.
4. **Date and number:** `Intl.DateTimeFormat`, `Intl.NumberFormat`.

### Observability

1. **Error tracking:** Sentry, Rollbar, or equivalent; `ErrorBoundary` sends to the service.
2. **Web vitals:** collect LCP/FID/CLS in production (`web-vitals` lib + custom endpoint or Vercel Analytics).
3. **User analytics:** business events (who clicked, who completed flow); no PII.
4. **Structured logging:** avoid `console.log` in production; use a proper logger with levels.
