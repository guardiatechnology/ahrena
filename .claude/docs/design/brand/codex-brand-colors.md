# Codex: Guardia Color Palette

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Color at any Guardia touchpoint

## Content

### Base colors and meaning

| Color | HEX | Meaning |
|-------|-----|---------|
| Bright Yellow | `#FFC30A` | Trust and Transparency — optimism and clarity |
| Warm Orange | `#F47720` | Efficiency and Agility — energy and dynamism |
| Soft Pink | `#DB6286` | Welcoming and Inclusion — empathy, respect |
| Deep Violet | `#552973` | Depth and Excellence — safety, compliance |
| Baltic Gray | `#3A3A44` | Stability and Integrity — professionalism |

### Scales (100, 200, 500 base, 700, 900)

| Color | 100 | 200 | 500 (base) | 700 | 900 |
|-------|-----|-----|------------|-----|-----|
| Bright Yellow | `#FFF3CE` | `#FFE490` | `#FFC30A` | `#B28807` | `#664E04` |
| Warm Orange | `#FDE3D1` | `#FAC29B` | `#F47720` | `#AB5316` | `#612F0D` |
| Soft Pink | `#F7DFE6` | `#EEB8C8` | `#DB6286` | `#99445D` | `#572735` |
| Deep Violet | `#DCD3E2` | `#B29FC0` | `#552973` | `#3B1D50` | `#22102E` |
| Baltic Gray | `#D7D7D9` | `#A6A6AA` | `#3A3A44` | `#28282F` | `#17171B` |

### Mono tones (technical)

| Color | Use | HEX |
|-------|-----|-----|
| Mono White | Light backgrounds, surfaces, plot areas | `#FDFDFD` |
| Mono Black | Text ink, axes, baselines | `#0E1016` |

Technical function, outside the brand's chromatic palette.

### Signal colors (data viz and critical states)

| Color | Semantics | HEX |
|-------|-----------|-----|
| Signal Green | Positive, health, growth | `#00BF63` |
| Signal Yellow | Attention, pending, alert | `#FFDE59` |
| Signal Red | Negative, decline, critical exception | `#FF3131` |
| Signal Blue | Informational, baseline, reference | `#004AAD` |

Universal convention (green = positive, yellow = attention, red = negative, blue = informational). **They do not replace the main palette** — use outside charts, dashboards, and alerts requires justification.

### Approved WCAG combinations (any use)

| Background | Text | Contrast | WCAG |
|------------|------|----------|------|
| Yellow 500 (`#FFC30A`) | Black | 13.06:1 | AAA at any size |
| Gray 500 (`#3A3A44`) | White | 11.24:1 | AAA at any size |
| Violet 500 (`#552973`) | Pink 200 (`#EEB8C8`) | 6.32:1 | AA at any size |
| Pink 500 (`#DB6286`) | Black | 6.10:1 | AA at any size, AAA on large text |
| Gray 500 (`#3A3A44`) | Gray 200 (`#A6A6AA`) | 4.63:1 | AA on normal text (avoid in long bodies) |

### Restricted combinations (titles, buttons, badges)

Meet WCAG minimum only for large text (18pt regular or 14pt bold and up):

| Background | Text | Contrast |
|------------|------|----------|
| Orange 500 (`#F47720`) | Violet 500 (`#552973`) | 3.85:1 |
| Violet 500 (`#552973`) | Orange 500 (`#F47720`) | 3.85:1 |
| Pink 500 (`#DB6286`) | White | 3.44:1 |

### Forbidden combinations

| Background | Text | Contrast | Action |
|------------|------|----------|--------|
| Yellow 500 (`#FFC30A`) | White | 1.61:1 | Remove; illegible at any size |
| Orange 500 (`#F47720`) | White | 2.80:1 | Below the 3:1 floor; deepen to Orange 700 (`#AB5316`, 5.28:1) for text/UI on light |

### Adjustments to free up body text

- White text on saturated backgrounds (orange/pink): deepen to the 700 scale (Orange 700 + White = 5.28:1, AA; Pink 700 + White = 6.9:1, full AA).
- Light text on Yellow: replace white with Violet 500 (6.70:1) or Gray 500 (>8:1).
- For chromatic identity with light text on orange/pink: use Pink 100 or Yellow 100 instead of white.
