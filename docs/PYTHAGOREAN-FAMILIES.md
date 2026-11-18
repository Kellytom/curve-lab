# Pythagorean families

> **draft A** — a working draft, not a final text.
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

## Parabola census

The y-axis crossing identifies the family:

| family | curve | crosses `b` axis at | examples |
|---|---|---|---|
| fixed Euclid `n` | `a=(b/(2n))²−n²` | `2n²` | 392, 800, 1250, 1458, 1922 |
| fixed Euclid `m` | `b=m²−a²/(4m²)` | `m²` | 400, 784, 1225, 1521, 1849 |
| Fässler fixed `N` | `b=|N−a²/(4N)|` | `N` | 1440–1458 cluster |

The observed sequence around 400, 800, 1250, 1458 and 1922 is the fixed-`n`
family at `n=14,20,25,27,31`. The fixed-`m` family also crosses near 400, 784,
1225, 1521 and 1849. A catalogue is infinite by parameter value; the useful
catalogue is by family and intercept law.

## The 800 band: n=20

The fixed-`n=20` family is the strong dark-green curve on the page. Its
y-intercept is `2n²=800`, but that is the degenerate `m=n=20` point, not a
triple. The first actual triple is `(41,840,841)` at **87.21°**; the family
continues to `(2625,2200,3425)` at about **39.97°**. It is a high-angle band,
not the 44°→4° `n=2` sweep.

For this family `b=40m`, so the points are evenly spaced vertically by 40. The
`a` and `c` steps are `2m+1`: 43, 45, 47, …, so the horizontal gaps widen.
Regular in `b`; increasingly wide in `a` and `c`.

## Fässler's second slicing

With the even leg as `a`, put `N=(b+c)/2`. If `a²/(4N)` is an integer, then

```text
(a, |N − a²/(4N)|, N + a²/(4N))
```

is a Pythagorean triple, and every triple can be written this way after
possibly exchanging the legs. The triples lie on

```text
b = |N − a²/(4N)|
```

a parabola reflected in the `a` axis. This `N` is not Euclid's `n`: the
fixed-Euclid-n curves and the fixed-N curves are two different slicings of the
same field.

At `a=2N` the parabola meets the axis with derivative `−1`, so the reflection
is at 45°. Swapping the legs gives the perpendicular family; the axes carry
the crossing pattern. Holding Euclid `m` instead of `n` gives another family; with
`a=2mn`, `b=m²−a²/(4m²)`. That is the other set of smooth parabolic slices
visible in the scatter. Near `N≈1450`, the values `38²=1444`, `2·27²=1458`,
`3·22²=1452`, `5·17²=1445`, and `10·12²=1440` make the parabolas nearly
coincide, producing the dense strip in the scatter.

Source: [Wikipedia, “Pythagorean triple”](https://en.wikipedia.org/wiki/Pythagorean_triple),
distribution section; the references there point to Albert Fässler and
conformal-mapping treatments.

The page overlays the `N≈1450` Fässler curves on the Euclid scatter, so the
two slicings can be compared directly.
 The page also draws every fixed-Euclid-`n` and fixed-Euclid-`m`
family inside the `c≤3500` bound, with the selected `n=1,2,3` curves darker.
 In a `500×500` box, the fixed-`n` family has `n=1..15` because
`2n²≤500`, and the fixed-`m` family has `m=1..22` because `m²≤500`. The ~22
downward curves are the fixed-`m` family; the right-opening curves are
fixed-`n`.

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

## From triangles to curves

The `n=2` sweep supplies 53 exact arm vectors. The chain is now rendered
(`workbench/pythagorean-families.html`, Fig. C1 and C2), built as a **triple
tangent chain**:

    T_k     = (a_k, -b_k)                  the arm as a tangent, +y up
    D_k     = 2 (T_k + T_{k+1})            integer node step
    P0..P3  = N_k, N_k + T_k, N_{k+1} - T_{k+1}, N_{k+1}

At a join the incoming derivative is `3 T_k` and the outgoing derivative is
`3 T_k` — the same vector, so the chain is **C1 exactly**, by construction, and
every control point is an integer. The step factor is 2, not 1: at
`D_k = T_k + T_{k+1}` the inner handles coincide and every span degenerates.

**Curvature** is C1 but not G2. Measured in exact rationals over the full sweep,
the jump at a join is 6.2% of the larger side at the median, 26.1% at worst.

**G2 is reachable, but not integrally.** With a handle length `h_k` per node
(C1 survives, since both sides of a join share `h_k`), the join condition
reduces to `C_k (S - h_k) = C_{k+1} (S - h_{k+2})` with `C_k = T_k x T_{k+1}` —
a two-step linear recurrence. It drives the curvature difference at all 51
joins to exactly zero, but the common denominator of the resulting handles has
84 digits, so clearing it produces an unusable grid. Integer C1 and exact G2
are different currencies here.

## What the sweep is

The angle is algebraic, not logarithmic: with `a = m^2 - n^2` and `b = 2mn` the
arm angle is `atan(2nm/(m^2-n^2))`, which falls like `2n/m` — for `n=2`, about
`229/m` degrees (`theta*m -> 229.2 = 4 rad`). A power fit gives
`theta ∝ m^-0.988` (`R^2 = 0.9999`).

Along the chain, `|kappa| ∝ s^-1.238` (`R^2 = 0.993`) where `s` is arc length:
a spiral, but not a clothoid (`s^+1`), a logarithmic spiral (`s^-1`) or a circle
(`s^0`). The sweep bends hard at the start and nearly straightens by the end.

## What the plot does and does not do

- It maps **all** triples up to `c=3500`, including multiples.
- It shows the scaling rays and the first three fixed-`n` parabolas.
- It selects the `n=2` angle sweep as an explicit sequence.
- It does not claim the whole triple field is one curve.
- The next step is to turn one family sweep into a chain and measure its G1/G2
  joins; the plot only supplies the exact integer arm pairs.
