# SPEC — the tuning lab (`/tune/`)

The clean description of one page: what it is for, what it shows, and the rules it must
keep. Faults, with their guards, are in `state/PROBLEMS-tune-lab-int.md`.

**Status, 2026-11-23:** the rail is uncapped, the readout names the fold, and the page carries a
strip of the same values on every kind. Built and live on both pages.

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

    width %   the base distance from the spine, as a share of the curve's own size;
              an unsaved curve starts at 1.5 %, a saved row at its own value
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

    Right edge 0.50 % → 0.66 % of the curve's size (1.32× at the belly). Left edge the same.
    Band width 0.50 %. The rail folds through itself here; the plate dots the crossing.

- [x] Distances are shares of the curve's own size, never bare units.
- [x] The band is never cut (2026-11-23): the rail is the ask at every station, and the readout
      reports the drawn width, not a cut number. Check: `scripts/check-tune-lab.mjs` reads
      `Band width <n> %` and finds no cut sentence; `tests/js/plate-guard.test.mjs` measures it.
- [x] When the rail folds through itself the readout says so, and says the plate dots the
      crossing and hides the loop. Check: the readout on `c-0046` at 0.5 %.
- [x] The amber guide to 1.5× is drawn on the first paint as well as on a redraw, so a redraw
      with unchanged values draws the same picture. Check: `scripts/check-tune-lab.mjs`.
- [x] The ratio is the variation along the curve: `1.00×` means parallel, and that is
      named as the flat case in the legend.

## 4 · The desk: one row per curve, a new curve beside its parent

A tuning row holds the four values and the turn for one curve, keyed by its uid. A new curve
is a real record with a uid of its own, so it appears on `/plates` beside the curve it came
from: `c-0002`, `c-0002a`, `c-0002b`, then `c-0003`.

- [x] **Ten stars and a none** sit above the form. A click stores the rating at once to the
      note's importance (0 = none); the set star clears it. Check: `scripts/check-tune-lab.mjs`
      (eleven buttons, the label matches the stored value) and the route `POST /api/curve-stars`.
- [x] **Save** writes the row for this uid and keeps every field it does not own. It then
      rebuilds that curve's plate. Check: `app/tests/desk-tune.test.mjs`
      (`save keeps every field the tune does not own`).
- [x] **Save as a new curve** needs a name. The box starts with a free `<curve>-vN`, so the
      page is saveable at once; clearing it refuses in place. It copies the spine's geometry, gives the record
      the next letter uid on that spine, writes the registry, the database rows, the desk row,
      and renders the plate. Check: `a new curve is a record beside its parent` and
      `a variant of a variant lands in the original series`.
- [x] **A name is checked against names, aliases and uids**, compared without case. A
      collision is refused and names the owning curve. Check: the collision tests in the
      same file.
- [x] The page lists every curve from this spine, base and variants, each linked to its own
      `/tune/<uid>`. Check: `scripts/check-tune-lab.mjs`.
- [x] **The order is by uid for now**, so a variant sits beside its parent. The ten stars will
      take over the order later; that is not built.
- [x] A save is one transaction, then the JSON copy, then the plate. A failed copy or render
      is reported, not hidden.

## 5 · What a stored outline says

- [x] Every stored outline (`path` or `polyline`) draws the plate's character law over the
      refined walk; the page draws the same band. Check: `scripts/check-tune-lab.mjs` selects
      `c-0273` and `c-0143` and expects a band for each.
- [x] The rail is the asked offset at every station, with no inside cap (2026-11-23). Where it
      folds through itself the page draws the crossing and the readout says the plate hides the
      loop. Check: `tests/js/plate-holes.test.mjs` and `tests/js/plate-gap.test.mjs`.
- [x] Fewer than three stored points: the spine only, and the page says so.
- [x] The outline is stored at six decimals. Identity may round to two; the drawing may not
      (`state/DESIGN-int.md`, register row 44).

## 6 · Layout

- [x] Preview left, controls right; the readout sits under the preview in the same column, so
      the left column's height matches the form and no empty band is left between them. The
      preview fills its column and centres the drawing.
- [x] The page uses the shell margin; no width of its own.
- [x] Below 860 px the page stacks to one column: the preview, the readout, then the form.
- [x] Width, plus and minus each have a number box and a slider; moving one moves the other.
      The slider carries no name, so only the number is submitted. Check:
      `scripts/check-tune-lab.mjs` (the slider reaches the number and redraws).
- [x] The version list sits under the strip, with one row per saved version.

## 7 · The same values on other kinds

The operator, 2026-11-23, after tuning `c-0046` to 0.5 %: "put some more curves below it to
confirm it works for all kinds."

- [x] Six figures under the grid, drawn at the page's own four values, so one setting is
      checked across the collection rather than on one curve.
- [x] The kinds come from the records, never from a typed list of uids: a row curve (two), a
      stored path (two), a path with branches, a wonk double. The first curve of each kind
      that draws is shown; the current curve is skipped.
- [x] Each caption names the uid (a link to its page), the kind, the name, and the measured
      crossing count on its rail. "No crossing at this width" is a result, not a failure.
- [x] Three figures across, one below 720 px; each figure is 130 px tall so the captions line
      up. Check: `scripts/check-tune-lab.mjs` (five or more figures, every named kind present,
      every caption gives a crossing count).
- [ ] A per-kind choice by the operator (which row curve, which double) is not built; the
      rule is first-in-registry for now.
