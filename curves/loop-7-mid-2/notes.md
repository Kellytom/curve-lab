# loop-7-mid-2

**In one line.** A curve whose speed is the polynomial below; 8 self-crossings,
grid 1/90, arc 3.6111.

## The formula

The speed is a complex polynomial, and the curve is its square, integrated:

```
w(t) = p(t) + i q(t)
z(t) = integral of w(t)^2 dt = integral of (p^2 - q^2) + i(2 p q) dt
```

```
p(t) = 1
q(t) = 6 - 73t^1 + 269t^2 - 392t^3 + 196t^4
```

Nothing here is sampled or fitted: the numbers are whole, so the arc length is a
polynomial integral and is exact.

## The variables

| symbol | meaning | value |
|---|---|---|
| `t` | the parameter, 0 at the start and 1 at the end | 0 to 1 |
| flat spots | where the tangent is horizontal, `q(t) = 0` | 1/7, 1/2, 1/2, 6/7 |
| `bend` | arc length over the straight distance between the ends | no value: the two ends land on the same point |
| `grid` | the pitch the whole rows need: 1 over this number | 1/90 |
| self-crossings | how many times the stroke meets itself | 8 |
| loop | the part of `t` that holds the knot | t 0.0015 to 0.9975 |
| step | the power step of the rows: 1 is whole powers | 1 |

## How it was found

family-census.json; see scripts/family_census.py for the box

## The figure

`figure.png` is the **factored** drawing, accepted on 2026-11-16. Drawn from the flat spots,
with y stretched by the factor printed under the title, because these rows make a curve that
hugs the x axis. `figure-exact.png` is the same picture before it replaced the original.
