# loop-5-12-mid-3

**In one line.** A curve whose speed is the polynomial below; 7 self-crossings,
grid 1/42, arc 68.0714.

## The formula

The speed is a complex polynomial, and the curve is its square, integrated:

```
w(t) = p(t) + i q(t)
z(t) = integral of w(t)^2 dt = integral of (p^2 - q^2) + i(2 p q) dt
```

```
p(t) = 1
q(t) = - 44 + 1115t^1 - 10085t^2 + 44470t^3 - 107020t^4 + 143608t^5 - 100800t^6 + 28800t^7
```

Nothing here is sampled or fitted: the numbers are whole, so the arc length is a
polynomial integral and is exact.

## The variables

| symbol | meaning | value |
|---|---|---|
| `t` | the parameter, 0 at the start and 1 at the end | 0 to 1 |
| flat spots | where the tangent is horizontal, `q(t) = 0` | 1/5, 1/12, 1/2, 1/2, 1/2, 11/12, 4/5 |
| `bend` | arc length over the straight distance between the ends | no value: the two ends land on the same point |
| `grid` | the pitch the whole rows need: 1 over this number | 1/42 |
| self-crossings | how many times the stroke meets itself | 7 |
| loop | the part of `t` that holds the knot | t 0.0513 to 0.9477 |
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
