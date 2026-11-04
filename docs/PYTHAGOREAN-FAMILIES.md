# Pythagorean families

The workbench page is `workbench/pythagorean-families.html`; the generator is
`scripts/pythagorean_families.py`; the data is `curve_lab/pyth_triples.py`.

## The two patterns

Plot every triple as `(a,b)`.

**Rays from the origin.** Every multiple `k(a,b,c)` of a primitive triple lies
on the same ray. A single primitive is a ray; its multiples are points along
it.

**Fixed-`n` parabolas.** Euclid's formula is

```text
a = m² − n²
b = 2mn
c = m² + n²
```

For a fixed `n`, varying `m` gives

```text
a = (b / (2n))² − n²
```

which is a parabola in the `(a,b)` plane. The page draws `n=1,2,3`.

## The n=2 sweep

The selected `n=2` sequence starts at:

```text
m=5: (20,21,29) ≈ 43.60°
```

and runs down the same parabola to:

```text
m=57: (3245,228,3253) ≈ 4.02°
```

The points are exact integer triples but irregularly spaced along the curve.
They are the first candidate arm/angle sequence for an integer cubic chain.

## What the plot does and does not do

- It maps **all** triples up to `c=3500`, including multiples.
- It shows the scaling rays and the first three fixed-`n` parabolas.
- It selects the `n=2` angle sweep as an explicit sequence.
- It does not claim the whole triple field is one curve.
- The next step is to turn one family sweep into a chain and measure its G1/G2
  joins; the plot only supplies the exact integer arm pairs.
