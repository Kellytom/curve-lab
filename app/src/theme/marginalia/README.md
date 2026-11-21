# Marginalia — the docs ornament template

A small, recorded customisation of Astro Starlight: every curve in the collection is an
ornament, used at **a quarter of the text width**, in the page furniture and in a contact sheet.

This directory is the template record. Copy it into another Starlight site and add the two
config lines below; nothing else in the site has to change.

## What is customised

| file | what it is |
|---|---|
| `marginalia.css` | the placements: page title, `h2` companion, blockquote corner, footer flourish, sidebar foot; all masks, so the ink follows the theme |
| `Head.astro` | Starlight's `Head` override. Picks four curves per page from the manifest by a hash of the pathname; the same page is stable, the whole set is used across the docs |
| `ornaments.json` | the generated manifest: every curve's uid, name, family, stars, file, natural width × height, and the scale (0.25) |
| `README.md` | this record |

## The config

```js
starlight({
  // ...
  customCss: ["./src/theme/marginalia/marginalia.css"],
  components: { Head: "./src/theme/marginalia/Head.astro" },
})
```

A docs page (`src/content/docs/docs/marginalia.md`) and a gallery (`src/pages/ornaments.astro`)
complete the template. The gallery shows every curve four-up — a quarter of the text width each.

## The rule

- **One ornamental unit is a quarter of the text column.** The gallery is four columns; the
  title, blockquote and footer ornaments are `width: 25%`; the sidebar is 45 % of its own pane.
- **Masks, not pictures.** `background-color: currentColor` plus `mask: url(...) center / contain`
  gives one file per curve for both themes.
- **The curves are the spine, one soft stroke, no rails.** The stroke is a zero-length dash with a
  round cap, spaced closer than the dot diameter, so the dots overlap into one smooth line — no
  Béziers, and the geometry is untouched. The ornaments are not plates: the plate's bands and
  paper are for print.

## The generator

```sh
node scripts/marginalia.mjs
```

It reads `workbench/curve-registry.json`, draws the spine of every curve (the speed rows, or the
refined stored path), flips y for SVG, and writes:

- `app/public/ornaments/<uid>.svg` — **generated, gitignored** (the set is 3.3 MB);
- `app/src/theme/marginalia/ornaments.json` — the tracked manifest.

`app/package.json` runs the generator before `dev` and `build`, so a clone has the ornaments
without a manual step.

## Reusing it elsewhere

Copy `app/src/theme/marginalia/` and `app/src/pages/ornaments.astro`; point the generator at the
new project's curve source and regenerate. The only site-specific parts are the registry path in
`scripts/marginalia.mjs` and the sidebar entry for the docs page.
