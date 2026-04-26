# Codex: Guardia Typography — Poppins, Lastica, and Roboto

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Typography in everyday communication, logos, and digital systems

## Content

### Poppins (everyday)

Modern geometric sans-serif from the Indian Type Foundry, distributed under SIL Open Font License (Google Fonts).

- **Structure:** geometric with smooth curves and consistent stroke.
- **Weights:** 9 (Thin 100 → Black 900) with italics.
- **Support:** Latin, Latin Extended, Devanagari.
- **Why Poppins:** visual coherence with Lastica (geometry), versatility for hierarchies, free distribution via Google Fonts (no license barriers).

### Recommended typographic hierarchy

| Element | Weight | Note |
|---------|--------|------|
| Main title (H1) | Bold (700) or SemiBold (600) | First reading hierarchy |
| Secondary title (H2) | SemiBold (600) | Sections within the document |
| Subtitle (H3/H4) | Medium (500) | Subdivisions and highlights |
| Body | Regular (400) | Standard running text |
| Support text | Light (300) | Captions, footnotes, metadata |
| Emphasis | Italic or SemiBold (600) | Pinpoint highlights |

### Where to use Poppins

Internal documents (memos, reports, policies, minutes); commercial and institutional presentations; proposals, contracts, and client materials; formal emails and signatures; digital interfaces and product materials; social media and blog posts; marketing and event materials.

### Lastica (exclusive to logos)

Geometric sans-serif by Alberto Fontense, chosen for the Guardia logo construction. Reserved for:

- Building the Guardia logos
- Official brand signature
- Applications where the brand appears as a seal or endorsement

Use exclusively the official logo files. DO NOT use in body text, editorial titles, or non-logo pieces.

### Roboto (fallback)

Sans-serif designed by Christian Robertson for Google, distributed under Apache License 2.0. Default typeface of Android and Google Workspace, present natively on virtually any device.

**When to use Roboto:**

- Systems or platforms restricted from importing external fonts
- Corporate environments restricting font installation
- Emails where the client renders only native fonts
- Documents shared with third parties using native fonts
- CSS fallback when Poppins fails to load

Roboto's hierarchy follows the same weight pattern as Poppins (direct substitution).

### CSS declaration

```css
font-family: 'Poppins', 'Roboto', sans-serif;
```

Ensures Poppins priority and automatic Roboto fallback.

### Installation

Poppins available at [Google Fonts](https://fonts.google.com/specimen/Poppins):

- **macOS:** `.ttf` opened in Font Book.
- **Windows:** `.ttf` installed via Settings → Fonts.
- **Google Workspace:** available natively in Docs, Slides, Sheets.
- **Microsoft 365:** install on the OS for use in Word, PowerPoint, Excel.
- **Web:** import via `<link>` or `@import` from Google Fonts.
- **Figma and Canva:** available natively.
