# wave-1of8-2of5-3

> **draft A** — a working draft, not a final text.
**In one line.** A curve whose speed is the polynomial below; 1 self-crossings,
grid 1/3003, arc 92.7566.

## The formula

The speed is a complex polynomial, and the curve is its square, integrated:

```
w(t) = p(t) + i q(t)
z(t) = integral of w(t)^2 dt = integral of (p^2 - q^2) + i(2 p q) dt
```

```
p(t) = 7 - 25t^1 + 25t^2
q(t) = - 42 + 811t^1 - 6017t^2 + 23198t^3 - 51180t^4 + 65272t^5 - 44800t^6 + 12800t^7
```

Nothing here is sampled or fitted: the numbers are whole, so the arc length is a
polynomial integral and is exact.

## The variables

| symbol | meaning | value |
|---|---|---|
| `t` | the parameter, 0 at the start and 1 at the end | 0 to 1 |
| flat spots | where the tangent is horizontal, `q(t) = 0` | 1/8, 2/5, 1/2, 1/2, 1/2, 3/5, 7/8 |
| `bend` | arc length over the straight distance between the ends | 1.33 |
| `grid` | the pitch the whole rows need: 1 over this number | 1/3003 |
| self-crossings | how many times the stroke meets itself | 1 |
| loop | the part of `t` that holds the knot | t 0.0279 to 0.9712 |
| step | the power step of the rows: 1 is whole powers | 1 |

## How it was found

workbench/found-curves.json; new batch

## The figure

`figure.png` is drawn by the page itself (`scripts/curve_png.mjs`), in the view
recorded in `curve.json`. Where a large row collapses to a flat line,
`figure-exact.png` holds the factored drawing. If the picture and the numbers
ever disagree, the numbers are right and the figure is stale — regenerate it
rather than trust it.
