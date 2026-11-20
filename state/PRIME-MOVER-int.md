# PRIME-MOVER-int — the prime mover: a unit circle instead of a linear t

The operator's reframing (2026-11-19), written as the standing direction. Read
this before designing a new parametric family, and say which of the two drivers a
curve uses: the linear `t` or the prime mover.

## The idea, in plain words

Instead of driving a parametric curve with a straight-line parameter `t` from 0
to 1, drive it with a **prime mover** (PM): a pair of variables `PMx` and `PMy`
that travel the **unit circle**. `PM = 2π` means the pair has turned a full turn;
`PM = −2π` means a full turn the other way; a span of `[−2π, 2π]` is 720°, two
turns, one each way.

A parametric equation driven that way has curvature **built in** — it leaves and
returns, it bends without being told to — instead of a straight parameter that
has to be bent by the coefficients. That is the point: the circle supplies the
curve; the polynomial supplies the variation on it.

**The arithmetic is the project's own rule, not trigonometry.** The circle is
walked through **Pythagorean triples**, so every point is a rational pair and the
grid survives. The operator's example: start at `(25, 0)` — the 7-24-25 triple
scaled by 5 — then `(24, 7)`, then add another `(7, 24, 25)` step, and so on
around the circle. The points are found once and then **reused**; a table of
them is cheaper than computing sines every time.

**The direction matters.** Going the other way gives different points, not the
same points in reverse order: the first negative step from `(25, 0)` is
`(24, −7)`, not `(24, 7)`. Two sets of `PMx, PMy` — clockwise and anticlockwise —
drive two different families from the same coefficients.

## Why it should make better curves

- **Natural curvature.** A circle-driven parameter already turns; the polynomial
  only modulates it. That is closer to how a stem, a volute or a flourish is
  built than a straight `t` with a large `t^7`.
- **Symmetry for free, in pairs.** The + and − walks are mirror images of each
  other about the starting radius, so a pair of curves can be built together.
- **Reusable, exact, small.** The points are whole numbers (or ratios with small
  denominators), so a curve driven by them stays on the integer grid and the
  points can be tabulated once in the database.

## The arithmetic fact that has to be faced

A fixed rational rotation — one p-triple applied again and again — **never
returns exactly to 2π**. Niven's theorem: the only rational values of `cos θ`
for a rational angle in degrees are `0, ±1/2, ±1`, giving 0°, 60°, 90°, 120°,
180°. Since every p-triple has rational cosine, the only p-triple rotations that
close are quarter and half turns; everything else walks densely and misses the
start by a little more each step. Ten steps of 3-4-5 (36.87°) reach 368.7°, not
360°.

So "all the way to 360" cannot be exact with one repeated triple. Three honest
routes, and the choice must be declared per curve:

1. **Accept the miss and state it** — walk N steps, print the closing gap in
   degrees and as a share of the radius. Sampled in the last hair of the turn.
2. **Change the triple at the wrap** — pick the last step from the table so the
   walk lands on the start; exact, at the cost of one irregular step.
3. **Use the quarter and half turns only** (90°, 180°), where a p-triple closes
   exactly, and vary the polynomial between them.

## What this touches

- **Every new parametric family** should say which driver it uses: `t` (linear)
  or PM (circle). Two drivers, two shapes, and the comparison is wanted.
- **The root family** (`lace-*`) is `t`-driven; it is not rewritten, it is the
  other side of the comparison.
- **Symmetry** (`state/SIMILARITY-int.md`), **the near-zero grace**, and the
  **frames** all apply unchanged; the driver changes the shape, not the gates.
- **The table of circle points** is a dataset: one row per step, per direction,
  with the triple used. It belongs in SQLite beside `CurveMetric` when it exists,
  because it is reused by every curve.

## The first thing to build

A table of the circle points for the first turn in both directions — from
`(25, 0)` by 7-24-25 steps, `+` and `−` — with the closing gap printed. Then one
curve driven by those points instead of by `t`, measured by the same gates
(crossings, inflections, bend, grid) so the two drivers can be compared as
numbers.

## The other way round the circle: chained imaginary transforms

The operator's note (2026-11-19): *"another way to do this is with ±(imaginary
number transforms) stacked or chained for a full circle: this will preserve
integer values… and keep us on the grid."*

This is the clean route, and it sidesteps the closure fact above entirely.

**The quarter turn is exact and closed.** Multiplication by `i` is a 90° turn on
integer coordinates, and four of them return exactly, with no gap:

```
(25, 0) → (0, 25) → (−25, 0) → (0, −25) → (25, 0)      exactly, four steps
```

The `−` direction is multiplication by `−i`, so the clockwise walk starts
`(25, 0) → (0, −25)` and is a different set of points, as the operator said.

**A p-triple is the same operation, scaled.** Multiplying by `3 + 4i` turns by
36.87° and multiplies the length by 5; dividing by 5 keeps it a rotation:

```
(25, 0) × (3+4i)/5 = (15, 20)      exact integers
(15, 20) × (3+4i)/5 = (−7, 24)     exact integers
(−7, 24) × (3+4i)/5 = (−23.4, 8.8) rational, grid 5
```

So a chain of p-triple steps is exact in `Fraction`, whole at the first steps and
on grid `5^k` after `k` steps. That is the arithmetic the project already uses
for rotations (`DESIGN-int` §Rotations are Gaussian rationals): every rational
rotation is a Gaussian rational of unit length, and a p-triple is the integer
generator of one.

**How the two compose.**
- A chain of `±i` gives exactly four directions and closes exactly. No gap, no
  policy needed — the only fully integer full circle.
- A chain of `(3+4i)/5` (or any p-triple) is dense and never closes exactly;
  it needs the declared policy from the section above.
- Mixing them, the walk closes exactly whenever the total turn is a multiple of
  90°: `i` and the p-triple **commute as multiplications**, so a run of quarter
  turns can be placed anywhere in the chain, and the closure question becomes
  "is the rest of the chain a multiple of 90°?".

**Consequence for the grid.** A curve driven by chained imaginary transforms is
multiplied by Gaussian integers throughout, so its points are Gaussian integers
up to a common power of 5 — one scale, one grid, no irrationality. That is the
strongest form of "stays on the grid" this project has, and it is why this route
is preferred for the prime mover when a curve must be exact.

**Note for the table.** The circle-point table should store every point as a
Gaussian pair `(a, b)` with its scale `5^k`, plus which factor produced it
(`i`, `−i`, or the triple). Then a curve's grid is the lcm of those scales, stated
by construction rather than measured after the fact.

## Many prime movers, retarded — the pendulum stack

The operator's addition (2026-11-19): *"an interesting curve might be made by
running the PM and then a second PM2 retarded behind the first… like several
pendulums. The addition or subtraction of the two could form a curve. Up to many
PMs, 7?"*

This is the mobile idea made exact. Each PM is a point travelling the circle; the
second is **the same travel, one step late**; the curve is their sum or
difference. A mobile is exactly that: vanes that swing in sequence.

**The arithmetic is addition of Gaussian integers.** A step of the 3-4-5 rotation
is `× (3+4i)/5`; a PM lagged by one step is the first PM multiplied by that same
factor. The sum of two PMs is then

```
P(t) = z(t) + z(t − lag)   =   z(t) · (1 + q^lag),   q = (3+4i)/5
```

so the pair is the single PM times a **constant Gaussian factor**. Worked, in
`Fraction`, lag 0/1/2 at the first points:

```
lag 0: (2.0, 0.0)  (1.2, 1.6)  (−0.56, 1.92)
lag 1: (1.6, 0.8)  (0.32, 1.76)  (−1.216, 1.312)
lag 2: (0.72, 0.96)  (−0.336, 1.152)  (−1.123, 0.422)
```

Every one is rational and, after the same power of 5, whole. The lag changes the
factor, not the machine — which is why the stack is cheap to compute and exact.

**Why up to seven is a sound cap.** Each additional PM multiplies the constant
factor by `(1 + q^{lag})`, so the grid rises by at most one power of 5 per PM (and
only when the lag's factor has a denominator). Seven PMs is therefore grid `5^7`
at the worst, which is the project's stated ladder limit; more would cost more
than the shapes are worth. Three to five is the practical range for a design.

**What it makes.** A sum of lagged PMs is a **travelling wave**: the same motion
sampled at several delays. With equal lags it is periodic and closes; with
unequal lags it is quasi-periodic, which is where the interesting, non-repeating
flourishes come from. Subtraction (`z(t) − z(t − lag)`) is the same with the
factor `(1 − q^lag)` and gives the chord-like version of the wave, useful for a
crossing centre.

**The ± question again.** The clockwise PM is `× (−i)` instead of `× i`, so a
stack may mix directions: a clockwise PM summed with an anticlockwise one traces
a lens, not a wave, and the two do not cancel unless the lags are equal.

**What to build first.** Three PMs, lags 0/1/2, at 3-4-5 steps, summed — one
curve, its grid printed, and the lags recorded as integers so the curve can be
rebuilt. That is the smallest object that shows whether the stack is worth the
seventh.

## Why the imaginary transform beats stacking points — and by how much

The operator's judgement (2026-11-19): *"the unit circle idea with stacked 7-24-25
triangles is nice in theory but blows up the grid scale, but imaginary transforms
(by 7-24-25) do not. So imaginary transforms would be better for us."*

**Agreed, with one arithmetic caveat that has to be stated.** A 7-24-25 step
carries the hypotenuse 25 = 5² in its denominator:

| steps | grid if each point is stored on the circle |
|---|---|
| 1 | 25 |
| 3 | 15,625 |
| 6 | 244,140,625 |
| 10 | 95,367,431,640,625 |

So a walk of ten steps is already past any usable grid, and the blow-up is the
same whether the division happens at each step or once at the end: the *final*
scale is `25^N`.

**What the imaginary transform actually buys — and it is real:**

1. **No denominators in flight.** Multiplying by `(7 + 24i)` keeps Gaussian
   integers integers. All the sums, lags and differences of the pendulum stack are
   integer work; the division by `25^N` happens **once**, at the end. There is no
   rounding anywhere on the way, so the curve is exact and reproducible.
2. **One scale for the whole curve.** Because the delay factor `(1 + q^lag)` is
   also a Gaussian rational, the per-PM scales combine by lcm; the curve needs one
   stated grid, not a scale per station.
3. **The grid is a choice, not a consequence.** With integer transforms you can
   keep the curve as integers and *decide* the presentation scale, instead of
   inheriting it from the last point you happened to compute.

**The practical rule that follows.**

- Use `(7 + 24i)` (and `(3 + 4i)`, `(5 + 12i)`) as **integer multipliers**, carry
  the products as Gaussian integers, and divide by the accumulated scale once.
- Keep the step count small: `N ≤ 3` is free (grid 25³ = 15,625), `N ≤ 6` is
  possible (5¹²), `N = 10` is out of reach by three orders of magnitude.
- If a curve needs a long walk, get the turn from **directions** (a rational slope
  such as 7/24) rather than from points on the circle: the slope costs no scale at
  all, and the p-triple is only needed where a *point* on the circle is required
  (a station, a junction, a rail hit).

That is the same conclusion the register already reached for rotations: the object
is the Gaussian rational, not the point on the circle, and the grid is stated by
construction.

## Four prime movers, damping, and the staircase — the operator's guess

The operator's reading (2026-11-19): *"about 4 prime movers will be helpful for
one curve, (they could affect xyz and time directions as well) after we find the
simple offsets with just 2 prime movers. We might need dampening or negative
prime movers to keep the spirals from going crazy. Imagine the lady descending
the staircase modernist painting…"*

**The order of work.** Two PMs first — one positive and one negative, or one
retarded — and only their **simple offsets** explored: the lag, the ratio, which
of the two carries the larger radius. That is the smallest object that can show a
different shape from the `t`-driven curves, and it is where the comparison should
be made. Four PMs is the target after that, not before: each additional PM
multiplies the grid by its factor's scale and the search by another dimension.

**What four PMs buy.** Four motions at once read as **space plus time** rather
than one curve in the plane:

- `PMx`, `PMy` — the plane, as now;
- `PMz` — a third coordinate that need not be drawn: it can become **width** (the
  rail's offset), **tone** (which part is filled), or a depth ordering of the
  strokes;
- `PMt` — the delay itself, the action of time: each PM's phase is a moment, and
  the drawing is the sum over moments.

That last reading is exactly the painting the operator names — Duchamp's *Nude
Descending a Staircase*: one figure at successive instants, all present at once.
A stack of lagged PMs is the arithmetic version: the same motion sampled at
several lags, summed, so the stroke carries its own history.

**Damping, so the spirals stay on the page.** Two honest controls, both exact:

1. **A damped radius.** Multiply each step by `(a+bi)·d` with `d` rational and
   less than one — `d = 4/5` is the natural choice, since it keeps the
   denominator a power of 5 and the grid stays a power of 5. The walk spirals
   **inward** and stops where you say.
2. **A negative mover.** The conjugate walk (`× (a−bi)`) turns the other way; two
   movers of opposite sign summed trace a bounded **lens** instead of a runaway
   spiral, and the pair cancels in angle while keeping its radii.

**The gate for a 4-PM curve**, stated so it can be checked: the maximum radius is
named and bounded; the grid is a stated power of 5; every point is a rational
pair; and the curve closes or is declared open with the gap printed. A stack that
cannot state those four is not ready to be drawn.

**What to build next.** Take the two-PM builder already on `/sandbox`, add the
lag and ratio as its simple offsets, print the radius bounds and the grid, and
only then add the third and fourth movers as width and delay. The staircase is the
picture to aim at; four is the guess to test, not to assume.

## Lags are fractions of a turn, not degrees — 2026-11-19

The operator's note: *"of course this will eventually be not degrees but fractions,
eg 1/9 and 8/9 like before."*

So the lag eventually reads like the root family's names: a mirrored pair written
`p/q` and `(q−p)/q`, with `1/9` and `8/9` the canonical example. The degrees in
the builder are the training wheels; the record should carry the fraction.

**The arithmetic that has to be faced.** A rotation by `2π·p/q` has rational
cosine and sine only for `q ∈ {1, 2, 3, 4, 6}` (Niven again — the same fact that
stops a repeated p-triple landing on 2π). So:

- `q = 2` — the 180° case, exact: `1/2`.
- `q = 3, 4, 6` — 120°, 90°, 60°, exact.
- `q = 9` — 40° per step, **not** rational. A `1/9` lag is a sampled angle, or an
  approximation by the nearest p-triple slope (`7/24` is 32.6°, `5/12` is 45.2°).

**What the fraction buys even when it is not exact.** It is the *address* of a
shape, not a claim of exactness: `lag 1/9` names the same object whether the
drawing used `cos` or a p-triple, and a future exact version can replace the
sampler without renaming the curve. The register already works this way — the
`lace-1of9-3` name outlived several changes of row values.

**How the beat is written.** The near-180 pair is `1/2 − δ` and `1/2 + δ`; for a
`1/9` pair the beat is `(q − 2p)/q` — for `p/q = 4/9` that is `1/9`. The form is
therefore:

    PM1  0        PM2  4/9        PM3  5/9        PM4  1

with `4/9` and `5/9` the mirrored pair and `1` the full turn. The drawing prints
both the fraction and the sampled angle, so the two never get confused.

**For the record.** A lag should be stored as `{p, q}` (integers, reduced) plus a
flag `exact: true|false` for whether the angle is a rational-rotation case. That
is the same shape as the root names, and it makes the builder's degrees a display
of the fraction rather than the source.

## What the probes found: product, radius law, odd powers — 2026-11-19

Three probes, each scored with the same loop test (tangential speed reverses
while the turn keeps one sign). Scripts: `scripts/pm_deep_search.py`,
`scripts/pm_product_probe.py`, and the four-mover search
`scripts/pm4_search.py`.

### 1. Adding movers: a geometric series cannot loop

96 four-mover sums, lags written as fractions of a turn. **One** passed the loop
test, and it was weak — a circle with a thin inner arc. The densest sums had
268–289 crossing points with **zero reversals** and zero inflections: braids, not
loops.

The reason is arithmetic, not tuning. Every mover shares one angular step, so
the sum is `Σ r_i^k e^{i(θ_i + kφ)` — a geometric series. A geometric series in
the plane is a circle or a spiral; the lags move the phase, not the nature.

### 2. Multiplying movers: star polygons and roses

`(1 + a e^{iαk})(1 + b e^{iβk}) = 4 cos(αk/2) cos(βk/2) e^{i(α+β)k/2}`.

With `a = b = 1` the radius pair changes sign twice per beat, the point passes
*through* the origin, and the figure is drawn with straight chords — a star
polygon (rendered: nine-pointed, 24 chord crossings). With radii under 1 the
figure is a rose/limaçon, and the collection already holds that under its own
name: `rose-k-2-a-1-b-1`, `rose-k-3-...`, `bounded-limacon-1-plus-2cos`.

152 products passed the numeric filter; every one rendered as a star polygon or
a rose. **The filter passes them and the eye rejects them**: clearance near the
origin, not crossing count, is what separates a drawn curve from a chord.

### 3. A radius law that grows and returns: a limaçon, one loop

`r(k) = 1 + a cos(2πk/N)` with the angle turning `turns` times gives exactly one
self-crossing, no inflections, aspect near 1 — a clean loop. 42 of 72 cases
qualified. It is a limaçon. The collection has three.

So: **the loop shape is not missing from mathematics; it is missing from the
mover line.** Everything the mover can reach is circle, spiral, rose, limaçon or
star, and all five are already named in the registry.

### 4. Odd powers: S curves are open, and that is the point

Every odd-power pair probed (`x,y` from `t, t³, t⁵` over a span) is an open
graph: 0 crossings, 0 reversals, 3–5 inflections. An S is a **segment quality**,
not a closed curve. That is not a failure — an S-shaped terminal is exactly what
W01's piece model needs, and `presets.py` already carries an `S-curve`.

### The conclusion to act on

New ornament does not come from a new closed curve. It comes from **assembly**:
a loop body, an S terminal, a declared joint, two tones. Each part is classical;
the combination, the exact integer terminals and the clearance proof are new.
That is the project's own scope sentence — *a grammar of plant-forms*, not a
gallery of curves. The next probe should be a two-part plate (loop + S), not a
fifth mover.

## The mirrored chain — 2026-11-19

The operator's definition, built as the top section of `/sandbox` and labelled
**Mirrored Euler transforms**:

> the first transform would be by (7,24,25) the second by (7,25,24) …

So the chain alternates a p-triple with its **mirror**, the same triple with its
last two numbers swapped: `(3,4,5)`, `(3,5,4)`, `(3,4,5)`, `(3,5,4)`, …

Written as the step that multiplies the running point:

| step | complex step | modulus | turn |
|---|---|---|---|
| triple `(x,y,z)` | `(x + iy)/z` | 1 | `atan2(y, x)` |
| mirror `(x,z,y)` | `(x + iz)/y` | `z/y` | `atan2(z, x)` |

The triple keeps the unit circle. **The mirror is a similarity, not a
rotation**: it turns by a different angle and grows by `z/y`. For `(3,4,5)` that
is 53.13° then 59.04°, growth 1.458 per mirror step; for `(7,24,25)` it is
73.74° then 74.36°, growth 1.082. The chain therefore breathes — out on one
step, back on the next — instead of holding one radius the way a single factor
does. The measurable chain for `(3,4,5)` starts
`1 → 0.600+0.800i → −0.550+1.350i → −1.410+0.370i`, which is exact in the
triple's own rationals and only drawn as a picture.

Because the mirror grows, the damping is stated per step as the **net radius**
(`percent / growth`), the same rule the two-mover damper already uses; otherwise
the growth `z/y` would quietly cancel the damper.

The section is a copy of the prime-mover machine on its own ids (`mm-*`), with
the triple and its mirror printed in the caption, and it saves under the family
`mirrored-euler`. Code: `app/src/scripts/mirror-mover.js`.

## The lattice spirograph — what the lattice allows, 2026-11-19

The operator's reading: chain the prime movers, then treat the secondary movers
as the main vane and the small vanes of a mobile — a spirograph with spirograph
ratios — but with **every station an integer lattice point**, so the curve can be
cut at a station and branched there.

Two probes, both exact. Code: `scripts/lattice_spirograph.py`,
`scripts/lattice_circle_mobile.py`; data: `workbench/lattice-spirograph.json`,
`workbench/lattice-mobile.json`.

### The constraint that decides everything

The integer points on the unit circle are only `(±1,0)` and `(0,±1)` — four
points, because `x² + y² = 1` in integers has no other solution. Add the
diagonals and you have the eight compass directions, whose length alternates
`1` and `√2`. So:

- **Bounded and exact ⇒ the compass (8 directions).** Nothing finer turns the
  lattice onto itself without growing.
- **Fine angles ⇒ denominators (a grid) or growth (a spiral).** This is the same
  Niven fact that stops a repeated p-triple landing on 2π, in a new place.

### Probe 1: the compass walk — too coarse

Two vanes, each stepping the compass at its own rate, the pen taking the summed
step. **42 closed walks, zero crossing pairs, at most 8 stations each** (the
period of the compass is 8). It closes beautifully and draws nothing: an octagon.

### Probe 2: the lattice mobile — exact, and coarse by nature

Each arm walks the integer points of its own circle, and the pen is the sum:

    P_k = A[k·q mod n_A] + B[k·p mod n_B]

Integer points on a circle of radius r, counted exactly:

| r | points |
|---|---|
| 5 | 12 |
| 25 | 20 |
| 65 | 36 |
| 325 | 60 |
| 1105 | 108 |

Every station is the sum of two integer points, so every station is an integer
point. The figure closes in `lcm` of the two arm periods. The measured shapes:
rosettes and star polygons when the ratio is large (`7/1` gave 1659 crossing
pairs at r = 25:65), and **quiet four-to-six-crossing figures** when the ratio is
near 1 (`65:325 1/1` → 4 crossings in 180 stations; `1105:1105 5/7` → 6 in 108).

### What this means for cut and branch

The cut is free: a station is an integer point, and the branch is the exact
integer perpendicular of the incoming segment, reduced to primitive integers.
Nothing is rounded, so the branch endpoint is on the lattice too. That is built
on `/sandbox` §0a — click a station and the dashed stub appears.

The price is stated on the page: the integer points on a circle are **not evenly
spaced in angle**, so the pen speeds up and slows down where they crowd. The
figures are coarser than a drawn spirograph.

### The choice to make, later

1. **Grid 1** — every station an integer, cut anywhere, coarse figures (this is
   built).
2. **A fine grid** — carry the curve on grid `1/q` (say `1/5` or `1/27720`, the
   project's usual measure) and cut at the stations whose coordinates are whole
   numbers. Fine figures, fewer legal cut points.

Both are honest; they differ in what "the lattice" means. The page currently
offers the first.

## The flip of a transform is a quarter turn — 2026-11-19

The operator's worked example:

> take a point at x=25. transform it to (7,24) with an euler transform. FLIP the
> transform, so the next transform goes to about 13, 22 or so.

Done exactly (`scripts/flip_demo.py`, figure `workbench/flip-transform.svg`).

**Step 1.** `(7,24,25)` divides by its hypotenuse: `25 · (7+24i)/25 = 7+24i`.
A rotation by `+73.7398°`, radius kept at 25.

**Step 2, and this is where the numbers choose the flip.** Five natural flips of
`(7,24,25)`, applied to `7+24i`:

| flip | step turn | lands at | radius |
|---|---|---|---|
| `(7,25,24)/24` swap last two (the *mirror*) | +74.36° | (−22.96, 14.29) | 27.043 |
| `(24,7,25)/25` swap legs | +16.26° | (0, 25) | 25 |
| `(7,−24,25)/25` conjugate | −73.74° | (25, 0) | 25 |
| **`(24,−7,25)/25` quarter turn** | **−16.26°** | **(13.44, 21.08)** | **25** |
| `(−24,7,25)/25` | +163.74° | (−13.44, −21.08) | 25 |

Only the quarter turn lands on the number the operator named. So **the flip of a
transform is the transform turned a quarter turn**: `(x, y) → (y, −x)`, which
in a triple is `(7,24,25) → (24,−7,25)`.

**The landing point is exact.** `7+24i` times `(24−7i)/25` is `(336+527i)/25`,
and `336² + 527² = 625²`, so the radius is exactly 25, not approximately.

**What the chain does.** Alternating the transform and its flip adds
`+73.7398°` then `−16.2602°`, a pair of `+57.4796°`. That does not divide a full
turn, so the chain **never closes and never leaves the circle**: after 8 stations
it is at `(−16.10, −19.13)`, still on radius 25, and it goes on for ever. Every
station is a Gaussian rational with denominator growing by 25 a pair, so the
coordinates are exact at every station and the grid is `1/25^k`.

**Two different operations, kept apart by name.** The *mirror* swaps the last two
numbers `(7,24,25) → (7,25,24)` and grows the radius by `z/y`; the *flip* turns
the transform a quarter turn `(7,24,25) → (24,−7,25)` and keeps the radius. The
`sandbox` section called *Mirrored Euler transforms* is the mirror; it should not
be read as the flip.

### The turn written as slopes — no trigonometry needed

The operator's check (2026-11-19): *"so the turn is 7/24 + 7/24?"*

In the tangent sense, yes, and exactly:

    tan(2·arctan(7/24)) = (2·7/24) / (1 − (7/24)²) = 336/527

and `336/527` is exactly the ratio of the second station, `P2 = (336 + 527i)/25`.
That is why the numbers came out as 336 and 527: they are the slope addition of
7/24 with itself.

The turn in **degrees** is not 32.52° (twice 16.26°) but 57.48°, because the flip
turns the other way: `73.74° − 16.26° = 57.48° = 90° − 32.52°`. The added slope
measures 32.52° from the *y* axis; the station measures 57.48° from the *x* axis.

The reason the pair is complementary is one line:
`(24/7) × (7/24) = 1`, so the transform's angle and the flip's angle add to
exactly 90°. That is also why the chain never leaves the circle.

**The whole chain can therefore be written with slopes and fractions only**, using
the tangent addition formula as a recursion:

    s_{k+1} = (s_k + t) / (1 − s_k·t),      t = +7/24 on a transform step,
                                            t = −7/24 on a flip step

No `cos`, no `sin`, no degrees — the guardrail's own arithmetic. Directions:
`0, 73.74, 57.48, 131.22, 114.96, 188.70, 172.44` degrees, a `+57.48` step a pair.

### Choosing the triple: a dial in degrees a pair

The pair step is `90° − 2·atan2(x, y)`, so the closer a triple is to 45°, the
slower the carousel. Measured, exact:

| triple | transform | flip | pair | pairs a turn |
|---|---|---|---|---|
| (7, 24, 25) | +73.7398° | −16.2602° | 57.4796° | 6.3 |
| **(48, 55, 73)** | **+48.8879°** | **−41.1121°** | **7.7758°** | **46.3** |
| (65, 72, 97) | +47.9250° | −42.0750° | 5.8500° | 61.5 |
| (119, 120, 169) | +45.2397° | −44.7603° | 0.4795° | 750.9 |

`(48, 55, 73)` is the one that gives "about 8 degrees each time": 7.7758° a pair,
46.3 pairs to a full turn. Exact stations from radius 73 on the x axis:

    P0  (73, 0)
    P1  (48, 55)
    P2  (5280/73, 721/73)      = (72.33, 9.88)
    P3  (213785/5329, 325008/5329) = (40.12, 60.99)

Because the pair advances only 7.78° while each single step jumps ~49° forward or
~41° back, the stations fall into **two interleaved streams**: the even stations
walk 7.78° at a time from 0°, the odd ones walk the same 7.78° from 48.89°
(their first station P1); the two streams are 48.89° apart, which is 41.11° + one
pair. The figure shows both as one dotted ring.

Corrected 2026-11-19: an earlier line here said the odd stream starts at 41.11°.
That was the flip's angle, not a station's; the odd stations are at
48.89°, 56.66°, 64.44°, 72.22° …

**The cost, stated:** the denominator grows as `73^(pairs)`. By `P7` it is
151,334,226,289. So the chain is exact at every station, but the integer form of
a long chain is a very large fraction — the same "grid" measure the project
already uses, not a defect of the method.

Command: `.venv/bin/python scripts/flip_demo.py --triple 48,55,73 --write`.
Figure: `workbench/flip-transform.svg` (Fig. 2).

## Keeping the grid: walk the circle's own points — 2026-11-19

The operator's correction, in their words:

> why cant you stay on the grid, say 625? is the sequence of events wrong? this is
> basic pythagorean triples around a circle, or perhaps ending slightly inset and
> then coming out to the circle again. the points are on the circle again and
> again, right? check grid-8

**They are right, and the sequence was wrong.** The flip chain multiplied the
*position* by `(48+55i)/73` and `(55−48i)/73`. The direction is exact, but every
step divides by 73, so station 7 lands on grid `1/73⁶`. That is a property of
chaining *turns*, not a limit of the circle.

**The grid–preserving order is: choose the circle first.**

| radius | whole-number points | neighbour gaps | deepest chord inset |
|---|---|---|---|
| 625 (5⁴) | 36 | 4.35° – 16.26° | 6.28 |
| 1105 (5·13·17) | 108 | 0.43° – 8.37° | 2.95 |
| 1625 | 84 | — | — |
| 5525 | 180 | 0.43° – 5.45° | 6.25 |

Every station satisfies `x² + y² = r²` exactly. No denominator appears anywhere.
The count follows the prime factors that are `1 mod 4`, not the radius: 325
(5²·13) has 60 points, more than 625's 36, because 625 has only the prime 5.

**The stations are the p-triples themselves**, scaled to the radius:

    (375, 500) = 125 · (3, 4, 5)
    (175, 600) =  25 · (7, 24, 25)
    (527, 336) = (527, 336, 625)   (a fresh primitive)
    (220, 585) =   5 · (44, 117, 125)

**The inset is real and is the sagitta.** Between two stations the pen cuts a
chord, so the drawing dips inside the circle and comes back out at the next
station — exactly the operator's description. Measured, not guessed: 6.28 units
at radius 625, 2.95 at radius 1105.

**Stepping by k points** (k coprime to the count) turns the same circle into a
star polygon — the spirograph ratio, still on whole numbers: 36 stations with
step 7 is a 36-point star, every vertex an integer point.

**grid-8's lesson, confirmed.** Its rational-slope compass
(`site/dist/assets/raystar_math.js`, "5ⁿ PYTHAGOREAN TANGENT SNAP") holds 36
directions built from `(3,4)` and `(7,24)` with a 12° snap: never rotate by a
decimal angle, always snap to an exact rational direction. Same principle — stay
rational rather than exact-and-fractional.

Command: `.venv/bin/python scripts/circle_grid_walk.py --radius 625 --write`.
Figure: `workbench/circle-grid-walk.svg` (Fig. 3).

## Curves with character — the search, 2026-11-19

`state/CHARACTER-int.md`. The short form: **sample the walk finely** — one triangle turn
a station, not the double angle — then apply whole-number polynomial maps. Thirteen
stations draw stars; ninety draw curves. The mature results are the astroid family
(`x = X(1−Y²)`, `y = Y(1−X²)`) and the pinch, on the thin triple: symmetric to 1e-4,
four to eight loops, no crossings.
