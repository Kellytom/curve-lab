# loop-3-8-13-mid-1

> **draft A** — a working draft, not a final text.
**In one line.** A curve whose speed is the polynomial below; 7 self-crossings,
grid 1/90, arc 893.8778.

## The formula

The speed is a complex polynomial, and the curve is its square, integrated:

```
w(t) = p(t) + i q(t)
z(t) = integral of w(t)^2 dt = integral of (p^2 - q^2) + i(2 p q) dt
```

```
p(t) = 1
q(t) = - 168 + 4994t^1 - 53165t^2 + 263424t^3 - 682675t^4 + 954478t^5 - 681408t^6 + 194688t^7
```

Nothing here is sampled or fitted: the numbers are whole, so the arc length is a
polynomial integral and is exact.

## The variables

| symbol | meaning | value |
|---|---|---|
| `t` | the parameter, 0 at the start and 1 at the end | 0 to 1 |
| flat spots | where the tangent is horizontal, `q(t) = 0` | 1/3, 1/8, 1/13, 1/2, 12/13, 7/8, 2/3 |
| `bend` | arc length over the straight distance between the ends | no value: the two ends land on the same point |
| `grid` | the pitch the whole rows need: 1 over this number | 1/90 |
| self-crossings | how many times the stroke meets itself | 7 |
| loop | the part of `t` that holds the knot | t 0.0523 to 0.9468 |
| step | the power step of the rows: 1 is whole powers | 1 |

## How it was found

family-census.json; see scripts/family_census.py for the box

## The figure

`figure.png` is **figure 1 as the page draws it**: the primary curve's own plot, captured with
`node scripts/curve_png.mjs curves/<slug>/curve.json curves/<slug>/figure.png 900`. Nothing is
re-drawn or re-fitted here, so the folder and the page cannot disagree.

If this row is one the page cannot draw faithfully — a large row collapses to a flat line —
the picture says so by being empty, and the numbers above are still exact. The factored
drawing, which does not have that problem, is kept beside it as `figure-exact.png`.
