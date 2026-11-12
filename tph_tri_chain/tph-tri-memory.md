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
| `out/fish-t24.csv` | 240 steps, every value an integer on grid 500000 |
| `out/fish-t24.svg` | Fig. T1, 240 triangles against the smooth curve |

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
u(t) = 1, v(t) = t                      generators, linear
x'(t) = 1 - t^2
y'(t) = 2t
sigma(t) = 1 + t^2
x(t) = t - t^3/3      y(t) = t^2      s(t) = t + t^3/3
```

Midpoint rule, N steps over [t0, t1], dt = (t1-t0)/N, t_i = t0 + (i+1/2)dt:

```text
dx_i = (1 - t_i^2) dt     dy_i = 2 t_i dt     ds_i = (1 + t_i^2) dt
dx^2 + dy^2 = ds^2        exactly, because (u^2-v^2)^2 + (2uv)^2 = (u^2+v^2)^2
```

Symmetry: `x(-t) = -x(t)`, `y(-t) = y(t)`. Loop closes at `t = sqrt(3)`,
point `(0, 3)`, loop length `4 sqrt(3)`.

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

- **t ∈ 3ℤ**: `(3u(1 − 3u²), 9u²)` → (0,0), (−6,9), (−66,36), (−234,81),
  (−564,144), … and their mirrors (−x, y).
- **t = ±√3**: (0, 3), the self-intersection, but at an irrational parameter.

Proof: `y = t²` integer with `t = a/b` in lowest terms forces `b = 1`, so t is an
integer; then `x = t − t³/3` is an integer only when `3 | t`. For irrational t,
write `y = k`; then `t = √k` and `x = √k(1 − k/3)`, which is an integer only at
`k = 3`, giving (0,3).

Consequence: **2.4, 2.5, 12/5 and 2.1 can never hit the lattice** — their y is
144/25, 25/4, 144/25 and 441/100. A glyph that must land on whole units
therefore stops at **t = 3**: nose (0,0), waist (0,3), tips (±6, 9), height 9 =
body 3 + tail 6, i.e. the tail is exactly twice the body height. `s(3) = 12`,
full length 24. This supersedes 12/5 whenever lattice hits are required.

The chain cannot reproduce the hit. Closed form, exact:

```text
x_chain = x(T) + T^3/(12N^2)      y_chain = y(T) exactly
s_chain = s(T) - T^3/(12N^2)
```

At T = 3, N = 120 the tip x is 1/6400 = 1.56e−4 short of −6. Only y lands
exactly. So the nodes live on the pitch-1/G lattice; the integer lattice belongs
to the curve, not to the chain.

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
  t = ±√3; the chain hits only y exactly (x is short by T³/(12N²)); "grid" in
  earlier notes means pitch 1/G, canvas is the cell extent.
