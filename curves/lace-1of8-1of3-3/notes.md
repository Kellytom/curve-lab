# lace-1of8-1of3-3

**In one line.** A curve whose speed is the polynomial below; 4 self-crossings,
grid 1/2730, arc 10.4114.

## The formula

The speed is a complex polynomial, and the curve is its square, integrated:

```
w(t) = p(t) + i q(t)
z(t) = integral of w(t)^2 dt = integral of (p^2 - q^2) + i(2 p q) dt
```

```
p(t) = 3 - 16t^1 + 16t^2
q(t) = - 14 + 275t^1 - 2081t^2 + 8158t^3 - 18220t^4 + 23416t^5 - 16128t^6 + 4608t^7
```

Nothing here is sampled or fitted: the numbers are whole, so the arc length is a
polynomial integral and is exact.

## The variables

| symbol | meaning | value |
|---|---|---|
| `t` | the parameter, 0 at the start and 1 at the end | 0 to 1 |
| flat spots | where the tangent is horizontal, `q(t) = 0` | 1/8, 1/3, 1/2, 1/2, 1/2, 2/3, 7/8 |
| `bend` | arc length over the straight distance between the ends | 1.418 |
| `grid` | the pitch the whole rows need: 1 over this number | 1/2730 |
| self-crossings | how many times the stroke meets itself | 4 |
| loop | the part of `t` that holds the knot | t 0.0249 to 0.9741 |
| step | the power step of the rows: 1 is whole powers | 1 |

## How it was found

workbench/found-curves.json; new batch

## The figure

`figure.png` is drawn by the page itself (`scripts/curve_png.mjs`), in the loop view:
the middle of `t`, framed on the knot. If the picture and the numbers ever disagree, the
numbers are right and the figure is stale — regenerate it rather than trust it.
