# lace-1of10-1of5-3

**In one line.** A curve whose speed is the polynomial below; 4 self-crossings,
grid 1/273, arc 55.7582.

## The formula

The speed is a complex polynomial, and the curve is its square, integrated:

```
w(t) = p(t) + i q(t)
z(t) = integral of w(t)^2 dt = integral of (p^2 - q^2) + i(2 p q) dt
```

```
p(t) = 6 - 25t^1 + 25t^2
q(t) = - 36 + 841t^1 - 7307t^2 + 31538t^3 - 75000t^4 + 100000t^5 - 70000t^6 + 20000t^7
```

Nothing here is sampled or fitted: the numbers are whole, so the arc length is a
polynomial integral and is exact.

## The variables

| symbol | meaning | value |
|---|---|---|
| `t` | the parameter, 0 at the start and 1 at the end | 0 to 1 |
| flat spots | where the tangent is horizontal, `q(t) = 0` | 1/10, 1/5, 1/2, 1/2, 1/2, 4/5, 9/10 |
| `bend` | arc length over the straight distance between the ends | 1.325 |
| `grid` | the pitch the whole rows need: 1 over this number | 1/273 |
| self-crossings | how many times the stroke meets itself | 4 |
| loop | the part of `t` that holds the knot | t 0.0191 to 0.98 |
| step | the power step of the rows: 1 is whole powers | 1 |

## How it was found

workbench/found-curves.json; new batch

## The figure

`figure.png` is drawn by the page itself (`scripts/curve_png.mjs`), in the loop view:
the middle of `t`, framed on the knot. If the picture and the numbers ever disagree, the
numbers are right and the figure is stale — regenerate it rather than trust it.
