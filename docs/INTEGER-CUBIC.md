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
