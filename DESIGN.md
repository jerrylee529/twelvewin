# Design System: Robinhood-Inspired Investing Web

## 1. North Star: "Build Your Market Strategy"

The UI should reference Robinhood's broader public web brand, not just a single stock detail page. The reference is a confident consumer investing site: oversized headlines, bold green brand areas, black text, rounded pill actions, clear product sections, and a calm but energetic path into market tools.

TwelveWin remains a data-heavy A-share research product, but the interface should feel more welcoming and productized. The first impression should say: "start researching, build your strategy, and track market signals" before the user drops into dense rankings and charts.

## 2. Design Principles

- **Brand-first sections:** Use large, memorable panels instead of small generic cards for primary landing content.
- **Green as a brand surface:** Green is not only a button color. It can be a full hero or feature background with black text.
- **Big type, short copy:** Robinhood's public pages use direct, compact messaging. Prefer short headlines over explanatory paragraphs.
- **Rounded product UI:** Use pill CTAs, large radii, and friendly spacing while keeping data tables precise.
- **Editorial section flow:** Alternate hero, tool introduction, market data, and legal/footer areas with clear spacing.
- **Business logic stays invisible:** UI changes must not alter routes, request payloads, table columns, chart APIs, or existing user flows.

## 3. Color Tokens

| Role | Token | Hex | Usage |
| --- | --- | --- | --- |
| Brand green | `--tw-primary` | `#00c805` | Primary actions, hero sections, active navigation |
| Brand green hover | `--tw-primary-hover` | `#00b806` | Hover/active state for primary actions |
| Ink | `--tw-ink` | `#000000` | Robinhood-style hero text and strong headlines |
| Text strong | `--tw-text` | `#111827` | Content headings, prices, core labels |
| Text muted | `--tw-muted` | `#6b7280` | Secondary copy, timestamps, helper text |
| Page background | `--tw-bg` | `#ffffff` | Main page background |
| Cream panel | `--tw-cream` | `#f7f3ea` | Warm homepage sections and feature panels |
| Card background | `--tw-surface` | `#ffffff` | Tables, cards, modals, form areas |
| Soft surface | `--tw-surface-soft` | `#f1f3f5` | Hover rows, nested blocks |
| Border | `--tw-border` | `#e5e7eb` | Subtle separation only |
| Up / China market | `--tw-up` | `#d93025` | Rising price in the current A-share convention |
| Down / China market | `--tw-down` | `#008a22` | Falling price in the current A-share convention |
| Focus ring | `--tw-focus` | `rgba(0, 200, 5, 0.25)` | Keyboard and input focus |

## 4. Typography

Use the system sans-serif stack by default, with Inter as the preferred web font when available.

- **Brand display:** `56px-72px`, `800`, tight letter spacing, line height near `1.0`.
- **Display price:** `40px-48px`, `700`, tight letter spacing, tabular numbers.
- **Page title:** `32px-44px`, `800`, line height `1.08`.
- **Section title:** `18px`, `700`.
- **Body:** `14px-16px`, line height `1.55`.
- **Table text:** `13px-14px`, tabular numbers for numeric columns.

All numeric data should use `font-variant-numeric: tabular-nums` to keep prices, ratios, and rankings stable while scanning.

## 5. Layout

- Public-facing entry sections can break out visually with large panels inside the centered container.
- Navigation remains persistent, white, and low-shadow, matching the light consumer finance tone.
- Hero sections use `32px-56px` padding, large radius, and strong brand color.
- Cards use `16px-24px` padding, `18px-24px` radius, and a soft border.
- Tables should look like data products, not Bootstrap defaults: sticky-like visual header, soft row hover, no heavy black borders.
- Mobile layout should stack cards and keep touch targets at least `44px` high.

## 6. Components

### Navigation

- White background, dark text, brand green active/hover state.
- Dropdown menus should feel like floating cards with rounded corners and soft shadows.
- Navigation should be clean and product-site-like, closer to Robinhood's "Log in / Sign up" simplicity than a dense admin menu.

### Buttons

- **Primary:** Green filled pill, dark text, strong hover state.
- **Dark CTA:** Black filled pill with white text on green or cream panels.
- **Secondary:** Light gray or cream pill with dark text.
- **Link button:** Green text, no underline unless hovered.
- Buttons should have visible focus rings and a minimum height of `38px`.

### Inputs

- Search and filter controls use rounded pill or rounded rectangle shapes.
- Focus state uses the brand green ring.
- Placeholder text stays muted, never low contrast.

### Tables

- Header background is soft slate.
- Rows are white with subtle hover.
- Borders are light and used only for structure.
- Pagination and toolbar buttons inherit the same pill button system.

### Market Cards

- Price cards should prioritize current price, daily change, open/high/low, volume, valuation ratios, and update time.
- Use red for rising and green for falling to preserve the existing A-share convention.
- Charts sit in white rounded panels with enough height reserved to prevent visual jumps.

### Brand Feature Cards

- Use short labels like "基本面排行", "技术信号", "行业板块", and "自选跟踪".
- Cards can sit on cream or white panels with minimal copy.
- Avoid heavy illustrations unless they are part of a coherent asset set.

### Modals

- Modal content uses rounded corners, clean header spacing, and a subtle shadow.
- The close button remains visible and keyboard accessible.

## 7. Motion & Interaction

- Use short transitions between `150ms` and `220ms`.
- Animate color, border, shadow, and transform only.
- Hover lift should be subtle: no more than `translateY(-1px)`.
- Respect `prefers-reduced-motion` by disabling transitions.

## 8. Accessibility

- Body text and table text must meet WCAG AA contrast.
- Focus rings must remain visible on links, buttons, inputs, and dropdown toggles.
- Color cannot be the only indicator for important states; labels such as "低估" should remain text-based.
- Do not remove Bootstrap's keyboard behavior for dropdowns, modals, or forms.

## 9. Do / Don't

### Do

- Use green and cream sections to create Robinhood-like brand rhythm.
- Use oversized headlines on entry pages.
- Keep financial numbers stable with tabular figures.
- Use brand green for product actions and positive affordances.
- Keep existing data shape and endpoint behavior unchanged.

### Don't

- Do not reintroduce the dark terminal palette for normal pages.
- Do not add decorative gradients that compete with stock charts.
- Do not make every surface a small white card; Robinhood's broader brand relies on large confident panels.
- Do not rely on red/green alone without labels when introducing new states.
- Do not change business routes, JavaScript request URLs, or table response handlers for visual work.