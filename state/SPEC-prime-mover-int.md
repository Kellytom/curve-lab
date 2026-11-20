# SPEC — the prime mover (`/prime-mover/`)

The clean description of one page: what it is for, what it shows, and the rules it must
keep. Work from this file. Every fault this page has had, with the guard for each, is in
`state/PROBLEMS-prime-mover-int.md`.

**Status, 2026-11-19:** every item below is a promise; `[x]` means it is built and a check
or a named script proves it, `[ ]` means it is not done. The count is kept honest by hand
when the file changes.

**The page:** `app/src/pages/prime-mover.astro`
**The driver:** `app/src/scripts/prime-mover-driver.js`
**The check:** `app/scripts/check-prime-mover-page.mjs`

## 1 · What the page is: one walk

**The walk is the page.** Everything else is a picture of it or derived from it.

    apex      (24, 7)              the first hypotenuse, on radius 25
    rotation  (527, 336, 625)      the double angle, 32.5204°: 527 + 336i = (24 + 7i)²
    stations  twelve, on the 25 circle, equally spaced

- [x] The walk is the orbit of an apex under the rotation, one model for every triple.
- [x] Every station is a reduced ratio of whole numbers: `x` a multiple of 24, `y` a
      multiple of 7, the hypotenuse a power of 5.
- [x] The rotation is the square of the triangle's own turn, because two triangles share
      each apex.
- [x] Twelve stations reach 357.7°, 2.3° short of a full turn; the shortfall is stated
      rather than hidden.
- [x] The station count follows the triple, and the page prints it (23 stations for the
      default half walk).

## 2 · What the driver puts out

    { i: {num, den}, x: {num, den}, y: {num, den} }

- [x] `i` is the counter, not an angle.
- [x] Every `num` and `den` is a whole number; nothing is stored as a decimal.
- [x] `x(−k) = x(k)` and `y(−k) = −y(k)` — the set of `i` is symmetric.
- [x] A single conversion to a float exists (`fixed(n, d, 30)`), and it is the only place
      a decimal is made.
- [ ] The driver's output table is on the page: it was moved to the notes and has not been
      replaced by a readout in the new layout.

## 3 · The step, and the choice of it

| triple | turn a step | steps | turn reached |
|---|---|---|---|
| `(3, 4, 5)` | 53.13° | 7 | 371.91° |
| `(7, 24, 25)` | 73.74° | 5 | 368.70° |
| `(44, 117, 125)` | 69.40° | 6 | 416.40° |
| `(56, 783, 785)` | 8.18° | 45 | 368.1° |

- [x] A thin triple steps finely: `(56, 783, 785)` moves 4.09° a triangle, so an apex
      moves 8.18° a station.
- [x] A cost guard disables a spirograph ratio whose BigInt cost is over 400,000; with
      `(56, 783, 785)` only ratio 3 is offered.
- [x] **The thin triple is the page default, with quadrants I and IV ticked.** The chooser
      carries `selected`, the box carries `checked`, so the first drawing is the half walk
      (23 stations, not 45). Picking another triple clears the tick.
- [x] **Quadrants I and IV only** halves the walk: 23 stations instead of 45.
- [x] The driver grid stays inside `2⁵³ − 1` for the triples the page offers.
- [ ] The guard line that reports the driver grid and whether every station divides it is
      not on the page; the limit is respected by construction, not by a printed check.

## 4 · Who reads it

- [x] Short sentences, everyday words, one idea at a time; no decimals in a table.
- [x] Each term gets its meaning the first time it is used.

## 5 · The words the page uses

| word | what it means here |
|---|---|
| **prime mover** | the point travelling the circle that supplies x and y |
| **i** | the driver's counter, not an angle |
| **station** | one position of the prime mover; a pair of exact ratios |
| **step** | one move, written as its triple |
| **first part** | the counter-clockwise values, `i < 0` |
| **second part** | the clockwise values, `i > 0` |
| **driver grid** | `hypotenuse^steps` for the chosen step |
| **reduced denominator** | `grid / gcd(x, y, grid)` |
| **ink dot** | the station at `i = 0`, belonging to neither part |
| **readout** | the line that names the station you clicked |

## 6 · What the page shows, top to bottom

The real order today, which the headings carry:

- [x] **The equations** — the operator's equation, stated before the figures.
- [x] **Fig. 1 · the walk** — the ring of stations, built by reflection; the heading names
      the triple, the mode and the station count.
- [x] **Fig. 2 · the hit points** — the stations with axes, the heading carrying the triple.
- [x] **Fig. 3 · the curves** — the polynomial presets on the walk.
- [x] **Fig. 4 · the spirograph** — one curve and its stations, ratio cost-guarded.
- [x] **Fig. 5 · curves with character** — six measured curves, each with axes, a grid, a
      15 px legend and a Bézier chain.
- [x] **Fig. 6 · an equation, and the circle taken out** — two lines, a hyperbola, and the
      walk's stations.
- [x] **Fig. 7 · the geared spirograph** — a wheel in a ring, integer stations.
- [x] **Fig. 8 · the linkage** — the crank-rocker, its mirror, integer stations.
- [x] **Fig. 9 · the circle taken out** — seven panels, then the table of identities.
- [ ] A readout that names a clicked station in exact ratios.
- [ ] A colour key line for first part and second part as a standing legend.

## 7 · The triangle figure (Fig. 1)

The construction, which must not be replaced by hand-placed shapes:

    T1  O, foot (24, 0), apex (24, 7)          foot on 24, apex on 25
    T2  reflect T1 across its hypotenuse        shares the 25 side with T1
    T3  reflect T2 across its 24 leg            shares the 24 side with T2
    T4  reflect T3 across its hypotenuse        shares the 25 side again

- [x] Built with JSXGraph from constructed points, one scale, both circles whole in frame.
- [x] Feet on 24, apices on 25, both circles dashed, a right-angle mark at each foot.
- [x] The title is inside the board.
- [x] Whole-number coordinates are labelled.
- [x] The walk is drawn with mirrored triangles, not with chords.

## 8 · The geometry, stated

Everything in Figs 1–4 follows from these facts; they are written here so the figures can
be checked against them rather than against an eye.

**1. Two circles and a triangle.** `C25` radius 25 and `C24` radius 24 about `O`, with
`|OF| = 24`, `|FA| = 7`, `|OA| = 25`, right angle at `F`. `cos φ = 24/25`, so both
coordinates are ratios.

**2. Reflection keeps the circle.** Every mirror line passes through `O`, so reflection
preserves the distance to `O`: every apex stays on `C25` and every foot on `C24`.

**3. Two reflections are one rotation.** Consecutive triangles advance the apex by
`2φ = 32.5204°`, and `(cos 2φ, sin 2φ) = (527/625, 336/625)`, hence `527² + 336² = 625²`.

**4. Parity is conserved.** `x′ = (527x − 336y)/625` stays even, `y′ = (336x + 527y)/625`
stays odd, because `625ᵏ` is odd — the numerators end in 4 or 6 and in 3 or 7.

**5. The integers behind the fractions.** `x` is always a multiple of `24 = 2³·3`, `y` a
multiple of `7`, and `x² + y² = (25 · 625ᵏ)²`: a p-triple at every level.

**6. It cannot close evenly.** `360 / 32.5204 = 11.07`, so twelve apices stop 2.3° short;
the spacing between consecutive apices is exactly equal, and that is what the check
measures.

- [x] The first apex is `(24, 7)`; every apex is on `C25` within 0.1 unit.
- [x] The gap between consecutive apices is 32.52° within 0.01°.
- [x] The figures are square, because a circle drawn with two scales is an ellipse.
- [x] Fig. 2 carries visible axes named `x` and `y`, a zero line and whole-number grid.

## 9 · Priority: the circle the walk cannot see

**The standing priority of the page.** A curve is rebuilt on the exact lattice by taking
its circle out and reading what is left at the walk's stations.

1. Write `F(x, y) = 0` and split it into the circular part `C` — every term `c·(x² + y²)` —
   and the remainder `R`, so `F = C + R`.
2. On the walk `x² + y² = 1` at every station, so `C` is the same constant everywhere and
   the walk is blind to it.
3. The character, as the walk reads it, is `R` alone.

- [x] The quadratic split is implemented and checked exactly:
      `x² + 2xy + y²` gives blind part 1 and remainder `2xy`.
- [x] The general split reduces any polynomial by `x² + y² = 1` to `a(y) + x·b(y)`;
      `(x² + y²)²` gives blind part 1 and no remainder terms.
- [x] A PH speed is recognised as a circle walk: `x' = u² − v²`, `y' = 2uv`, radius
      `u² + v²`; the tangent has norm 1 exactly on all three stored lace curves.
- [x] The sharp edge is stated: `2xy = 1` with `x² + y² = 1` needs `x = 1/√2`, irrational,
      so no station lands on it and the figure prints a tolerance instead.
- [x] Every identity is asserted in `Fraction`, never in a float.

## 10 · Rosettes from linkages, done exactly

A coupler curve is asymmetric; the crank run backwards gives its mirror; the pair is a
rosette made by a mechanism.

- [x] The closure rule is stated: a joint is rational only when the closure quadratic has
      a rational square discriminant.
- [x] `scripts/linkage_exact.py` refuses a link set that is not exact, and searches the
      space: 60 parallelogram sets close at all 20 rational crank directions.
- [x] `tests/test_linkage_exact.py` pins the parallelogram, the joint conditions and the
      refusal for a general crank-rocker.
- [ ] The exact parallelogram rosette is drawn on the page; Fig. 8 is still the sampled
      crank-rocker and says so.

## 11 · The circle taken out (Fig. 9)

**Drawings first, table second.** The operator's words: "how can i analyze with no plot?"

- [x] Seven panels in page order: three curves stationed by the circle, three remainders,
      then the operator's equation.
- [x] `c-0028 · lace-2-eight-3`, `c-0029 · lace-balloon-3`, `c-0060 · lace-arch-x-1` are
      drawn from their own stored rows.
- [x] Each panel has a title inside, axis lines named `x` and `y`, a whole-number grid, and
      a legend inside at 15 px.
- [x] Each panel takes the data's own aspect, so no empty band.
- [x] Every point is evaluated in `Fraction`; the line between stations is a cubic Bézier
      chain, never a polyline, and the caption says the line is approximate.
- [x] The table of identities follows, one row per implementation, every error exactly 0.
- [x] The page check counts seven panels and fails on a missing label, a missing legend, or
      a polyline.

## 12 · Taking the circle out of a parametric curve

The operator's words, quoted so they are not paraphrased away:

> "what does the spec say about taking the x^2+y^2 out of the parametric polynomials in
> the database we choose to display? what does it say about plotting that curve, not the
> old curve?"

> "take a nice curve from the database, and plug it in to this generator … take a circle
> out of it … so that when you plugged in the new i values based on the circle, the curve
> would be reformed."

**The rule.** For `x(t), y(t)`: form `P(t) = x(t)² + y(t)²`; the circular part is its mean
`C = ∫₀¹ P dt` (the constant term is useless — every lace curve starts at the origin);
the remainder is `R = P − C`; the reformed point is `z·R/P`.

**What that does, said plainly.** `R/P = 1 − C/P` depends only on distance, so the point
keeps its direction and only its radius changes. **A radial term cannot bend a parametric
curve.** A circle is the case `P ≡ C`, where `R ≡ 0` and the curve collapses to the origin.

- [x] The operation is implemented exactly in `scripts/circle_plots.py`.
- [x] The curve is plotted with its stations set by the circle parameter `t = Y/(1+X)`,
      kept to `0 ≤ t ≤ 1`, with the stations as exact rational points.
- [x] The remainder is plotted in the bounded form `(P − C)/(P + C)`: zero where the circle
      carries the curve, positive outside the mean circle, negative inside.
- [x] The spec says that the shape cannot change, so no figure claims a new outline.

## 13 · The mechanisms (Figs 7 and 8)

- [x] **Fig. 7, the geared spirograph** — a wheel of radius `r` inside a ring `R`, pen `d`;
      `R/r = 6/2` gives three petals; axes, grid and integer stations drawn.
- [x] **Fig. 8, the linkage** — a Grashof crank-rocker (`AB = 2`, ground `5`, coupler `5`,
      rocker `3`), interactive, the coupler curve and its mirror.
- [x] Integer stations are coloured by the part of the turn: blue first, orange second.
- [x] Both captions say **sampled**: the joints are circle intersections and the pen angle
      is a real number.

## 14 · Not on this page yet

- [ ] Stage II: the curves built from the driver table.
- [ ] A free step count: steps are fixed per triple.
- [ ] Saving or exporting a driver.
- [ ] Keyboard access to the stations: clicking is mouse-only.

## 15 · How this page thinks: algorithmically, geometrically

The standing method, in the operator's words: *"you need to think algorithmically and
geometrically."* Every figure on this page is produced by a construction that can be
written down, not by hand-placed shapes.

**The first algorithmic idea — reform a database curve with the circle's values.**
Take a mature curve with character from the database, take `x² + y²` out of it, then plug
in the "new `i` values based on the circle". The circle is the object the walk can express
exactly, so the reform is: station the curve at `t = Y/(1+X)` from the walk, which makes
every station a rational point of the lattice.

- [x] The rule is stated (§12) and implemented (`scripts/circle_plots.py`).
- [x] The figure prints the original parametric rows and the reformed formula beside the
      drawing, so the reader can judge whether the reform is simpler.
- [x] The spec says plainly that a radial removal cannot change a curve's shape, so the
      reform is a re-stationing, not a new outline.
- [x] A stored curve is reformed *and* saved back to the database as its own record:
      `c-0272` `lace-2-eight-3-circle-parameter`, a path of 61 exact stations taken at
      `t = k/60` on `c-0028`, each with its own rational circle point; the note states
      the parameter and C, its row is in `workbench/circle-split.json`, and
      `tests/test_circle_split.py` (`test_way_4_the_reformed_curve_is_saved_as_its_own_record`)
      fails without it.

**The second algorithmic idea — make rosettes with linkages.** A coupler curve is
asymmetric; the crank run backwards gives its mirror; the pair is a rosette made by a
mechanism rather than sampled from a spirograph.

- [x] The exactness condition is a rule, not a hope: a joint is rational only when the
      closure quadratic has a rational square discriminant (§10).
- [x] The search found the exact family: 60 parallelogram link sets close at every one of
      20 rational crank directions.
- [ ] That family is drawn on the page; Fig. 8 remains the sampled crank-rocker.

**Two habits that follow, and are checked:**

- [x] A diagram never appears without its formula: every Fig. 9 panel prints its rows, its
      remainder and its reform under the drawing.
- [x] An idea becomes a check or it is a wish: each method above names the script and the
      test or page check that fails when it stops being true.

## 16 · How to change this page

- [x] Change this file first: what moves, which rule changes, what it costs.
- [x] If the change moves code, rewrite the file in one pass; a single line may be patched.
- [x] Run the gates: `node app/scripts/check-prime-mover-page.mjs`,
      `.venv/bin/python scripts/check_no_imaginaries.py`, `npm --prefix app run check`,
      `.venv/bin/python scripts/test.py --fast`.
- [x] Rebuild the readable copy: `.venv/bin/python scripts/spec_page.py --all`.
- [x] Record a fixed fault in `state/PROBLEMS-prime-mover-int.md`, never here.

## Count

- [x] The list is honest: 72 ticked, 10 open — every `- [ ]` and `- [x]` in this file,
      counted 2026-11-19 (the older line said 64 and 9 and had gone stale).
