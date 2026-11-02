# Integer PH curves: the generator, the grid, and what is actually true

A corrected version of a survey that has been circulating in this project.
Where it agrees with the arithmetic it is kept; where it does not, the number
below was computed, not remembered. Every figure on this page comes from
`scripts/generators.py`, which works in `fractions.Fraction` and asserts that each
coordinate is integral before it writes anything.

## The generator

A planar curve has a *Pythagorean hodograph* when the speed is a polynomial:

```
x'(t)^2 + y'(t)^2 = sigma(t)^2
```

Every such curve is written, with complex polynomials `w = u + iv` and a factor
`h`,

```
z'(t) = h(t) · ( u(t)^2 - v(t)^2 ,  2 u(t) v(t) )
sigma = h(t) · ( u(t)^2 + v(t)^2 )
```

and Farouki and Sakkalis's lemma fixes the degree:

```
n = deg h + 2 · max(deg u, deg v) + 1
```

That identity is the load-bearing one, and the survey omitted it — which is why
its quartics and sextics had no construction. With `h = 1` only odd degrees
appear; the `h` factor is the only way to reach an even degree:

| `deg h` | `max(deg u, deg v)` | degree |
|---|---|---|
| 0 | 1 | 3 |
| 1 | 1 | 4 |
| 0 | 2 | 5 |
| 2 | 1 | 5 |
| 1 | 2 | 6 |

## What comes free

With integer generators, and no approximation anywhere:

- **speed** is the polynomial `h (u² + v²)`;
- **arc length** integrates it exactly, as a polynomial;
- **tangent** is `2·atan(v/u)`, or in integers, Euclid's doubling
  `(u²−v², 2uv) / (u²+v²)`;
- **offset** by a distance `d` is *rational*, not refitted;
- **curvature** is a rational function;
- **splitting** at any `t` keeps the curve PH and keeps the generators integral.

## The integer arithmetic

Control points come from integrating the hodograph, so the cubic divides by 3,
the quartic by 4, the quintic by 5, the sextic by 6 — then a conversion to the
Bernstein basis multiplies by binomials. Milestones at `t = k/m` bring the
Bernstein weights, which carry `m` to the degree. The least integer that clears
both is the scale.

What that means in practice, for four curves built from small numbers:

| curve | n | generators | step | scale | integer grid |
|---|---|---|---|---|---|
| cubic | 3 | `h=(1)` `u=(2,-2)` `v=(1,-2)` | 1/4 | 24 | 32 × 32 |
| quartic | 4 | `h=(1,2)` `u=(1,-1)` `v=(1,-2)` | 1/4 | 1536 | 1152 × 1280 |
| quintic | 5 | `h=(1)` `u=(-2,-1,1)` `v=(-1,-1,2)` | 1/2 | 480 | 1872 × 1744 |
| sextic | 6 | `h=(1,2)` `u=(-1,1,0)` `v=(2,-1,0)` | 1/2 | 240 | 880 × 640 |

Three consequences, and they contradict the folklore.

**The milestone scale is `mⁿ`, and PH never improves it.** A plain Bézier whose
control points are integers already has integer control points at scale 1, and
pays exactly the same `mⁿ` for its milestones. PH *costs* a factor of 3
(cubic) or 15 (quintic) on the control points, because the integration
denominator has to be cleared. What PH buys is exact arc length, rational
offsets and a rational frame — not a smaller lattice.

**Integer milestones always exist.** Any finite set of rational parameters
clears at the lowest common multiple of its denominators. The bean, for
example, has quarter-points with denominators 1, 91, 3, 91 and 1, so a scale of
273 puts every one on the grid. The scale is a fact about the arithmetic, not a
wall.

**What is impossible is the strong claim.** No bounded curve holds infinitely
many lattice points, so "infinitely many points on the curve can be integers"
cannot be true of any curve, PH or not. You get finitely many, at parameters
you choose.

## The numbers that circulate

| claim | what it is | verdict |
|---|---|---|
| cubic, fifths, scale 750 | 375 for `u=(2,1)`, `v=(1,2)` | 2× too high |
| quintic, fifths, 3,125 | `5⁵`, the step term | a floor, not the scale |
| quintic, fifths, 187,500 | `2²·3·5⁶`, one generator set | true of some numbers only |
| quintic, tenths, 3,000,000 | `10⁵ = 100,000` is the step floor | 30× too high |
| "2, 4, 8, 16 at eighths → 128" | a cubic at eighths is at least `3·512` | not reproduced |
| arc length 26 for the worked example | 26 is the unscaled sum; ×3 gives 78 | off by the scale |

None of these are fatal — they are all the same error, which is treating a
number that belongs to *one set of generators* as if it belonged to the degree.

## Degree by degree

- **n = 2** does not exist. There are no quadratic PH curves.
- **n = 3** is the Tschirnhausen cubic, up to scale and rotation: one shape
  only, no inflection, so a C-curve. Loops and cusps are reachable by letting
  the generators cross.
- **n = 4** needs `deg h = 1`. It can inflect, which the cubic cannot.
- **n = 5** is the workhorse: C and S shapes, first-order Hermite interpolation
  with a single segment, and the only low degree that supports C² PH splines.
  The quintic transition curve — straight line to circular arc with monotone
  curvature — is the lowest-degree polynomial that does the clothoid's job.
- **n = 6** takes `deg h = 1` with quadratic generators. This is where the
  multiple-cusp shapes live.

## Named curves

Two of these are nodal cubics, and only one is the PH one. Every cubic PH curve
is a scaled, rotated *Tschirnhausen cubic*, `27ay² = (a−x)(8a+x)²`, whose node
crosses at 60 degrees. The other, `y² = x²(x+1)`, crosses at 90 — same genus,
same degree, reachable from the first only by an affine map, never by a
similarity, because an angle is not affine. A cubic PH curve's control polygon
is what the top of this page has been building; the node angle is how you tell
whether a nodal cubic is that family or merely nearby.

The test that separates these is rationality, and it is decidable: count the
singular points, and check that the gradient vanishes at each. A rational curve
has an exact Bézier — substitute `t = s/(1−s)` and clear denominators. A curve
with a cusp does not, and sampling is the honest fallback.

| curve | equation | degree | tier | integer data |
|---|---|---|---|---|
| bean | `x⁴ + x²y² + y⁴ = x(x² + y²)` | 4 | rational · exact Bézier | control 12, milestones 273 |
| bicorn | `y²(1 − x²) = (x² + 2y − 1)²` | 4 | rational · exact Bézier | control 6, milestones 105 |
| pear | `x² = y³(1 − y)` | 8 | rational · exact Bézier | control 35, milestones 625 |
| heart | `(x² + y² − 1)³ = x²y³` | 6 | not rational · sampled | — |
| nodal | `y² = x²(x + 1)` | 3 | rational · exact Bézier | control 3, milestones 1 |
| tschirnhausen | `27y² = (1 − x)(8 + x)²` | 3 | rational · exact Bézier | control 1, milestones 27 |
| bow | `x⁴ = x²y − y³` | 4 | rational · exact Bézier | control 3, milestones 16 |
| epicycloid k=3 | `x = 4cos θ − cos 4θ,  y = 4sin θ − sin 4θ` | 8 | rational · exact Bézier | control 35, milestones 1 |
| epicycloid k=5 | `x = 6cos θ − cos 6θ,  y = 6sin θ − sin 6θ` | 12 | rational · exact Bézier | control 231, milestones 1 |
| deltoid | `x = 2cos θ + cos 2θ,  y = 2sin θ − sin 2θ` | 4 | rational · exact Bézier | control 3, milestones 1 |
| hypocycloid k=5 | `x = 4cos θ + cos 4θ,  y = 4sin θ − sin 4θ` | 8 | rational · exact Bézier | control 35, milestones 1 |
| nephroid | `z ↦ z³ + 3z on the unit circle` | 6 | rational · exact Bézier | control 5, milestones 1 |
| astroid | `(x² + y² − 1)³ + 27x²y² = 0` | 6 | rational · exact Bézier | control 5, milestones 1 |
| trifolium | `(x² + y²)² − x³ + 3xy² = 0` | 4 | rational · exact Bézier | control 12, milestones 50 |
| quadrifolium | `(x² + y²)³ = (x² − y²)²` | 6 | rational · exact Bézier | control 15, milestones 125 |
| circle | `x² + y² = 1` | 2 | rational · exact Bézier | control 1, milestones 5 |
| rounded square | `four edges and four quarter arcs` | 4 + 4 pieces | rational · exact Bézier | control 1, milestones 425 |
| squircle | `|x|⁴ + |y|⁴ = 1` | 4 | not rational · sampled | — |
| cardioid | `(x² + y²)² + 2x(x² + y²) − y² = 0` | 4 | rational · exact Bézier | control 3, milestones 25 |
| bernoulli | `(x² + y²)² = x² − y²` | 4 | rational · exact Bézier | control 4, milestones 41 |
| gerono | `x⁴ − x² + y² = 0` | 4 | rational · exact Bézier | control 6, milestones 25 |
| cruciform | `x²y² − b²x² − a²y² = 0` | 4 | rational · unbounded, sampled per arm | — |
| piriform | `x⁴ − 2x³ + y² = 0` | 4 | rational · exact Bézier | control 3, milestones 25 |

The bean is worth spelling out. In polar form it is `r = cosθ / (1 − ¼sin²2θ)`,
a ratio of polynomials; with `t = tan(θ/2)` and `t = s/(1−s)` it becomes an
exact rational Bézier whose homogeneous control values are whole numbers, and
it reproduces the curve to `10⁻¹⁶`. Its two `W = 0` control values are points at
infinity, which is why there is no control *polygon* to lay on the lattice.

The piriform is the fourth exact one. Its equation is `a⁴y² = b²x³(2a − x)`,
which at `a = b = 1` is `y² = x³(2 − x)`: a rational quartic with a cusp at the
origin, a vertex at `(2, 0)`, and the bounds `0 ≤ x ≤ 2`, `|y| ≤ 3√3/4`.
Through `x = 1 + sin t`, `y = cos t (1 + sin t)`, then `u = tan(t/2)`, the
homogeneous generator is `X = (u+1)²(1+u²)`, `Y = (u+1)²(1−u²)`, `W = (1+u²)²`
— whole numbers, no clearing needed.

Two wrong forms are worth recording, because both look plausible. The quartic
`x⁴ − x²y + y² = 0` is a quadratic in `y` with discriminant `−3x⁴`, so its only
real point is the origin; and `x⁴ + x²y − y² = 0` factorises as
`(y − k₁x²)(y − k₂x²)` with `k = (1 ± √5)/2` — two parabolas, not a pear. Only
the `x³` form is the curve.

## The catenary

A true catenary is `a·cosh(x/a)`: transcendental, so no scale factor can put it
on an integer grid. The AHPH family keeps the PH property in a hyperbolic basis
— exact arc length, rational offsets — but not integers. The integer-friendly
answer is the one this repo already uses: four Tschirnhausen cubics over the
curve, worst error 0.41 per cent of `a`.

## What this session measured

Two results, both negative, both worth keeping.

**The discriminant route does not produce a lattice.** It is true that a
segment's closure quadratic has a rational square discriminant exactly when the
fit is exact. But on the full 92-rung pythagorean ladder, for the four catenary
chords, **0 of 17,168** non-negative discriminants are squares; and where one
is, `k` carries a denominator in the thousands, so the control points are
rational, not integral. Choosing the pair buys exactness, not integers.

**The generator route does.** You do not fit through prescribed points and hope;
you choose integers and the endpoint is whatever it is. That is the difference
between `scripts/generators.py` and a least-squares fit.

Along the way `from_pairs` in `scripts/hodograph.py` turned out to rotate by
half the tangent angle, so it only closed when a segment started at zero. It is
fixed and now agrees with `from_hermite` to `10⁻¹⁴`.

## Open

- Whether the named curves should be fitted to a measured reference with a
  stated tolerance, in the manner of `FIDELITY.md`.
- Whether the named curves should be fitted to a measured reference with a
  stated tolerance, in the manner of `FIDELITY.md`.
- Whether `generators` should write straight into the web app's input pages.
