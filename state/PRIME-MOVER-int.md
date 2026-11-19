# PRIME-MOVER-int — the prime mover: a unit circle instead of a linear t

The operator's reframing (2026-11-19), written as the standing direction. Read
this before designing a new parametric family, and say which of the two drivers a
curve uses: the linear `t` or the prime mover.

## The idea, in plain words

Instead of driving a parametric curve with a straight-line parameter `t` from 0
to 1, drive it with a **prime mover** (PM): a pair of variables `PMx` and `PMy`
that travel the **unit circle**. `PM = 2π` means the pair has turned a full turn;
`PM = −2π` means a full turn the other way; a span of `[−2π, 2π]` is 720°, two
turns, one each way.

A parametric equation driven that way has curvature **built in** — it leaves and
returns, it bends without being told to — instead of a straight parameter that
has to be bent by the coefficients. That is the point: the circle supplies the
curve; the polynomial supplies the variation on it.

**The arithmetic is the project's own rule, not trigonometry.** The circle is
walked through **Pythagorean triples**, so every point is a rational pair and the
grid survives. The operator's example: start at `(25, 0)` — the 7-24-25 triple
scaled by 5 — then `(24, 7)`, then add another `(7, 24, 25)` step, and so on
around the circle. The points are found once and then **reused**; a table of
them is cheaper than computing sines every time.

**The direction matters.** Going the other way gives different points, not the
same points in reverse order: the first negative step from `(25, 0)` is
`(24, −7)`, not `(24, 7)`. Two sets of `PMx, PMy` — clockwise and anticlockwise —
drive two different families from the same coefficients.

## Why it should make better curves

- **Natural curvature.** A circle-driven parameter already turns; the polynomial
  only modulates it. That is closer to how a stem, a volute or a flourish is
  built than a straight `t` with a large `t^7`.
- **Symmetry for free, in pairs.** The + and − walks are mirror images of each
  other about the starting radius, so a pair of curves can be built together.
- **Reusable, exact, small.** The points are whole numbers (or ratios with small
  denominators), so a curve driven by them stays on the integer grid and the
  points can be tabulated once in the database.

## The arithmetic fact that has to be faced

A fixed rational rotation — one p-triple applied again and again — **never
returns exactly to 2π**. Niven's theorem: the only rational values of `cos θ`
for a rational angle in degrees are `0, ±1/2, ±1`, giving 0°, 60°, 90°, 120°,
180°. Since every p-triple has rational cosine, the only p-triple rotations that
close are quarter and half turns; everything else walks densely and misses the
start by a little more each step. Ten steps of 3-4-5 (36.87°) reach 368.7°, not
360°.

So "all the way to 360" cannot be exact with one repeated triple. Three honest
routes, and the choice must be declared per curve:

1. **Accept the miss and state it** — walk N steps, print the closing gap in
   degrees and as a share of the radius. Sampled in the last hair of the turn.
2. **Change the triple at the wrap** — pick the last step from the table so the
   walk lands on the start; exact, at the cost of one irregular step.
3. **Use the quarter and half turns only** (90°, 180°), where a p-triple closes
   exactly, and vary the polynomial between them.

## What this touches

- **Every new parametric family** should say which driver it uses: `t` (linear)
  or PM (circle). Two drivers, two shapes, and the comparison is wanted.
- **The root family** (`lace-*`) is `t`-driven; it is not rewritten, it is the
  other side of the comparison.
- **Symmetry** (`state/SIMILARITY-int.md`), **the near-zero grace**, and the
  **frames** all apply unchanged; the driver changes the shape, not the gates.
- **The table of circle points** is a dataset: one row per step, per direction,
  with the triple used. It belongs in SQLite beside `CurveMetric` when it exists,
  because it is reused by every curve.

## The first thing to build

A table of the circle points for the first turn in both directions — from
`(25, 0)` by 7-24-25 steps, `+` and `−` — with the closing gap printed. Then one
curve driven by those points instead of by `t`, measured by the same gates
(crossings, inflections, bend, grid) so the two drivers can be compared as
numbers.
