# book — temporary plate export

The short-term deliverable: PNG plates for a book, from the curves we already
have. SVGs are written beside them, so the later Inkscape step starts from the
same geometry. The operator's rules, 2026-11-17: **white ground, no text on the
image, clipped to the curve**, a plain gallery with no controls.

## The name

    <descriptor>-<variant>-t-exp-c-<serial>

    swan-1-t-exp-c-0001.png

- **descriptor** — the shape's word: `swan`, `sweep`, `lace`. Lowercase letters
  and digits, no hyphen (the `-t-exp-c-` marker is how the name is parsed).
- **variant** — an integer, for another offset or another member of the family.
- **t** — temporary set. The final set can be `f` without renaming the geometry.
- **exp** — export, not a working page.
- **c** — curve (as opposed to a terminal or an ornament).
- **serial** — four digits, allocated once in `plates.json`, never reused. A
  re-export keeps the name, so a LibreOffice link survives.

## The image

| property | value | why |
|---|---|---|
| long side | 3000 px | 10 in at 300 dpi; downscaling for the page is safe |
| dpi | 300 (PNG `pHYs`) | LibreOffice inserts at 254 × the aspect mm, not 790 mm |
| ground | `#ffffff` | print |
| ink | `#111111` | print |
| stroke | 0.35% of the long side (10.5 px) | about 0.5 mm at 150 mm wide |
| margin | 1.2% of the long side (36 px) | the stroke is never cut; the curve fills 97.6% |
| text | none | operator's instruction; the gallery carries the name |
| gallery | two columns, the label outside the image | operator's instruction; the label is the id and the note |
| canvas | the bounding box of spine + both rails | no side whitespace; "clipped to the curve" |

The curve is as large as the image allows because the canvas aspect **is** the
drawn bounding box. A tall curve gets a tall plate; nothing is padded to a
square.

## Adding a plate

1. Add a row to `plates.json` with a fresh serial. Three kinds:
   - `"kind": "ph"` — a speed pair `u`, `v`. The rail is exact.
   - `"kind": "record"` — a stored curve's `slug`; its speed rows are a PH pair.
   - `"kind": "cubic"` — a Pythagorean `triple`; the rail is the true normal
     offset, sampled.
2. `offsetShare` is the rail distance as a share of the spine's bounding-box
   diagonal. The export refuses a plate whose rail folds (`|d·κ| ≥ 0.98`).
3. Run:

```sh
.venv/bin/python scripts/plate_export.py
```

It writes `svg/<id>.svg`, `plates/<id>.png`, `render.html` and `index.html`,
prints the distance, the fold margin, the pixel size and the bytes, and stamps
300 dpi.

## What is not done

- **Clipping to the ink.** The curve's ends stop at the margin, not at a hand
  cut; the operator will trim where it matters.
- **Character offsets.** The rails are a constant distance; a varying width
  (a stroke that swells) is the later width-modulation track.
- **Labels.** Deliberately none on the image. If a plate needs a caption, it
  belongs in the book layout.
- **LibreOffice layout.** The plates are made for framing, not paged yet. A
  contact sheet with the trim size is the next step.
- **A final set.** `t` means temporary; the chosen plates get a stable set
  letter before print.

## The files

| path | what it is |
|---|---|
| `plates.json` | the manifest: id, source, offset share, note |
| `plates/*.png` | the images, 300 dpi |
| `svg/*.svg` | the same plates as SVG |
| `render.html` | the page the screenshots are taken from (generated) |
| `index.html` | the gallery, no controls (generated) |
