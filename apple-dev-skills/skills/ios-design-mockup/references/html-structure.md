# HTML Structure & Layout Reference

This file gives you the skeleton, CSS variables, and the SVG arrow technique. Copy and adapt — don't reinvent.

## Top-level structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>[App Name] — Design Mockup</title>
<style>
  /* Tokens go in :root, see design-tokens.md */
  :root { ... }

  body {
    margin: 0;
    background: #f5f5f7;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", system-ui, sans-serif;
    color: #1d1d1f;
  }

  .canvas {
    position: relative;       /* anchor for the arrows SVG */
    min-width: max-content;   /* allow horizontal scroll */
    padding: 40px;
  }

  .arrows-layer {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;     /* don't block scroll/select */
    z-index: 10;
  }
</style>
</head>
<body>
  <header class="header">...</header>
  <main class="canvas">
    <section class="flows">
      <!-- screen frames grouped by flow -->
    </section>
    <svg class="arrows-layer" xmlns="http://www.w3.org/2000/svg">
      <!-- arrow paths -->
    </svg>
  </main>
  <aside class="tokens-panel">...</aside>
</body>
</html>
```

## iPhone frame component

Each screen frame is a `.phone` element. Give it an `id` so arrows can reference it.

```html
<div class="phone" id="S03-login">
  <div class="phone-shell">
    <div class="dynamic-island"></div>
    <div class="status-bar">
      <span class="time">9:41</span>
      <span class="status-icons">
        <!-- inline SVG: signal, wifi, battery -->
      </span>
    </div>
    <div class="screen-content">
      <!-- the actual screen design -->
    </div>
    <div class="home-indicator"></div>
  </div>
  <div class="phone-label">S03 — Login</div>
</div>
```

```css
.phone {
  width: 393px;
  flex-shrink: 0;
}

.phone-shell {
  position: relative;
  width: 393px;
  height: 852px;
  background: white;
  border-radius: 47.33px;
  box-shadow:
    0 0 0 4px #1d1d1f,
    0 30px 60px rgba(0,0,0,0.15);
  overflow: hidden;
}

.dynamic-island {
  position: absolute;
  top: 11px;
  left: 50%;
  transform: translateX(-50%);
  width: 125px;
  height: 37px;
  background: #000;
  border-radius: 20px;
  z-index: 100;
}

.status-bar {
  position: relative;
  height: 54px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px 0;
  font-size: 17px;
  font-weight: 600;
}

.home-indicator {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  width: 134px;
  height: 5px;
  background: #1d1d1f;
  border-radius: 3px;
}

.phone-label {
  text-align: center;
  margin-top: 12px;
  font-size: 13px;
  color: #86868b;
  font-weight: 500;
}
```

## Flow grouping

Group frames in columns by flow, with horizontal progression within each flow.

```html
<div class="flow">
  <h2 class="flow-title">Onboarding</h2>
  <div class="flow-frames">
    <div class="phone" id="S01">...</div>
    <div class="phone" id="S02">...</div>
    <div class="phone" id="S03">...</div>
  </div>
</div>
```

```css
.flow {
  margin-bottom: 80px;
}

.flow-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 24px;
  color: #1d1d1f;
}

.flow-frames {
  display: flex;
  gap: 80px;       /* leave room for arrows between frames */
  align-items: flex-start;
}
```

## SVG arrows

One SVG layer covers the whole canvas. Each arrow is a path. Coordinate math: use the parent canvas's coordinate system, so position frames first, then derive arrow endpoints from frame positions.

**Simplest approach**: hard-code arrow coordinates after laying out frames. For each frame, you know its `left` and `top` in the canvas. The arrow exits the right edge of one frame and enters the left edge of the next.

```html
<svg class="arrows-layer" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- triangle arrowhead -->
    <marker id="arrow-solid" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#007AFF"/>
    </marker>
    <marker id="arrow-dashed" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#FF9500"/>
    </marker>
  </defs>

  <!-- push navigation: solid blue -->
  <path d="M 480 400 C 540 400, 540 400, 600 400"
        fill="none" stroke="#007AFF" stroke-width="2"
        marker-end="url(#arrow-solid)"/>
  <text x="540" y="390" font-size="12" fill="#007AFF" text-anchor="middle">
    tap "Sign In"
  </text>

  <!-- modal present: dashed orange -->
  <path d="M 480 600 C 540 600, 540 600, 600 600"
        fill="none" stroke="#FF9500" stroke-width="2" stroke-dasharray="6 4"
        marker-end="url(#arrow-dashed)"/>
  <text x="540" y="590" font-size="12" fill="#FF9500" text-anchor="middle">
    tap "+" present
  </text>
</svg>
```

### Arrow style legend

| Transition type | Style | Color |
|---|---|---|
| push (NavigationLink) | solid | #007AFF blue |
| modal present (sheet) | dashed | #FF9500 orange |
| full-screen cover | dashed thick (3px) | #FF3B30 red |
| tab switch | double-headed solid | #8E8E93 gray |
| dismiss / back | thin solid | #C7C7CC light gray |

Include this legend in the header strip so viewers can decode the arrows.

### Computing arrow coordinates

If frames are in a flex row with `gap: 80px` and each frame is 393px wide starting at canvas padding 40px:

- Frame N's left edge = `40 + N * (393 + 80)`
- Frame N's right edge = frame N left + 393
- Vertical center = frame top + 426 (half of 852)

For an arrow from frame N's right edge to frame N+1's left edge at the same vertical center, the path is a horizontal line or gentle S-curve. Use a cubic Bezier for visual softness:

```
M [N right] [center]
C [N right + 30] [center], [N+1 left - 30] [center], [N+1 left] [center]
```

For arrows that go up/down (different flow rows), compute both endpoints and route the path around frames rather than through them. A simple L-shape via two Bezier control points works well.

## Header strip

```html
<header class="header">
  <div class="header-left">
    <h1>[App Name]</h1>
    <div class="meta">v0.1 · Generated 2026-XX-XX</div>
  </div>
  <div class="legend">
    <div class="legend-item">
      <svg width="40" height="10"><line x1="0" y1="5" x2="36" y2="5" stroke="#007AFF" stroke-width="2"/></svg>
      <span>push</span>
    </div>
    <div class="legend-item">
      <svg width="40" height="10"><line x1="0" y1="5" x2="36" y2="5" stroke="#FF9500" stroke-width="2" stroke-dasharray="4 3"/></svg>
      <span>modal</span>
    </div>
    <!-- etc -->
  </div>
</header>
```

## Tokens panel

A sticky right-side panel (or below the canvas if width is constrained).

```html
<aside class="tokens-panel">
  <h2>Design System</h2>
  <section>
    <h3>Colors</h3>
    <div class="color-grid">
      <div class="color-swatch">
        <div class="swatch" style="background: #007AFF"></div>
        <div class="swatch-meta">
          <div class="swatch-name">Tint / systemBlue</div>
          <div class="swatch-hex">#007AFF</div>
          <div class="swatch-swiftui">Color.blue</div>
        </div>
      </div>
      <!-- ... -->
    </div>
  </section>
  <section><h3>Typography</h3>...</section>
  <section><h3>Spacing</h3>...</section>
  <section><h3>Radius</h3>...</section>
  <section><h3>Components</h3>...</section>
</aside>
```

## Print styles

```css
@media print {
  body { background: white; }
  .canvas { padding: 20px; }
  .phone-shell { box-shadow: 0 0 0 2px #1d1d1f; }
  @page { size: A3 landscape; margin: 10mm; }
}
```

## Tips

- **Lay out screens first, draw arrows last.** Get all frames placed and labeled, then compute arrow coordinates from the layout.
- **Use IDs on every frame** (`id="S03-login"`) — makes future edits much easier.
- **CSS variables for everything design-token-related** — so the user can tweak one value and have it propagate.
- **Don't over-detail content inside screens.** Real text from the spec where possible; otherwise `Lorem ipsum` is fine for placeholder body text but use real button labels and screen titles.
- **Avoid emoji as iOS UI elements.** Use SF Symbol SVGs from `sf-symbols.md`. Emoji is acceptable only when the spec explicitly says so (e.g. a chat app showing user-typed messages).
