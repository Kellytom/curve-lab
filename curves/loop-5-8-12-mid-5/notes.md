# loop-5-8-12-mid-5

**In one line.** A curve whose speed is the polynomial below; 19 self-crossings,
grid 1/74364290, arc 2256.0932.

## The formula

The speed is a complex polynomial, and the curve is its square, integrated:

```
w(t) = p(t) + i q(t)
z(t) = integral of w(t)^2 dt = integral of (p^2 - q^2) + i(2 p q) dt
```

```
p(t) = 1
q(t) = - 308 + 11853t^1 - 188487t^2 + 1649658t^3 - 8932104t^4 + 31775616t^5 - 76510896t^6 + 125629344t^7 - 138652416t^8 + 98395648t^9 - 40550400t^10 + 7372800t^11
```

Nothing here is sampled or fitted: the numbers are whole, so the arc length is a
polynomial integral and is exact.

## The variables

| symbol | meaning | value |
|---|---|---|
| `t` | the parameter, 0 at the start and 1 at the end | 0 to 1 |
| flat spots | where the tangent is horizontal, `q(t) = 0` | 1/5, 1/8, 1/12, 1/2, 1/2, 1/2, 1/2, 1/2, 11/12, 7/8, 4/5 |
| `bend` | arc length over the straight distance between the ends | no value: the two ends land on the same point |
| `grid` | the pitch the whole rows need: 1 over this number | 1/74364290 |
| self-crossings | how many times the stroke meets itself | 19 |
| loop | the part of `t` that holds the knot | t 0.0513 to 0.9477 |
| step | the power step of the rows: 1 is whole powers | 1 |

## How it was found

family-census.json; see scripts/family_census.py for the box

## The figure

`figure.png` is the **factored** drawing, accepted on 2026-11-16. It is drawn from the flat
spots — `q` as a product of `(t − r)`, `p` constant — where nothing cancels, and `y` is
stretched by the factor printed under the title, because these rows make a curve that hugs
the x axis. The stretch is stated on the figure so the picture is never mistaken for an
equal-aspect drawing. `figure-exact.png` is the same picture before it replaced the original;
`figure-exact.svg` is its source.
