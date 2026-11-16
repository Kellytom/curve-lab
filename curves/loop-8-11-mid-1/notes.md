# loop-8-11-mid-1

**In one line.** A curve whose speed is the polynomial below; 9 self-crossings,
grid 1/42, arc 762.3571.

## The formula

The speed is a complex polynomial, and the curve is its square, integrated:

```
w(t) = p(t) + i q(t)
z(t) = integral of w(t)^2 dt = integral of (p^2 - q^2) + i(2 p q) dt
```

```
p(t) = 1
q(t) = - 70 + 1627t^1 - 12205t^2 + 33950t^3 - 38720t^4 + 15488t^5
```

Nothing here is sampled or fitted: the numbers are whole, so the arc length is a
polynomial integral and is exact.

## The variables

| symbol | meaning | value |
|---|---|---|
| `t` | the parameter, 0 at the start and 1 at the end | 0 to 1 |
| flat spots | where the tangent is horizontal, `q(t) = 0` | 1/8, 1/11, 1/2, 10/11, 7/8 |
| `bend` | arc length over the straight distance between the ends | no value: the two ends land on the same point |
| `grid` | the pitch the whole rows need: 1 over this number | 1/42 |
| self-crossings | how many times the stroke meets itself | 9 |
| loop | the part of `t` that holds the knot | t 0.0571 to 0.9419 |
| step | the power step of the rows: 1 is whole powers | 1 |

## How it was found

family-census.json; see scripts/family_census.py for the box

## The figure

`figure.png` is drawn by the page itself (`scripts/curve_png.mjs`), in the loop view:
the middle of `t`, framed on the knot. If the picture and the numbers ever disagree, the
numbers are right and the figure is stale — regenerate it rather than trust it.
