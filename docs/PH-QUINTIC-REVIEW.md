# PH quintics: where the work stands

A senior review of the PH quintic work: the result, what is solid, what is not,
and the plan for the next level - finding every integer hit once a curve is
chosen.

Live page: `workbench/ph-quintic-gallery.html` (figures Q1-Q13).

## 1. The result

The work has a closed-form account of the PH quintic, and it is correct.

Write the speed path in the centred frame, `h = t - 1/2`:

```
w(h) = speedMid + slopeMid*h + curvatureMid*h^2
speedMid     = w(1/2)
slopeMid     = w'(1/2)
curvatureMid = w''(1/2)/2
```

Then, exactly:

```
arc   = |speedMid|^2 + (|slopeMid|^2 + 2 speedMid.curvatureMid)/12 + |curvatureMid|^2/80
chord = speedMid^2 + (2 speedMid*curvatureMid + slopeMid^2)/12 + curvatureMid^2/80
bend  = arc / |chord|
```

The weights `1, 1/12, 1/80` are the integrals of `1, h^2, h^4` over
`[-1/2, 1/2]`. The chord is a sum of three complex vectors, so the bend is large
exactly when they cancel.

With `slopeMid = 0` the three directions are locked to `0, phi, 2phi` and the
lengths to `1, x/6, x^2/80`, where `x = |curvatureMid|/|speedMid|`. That gives a
short dictionary of classic shapes:

| shape | condition | numbers |
|---|---|---|
| first and middle terms equal legs | length(T1) = length(T2) | `x = 6` |
| first and third terms equal legs | length(T1) = length(T3) | `x = 4*sqrt(5)` |
| middle and third terms equal legs | length(T2) = length(T3) | `x = 40/3` |
| right angle, first to middle | `phi = 90 deg` | any `x` |
| right angle, first to third | `phi = 45 deg` | any `x` |
| the triangle closes | `chord = 0` | `x = 4*sqrt(5)`, `phi = 138.19 deg` |

The closure is exact: `chord = speedMid^2 (1 + ratio/6 + ratio^2/80)` with
`ratio = curvatureMid/speedMid`, which vanishes at
`ratio = -20/3 +/- (8*sqrt(5)/3) i`, i.e. `|ratio| = 4*sqrt(5) ~ 8.94` at
`curvatureAngle = 138.19 deg`.

The formula also inverts. Given the three chord terms:

```
speedMid     = sqrt(T1)
curvatureMid = sqrt(80*T3)
slopeMid     = sqrt(12*T2 - 2 speedMid*curvatureMid)
```

Each square root has two signs, so one diagram gives up to eight curves -
mirrors and rotations of one shape. This is the design tool: draw the diagram,
solve for the recipe.

## 2. What is solid

- **Exactness is the house rule.** Recipes are stored as exact fractions, never
  as decimals, and the pitch is the lcm of the integrated coefficients'
  denominators. A decimal like 1.5 costs pitch; the JSON records the cost.
- **Pages are generated.** Nothing on the gallery is hand-drawn; the board and
  the sheets are built from the case tables.
- **Naming is now written down** (`AGENTS.md`): camelCase in JavaScript, kebab
  ids prefixed by figure, snake_case in Python, and every maths symbol gets a
  searchable name.
- **The data files are tested.** 16 presets, 10 saved curves, and the numbers
  are checked against the generator.
- **The maths has been verified twice**, independently, in Python and in
  JavaScript, on every preset.

## 3. Defects, in priority order

### 3.1 The exact formula lives only in JavaScript

The page states that the three lines reproduce every preset to within 1e-4, but
`scripts/ph_quintic_presets.py` still computes `bend_ratio` by sampling 800
points. The JSON is therefore approximate while advertising exactness, and the
formula cannot be reused by a test, a script, or the integer-hit work.

Fix: one `exact_bend(u, v)` in the library, used by the presets, the saved-curve
cleaner and the page generator.

### 3.2 Four JavaScript implementations of the same maths

`workbench/ph-quintic-gallery.html` carries six `<script>` blocks, 22 copies of
`evalQuadratic` and six pitch implementations. They have already drifted: Q8 has
12 preset buttons, the preset JSON has 16 presets.

Fix: one `workbench/js/ph-panels.js` with `metrics`, `drawCurve`,
`buildPanel`, `chordTerms`; each figure becomes a config object.

### 3.3 The generator is 1647 lines and its JavaScript is untested

Prose, Python and JavaScript live in one string, so a `replace` can break a
panel. It has: Q7 lost its sliders once, and `mTop` leaked into Q7 once. Neither
was caught by a test.

Fix: split data from template, and add one headless check that loads the page
and asserts the six readouts (`1.15`, `5.58`, `2.00`, `1.91`, `2.04`, `2.00`).
That is twenty lines and it would have caught both breaks.

### 3.4 Floats leak into exact arithmetic

`Fraction(0.2)` is the exact binary fraction. It produced a pitch of `1.6e33`,
then `9.3e107` in saved curves. Both were fixed by rounding, in two different
places.

Fix: one `to_fraction(value, max_decimals=6)` that refuses silent binary noise,
and a test that `Fraction(float)` appears nowhere else.

### 3.5 The saved-curve loop is not closed

Saved curves live in `localStorage`; the operator must paste JSON back, and then
a script cleans it. A small merge step would close the loop: read the clipboard
or a dropped file, clean it, append to the preset JSON.

### 3.6 The page is 664 KB

Inline SVG for 48 thumbnails. Fine locally, heavy for a deploy. Not urgent.

## 4. The next level: integer hits

Given a chosen curve `r(t) = x(t) + i y(t)` with rational coefficients, find
every lattice point it passes through. Three methods, and they are not
equivalent.

### 4.1 The pitch stops - fast, not complete

Sample at `t = m/pitch`. Exact at those stops, `O(pitch)`, and they are the
canonical grid. But they miss hits: for `x = t`, `y = t^2` the pitch is 1 and
the integer points are at every integer `t`; the stops see only `t = 0, 1`.

### 4.2 The exact method - complete

For each lattice point `(X, Y)` in the bounding box, compute
`gcd(x(t) - X, y(t) - Y)` over the rationals. A non-constant gcd means the point
is on the curve, and its roots give the parameters - rational or algebraic. The
box is a few hundred wide and the polynomials are degree 5, so this is cheap and
complete.

### 4.3 The midpoint method - a different question

Sample at cell centres, `t = (2m+1)/(2*pitch)`, and measure the distance to the
nearest lattice point. That is a near-miss report: how close the curve comes to
the grid between stops. It is not a hit list.

### 4.4 The API

```
hits_at_stops(u, v)        # O(pitch), exact, the canonical grid
hits_exact(u, v, box)      # bounding box + polynomial gcd, complete
near_misses(u, v, box)     # midpoint: distance to the nearest lattice point
```

Tests: the pick must give `(15, 4)` at pitch 10; a curve with a hit off the
stops must find it; a curve with none must return none.

## 5. Plan

1. **Done.** `exact_bend` in the library, at any degree; the presets use it
   (`scripts/ph_quintic_metrics.py`, nine tests).
2. **Done.** A headless page check with the six readouts
   (`scripts/check-ph-page.mjs`); it caught a class collision on its first run.
3. **Done.** `to_fraction` and its test, in the metrics module.
4. **Done.** `scripts/ph_quintic_hits.py` - the stops, the exact gcd method and
   the near misses, with nine tests.
5. **Done.** One implementation of the pitch, bend, inflection and closest
   (`recipeMetrics`); the panels read it.
6. **Done.** The panel JavaScript is `scripts/ph_panels.js`, the preset rows
   come from the JSON, a browser save merges with `--from`, and the generator
   is down from 1647 to 823 lines.
7. **Done.** Q14 takes any degree: two coefficient lists in, curve, exact
   metrics and the numeric hits out. The metrics are degree-agnostic in the
   page too (one Horner evaluator and `exactBend`). Mixed-degree lists pad to
   the longer one - a bug that both languages had.

The first four were the ones the degree-7 work depends on: exact metrics,
integer hits, a fraction guard and a check that notices a broken panel.
