# Apple HIG Design Tokens

These are the canonical iOS values. Drop them into the HTML as CSS variables and the tokens panel.

## CSS variables (paste into `:root`)

```css
:root {
  /* ===== Colors — semantic, Light Mode ===== */
  --color-label: #000000;
  --color-label-secondary: rgba(60, 60, 67, 0.6);
  --color-label-tertiary: rgba(60, 60, 67, 0.3);
  --color-label-quaternary: rgba(60, 60, 67, 0.18);

  --color-fill: rgba(120, 120, 128, 0.2);
  --color-fill-secondary: rgba(120, 120, 128, 0.16);
  --color-fill-tertiary: rgba(118, 118, 128, 0.12);
  --color-fill-quaternary: rgba(116, 116, 128, 0.08);

  --color-bg: #FFFFFF;
  --color-bg-secondary: #F2F2F7;
  --color-bg-tertiary: #FFFFFF;

  --color-bg-grouped: #F2F2F7;
  --color-bg-grouped-secondary: #FFFFFF;
  --color-bg-grouped-tertiary: #F2F2F7;

  --color-separator: rgba(60, 60, 67, 0.29);
  --color-separator-opaque: #C6C6C8;

  /* ===== System colors (default Light values) ===== */
  --color-system-blue:   #007AFF;  /* default tint */
  --color-system-green:  #34C759;
  --color-system-indigo: #5856D6;
  --color-system-orange: #FF9500;
  --color-system-pink:   #FF2D55;
  --color-system-purple: #AF52DE;
  --color-system-red:    #FF3B30;
  --color-system-teal:   #30B0C7;
  --color-system-yellow: #FFCC00;

  --color-system-gray:   #8E8E93;
  --color-system-gray-2: #AEAEB2;
  --color-system-gray-3: #C7C7CC;
  --color-system-gray-4: #D1D1D6;
  --color-system-gray-5: #E5E5EA;
  --color-system-gray-6: #F2F2F7;

  /* App tint — override with brand color from spec if present */
  --color-tint: var(--color-system-blue);

  /* ===== Typography ===== */
  /* size / line-height / weight */
  --font-large-title:     34px / 41px / 700;
  --font-title-1:         28px / 34px / 700;
  --font-title-2:         22px / 28px / 700;
  --font-title-3:         20px / 25px / 600;
  --font-headline:        17px / 22px / 600;
  --font-body:            17px / 22px / 400;
  --font-body-emphasized: 17px / 22px / 600;
  --font-callout:         16px / 21px / 400;
  --font-subheadline:     15px / 20px / 400;
  --font-footnote:        13px / 18px / 400;
  --font-caption-1:       12px / 16px / 400;
  --font-caption-2:       11px / 13px / 400;

  /* ===== Spacing ===== */
  --space-xxs: 4px;
  --space-xs:  8px;
  --space-sm:  12px;
  --space-md:  16px;   /* the default iOS layout margin */
  --space-lg:  20px;
  --space-xl:  24px;
  --space-2xl: 32px;
  --space-3xl: 44px;   /* minimum touch target */
  --space-4xl: 64px;

  /* ===== Radius ===== */
  --radius-xs: 4px;
  --radius-sm: 8px;
  --radius-md: 10px;   /* default button/control */
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-2xl: 22px;
  --radius-card: 16px;
  --radius-modal: 10px;
  --radius-phone: 47.33px;

  /* ===== Shadows / elevation ===== */
  --shadow-1: 0 1px 3px rgba(0,0,0,0.08);
  --shadow-2: 0 4px 12px rgba(0,0,0,0.10);
  --shadow-3: 0 12px 32px rgba(0,0,0,0.15);

  /* ===== Standard heights ===== */
  --height-navbar: 44px;
  --height-tabbar: 49px;
  --height-row: 44px;
  --height-row-large: 60px;
  --height-button: 50px;
  --height-button-small: 32px;
  --height-textfield: 36px;
  --height-search: 36px;
}
```

## Typography samples (paste into tokens panel)

```html
<section>
  <h3>Typography</h3>
  <div class="type-sample" style="font-size:34px;line-height:41px;font-weight:700">Large Title — 34/41 Bold</div>
  <div class="type-sample" style="font-size:28px;line-height:34px;font-weight:700">Title 1 — 28/34 Bold</div>
  <div class="type-sample" style="font-size:22px;line-height:28px;font-weight:700">Title 2 — 22/28 Bold</div>
  <div class="type-sample" style="font-size:20px;line-height:25px;font-weight:600">Title 3 — 20/25 Semibold</div>
  <div class="type-sample" style="font-size:17px;line-height:22px;font-weight:600">Headline — 17/22 Semibold</div>
  <div class="type-sample" style="font-size:17px;line-height:22px;font-weight:400">Body — 17/22 Regular</div>
  <div class="type-sample" style="font-size:16px;line-height:21px;font-weight:400">Callout — 16/21 Regular</div>
  <div class="type-sample" style="font-size:15px;line-height:20px;font-weight:400">Subheadline — 15/20 Regular</div>
  <div class="type-sample" style="font-size:13px;line-height:18px;font-weight:400">Footnote — 13/18 Regular</div>
  <div class="type-sample" style="font-size:12px;line-height:16px;font-weight:400">Caption 1 — 12/16 Regular</div>
  <div class="type-sample" style="font-size:11px;line-height:13px;font-weight:400">Caption 2 — 11/13 Regular</div>
</section>
```

## Button variants

```html
<!-- Primary (filled) -->
<button style="
  height: 50px;
  padding: 0 20px;
  background: var(--color-tint);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 17px;
  font-weight: 600;
">Primary</button>

<!-- Secondary (tinted) -->
<button style="
  height: 50px;
  padding: 0 20px;
  background: rgba(0,122,255,0.15);
  color: var(--color-tint);
  border: none;
  border-radius: 12px;
  font-size: 17px;
  font-weight: 600;
">Secondary</button>

<!-- Plain / tertiary -->
<button style="
  height: 50px;
  padding: 0 20px;
  background: transparent;
  color: var(--color-tint);
  border: none;
  font-size: 17px;
  font-weight: 600;
">Plain</button>

<!-- Destructive -->
<button style="
  height: 50px;
  padding: 0 20px;
  background: var(--color-system-red);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 17px;
  font-weight: 600;
">Delete</button>
```

## NavBar

```html
<!-- Large title style -->
<div style="
  padding: 8px 16px 16px;
  background: var(--color-bg);
">
  <div style="font-size: 34px; font-weight: 700;">Title</div>
</div>

<!-- Inline title style -->
<div style="
  height: 44px;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  padding: 0 16px;
  background: var(--color-bg);
  border-bottom: 0.5px solid var(--color-separator);
">
  <span style="color: var(--color-tint); font-size: 17px;">‹ Back</span>
  <span style="font-size: 17px; font-weight: 600;">Title</span>
  <span style="text-align: right; color: var(--color-tint); font-size: 17px;">Edit</span>
</div>
```

## TabBar

```html
<div style="
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 83px;            /* 49pt + 34pt home indicator safe area */
  padding-bottom: 34px;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(20px);
  border-top: 0.5px solid var(--color-separator);
  display: flex;
">
  <div class="tab-item active">...</div>
  <div class="tab-item">...</div>
</div>

<style>
.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding-top: 6px;
  color: var(--color-system-gray);
  font-size: 10px;
}
.tab-item.active { color: var(--color-tint); }
.tab-item svg { width: 25px; height: 25px; margin-bottom: 3px; }
</style>
```

## List row (grouped style)

```html
<div style="
  background: var(--color-bg);
  border-radius: 10px;
  overflow: hidden;
  margin: 0 16px;
">
  <div style="
    min-height: 44px;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 0.5px solid var(--color-separator);
  ">
    <span style="font-size: 17px;">Setting label</span>
    <span style="color: var(--color-label-secondary); font-size: 17px;">Value ›</span>
  </div>
  <!-- repeat rows; last row omits border-bottom -->
</div>
```

## TextField

```html
<!-- Default -->
<div style="
  height: 36px;
  padding: 0 12px;
  background: var(--color-fill-tertiary);
  border-radius: 10px;
  display: flex;
  align-items: center;
  font-size: 17px;
  color: var(--color-label-secondary);
">Placeholder</div>

<!-- Focused -->
<div style="
  height: 36px;
  padding: 0 12px;
  background: var(--color-bg);
  border: 2px solid var(--color-tint);
  border-radius: 10px;
  display: flex;
  align-items: center;
  font-size: 17px;
">User input│</div>

<!-- Error -->
<div style="
  height: 36px;
  padding: 0 12px;
  background: var(--color-bg);
  border: 2px solid var(--color-system-red);
  border-radius: 10px;
  display: flex;
  align-items: center;
  font-size: 17px;
">Invalid email</div>
```

## SwiftUI name reference

When labeling colors in the tokens panel, use these SwiftUI names so iOS engineers can map directly:

| Hex / value | SwiftUI |
|---|---|
| `#007AFF` (default tint) | `Color.accentColor` / `Color.blue` |
| `#FF3B30` | `Color.red` |
| `#34C759` | `Color.green` |
| `#FF9500` | `Color.orange` |
| `#FFCC00` | `Color.yellow` |
| `#AF52DE` | `Color.purple` |
| `#FF2D55` | `Color.pink` |
| `#8E8E93` | `Color.gray` |
| Label primary | `Color.primary` / `Color(.label)` |
| Label secondary | `Color.secondary` / `Color(.secondaryLabel)` |
| systemBackground | `Color(.systemBackground)` |
| systemGroupedBackground | `Color(.systemGroupedBackground)` |
| separator | `Color(.separator)` |

For typography:

| Token | SwiftUI |
|---|---|
| Large Title | `.largeTitle` |
| Title 1 | `.title` |
| Title 2 | `.title2` |
| Title 3 | `.title3` |
| Headline | `.headline` |
| Body | `.body` |
| Callout | `.callout` |
| Subheadline | `.subheadline` |
| Footnote | `.footnote` |
| Caption 1 | `.caption` |
| Caption 2 | `.caption2` |

## Dark Mode (only if requested)

If the spec calls for Dark Mode, swap these in a second `:root[data-theme="dark"]` block:

```
--color-label: #FFFFFF;
--color-label-secondary: rgba(235,235,245,0.6);
--color-bg: #000000;
--color-bg-secondary: #1C1C1E;
--color-bg-grouped: #000000;
--color-bg-grouped-secondary: #1C1C1E;
--color-separator: rgba(84,84,88,0.65);
--color-system-blue: #0A84FF;
--color-system-red:  #FF453A;
--color-system-green:#30D158;
--color-system-orange:#FF9F0A;
```
