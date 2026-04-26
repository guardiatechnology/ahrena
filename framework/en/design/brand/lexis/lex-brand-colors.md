# Lexis: Approved Color Palette and WCAG Combinations

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Guardia visual identity at any touchpoint

## Purpose

Ensure recognition and accessibility. The Guardia palette carries meaning (Trust, Efficiency, Welcoming, Excellence, Stability). Off-palette colors dilute the brand; combinations without contrast block users and violate WCAG 2.1.

## Law

> **Every Guardia piece (interface, material, document, post, slide, email) MUST use exclusively the official palette — Bright Yellow #FFC30A, Warm Orange #E07400, Soft Pink #DB6286, Deep Violet #4F186D, Baltic Gray #3A3A44, Mono White #FDFDFD, and Mono Black #0E1016, with the 100/200/500/700/900 scales — and MUST meet WCAG 2.1 AA (4.5:1 normal text, 3:1 large text/UI). The combination Yellow 500 over White (1.61:1) is FORBIDDEN. Combinations in the 3:1–4.5:1 range are restricted to titles, buttons, and badges. Signal colors (Green #00BF63, Yellow #FFDE59, Red #FF3131, Blue #004AAD) are reserved for data viz and critical system states.**

## Coverage

- **Applies to:** UI (platform, site, app), commercial and institutional materials, decks, documents, emails, social media posts, icons, and illustrations.
- **Bound agents:** designers, frontend, mobile, marketing, support, AI agents that generate visual pieces or interfaces.
- **Exceptions:** partner logos and third-party brands (presented in their original color). Specific cases require an ADR or recorded exception in Notion.

## Consequences of Violation

1. **Identity:** off-palette color weakens recognition and breaks Brand Kit coherence.
2. **Accessibility:** sub-WCAG combinations block low-vision users and expose the brand to regulatory liability (LGPD, ADA, accessibility standards).
3. **Remediation:** swap to an approved tone; on saturated backgrounds (orange/pink), deepen to the 700 scale before applying white; on yellow, replace white with Violet 500 or Gray 500.

## Examples

### Correct

Black text over Yellow 500 (13.06:1, AAA); White over Gray 500 (11.24:1, AAA); Violet 500 button with White label (>7:1); Orange 500 badge with Violet 500 text reserved for buttons/titles (3.96:1, AA large); financial chart using Signal Green/Signal Red only on the data axis.

### Incorrect

White text over Yellow 500 (1.61:1, illegible); a "purple-ish" color invented to complement the brand; institutional green used as brand color in a hero; `#4F186D` used outside the tokenized palette (hardcoded next to non-approved colors).

## Automated Validation

- **Tooling:** Stylelint with palette plugin, axe-core and Lighthouse a11y in CI; automated visual review (warrior-hephaestus) flagging combinations below WCAG minimum; tokens centralized in `@guardia/design-system`.
- **Timing:** pre-commit, UI CI, design review for non-UI materials.
- **Metric:** 0 color values outside the palette on `main`; 100% of text/background combinations ≥ 4.5:1 (normal) and ≥ 3:1 (UI/large); 0 occurrences of the forbidden Yellow 500 + White combination.

## References

- [codex-brand-colors](../codex/codex-brand-colors.md)
- WCAG 2.1, AA and AAA
- Notion — Branding / Cores
