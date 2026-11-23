# SPEC — chat display (`/chat-display/`)

**Status, 2026-11-23:** first slice built — the index, one appendix page, KaTeX maths.

**The index:** `app/src/pages/chat-display/index.astro`
**An appendix:** `app/src/pages/chat-display/[slug].astro`, one per
`app/src/data/chat-display/<slug>.md`
**The renderer:** `app/src/lib/markdown.js` (micromark + mdast + KaTeX)
**The check:** `app/scripts/check-pages.mjs` (header, main, draft mark, no self-link)

## What it is

The operator: "the full chat response in browser". A reply is one line; the long version —
figures, formulas, tables, a slider where it earns it — lives at its own URL. One page per
answer, generated from a Markdown file, never hand-edited HTML.

- **The chat line:** `see the appendix: http://127.0.0.1:4321/chat-display/<slug>/`.
- **The page:** the Markdown file rendered, with maths typeset by KaTeX and bare URLs coloured.
- **The index:** every appendix, newest first by file name.

## The libraries, and why each is here

| library | why |
|---|---|
| `micromark` + `mdast` | already carried by Astro; the Markdown parser |
| `micromark-extension-math` + `mdast-util-math` | `$inline$` and `$$display$$` nodes |
| `katex` | those nodes typeset as mathematics, not spelled out |
| `d3` | already present; charts when a chart says more than a table |

Installed 2026-11-23 with `npm --prefix app install katex micromark-extension-math mdast-util-math`.
No Quarto: it is a second publishing toolchain and would duplicate Astro.

## Rules with a check each

- [x] A page is a Markdown file; the HTML is generated on every request. Check: edit the file,
      reload, the change appears.
- [x] Maths renders. Check: `/chat-display/offsets/` contains KaTeX output.
- [x] One header, one `<main id="main">`, the shared margin. Check: `check-pages.mjs`.
- [x] A missing appendix says so and links to the index, with a 200. Check: `/chat-display/nope/`.
- [x] The chat still says the result in words; the appendix is the long form, not a substitute.

## What is not built

- Figures are not yet generated per appendix; they are Markdown-embedded or linked.
- The interactive pane (a slider like the loop-angle one) is not mounted in an appendix yet.
- No index ordering beyond file name; a date in the slug is the convention
  (`2026-11-23-offsets`).
