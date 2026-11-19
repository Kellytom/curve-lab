# RESEARCH-int — has anyone else made these curves?

Search run 2026-11-19, on the operator's question: *"I find it difficult to
believe no one else has found all these good curves… find anyone else who has
made or researched these specific curves. If they haven't maybe there is
something close that talks about combining curves, adding a near zero offset,
wobble, higher degree parametric curves with many loops."*

Searched the open web and the GitHub API. Terms are listed in §4 so a later
session does not repeat them. No code was changed for this note.

---

## 1. Findings

| # | What it is | Link | How close |
|---|---|---|---|
| 1 | **Pythagorean-hodograph (PH) curves.** A planar polynomial curve whose derivative is `(u² − v², 2uv)` for polynomials `u, v`; its speed is the polynomial `u² + v²`, so arc length is a polynomial. Named by Farouki and Sakkalis, 1990. | https://en.wikipedia.org/wiki/Pythagorean_hodograph_curve | **Identical.** Our curve is built exactly this way: `x += (u² − v²)`, `y += 2uv`, and `speedX`/`speedY` *are* `u` and `v` (`scripts/near_zero.py`, `position()`). The family has a name and a forty-year literature. |
| 2 | Farouki's introduction to PH curves (book chapter, PDF) | https://faculty.engineering.ucdavis.edu/farouki/wp-content/uploads/sites/51/2021/07/Introduction-to-PH-curves.pdf | The standard reference for the algebra, the control polygon, and the offset behaviour — "self-intersections of the untrimmed offset" is a figure in it. |
| 3 | **Offsets / parallel curves** — the locus at a fixed normal distance. Cusps appear where the offset radius equals the radius of curvature; the offset self-intersects beyond that. In CAD the term is *offset curve*. | https://en.wikipedia.org/wiki/Parallel_curve | **Identical to our rails.** A rail at a small character offset is an offset curve. This is the field's name for it. |
| 4 | **Bound on offset distance to avoid self-intersection** — given a spine that does not self-intersect, there is a stated bound on `d`. | https://doi.org/10.1016/j.cagd.2023.102196 | Close: it answers "how near zero can the offset be before it crosses itself", the question our near-zero work asks from the other side. |
| 5 | **Reach, thickness, global self-distance.** The reach of a set is the largest `r` such that every point nearer than `r` has a unique closest point. For a curve it is set by the radius of curvature *and* by how near the curve comes to itself. | https://arxiv.org/pdf/1005.4609 (figure 2 states both bounds) · https://geometrica.saclay.inria.fr/team/Fred.Chazal/papers/ccslmt-icutn-17/inference.pdf (§5 defines reach) | **This is our "grace", named.** `grace → 0` means the reach is small: the curve nearly touches itself, and any tube around it pinches. The literature calls the two branches an "almost self-intersection". |
| 6 | **Quine's bound.** A complex polynomial of degree `n` restricted to the unit circle is a closed curve with at most `(n − 1)²` self-intersections (few exceptions). | https://arxiv.org/pdf/1902.02468 (abstract and §1) | Close in spirit: a hard ceiling on crossing pairs from the degree, the same trade our search makes. Our `t` is a real interval, not the circle, so the bound is not directly ours, but the question is the same one. |
| 7 | **Node bound for algebraic curves.** An irreducible plane curve of degree `d` has at most `(d − 1)(d − 2)/2` double points, and the bound is attained by rational curves. | https://en.wikipedia.org/wiki/Algebraic_curve | Close: a parametric curve of degree `d` is an algebraic curve of degree at most `d`. This gives the ceiling our many-crossing search is walking toward, and says how many pairs are still available at each degree. |
| 8 | **Lissajous self-intersection counts.** Closed form for the node count of `(sin pt, sin qt)`: `2pq − p − q` when both are odd, `(p − 1)(q − 1)/2` when `p` is even and `q` odd. | https://mathoverflow.net/questions/38118 · https://math.unipd.it/~erb/Lissajous.html (Table 1) | Close: a *trigonometric* family with an exact crossing count. Different function class (not polynomial, not exact on our grid) but the nearest worked example of "count the pairs from the frequency rows". |
| 9 | **Trochoids / spirograph / guilloché double points.** The intersection count of hypotrochoids and epitrochoids, worked out in a recent paper with drawings. | https://dresden.academic.wlu.edu/files/2024/07/TrochoidsThirdSubmission.pdf | Close: the classical many-loop decorative curve, with a count. Rational, not polynomial; the count formula is the useful part. |
| 10 | **Guilloché as a design tradition** — engine-turned bands of interlaced curves on banknotes and watch dials; built from hypotrochoids, often layered. | https://en.wikipedia.org/wiki/Guilloch%C3%A9 · https://mathworld.wolfram.com/GuillochePattern.html | Close: our frames and character rails are a guilloché band rebuilt from an exact curve instead of a trochoid. The tradition is old; the exact-grid version is not. |
| 11 | **Turk's head knots** — a single closed curve woven on a `p × q` grid; crossing count `q(p − 1)`; the knot is a knot iff `gcd(p, q) = 1`. | https://arxiv.org/pdf/2409.20106 (survey) · https://mathworld.wolfram.com/TurksHeadKnot.html | Close to our `lace-*` family: one stroke, many crossings, a lattice rule that says when it closes. The field counts crossings of a fixed woven pattern; we count crossings of an arbitrary polynomial. |
| 12 | **GitHub: PH implementations** — `suremarc/pythagorean-hodographs` (Rust), `firepick1/ph5` (C++, quintics), `ahrvoje/ph-splines` (Python), `areijonen/ph-curves` (TeX). Five repositories match "pythagorean hodograph" in total. | https://github.com/suremarc/pythagorean-hodographs · https://github.com/firepick1/ph5 | Close but aimed elsewhere: all are CAD/spline interpolation libraries. None is a catalogue of many-loop curves, none counts crossings, none is about ornament. |
| 13 | **GitHub: spirograph / harmonograph / guilloché toys** — `binarymax/guilloche`, `gwygonik/Spiroh`, `ttencate/harmonograph`, `LogarythmTech/GuillochePatterns`, `seedcode/SpirographN`. | https://github.com/binarymax/guilloche · https://github.com/ttencate/harmonograph | Close in look, far in method: every one is trigonometric (circles, sines, damped sines). None searches a polynomial family, none is exact, none ranks by crossings. |
| 14 | **Computer-generated ornament.** Craig Kaplan, *Geometric Ornamental Design* (dissertation); Wong, *Computer-Generated Floral Ornament*; Anderson, *User-Driven Two-Dimensional Computer-Generated Ornamentation*. | https://parametrichouse.com/geometric-ornamental-design/ · http://eecs.umich.edu/courses/eecs498-2/papers/wong98.pdf · https://digitalcommons.calpoly.edu/cgi/viewcontent.cgi?article=1204&context=csse_fac | **Close to our ornament half**: apophyges, spines, fillets, borders, all generated from curves. None starts from exact integer polynomial curves on a stated grid. |
| 15 | **Mathematical art from parametric equations** — Hamid Naderi Yeganeh builds figures from thousands of trigonometric curves and hand-tuned formulas. | https://en.wikipedia.org/wiki/Hamid_Naderi_Yeganeh | Close in aim (many curves, one stroke, ornament-like figures), different method: hand-tuned trigonometry, no exact arithmetic, no crossing measure. |
| 16 | **Minkowski sum of plane curves** — the set of all point sums `a + b`; the boundary is built from translated pieces of the two curves. | https://en.wikipedia.org/wiki/Minkowski_addition · https://www.sciencedirect.com/science/article/pii/S037704270600690X | **Not the same as our addition.** Our `A + B` adds values at the *same* parameter; the Minkowski sum adds *every* pair. Worth reading only to know the difference, otherwise the two get confused. |
| 17 | **Singular points of a plane curve** — the full vocabulary: *crunode* (two branches cross), *acnode* (an isolated speck), *cusp* / *spinode*, *tacnode* (two branches touch), *rhamphoid cusp*, *multiple point of order k*, *point of undulation*, *flecnode*. | https://en.wikipedia.org/wiki/Singular_point_of_a_curve | **This is the vocabulary for the fold.** Every way a stroke can meet itself already has a name. |
| 18 | **Cusp** and **rhamphoid cusp** — local models `y² = x³` and `y² = x⁵`; one tangent, two coincident branches. | https://en.wikipedia.org/wiki/Cusp_(singularity) · https://en.wikipedia.org/wiki/Rhamphoid_cusp | Close, and **not what our middle is** — our speed never vanishes (§2a, computed). Do not call the fold a cusp. |
| 19 | **Genus with multiple points**: `g = (d−1)(d−2)/2 − Σ C(m_P, 2)` for ordinary multiple points; Chasles–Cayley–Brill. | https://aeb.win.tue.nl/2WF02/genus.pdf · https://encyclopediaofmath.org/wiki/Chasles-Cayley-Brill_formula | **This is the budget our recipe spends.** A point of multiplicity `m` at the middle costs `m(m−1)/2` nodes — exactly as much as that many crossings. |
| 20 | **Symmetrical coupler curves and singular-point classification** — symmetric four-bar coupler curves, classified by crunode, tacnode and spinode. | https://doi.org/10.1115/1.2167651 | **The closest industrial relative found.** Symmetric, many-noded plane curves produced by a mechanism, and classified by the same singular points. |
| 21 | Coupler-curve synthesis and **cognate linkages** — three different four-bars trace the same coupler curve. | https://vbn.aau.dk/en/publications/coupler-curve-synthesis-of-four-bar-linkages-via-a-novel-formulat/ · https://en.wikipedia.org/wiki/Cognate_linkage | Close: an engineered source of symmetric noded curves, with a design literature of its own. |
| 22 | **Lemniscate of Gerono** — degree four, genus zero, bisymmetric figure-eight with one double point at the middle. | https://en.wikipedia.org/wiki/Lemniscate_of_Gerono · https://mathcurve.com/courbes2d.gb/gerono/gerono.shtml | The **simplest named member** of our family: cheap, symmetric, folded at the middle, one node. |
| 23 | **Spiro / libspiro** — Levien's clothoid-based curve tool for type design; it reasons about curvature, cusps and loops explicitly. | https://levien.com/spiro · https://github.com/fontforge/libspiro · https://levien.com/phd/thesis.pdf | Close in the trade: a designer's tool for exactly this shape language. Different curve class, no exact grid, no crossing count. |
| 24 | **Type-design practice**: a well-formed glyph contour must not intersect itself; overlaps are removed with "Remove Overlap" (Cmd-Shift-O). | https://tug.org/TUGboat/tb16-3/tb48kinc.pdf · https://glyphsapp.com/learn/drawing-good-paths | **Negative hit, and a useful one**: the trade treats a loop in an *outline* as a defect, so nobody there builds loops deliberately at contour level. |
| 25 | **Flat spot** — a CAD term for a point of zero curvature on a curve or surface, named as an artifact. | https://doi.org/10.1080/00207160701828157 | Close: `m ≥ 2` gives exactly this at the middle (§2a, computed). The word is a criticism, so use it with care. |
| 26 | **Hyperflex / point of undulation** — the tangent line has contact of order ≥ 4 with the curve; an ordinary flex is order 3. | https://en.wikipedia.org/wiki/Singular_point_of_a_curve · https://arxiv.org/html/2502.02075 | **The right name for the fold at `m = 2` and `m ≥ 3`** (§2a, computed). |
| 27 | **Curves with prescribed singularities** — the enumerative trade: how many plane curves of degree `d` carry a fixed set of singular points (Kontsevich; Caporaso–Harris). | https://math.berkeley.edu/~chd/expo/kontsevich_formula.pdf | Distant, but it is the field that already asks "fix the multiplicity at a point, count the rest". |
| 28 | **Figure-eight / bowtie** family pages — bowtie `ρ = 2 sin 2t + 1`, a bisymmetric figure-eight. | http://balmoralsoftware.com/mathsite/boundary/bowtie/bowtie.htm | Popular naming only: no construction method, no exact grid. |

### 1a. What the fold at the middle actually is (computed, not recalled)

The job brief called the middle a fold where the speed "vanishes to order `m`".
In our recipe it does not vanish, and that changes the name of the object.
`scripts/root_search.py` builds `candidate(p, q, m)` as

```
v(t) = (t − p/q)(t − (q−p)/q)(t − 1/2)^m      the y speed
u(t) = 1 − 2t + 2t² = 2(t − 1/2)² + 1/2       the x speed
```

`u` is positive everywhere (`u(1/2) = 1/2`, `u'(1/2) = 0`, a minimum), so
`u + iv` never vanishes, the parametric speed `u² + v²` never vanishes, and the
curve is **regular at the middle**. There is no cusp. What is special there is
the order of contact with the horizontal tangent, and (for `m ≥ 2`) the
curvature.

Printed on 2026-11-19 by a `Fraction` check on `candidate()`; the curvature in
PH form at `t = 1/2` reduces to

```
kappa(1/2) = 2(u'v − u v') / (u² + v²)²  =  −16 · v'(1/2)
```

| family | `m` | `v'(1/2)` | `v''(1/2)` | `kappa(1/2)` | contact order | what the middle is |
|---|---|---|---|---|---|---|
| `lace-1of8-m1` | 1 | −9/64 | 0 | 9/4 | 2 | smooth top; ordinary tangency, curvature non-zero |
| `lace-1of8-m2` | 2 | 0 | −9/32 | 0 | 3 | **flex** (ordinary inflection) — and a CAD flat spot |
| `lace-1of8-m3` | 3 | 0 | 0 | 0 | 4 | **hyperflex / point of undulation** |
| `lace-1of9-m1` | 1 | −49/324 | 0 | 196/81 | 2 | smooth top |
| `lace-1of9-m2` | 2 | 0 | −49/162 | 0 | 3 | flex |
| `lace-1of9-m3` | 3 | 0 | 0 | 0 | 4 | hyperflex |

Two more facts from the same check, both useful for the page text:

- the speed squared at the middle is exactly `u(1/2)² = 1/4` for every `m`, the
  smallest speed on the stroke, so the pen is slowest at the fold and the legs
  run away from it;
- `y(t) − y(1/2)` starts at order `m + 1` in `(t − 1/2)`, which is where the
  contact orders in the table come from.

Reproduce:

```sh
.venv/bin/python - <<'PY'
from fractions import Fraction as F
import math
def poly(roots):
    c=[F(1)]
    for r in roots:
        n=[F(0)]*(len(c)+1)
        for i,a in enumerate(c): n[i+1]+=a; n[i]-=a*r
        c=n
    return c
def der(c,k):
    for _ in range(k): c=[c[i]*i for i in range(1,len(c))]
    return c
def ev(c,t): return sum(a*t**i for i,a in enumerate(c))
for q in (8,9):
    for m in (1,2,3):
        v=poly([F(1,q),F(q-1,q)]+[F(1,2)]*m)
        print(f"lace-1of{q}-m{m}", m, ev(der(v,1),F(1,2)), ev(der(v,2),F(1,2)), -16*ev(der(v,1),F(1,2)))
PY
```

---

## 2. Verdict

### 2a. Does the field have a name for "symmetric, long-legged, folded at the middle, cheap integer coefficients"?

**No single name. It has a name for every part, and the parts cover it.** That is
the honest answer, and it is a better one than a borrowed label that half fits.

- *The fold at the middle* is **not a cusp** in our recipe: the speed never
  vanishes (§1a, computed). It is a point of high-order contact with the
  horizontal tangent — an ordinary **tangency** at `m = 1`, an **inflection**
  (flex) at `m = 2`, a **hyperflex / point of undulation** at `m = 3` and above.
  If the recipe is ever changed so that `u` can vanish too, the word becomes
  **cusp**, and a coincident-tangent cusp is a **rhamphoid cusp**.
- *A stroke that nearly touches itself* is a **tacnode** in the limit; if it
  crosses, a **crunode**; if it leaves an isolated speck, an **acnode**. Those
  three are the classification used for symmetric coupler curves (#20).
- *Many crossings* are **nodes**, counted by the genus budget
  `g = (d−1)(d−2)/2 − Σ C(m_P, 2)` (#19). The multiplicity we place at the middle
  is paid for out of the same budget: `m` at the middle costs `m(m−1)/2` nodes.
- *"Long shallow legs"* has no term of its own in the curve literature; it is a
  consequence of the speed being smallest at the fold (§1a) and growing outward.
- *"Symmetric"* is exact here: the roots come in pairs `r, 1 − r`, so `v` is even
  or odd about `t = 1/2`.

**Recommended names to use from now on.** In an academic sentence: "a
mirror-symmetric Pythagorean-hodograph curve with a high-order contact at the
midpoint". In a trade sentence: "a folded stroke" or "a folded middle". In the
data: **nodes**, not "crossing pairs", when writing for a mathematician; keep
"crossing pairs" for the operator's readouts, and say both once.

**Do not** say "cusp" for our middle, and do not say "fold" without the gloss:
in singularity theory a *fold* is the `A2` germ of a map from the plane to the
plane, not a feature of a plane curve. A mathematician will read "fold" as a
catastrophe, not as our turning point.

### Already known, with the field's name

- **The curves are PH curves.** `speedX`/`speedY` are the hodograph pair; the
  integral `(u² − v², 2uv)` is the textbook construction. Use the name
  "Pythagorean-hodograph curve" in the docs and in the pitch; it is a
  forty-year-old CAGD term, not a coinage.
- **The rails are offset curves** (parallel curves). Their cusp and
  self-intersection behaviour is textbook, including the distance at which the
  offset first crosses itself.
- **"Grace" is the reach (thickness, global self-distance).** The named quantity
  is the radius below which the tube around a curve stops being simple. Our
  measure is the same fact read from the curve's own middle.
- **The crossing ceiling is a named theorem, twice over**: Quine's `(n − 1)²`
  for a polynomial on the circle, and `(d − 1)(d − 2)/2` nodes for a plane
  curve of degree `d`.
- **One-stroke many-crossing ornament** is Turk's head knotwork (exact crossing
  count `q(p − 1)`) and guilloché (spirograph bands). Both are the ancestor of
  the `lace-*` idea.

### Close, and worth reading

- Farouki's PH introduction (#2) for the algebra and the offset figures.
- The offset-distance bound (#4) for "how small can the offset be".
- The reach/thickness papers (#5) for the language of nearly-touching curves.
- Kaplan (#14) and Wong (#14) for ornament grammar and borders.
- The trochoid and Lissajous counts (#8, #9) for the shape of a closed-form
  crossing count — a model for what an exact PH count might look like.

### Appears original (state plainly: no prior art found)

- **A catalogue of PH curves on one exact grid, ranked by crossing pairs and
  inflections, for ornament.** PH repositories are spline tools; ornament
  papers are trigonometric or hand-drawn. Nothing joins the two.
- **The mirrored root recipe** — roots at `p/q` and `(q − p)/q`, plus a stack at
  `1/2`. Mathematically this is a polynomial even or odd about `t = 1/2` (a
  polynomial in `(t − 1/2)²`) whose multiplicity at the midpoint sets the contact
  order there (§1a). I found no name for it as a *curve generator*, and no paper
  using it to build many-loop curves. The ingredients are elementary; the recipe
  and its use as a search move look like ours.
- **Choosing the multiplicity at the middle and spending the rest on nodes.**
  Enumerative geometry does ask "fix the singularities, count the curves" (#27),
  and the genus formula (#19) is the budget. But I found no one using the
  multiplicity as a *design dial* on one curve — raising `m` to trade crossings
  for a flatter fold. That use is ours.
- **Curve addition `A + B` and `A + iB`.** Adding two complex polynomials is
  trivially closed (`p = pA + i·pB` is another complex polynomial), so the
  operation has no literature of its own; the nearest named thing is the
  Minkowski sum, which is *not* what we do. Using it to breed new ornament
  strokes from two good ones appears to be ours.
- **"Wobble"** — moving the closest-approach point off centre by a small
  rational rotation or offset. In the literature that is a plain perturbation of
  the curve; as a *control on where the near-touch happens* it appears to be our
  term and our move.
- **The near-zero/grace reading as a design value** (a curve that passes within
  a small share of its own size of its middle without touching) is the reach
  quantity used as an aesthetic score. The mathematics is known; the use as a
  filter is not something I found.

---

## 3. What this means for the pitch

The honest sentence is: **the curve class is standard, the use is not.**

PH curves, offsets, reach and Quine's bound are all established mathematics,
and the docs should say so and cite Farouki — claiming them as new would be
laughed at by any CAD reader. What is not established is the thing this project
actually makes: one exact grid, an exhaustive search over a root recipe, curves
chosen by crossing count and inflection count, dressed with offset rails and a
generated border, and read as a grammar of ornament. No paper or repository
found does that.

Two sentences for the pitch, both defensible:

- "A mirror-symmetric Pythagorean-hodograph curve on an exact integer grid, with
  the multiplicity at its midpoint set by design — a smooth tangency at one
  setting, an inflection at the next, a hyperflex beyond that — and the rest of
  the node budget spent on crossings."
- "The curve class is named (PH), the fold is named (tangency, flex, hyperflex),
  and what a stroke does when it meets itself is named (crunode, tacnode,
  acnode). The grammar that chooses between them on one exact grid is not."

---

## 4. Search terms tried (do not repeat)

Web:
`Pythagorean hodograph curves Farouki polynomial parametric speed` ·
`polynomial parametric plane curve maximum number of self-intersection double points degree bound` ·
`Quine bound number of self-intersections polynomial parameterization plane curve` ·
`parametric polynomial curve many self-intersections generator` ·
`number of self-intersections of epitrochoid hypotrochoid spirograph formula double points` ·
`guilloche pattern mathematics generation banknote engine turning curves formula` ·
`maximum number of nodes double points plane algebraic curve degree d (d-1)(d-2)/2` ·
`Minkowski sum of parametric polynomial curves planar curve addition properties` ·
`palindromic polynomial roots symmetric about 1/2 substitution t - 1/2` ·
`polynomial roots closed under t -> 1-t symmetric about one half` ·
`Turk's head knot mathematics single closed curve number of crossings interlacement` ·
`"offset curve" "parallel curve" self-intersection distance to curve singular points cusp offset` ·
`"reach" of a curve self-distance tubular neighbourhood nearly touching itself definition` ·
`Lissajous curve number of self-intersection nodes formula` ·
`generative ornament grammar curves offsets interlaced pattern algorithm paper` ·
`Hamid Naderi Yeganeh parametric equations mathematical art` ·
`Pythagorean hodograph curve self-intersection loops many turning number` ·
`Pythagorean hodograph curve cusp multiplicity order degenerate PH curve cusps` ·
`coupler curves four-bar linkage double points symmetric cognate curves many nodes` ·
`hyperflex higher order flex plane curve tangent contact multiplicity definition` ·
`Raph Levien Spiro spline font design curve loop calligraphic stroke centreline` ·
`flat spot curve curvature vanishing order parametric curve construction CAD` ·
`plane curve m-fold point multiple point at midpoint rational parametrization genus formula` ·
`lemniscate of Gerono figure-eight curve double point self-intersection` ·
`arabesque rinceau scrollwork construction geometry curve flourish design method` ·
`"bowtie curve" OR "hourglass curve" OR "pinched curve" algebraic double point` ·
`font glyph outline self-intersection loop cusp detection type design contour`

GitHub repository search (API):
`pythagorean hodograph` (5 results) · `spirograph` · `harmonograph` ·
`guilloche` · `self-intersection curve` · `parametric curves art`

Pages read in full: `Singular point of a curve` (Wikipedia) for the crunode /
acnode / cusp / tacnode / rhamphoid-cusp definitions and the genus paragraph.

Not tried, and worth a later pass: Google Scholar for "PH curve" + "loop" +
"turning number"; the Mathcurve site (mathcurve.com) index of named curves;
Craig Kaplan's ornament bibliography in full; "coupler curve atlas" as a picture
source; searching in German and French for the ornament terms
(`Ranke`, `rinceau`, `Guilloche`).

---

## 5. Links, plain

- https://en.wikipedia.org/wiki/Pythagorean_hodograph_curve
- https://faculty.engineering.ucdavis.edu/farouki/wp-content/uploads/sites/51/2021/07/Introduction-to-PH-curves.pdf
- https://en.wikipedia.org/wiki/Parallel_curve
- https://doi.org/10.1016/j.cagd.2023.102196
- https://arxiv.org/pdf/1005.4609
- https://arxiv.org/pdf/1902.02468
- https://en.wikipedia.org/wiki/Algebraic_curve
- https://mathoverflow.net/questions/38118
- https://math.unipd.it/~erb/Lissajous.html
- https://dresden.academic.wlu.edu/files/2024/07/TrochoidsThirdSubmission.pdf
- https://en.wikipedia.org/wiki/Guilloch%C3%A9
- https://mathworld.wolfram.com/GuillochePattern.html
- https://arxiv.org/pdf/2409.20106
- https://mathworld.wolfram.com/TurksHeadKnot.html
- https://github.com/suremarc/pythagorean-hodographs
- https://github.com/firepick1/ph5
- https://github.com/ahrvoje/ph-splines
- https://github.com/binarymax/guilloche
- https://github.com/ttencate/harmonograph
- https://github.com/LogarythmTech/GuillochePatterns
- https://parametrichouse.com/geometric-ornamental-design/
- http://eecs.umich.edu/courses/eecs498-2/papers/wong98.pdf
- https://digitalcommons.calpoly.edu/cgi/viewcontent.cgi?article=1204&context=csse_fac
- https://en.wikipedia.org/wiki/Hamid_Naderi_Yeganeh
- https://en.wikipedia.org/wiki/Minkowski_addition
- https://www.sciencedirect.com/science/article/pii/S037704270600690X
- https://en.wikipedia.org/wiki/Singular_point_of_a_curve
- https://en.wikipedia.org/wiki/Cusp_(singularity)
- https://en.wikipedia.org/wiki/Rhamphoid_cusp
- https://en.wikipedia.org/wiki/Crunode
- https://en.wikipedia.org/wiki/Acnode
- https://en.wikipedia.org/wiki/Tacnode
- https://aeb.win.tue.nl/2WF02/genus.pdf
- https://encyclopediaofmath.org/wiki/Chasles-Cayley-Brill_formula
- https://doi.org/10.1115/1.2167651
- https://vbn.aau.dk/en/publications/coupler-curve-synthesis-of-four-bar-linkages-via-a-novel-formulat/
- https://en.wikipedia.org/wiki/Cognate_linkage
- https://en.wikipedia.org/wiki/Lemniscate_of_Gerono
- https://mathcurve.com/courbes2d.gb/gerono/gerono.shtml
- https://levien.com/spiro
- https://github.com/fontforge/libspiro
- https://levien.com/phd/thesis.pdf
- https://tug.org/TUGboat/tb16-3/tb48kinc.pdf
- https://glyphsapp.com/learn/drawing-good-paths
- https://doi.org/10.1080/00207160701828157
- https://arxiv.org/html/2502.02075
- https://math.berkeley.edu/~chd/expo/kontsevich_formula.pdf
- http://balmoralsoftware.com/mathsite/boundary/bowtie/bowtie.htm
