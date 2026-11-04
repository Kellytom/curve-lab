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

The `n=2` sweep supplies 53 exact arm vectors. The first assembly candidate is
a **triple tangent chain**: each triple is the endpoint tangent of a cubic, and
the shared triple repeats at each join, so the chain is C1 by construction.
With a step of `100000`, the x extent is `5,200,000`; every control point is an
integer. The alternative is a **triangle strip** that shares triangle vertices
and smooths the resulting polyline afterward. The chain is not rendered yet;
the TODO records the choice.

## What the plot does and does not do

- It maps **all** triples up to `c=3500`, including multiples.
- It shows the scaling rays and the first three fixed-`n` parabolas.
- It selects the `n=2` angle sweep as an explicit sequence.
- It does not claim the whole triple field is one curve.
- The next step is to turn one family sweep into a chain and measure its G1/G2
  joins; the plot only supplies the exact integer arm pairs.
