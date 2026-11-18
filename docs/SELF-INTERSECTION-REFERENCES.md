# Self-intersection detection for curves and surfaces

A short reference list for the curve finder and the loop/cusp checks. Every entry
was verified online on 2026-11-17.

## The algebraic-elimination family

### Pekerman, Elber & Kim (2008)

**Paper:** *Self-intersection detection and elimination in freeform curves and
surfaces*

**Journal:** *Computer-Aided Design* 40(2), 150–159  
**DOI:** [10.1016/j.cad.2007.10.004](https://doi.org/10.1016/j.cad.2007.10.004)

**What it does.** Gives algorithms for detecting and removing local and global
self-intersections in freeform planar curves and surfaces. The tools are a
**binormal-line criterion** and a direct **algebraic elimination** procedure that
solves the self-intersection constraints without subdivision.

**Why it matters here.** This is the family that `nodes.py` and its resultant
approach belong to. If the curve finder's algebraic path needs a literature
anchor, this is the one.

## The exact cubic case

### Sánchez-Reyes (2024)

**Paper:** *Self-Intersections of Cubic Bézier Curves Revisited*

**Journal:** *Mathematics* 12(16), 2463  
**DOI:** [10.3390/math12162463](https://doi.org/10.3390/math12162463)

**What it does.** Shows that for a cubic Bézier curve the self-intersection
parameters are the roots of a quadratic equation. The curve factorises, and the
parameters come out in closed form. Also notes that only **planar** cubics can
self-intersect, and every self-intersecting cubic is an affine image of the
**Tschirnhausen cubic**.

**Why it matters here.** This is the closest published exact-cubic analogue to
the factorisation the curve finder is building. A cubic self-intersection test
can be exact and fast; higher degrees will need resultants or subdivision.

## The Tschirnhausen cubic

The Tschirnhausen cubic is the canonical self-intersecting cubic. It is also
called Catalan's trisectrix or l'Hospital's cubic.

**Parametric form** (parameter \(t\), scale \(a\)):

\[
x(t) = a(1 - 3t^2), \qquad y(t) = at(3 - t^2).
\]

**Implicit form:**

\[
27ay^2 = (a - x)(x + 8a)^2,
\]

or equivalently

\[
27ay^2 = x^2(x + 9a).
\]

**Key properties.**

- It has one ordinary double point (a node or crunode) at \((-8a, 0)\).
- The loop corresponds to \(t \in [-\sqrt{3}, \sqrt{3}]\).
- The crossing angle inside the loop is **60°**.
- Arc length: \(s(t) = at(3 + t^2)\).
- Curvature: \(\kappa(t) = \dfrac{2}{3a(1 + t^2)^2}\).
- Tangential angle: \(\phi(t) = 2\tan^{-1} t\).
- Loop area: \(\dfrac{72\sqrt{3}}{5}a^2\).

**Why it is special.** Sánchez-Reyes (2024) shows that every self-intersecting
planar cubic Bézier curve is an invertible affine transformation of a segment of
the Tschirnhausen cubic. So if a cubic has a loop, it is secretly this curve
after a shift, rotation, scaling and shear.

## From cubics to higher-degree curves

The Tschirnhausen cubic is the end of the line for a clean universal
classification. For higher degrees, self-intersecting polynomial curves become
much more diverse.

**Pythagorean-hodograph view.** The Tschirnhausen cubic is, up to similarity,
the **only planar cubic PH curve**. Farouki's book proves that for PH curves:

- there are no quadratic PH curves;
- planar PH cubics are exactly Tschirnhausen cubics;
- planar PH **quintics** are the first flexible-enough family for free-form design.

So the lace family, if it is PH, cannot all be Tschirnhausen cubics unless every
lace is cubic. Higher-degree laces must be checked with the PH quintic (or
higher) loop and cusp criteria.

**Affine classification of cubics.** Every polynomial cubic falls into one of
four affine types:

| Type | Singularity | Canonical example | Self-intersection? |
|---|---|---|---|
| Crunodal | node (double point) | Tschirnhausen cubic | yes |
| Cuspidal | cusp | semi-cubical parabola \(y^2 = x^3\) | limiting case |
| Acnodal | isolated double point | acnodal cubic | no (complex tangents) |
| S-shaped | one inflection | graph of \(y = x^3\) | no |

Only the crunodal type has a real self-intersection.

**Higher-degree bounds.** For a general polynomial curve of degree \(n\), there
is no single "Tschirnhausen degree-\(n\) curve" that captures all
self-intersections. Instead one gets bounds. Quine's classical result says a
closed curve traced by a degree-\(n\) polynomial on the unit circle has at most
\((n-1)^2\) self-intersections, and that bound is sharp.

**Geometric generalisation.** The Tschirnhausen cubic is the \(e = 1\) member of
the **ichthyoid curve family** — negative pedal curves of conics with respect to
a focus. For eccentricity \(e \neq 1\) these ichthyoids are quartic or higher,
so the family gives one way to generalise the cubic geometrically, but not an
algebraic canonical form for all self-intersecting curves.

## Elevating the Tschirnhausen cubic

There are two ways to "raise the degree" of a Tschirnhausen cubic. They give
very different results.

### Degree elevation as a Bézier curve

A degree-\(n\) Bézier curve can be rewritten as a degree-\((n+1)\) Bézier curve
without changing the underlying shape. The new control points are convex
combinations of the old ones:

\[
\mathbf{P}_i^{(n+1)} = \frac{i}{n+1}\mathbf{P}_{i-1}^{(n)} + \frac{n+1-i}{n+1}\mathbf{P}_i^{(n)}.
\]

If you degree-elevate a Tschirnhausen cubic to quartic, quintic, or higher, the
curve is **still a Tschirnhausen cubic**. The extra control points are not free;
they are fixed by the old ones. You get more handles, but no new geometry.

### True higher-degree PH curves

A planar PH curve is built from a complex polynomial \(w(t)\) by squaring the
hodograph:

\[
r'(t) = w(t)^2.
\]

If \(w(t)\) has degree \(m\), then \(r(t)\) has degree \(2m+1\). The table below
shows how the parameter count grows:

| Curve degree | Degree of \(w(t)\) | Complex coefficients | Real parameters | Design capability |
|---:|---:|---:|---:|:---|
| 3 | 1 | 2 | 4 | Tschirnhausen cubic only (up to similarity) |
| 5 | 2 | 3 | 6 | First-order Hermite interpolation; can inflect |
| 7 | 3 | 4 | 8 | More loops and self-intersections possible |
| \(2m+1\) | \(m\) | \(m+1\) | \(2m+2\) | Increasing shape freedom |

**Why the jump at degree 5 matters.** A cubic PH curve has no finite inflection
points. A quintic PH curve can inflect, so it can follow an S-shaped path. That
makes quintics the first useful PH family for free-form design.

**The Hermite interpolation problem.** Matching given endpoints and tangent
vectors by a planar PH quintic leads to a system of quadratic equations. Farouki
shows that there are generally **four distinct PH quintic solutions**. Some of
them contain unwanted loops or cusps. The "good" interpolant is selected by a
shape measure such as:

- shortest arc length,
- smallest absolute rotation index,
- lowest elastic bending energy.

So raising the degree from 3 to 5 does not just add parameters — it introduces a
selection problem.

### What higher degree means for self-intersections

A polynomial curve of degree \(n\) can have up to

\[
(n-1)^2
\]

self-intersections (Quine's bound for a closed curve traced by a polynomial on
the unit circle; the bound is sharp). So:

- cubic: at most 1 self-intersection,
- quintic: at most 4,
- septic: at most 9,
- degree \(n\): at most \((n-1)^2\).

Unlike the cubic case, there is **no single canonical curve** that captures all
self-intersecting quintics or septics. The space of self-intersecting curves is
high-dimensional and must be sampled or constrained.

### Exactness

The Tschirnhausen parameterization uses polynomials in \(t\):

\[
x(t) = a(1 - 3t^2), \qquad y(t) = at(3 - t^2).
\]

With a rational choice of \(a\) and \(t\), every point is rational. There is no
\(\sin\) or \(\cos\) of a general angle, so the construction stays on the
integer/rational grid. This matters for the project's exact-curve goals.

## PH curves and loop conditions

### Farouki, *Introduction to Pythagorean-Hodograph Curves* (2008)

**Book:** *Pythagorean-Hodograph Curves: Algebra and Geometry Inseparable*

**Publisher:** Springer  
**ISBN:** 978-3-540-73397-3  
**PDF:** [faculty.engineering.ucdavis.edu/farouki](https://faculty.engineering.ucdavis.edu/farouki/wp-content/uploads/sites/41/2013/02/Introduction-to-PH-curves.pdf)

**What it does.** The standard reference for PH curves: their hodograph
structure, rational offsets, polynomial arc length, and the conditions under
which they develop **loops, cusps and inflections**. The book covers both planar
PH curves (complex representation) and spatial PH curves (quaternions / Hopf
map).

**Why it matters here.** The lace family in this project are PH curves. Before
shipping a lace design, its loop and cusp conditions should be checked against
the criteria in this book.

## Fast NURBS self-intersection

### Li, Jia & Chen (2025)

**Paper:** *Fast Determination and Computation of Self-intersections for NURBS
Surfaces*

**Journal:** *ACM Transactions on Graphics* 44(2), Article 18  
**DOI:** [10.1145/3727620](https://doi.org/10.1145/3727620)

**What it does.** Constructs an **algebraic signature** from the control points.
If the signature is non-negative, the surface has no self-intersection. If a
self-intersection exists, the same signature is reused recursively to compute the
self-intersection locus. The paper compares the method with the OCCT and ACIS
kernels.

**Why it matters here.** This is the current state of the art for NURBS surfaces,
and it makes the same algebraic/numerical split that the curve finder faces. The
signature idea is worth knowing about if the project ever moves from curves to
surfaces.

## Comparison

| Reference | Object | Method | Output |
|---|---|---|---|
| Pekerman et al. 2008 | curves, surfaces | binormal-line + algebraic elimination | detect and remove self-intersections |
| Sánchez-Reyes 2024 | cubic Bézier | factorisation / quadratic formula | exact self-intersection parameters |
| Farouki 2008 | PH curves | hodograph algebra | loop, cusp and inflection conditions |
| Li et al. 2025 | NURBS surfaces | algebraic signature + recursion | existence test and locus computation |

## Links to the project

- `curve_lab/reduction.py` and `scripts/curve_finder.py` are building a curve
  properness / collapse detector. Pekerman et al. and Sánchez-Reyes give the
  algebraic context; Sánchez-Reyes gives the exact cubic target shape.
- `nodes.py` and its resultant work fit the Pekerman et al. algebraic-elimination
  family.
- The lace / PH families should be audited against Farouki's loop/cusp criteria.
- Li et al. is the surface-level reference if the project later needs NURBS
  self-intersection detection.
