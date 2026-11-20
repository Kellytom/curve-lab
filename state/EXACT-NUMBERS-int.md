# EXACT NUMBERS — what we use instead of complex steps

One page, so nobody has to reconstruct it. The operator's rule, and the arithmetic
behind it.

## The rule

**No complex steps in this code, and no square roots riding along in a position.**
A curve is driven by ratios of whole numbers, and nothing else. This is not a
matter of taste: a complex step imports an irrational length, and once it is in a
position it is there for ever.

## Why the complex step was dropped

Take the step `2 + i`. Its length is `√5` — not a ratio of whole numbers. After one
step the position has length `√5`; after two, `5`; after three, `5√5`; and so on.
The square root never leaves. Any figure built that way can be *sampled* to any
precision, but it cannot be written as exact ratios, so it cannot be cut, joined or
measured on a grid.

## What is used instead

| instead of | use | example |
|---|---|---|
| a complex step | a **p-triple**, written as three whole numbers | `(3, 4, 5)`: a turn with legs 3 and 4 and hypotenuse 5 |
| the length `√5` | a **whole hypotenuse** | `3² + 4² = 5²`, so the length is exactly 5 |
| the unit step | `(x, y, z)` divided by its hypotenuse | x becomes `3/5`, y becomes `4/5` — both ratios |
| the imaginary unit | the **quadrature component** | the part 90° out of phase, named in words |
| a complex number in prose | a **Gaussian rational** (whole parts: Gaussian integer) | `3/5 + (4/5)·i` is a Gaussian rational written as a pair |
| a rotation by a decimal angle | a **Gaussian rotation** | multiplication by `(3+4i)/5`, or the quarter turn as a p-triple `(0, 1, 1)` |

The vocabulary is settled in `state/DESIGN-int.md` § *Naming: quadrature, rotation,
phasor*: "imaginary" is banned from new prose and code; the words are complex
number, Gaussian rational, Gaussian integer, Gaussian rotation, quarter turn,
quadrature component, phasor.

## How to convert a complex step

A step `a + bi` is exact only when `a² + b²` is a perfect square. Then:

1. find `z` with `z² = a² + b²` — the hypotenuse,
2. write the step as the triple `(a, b, z)`,
3. the position moves by `(a/z, b/z)` — two ratios,
4. if `a² + b²` is **not** a square, the step is refused; choose another triple.

Example: `7 + 24i` → `7² + 24² = 625 = 25²` → the triple `(7, 24, 25)` → the step is
`7/25` and `24/25`, and the turn is `atan(24/7)`, which is a readout, never an input.

## Where the rule is enforced

- **The pages and their scripts** (`app/src/`): `scripts/check_no_imaginaries.py`
  fails on `1j`, `Math.sqrt(5)`, `complex(`, `cmath`, or the word "imaginary" in
  new text. Run by `scripts/prepush.sh`.
- **The prime-mover scripts** (`scripts/prime_loop.py`, `scripts/circle_grid_walk.py`,
  `scripts/flip_demo.py`): written with whole numbers and `Fraction` only.
- **The spec for the engine** (`state/SPEC-prime-mover-int.md`): rule 9 — `i` is the
  dial and nothing else; a step is written as a triple.

## Not yet converted — stated, not hidden

The PH-curve maths still uses Python complex numbers internally:
`curve_lab/ph_hermite.py`, `curve_lab/measure.py` (a bend result), `scripts/ph_carry.py`,
`scripts/g3_cut.py`, `scripts/ph_families.py`, `scripts/pm4_search.py`,
`scripts/pm_deep_search.py`, and their tests.

Those are on the record rather than quietly excluded. They are the next
conversion: each one needs a p-triple or a rational replacement found before the
complex form is removed, and removing it without the replacement would break the
figure. The rule above applies to new code now, and the list above is the debt.
