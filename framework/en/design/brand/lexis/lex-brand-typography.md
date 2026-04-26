# Lexis: Official Typography — Poppins, Lastica, and Roboto

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Guardia typographic communication on any channel

## Purpose

Sustain typographic coherence. Lastica is proprietary to the brand signature; Poppins is the everyday typeface; Roboto is the native fallback for environments restricted to system fonts. Mixing fonts ad hoc, or using Lastica in body copy, dilutes identity and breaks hierarchy.

## Law

> **Guardia MUST use Poppins as the everyday typeface in all communication (documents, decks, proposals, internal materials, web, app, social media), with a standardized hierarchy (H1 Bold/SemiBold, H2 SemiBold, H3/H4 Medium, body Regular, support Light, emphasis Italic or SemiBold). Lastica is EXCLUSIVE to the official logos and brand signature — using it in body text, editorial titles, or any non-logo piece is FORBIDDEN. Roboto is the ONLY accepted fallback when Poppins is unavailable, declared in CSS as `font-family: 'Poppins', 'Roboto', sans-serif;`. Other fonts (Inter, Montserrat, Helvetica, Arial, Lato, Open Sans, etc.) are FORBIDDEN unless documented in an ADR.**

## Coverage

- **Applies to:** UI (web, mobile, email), decks, documents, proposals, contracts, social media posts, blog, events, icons with text.
- **Bound agents:** designers, frontend, mobile, marketing, sales, AI agents that generate text-bearing pieces.
- **Exceptions:** technical use of monospaced typefaces in code snippets (free choice among popular mono fonts: JetBrains Mono, Fira Code, Menlo); partner logos (keep their original typography).

## Consequences of Violation

1. **Identity:** font mixing erodes recognition and the brand's sense of care.
2. **Hierarchy:** lack of standardized hierarchy weakens reading in dense decks, dashboards, and materials.
3. **Remediation:** replace with Poppins (or Roboto in fallback); reserve Lastica for the official logo files; refactor typographic tokens in `@guardia/design-system` when the violation occurs in code.

## Examples

### Correct

Slide with H1 Poppins Bold 700, body in Poppins Regular 400, quote in Poppins Italic; landing page with `font-family: 'Poppins', 'Roboto', sans-serif`; email signature in Poppins (text) + official logo file in Lastica (image); contract in Poppins with Medium 500 hierarchy for subtitles.

### Incorrect

Body block in Lastica (font is exclusive to the logo); title in Inter or Montserrat because "it looked nice"; commercial deck mixing Helvetica and Roboto; CSS without explicit fallback (`font-family: 'Poppins', sans-serif`).

## Automated Validation

- **Tooling:** Stylelint rule `font-family-no-missing-generic-family-keyword` + allow-list (Poppins, Roboto + monospace); design review (warrior-hephaestus) detecting Lastica use outside official files; typographic tokens centralized in `@guardia/design-system`.
- **Timing:** pre-commit, UI CI, PR review for non-UI materials.
- **Metric:** 0 `font-family` declarations with fonts outside the allow-list; 0 occurrences of Lastica in body text; 100% of CSS declarations with `'Poppins', 'Roboto', sans-serif` fallback.

## References

- [codex-brand-typography](../codex/codex-brand-typography.md)
- Poppins (Google Fonts, SIL OFL); Roboto (Apache 2.0); Lastica (proprietary, Alberto Fontense)
- Notion — Branding / Tipografia
