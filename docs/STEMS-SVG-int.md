# The stems print sheet — 8.5 × 11, three presets in a vase

**Status:** working design, 2026-11-02. Reuse this page rather than rebuild it.
The visual proof is `workbench/stems-abc.html`; the print file is
`workbench/stems-abc.svg`.

## What it is

Three generator presets, sampled from their exact rational Bézier control data,
standing in solid gold squircle vases at the 10-inch line and rising to about
the 3-inch mark. The stems are separate groups (`stem-a`, `stem-b`, `stem-c`)
so they can be moved, mirrored or swapped. The top tips are the positions for
the ornaments still to come: a leaf, flower, bean or heart.

The sheet has **no page border**. Its two rulers sit in the 0.5 in margins.

## Files and pipeline

| File | Role |
|---|---|
| `scripts/stems_print.py` | geometry: preset inputs, rotations, scale, vase placement, 2,001 page samples |
| `scripts/stems_print.mjs` | renderer: SVG and print wrapper from the JSON; no SVG library |
| `workbench/stems-abc.json` | the contract between the two |
| `workbench/stems-abc.svg` | the printable SVG |
| `workbench/stems-abc.html` | on-screen / print wrapper with `@page 8.5in 11in` |
| `npm run stems` | `node scripts/stems_print.mjs` |

Regenerate:

```sh
.venv/bin/python scripts/stems_print.py      # writes the JSON
node scripts/stems_print.mjs                 # writes the SVG + HTML
# or just: npm run stems
```

Open <http://127.0.0.1:8003/workbench/stems-abc.html>.

The split is deliberate: Python owns the curve mathematics; Node owns the
drawing. The JSON is enough to redraw the sheet without Python.

## Page and units

- Page: **8.5 × 11 in = 215.9 × 279.4 mm**.
- Internal: **1 SVG unit = 1 mm**; `viewBox="0 0 215.9 279.4"`, physical
  `width="215.9mm" height="279.4mm"`.
- Margins: **12.7 mm** (0.5 in); drawing area **190.5 × 254 mm**.
- Model coordinates are **+y up**; the page is **+y down**. The flip happens
  once in the stem mapping:
  `page_y = CELL_BOTTOM - STEM_LIFT - (model_y - y0) * scale`.
- The previous version used 0.01 in units and inch rulers; this one is metric.
  Do not mix the two.

## The three stems

| label | preset | inputs | rotation | other |
|---|---|---|---|---|
| **a** | sextic | `n=6`, `h=(1,2)`, `u=(-1,1,0)`, `v=(2,-1,0)`, step `1/2` | **143.0956° CW** — the exact start-vertical angle, requested as ~120° CW | first; most vertical from the box |
| **b** | quintic | `n=5`, `h=(1)`, `u=(-2,-1,1)`, `v=(-1,-1,2)`, step `1/2` | **30° CCW** | second; slightly right from the box |
| **c** | cubic | `n=3`, `h=(1)`, `u=(2,-2)`, `v=(1,-2)`, step `1/4` | **35° CCW** | third; unmirrored, right-leaning |

- The order is **a, b, c**: a first (most vertical at the box), b second
  (slightly right), c third (right). The title follows the list order.
- “Lean” is measured from the **visual top** to the **visual base**, not from
  the parameter ends. All three currently read **right** by that test; a is the
  most vertical at the base, b/c progressively more right.
- Each stem is scaled to **177.8 mm (7 in)** tall, with no fit factor now. a/b
  tops land at **76.2 mm (3 in)**; c’s parameter end is the inner hook at
  99.5 mm, with its outer hook higher.
- The base of each stem is lifted **12.7 mm (0.5 in)** from the bottom of its
  vase, so the stem emerges from the **vase mouth**, not from behind it.
- Sampling: 667 points per stem, 2,001 total, in `points_page_mm`.

## Vases

- **12.7 mm (0.5 in)** n = 4 **squircles**: `|x|⁴ + |y|⁴ = 1`, the same
  squircle as the Euler-square page.
- Solid **gold**: fill `#c9a441`, edge `#a8852f`, edge width 0.2 mm.
- At the **10-inch line**: the boxes run from **254.0 mm to 266.7 mm** absolute
  (the drawing bottom is 266.7 mm). The 10-inch line is 254 mm from the top.
- The boxes are placed explicitly at **x = 12.7, 30.4 and 48.1 mm**, so there
  is a **5 mm margin between boxes**. The stems’ bases sit at the box centres;
  the stems overlap and fan from the tight vase row, leaving the right side of
  the page empty.
- Labels `a`, `b`, `c` sit 3 mm under each vase, 2.4 mm Georgia, muted.

## Drawing style

| element | value |
|---|---|
| stem | `#2e2413`, 0.46 mm stroke, round joins/caps |
| vase | `#c9a441` fill, `#a8852f` edge, 0.2 mm |
| endpoints | open red `#b23a2b` circles, r = 0.6 mm, 0.25 mm stroke |
| helper text | `#7b6c4e`; labels 2.4 mm, title 3.0 mm, rulers 2.2 mm |
| page | white, no border |

The top endpoint is the ornament position; the bottom endpoint is the vase
mouth. Both are marked with open circles so the tips are findable.

## Rulers

They sit in the 12.7 mm margins, outside the drawing area.

- Bottom: 0–190 mm across the 190.5 mm drawing width; 5 mm ticks, 20 mm labels
  (0, 20, … 180), plus 190 at the end and `mm`.
- Side: 0–254 mm down the 254 mm drawing height; 5 mm ticks, 20 mm labels
  (0, 20, … 240), plus 254 at the end and `mm`.
- Ruler line 0.2 mm; ticks 2.3 mm (10 mm) / 1.3 mm (5 mm).

## JSON contract

Top level:

```json
{
  "page": {
    "width_mm": 215.9, "height_mm": 279.4, "margin_mm": 12.7,
    "drawing_mm": [190.5, 254.0], "units_per_mm": 1
  },
  "box_shape": "squircle n=4",
  "stems": [ ... ],
  "note": "..."
}
```

Each stem:

```json
{
  "label": "a",
  "preset": "sextic",
  "inputs": { "n": 6, "h": [1,2], "u": [-1,1,0], "v": [2,-1,0],
              "step": "1/2", "control_scale": 240 },
  "rotation": { "direction": "cw", "deg": 143.0956 },
  "mirror": false,
  "lean": "right",
  "shift_mm": 0.0,
  "natural_box": [-0.001, 0.0, 319.374, 1040.192],
  "cell": { "x_mm": 12.7, "bottom_mm": 266.7, "side_mm": 12.7 },
  "scale_page_per_model": 0.1709,
  "start_page_mm": [19.05, 254.0],
  "end_page_mm": [73.6406, 76.2],
  "points_page_mm": [[19.05, 254.0], ...]
}
```

`natural_box` is in the rotated model units; `scale_page_per_model` maps it to
page mm. `cell.x_mm` is the left edge of the vase; the stem’s base is at
`cell.x_mm + cell.side_mm/2`. The renderer does not need any other state.

## Reuse

- **Change a stem:** edit its entry in `STEMS` in `scripts/stems_print.py`
  (spec, `rotation`, `mirror`); rerun both scripts.
- **Add a fourth stem:** append to `STEMS`. The boxes are placed at
  `MARGIN + i * (CELL + BOX_GAP)`, so the new vase lands 5 mm after the last;
  the stems are shifted so each base sits at its box centre. The Node title
  and labels follow the list. The 2,001 sample count changes with 667 per stem.
- **Change the vase:** the squircle is `squirclePath(..., n=4)` and the colors
  are `VASE` / `VASE_EDGE` in `scripts/stems_print.mjs`.
- **Change the layout:** `CELL` (vase), `BOX_GAP` (5 mm), `CELL_TOP`,
  `STEM_LIFT`, `STEM_H`, `MARGIN` at the top of `scripts/stems_print.py`.
- **Change the page:** the page constants in Python and the `width`/`height`,
  rulers and `@page` in the Node/HTML. The rulers are sized from the page
  constants, not hard-coded to 8.5 × 11 where possible.
- **Restyle:** only `scripts/stems_print.mjs`; the Python emits geometry only.

## Decisions and open points

- **a is 143.0956° CW, not 120°.** The 120° was approximate; 143.0956° is the
  exact turn that makes the first tangent vertical. Set `rotation=120.0` if the
  literal 120° matters more than the vertical start.
- The stems are the **generator presets**, not clothoid chains. There is no
  clothoid `A`/`L` here; the PH inputs are the constants. The JSON note says so.
- The vases form a **5 mm-spaced row** at the left; the stems overlap and fan
  from it. The right half of the page is deliberately empty for now.
- The top tips are at about the **3-inch mark**; the ornaments (leaf, flower,
  bean, heart) are not part of this sheet yet.
- The physical print is 8.5 × 11 in even though the internal coordinates are
  mm. Printing the HTML uses `@page size: 8.5in 11in; margin: 0`; the SVG
  already carries its own 0.5 in margin.
