# Lexis: Frontend Accessibility (WCAG 2.1 AA)

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Accessibility across all web interfaces produced by the frontend application

## Purpose

Accessibility is not an optional feature — it is a legal requirement (LGPD art. 18, Brazilian Inclusion Law, ADA, European EAA) and an ethical one. An inaccessible UI excludes users with visual, motor, cognitive, or auditory disabilities, and impoverishes the experience for everyone (keyboard users, assistive devices, noisy environments). For AI agents generating frontend code, ignoring accessibility is building legal and human debt.

This Lexis exists to ensure that **every UI produced meets at least WCAG 2.1 level AA**, that **interactive elements are keyboard-navigable**, that **content is announced correctly by screen readers**, and that **color contrast is adequate**.

## Law

> **Every UI produced MUST meet WCAG 2.1 level AA as a minimum. Interactive elements MUST be reachable and operable via keyboard. Images and icons with meaning MUST have alternative text. Forms MUST have associated labels. Colors MUST meet a contrast ratio of 4.5:1 for normal text and 3:1 for large text. Dynamic state MUST be announced to assistive technologies.**

## Rules

### 1. Semantic HTML

The agent **MUST**:

1. Use native elements: `<button>`, `<a>`, `<nav>`, `<main>`, `<header>`, `<footer>`, `<article>`, `<section>`.
2. Not reinvent: a `<div onClick={...}>` with role and tabindex is worse than a `<button>`.
3. Use correct heading hierarchy: a single `h1` per page, `h2` for sections, `h3` nested under `h2`, etc.

### 2. Keyboard navigation

Every interactive element **MUST**:

1. Be reachable via `Tab` (logical order).
2. Be activatable via `Enter` (links) or `Space` (buttons, checkboxes).
3. Have visible focus (do not remove `:focus-visible` from CSS).
4. Support `Esc` to close modals, dropdowns, drawers.
5. Support `Arrow` keys in lists, menus, tabs, radio groups (per ARIA Authoring Practices).

### 3. Images and media

1. **Every `<img>`** with meaning **MUST** have a descriptive `alt`.
2. **Decorative images** use `alt=""` (explicit, not omitted).
3. **Icons that are buttons** use `aria-label` or visually hidden text (`.sr-only`).
4. **Videos** must have captions; **audios** must have transcripts.

### 4. Forms

1. **Every `<input>`, `<textarea>`, `<select>`** **MUST** have an associated `<label>` via `htmlFor` or nesting.
2. **Required fields** marked with `required` and visual indication + `aria-required="true"`.
3. **Validation errors** exposed via `aria-invalid="true"` + message in `aria-describedby`.
4. **Groupings** use `<fieldset>` + `<legend>`.

### 5. Contrast and colors

1. **Normal text (≤18px)**: minimum contrast 4.5:1 against the background.
2. **Large text (≥18px bold or ≥24px regular)**: minimum contrast 3:1.
3. **Icons and graphic elements**: minimum contrast 3:1.
4. **Color is never the only indicator** of state (e.g., red error also has icon + text).
5. Test with automated tools (axe, Lighthouse) and manually in "color blindness" mode.

### 6. Dynamic content

1. **Asynchronous loading** uses `aria-busy="true"` or `role="status"` to indicate state.
2. **Flash messages (toasts, alerts)** use `role="alert"` (assertive) or `role="status"` (polite).
3. **Modals** are focus-trapped and return focus to the element that opened them; use `aria-modal="true"` and `role="dialog"`.
4. **SPA routes** move focus to the new content after navigation.

### 7. Language and reading order

1. **`<html lang="en">`** (or the project's default language).
2. **Content in another language** uses `lang="pt-BR"` on the parent element.
3. **Reading order** in the DOM reflects visual order (no `order` in flex/grid breaking logical flow).

## Applicability

- **Applies to:** every rendered UI, including third-party library components (if a library is not accessible, replace or contribute with a fix)
- **Linked agents:** `warrior-hephaestus` and any other agent that generates frontend
- **Exceptions:** None. Lexis admit no exceptions.

## Consequences of Violation

1. **User exclusion:** people with disabilities cannot use the application — ethical and reach problem
2. **Legal risk:** LGPD, Brazilian Inclusion Law (LBI), EAA may result in regulatory or judicial actions
3. **Impaired SEO:** inaccessible sites rank worse (Google uses accessibility signals)
4. **Remediation:** run axe/Lighthouse; fix critical violations immediately; add accessibility tests to CI

## Automated Validation

- **Tool:**
  - `eslint-plugin-jsx-a11y` (lint)
  - `@axe-core/react` or `jest-axe` (tests)
  - Lighthouse accessibility audit (CI)
  - Playwright/Cypress + axe-core (E2E)
- **Moment:** every PR; manual screen reader check on every significant release
- **Metric:** 0 automatically detectable WCAG AA violations

## References

- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)
- [Brazilian Inclusion Law (LBI)](http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm)
- `lex-frontend-testing` — accessible queries in tests
