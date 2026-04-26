# Lexis: Correct Use of the Guardia Logo

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Guardia logo, symbol, and standalone mark in any application

## Purpose

Preserve legibility and recognition. The primary logo (violet square with orange G + Lastica) has versions for each chromatic context. Applying the wrong version (e.g., primary on a violet background) makes the symbol blend into the background and breaks identity.

## Law

> **Every application of the Guardia logo MUST use ONLY the official files and MUST select the correct variant based on the background: (1) **Primary logo** (violet symbol + orange G) on light backgrounds and dark backgrounds outside the violet spectrum; (2) **Secondary logo** (orange symbol + violet G) on backgrounds within the violet spectrum; (3) **Monochrome black** on light backgrounds when color is unavailable; (4) **Monochrome white** on dark backgrounds when color is unavailable; (5) **Standalone mark** (without the "Guardia" wordmark) only in reduced applications (favicon, avatar, compact signature) or where the brand is already established in context. Recoloring, distorting, rotating, applying outlines, shadows, gradients, or effects; replacing Lastica with another font; reducing the logo below the documented minimum size; or applying the wrong version for the background (e.g., primary on violet) is FORBIDDEN.**

## Coverage

- **Applies to:** UI (favicons, headers, login screen), emails, decks, proposals, contracts, social media, events, swag, videos, partnerships.
- **Bound agents:** designers, marketing, sales, frontend/mobile (favicon, headers), AI agents that produce branded pieces.
- **Exceptions:** clearly marked internal parodies (off-brand), seasonal celebrations approved by Brand. Every public exception requires CEO or designated Brand owner approval.

## Consequences of Violation

1. **Identity:** distorted or recolored logo weakens recognition and creates a sense of carelessness.
2. **Legibility:** wrong version for the background makes the symbol invisible.
3. **Remediation:** swap to the corresponding official file; restore original dimensions; remove applied effects; review the variant-by-background checklist before republishing.

## Examples

### Correct

Site on white background using the primary logo; login screen with Violet 500 background using the secondary logo; B&W contract using monochrome black on white page; favicon using the violet standalone mark; banner over Deep Violet using the orange transparent mark; email signature with primary logo exported from official files.

### Incorrect

Primary logo on a Violet 500 background (violet symbol blends into the background); logo recolored green to "match the post theme"; logo with shadow "to stand out"; word "Guardia" typed in Helvetica simulating the logo; logo below 16px height in UI; logo distorted to 16:9 to fill a banner.

## Automated Validation

- **Tooling:** automated review (warrior-hephaestus + human Brand reviewer) detecting non-official logos or applications on conflicting backgrounds; `@guardia/design-system` library exposing a single `<Logo variant="..." />` component that always picks the correct variant.
- **Timing:** UI PR review; Brand review for commercial and institutional pieces; quarterly external assets audit.
- **Metric:** 0 recolored/distorted logos in published pieces; 100% of in-product applications consuming `<Logo />` from the library; 0 applications of the primary version on backgrounds within the violet spectrum.

## References

- [codex-brand-logo](../codex/codex-brand-logo.md)
- Notion — Branding / Logomarca e Logotipos
