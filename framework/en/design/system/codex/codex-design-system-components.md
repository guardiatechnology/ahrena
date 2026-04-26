# Codex: Components via @guardia/design-system

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** UI component consumption in Guardia code

## Overview

The `@guardia/design-system` library is the source of truth for Guardia's UI components (buttons, cards, alerts, forms, badges, content blocks, agentic layouts, charts). This Codex guides how to consume, compose, and contribute to the library, sustaining the law [lex-design-system-library](../lexis/lex-design-system-library.md): **all Guardia UI MUST consume `@guardia/design-system`**.

## Context

- **Domain:** component consumption in React/React Native (and other runtimes the library may support).
- **Target audience:** frontend, mobile, fullstack, AI agents that produce UI code (warrior-hephaestus, warrior-iris).
- **Update trigger:** at every library release; when the *Componentes* page in Notion is revised.

## Content

### Core premise

`@guardia/design-system` encapsulates the Design System stack (shadcn/ui + Tailwind + CopilotKit + Lucide + brand tokens) and exposes ready-made components with tokens and accessibility built in. **Do not consume shadcn/ui, Radix, MUI, or Chakra directly.** The contract with the brand lives in the library, not in the primitives.

### Installation

```bash
# pnpm (preferred)
pnpm add @guardia/design-system

# npm
npm install @guardia/design-system

# yarn
yarn add @guardia/design-system
```

Configure the stylesheet and provider at app boot:

```tsx
import '@guardia/design-system/styles.css';
import { GuardiaProvider } from '@guardia/design-system';

export function App({ children }: { children: React.ReactNode }) {
  return <GuardiaProvider>{children}</GuardiaProvider>;
}
```

> Exact names (`GuardiaProvider`, import paths) follow what is published in the library; check the `@guardia/design-system` repo README before copying literally.

### How to choose a component

1. Search first in the Chromatic catalog or the library README.
2. Combine existing variants and props before creating local abstractions.
3. If no equivalent exists, open an issue in the `@guardia/design-system` repo with:
   - real use case (link to the screen or material driving the demand);
   - API proposal (props, variants, states);
   - visual reference (Figma or screenshot).
4. While the issue is discussed, build a *temporary* wrapper inside the product, marked with a TODO pointing to the issue — never a parallel primitive (without tokens).

### Main components (expected map)

The library organizes components into families. Names may vary across releases; the table below is a conceptual reference:

| Family | Examples | Use |
|--------|----------|-----|
| Action | `Button`, `IconButton`, `MenuButton` | Trigger commands or navigation |
| Input | `Input`, `TextArea`, `Select`, `Combobox`, `DatePicker`, `Switch`, `Checkbox`, `Radio` | Data capture |
| Feedback | `Alert`, `Toast`, `Banner`, `Skeleton`, `EmptyState` | Informative states |
| Structure | `Card`, `Sheet`, `Dialog`, `Drawer`, `Tabs`, `Accordion` | Containers and segmentation |
| Typography | `Heading`, `Text`, `Code`, `InlineCode` | Token-driven text hierarchy |
| Navigation | `Breadcrumbs`, `Pagination`, `Stepper` | In-product wayfinding |
| Data | `Table`, `DataGrid`, `Badge`, `Avatar`, `Progress`, `Stat` | Tabular display and indicators |
| Charts | `LineChart`, `BarChart`, `AreaChart`, `PieChart` (on shadcn/ui Charts) | Data viz with semantic colors |
| Brand | `Logo`, `LogoMark` | Automatic variant selection per background |
| Agentic | `ChatPanel`, `Workspace`, `PlanTrace`, `SourceCard`, `ApprovalGate` | AI-First patterns (CopilotKit) |

> This table is living. The source of truth is the Chromatic catalog + repo README.

### Composition example

```tsx
import {
  Card,
  Heading,
  Text,
  Stat,
  Badge,
  Button,
  Alert,
} from '@guardia/design-system';

export function ReconciliationSummary({ summary, onApprove }: Props) {
  return (
    <Card variant="elevated" padding="lg">
      <Heading level={2}>Cielo reconciliation — Apr 25</Heading>
      <Text tone="muted">127 transactions analyzed in 4m12s</Text>

      <Stat label="Reconciled" value={119} tone="positive" />
      <Stat label="Pending" value={8} tone="attention" />

      {summary.pendingCount > 0 && (
        <Alert tone="warning">
          {summary.pendingCount} transactions need review before close.
        </Alert>
      )}

      <Badge tone="info">Source: bank statement + Cielo EDI</Badge>
      <Button intent="primary" onClick={onApprove}>Approve close</Button>
    </Card>
  );
}
```

Note: no inline styles, no hex colors, no shadcn/ui or Radix imports.

### Composition vs. customization

- **Composition (preferred):** combine ready-made components. Variations via `variant`, `intent`, `tone`, `size`.
- **Slot pattern:** when needing to replace a region, use slots/children exposed by the API.
- **Style overrides:** allowed *only* for density/spacing via tokens (e.g., `paddingY="sm"`). Never override colors or typography.
- **Local customization:** when unavoidable, isolate in an *adapter* clearly marked `// TODO: contribute to @guardia/design-system — issue #N`.

### Tokens

Tokens are exposed by the library via theme (CSS variables) and typed helpers (e.g., `useTokens()`). Never use hardcoded hex values, fonts, or sizes; always reference tokens.

```tsx
import { useTokens } from '@guardia/design-system';

const tokens = useTokens();
// tokens.color.brand.violet[500] → '#4F186D'
// tokens.spacing.lg → '24px'
```

### Accessibility

- Each library component already delivers: visible focus, keyboard support, correct ARIA, minimum WCAG 2.1 AA contrast.
- In product, ensure composition preserves these properties: do not wrap `Button` in `<div onClick>`, do not hide `<label>`, do not replace `Heading` with a styled `<div>`.
- Test with axe-core and a screen reader on critical screens.

### Versioning and updates

- The library follows **SemVer**. Breaking changes → major; new features → minor; fixes → patch.
- Update regularly (ideally via Renovate/Dependabot weekly).
- On breaking changes, read the changelog first; run visual tests (Chromatic) and E2E.

### When to contribute vs. when to consume

| Situation | Action |
|-----------|--------|
| Component exists and fits | Consume directly |
| Component exists but lacks variant/prop | Open a PR in `@guardia/design-system` adding the variant |
| Component does not exist, repeatable pattern | Open issue + propose new component |
| Unique product pattern, non-reusable | Compose with library primitives inside the product, without becoming a parallel primitive |

## References

- [lex-design-system-library](../lexis/lex-design-system-library.md) — mandatory use
- [codex-design-system](codex-design-system.md) — overview
- [codex-ai-first-experience](codex-ai-first-experience.md) — agentic components
- Repo: `@guardia/design-system` (github.com/guardiatechnology/design-system)
- Chromatic catalog
