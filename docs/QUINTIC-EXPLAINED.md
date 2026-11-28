# The quintic in Inkscape, explained

A quintic is one smooth curve through six points. This page takes it from "what am I
looking at" to the parts an expert will ask about: the shared record, the measured
miss, and the claim that two joined cubics can hide a quintic — which is false, and
this page shows why with numbers.

Everything here is built and running. The extension is
`inkscape/quintic-guide.inx` + `quintic_guide.py`, the maths is
`inkscape/quintic_math.py`, and the user reference is
[`docs/QUINTIC-GUIDE.md`](QUINTIC-GUIDE.md).

## Part 1 — the beginner's walkthrough

### What you are making

You draw a stroke. The extension puts **six points** on it, then draws the one
quintic curve that those six points describe. The six points stay exact: they are the
curve, in the same way that four points are a cubic. The line you see on the canvas
is a chain of **cubics** that follows the quintic; it is a drawing of the curve, not
the curve itself.

Three layers, top to bottom:

1. **the drawn stroke** — your hand, the trackball, the shape you want;
2. **the six-point quintic** — the exact curve fitted to the stroke;
3. **the cubic chain** — what SVG can store and Inkscape can draw.

Both gaps are measured and printed: stroke → quintic, and quintic → chain. Nothing
on the page claims more than the measurement.

### The one dial: fullness

The six points are `G0 … G5`. Fullness, `α`, decides how far the inner four points
are pulled from the straight chord towards your drawn points:

> `Pi = (1 − α)·Li + α·Gi`, where `Li` is the same point on the straight line from
> the first point to the last.

In words: **α = 1 keeps your drawn shape, α = 0 collapses the curve to a straight
line, and the two ends never move.** That is the slider to drag with Live preview
ticked.

### Step by step

1. **Install once.** In the repo:

   ```sh
   sh scripts/install_inkscape_quintic.sh
   ```

   Restart Inkscape. Two entries appear under **Extensions → Curve Lab**.

2. **Draw a pale guide.** Any path: a freehand stroke, or a path built node by node.
   Make it the shape you want, not a sketch of it. Pale and dotted helps, because the
   inner curve is drawn on top.

3. **Select the guide**, then **Extensions → Curve Lab → Quintic from Guide**.

4. **Points tab.** Choose where the six points come from:
   *On the curve, evenly spaced* (start here), *A best fit*, or one of the two cage
   modes. Leave **Spans** at 1 for a short stroke; a long stroke needs 2–4. Leave the
   cut at **Equal arc length**.

5. **Display tab.** **Fullness** 1, **Cubic segments** 0 (fit to tolerance),
   **Mark the six points** on. Tick **Live preview** in the dialog if it is not
   already ticked, then drag fullness and watch the curve change.

6. **Read the label.** Under the curve you get one line:
   `N spans, M cubics, miss X px, bound Y px`. *Miss* is the measured distance from
   your stroke to the quintic. *Bound* is the proved limit on how far the cubic chain
   can be from the quintic — a bound, so it is always at or above the true error.
   If the miss is too big for the job, raise Spans and apply again.

7. **Apply.** You get the inner curve, a small ring on each of the six points, and
   the label. The guide stays where you put it. Running again with the same settings
   replaces the curve instead of stacking a copy.

8. **Export tab.** Give an **Export folder** and you get three files next to it:
   `<guide>-quintic.json` (the shared record), `<guide>-blender.py`,
   `<guide>-geogebra.txt`. Only the six exact points leave — never the cubic drawing.

9. **Bring a curve back.** **Extensions → Curve Lab → Quintic sheet: place a curve**
   asks for a uid (for example `q6-trefoil-10`) and places that curve from the shared
   sheet, with its six points marked.

### What each control does

| control | in one line |
|---|---|
| Six points are | where the six points come from: on the stroke, a best fit, or the guide's own nodes |
| Spans | how many quintics the stroke becomes; one quintic per span |
| Fullness | tension from 1 (your shape) to 0 (straight chord); ends fixed |
| Cubic segments | how many cubics draw each quintic; 0 fits to the tolerance |
| Tolerance | the largest allowed quintic-to-chain miss, in px |
| Smooth the seams | forces C1 across spans |
| Clamp inside the six points | forbids the curve leaving the control polygon |
| Mark / label / keep guide | the marks, the measured line, the pale guide |
| Export folder | where the three files are written; blank writes nothing |
| Copy the six points | puts them on the clipboard instead |
| Also write the offset | writes an offset curve, marked approximate unless the curve is PH |

### Why Inkscape shows cubics

SVG has no quintic element. A path holds lines, cubics (three control points per
span) and arcs. So the extension keeps the six points in the sidecar file and fits a
**C2 cubic chain** — two cubics share a node and a tangent, with the second
derivative matched as well — through stations on the quintic. The chain is the
display; the six points are the curve.

Could this be a live path effect instead? An Inkscape live effect is a compiled
effect, and a Python `inkex` extension cannot register one. The built route is the
dialog with **Live preview**: every control change re-runs the extension and redraws.
For this job it feels the same, and it needs no compiled component.

### What leaves the file

- **`<guide>-quintic.json`** — the shared record `curve-lab.quintic/1`,
  `format/quintic.schema.json`. The six points go in with **y up** (SVG's y is down;
  the writer flips once and says so), each span carries its start and end frames
  (point, tangent, curvature, rate), and the joins carry their measured residual.
- **`<guide>-blender.py`** — paste into Blender's Text Editor and run. One exact
  order-6 NURBS spline per span, `use_endpoint_u = True`, six points. Blender's
  `order_u` is clamped to the point count quietly, so six points with order 6 is the
  only exact quintic span.
- **`<guide>-geogebra.txt`** — one command per line for GeoGebra's Input Bar: the
  six points as `P0 … P5`, then the Bernstein form of the curve,
  `Q(t) = (1−t)⁵P0 + 5t(1−t)⁴P1 + 10t²(1−t)³P2 + 10t³(1−t)²P3 + 5t⁴(1−t)P4 + t⁵P5`.

Both export files are y up, so the flip happens once in the writer and neither
application needs a second one.

### How to tell it worked

- The label is present and its miss is small for your job.
- Six rings sit on the curve, and the curve passes through them in the on-the-curve
  mode.
- A repeat run with the same settings replaces, not duplicates.
- The export folder holds the three files, and the JSON passes the strict check
  (next part).

## Part 2 — the expert part

### The record, and the one open contract question

The record is `curve-lab.quintic/1`; `scripts/check_quintic_contract.py` is the
check. On this side it passes `--strict` on my exports. On the shared sheet it fails
on three envelope keys:

```sh
.venv/bin/python scripts/check_quintic_contract.py workbench/quintic-guides.json --strict
# FAIL ... keys the schema does not allow: note, order, worstApproximationError
```

`workbench/quintic-guides.json` belongs to the curve-lab side, so the choice is
theirs: drop the keys, or make `order` the integer 6 and move the point names to
`labels`. The open question that goes with it: the sheet's `worstApproximationError`
(0.1182) is recorded without the span count it was measured at, so it cannot be
compared with my numbers until the count and the measure (max distance or station
sample) are named.

### What is measured

The block below is computed by `scripts/quintic_explained.py` from the sheet with
the extension's own maths. It is regenerated, not typed: `--check` fails when the
page and the numbers disagree.

<!-- numbers:start -->

| curve on the sheet | 1 span | 2 spans | 3 spans | 4 spans | 6 spans | C3 jump at the seam, 2 spans (px) | worst recovered point (px) |
|---|---|---|---|---|---|---|---|
| `q6-flattened-arch-10` | 40.4 | 4.0 | 0.864 | 0.273 | 0.054 | 280.0 | 12.1 |
| `q6-parabola-01` | 0.000065 | 0.000033 | 0.000022 | 0.000016 | 0.000011 | 0 | 0 |

Measured in the sheet's own units (the cages are in px) by `scripts/quintic_explained.py`, which calls the extension's `quintic_math.py`. The last two columns test the "hidden quintic" claim: the seam jump is the difference between the two cubics' third derivatives at the shared node, and the recovered point is the worst of the six points a naive recovery gets back from the two-cubic chain.

<!-- numbers:end -->

Read the rows as follows. One span is a bad fit on a wild curve and a long one needs
more; the chain is measured against the quintic, not against the stroke. The parabola
row is the exact case: a quadratic is a cubic, so its numbers are floating-point
zeros (below 0.0001 px). The two right-hand columns test the "two cubics hide a
quintic" claim, next.

### Two cubics do not hide a general quintic

The claim is that two joined cubics with **C3 continuity** at the shared node are a
single quintic Bézier in disguise. It is false, and the reason is one line:

> A cubic's third derivative is **constant**. If two cubics share their third
> derivative at a node, they share it everywhere, so the joined curve has a constant
> third derivative — and a curve whose third derivative is constant is **one cubic**,
> not a quintic.

So the C3 test finds a degree-elevated cubic. That is still a useful thing to detect
(a curve that *is* a cubic but is stored with more control points), but it is not a
hidden quintic: the quintic's third derivative changes along the curve, and no pair
of cubics can reproduce that.

The table makes the size of the gap concrete: on the flattened arch, the
third-derivative jump at the seam of the 2-span chain is 280 px per unit `t³`, while
that same chain is still 4.0 px away from the quintic it is meant to follow. The two
cubics are not a hidden quintic; they are a visible approximation of one.

What that means for a reverse-engineering script:

- **A least-squares recovery always returns a quintic.** Twelve numbers in, six
  control points out; the fit is well defined.
- **The recovery is exact only when the cubics came from a quintic's halves** — which
  happens when the quintic is a degree-elevated cubic (the parabola row is the clean
  case). Otherwise it returns the closest quintic, and the residual says how far it
  is.
- **The chain is not the curve.** Recovering a quintic from an SVG chain recovers the
  chain's best quintic, not the one that was drawn. That is why the extension writes
  the six points to the sidecar at the moment it draws: the exact values never have
  to be reconstructed from the drawing.

### Fullness is not recoverable from the curve alone

`α` is defined against the guide: `Pi = (1−α)Li + αGi`. Without `Gi` it is not
identifiable — halve the guide's height and double `α` and the six inner points do
not move. Keep the guide in the file, or the guide convention, if `α` has to survive
a round trip. Given both, `α` follows per point:
`α = |Pi − Li| / |Gi − Li|`.

### Offsets and PH

The offset export is marked `exact: false` because it is approximate: none of the
sheet's 200 curves is a Pythagorean-hodograph curve. PH is the property that would
give an exact offset, and it is decided here in exact polynomial arithmetic, not by
sampling.

### What is proved, and what is still the operator's step

- **Installed and run from the installed path.** `sh scripts/install_inkscape_quintic.sh`
  copies both `.inx` files and both scripts; run headless from that folder, the
  extension wrote the record, the report, the Blender file and the GeoGebra file, and
  `scripts/check_quintic_contract.py --strict` passed on the record.
- **Blender (4.2.23 LTS) has read the export.** Running the generated script in
  `blender -b` created one spline with `order_u = 6`, 6 points and
  `use_endpoint_u = True`: an exact order-6 NURBS quintic. That is Blender's own
  report, not a claim from a file reader.
- **GeoGebra has not seen the commands.** No GeoGebra app is installed on this
  machine, so the `-geogebra.txt` lines are checked as text only. Paste them into the
  Input Bar once to close that gap.
- **The GUI has not been driven.** The dialog has only been run headless. Open a
  drawn stroke, run **Extensions → Curve Lab → Quintic from Guide**, tick Live
  preview and drag Fullness once. One minute of clicking is the remaining proof.
- Nothing is pushed this session.

---

*Files: `docs/QUINTIC-EXPLAINED.md` (this page), `docs/quintic-explained.html` (its
twin), `scripts/quintic_explained.py` (numbers and twin), `inkscape/quintic_math.py`
(the maths), `docs/QUINTIC-GUIDE.md` (the user reference).*
