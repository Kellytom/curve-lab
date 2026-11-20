# Prior art: curves driven by a point on a circle

Question: what does the literature call a parametric curve whose parameter is an
angle on a circle, `x(θ) = f(cos θ, sin θ)`, instead of a linear `t`? And has
anyone forced such a curve onto an integer lattice?

Searched 2026-11-19 (web search only; no paywalled full texts read). Every
"integer lattice" verdict below is "found nothing", not "proved absent".

## The short answer

| Name in the literature | What it is | On an integer lattice? |
|---|---|---|
| Circular harmonics | a curve as a sum of `cos kθ`, `sin kθ` terms | no |
| Fourier descriptors | one epicycle per Fourier coefficient | no |
| Hypotrochoid / epitrochoid | a point on a rolling circle | only via a rational parametrisation |
| Trigonometric Bézier | a Bézier basis of `sin`/`cos`, exact arcs | no (real control points) |
| Lissajous, rational ratio | closed iff the frequency ratio is rational | as exact nodes, not lattice points |
| Chebyshev parametrisation | `cos nθ = T_n(cos θ)`, trig → algebraic | no (only an "integer Chebyshev" problem) |
| Stereographic / Pythagorean | rational points of the unit circle | **yes**, for the circle itself |
| Pythagorean-hodograph | polynomial curve with rational speed | **yes**, but no angle |

**No prior art found** for the whole combination: an integer-grid family of
curves whose parameter steps by rational points of a circle. The mechanism is
classical; the application to a grid family is the gap. Say "no prior art found
in a 2026-11-19 web search", never "novel".

---

## 1. Circular harmonics

**Definition.** A 2-D shape or closed curve written as a sum of terms
`a_k cos kθ + b_k sin kθ`, the planar twin of spherical harmonics; the curve is
the sum of its harmonics, each harmonic one circular motion.

**Citation.** Circular Harmonics, valdes.cc — https://valdes.cc/articles/ch.html
(the same objects appear in shape-matching literature as the frequency-domain
form of a Fourier descriptor; see 2).

**Integer lattice.** No. Coefficients are real magnitudes; the harmonics are
exact circles, so a "harmonic" on a lattice would need its own radius to be a
lattice length. Nothing found.

Note the name collision: "circular harmonics" also means a pitch-class / tonal
analysis in music theory. Do not cite that meaning for geometry.

## 2. Fourier descriptors and epicycles

**Definition.** A closed curve sampled as `z(s) = x(s) + i y(s)`; its discrete
Fourier coefficients are complex amplitudes, and the inverse transform draws the
curve as one rotating circle (an epicycle) per coefficient — a chain of circles
each carried by the last.

**Citation.** C. T. Zahn and R. Z. Roskies, "Fourier Descriptors for Plane Closed
Curves", *IEEE Trans. Computers* C-21 (1972) — PDF:
https://slac.stanford.edu/pubs/slacpubs/0750/slac-pub-0850.pdf
Interactive epicycle view: https://www.dynamicmath.xyz/fourier-epicycles/

**Integer lattice.** No. This is the nearest thing to our construction in the
literature: the epicycle chain is exactly "walk a circle by an angle". Every
amplitude is a real number, and the standard use is shape matching, not exact
integer geometry.

## 3. Rational parametrisation of hypotrochoids and epitrochoids

**Definition.** A trochoid is the path of a point fixed to a circle rolling on
(great) or inside (hypo) a fixed circle:
`x = (R−r)cos θ + d cos((R−r)θ/r)`, `y = (R−r)sin θ − d sin((R−r)θ/r)`.

**Citation.** Mathcurve, "Hypotrochoid" —
https://mathcurve.com/courbes2d.gb/hypotrochoid/hypotrochoid.shtml
Classical: R. C. Archibald, "The Cardioide and Some of Its Related Curves"
(1900), still the standard historical survey (unverified detail).
Epitrochoid family overview: https://www.walter-fendt.de/html5/men/epihypotrochoids_en.htm

**Integer lattice.** Not as trochoids. But: a trochoid with rational `R/r` is an
**algebraic curve**, hence rationally parametrisable (genus 0 when it has a
rational point, e.g. an epicycloid/hypocycloid cusp). A rational parametrisation
*is* an integer-lattice statement — see 7. The rolling circle is the Ptolemaios
epicycle; the "on a circle, odd closing" behaviour is the rational-ratio
condition, same as Lissajous (5).

## 4. Polynomial / rational curves with a trigonometric parameter (trigonometric Bézier)

**Definition.** A Bézier-type basis built from `sin`, `cos` and `1` instead of
`(1−t)^k t^(n−k)`, so that a segment can be an exact arc of a circle; the
uniform cubic "trigonometric Bézier" basis is `{sin²u, cos²u, ...}` with control
points, plus two shape parameters.

**Citation.** X.-A. Han, Y. Ma, X.-L. Huang, "The cubic trigonometric Bézier
curve with two shape parameters", *Applied Mathematics Letters* 22 (2009) —
https://www.sciencedirect.com/science/article/pii/S0893965908001262
Recent survey-adjacent item: "Quantum Trigonometric Bézier Curves",
arXiv:2510.09336 — https://arxiv.org/abs/2510.09336

**Integer lattice.** No. These are design curves with real control points; the
trig basis exists so the circle comes out *exactly*, which is the opposite
worry from keeping coordinates whole.

## 5. Lissajous curves, rational frequency ratios, Chebyshev form

**Definition.** `x = A sin(a t + δ)`, `y = B sin(b t)`; closed exactly when
`a/b` is rational, and when `a, b` are integers the figure is an algebraic curve
whose implicit equation is a polynomial in `x, y` via `cos(nθ) = T_n(cos θ)`.

**Citations.** Wikipedia, "Lissajous curve" —
https://en.wikipedia.org/wiki/Lissajous_curve (closed-iff-rational, Chebyshev
identity). Wolfram MathWorld, "Lissajous Curve" —
https://mathworld.wolfram.com/LissajousCurve.html (periodic iff the frequency
ratio is rational; implicitisation by Chebyshev polynomials).
Erb et al. on Lissajous curves with integer frequencies as cubature nodes:
*Dolomites Research Notes on Approximation* (2015) — https://arxiv.org/abs/… (the
exact item was seen only through an aggregator page; **unverified**).

**Integer lattice.** Partly the closest match, but as *sampling nodes*, not as
lattice points: the Chebyshev-Lissajous nodes used for cubature have exact
algebraic (not integer) coordinates. No integer-lattice Lissajous found.

## 6. Chebyshev / trigonometric parametrisation

**Definition.** Using `T_n(cos θ) = cos nθ` to trade a trigonometric polynomial
for a polynomial one; a curve given by two trigonometric polynomials of degree
`n` becomes an algebraic curve of degree `n`, and conversely every curve with a
trigonometric parametrisation is algebraic.

**Citation.** T. J. Rivlin, *The Chebyshev Polynomials* (Wiley, 1974); the
identity and its use in Lissajous implicitisation as cited in 5.
Chebyshev's own linkage work is the historical root: "Chebyshev linkage",
https://en.wikipedia.org/wiki/Chebyshev_linkage

**Integer lattice.** Only the *integer Chebyshev problem* exists — minimising
`‖p‖` over integer-coefficient polynomials on `[−1,1]` (Borwein & Erdélyi,
*Polynomials and Polynomial Inequalities*, 1995). That is a different question
(coefficients integer, curve not on a lattice). No Chebyshev-parametrised curve
on a lattice found.

## 7. The bridge that does reach integers: stereographic / Pythagorean parametrisation

**Definition.** Every rational point of the unit circle is
`((1−t²)/(1+t²), 2t/(1+t²))`; with `t = p/q` this is
`((q²−p²), 2pq, q²+p²)/|·|`, i.e. a Pythagorean triple. This is the *only*
standard way a circle-driven parameter becomes exact on a lattice.

**Citations.** "Pythagorean triple — rational points on the unit circle",
https://en.wikipedia.org/wiki/Pythagorean_triple
"Rational curve" / conic parametrisation by a line of slope `t`,
https://en.wikipedia.org/wiki/Algebraic_curve#Rational_curves
NURBS exact circle, same weight form: Piegl & Tiller, *The NURBS Book*, §7.4
(unverified page number).

**Integer lattice.** Yes, at the level of the *circle*, not the curve: the
triples give whole-number points on the circle. Scaling the whole construction by
`q²+p²` makes the circle integer at the cost of a growing grid — which is the
grid-bill question in `state/ACHIEVEMENTS-int.md`, not a new one.

## 8. Pythagorean-hodograph (PH) curves — the polynomial analogue

**Definition.** A polynomial curve whose derivative has rational length, so arc
length is a polynomial; equivalently, a curve whose hodograph is a Pythagorean
triple of polynomials.

**Citations.** Wikipedia, "Pythagorean hodograph curve" —
https://en.wikipedia.org/wiki/Pythagorean_hodograph_curve
R. T. Farouki, "Introduction to Pythagorean-hodograph curves" —
https://faculty.engineering.ucdavis.edu/farouki/wp-content/uploads/sites/51/2021/07/Introduction-to-PH-curves.pdf
R. T. Farouki, *Pythagorean-Hodograph Curves: Algebra and Geometry Inseparable*
(Springer, 2008).

**Integer lattice.** Closest existing *exactness* programme: PH curves are
polynomial, so integer control points stay integer under the Bernstein form.
But PH is about the tangent, not about a circle parameter — no trig, and the
curve does not re-derive from an angle.

---

## Verdict for curve-lab

The literature has a name for each half of our construction, and no name for the
whole of it:

- **"circle-driven parameter"** → circular harmonics / Fourier descriptors
  (shape analysis, real amplitudes, no exactness claim).
- **"trigonometric polynomial parametrisation"** → trigonometric Bézier /
  Chebyshev-Lissajous (exact circles, real control points, no lattice).
- **"exact rational circle parameter"** → stereographic / Pythagorean triples and
  PH curves (exact, integer-friendly, but about the circle or the tangent, never
  about a whole curve family on one grid).

**No prior art found** for the combination we use: an integer-lattice curve whose
parameter steps by rational points of a circle (p-triples), so the curve is
simultaneously exact, integer, and angle-driven. The nearest neighbours are PH
curves (exact, integer control net, no trig) and the stereographic circle
parametrisation (exact, integer, angle-driven, but only for the circle itself).

That is the honest claim: the *mechanism* is classical (Ptolemy → Chebyshev →
NURBS weights), the *application* to a grid family of algebraic curves appears
to be ours. Say "no prior art found in a 2026-11-19 web search", not "novel".
