# lace-1of8-1of6-3

**In one line.** A curve whose speed is the polynomial below; 4 self-crossings,
grid 1/5005, arc 56.3443.

## The formula

The speed is a complex polynomial, and the curve is its square, integrated:

```
w(t) = p(t) + i q(t)
z(t) = integral of w(t)^2 dt = integral of (p^2 - q^2) + i(2 p q) dt
```

```
p(t) = 6 - 36t^1 + 36t^2
q(t) = - 35 + 782t^1 - 6728t^2 + 29008t^3 - 69040t^4 + 92128t^5 - 64512t^6 + 18432t^7
```

Nothing here is sampled or fitted: the numbers are whole, so the arc length is a
polynomial integral and is exact.

## The variables

| symbol | meaning | value |
|---|---|---|
| `t` | the parameter, 0 at the start and 1 at the end | 0 to 1 |
| flat spots | where the tangent is horizontal, `q(t) = 0` | 1/8, 1/6, 1/2, 1/2, 1/2, 5/6, 7/8 |
| `bend` | arc length over the straight distance between the ends | 1.343 |
| `grid` | the pitch the whole rows need: 1 over this number | 1/5005 |
| self-crossings | how many times the stroke meets itself | 4 |
| loop | the part of `t` that holds the knot | t 0.021 to 0.978 |
| step | the power step of the rows: 1 is whole powers | 1 |

## How it was found

workbench/found-curves.json; new batch

## The figure

`figure.png` is **figure 1 as the page draws it**: the primary curve's own plot, captured with
`node scripts/curve_png.mjs curves/<slug>/curve.json curves/<slug>/figure.png 900`. Nothing is
re-drawn or re-fitted here, so the folder and the page cannot disagree.

If this row is one the page cannot draw faithfully — a large row collapses to a flat line —
the picture says so by being empty, and the numbers above are still exact. The factored
drawing, which does not have that problem, is kept beside it as `figure-exact.png`.
