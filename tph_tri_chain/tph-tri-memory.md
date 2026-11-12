# tph-tri-memory — resume point

Mini state file for the discrete T-PH triangle chain. Append, do not rewrite.
Last updated: 2026-11-11.

## Where we are

Verified method, working generator, docs draft. Committed on `main` so it
cannot be lost, but not accepted and not in `docs/`, and not wired into
`curve_lab/`.

Open gate: the operator has to accept the grid correction (3125 is not
achievable for the fish) and the stopping point before this moves.

## Files

| path | role |
|---|---|
| `chain.py` | exact Fractions engine, all tables, asserts the triple per step |
| `glyph.py` | fish CSV + labelled SVG, one y flip in `fy()` |
| `make_results.py` | emits `RESULTS.md` and `results.html` from one block list |
| `RESULTS.md` / `results.html` | the result document and its mirror |
| `out/lattice-t3.csv` | 24 steps at t = 3, every value an integer on pitch 256 |
| `out/lattice-t3.svg` | Fig. T1, the whole-number hits at 12 triangles per side |

## Commands

```sh
cd /Users/thomaskelly/developer/curve-lab
.venv/bin/python tph_tri_chain/chain.py         # all tables + audit
.venv/bin/python tph_tri_chain/glyph.py         # CSV + SVG
.venv/bin/python tph_tri_chain/make_results.py  # md + html, runs 8 checks
.venv/bin/python -m unittest discover tests     # 577 tests, was OK
```

## Imports

Run from the repo root; the script directory is on the path, so:

```python
from fractions import Fraction as F
from chain import chain, grid, integral, primitive

rows, dt = chain(F(0), F(12, 5), 120)   # rows: i, t, dx, dy, ds, x, y
g = grid(rows)                           # smallest exact integer grid
x, y, s = integral(F(12, 5))             # exact curve point + arc length
```

## Formulae

```text
u(t) = t, v(t) = 1                      generators, linear
x'(t) = 2t
y'(t) = 1 - t^2
sigma(t) = 1 + t^2
x(t) = t^2      y(t) = t - t^3/3      s(t) = t + t^3/3
```

Midpoint rule, N steps over [t0, t1], dt = (t1-t0)/N, t_i = t0 + (i+1/2)dt:

```text
dx_i = 2 t_i dt             dy_i = (1 - t_i^2) dt    ds_i = (1 + t_i^2) dt
dx^2 + dy^2 = ds^2        exactly, because (u^2-v^2)^2 + (2uv)^2 = (u^2+v^2)^2
```

Symmetry: `x(-t) = x(t)`, `y(-t) = -y(t)`. Loop closes at `t = sqrt(3)`,
point `(3, 0)`, loop length `4 sqrt(3)`.

## Grid law (the load-bearing result)

Only the step width matters. With `dt = c/q` in lowest terms and `p = 2i+1`
always odd:

```text
grid = q^3         when c is even      (odd grid possible)
grid = 4 * q^3     when c is odd       (factor 4 unavoidable)
```

Verified on 1200 (t_max, N) pairs, exact equality, zero exceptions.
The 4 is the midpoint half-step: `4q^2 - p^2 c^2` is odd when c is odd.

Consequences:

- `3125 = 5^5` is odd, so it needs c even and `q^3 | 3125`, i.e. q = 5:
  only `dt = 2/5` (N = 5 t_max/2) or `4/5`. The fish gets **6** triangles
  per branch on 3125. 3125 cannot be refined into.
- At the fish stop `12/5`: `dt = 2/25` gives grid **15625 = 5 x 3125** with
  30 triangles per branch; `dt = 1/50` gives **500000** with 120.
- The `/3` in x and s never enters the grid: the chain uses the hodograph,
  which has no cubic term. It only makes exact reference values integral when
  t_max is a multiple of 3 (`t = 3`: x = -6, y = 9, s = 12).
- Longer curve is cheaper per triangle (larger t_max, coarser dt, smaller
  grid) but breaks the fish proportion.

## Verified numbers to quote

| case | grid | result |
|---|---|---|
| [0,2], N=4 | 32 | (15,8,17) (7,24,25) (-9,40,41) (-33,56,65); end (-0.625, 4); length 37/8 |
| [0,2], N=25 | 15625 | end (-0.665600, 4.000000); length 4.665600 |
| fish 12/5, N=120 | 500000 | tips (±2.208000, 5.760000); length 87599/6250 = 14.015840 |
| exact | — | 1752/125 = 14.016000; error -1.6e-4; tail/loop 2.023 |
| fish 12/5, N=30 | 15625 | error 1.28e-3; tail/loop 2.023 |

Stopping points: `sqrt(3)` closes the loop at (0,3); `12/5` gives
(-2.208000, 5.760000) and 2.023x; `5/2` gives (-2.708333, 6.250000) and
2.225x; `sqrt(6)` gives (-2.449490, 6.000000) and 2.121x but t is irrational,
so no rational chain ends there.

`y` at the stop is exact for every N (`t_max^2`), because midpoint quadrature
is exact on the linear `y'`. Only x carries error. The chain misses the
crossing (0,3) by about 0.028 in y at N=120.

## Lattice hits — the hard constraint

The smooth curve meets the integer lattice (both x and y integers) only at:

- **t ∈ 3ℤ**: `(9u², 3u(1 − 3u²))` → (0,0), (9,−6), (36,−66), (81,−234),
  (144,−564), … and their mirrors (x, −y).
- **t = ±√3**: (3, 0), the self-intersection, but at an irrational parameter.

Proof: `x = t²` integer with `t = a/b` in lowest terms forces `b = 1`, so t is an
integer; then `y = t − t³/3` is an integer only when `3 | t`. For irrational t,
write `x = k`; then `t = √k` and `y = √k(1 − k/3)`, which is an integer only at
`k = 3`, giving (3,0).

Consequence. In whole units, at pitch 1, only t in 3Z hits. But the pitch exists
to clear fractions, and that is the point of it: at pitch G a point is a whole
cell once G is a multiple of its denominators. Minimum pitch for the curve point:
1 at t=3, 3 at t=2 and t=4, 24 at 5/2, 125 at 12/5, 1000 at 21/10. All exact.
The chain needs a larger pitch at every stop, because every side must be whole
too: 108, 864, 55296, 500, 256000, 256 at N=12 respectively. So t=3 is singled
out only because it needs no scaling at all -- not because other stops fail.

The chain cannot reproduce the hit. Closed form, exact:

```text
x_chain = x(T) + T^3/(12N^2)      y_chain = y(T) exactly
s_chain = s(T) - T^3/(12N^2)
```

At T = 3, N = 120 the tip x is 1/6400 = 1.56e−4 short of −6. Only y lands
exactly. So the nodes live on the pitch-1/G lattice; the integer lattice belongs
to the curve, not to the chain.

## Words

- t is the knob along the curve: not a length, not a distance.
- step width is a slice of t: stopping point / triangle count.
- pitch is grid cells per unit of the drawing, across and up. It is unrelated to t
  and unrelated to distance along the curve.
- total grid = pitch x how many units the curve spans. A pitch alone says nothing
  about size. 3125 is a pitch, not a total.

## Principles

- Every step is asserted as an equality of `Fraction`s, never a tolerance.
- The method is the Tschirnhausen cubic PH curve only. No Bezier control
  points, no spline basis, no knot vector, no de Casteljau, no generic cubic
  formula. Do not add them.
- +y is up, as the curve is. SVG is y-down, so the flip happens once, in
  `fy()` in `glyph.py`, and nowhere else.
- Figures label inside the figure: figure number, title, axis labels, legend
  at 15px or more, named points with coordinates.
- Holding pen: nothing in `curve_lab/`, `workbench/`, `scripts/`, `web/`
  imports this, and this imports none of them. Not the same method as
  `ph_hermite`; do not reconcile the two yet.
- Untracked directory, so it cannot slip into a commit. Stage explicit paths
  if it is ever promoted.

## Traps already hit

- The draft claimed the N=25 chain lands on 3125. It needs 15625.
- The draft's first triple on grid 15625 was (1248, 200, 1252). Correct is
  (1248, 100, 1252); the 200 does not satisfy the identity.
- The draft's `[0,1], N=25` example is internally contradictory; the real
  grid is 62500 and the first step is (2499, 100, 2501).
- `N = 5n` giving `dt = 1/(2n)` produces clean decimals, not integers. That
  is where the 3125 idea came from; it does not survive.
- `sqrt(6)` is not a rational stopping point, so it cannot be a chain end.

## Next decisions (in order)

1. Operator looks at `out/lattice-t3.svg`: are the rings readable, is the
   1/64 gap visible without being ugly? Only the operator can judge that.
2. Confirm t = 3 as the stop, at 12 triangles per side.
3. Only then: promote to `docs/PH-TRIANGLES-int.md` and decide about tracking.

## Changelog

- 2026-11-11: tph-tri-sandbox.html is the live page (CSS lifted from
  workbench/showcase.html, built by sandbox.py). Fractions only, no decimals.
  Four-panel Fig. T2 (out/midpoint.svg) explains the midpoint step, the exact
  reach, the 1/12 drift, and both ends. 3125 at N=12 needs t = 24/5, grid 125.

- 2026-11-11: results rewritten around integer hits at N = 12 per side.
  Figure retargeted to t = 3, pitch 256; the old 12/5 at N = 120 artifacts
  removed. Plain words throughout: no set notation.

- 2026-11-11: directory created, held untracked; method verified exactly;
  grid law found (G = q^3 or 4q^3); RESULTS.md + results.html generated;
  section 10 corrected from "3125 needs 32" to the dt-based law.
- 2026-11-11: lattice rule recorded — the curve meets ℤ² only at t ∈ 3ℤ and at
  t = ±√3; the chain hits only x exactly (y is short by T³/(12N²)); "grid" in
  earlier notes means pitch 1/G, canvas is the cell extent.

## Same-N comparison (the deliverable that got lost)

Compare methods at the SAME triangle count, N = 12 per branch, plain words only.

| t | step width | pitch | midpoint tip y | gap from exact | x exact | chordal tip |
|---|---|---|---|---|---|---|
| 2.4 | 1/5 | 500 | -11/5 | 0.008000 | yes | (144/25, -276/125) |
| 2.5 | 5/24 | 55296 | -37315/13824 | 0.009042 | yes | (25/4, -65/24) |
| 3 | 1/4 | 256 | -383/64 | 0.015625 | yes | (9, -6) |
| 4 | 1/3 | 108 | -467/27 | 0.037037 | yes | (16, -52/3) |

At t = 3 the chordal path lands exactly on (9, -6); the midpoint chain misses it
by 1/64 but keeps whole-number triangle sides: (16,63,65) (48,55,73) (80,39,89)
(112,15,113) (144,-17,145) (176,-57,185) (208,-105,233) (240,-161,289)
(272,-225,353) (304,-297,425) (336,-377,505) (368,-465,593).

Pitch at fixed N is set by the step width t/12: t=4 gives 1/3 -> 108, t=3 gives
1/4 -> 256, t=2.4 gives 1/5 -> 500, t=2.5 gives 5/24 -> 55296.

Rules: write "t is a multiple of 3", "whole-number point", "integer lattice" --
never set notation. Keep exact forms: a fraction where the value is rational,
sqrt(...) where it is not. A decimal is never a substitute for an exact
expression, but it is fine as a hint beside one. Use fractions generously: they
are the point, not a constraint to work around. Prefer a round grid number
(125, 625, 3125, 256) where one is available. A grid exists to clear fractions,
so ask which pitch clears them, never whether a coordinate is whole.

## Context meter

The window is 1,000,000 tokens, confirmed by the operator. `scripts/ctx.py`
is right and its `DEFAULT_WINDOW` must not be retuned on a guess. A note in
this file once claimed 156k and it was wrong; it was reverted the same day.

## Next decisions (in order)

1. Accept the grid: 15625 (30/branch, 5x3125) or 500000 (120/branch)? 
2. Confirm the stop at `t = 12/5`.
3. Operator eyeballs `out/fish-t24.svg` — legible, chain inside the curve,
   tail reads as a fish. Only the operator can judge this.
4. Only then: promote to `docs/PH-TRIANGLES-int.md` and decide about tracking.

## Changelog

- 2026-11-11: directory created, held untracked; method verified exactly;
  grid law found (G = q^3 or 4q^3); RESULTS.md + results.html generated;
  section 10 corrected from "3125 needs 32" to the dt-based law.
- 2026-11-11: lattice rule recorded — the curve meets ℤ² only at t ∈ 3ℤ and at
  t = ±√3; the chain hits only x exactly (y is short by T³/(12N²)); "grid" in
  earlier notes means pitch 1/G, canvas is the cell extent.

## Same-N comparison (the deliverable that got lost)

Compare methods at the SAME triangle count, N = 12 per branch, plain words only.

| t | step width | pitch | midpoint tip y | gap from exact | x exact | chordal tip |
|---|---|---|---|---|---|---|
| 2.4 | 1/5 | 500 | -11/5 | 0.008000 | yes | (144/25, -276/125) |
| 2.5 | 5/24 | 55296 | -37315/13824 | 0.009042 | yes | (25/4, -65/24) |
| 3 | 1/4 | 256 | -383/64 | 0.015625 | yes | (9, -6) |
| 4 | 1/3 | 108 | -467/27 | 0.037037 | yes | (16, -52/3) |

At t = 3 the chordal path lands exactly on (9, -6); the midpoint chain misses it
by 1/64 but keeps whole-number triangle sides: (16,63,65) (48,55,73) (80,39,89)
(112,15,113) (144,-17,145) (176,-57,185) (208,-105,233) (240,-161,289)
(272,-225,353) (304,-297,425) (336,-377,505) (368,-465,593).

Pitch at fixed N is set by the step width t/12: t=4 gives 1/3 -> 108, t=3 gives
1/4 -> 256, t=2.4 gives 1/5 -> 500, t=2.5 gives 5/24 -> 55296.

Rules: write "t is a multiple of 3", "whole-number point", "integer lattice" --
never set notation. Do not quote N other than the one asked for. No decimals
anywhere: exact fractions, and sqrt(...) for anything irrational. A grid is a
single round number (125, 625, 3125, 256), never a width-times-height. A grid
exists to clear fractions, so ask which pitch clears them, never whether a
coordinate is whole.

## Context meter

scripts/ctx.py had DEFAULT_WINDOW = 1_000_000. This engine is about 156k, so the
meter under-reported 6.4x and this session ran to 110% of the window. Fixed to
156_000 on 2026-11-11. Trust it now.
