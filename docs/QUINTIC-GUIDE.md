# Quintic from Guide — a free-form quintic inside Inkscape

Two extensions that meet a shared record at the middle:

- **Quintic from Guide** — select a drawn stroke, take six points off it, draw the
  quintic through them as cubic Béziers, and write the six exact control points in
  the shared format for Blender, GeoGebra and the curve-lab side.
- **Quintic sheet: place a curve** — read a curve from the shared sheet and put it
  on the canvas, with its six control points marked, so it can be worked on.

Operator's ask, 2026-11-26/27: "build this exact workflow right inside Inkscape",
"use industry best practice and follow what blender does with its control points",
then the split — "you as deep2 are working on the inkscape code, and deep1 can work
on the code from the curve lab side… but you have to work together on a shared data
structure".

## The three layers

| layer | what it is | how good it is |
|---|---|---|
| 1 the drawn curve | the freehand stroke, read from the selection | the reference |
| 2 the six-point curve | six points taken off it, and the quintic through them | the **drawn→quintic** miss, printed |
| 3 the quintic display | that curve as a C2 cubic chain, because SVG has no quintic | the **quintic→chain** miss **and its proved bound**, printed |

## The shared record

The contract is `workbench/quintic.schema.json`, format `curve-lab.quintic/1`,
written and owned by the curve-lab side. The extension **reads** it and **writes**
the same shape; it never writes the data file. The meanings, the one flip, the
known differences and the check command are in `state/QUINTIC-CONTRACT-int.md`.

What matters when reading a record: `points` is six control points, **y up**,
`frame.start.tangent = P1 − P0` and `frame.end.tangent = P5 − P4` (both forward),
and a join carries a measured residual or it is not a join.

Files:

| path | what it is |
|---|---|
| `inkscape/quintic-guide.inx`, `quintic_guide.py` | the drawing dialog (three tabs) |
| `inkscape/quintic-sheet.inx`, `quintic_sheet.py` | place a curve from the sheet |
| `inkscape/quintic_math.py` | the pipeline: Bernstein, exact solve, fits, the C2 chain, the proved bound, the exports |
| `inkscape/quintic_theory.py` | the analysis: seams, PH, offsets, knots, joins, the contract writer |
| `tests/test_quintic_math.py` | 46 tests |
| `scripts/quintic_report.py` | every number in this document |
| `scripts/quintic_contract.py` | the reader-side check of the format |
| `scripts/check_blender_quintic.py` | Blender's own evaluation of the exported span |
| `state/QUINTIC-CONTRACT-int.md` | this side of the contract |
| `state/PROBLEMS-quintic-guide-int.md` | the faults it has had |

Python, not TypeScript: an Inkscape extension must speak `inkex`, and inkex is
Python. The maths modules are inkex-free so they run under `.venv/bin/python` with
Inkscape closed.

## Install

```sh
cp inkscape/quintic-guide.inx inkscape/quintic_guide.py \
   inkscape/quintic-sheet.inx inkscape/quintic_sheet.py \
   ~/Library/"Application Support"/org.inkscape.Inkscape/config/inkscape/extensions/
```

- **Extensions → Curve Lab → Quintic from Guide**
- **Extensions → Curve Lab → Quintic sheet: place a curve**

The maths is read from this repository (`~/developer/curve-lab`, or
`$CURVE_LAB_ROOT`), so editing `quintic_math.py` needs no reinstall.

## Layer 2: the four ways to take six points

Blender's Bézier control points sit **on** the curve and the handles are computed,
so the point you place is a point the curve goes through. That is the default.

| mode | the six points | the curve |
|---|---|---|
| **On the curve, evenly spaced** (default) | on the stroke, at 0, .2, .4, .6, .8, 1 of its arc length | solved exactly through all six |
| **A best fit** | *not* on the stroke; least squares, then three parameter-correction passes | smallest total miss, ends pinned |
| **A cage: the guide's 6 nodes** | the six nodes of the guide path | the quintic's control points |
| **A cage from 6 samples** | the same six even points, used as control points | as above |

The solve through six points is exact: the Bernstein weights at t = k/5 are
rational, so the 6×6 system is solved in `Fraction` and only the answer becomes
decimals. The best fit is Piegl & Tiller ch. 9 with §9.4.2's parameter correction —
each sample moves onto its nearest point, then the fit repeats.

## Spans, and where to cut

A long stroke is not one quintic. **Spans** cuts it, and each stretch gets its own
six points, quintic and chain; spans meet C0 exactly at the cut. Measured on
2026-11-27 with `scripts/quintic_report.py` — miss from the drawn stroke to the
six-point curve, in px (max / rms):

| stroke | mode | 1 span | 2 | 3 | 4 | 6 |
|---|---|---|---|---|---|---|
| wild 400 px | on the curve | 46.087 / 20.519 | 16.776 / 4.397 | 6.435 / 0.975 | 3.414 / 0.505 | 0.522 / 0.098 |
| wild 400 px | best fit | 21.801 / 11.149 | 5.671 / 1.643 | 0.890 / 0.223 | 0.651 / 0.145 | 0.200 / 0.033 |
| freehand-like | on the curve | 26.004 / 10.664 | 2.848 / 0.790 | 1.225 / 0.264 | 0.666 / 0.169 | 0.210 / 0.044 |
| freehand-like | best fit | 11.623 / 6.359 | 1.567 / 0.579 | 0.419 / 0.107 | 0.228 / 0.075 | 0.070 / 0.021 |

- One span on a long stroke is a bad fit — 26 px to 46 px. Only a split fixes that.
- The best fit roughly halves the miss at equal span count.
- **Cutting at the sharpest bends was measured and is worse**: 3 spans, best fit,
  through the installed extension: even cuts 0.419 px (freehand) and 0.890 px
  (wild), curvature cuts 0.632 px and 1.365 px. Cutting at a bend makes one stretch
  longer in arc length, and a longer stretch is harder for six points. The option
  stays for loops, where arc length is a poor guide, and is **not** the default.

## The display chain, and its proved bound

The chain passes exactly through the quintic's stations, leaves and arrives on the
quintic's own end tangents, and is **C2** at every interior joint.

Its miss is measured **and** bounded. The bound is a proof, not a sample: split the
quintic at each station (de Casteljau, exact), raise each cubic to degree 5 (exact),
subtract — the difference is a Bézier, and a Bézier lies inside the convex hull of
its control points, so the largest difference coefficient is an upper bound. The
fit accepts a chain only when that bound is inside the tolerance.

| cubics | wild cage: bound / measured | gentle cage: bound / measured |
|---|---|---|
| 4 | 1.623 / 0.950 px | 0.039 / 0.024 px |
| 8 | 0.107 / 0.055 px | 0.00244 / 0.00152 px |
| 16 | 0.00683 / 0.00321 px | 0.000153 / 0.000095 px |

The bound runs 1.6–2.1× the measurement, which is the price of a proof the sampling
cannot produce. Tolerance 0.001 px needs 32 cubics on the wild cage, 16 on the
gentle one; a fit costs 22–186 ms.

## Fullness is tension

`P_i = (1 − α) · L_i + α · G_i`, where `L_i` is the straight chord at i/5 and `G_i`
is the drawn point. α = 1 keeps the drawn curve, α = 0 is the straight line, and the
ends never move. Because `P_1 − P_0` scales with α, this is the tangent length — the
same thing a Bézier handle length does in Blender.

## Seams, and what a join costs

Each span ends on its own stretch's tangent, so an unsmoothed cut is a corner:
10.6° on the test guide, 79.5° on a hard one. **Smooth the seams** moves only the two
control points next to each seam onto their shared bisector, keeping their lengths,
which makes the join **G1** and leaves every point the curve passes through alone.

A stroke that starts where it ends is a **loop**: the record says `closed: true`,
adds the signed `winding`, and the wrap from the last span back to the first is
smoothed and written as a join too. A two-span loop therefore carries two joins —
`0 -> 1` and `1 -> 0` — both measured at 0.000000°.

A smoothed join is written into the record with its measured residual — position gap,
tangent angle, curvature step, curvature-rate step. An unsmoothed seam writes **no
join at all**, because the schema has no word for C0 and a false `G1` is worse than
silence.

## No overshoot, or an honest number

A quintic through six points can balloon outside them: **1575 px** (even points) and
**480 px** (best fit) on a 400 px cage. **Clamp inside the six points** pulls the
control points into the six points' box, and the convex-hull property then keeps the
whole curve inside it — `OvershootTest` checks 1001 points. It costs miss (3 spans:
27.8 px clamped against 6.4 px not), so it is off by default and the run says which
happened.

## A cubic dressed as a quintic gets one cubic

68 of the 200 curves on DeepSeek1's sheet are degree 3 or lower — the parabola family
is exactly a quadratic. The chain tests the true degree from the forward differences
and starts at one cubic for those: the parabola draws as **one cubic at 0.0001 px**,
where the old code spent two.

## PH, and the offset that cannot be exact

A general quintic is **not** a Pythagorean-hodograph curve, so it has no exact
offset: `|B'(t)|` is the square root of a quartic. The extension decides this with
polynomial arithmetic in `Fraction` — x′² + y′² must be a perfect square, i.e.
`deg(gcd(p, p′)) = deg(p)/2` — and prints the answer: **0 of the 200 sheet curves
are PH**. That matters because this project's rails assume exact offsets.

For a non-PH curve the **Offset** export writes `<guide>-offset.json`: the offset
sampled along the exact normals and fitted with a C2 chain, with its measured miss
and its `exact: false`. It is a drawing of the offset, never a claim that it is
exact.

## What leaves Inkscape

| file | what it is |
|---|---|
| `<guide>-quintic.json` | **the contract**: `curve-lab.quintic/1`, six points per span, y up, frames, measured joins |
| `<guide>-report.json` | my numbers: proved bound, PH, cusps, true degree, overshoot — not part of the contract |
| `<guide>-blender.py` | one exact order-6 NURBS spline per span, `use_endpoint_u` |
| `<guide>-geogebra.txt` | `P0…P5` and `Q(t)`, or `S1_P0…`/`C1(t)` per span |
| `<guide>-offset.json` | the offset, with `exact: false` unless the curve is PH |

**One y flip, and it is named**: the document is y down, the record and both
external tools are y up. `qm.to_y_up` on the way out, `quintic_sheet.to_svg` on the
way in, each called once.

## Use

1. Draw the guide; leave it pale and dotted. Select it.
2. **Quintic from Guide** → Points tab: mode and spans; Display tab: keep Live
   preview ticked and drag **Fullness**; Export tab: a folder.
3. Apply. Run again with the same numbers and nothing is rewritten (inkex compares
   documents and skips an identical save).
4. To work on a sheet curve instead: **Quintic sheet: place a curve**, give the uid
   (`q6-parabola-01`), a scale and an origin.

## Checked by an independent evaluator

Blender is the independent one: `scripts/check_blender_quintic.py` hands the six
points to Blender 4.2.23 LTS, reads back the vertices of the order-6 clamped
NURBS, and compares them with the Bernstein sum computed here.

| control points | Blender vertices | largest deviation |
|---|---|---|
| the parabola arch (0,0 … 120,0) | 300 | **0.000016 px** |
| the wild cage | 300 | **0.000051 px** |

So "six points + `order_u = 6` + `use_endpoint_u` is one exact quintic span" is
measured against Blender's own evaluation, not only against our algebra.

## Checks

```sh
.venv/bin/python -m unittest tests.test_quintic_math            # 46 tests
.venv/bin/python scripts/quintic_report.py                      # every table here
.venv/bin/python scripts/quintic_contract.py <file> --extent-must-follow
.venv/bin/python scripts/check_blender_quintic.py               # Blender vs our algebra
node --test tests/js/quintic-data.test.ts                       # the shared test
```

## Limits, stated

- Inkscape draws cubics; the quintic is only ever the record plus a chain.
- Spans join C0 unless the seams are smoothed; smoothing moves the two interior
  control points at each seam and therefore changes the shape slightly.
- A non-PH curve has no exact offset, and no amount of arithmetic will make one.
- One guide per run: the first path in the selection is used.
- The sheet importer draws one curve at a time, by uid.
