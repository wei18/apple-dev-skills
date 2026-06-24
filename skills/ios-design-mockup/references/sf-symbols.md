# SF Symbols — Inline SVG snippets

SF Symbols is Apple-licensed and can't be redistributed as font files. These are stylistically-faithful redraws of the 20 most common symbols, as inline SVG. They look at home in iOS mockups without being literal copies.

For any symbol not listed here, use a text placeholder: `[icon: figure.run.circle]`.

## How to use

Drop the `<svg>` directly into your HTML. Set `width`/`height` to control size. `fill="currentColor"` lets the symbol inherit text color (use this for TabBar items, NavBar buttons, etc).

```html
<span style="color: var(--color-tint);">
  <svg width="25" height="25" viewBox="0 0 24 24" fill="currentColor">...</svg>
</span>
```

Standard sizes:
- TabBar icon: 25 × 25
- NavBar icon: 22 × 22
- List row trailing chevron: 12 × 20
- Inline body icon: 17 × 17

---

## Navigation / chrome

### chevron.right (back/forward indicator)
```svg
<svg viewBox="0 0 12 20" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <path d="M2.5 2 L10 10 L2.5 18" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
</svg>
```

### chevron.left
```svg
<svg viewBox="0 0 12 20" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M9.5 2 L2 10 L9.5 18" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

### xmark (close)
```svg
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M6 6 L18 18 M18 6 L6 18" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
</svg>
```

### plus
```svg
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 5 V19 M5 12 H19" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
</svg>
```

### ellipsis (more menu)
```svg
<svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <circle cx="5" cy="12" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="19" cy="12" r="2"/>
</svg>
```

---

## TabBar / common

### house (Home tab)
```svg
<svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 3 L2 11 V21 H9 V14 H15 V21 H22 V11 Z"/>
</svg>
```

### house.fill — same path, used for active state

### magnifyingglass (Search)
```svg
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="11" cy="11" r="6" stroke="currentColor" stroke-width="2.5"/>
  <path d="M16 16 L21 21" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
</svg>
```

### heart
```svg
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 21 C-7 9 6 -1 12 7 C18 -1 31 9 12 21 Z" stroke="currentColor" stroke-width="2" fill="none"/>
</svg>
```

### heart.fill
```svg
<svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 21 C-7 9 6 -1 12 7 C18 -1 31 9 12 21 Z"/>
</svg>
```

### person.circle
```svg
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
  <circle cx="12" cy="10" r="3.5" fill="currentColor"/>
  <path d="M5 20 C7 16 17 16 19 20" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/>
</svg>
```

### person.circle.fill
```svg
<svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="10"/>
  <circle cx="12" cy="10" r="3.5" fill="white"/>
  <path d="M5 20 C7 16 17 16 19 20" stroke="white" stroke-width="2" stroke-linecap="round" fill="none"/>
</svg>
```

### gearshape (Settings)
```svg
<svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 8.5 a3.5 3.5 0 1 0 0 7 a3.5 3.5 0 0 0 0 -7 z M19.4 12 c0 .6 -.1 1.2 -.2 1.8 l2.1 1.6 c.2.1.2.4.1.6 l-2 3.4 c-.1.2-.4.3-.6.2 l-2.5 -1 a7.4 7.4 0 0 1 -3.1 1.8 l-.4 2.6 c0 .2-.2.4-.5.4 h-4 c-.2 0-.4 -.2 -.4 -.4 l-.4 -2.6 a7.4 7.4 0 0 1 -3.1 -1.8 l-2.5 1 c-.2 .1-.5 0-.6 -.2 l-2 -3.4 c-.1-.2 -.1 -.5 .1 -.6 l2.1 -1.6 a7 7 0 0 1 0 -3.6 l-2.1 -1.6 c-.2 -.1 -.2 -.4 -.1 -.6 l2 -3.4 c.1 -.2 .4 -.3 .6 -.2 l2.5 1 a7.4 7.4 0 0 1 3.1 -1.8 l.4 -2.6 c0 -.2 .2 -.4 .4 -.4 h4 c.3 0 .5 .2 .5 .4 l.4 2.6 a7.4 7.4 0 0 1 3.1 1.8 l2.5 -1 c.2 -.1 .5 0 .6 .2 l2 3.4 c.1 .2 .1 .5 -.1 .6 l-2.1 1.6 c.1 .6 .2 1.2 .2 1.8 z" fill-rule="evenodd"/>
</svg>
```

### bell
```svg
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M6 16 V11 a6 6 0 0 1 12 0 V16 L19.5 18 H4.5 L6 16 Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
  <path d="M10 21 a2 2 0 0 0 4 0" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>
```

---

## Status bar icons

### Cellular signal
```svg
<svg viewBox="0 0 20 14" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <rect x="0"  y="9" width="3" height="5" rx="0.5"/>
  <rect x="5"  y="6" width="3" height="8" rx="0.5"/>
  <rect x="10" y="3" width="3" height="11" rx="0.5"/>
  <rect x="15" y="0" width="3" height="14" rx="0.5"/>
</svg>
```

### Wifi
```svg
<svg viewBox="0 0 20 14" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <path d="M10 14 a1.5 1.5 0 1 0 0 -3 a1.5 1.5 0 0 0 0 3 z"/>
  <path d="M5 9 C7 7 13 7 15 9" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>
  <path d="M2 5 C5 2 15 2 18 5" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>
</svg>
```

### Battery (full)
```svg
<svg viewBox="0 0 28 14" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="0.5" y="0.5" width="23" height="13" rx="3" stroke="currentColor" opacity="0.4"/>
  <rect x="2" y="2" width="20" height="10" rx="1.5" fill="currentColor"/>
  <rect x="24.5" y="4.5" width="2" height="5" rx="1" fill="currentColor" opacity="0.4"/>
</svg>
```

---

## Common UI

### checkmark
```svg
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 12 L10 18 L20 6" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

### checkmark.circle.fill
```svg
<svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="10"/>
  <path d="M7 12 L10.5 15.5 L17 9" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
</svg>
```

### exclamationmark.triangle (warning)
```svg
<svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 3 L22 20 L2 20 Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round" fill="none"/>
  <path d="M12 9 V14" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
  <circle cx="12" cy="17.5" r="1" fill="currentColor"/>
</svg>
```

### arrow.up.right (external link)
```svg
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M7 17 L17 7 M8 7 H17 V16" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

### square.and.arrow.up (Share)
```svg
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 3 V15 M7 8 L12 3 L17 8" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M5 12 V20 H19 V12" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/>
</svg>
```

### trash
```svg
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 7 H20 M9 7 V4 H15 V7 M6 7 L7 21 H17 L18 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

### pencil
```svg
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M3 21 L7 20 L20 7 L17 4 L4 17 L3 21 Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
</svg>
```

---

## Notes for inventing iOS-style icons

When you need a symbol not in the list:

1. Match SF Symbols stroke weight — most are around 2-2.5px on a 24px viewBox
2. Use `stroke-linecap="round"` and `stroke-linejoin="round"` — SF Symbols are uniformly rounded
3. For "filled" variants of outlined icons, swap `stroke` for `fill` on the same path
4. Keep optical balance — symbols look slightly smaller than their bounding box; visual weight near 70-75% of the viewBox is typical
5. If in doubt, leave a text placeholder rather than a bad drawing
