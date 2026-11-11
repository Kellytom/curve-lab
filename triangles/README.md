# triangles/ — the alternative route to integer points on a Tschirnhausen PH curve

This directory is a **separate method**, kept apart on purpose. It is not the
`ph-families.html` method and it must not be folded into it.

## What it is for

The page method (`scripts/ph_families.py`, `workbench/ph-families.html`) takes a
PH curve, chooses milestones `t = k/m`, and multiplies the **whole curve** by one
scale `S` so those milestones become integers. The integer points that result
belong to one curve at one scale, and the scale grows with the degree.

This directory starts from the other end: **build the curve out of Pythagorean
triangles**, so the integer points are in the construction rather than bought
with a scale. Whatever is proved here should stand on its own: same inputs, same
numbers, no reliance on the page.

## The boundary — read this before editing

- **Nothing here imports from `scripts/ph_families.py` or
  `curve_lab/ph_hermite.py`**, and neither of those imports anything here. If a
  shared helper is genuinely needed, it moves to `curve_lab/` as its own module
  and both sides import that; neither side reaches into the other.
- **No edits to `workbench/ph-families.html`** from this directory. If this
  method earns a page, it gets its own, built by a generator that lives **in
  this directory**.
- **Tests live here too** (`tests_triangles/`), so a failure names the method.
- The page's vocabulary stays as it is: *milestone* for `t = k/m`, *PPH* for
  piecewise PH, and no use of `PHH` (the literature's PHH is the H-Bézier
  approximation). This directory inherits that vocabulary rather than inventing
  a second one.
- If the two methods ever disagree about a number, that is a finding, not a bug
  to paper over: record both and why.

## The shapes already known

The alpha the page draws is `18y² = x(x−6)²`, with integer points
`(18k², ±6k(3k²−1))` plus the node `(6,0)`. At `h = 3` the same curve has
integer controls `(0,0), (0,2), (2,4), (6,4)` and ten lattice points in
`t ∈ [−4,4]`.

The Pythagorean integer cubic family (`curve_lab/pyth_cubic.py`) already builds
cubics from triples: `P₀=(0,0)`, `P₁=(a,−b)`, `P₂=(2c−a,b)`, `P₃=(2c,0)`, with
`a²+b²=c²`. It is exact and integer but **not PH** — the name is the control
triple, not the hodograph. Any claim that a triangle construction gives a PH
curve has to show the hodograph condition `x'² + y'² = σ²`, not assume it.

## Where to start

Not decided here. The first job in a fresh session is to write down, in this
file, the exact rule the method follows, then prove it on one curve before
scaling it to the rest.
