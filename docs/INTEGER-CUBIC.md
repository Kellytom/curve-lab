# Integer cubic Béziers

An exact cubic family whose control points are integers, built from a
Pythagorean triple.

For any positive integers `a² + b² = c²`:

```text
P0 = (0, 0)
P1 = (a, −b)
P2 = (2c − a, b)
P3 = (2c, 0)
```

The chord is `2c`, both handle arms have length `c`, and both endpoint
tangents are at `−atan2(b, a)`. Every control point is an integer. Nothing is
fitted.

The page is `workbench/integer-cubic.html`; the constructor is
`curve_lab/pyth_cubic.py`.

## The 3-4-5 base

```text
(a, b, c) = (3, 4, 5)
P0 = (0, 0)
P1 = (3, −4)
P2 = (7, 4)
P3 = (10, 0)
```

- chord `10`, both arms `5`;
- both tangents `−53.13°` (`−atan(4/3)`);
- the two handle vectors are congruent 3-4-5 vectors;
- `P2` is the reflection of `P1` through the chord midpoint.

## Why the integers survive

The arm vector is `(a, −b)` with length `c`. The second handle is the same
vector reflected through the chord midpoint `(c, 0)`, so its offset from `P3`
is `(−a, b)`. Both the chord and the handles are built from integers.

This is not a rounding of a fitted curve. It is a direct construction from the
triple.

## Rotations

Rotating the curve by an arbitrary angle generally makes the coordinates
irrational. Rotating by an angle with rational sine and cosine, then scaling by
the denominator, returns integer coordinates.

For the 3-4-5 base:

- rotate by `53.13°` (`cos = 3/5`, `sin = 4/5`) and scale by `5`:

  ```text
  P0=(0,0), P1=(25,0), P2=(5,40), P3=(30,40)
  ```

- rotate by `36.87°` (`cos = 4/5`, `sin = 3/5`) and scale by `5`:

  ```text
  P0=(0,0), P1=(24,−7), P2=(16,37), P3=(40,30)
  ```

The angle between each arm and the chord stays `53.13°`.

## Other triples

The same construction works for every Pythagorean triple. The page carries:

| triple | tangent | chord | arm |
|---|---:|---:|---:|
| 3-4-5 | −53.13° | 10 | 5 |
| 4-3-5 | −36.87° | 10 | 5 |
| 5-12-13 | −67.38° | 26 | 13 |
| 12-5-13 | −22.62° | 26 | 13 |
| 8-15-17 | −61.93° | 34 | 17 |
| 15-8-17 | −28.07° | 34 | 17 |
| 7-24-25 | −73.74° | 50 | 25 |
| 24-7-25 | −16.26° | 50 | 25 |
| 20-21-29 | −46.40° | 58 | 29 |
| 21-20-29 | −43.60° | 58 | 29 |

Each pair is a triple and its complementary slope.

## What this means for the curve system

This is an exact integer-control spine, not a promise that every later
operation stays integer. The useful distinction is what follows from the
construction and what needs its own test.

| operation | status | why |
|---|---|---|
| integer controls | yes | the four points are built from integers |
| point at rational `t=p/q` | rational, then integer after scaling | de Casteljau denominators divide `q³` |
| split at rational `t` | rational, then integer after scaling | the sub-curve has the same denominator |
| exact offset | no, not automatically | the normal needs a square root; the base curve is not PH |
| G2 join | possible, needs solving | tangent and curvature are rational; asymmetric arms give more freedom |
| arc length | no | a cubic arc length is generally not rational |

### Points along the curve

Choose a rational parameter `t=p/q`. The de Casteljau construction gives
rational control points with denominators dividing `q³`. Multiply the whole
cubic by `q³`, and every control point, the split point, and both sub-curves
become integer. For a finite set of fractions, use a common denominator `Q`
and scale by `Q³`.

For the 3-4-5 base at `t=1/3`, scale by `27`. The first sub-curve is

```text
P0=(0,0), P1=(27,−36), P2=(57,−36), P3=(88,−24)
```

and the split point is `(88,−24)`. The shape is unchanged; the lattice is
simply finer. The parameter is a fraction of the curve's parameter, not a
distance along it, and the required scale can grow quickly.

### The 60³ grid

A natural asymmetric example is the quarter-turn cubic

```text
P0=(0,0), P1=(4,−3), P2=(7,−4), P3=(10,0)
```

It starts at slope `−3/4`, ends at slope `4/3`, and has integer controls. The
combined grid is `3³ · 4³ · 5³ = 60³ = 216000`. The `2³` factor is already
inside `4³`; multiplying by it again would make the grid eight times finer
than needed.

Every point at `t=k/60` has a denominator dividing `60³`, so scaling by
`60³ = 216000` puts all 61 sampled points on one integer grid. Those are
parameter samples, not arc-length points. The grid does not make offsets or
arbitrary curve points integer.

### Offsets are a separate promise

Integer controls do not make an offset curve integer. An offset point needs the
unit normal, which involves a square root. The normal is rational at special
points such as endpoints with Pythagorean tangents, but not at a generic point.
The offset of a general cubic is not another cubic, and the 3-4-5 base is not a
Pythagorean-hodograph cubic, so its exact offset is not rational in general.

Treat offsets as a fitted or numeric layer. Exact rails remain lines, arcs and
PH curves; this family gives a clean spine to offset from, not an exact offset
family.

### G2 joins, symmetric and asymmetric

G2 needs both the tangent direction and the curvature to match. For an integer
cubic, endpoint curvature is rational, so this becomes a rational algebra
problem rather than a numerical fitting problem.

The symmetric family is a single shape parameter per triple: both arms have the
same length, and the two endpoint curvatures have the same magnitude and
opposite signs. That is elegant, but it is rigid at a join: matching one end
fixes the curvature scale for the other.

An asymmetric version removes that constraint. Take

```text
P0=(0,0), P1=(a0,−b0), P2=(L−a1,b1), P3=(L,0)
```

with integer chord `L` and two Pythagorean arms `(a0,b0)` and `(a1,b1)`. The
arm lengths can differ, and the two endpoint curvatures can be tuned
independently. That is the natural way to give a piece a G2 match on both
sides: rotate at a Pythagorean angle, translate on integers, choose or scale
the arms for the two curvatures, then clear the common denominator.

This is a direction, not yet a proved recipe. A zero-curvature endpoint cannot
be scaled into a nonzero one, the sign of curvature must match, and the
required integer scale may be large. The asymmetric shape also moves the
inflection, so it needs a shape and clearance check, not only a curvature
check.

### What to add next

- a split-and-scale helper with exact rational arithmetic and tests at `t=1/2`
  and `t=1/3`;
- a G2 join probe that reports tangent mismatch, curvature mismatch, and the
  final integer scale;
- an asymmetric-arm search: which pairs of Pythagorean arms can match two
  chosen endpoint curvatures;
- one offset comparison on this curve, labelled fitted rather than exact;
- a small lattice census: which integer points appear at chosen scales, and
  how large the scales get;
- a two-parabola S probe: elevate two quadratics, solve the G2 join, and compare
  with the cubic.

## Another route: elevate a quadratic

A quadratic Bézier is a parabola. Degree elevation turns it into a cubic
without changing the curve:

```text
R0=Q0, R1=(Q0+2Q1)/3, R2=(2Q1+Q2)/3, R3=Q2
```

That is exact, not a fit. If the quadratic controls are integers, the elevated
controls may acquire a factor of 3; scale by 3 to clear it. Points at a rational
`t=p/q` have denominators dividing `q²` for the quadratic, which is cheaper
than the cubic's `q³`.

A single parabola cannot make an S: its curvature has one sign. An S needs two
pieces, one on each side of the inflection. If you start with two quadratics
and elevate them, the piecewise-parabolic S is exact for that design. If you
start with the existing integer cubic S and split it at `1/2`, each half is
still a cubic; replacing each half by a quadratic is an approximation, not an
exact elevation.

The trade is fewer shape controls. Two parabolas give a clean S and easy G1
joins, but G2 still requires a curvature match, and the family has fewer
degrees of freedom than the asymmetric cubic. Parabola offsets are also not
rational in general.

| representation | exact for | point denominator | shape freedom |
|---|---|---|---|
| single cubic | a cubic | `q³` | high; asymmetric arms |
| elevated quadratic | one parabola | `q²`, then ×3 for integer controls | one bend |
| two elevated quadratics | a piecewise-parabolic S | `q²` per piece | two bends; join conditions |

## The 3125 circle

The integer points on `x² + y² = 3125` give these slopes:

```text
0.00°, 4.35°, 16.26°, 20.61°, 32.52°, 36.87°, 53.13°,
57.48°, 69.39°, 73.74°, 85.65°, 90.00°
```

These are rational-lattice rotations. Scaling by `3125` clears the denominator
and returns integer control points. The number `3125` also appears as a
clothoid parameter elsewhere in the project; that is a different use of the
same number (`docs/clothoid-grid-3125.md`).

## Scope

This is an exact integer-control cubic family. Its useful properties are:

1. integer coordinates;
2. chord and arm lengths fixed by the triple;
3. rational endpoint tangents;
4. integer rotations at Pythagorean angles.

## Verification

```sh
.venv/bin/python -m unittest tests.test_pyth_cubic
```

`tests/test_pyth_cubic.py` checks every triple, the base coordinates, the
`53.13°` tangent, and both rotated/scaled examples.
