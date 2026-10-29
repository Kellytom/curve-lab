# pythagorean-spiral

Clothoid-shaped chains built from Pythagorean triangles, in exact rational
arithmetic. No `sin`, no `cos`, no floats in the geometry: a heading is a pair
of `Fraction`s, and every node is rational.

This directory is a **candidate replacement** for the curve layer, kept beside
`clothoid_lab/` so the two can be compared. Nothing here is imported by the
package yet.

## Run

```sh
cd pythagorean-spiral
../.venv/bin/python -m pythagorean_spiral.cli --mode lobe --steps 15 --length 3121
../.venv/bin/python -m pythagorean_spiral.cli --mode hook --multiplier 3 --n-out 5 --out /tmp/hook.svg
../.venv/bin/python -m pythagorean_spiral.cli --list-closures
../.venv/bin/python -m unittest discover -s tests -t .
../.venv/bin/python scripts/compare_bertolazzi.py   # from the repo root
```

## What it does

A chain is a polygon of equal chords. Chord `k` runs at heading
`alpha * T(k-1)` where `T(j) = j(j+1)/2` and `alpha` is the acute angle of a
primitive right triangle. That is the clothoid law read as a difference
equation: heading quadratic in the step index, so curvature linear in arc
length.

Three named constructions, each ending **exactly** on an axis:

| mode | turning | end | chords |
|---|---|---|---|
| `spiral` | `0,1,2,…` | open | n |
| `lobe` | `0..n-1`, then `-(n-1)..0` | east, sharp apsis | 2n |
| `hook --multiplier m` | `0..N`, then `-m,-2m,…` | east, sharp apsis | N+1+n_out |
| `g2` | `0..n-1`, `n-1..0`, `-1..-j` | east, **G2** apsis | 2n+j |

Exact closure is not a matter of tuning: see `docs/AUDIT.md` §3. With one
triangle the only axis landing is total turn zero, so `hook` and `g2` exist only
on the integer solutions of `T(N) = m*T(n_out)` and `j(j+1) = 2n(n-1)`.

## Files

| Path | What |
|---|---|
| `pythagorean_spiral/exact.py` | `Dir`: an exact unit direction, closed under multiplication |
| `pythagorean_spiral/triples.py` | primitive triples, thinness, double-angle twin |
| `pythagorean_spiral/spiral.py` | `Spiral`: the chord chain; exact nodes; the equivalent clothoid |
| `pythagorean_spiral/closure.py` | which turn sums cancel, exactly |
| `pythagorean_spiral/design.py` | the four named constructions |
| `pythagorean_spiral/spans.py` | chords to cubics, in `clothoid_lab`'s span format |
| `pythagorean_spiral/svg.py` | a small writer; y is flipped here, once |
| `docs/AUDIT.md` | every claim in the source notes, checked, and the verdicts |
| `scripts/compare_bertolazzi.py` | the chain against the engine already in this repo |

## What is exact, and what is not

Exact: the triangle rotations, the node coordinates, the turn bookkeeping, the
closure conditions, the final heading (it is literally east, not 0.000°).

Not exact: the curve. The chain is the **Euler polygon** of the clothoid with
`kappa0 = alpha/(2L)`, `kd = alpha/L²`. Measured against Bertolazzi on the
79-3120-3121 chain: node heading error `1e-13` degrees, node position error up
to `1.0032` chords. So the headings are the clothoid's, and the vertices are a
polygon that tracks it.

The chain stops resolving a curve when `alpha*k` approaches a radian, around
`k = 1/alpha = 39` steps for the thin triangle. Past that the chords jump the
local radius and the picture is aliasing, not a spiral. The CLI prints the
widest chord angle and warns past ~52°:

| construction | widest chord angle | reads as a curve |
|---|---|---|
| `lobe --steps 7` | 8.7° | yes |
| `lobe --steps 15` | 20.3° | yes |
| `hook --multiplier 3 --n-out 5` | 21.8° | yes |
| `hook --multiplier 8` | 58.0° | no — the fast exit aliases |
| `spiral --steps 32` | 45.0° | marginal, two laps |
