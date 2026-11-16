# loop-12-15-18-mid-1

**In one line.** A curve whose speed is the polynomial below; 6 self-crossings,
grid 1/66, arc 66596891.5606.

## The formula

The speed is a complex polynomial, and the curve is its square, integrated:

```
w(t) = p(t) + i q(t)
z(t) = integral of w(t)^2 dt = integral of (p^2 - q^2) + i(2 p q) dt
```

```
p(t) = 1
q(t) = - 2618 + 131479t^1 - 2384613t^2 + 18773622t^3 - 62517420t^4 + 98490168t^5 - 73483200t^6 + 20995200t^7
```

Nothing here is sampled or fitted: the numbers are whole, so the arc length is a
polynomial integral and is exact.

## The variables

| symbol | meaning | value |
|---|---|---|
| `t` | the parameter, 0 at the start and 1 at the end | 0 to 1 |
| flat spots | where the tangent is horizontal, `q(t) = 0` | 1/12, 1/15, 1/18, 1/2, 17/18, 14/15, 11/12 |
| `bend` | arc length over the straight distance between the ends | no value: the two ends land on the same point |
| `grid` | the pitch the whole rows need: 1 over this number | 1/66 |
| self-crossings | how many times the stroke meets itself | 6 |
| loop | the part of `t` that holds the knot | t 0.0337 to 0.9653 |
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
