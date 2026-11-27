# Quintic from Guide — a free-form quintic inside Inkscape

You draw a free-hand guide with a trackball or an Apple Pencil. The extension
takes six points off that stroke, draws the quintic Bézier through them, and
exports the six exact control points to Blender and GeoGebra. SVG itself draws
only cubics, so the on-screen curve is a C2 chain of cubics — the record is the
quintic.

Operator's ask, 2026-11-26: "in order to display a free form quintic curves use
inkscape … build this exact workflow right inside Inkscape", then "use industry
best practice and follow what blender does with its control points", then "do all
the work".

## The three layers

| layer | what it is | how good it is |
|---|---|---|
| 1 the drawn curve | the freehand stroke, read from the selection | the reference |
| 2 the six-point curve | six points taken off the stroke, and the quintic through them | the **drawn→quintic** miss, printed |
| 3 the quintic display | that curve as a C2 cubic chain, because SVG has no quintic | the **quintic→chain** miss, printed |

Both misses are printed after every run, in pixels. Neither is assumed.

Files:

| path | what it is |
|---|---|
| `inkscape/quintic-guide.inx` | the dialog: three tabs, Points / Display / Export |
| `inkscape/quintic_guide.py` | the glue — reads the selection, writes the path |
| `inkscape/quintic_math.py` | all the maths; plain stdlib, no inkex |
| `tests/test_quintic_math.py` | 32 tests guarding the maths and the exports |
| `scripts/quintic_report.py` | prints every table in this document |
| `state/PROBLEMS-quintic-guide-int.md` | the faults this extension has had |

Python, not TypeScript: an extension that runs inside Inkscape must speak
`inkex`, and inkex is Python. The maths file is inkex-free so it can be tested by
`.venv/bin/python` with Inkscape closed.

## Install

```sh
cp inkscape/quintic-guide.inx inkscape/quintic_guide.py \
   ~/Library/"Application Support"/org.inkscape.Inkscape/config/inkscape/extensions/
```

Then **Extensions → Curve Lab → Quintic from Guide**. The maths is read from this
repository (`~/developer/curve-lab`, or `$CURVE_LAB_ROOT`), so editing
`quintic_math.py` needs no reinstall; editing the `.py` glue or the `.inx` does.

## Layer 2: the four ways to take six points

Blender's Bézier control points sit **on** the curve and the handles are
computed, so the point you place is a point the curve goes through. That is the
first mode and the default.

| mode | the six points | the curve |
|---|---|---|
| **On the curve, evenly spaced** (default) | on the stroke, at 0, .2, .4, .6, .8, 1 of its arc length | solved exactly through all six |
| **A best fit** | *not* on the stroke; the control points with the smallest total miss | least squares, ends pinned to the stroke's ends |
| **A cage: the guide's own 6 nodes** | the six nodes of the guide path | the quintic's control points — the curve sits inside them |
| **A cage from 6 samples** | the same six even points, used as control points | as above |

The solve for "on the curve" is exact, not iterative: the six Bernstein weights
at t = k/5 are rational, so the 6×6 system is solved in `Fraction` and only the
answer becomes decimals. The best fit is the textbook single-span least squares
(Piegl & Tiller ch. 9): arc-length parameter, ends pinned, 4×4 normal equations.

## Spans: one quintic is not always enough

A long stroke is not one quintic. Split it with **Spans** and each stretch gets
its own six points, its own quintic and its own chain; the spans meet C0, exactly
where the stroke was cut, so there is no gap. Measured on 2026-11-26 with
`.venv/bin/python scripts/quintic_report.py` — miss from the drawn stroke to the
six-point curve, in px:

| stroke | mode | 1 span | 2 | 3 | 4 | 6 |
|---|---|---|---|---|---|---|
| wild 400 px | on the curve | 46.087 / 20.519 | 16.776 / 4.397 | 6.435 / 0.975 | 3.414 / 0.505 | 0.522 / 0.098 |
| wild 400 px | best fit | 46.130 / 21.582 | 9.940 / 2.849 | 2.311 / 0.483 | 1.448 / 0.333 | 0.325 / 0.072 |
| freehand-like | on the curve | 26.004 / 10.664 | 2.848 / 0.790 | 1.225 / 0.264 | 0.666 / 0.169 | 0.210 / 0.044 |
| freehand-like | best fit | 13.058 / 7.265 | 1.876 / 0.786 | 0.413 / 0.157 | 0.256 / 0.098 | 0.080 / 0.025 |

(max / rms; both columns in each cell.)

Read it this way:

- **One span on a long stroke is a bad fit** — 26 px to 46 px. No six points can
  fix that; only a split can.
- **Two spans** bring a freehand stroke to about 2 px; **four** to under 1 px.
- **The best fit roughly halves the miss** at the same span count, and is barely
  better than even points at one span on a wild stroke — the freedom is not
  there to use.

## Layer 3: the cubic chain

The chain passes exactly through the quintic's stations (t = i/n), leaves and
arrives on the quintic's own end tangents, and is **C2** at every interior joint
(a clamped cubic spline, solved by `h[j-1]d[j-1] + 2(h[j-1]+h[j])d[j] +
h[j]d[j+1] = 3(Δ[j-1] + Δ[j])`). Between stations it is an approximation, and
its size is measured by distance to the cubic itself.

Set **Cubic segments = 0** and the extension picks the smallest count that meets
the tolerance (2, 4, 8, 16, 32). Measured:

| cubics | wild cage (400 px) | gentle cage (250 px) |
|---|---|---|
| 2 | 16.1187922 px | 0.3720579 px |
| 3 | 3.0009945 px | 0.0771605 px |
| 4 | 0.9495546 px | 0.0241327 px |
| 8 | 0.0548640 px | 0.0015216 px |
| 16 | 0.0032101 px | 0.0000954 px |
| 32 | 0.0001993 px | 0.0000064 px |

The brief's "two or three cubics at under 0.001 px" does not hold at document
scale: 0.001 px needs 16 cubics on the gentle cage and 32 on the wild one. Few
nodes and sub-pixel accuracy are a trade, and the extension reports the miss it
achieved rather than the one it hoped for. A fit costs 20–116 ms, which keeps
live preview usable.

## Fullness is tension

`P_i = (1 − α) · L_i + α · G_i`, where `L_i` is the straight chord at i/5 and
`G_i` is the drawn point. α = 1 keeps the drawn curve, α = 0 is the straight
line, and the two end points never move. Because `P_1 − P_0` scales with α this
is the tangent length — the same thing a Bézier handle length does in Blender.

## No overshoot, or an honest number

A quintic through six points can balloon outside them: on the 400 px test guide
the **best fit** sticks out by **480 px** and **even points** by **774 px**; on a
gentle 250 px cage, 16.67 px. Blender has "Auto Clamped" handles for this reason.

**Clamp inside the six points** pulls each control point into the box holding the
six points. That is provable, not cosmetic: a Bézier stays inside the convex hull
of its control points, so the clamped curve cannot leave the box.
`OvershootTest` checks 1001 points of the curve against the box. It is off by
default, and clamping costs miss (3 spans clamped: 27.762 px against 6.435 px
unclamped) — so the run says which happened.

## The six points are visible

**Mark the six points** draws a small ring at each control point, in a group
tagged `data-quintic-points`, so the three layers can be seen rather than
inferred. The curve itself is tagged `data-quintic-guide="<guide id>"` and is
replaced, not stacked, when the extension runs again.

## What leaves Inkscape

With **Export folder** set, three files per guide (`<guide id>-*`):

- `quintic.json` — the record: per span, six control points in SVG coordinates
  (y **down**), the drawn→quintic max and RMS, the cubic count and the
  quintic→chain miss.
- `blender.py` — paste into Blender's Text Editor and run: one exact order-6
  NURBS spline per span, `use_endpoint_u = True`. Blender clamps the order to the
  point count silently, so 6 points and order 6 together are the only
  combination that means what it says.
- `geogebra.txt` — `P0 … P5` and `Q(t)` as the Bernstein sum for one span;
  `S1_P0 … S1_P5`, `C1(t)`, `S2_P0 …` for several.

**The y flip happens here and only here**: SVG is y down, Blender and GeoGebra
are y up, so the exports negate y and say so in a comment. The drawn path keeps
the document's coordinates.

## Use

1. Draw the guide with a pen or trackball; leave it pale and dotted.
2. Select it. **Extensions → Curve Lab → Quintic from Guide.**
3. Points tab: choose the mode, raise **Spans** until the printed miss is small
   enough for the job.
4. Display tab: keep Live preview ticked and drag **Fullness**. Each change
   re-runs the extension; a fit takes 20–116 ms here.
5. Apply. Run again with the same numbers and nothing is rewritten: inkex
   compares documents and skips an identical save.

## Testing a whole sheet of guides

```sh
.venv/bin/python scripts/quintic_report.py --sheet workbench/quintic-guides --spans 3
```

Runs the **installed** extension over every `.svg` in the folder and prints one
row per curve, read back from the sidecar the extension wrote — so the numbers
come from Inkscape's own Python, through the files the operator installs.
`--mode` picks even / lsq / cage-nodes / cage-samples.

## Limits, stated

- Inkscape draws cubics; the quintic is only ever the record plus a chain.
- Spans join C0. A visible corner at a cut is possible on a sharp stroke; raise
  the span count or accept it.
- One guide per run: the first path in the selection is used.
- Live preview re-runs the whole extension on every slider move.
