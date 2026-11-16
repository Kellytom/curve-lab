# wide-knot-x20

**In one line.** A curve whose speed is the polynomial below; 6 self-crossings,
grid 1/693, arc 7.1674.

## The formula

The speed is a complex polynomial, and the curve is its square, integrated:

```
w(t) = p(t) + i q(t)
z(t) = integral of w(t)^2 dt = integral of (p^2 - q^2) + i(2 p q) dt
```

```
p(t) = 4 - 20t^1 + 20t^2
q(t) = - 9 + 154t^1 - 808t^2 + 1872t^3 - 2000t^4 + 800t^5
```

Nothing here is sampled or fitted: the numbers are whole, so the arc length is a
polynomial integral and is exact.

## The variables

| symbol | meaning | value |
|---|---|---|
| `t` | the parameter, 0 at the start and 1 at the end | 0 to 1 |
| flat spots | where the tangent is horizontal, `q(t) = 0` | not recorded |
| `bend` | arc length over the straight distance between the ends | 3.908 |
| `grid` | the pitch the whole rows need: 1 over this number | 1/693 |
| self-crossings | how many times the stroke meets itself | 6 |
| loop | the part of `t` that holds the knot | t 0.0015 to 0.9975 |
| step | the power step of the rows: 1 is whole powers | 1 |

## How it was found

workbench/found-curves.json; new batch

## The figure

`figure.png` is drawn by the page itself (`scripts/curve_png.mjs`), in the loop view:
the middle of `t`, framed on the knot. If the picture and the numbers ever disagree, the
numbers are right and the figure is stale — regenerate it rather than trust it.
