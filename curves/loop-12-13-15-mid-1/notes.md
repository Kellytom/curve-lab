# loop-12-13-15-mid-1

**In one line.** A curve whose speed is the polynomial below; 6 self-crossings,
grid 1/6, arc 14232553.8333.

## The formula

The speed is a complex polynomial, and the curve is its square, integrated:

```
w(t) = p(t) + i q(t)
z(t) = integral of w(t)^2 dt = integral of (p^2 - q^2) + i(2 p q) dt
```

```
p(t) = 1
q(t) = - 1848 + 83614t^1 - 1387533t^2 + 10226552t^3 - 33116895t^4 + 51575958t^5 - 38329200t^6 + 10951200t^7
```

Nothing here is sampled or fitted: the numbers are whole, so the arc length is a
polynomial integral and is exact.

## The variables

| symbol | meaning | value |
|---|---|---|
| `t` | the parameter, 0 at the start and 1 at the end | 0 to 1 |
| flat spots | where the tangent is horizontal, `q(t) = 0` | 1/12, 1/13, 1/15, 1/2, 14/15, 12/13, 11/12 |
| `bend` | arc length over the straight distance between the ends | no value: the two ends land on the same point |
| `grid` | the pitch the whole rows need: 1 over this number | 1/6 |
| self-crossings | how many times the stroke meets itself | 6 |
| loop | the part of `t` that holds the knot | t 0.0415 to 0.9575 |
| step | the power step of the rows: 1 is whole powers | 1 |

## How it was found

family-census.json; see scripts/family_census.py for the box

## The figure
`figure.png` is withdrawn, 2026-11-16. The pipeline runs end to end — the page is opened,
the record loaded, the loop view framed, the plot screenshotted — but the pictures come
out as a flat line rather than a knot, and the ink measurement says so: 500 to 1,000 dark
pixels spread 240 to 514 across and only 1 to 16 down, which is a horizontal line and its
axis, not a curve. One curve of the ten (loop-7-mid-2, spread 251x116) does draw.

Two causes were tried and rejected: dividing the row by its peak made the curve 10^-15
wide (scaling w scales the curve by its square, so the factor must be 1/sqrt(peak)), and
1/sqrt(peak) still degraded a curve that draws unscaled (peak 2.7e5). The remaining
suspicion is cancellation in p^2 - q^2 at peaks near 10^8, which needs the factored form
or exact arithmetic rather than a rescale. The numbers in this folder are exact and
unaffected; only the picture is missing.
