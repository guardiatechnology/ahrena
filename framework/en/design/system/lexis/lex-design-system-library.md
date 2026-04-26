# Lexis: Mandatory Use of the @guardia/design-system Library

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Guardia platform, site, app, and digital materials

## Purpose

Ensure visual coherence, accessibility, and governance when consuming UI components. Reimplementing buttons, inputs, cards, alerts, forms, or any other pattern outside the official library creates color drift, token drift, and accessibility regressions — all of which break the coherence promise of the Brand Kit and the Design System.

## Law

> **Every Guardia interface (platform, site, app, transactional emails, dashboards) MUST consume components from the `@guardia/design-system` library. Reimplementing primitives (button, input, card, alert, modal, badge, toast, etc.) or using hardcoded color, typography, or spacing values instead of the tokens exposed by the library is FORBIDDEN. Composition (combining existing components) is the only permitted path for variations; new primitives follow the Design System governance flow.**

## Coverage

- **Applies to:** all versioned UI code at Guardia (React, React Native, emails, landing pages, micro-frontends).
- **Bound agents:** frontend/mobile developers, designers opening code PRs, AI agents that generate components (warrior-hephaestus, warrior-iris and variants).
- **Exceptions:** only during throwaway prototyping in repositories tagged `prototype/*` or `spike/*`. Any code progressing to production, even via partial merge, MUST migrate to `@guardia/design-system` before deploy. Real gaps (missing component) MUST be addressed by contributing to the library, recorded in an ADR.

## Consequences of Violation

1. **PR block:** design review and CI reject PRs that import `shadcn/ui`, `@radix-ui/*`, `mui`, `chakra-ui` directly, or define Tailwind classes with colors outside tokens.
2. **Color drift:** loose components do not receive token updates (e.g., rebrand, WCAG adjustment) and break coherence across channels.
3. **Remediation:** replace the local component with the equivalent in `@guardia/design-system`; when no equivalent exists, open an issue in the library repo with use case and proposal before proceeding.

## Examples

### Correct

```tsx
import { Button, Card, Alert, useTokens } from '@guardia/design-system';

export function ApprovalCard({ onApprove }: Props) {
  return (
    <Card variant="elevated">
      <Alert tone="warning">Pending approval</Alert>
      <Button intent="primary" onClick={onApprove}>Approve</Button>
    </Card>
  );
}
```

### Incorrect

```tsx
// Reimplements primitives and uses hardcoded colors — VIOLATES THE LAW
export function ApprovalCard({ onApprove }: Props) {
  return (
    <div style={{ background: '#4F186D', padding: 24, borderRadius: 8 }}>
      <span style={{ color: '#FFC30A' }}>Pending</span>
      <button
        onClick={onApprove}
        className="bg-orange-600 text-white px-4 py-2"
      >
        Approve
      </button>
    </div>
  );
}
```

## Automated Validation

- **Tooling:** ESLint with `no-restricted-imports` blocking `@radix-ui/*`, `@mui/*`, `@chakra-ui/*`, `shadcn-ui`; Stylelint/Tailwind plugin forbidding non-tokenized colors; automated PR review (warrior-hephaestus) flagging reimplementations.
- **Timing:** pre-commit (lint), CI (build + lint), PR review.
- **Metric:** 0 forbidden imports on `main`; 0 hardcoded color values outside tokens; mean time < 1 day between identifying a gap and opening an issue in the library.

## References

- [codex-design-system](../codex/codex-design-system.md), [codex-design-system-components](../codex/codex-design-system-components.md)
- Library: `@guardia/design-system` ([repo](https://github.com/guardiatechnology/design-system))
- Visual catalog: Chromatic; design mirror: Figma
