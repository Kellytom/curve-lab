# SC-NOTES-measure-port — what each piece does, for the docs

Written during the TypeScript port of `curve_lab/measure.py` →
`app/src/lib/measure.ts` (2026-11-21). This is the big picture a reader needs
before any single function makes sense. Move it into the Starlight docs when
the conversion settles.

## The object being measured

A curve is stored as two **speed rows**: `speedX` and `speedY`, polynomials
`u(t)`, `v(t)` whose integral is the curve — `x(t) = ∫(u² − v²)dt`,
`y(t) = ∫2uv dt`. That is the Pythagorean-hodograph construction: it makes the
stroke's *speed* (`u² + v²`) a polynomial, so arc length is a polynomial too
and every number below is exact arithmetic, not sampling.

## The five numbers, and what each piece computes

| piece | what it does | why it is built this way |
|---|---|---|
| `toFraction` | reads a stored coefficient as an exact fraction; a float is taken through its decimal text (six places), so 0.1 is one tenth, not the binary approximation | the pages write decimals; the maths needs rationals |
| `weight(p)` | ∫h^p over [−½, ½] = 0 for odd p, 1/(2^p·(p+1)) for even | centring on h = t − ½ makes the arc a dot product of the squared rows instead of a double sum over t |
| `centred` | rewrites the speed rows in powers of h = t − ½ (binomial shift) | the step that makes `weight` usable |
| `arcAndChord` | the arc = ∫(u²+v²) as one exact Fraction; the chord = |∫(u+iq)²|; bend = arc/chord | two integrals from one loop over the squared, centred rows |
| `grid` | the least common multiple of the position terms' denominators — "grid 36" means every position is whole once multiplied by 36 | read off the squared rows term by term (each term divides by one more than its power) |
| `curvePolynomials` | x(t), y(t) as exact coefficient lists | the position polynomials the figures draw |
| `closest` | how near the speed path comes to the origin (a near-cusp signal), sampled exactly at t = i/800 | a different question from the arc; sampled but with exact evaluations |
| `inflections` | where the tangent turns the other way: the sign changes of the Wronskian `u v' − v u'`, bracketed on the sample grid and bisected 50 times | the Wronskian's degree bounds the count (2k−1), so a shorter list is the honest reading |
| `limitDenominator` | Python's `Fraction.limit_denominator` — the nearest rational with a bounded denominator, used inside the bisection | the bisection's sign test must match Python exactly or the root lands differently |
| `metrics` | everything a gallery shows, assembled once | one call, so a page and a test cannot compute different numbers |

## The three faults the port surfaced (each is a lesson for the next port)

1. **Adding numerators across different denominators** — `(a+c)/(b+d)` instead
   of the true sum. The arc was silently wrong until the parity check caught it.
2. **A tie-break against the wrong state** — `limitDenominator`'s closeness
   comparison must be against the *original* fraction, not the loop-mutated
   CF tail. The variable was captured after the loop; the root moved.
3. **The early return must test the reduced denominator** — CPython returns
   immediately when the value's *reduced* denominator fits (a dyadic like
   15055/32768 never enters the loop); testing the raw 2^54 instead made the
   loop run into a zero remainder and crash.

## The parity harness

`app/scripts/parity-measure.mjs` compares the TypeScript `metrics` against the
Python `metrics` (dumped to JSON by a one-off `curve_lab.measure.metrics` run)
on every stored curve: grid exactly, bend/arc/closest within 1e-9 relative,
inflection lists position by position. **212 curves, 0 mismatches** is the
passing state; the harness stays in the repo so the next port row reuses it.
