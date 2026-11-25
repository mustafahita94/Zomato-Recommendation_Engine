---
name: "Discover — Late-Night Bangalore Dining"
description: "Warm, calm, dark-theme design system for Discover, an AI restaurant recommender for Bangalore."
---

## Overview

Discover is a late-night food discovery companion for Bangalore—warm, calm, and trustworthy, never a noisy marketplace or a neon-soaked dashboard. The interface pairs deep charcoal-navy canvases with subtle rose and soft amber warmth, keeping attention on a single focused flow: set preferences, submit, and read ranked picks with clear AI explanations.

## Colors

The palette is anchored in deep charcoal-navy surfaces (`#0B0F14` to `#0D1219`) with elevated slate panels (`#151B24` and `#1A222E`) and crisp, low-glare typography (`#E8EEF7` primary, `#9AA8BC` muted). Rose-coral (`#FB7185`) drives primary actions and rank badges, soft amber (`#FDBA74`) highlights star ratings and fallback notices, and success green (`#4ADE80`) indicates live Groq connectivity.

- **Primary (Rose-Coral):** Reserved for the primary CTA gradient (`#FB7185` to `#C94B60`) and `#1`–`#5` rank badges.
- **Secondary (Soft Amber):** Used for star ratings (`★ 4.5`), subtle hero/background radial washes, and non-fatal fallback notices.
- **Success (Connected Green):** Strictly semantic—used only for the Groq connected status dot and healthy catalog indicators.
- **Error (Crimson):** Reserved for missing-catalog or load-failure recovery states.

```yaml
colors:
  primary: "#FB7185"
  on-primary: "#400010"
  primary-deep: "#C94B60"
  primary-container: "#400010"
  on-primary-container: "#FFDADC"
  secondary: "#FDBA74"
  on-secondary: "#2C1600"
  secondary-container: "#492900"
  on-secondary-container: "#FFDCBD"
  success: "#4ADE80"
  on-success: "#00210C"
  success-container: "#003919"
  on-success-container: "#C4FFCD"
  error: "#FF897D"
  on-error: "#410002"
  error-container: "#690005"
  on-error-container: "#FFDAD6"
  surface-base: "#0B0F14"
  surface-canvas: "#0D1219"
  surface: "#151B24"
  surface-elevated: "#1A222E"
  surface-input: "#0F151E"
  on-surface: "#E8EEF7"
  on-surface-muted: "#9AA8BC"
  outline: "#2B3442"
  outline-strong: "#3A4658"
```

## Typography

**Sora** leads display and section headings with tight, geometric confidence, while **Outfit** carries all UI controls, labels, and AI explanation paragraphs with open, calm legibility. **Space Mono** is reserved for tabular metrics such as latency, candidate counts, and catalog totals.

```yaml
typography:
  display-lg:
    fontFamily: "Sora"
    fontSize: 44px
    fontWeight: 600
    lineHeight: 50px
    letterSpacing: -0.9px
  display-lg-mobile:
    fontFamily: "Sora"
    fontSize: 30px
    fontWeight: 600
    lineHeight: 36px
    letterSpacing: -0.6px
  headline-lg:
    fontFamily: "Sora"
    fontSize: 24px
    fontWeight: 600
    lineHeight: 32px
    letterSpacing: -0.4px
  headline-md:
    fontFamily: "Sora"
    fontSize: 20px
    fontWeight: 600
    lineHeight: 28px
    letterSpacing: -0.25px
  title-md:
    fontFamily: "Outfit"
    fontSize: 17px
    fontWeight: 600
    lineHeight: 24px
    letterSpacing: -0.1px
  body-lg:
    fontFamily: "Outfit"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 25px
    letterSpacing: 0px
  body-md:
    fontFamily: "Outfit"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 22px
    letterSpacing: 0px
  label-lg:
    fontFamily: "Outfit"
    fontSize: 14px
    fontWeight: 600
    lineHeight: 20px
    letterSpacing: 0.1px
  label-sm:
    fontFamily: "Outfit"
    fontSize: 12px
    fontWeight: 500
    lineHeight: 16px
    letterSpacing: 0.3px
  mono-sm:
    fontFamily: "Space Mono"
    fontSize: 12px
    fontWeight: 400
    lineHeight: 18px
    letterSpacing: 0px
```

## Layout & Spacing

Desktop-first wide layout (`max-width: 1120px`, sitting comfortably in the `1080–1200px` target) with generous vertical breathing room and a clean 8px base rhythm. On mobile (`390px`), multi-column preference grids collapse into a single vertical stack with 16px outer gutters.

```yaml
spacing:
  gutter-xs: 4px
  gutter-sm: 8px
  gutter-md: 16px
  gutter-lg: 24px
  gutter-xl: 32px
  section: 48px
  page-margin: 24px
```

## Elevation & Depth

Hierarchy relies on tonal surface stepping (`surface-base` → `surface` → `surface-elevated`) paired with subtle hairline borders (`rgba(232, 238, 247, 0.12–0.18)`) rather than heavy drop shadows or multi-layer glassmorphism. Subtle radial ambient washes of rose and soft amber sit behind the hero without glow spam.

## Shapes

Generous, calm rounding (`16px`–`20px`) softens panels, recommendation cards, and dashed empty/error containers, while form controls use `12px` and rank/status pills use full pill radii.

```yaml
rounded:
  sm: 8px
  DEFAULT: 12px
  md: 16px
  lg: 20px
  full: 9999px
```

## Motion & Micro-interaction

Transitions are understated and immediate: interactive controls respond in `120ms`, and recommendation cards settle smoothly without looping animations or decorative motion.

```yaml
motion:
  state-change:
    duration: 120ms
    delay: 0ms
    timingFunction: ease-out
  surface-enter:
    duration: 220ms
    delay: 0ms
    timingFunction: cubic-bezier(0.2, 0, 0, 1)
```

## Voice & Content Strategy

Direct, warm, and appetizing without hype or buzzwords. Headings and labels use sentence case; action buttons name the outcome (`Get recommendations`, `Reset filters`). Explanations stay concise (1–2 sentences) and explain *why* a Bangalore spot fits the user's budget, neighborhood, and mood. No emoji decoration anywhere in the UI.

## Components

Component implementations live as individual HTML sticker sheet files in
`components/`. Each file contains the canonical, styled HTML components with
`<!-- COMPONENT: name -->` comment markers. Read each file before use.

- **Badge** → `@components/badge.html` — `badge-numeric`, `badge-dot`
- **Banner** → `@components/banner.html` — `banner-info`, `banner-with-action`, `banner-dismissible`
- **Button** → `@components/button.html` — `button-primary`, `button-icon`, `button-with-icon`
- **Card** → `@components/card.html` — `card-elevated`, `card-action`, `card-interactive`, `card-interactive-2`
- **Input Field** → `@components/input-field.html` — `input-field-text`, `input-field-icon`
- **Select** → `@components/select.html` — `select-native`, `select-custom`
- **Slider** → `@components/slider.html` — `slider-continuous`, `slider-discrete`, `slider-range`
