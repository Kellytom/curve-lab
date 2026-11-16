# curves — one folder per curve

A curve is read as a whole: the numbers, the sentence that says what it looks like, and
the picture. So each curve gets a folder, not a row in a table.

```
curves/
  README.md            this file
  index.json           every curve's numbers, one row each, newest measurement last
  <slug>/
    curve.json         the record the page saves, plus a figure specification
    notes.md           variables, formula, plain explanation, provenance
    figure.png         the loop view, drawn by the page itself
```

## Why three files and not one

- **`curve.json` is the machine copy.** It holds the speed rows, the flat spots, the
  loop window, the grid and the measured numbers, in the same shape the sandbox page
  saves. It can be loaded back into the page without translation.
- **`notes.md` is the human copy.** The formula written out, every variable named with
  its meaning and value, one plain sentence about the shape, and where the curve came
  from. A reader who never opens the page can understand the curve from this file.
## Adjusting a figure by hand

The view is written into `curve.json`, so a figure can be corrected without touching code:

```json
"figure": {
  "file": "figure.png",
  "view": "loop",            // "loop" (default), "knot", "whole"
  "focus": { "x": -1.2, "y": -0.3 },   // frame this point instead of the whole curve
  "zoom": 4,                            // the page's zoom slider, positive zooms in
  "pan": [0, 20],                       // pan x and y, in per cent of the frame
  "range": [0.03, 0.97]                 // an explicit window of t, overriding the view
}
```

Then `.venv/bin/python scripts/curve_files.py --record curves/<slug>/curve.json --png 900`.
Omitting every key but `file` gives the loop view. Measured 2026-11-16: seven of the ten
figures show the curve (ink spread 608 wide and 7 to 271 tall), three draw a flat line
(608 by 1) and are withdrawn with their reason.

**No figures are currently shipped.** The pipeline (`scripts/curve_png.mjs`) works, but
the loop view renders these rows as a flat line: measured on all ten, ink spread 240–514
px across and 1–16 px down. One curve draws (spread 251×116). The cause is under
investigation — cancellation at peaks near 10^8, or the framing — and the rule stands:
a figure is only written when it can be shown.

**A figure is only written when the drawing can show it.** Measured 2026-11-16: curves
with eleven or more flat spots have coefficients of 10^13 to 10^23, and the page draws in
double precision, so the knot — 10^-13 of the row's size — collapses to a single point.
Five of the ten folders have `"figure": null` for that reason; their notes say so and
their numbers are still exact. A figure is never invented to fill the gap.

- **`figure.png` is the eye's copy.** 900 px wide, well under the 150 KB limit, made by
  `scripts/curve_png.mjs` from the page's own drawing in the loop view. If the figure and
  the notes ever disagree, **the notes are right** and the figure is stale.

`index.json` is the only aggregate. Adding a curve writes its folder and appends to the
index; it never rewrites a neighbour, so two curves cannot corrupt each other.

## Naming

`loop-<outer denominators>-mid-<copies at 1/2>`, for example `loop-8-11-mid-1` is the
family with flat spots at 1/8 and 1/11 (and their mirrors) plus one copy at 1/2.

## What the numbers mean

| name | meaning | unit |
|---|---|---|
| `grid` | the pitch the rows need, written `1/N` | 1 over N |
| `crossings` | how many times the stroke meets itself | a count |
| `bend` | arc length over the straight distance between the ends | ratio, 1 is straight |
| `arc` | the length of the stroke | exact fraction |
| `loop` | the part of `t` that holds the knot | `t` from, to |
| `step` | the power step of the rows; 1 is whole powers | 1, ½, ⅓ … |

`bend` has no value when the two ends land on the same point — the curve closes, and
arc over zero chord is infinite. That is written in the notes rather than left blank.

## Making one

```sh
.venv/bin/python scripts/curve_files.py --top 3 --cheap 4 --png 900
.venv/bin/python scripts/curve_files.py --record some-record.json --png 900
```

`--top N` takes the N curves with the most crossings from
`workbench/family-census.json`; `--cheap N` adds the N cheapest knots (grid ≤ 100 with
five crossings or more). `--png WIDTH` renders the figure at that width through a
headless browser — the page must be serving on `127.0.0.1:8003`.
