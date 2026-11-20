# SPEC — the stylesheets

The clean description of how the app is styled. It carries no history; faults and
their guards are in `PROBLEMS-css-int.md`.

**Layout:** `app/public/vendor/app-shell.css`
**Colours and type:** `app/public/vendor/curve-lab-theme.css`
**Base:** `app/public/vendor/pico.min.css`
**Check:** `app/scripts/check-pages.mjs` (every page), `app/scripts/check-layout.mjs`
(three widths, zoom included)

## The one idea

**One stylesheet owns layout, one owns colour, and a page owns neither.** A page may
size its own figures in its `head` slot; it does not restate a margin, a font, or a
colour that the shell already sets.

## What each file owns

| file | owns | never contains |
|---|---|---|
| `pico.min.css` | the base controls, forms, spacing scale | anything of ours |
| `curve-lab-theme.css` | the colours and the type faces, as CSS variables | layout |
| `app-shell.css` | the header, the page margin, overflow rules | colour literals, except in the header's rules |

A colour literal in a page is allowed for a figure's own marks (a curve's stroke, a
station's dot), because those are data, not chrome.

## The header

Two rows, one margin:

1. **the title row** — `curve-lab` (Georgia, 700, 1.12rem/1.15) and the `draft A`
   mark in small caps beside it;
2. **the options row**, indented `0.9rem` behind a 2px rule — `this page is …`,
   then the menu, all in the mono face at 0.7rem/1.5.

Rules for it:

- **The title stays on its line.** The brand never wraps; the draft mark may drop
  below it at narrow widths.
- **The options wrap freely but stay indented**, so they read as choices under a
  title rather than as a second title.
- **The header is at most 96 px tall** at 1280 px wide; 86 px is the working value.
- **The current page is text, not a link**, marked `aria-current="page"`.

## The page margin

One rule, for every page, in `app-shell.css`:

    main { width: 100%; max-width: 1180px; margin-inline: auto; padding: 0 1.25rem 3.5rem; }

A page does not invent its own. `mainClass=""` is for a page with its own layout, and
even then it inherits this margin.

## Overflow

- **A panel of large numbers scrolls inside itself** (`overflow-x: auto`); it never
  widens the document.
- **The document never scrolls sideways.** Asserted at 1280 and 420 px.
- **A figure fits its frame**: if a circle would be cut by the edge, the frame grows
  or the circle is not drawn.

## Text size and browser zoom

**The reader may enlarge the text, and the page must hold.** The operator's habit is
`Cmd +` twice, which is 150%: every dimension grows, and the layout width shrinks to
`1280 / 1.5 ≈ 853` CSS pixels. Other readers zoom differently, use a larger default
font, or read on a phone, so the rule is stated in layout widths rather than in one
person's keystrokes.

What must hold at 150% and at 420 px:

- **no sideways scrolling** — the document fits its viewport;
- **the brand stays on one line** — it is a title, not a sentence;
- **the options may wrap** and the header may grow taller; the 96 px ceiling applies
  only at 100% width, where a 220 px ceiling replaces it under zoom;
- **figures shrink with the page**, never overflow it.

Check: `app/scripts/check-layout.mjs`, run by `npm --prefix app run test:pages`. It
measures 1280, 853, 683 and 420 px wide.

## Type

- Two faces only: Georgia for headings and the brand, the monospace stack for
  numbers, labels and controls.
- Nothing below 0.7rem, except tick labels, which may be 0.62rem.
- Legends and figure labels are at least 15 px on the rendered page.

## Naming

`kebab-case` for classes and ids, prefixed by the figure or section that owns them
(`pm-`, `gd-`, `st-`, `sp-`, `hit-`, `site-`). A class used by one page lives in that
page's `head` slot; a class used by two lives in `app-shell.css`.

## How to change it

1. Change this file first: what moves, which rule changes, what it costs.
2. If the change touches more than two rules, rewrite the block; single values may
   be patched.
3. Run `npm --prefix app run check` and open two pages at 1280 and 420 px wide.
4. If a fault was fixed, record it in `PROBLEMS-css-int.md` with its guard.
