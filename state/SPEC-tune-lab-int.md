# SPEC — the tuning lab (`/tune/`)

The clean description of one page: what it is for, what it shows, and the rules it must
keep. Faults, with their guards, are in `state/PROBLEMS-tune-lab-int.md`.

**Status, 2026-11-21:** built, live on both pages, and the desk's saves are in.

**The page:** `app/src/pages/tune/index.astro`
**The drivers:** `app/src/scripts/tune-lab.js` and `app/src/scripts/tune-uid.js`
**The drawing:** `app/src/scripts/tune-render.js`, shared by both pages
**The maths:** `workbench/plate_math.js`, served at `/api/plate-math` (not copied)
**The data:** `/api/curve/<uid>` → `{ uid, name, speedX, speedY, path }`
**The desk:** `app/src/lib/desk-tune.js`, the row rules; `/api/tune` writes
**The check:** `scripts/check-tune-lab.mjs` (headless Chrome, against a running server)

## 1 · What the page is: one curve, four values, a live drawing

The page exists so a person can see what each value does before saving it to a curve.
It is the sandbox; `/tune/<uid>` is the page that writes.

- [x] The list of curves is a short, named sample: five with speed rows, three stored as paths.
- [x] Every drawing is made in the browser by `plate_math.js` — the same file
      `print_plates.mjs` loads. A copy of the maths on the page would make the preview a
      picture of a picture; `/api/plate-math` serves the single file.
- [x] Dragging a control redraws without a page load. Check: the SVG changes when `plus`
      changes (`scripts/check-tune-lab.mjs`).
- [x] Nothing on this page is saved.

## 2 · The four values, and what each one does

    width %   the base distance from the spine, as a share of the curve's own size
    plus      how much the right edge widens along the curve
    minus     the same for the left edge
    profile   bow: widest at the middle
              s: wide near the start, pinched at the middle, the far half on the other side
              taper: nothing at the start, widest two-thirds along, nothing at the end

- [x] The two sides carry independent laws. Check: with `plus` 6 and `minus` 0 the two
      edges differ (`tests/js/plate-character.test.mjs`).
- [x] `plus` 0 with `minus` 0 is the **only** parallel setting, and the readout says
      `1.00×`. Check: `scripts/check-tune-lab.mjs`.

## 3 · What the readout says

    Right edge 1.5 % → 4.5 % of the curve's size (3.00× at the belly). Left edge the same.
    Band width 1.5 % — asked 6 %, cut so the band cannot fold over itself.

- [x] Distances are shares of the curve's own size, never bare units.
- [x] When the fold guard cuts the width, the readout says so and gives the asked value.
- [x] The ratio is the variation along the curve: `1.00×` means parallel, and that is
      named as the flat case in the legend.

## 4 · The desk: one row per tuning, many versions per spine

A row's `name` is its key and its URL; `curveName` is the name a person typed. Many rows may
carry the same `spine` — five versions of one curve is the point — but two rows may never
share a name.

- [x] **Save over this row** writes the four values and the turn into the row you are on and
      keeps every field it does not own (a chosen name, a construction). Check:
      `app/tests/desk-tune.test.mjs` (`overwrite keeps every field the tune does not own`).
- [x] **Save as new version** needs a name, makes a new row on the same spine, and never
      overwrites the base row. Check: `a new version is a new row on the same spine`.
- [x] **A name collision is refused**, case-insensitively, by the row key or the chosen name,
      and the refusal names the row that holds it. A new version may not take a curve id.
      Check: the three collision tests in the same file.
- [x] The page lists every row on this spine, marks the base row and the current row, and
      links each to its own `/tune/<name>`. Check: `scripts/check-tune-lab.mjs`.
- [x] A `name` is a URL segment: lower-case, digits and dashes only (`slugOf`).
- [x] A save writes the database in one transaction, then the JSON copy the plate reads. A
      failed copy is reported, not hidden.
- [x] **No automatic plate render.** The operator's words: "instead of save and render, put
      robust desk io". The plate picks the row up at its next export.

## 5 · What a path curve says

A curve stored as a path cannot take rows-based rails yet.

- [x] It draws the spine and says "this curve is stored as a path: the plate prints the
      spine only". Check: `scripts/check-tune-lab.mjs` selects `c-0273`.

## 6 · Layout

- [x] Preview left, controls right, legend below the readout. The legend defines every
      control in plain words, including the flat case.
- [x] The page uses the shell margin; no width of its own.
- [x] The version list sits under the readout, with one row per saved version.
