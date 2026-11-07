---
name: rtl-check
description: Scan the codebase for directional CSS properties that are missing RTL handling. Reports violations grouped by file with suggested fixes using logical properties or theme.dir conditionals.
---

Scan this codebase for CSS styles that use hardcoded directional properties without proper RTL support.

## What to scan

Search all style files: `*.styles.ts`, `styles.ts`, `*.styles.tsx`, and styled-component definitions inside `.tsx` files.

## Properties that require RTL handling

Flag any use of these CSS properties **unless** they are already inside an RTL-aware block:
- `padding-left`, `padding-right`
- `margin-left`, `margin-right`
- `border-left`, `border-right`
- `left:`, `right:` (in `position` context)
- `float: left`, `float: right`
- `text-align: left`, `text-align: right`

## What counts as proper RTL handling (do NOT flag these)

- The property is inside a `theme.dir === "rtl"` conditional (ternary or if-block)
- The property is inside a `[dir="rtl"] &` CSS selector block
- A logical property equivalent is used instead:
  - `padding-inline-start/end` instead of `padding-left/right`
  - `margin-inline-start/end` instead of `margin-left/right`
  - `border-inline-start/end` instead of `border-left/right`
  - `inset-inline-start/end` instead of `left/right`
  - `text-align: start/end` instead of `left/right`

## Do NOT flag

- `flex-direction: column/row` — not direction-dependent
- `top`, `bottom` — vertical axis, not affected by RTL
- `margin-left: auto` used purely for alignment in flex contexts — flag it but note it as low severity since `margin-inline-start: auto` is the logical equivalent
- Properties already inside an RTL-aware block

## Output format

Group findings by file. For each violation, show:
1. File path and line number
2. The offending property
3. Severity: **high** (visible layout shift in RTL), **medium** (positional), **low** (cosmetic)
4. Suggested fix — prefer logical properties; fall back to the `theme.dir === "rtl"` conditional pattern already used in this project

At the end, print a summary: total violations found, files affected, and a prioritized list of what to fix first.

## Reference patterns from this codebase

**Correct — use `theme.dir` conditional:**
```ts
${({ theme }) => theme.dir === "rtl" ? css`right: 0;` : css`left: 0;`}
```

**Correct — use logical property:**
```css
inset-inline-start: 0;
margin-inline-start: 4px;
padding-inline-start: 16px;
```

**Correct — use `[dir="rtl"]` selector:**
```css
[dir="rtl"] & {
  border-radius: 2px 0 0 2px;
}
```
