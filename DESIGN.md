# Design System: The Predictive Terminal (Dark)

## 1. North Star: "A Professional A-Share Research Terminal"

TwelveWin's web UI is a **dark, data-dense quantitative research terminal** for Chinese A-share investors. The reference points are professional market tools (TradingView dark, Bloomberg-style terminals, Binance) rather than consumer investing brands.

The first impression should say: precision, data density, and market awareness. Dark surfaces, one electric-blue brand accent, and the Chinese market convention of **red = up, green = down** everywhere.

Tokens live in [`web/app/globals.css`](web/app/globals.css). All components must consume tokens — no ad-hoc hex values in components.

## 2. Design Principles

- **Dark terminal first:** Deep-space blue surfaces (`#0b1326` family) on every page, including marketing/landing and blog.
- **One brand accent:** Electric blue (`--primary: #3b82f6`) for CTAs, active states, links, and focus. Purple (`--secondary`) is reserved exclusively for AI-related features (AI chips, AI research assistant identity).
- **China market color convention:** Red rises, green falls. Never invert. Color is never the only signal — keep text labels (e.g. "低估", "+0.24%").
- **Data density over whitespace:** Tables, KPI panes and charts should feel like a terminal: compact paddings (`--cell-padding-*`), 1px pane gaps, tabular numbers.
- **CJK-first typography:** Chinese labels are never uppercased or letter-spaced like English microcopy; minimum 12px for Chinese label text.
- **Business logic stays invisible:** UI changes must not alter routes, request payloads, table columns, chart APIs, or existing flows.

## 3. Color Tokens

| Role | Token | Value | Usage |
| --- | --- | --- | --- |
| Surface | `--surface` | `#0b1326` | Page background |
| Pane | `--surface-container` | `#171f33` | Tables, cards, panes |
| Recessed | `--surface-container-lowest` | `#060d20` | Inputs, table headers |
| Text | `--on-surface` | `#dbe2fd` | Primary text |
| Muted text | `--on-surface-variant` | `#b8c1dc` | Secondary copy, labels |
| Brand primary | `--primary` | `#3b82f6` | CTAs, active nav, focus, links |
| Primary strong | `--inverse-primary` | `#2563eb` | Filled CTA backgrounds |
| Primary accent text | `--primary-container` | `#8ab4ff` | Accent text/icons on dark, stock codes |
| CTA gradient | `--gradient-cyber` | `#2563eb → #38bdf8` | Primary gradient buttons |
| Up / rising | `--bullish` | `#f6465d` | Rising prices, gains (A-share red) |
| Up background | `--bullish-container` | `rgb(246 70 93 / 0.14)` | Up chips, flash backgrounds |
| Down / falling | `--bearish` | `#0ecb81` | Falling prices, losses (A-share green) |
| Down background | `--bearish-container` | `rgb(14 203 129 / 0.14)` | Down chips, flash backgrounds |
| AI accent | `--secondary` | `#ebb2ff` | AI features only (chips, AI assistant) |
| Error | `--error` / `--error-container` | `#ffb4ab` / `#93000a` | Errors only — never for market up/down |

Charts (`lightweight-charts`, ECharts) cannot read CSS variables in all options; chart constants must stay in sync with `--bullish` / `--bearish` (see comments in `candlestick-chart.tsx`, `stock-line-chart.tsx`).

## 4. Typography

System sans stack with CJK fonts listed **before** the generic `sans-serif` fallback (PingFang SC / Microsoft YaHei / Source Han Sans).

- **Body:** 14px, line-height 1.5.
- **Display:** `.display-lg` 48px / `.display-sm` 32px, 700, tight tracking.
- **Headline:** `.headline-md` 18px / 600.
- **Labels (CJK-safe):** `.title-sm`, `.label-md`, `.label-sm`, `.label-zh` — all ≥12px, no `text-transform: uppercase`, letter-spacing ≤0.04em. Uppercase + wide tracking is allowed only for genuinely English microcopy (e.g. "AI Research").
- **Numbers:** always `font-variant-numeric: tabular-nums` (`.tabular-nums` / `.data-num`); mono (`--font-mono`) for code-like data.

## 5. Layout

- Max container `--container-max-width: 1920px`; dashboard = top header (48px) + 224px left sidebar + scrollable main.
- Panes separated by `--terminal-gap: 1px` instead of borders, on recessed background.
- Table cells: `--cell-padding-x: 8px`, `--cell-padding-y: 4px`; zebra rows with `surface-container` / `surface-container-low`, hover `surface-container-high`.
- Radii are intentionally small: `--radius-sm: 2px`; pills only for search/quick-link chips.
- Mobile: stack panes, keep touch targets ≥44px.

## 6. Components

### Navigation
- Dark translucent header (`.nav-header`) with blur; active link gets `--nav-accent` (= `--primary`) 2px underline.
- CTA button `.nav-menu-cta`: filled `--inverse-primary`, hover `--primary`, white text.
- Landing and dashboard headers share the same dark terminal style.

### Buttons
- **Primary:** `.btn-gradient-primary` blue gradient, white text.
- **Container:** `.btn-primary-container` light-blue fill (`--primary-container`), navy text.
- **Secondary/ghost/outline:** surface-container fills or `ghost-outline` inset ring.
- Visible focus states required; min height 38px.

### Tables
- Header row on `surface-container-lowest`, muted 12px text.
- Numeric columns right-aligned conceptually, tabular nums, red/green tone for signed values.
- Large CNY values must be humanized (`万` / `亿` / `万亿`) — never raw 8-digit numbers.

### Market data
- Price up: `--bullish` red; down: `--bearish` green; flat: `--on-surface-variant`.
- Up/down chips use `bullish-container` / `bearish-container` backgrounds.
- Charts sit on `surface-container` panes with reserved height to avoid layout shift.

### AI features
- AI chips/labels use `--secondary` purple — this is the *only* place purple appears.

## 7. Motion & Interaction

- Transitions 150–220ms; animate color/border/shadow/transform only.
- Price-change flash: background pulse with `bullish-container` / `bearish-container` ~200ms.
- Respect `prefers-reduced-motion`.

## 8. Accessibility

- Body and table text meet WCAG AA on their actual surfaces (check dark contrast separately).
- Focus rings visible on links, buttons, inputs.
- Color never the sole indicator: keep text labels alongside red/green.

## 9. Do / Don't

### Do
- Keep the dark terminal palette on all pages, including landing and blog.
- Use one blue accent for everything interactive; purple only for AI.
- Use red-up/green-down consistently, sourced from tokens.
- Humanize large numbers with Chinese units (亿 / 万亿).
- Keep existing data shapes and endpoint behavior unchanged.

### Don't
- Don't introduce light-theme pages without a deliberate, separate decision.
- Don't add purple/pink "AI" gradients to product surfaces.
- Don't hardcode hex colors in components — extend tokens instead.
- Don't uppercase or letter-space Chinese text; don't set Chinese labels below 12px.
- Don't change business routes, request URLs, or response handlers for visual work.
