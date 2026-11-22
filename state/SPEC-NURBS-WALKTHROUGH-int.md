# SPEC-NURBS-WALKTHROUGH-int — one curve, the whole process, back to the registry

> **draft A** — the walkthrough for `c-0059 lace-1of10-3-2` (degree 11,
> 11 crossings). The Python code is the prototype for the full pipeline.

## The curve

    uid      c-0059
    name     lace-1of10-3-2
    speedX   [3, -16, 16, 0, 0, 0]
    speedY   [-9, 154, -808, 1872, -2000, 800]
    degree   11 (position)
    crossings 11

The speed rows are the recipe: one mirror pair at 1/10, a second pair at
1/3, and a root stack of 2 at ½. The position polynomial is their integral:
x(t) = ∫(u²−v²), y(t) = ∫2uv, degree 11.

## The process, in eight steps

| step | what happens | what's exact |
|---|---|---|
| 1 | read the speed rows | exact |
| 2 | build the position polynomial (integral of the squared rows) | exact |
| 3 | convert power → Bernstein (the NURBS basis change) | exact |
| 4 | write the SVG: the cubic spans as path data, the NURBS as metadata | the metadata is exact |
| 5 | Inkscape: the operator edits the cubic nodes | the edited cubics are exact |
| 6 | the extension reads the edited cubics back | exact |
| 7 | re-fit speed rows to the edited curve (a PH approximation) | fitted, miss stated |
| 8 | write the variant record to the registry | the record is exact for the fitted curve |

## The miss, defined

After step 5, the curve is whatever the operator drew. The reconstructed
speed rows (step 7) describe the closest PH curve to that drawing. The miss
between them is measured as a share of the curve's bounding-box diagonal and
printed beside the figure. If the miss is under the dial (0.05 % of size),
the variant is real. If not, the edit moved too far from PH and the desk
says so.

## The NURBS object, defined

    NurbsCurve(degree=11)
      control_points: [(Fraction, Fraction) × 12]   ← the Bernstein coefficients
      weights:        [Fraction(1)] × 12             ← all 1 (a polynomial)
      knot_vector:    [0, 0, …, 0, 1, 1, …, 1]      ← a Bézier piece (no interior knots)

The basis change from the power form is a lower-triangular solve (the
Bernstein coefficients of a power polynomial are unique and exact in
Fraction).

## The PH re-fit, defined

After the operator edits the cubic spans, the derivative of the edited
curve is a piecewise polynomial (x′, y′). The PH re-fit finds u(t), v(t) of
degree ≤ 5 such that the reconstructed curve is close to the edited curve.
The algorithm: sample the edited curve's tangent angle θ(t) and speed
σ(t), then solve for u and v from the PH equations:

    u² − v² = x′·σ(t)
    2uv     = y′·σ(t)

The σ(t) that makes the system solvable is the one where (u²+v²)² = the
sum of squares of the derivative — a nonlinear condition that is solved
numerically on the sample grid. The result is a PH approximation of the
edited curve, with the miss stated.

## What goes back to the registry

A variant record (the same naming rule as the reduction pipeline):

    name:              lace-1of10-3-2-edited
    params.variantOf:  c-0059
    reducedFrom:       the edited cubic spans (the Inkscape edit)
    reducedDegree:     11
    maxMiss:           <the reconstruction miss, share of size>
    speedX:            <the re-fitted speed rows>
    speedY:            <the re-fitted speed rows>

The sandbox can iterate it; the rails can be built; the clearance rule can
measure it. The full machinery works because the curve has speed rows
again.
