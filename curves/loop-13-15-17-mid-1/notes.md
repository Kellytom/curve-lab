# loop-13-15-17-mid-1

**In one line.** A curve whose speed is the polynomial below; 6 self-crossings,
grid 1/36, arc 76048320.3611.

## The formula

The speed is a complex polynomial, and the curve is its square, integrated:

```
w(t) = p(t) + i q(t)
z(t) = integral of w(t)^2 dt = integral of (p^2 - q^2) + i(2 p q) dt
```

```
p(t) = 1
q(t) = - 2688 + 134984t^1 - 2461298t^2 + 19538337t^3 - 65308495t^4 + 103047973t^5 - 76924575t^6 + 21978450t^7
```

Nothing here is sampled or fitted: the numbers are whole, so the arc length is a
polynomial integral and is exact.

## The variables

| symbol | meaning | value |
|---|---|---|
| `t` | the parameter, 0 at the start and 1 at the end | 0 to 1 |
| flat spots | where the tangent is horizontal, `q(t) = 0` | 1/13, 1/15, 1/17, 1/2, 16/17, 14/15, 12/13 |
| `bend` | arc length over the straight distance between the ends | no value: the two ends land on the same point |
| `grid` | the pitch the whole rows need: 1 over this number | 1/36 |
| self-crossings | how many times the stroke meets itself | 6 |
| loop | the part of `t` that holds the knot | t 0.0366 to 0.9624 |
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
