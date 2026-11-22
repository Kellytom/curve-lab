# DESIGN-int — decisions already taken, and why

Read before changing a control, a page or an ordering. Each line is a decision,
the reason it was made, and its status. **Settled** means do not re-open it
without the operator saying so in words. **Open** means it is a live question.

Dates are the day the decision was made. Where the operator asked for it, the
entry says so.

## Speed numbers (the boxes and their sliders)

- **Two sliders per speed number: mantissa and decade.** Settled 2026-11-14, by
  the operator. The mantissa slider (red) sets the size 0–10, the decade slider
  (blue, 64 px) sets the power of ten −2…6. Reason: large numbers are quick to
  reach; the mantissa alone cannot get to 1000 or 0.01 without the buttons.
  Twenty-four sliders at degree 11 is correct, not a bug.
- **The sign lives in the number box, not the slider.** The slider carries size
  only; the `−` button flips the sign. Reason: a slider through zero would make
  zero sit in the middle, which reads as "set to middle" when the value is
  nothing.
- **Scale buttons stay beside the sliders** (`√2`, `×1.1`, `e`, `×1`, `×10`,
  `×100`). Reason: the decade slider is coarse; these are the exact snaps.
- **The power labels follow the step, written as fractions.** At step ½ the six
  boxes read `t^0`, `t^1/2`, `t`, `t^3/2`, `t^2`, `t^5/2`; at step ⅓ they read
  `t^0`, `t^1/3`, `t^2/3`, `t`, `t^4/3`, `t^5/3`. The worked formula under the
  page and the closing line use the same names. Reason: a box labelled `t^2`
  that carries `t^1` is a lie. Fractions, not decimals, so `t^5/2` never becomes
  the rounded `t^2.5`. Settled 2026-11-14.
- **The exponent step is a slider with named buttons** on the experimental page
  only: 1, ½, ⅓, ¼, plus any value between (0.75 gives `t^0.75`, `t^1.5`,
  `t^2.25`). Settled 2026-11-14.

## The roots panel and the ruler

- **A flat spot is a root.** The wording on the page and in this repo: a root of
  the y speed is where the stroke runs horizontal. Settled.
- **Mirror is on by default.** One click at `1/9` places `1/9` and `8/9`.
  Reason: symmetry has to be put in on purpose; a random row almost never has
  it. Settled.
- **Dots stack for multiplicity.** Three dots at `1/2` is the triple flat, which
  is what makes the long flat middle. Settled.
- **Click the line to add; click a dot to remove that copy; shift-click clears
  the stack.** Settled 2026-11-14, by the operator ("click on the dot again and
  it disappears"). Dots sit clear of the line so the line stays clickable.
- **`fill the numbers` multiplies the roots out** and picks the rung that fits
  (five spots → degree 11, six → degree 13). Reason: the row is the polynomial
  the spots multiply to; nobody should type it by hand.
- **A fractional bow scales both rows** by its denominator, and the status line
  says so. Reason: a common scale leaves the shape alone and keeps every number
  whole.
- **Ruler positions are fractions with denominators 2, 3, 4, 5, 6, 7, 8, 9, 10
  and 12**, mirrored about `1/2`. Settled.
- **Sliders for `copies at 1/2` (0–6) and `bow` (−4…4)** sit under the ruler.
  Settled 2026-11-14.

## Pages

- **`ph-nth-sandbox.html`** — part 1: the degree ladder, a gallery of the seeds
  and whatever the finder wrote.
- **`ph-nth-sandbox-2.html`** — part 2: the **Knotlike curves** section first,
  then everything else.
- **`ph-nth-sandbox-exp.html`** — experimental, **no gallery at all**, exponent
  step defaults to ½. Reason: a curve under test must not sit among the ones we
  keep. Settled 2026-11-14, by the operator.
- **The knotlike section leads with the operator's six pasted curves**
  (`wave3`, `knot`, `bud`, `knot-2`, `wave5`, `hersheys copy`), tagged *yours*,
  then the finds tagged *found*. Reason: the finds are compared against them,
  not instead of them. Settled 2026-11-14.
- **Order inside the finds: most meetings with the partner copy first, then the
  cheapest grid, then the lowest bend.** Reason: meetings is the knot measure;
  among equals the cheap grid is the better curve. Settled 2026-11-14.
- **Moves are stored by name in the generator**, never by hand-editing the page:
  `DEMOTE`/`AFTER` for the block below figure 42, `MOVES` for single moves. A
  render-time sort used to undo them; there is none now — the order the page
  shows is the order the generator wrote.

## Fractional exponents (the experimental page)

- **The ladder runs to 30 numbers per axis** (speed degree 14, position degree
  29) and the experimental page opens there, so step ½ reaches `t^7` — fifteen
  rows instead of six. Reason: halving the step halves the top power, so double
  the rows to get back to it. Settled 2026-11-14, by the operator.
- **No grid and no inflection count off whole powers.** The page prints
  `grid n/a` and `inflections n/a`. Reason: a fractional exponent has no integer
  grid and no polynomial Wronskian, so those numbers do not exist. Settled
  2026-11-14.
- **Bend, closest and openness are measured from the curve** when the step is
  not 1.
- **Negative `t` uses the odd extension** `sign(t) |t|^(k·step)`, and the readout
  says so in words. Reason: a fractional power of a negative number is complex;
  this is a declared choice, not a silent one.
- **Mirror symmetry holds only at step 1.** Measured: mirror gap 0.0000 at step
  1, 0.42 at ½, 0.41 at ⅓, as a share of the curve's size. Reason: the speed is
  a polynomial in `t^s`, and mirroring `u` about ½ is the same as mirroring `t`
  about ½ only when `s = 1`. Do not promise balanced knots at fractional steps.
- **A fractional step cannot be symmetric at all, not merely less so.** Measured
  over 569 random rows at steps 1, ½, ¾, 3/2 and 2: not one came within 1e-3 of
  its own mirror or half turn. The reason is arithmetic, not sampling: symmetry
  needs the parameter point `t = 2^(-1/s)`, which is irrational for every
  rational step except 1. So half powers are for *new shapes*, never for
  balanced knots. Settled by measurement 2026-11-14.
- **The x row may carry its own mirrored roots.** This is the axis that adds
  loops while keeping the mirror exact: both rows are mirrored, so the curve
  stays symmetric. It produced knots with 20 meetings where the best earlier
  family reached 16, so it is the preferred way to widen the search.

## High-order tail terms loosen the knot

The low powers set the knot; a small tail at the top powers (measured on the
operator's find: `t^11` to `t^14`, coefficients of order one) opens it up and
costs the mirror.

| tail scale | crossings | knot share | mirror gap |
|---|---|---|---|
| 0 (the lace) | 13 | 4% | 0.00 |
| 0.5 | 8 | 9% | 0.28 |
| 1 (the find) | 8 | 19% | 0.51 |
| 2 | 7 | **43%** | 0.55 |
| 4 | 5 | 3% | 0.16 |
| 8 | 4 | 1% | 0.44 |

So: doubling the tail takes the knot from 19% to 43%; quadrupling it destroys the
crossings instead of loosening them. The symmetry is gone from the first step —
that is the point of the axis, and it is the only lever found so far that makes a
knot bigger without flattening the whole figure. The find is kept as
`loose-knot-tail14` in the knotlike section.

## Tweaks that keep the mirror

A row is even or odd about t = 1/2, and a tweak keeps the mirror only if it has
the same parity as the row it touches. Measured on the operator's curve: x is
even (reads the same from the far end), y is odd (reads as its own negative).

Patterns that hold the mirror, as additions at the given powers, times a size:

| row | powers | numbers |
|---|---|---|
| x (even) | t1, t2 | -1, +1 |
| x (even) | t2, t3, t4 | +1, -2, +1 |
| x (even) | t3 … t6 | +1, -3, +3, -1 |
| y (odd) | t1, t2, t3 | -1, +3, -2 |
| y (odd) | t2 … t5 | -1, +4, -5, +2 |

The operator's own habit — +0.1 on one power, −0.1 on the next — is the first
row: it works because the two changes cancel when the row is read backwards.

Multiplying a whole row by `1 + size(t − t²)` also holds the mirror, and it is the
stronger lever (crossings 13 → 19 at size 0.2). Two traps, both hit and fixed:
the product is two powers longer than the row — trimming it to the old length
drops the terms that balance the change, which is exactly the lopsided curve; and
it must be done in powers, not in boxes, because at step 1/2 a box is half a
power and the factor would centre at t = 1/4.

The experimental page carries these as buttons; the primary curve redraws at once
and `window.phNthSymmetry()` reports the mirror gap, which is 0.0000 for every
pattern above at steps 1 and 1/2.

## What a tweak costs in grid

The tweak sizes are fractions, and the fraction decides the integer grid the curve
needs. Measured on the operator's curve at step 1, adding `x: t1,t2`:

| size | grid after | factor |
|---|---|---|
| 1 | 6,930 | ×2 |
| 1/4 | 22,176 | ×6.4 |
| 1/2 | 27,720 | ×8 |
| 1/8 | (cheaper than 1/4 in every case tried) | — |
| **1/3** | **86,625,000,000,000** | ruined |

1/3 is not an arithmetic limit but a machine one: a third cannot be written
exactly in binary, so every coefficient becomes a long decimal and the grid
explodes. **Only halves, quarters, eighths and whole numbers are offered**, and
the page says why. The multiply by `1 + size(t − t²)` is the most expensive
(1/2 took the grid to 5,765,760) because the factor is used twice.

The status line reports the grid after every tweak, so the cost is visible rather
than discovered later.

## A tweak is a share of the coefficient, not an absolute step

An absolute size changes every coefficient by the same amount. A share takes a
fraction of the coefficient itself, which keeps a mirrored pair balanced: the pair
has equal magnitude, so a quarter of 16 moves both ends by 4.

Measured on the default curve at step 1, adding `x: t1, t2`:

| share of the 16 pair | tweak | x becomes | grid |
|---|---|---|---|
| 1/16 | +1 | 3, -17, 17 | 6,930 |
| 1/8 | +2 | 3, -18, 18 | 3,465 |
| **1/4** | **+4** | 3, -20, 20 | **693** |
| 1/2 | +8 | 3, -24, 24 | 3,465 |

All keep the mirror exact. The grid is a least common multiple over the whole
position polynomial, so a share can lower it — 1/4 made the curve five times
cheaper — as well as raise it, which 1/16 did. That is the operator's gcd
instinct confirmed: the numbers have to be read together, not one at a time.

The panel offers both levers, an absolute fraction and a share of the x pair, and
the status reports the grid after every tweak.

## A rung hides numbers, it never deletes them

Moving to a lower degree keeps every coefficient above the new rung in a stash and
shows zeros in the new boxes; moving back restores them. Measured: a value of 777
in the top box at degree 29 survives degree 11 and returns on the way up. The rule
is the same everywhere in this project: a view may hide data, never destroy it.

## Half powers: a dial, not a field

Probed 2026-11-14 with `scripts/half_probe.py`; three answers, all measured.

1. **They are not a place to look for knots.** Of 400 random half-power rows, none
   had five or more crossings with a sane aspect. A half-power row is a polynomial
   in `sqrt(t)`, and its geometry collapses toward a flat band: the same numbers that
   give 38% knot at step 1 give 1% at step 1/2, with the legs at 86%.
2. **One half-power term is a useful asymmetry dial.** On a curve with six
   crossings, a value of 1 at `t^1/2` gave **nine** crossings, knot 22%, bend 2.86 —
   unbalanced (mirror gap 0.245) but knottier. At 4 it collapsed to two crossings.
   So: one or two terms in the odd boxes changes the shape deliberately; it is not
   where a search would start.
3. **The balanced tweak patterns are step-safe.** At step 1/2 they land on the
   whole-power boxes (the panel maps powers, not boxes), so the mirror stays exact:
   measured gap 0.0000 with the x pattern, the y pattern, and both, and the knot
   moves 38% → 40%, 41%, 34%. Used on an *odd* box instead they break the mirror,
   which is the dial above.

**Consequence for the Bezier step:** a half-power row has no polynomial
parameterisation in `t`, so it cannot be span-fitted exactly the way a whole-power
row can. It would have to be sampled and fitted — labelled fitted, never exact. That
is the reason to treat half powers as an experiment on a single curve rather than a
family to catalogue.

## Trigonometry: irrational values are a red flag — 2026-11-18

- **Ratios come from 2, 3, 4 and 5.** The operator's standing assumption
  (2026-11-18): weights, amplitudes and turns use `1, 1/2, 1/3, 1/4, 1/5` and
  integer rates, and tilts use the `3-4-5` triple. Measured: a mobile on those
  keeps grids of **5, 10, 15, 50**. A `5-12-13` tilt adds a 13 and an `8-15-17`
  adds a 17 — exact, but the grid jumps to 4250 and 13260, which is no longer
  simple. Treat a denominator above 5 as a red flag of the same kind as a
  `cos`: allowed if a reason is written down, not by accident.



Settled by the operator: "I don't mind trig that uses rational fractions like 3/4
or 7/24 but we have to stay on the integer grid, and once you go irrational it is
pretty hard to get back to rational."

- **The object is the ratio, never the angle.** `cos θ`, `sin θ` for a general
  angle are irrational, so any point built from them leaves the integer grid and
  cannot come back. What is allowed is a **rational point of the circle**: a
  `p`-triple such as `3-4-5` or `7-24-25`, or equivalently the rational
  parametrisation

      cos θ = (1 − t²)/(1 + t²),   sin θ = 2t/(1 + t²),   t = 7/24

  which gives `(527/625, 336/625)` — exact fractions, on the grid at 625.
- **A curve drawn by sampling `cos`/`sin` is a drawing, not the curve.** The
  roses on `/finder` were sampled that way; the algebra has an exact rational
  form, but the picture does not, and the caption must say "sampled" until it is
  rebuilt from rational points.
- **Trig is not impossible, it is a red flag.** A `sin`/`cos` in a generator is
  the signal to ask: can this be written with `t = tan(θ/2)` and a rational `t`?
  If yes, rewrite it. If no, label the figure sampled and do not claim exactness.
- **The same rule covers every rotation.** A rotation matrix with `cos θ` is the
  same red flag; a rotation by a `p`-triple, `(3/5, 4/5)`, is exact on the grid.
  The repo already has the machinery: `curve_lab/pyth_cubic.py` and the
  `pythagorean-spiral` turn lattice.

## Rotations are Gaussian rationals — 2026-11-18

- **The operation is multiplication by a Gaussian rational** `(a + bi)` with `a, b`
  rational; a rotation needs unit length, `a² + b² = 1`, so every rational rotation
  is a **Pythagorean triple** (`3-4-5`, `5-12-13`, `8-15-17`). The repo already
  uses these in `curve_lab/pyth_cubic.py` and the spiral turn lattice.
- **For a PH curve the speed turns by half the angle.** Rotating a vertical-mirror
  curve by `θ` multiplies its speed by `e^{iθ/2}`, so the rows stay rational only
  when `tan(θ/2)` is rational. `θ` from a p-triple satisfies this: `3-4-5` gives
  `tan(θ/2) = 1/2`, and multiplying the rows by the common factor `√5` makes them
  whole. `45°` gives `tan 22.5° = √2 − 1`, irrational, so **no rational rows exist**
  and no exact `y = x` PH curve can be written.
- **What is reachable:** mirror axes of slope `−3/4`, `−4/3`, `−15/8`, `−12/5` …
  from `q = 1/2, 1/3, 1/4, 1/5`. What is not: `y = x`, `y = −x`, and any axis whose
  half-angle is not Pythagorean.
- **The sandbox shows the family** under "Rational rotation: a mirror you can turn"
  on `ph-nth-sandbox-exp.html`, one panel per `q`, with the 45° attempt drawn from
  floats and labelled not exact.
- **A turn is saved as a new curve, never over the old one** — 2026-11-18, by the
  author. The name takes the postfix `-rotpofr`, where `p/r` is the tangent of
  half the turn: `-rot3of4`. A slash cannot appear in a name because it is the
  path separator; `of` matches the existing `lace-1of8-1of3-3` style.
- **The whole-row turn also scales the curve by `r² + p²`.** Multiplying the
  speed by `(r + i p)` turns the position by `2·atan(p/r)` and scales it by
  `r² + p²` (5 for `q = 1/2`). This is arithmetic, not a defect: no whole-number
  rows give a pure turn. The HUD says the scale in the same line as the turn.

## Optical versus real (matters for the Bezier conversion)

Some controls move the camera and leave the numbers alone. Others change the
numbers. Only the second kind may be exported.

**Optical — the rows are untouched, so these must never reach an export:**
`zoom`, `focus the knot`, `show only the knot` (the `t from` / `t to` window),
`rotate -45`, `hide the grey curve`, `rails`, `character offsets`, the terminals.

**Real — these rewrite the rows:**
the flat spots and the fill buttons, `copies at 1/2`, `bow`, the exponent step,
typing in any box, and `rebuild without the legs`.

Rule for the Bezier step: read `terms` from the record and convert those. Never
convert what the plot shows, because the window can crop the stroke and the
zoom changes nothing at all. If a curve with no legs is wanted, it must come from
`rebuild without the legs` (exact, checked against a Python reference to the
integer) or from different flat spots — not from the window.

Measured note: on the curves tried, the self-crossings run across nearly the
whole `t` range (for example t 0.081 to 0.919), so no shorter exact span holds
them and the rebuild honestly reports the whole curve. Legs are shortened by
moving the flat spots, not by cutting `t`.

## Images: the "no image input" rule was false

Corrected 2026-11-17, by the operator: "it is not true whatever it is".

- **The engine reads images.** Commit `3558a3e` (2026-11-04) recorded that one
  PNG read fails every later turn; what actually failed were very large files.
  The rule was deprecated in `AGENTS.md` on 2026-11-16 but survived in
  `/fhandon` and `state/READING-int.md`, so a command kept telling sessions not
  to look at a figure that had been readable for days.
- **Every copy is gone**, and the limit is 450 KB and 3000 px on the long side,
  downscaled only when a limit is actually broken. A figure is still best judged
  by printed numbers or the DOM; looking at it is allowed, not required.

## Context: no budget, the operator decides

Settled 2026-11-17, by the operator: "take out all constraints about context
budget... the problem was chrome not opencode."

- **Every instruction that constrained context use is removed**: no budget line
  before a task, no percentage, no minute count, no metric pasted into a handoff.
- **The 2026-11-16 meter measured the wrong thing.** It reported OpenCode's
  share, but the pressure was Chrome holding memory on an 8 GB machine. Retiring
  the meter without retiring the budget kept a constraint with no measurement
  behind it.
- **The operator monitors and decides how long a session runs**, and may ask for
  several actions in one session. The agent reports each action as it lands.
- **What survives is honesty, not memory**: never report a narrowed result as
  complete, and "complete" needs a diff or a test.

## Self-crossings: crossing pairs, not meeting points

Settled 2026-11-16, after the page and the record disagreed on
`lace-1of10-1of5-3` (page 5, record 4).

- **The number is a count of crossing pairs**: two parameters `t1 < t2` where the
  stroke passes through the same place. It is scale-free, and it is what the
  galleries sort by and the page prints.
- **Three passes through one point are three pairs.** That curve has 5 pairs at
  3 places, one of them a triple point. If a reader needs places, say *meeting
  points*; never call both "crossings".
- **The stored numbers were stale.** The galleries' `self` values were written
  before the parameter-pair dedupe replaced the distance dedupe, and nothing
  recomputed them: 100 numbers across seven files were wrong. `scripts/crossing_audit.py`
  recomputes them, `--write` puts them back, and `tests/test_crossings.py` keeps
  them honest. Reason: a displayed number that no current routine produces is
  the fault class the 2026-11-16 review named.

## Saved curves: a read that fails must never become a write

Settled 2026-11-16, after the operator's saved buttons were emptied twice and the
operator asked "how can you lose all those curves when we werent even touching
that code".

- **A failed read is not an empty list.** `readSaved()` says whether it read; a
  save refuses to treat a damaged value as nothing. Reason: the old code did
  `saved()` (which returned `[]` on any parse error), filtered it, pushed one
  curve, and wrote — one save deleted every other curve.
- **Every write keeps the previous value.** `ph-nth-curves-backup` holds the list
  as it was before the write, and `ph-nth-curves-mirror` holds the list as it is
  now. Reason: the damage is noticed a session later, so there has to be a value
  to go back to without a browser profile.
- **A damaged value is repaired on load**, from the backup, then the mirror.
  Only a browser that has never held a list is seeded.
- **The repository keeps a list: `workbench/operator-list.json`**, written by
  `scripts/operator_list.py` from the stored records. The page seeds a browser
  with no list from it, and `restore a list` reads any export back in.
  `tests/test_operator_list.py` keeps it current and complete.
- **The check is `scripts/check-saved.mjs`**, six browser checks, because a
  storage rule cannot be proven from the Python suite alone.

## One exact numeric core, and the page reading it

Settled 2026-11-16, from the senior review's first item ("the numeric core
exists three times and disagrees with itself").

- **`curve_lab/measure.py` is the only exact implementation** of grid, bend,
  arc, inflections and closest. `scripts/ph_quintic_metrics.py` is now a facade
  over it, keeping the names a dozen scripts import. Reason: two
  implementations agreed on 74 curves and disagreed on the seventy-fifth —
  `loop-13-15-17-mid-1`, exact grid 36, page 5,148 — and a third copy would
  have found a seventy-sixth.
- **The disagreement is a double limit, not a coding slip.** The page scales a
  row to whole numbers and squares it; a coefficient of 1.03e8 squares to
  1.06e16, past 9.0e15 where a double stops counting by ones. No amount of
  care in the JavaScript fixes that; the exact answer has to be carried.
- **A stored curve's numbers come from its record.** The record now holds the
  exact grid and bend, and the page prints them, labelled "(exact, from the
  record)", while the loaded rows are still untouched. The first edit returns
  the page to its own arithmetic, which is honest for a curve being made.
  Reason: the page must not claim an exactness it does not have, and a record
  must not be re-derived by a viewer.
- **`scripts/exact_numbers.py` audits every record against the core**, and
  `--write` puts the exact number back. `tests/test_exact_numbers.py` runs the
  audit in the suite, so a wrong number is a red test, not a curve that looks
  different from its figure.

## Exact form before cubics — 2026-11-17

Settled 2026-11-17, by the operator: "i am trying to avoid cubic beziers until
later... that is the last step before transfer to inkscape and glyphs 4".

- **The working representation is exact polynomial data** — the speed pair, the
  position polynomials, or a ratio of two polynomials. A cubic Bézier chain is
  the **export step** (PLAN S5), not the form the work is reasoned in. A card
  may print a cubic fit's measured miss as a number; it does not draw the cubic
  chain.
- **A PH curve's offset is exact and rational**: `O = C + d·(−y', x')/σ`, with
  `σ = u² + v²` a polynomial. `curve_lab/ph_offset.py` implements it in
  `Fraction`; there is no Bézier control data and no weight in the card.
- **Measured on `integer-105`** (`u = 2 − 5t + 6t²`, `v = 4 − 20t + 20t² − 2t³`):
  pitch 105, and at 105 the curve has exactly **two** lattice points, the ends.
  The first interior hit is the midpoint at **t = 1/2, grid 3360** — 32 times
  the pitch. The next stations are 25,515 (t = 1/3), 76,545 (t = 2/3), 143,360
  (t = 3/4) and so on, one at a time.
- **A rail hits the lattice only when d is chosen for the hit.** At
  d = 41/1120 the rail's first hit is the same grid 3360, at the same t; at
  d = 3/100 it is 688,800. The reason is arithmetic: the unit normal at the
  station is (40/41, −9/41), so d must carry the factor 41. A branch is its own
  curve, not a parallel offset, so it can be built on the lattice independently
  — the rails are the only side curves whose hits are dictated by the parent.
- **A station is not a mirror line.** The midpoint station translates to
  (0, 4130) on grid 3360, and the two rails land at (120, 4103) and
  (−120, 4157). But the curve is not symmetric (half-turn gap 37% of its size,
  vertical-mirror gap 49%), the tangent at the station is 12.7° off vertical,
  the inflection is at t = 0.5051, and x = 0 meets the curve four times. A true
  mirror axis needs a symmetric curve: the Pythagorean integer cubic family is
  half-turn symmetric with its midpoint at (c, 0) on scale 1, but it is not PH,
  so its rail is fitted. A symmetric PH curve is the third option.
- **A symmetric PH candidate was found** (2026-11-17, **not adopted**):
  `u = 1`, `v = (2t − 1)²`. Both speeds are even about 1/2, so the curve is a
  half turn about its midpoint (2/5, 1/3), the tangent there is exactly
  horizontal, and the vertical line through it crosses the curve once. Grid 15
  puts the station at (6, 5); one shift by −2/5 puts it at (0, 5); both rails at
  d = 1/15 land at (0, 6) and (0, 4) on the same grid; the + rail's first
  interior hit is grid 5. It is the first curve here with both an exact rail and
  a mirror station, and it changes the primary curve, so the choice is the
  operator's.

## Browser JS, Node as a tool — 2026-11-17

Settled 2026-11-17, by the operator: the page layer should be JS, but "dont get
too dependent on node except for good reason (the code is already debugged)".

- **Live page maths is JS**, in small self-contained modules that load as a
  plain script or through `require`; no bundler, under 200 lines each.
- **Node is a verification tool**, not a build dependency: it runs the browser
  modules' tests and the Playwright page checks. No generator moves to Node to
  be Node.
- **Python stays where it is debugged** — the engine, the records, the audits,
  the generators that write static cards. A calculation moves only when a page
  must compute it live, and then the Python twin is deleted in the same commit.
- **One number, one source**: a live number from the JS module, a stored number
  from the record. No third implementation.
- **No floats on an exact path**; the 1e16 case (`loop-13-15-17-mid-1`) is the
  mandatory test when a grid or crossing function moves.
- The first slice: `exact.js`, `poly_exact.js`, `ph_offset.js`, pinned to the
  Python numbers by `tests/js/ph_offset.test.js`; `scripts/test.py` runs
  `node --test`; `scripts/code_count.sh` prints the language split at handoff.
  The full plan and order is `state/PORT-int.md`.

## Book plates — 2026-11-17

The short-term deliverable: PNG plates for a book, SVGs kept beside them for the
later Inkscape step. The operator's rules, in their words: **white background,
no text on the image, clipped to the edge of the curve**, a plain gallery with
no input fields.

- **This overrides the figure-label rule for these plates.** A book plate has no
  title, axes or legend inside the image; the gallery and the manifest carry the
  name and the note. Every other figure still follows the label rule.
- **The name is `<descriptor>-<variant>-t-exp-c-<serial>`**, for example
  `swan-1-t-exp-c-0001`. The serial is allocated once in `book/plates.json` and
  never reused, so a re-export keeps the name and a LibreOffice link survives.
- **The size is decided by the bounding box of spine plus both rails.** The
  canvas aspect is that box, so the curve fills 97.6% of the long side; a margin
  of 1.2% keeps the stroke from being cut. Long side 3000 px, stroke 0.35% of
  it, 300 dpi in the PNG so LibreOffice inserts at 254 mm rather than 790 mm.
- **The rails are character rails, not parallel offsets** (operator,
  2026-11-17): a ±d base at the record's width percent, bowed by its `plus` /
  `minus` strength and its `bow`, `s` or `taper` profile. The construction is
  the sandbox's (`workbench/ph_nth_panels.js`, `characterRail`), reproduced in
  `workbench/plate_math.js`. A parallel rail is a later feature and is not
  drawn. When the base offset would fold, the width is halved; at the 0.2%
  floor the plate is spine-only and says so.
- **The inline data is checked.** The lab's curve data is written into the page;
  the generator refuses an empty list, a count mismatch or a row of zeros, and a
  test compares the inline copy with the file. Reason: the 2026-11-16 fault, when
  a damaged read emptied two thirds of the saved curves.
- **A folded base offset is never drawn.** If `|d·κ|` at the record's width
  would fold, the width is halved until it does not; at the 0.2% floor the
  plate is spine-only and the caption says so. Two of the 27 saved curves land
  there: `involute-fit` and `inflect-2`.

## Starring is a download, not a server write — 2026-11-17

The operator stars designs in the lab and wants them in the book gallery. The
lab runs in the browser; its stars live in `localStorage`; the exporter runs in
Node and cannot read a browser. The bridge is a **downloaded file**:
`workbench/starred.json`. The lab allocates each star a serial (from 0301) once,
stores it with the settings, and downloads the file; the exporter reads it if
present and adds the plates under the top section. There is no write endpoint on
the server, and a missing file is a prompt, not an error. This is the same
pattern as the saved-curve list: the browser cannot be the database.

## Symmetry is measured, not guessed — 2026-11-17

The operator's note: the saved curves are not all internally symmetric, so the
lab groups them. The measurement is on the spine, at 400 stations:

- **half turn** — `C(1/2+s) + C(1/2−s) = 2C(1/2)`;
- **mirror** — the same about the vertical line through the midpoint, so the
  x values add to `2x(1/2)` and the y values are equal;
- **none** — neither, within 0.5% of the bounding-box diagonal.

**The operator's category is stricter than the axis test.** Among the seed,
only `u-bowl` and `wave-coarse` count as symmetric; the 60 **found** curves take
their measured symmetry. The measured kind stays in the data and the readout
prints both, so the difference is visible: `v-sharp` is a measured mirror but
the operator's category is asymmetric. The lab now offers **88 curves**
(28 seed/new + 60 found) and **62 are symmetric** under this rule. The record
lives in `workbench/real-curves.json`, with `source` (seed, new, found),
`symmetry` and `category` per curve.

## Central designs are at least two curves — 2026-11-17

The operator's definition: a central design has **at least two curves joined at
their legs** (or end to end). Two forms so far:

- **The leaf** — curve a below, the flipped curve b above, both pairs of feet on
  the same two points. Measured tip angles: arch/arch 90°/90°, S/arch 90°/0°.
- **The chain** — curve a then curve b, end to end, **not flipped**. A shallow-leg
  curve and a steep-leg curve can meet at a shared foot; the join angle is the
  difference between a's end tangent and b's start tangent. That difference is
  the design's decision, not a fault: it is a corner unless the angles match.
- The book plates are single curves (spine plus character rails), not central
  designs.

## Square and frame: the leg bisects the corner — 2026-11-17

The operator's construction, 2026-11-17: measure the curve's chord (the
end-to-end distance on x, with the legs at the same y), make an invisible square
of that side, and put one curve on each edge. North is the x-flip, east the
quarter turn, west the mirror. `curve_lab/square_assembly.py` and
`workbench/plate_math.js` implement it; `scripts/square_try.py` is the static
proof and `workbench/square-frame.html` is the lab.

- **One rule: the leg bisects the corner.** A square corner is 90°, so the leg
  is 45°. The angle is reached by scaling the curve *across its chord*, so the
  ends stay on the edge and the square stays closed at the measured side.
- **Measured joins:** an arch at a 45° leg joins continuously (0° kink); an S
  at 45° joins at 90° (a miter); an arch as drawn leaves 16°.
- **The frame is the same rule with `n` chords a side.** The side is
  `n × the chord`, so 3 copies fill one side and 5 make a finer, lace-like
  scale. The frame and the central cross are built **separately** and only
  overlaid — a picture in a frame. Do not merge them into one curve set.
- **The page is a lab, not a plate.** Curve, curves per side, leg angle, print
  size, fill, alternate flips and the cross, all live. The page measures in
  points (1/72 in).
- **The stroke floor is exactly 1 point** at every size from 1 to 4 inches:
  `strokeFor` returns `max(1, 0.0035 × width in points)`, so the percentage
  rules above 3.97 in and the floor holds below it. A scaled-down plate never
  loses its line.
- **Squares and rectangles only, for now.** The operator parked other polygons
  on 2026-11-17. The same corner rule holds when they return: a pentagon's
  corner is 108° (leg 54°), a pentagram point 36° (leg 18°) — but the box is
  not square and the counts are per axis, so it is a separate piece of work.

## Astro is the app — 2026-11-17

Settled 2026-11-17, by the operator: the final result is Astro; no React; local
file support; it must work on Next and other servers. `app/` runs Astro 5.18.2
with the Node adapter on **:4321**. Astro 7 was refused by this machine's Node
22.4.1 (it wants >=22.23.4); Astro 5 accepts it, and a global 5.18.2 is
installed. The page imports `workbench/plate_math.js` and
`workbench/real-curves.json` — no second maths. The save is
`app/src/lib/stars.js`, plain Node (validate, temp file, rename), called by a
thin Astro route; a Next or Hono route can call the same function. The lab's
"save to workbench" writes `workbench/starred.json` from the page, and the
download stays as the fallback. Migration order and the Python bridge are in
`state/ASTRO-int.md`. The old generated pages remain until each is ported and
deleted in the same commit.

## The book gallery is the Astro page — 2026-11-17

Settled 2026-11-17, when A2 landed. The generated `book/index.html` is retired.

- **The gallery is a server page**, `app/src/pages/book.astro`, reading
  `book/plates.json` and `workbench/starred.json` on every request. Reason: a
  star saved to `workbench/starred.json` shows up without a rebuild, and the
  listing cannot drift from the file the way a generated page can.
- **One caption, one module.** `workbench/plate_compose.js` holds the compose
  call; the exporter and the gallery both require it. Reason: the caption is
  the plate's name in the book, so two copies of the wording is the fault class
  the register already names.
- **Every star is listed, even before its PNG exists.** A star with no exported
  plate says `PNG not exported yet` on its card. Reason: dropping it would make
  the gallery quietly disagree with the file it claims to list.
- **The PNGs are served from `book/plates/`**, not copied into `app/public/`:
  `app/src/pages/api/plate/[id].js` checks the id against the plate-name pattern
  and the resolved path against the plate directory. Reason: 5.8 MB of plates
  would otherwise exist twice, and two copies drift.
- **The exporter writes SVG, PNG and `render.html` only.** No page is generated
  from it. A missing `starred.json` is still a prompt, not an error.

## Searching and naming

- **Symmetry is built in by choosing roots, never by hoping.** A row from
  mirrored roots is symmetric by construction; a random small-integer row
  essentially never is (1,500 draws, 0 hits).
- **Names state the construction**: kind + every mirrored pair + the middle
  count. `lace-1of9-3` = a lace (four or more self-crossings), pair at 1/9 and
  8/9, three roots at 1/2. `2x` marks a repeated pair. Settled.
- **The finds are split by batch.** Part 2 keeps the earlier family; the
  experimental page's foot carries only the newer batch, tangliest first, odd
  shapes included. Reason: a page for looking at new shapes should not be a
  second copy of the kept collection. `found-curves.json` marks each row
  `batch: first` or `batch: new`. Settled 2026-11-14, by the operator.
- **The "x row roots" axis turned out to be the bow, sampled finer.** A row like
  `[7, -25, 25]` is `7(1 - 3.57 t(1-t))`, a bow of 3.57 — between the old
  hand-picked 2 and 4. So the gain came from trying bow strengths that were not
  on the list, not from a new construction. The bow slider now reaches ±12 for
  that reason.
- **Finds land in `workbench/found-curves.json`**, which the galleries read at
  load. A row proportional to an existing seed is skipped.

## Process

- **No internet, no CI, no push without the operator saying so.**
- **Generated pages may be read.** Reading the built page is how a claim about
  the page is checked; the DOM is the evidence, not the generator's list.
- **A number in a report is measured, not recalled.** Counts, positions and
  order come from the DOM or from a script's printed output, with the command
  named.

## Frames start as thumbnails — 2026-11-19

Settled by the operator: "you can keep track of these pngs as simple thumbnails
basically. dont worry about the final pngs yet."

- The 90 `illus-` frames are **600 px thumbnails**, copied from the bordered set
  so the plates can be seen, ordered and named. `workbench/frames.json` records
  `thumbnailPixels` and says so in its note.
- The book-plate rule (3000 px, 300 dpi, 1.2% margin) still governs the **final**
  export and is not applied here. Re-rendering at print size is a separate step,
  after the set is chosen.
- A thumbnail is never called a plate. The `/frames` page says "plates" for the
  list and "thumbnail" in the data; the file's note carries the distinction.

## The app has one shell — 2026-11-19

Settled by the operator: "every page in astro should look like this: same css:
[title] · the hub · the book gallery · this page is the [title]", and "don't put
a link to the same file in the header; all industry standard best practice".

- **One header component**, `app/src/components/AppNav.astro`, rendered by every
  page right after `<body>`: the brand, the draft mark, the page's own name (the
  sentence "this page is the lab"), then a `<nav aria-label="Main">` list.
- **The current page is not a link to itself.** It is left out of the menu and
  the page's name is stated in the header instead. No `aria-current` on a link
  that would reload the page you are on.
- **A skip link** to `#main`, and every page has exactly one `<main id="main">`,
  so the menu is not the first thing the keyboard has to walk through.
- **Colours only from `curve-lab-theme.css`**; `app/public/vendor/app-shell.css`
  holds the layout and is linked after Pico and the theme on every page. A page
  that sets its own background is the out-of-date case.
- The check is `app/scripts/check-pages.mjs`: 12 pages, one header, one main,
  the draft mark, no self-link.

## Figures are files, not inlined SVG — 2026-11-19

`/illuminations` inlined 238 bordered drawings into one document: **82,689,119
bytes**, 0.96 s to build and send, every visit. Each figure is now
`/illuminations/fig-N.svg`, served with `Cache-Control: public, max-age=604800`
and a strong ETag, and the page asks for it with `loading="lazy"`.

- Measured after: the page is **307,907 bytes** (268× smaller) and 0.069 s.
  One figure is about 465 KB and is fetched once, then kept.
- The gallery build is memoised, keyed by the mtime of the registry and the
  notes, so a data edit rebuilds it and an unchanged page does not.
- The same rule applies to any future page with many drawings: a file per
  drawing, not one enormous HTML response.

## One star per curve — 2026-11-19

The finder stored stars by name and by id, so a curve starred under an old name
and again under its new one counted twice, and a mirrored curve that was also
featured was drawn in two sections.

- **`app/src/lib/star-list.js`** dedupes a stored list by the curve id (a name
  resolves through the page's own name→id table). A star whose name no longer
  maps is kept, never dropped.
- **Sections never overlap**: `app/src/lib/finder-sections.js` removes each
  group from the next, so "Symmetric" wins over "Best so far".
- **A removal is named.** Un-starring sends the name in `removed`; the page and
  the server both require it, so a partial list can no longer delete a star.

## Static checks are the gate — 2026-11-19

Settled by the operator: "a library? a methodology that is actually enforceable,
not just md?" — and "i consider typescript a BIG framework. but do it".

- **TypeScript through Astro.** `app/tsconfig.json` extends `astro/tsconfigs/base`;
  `npm --prefix app run check` runs `astro check`. It found 42 errors the first
  time, including the class that cost three sessions: a name used outside its
  scope in a page script.
- **ESLint with `no-undef`** checks `src/lib`, `src/scripts`, `tests` and
  `scripts`. It is the same fault at the plain-JavaScript edge.
- **A page carries no rules.** Its `<script>` is one import; the logic lives in
  `app/src/scripts/*.js` (linted) or `app/src/lib/*.js` (linted and unit-tested).
  `names-desk.js`, `finder-stars.js`, `illuminations.js` and `lab.js` follow it.
- **`draftState`** is the tested rule for a browser draft: it counts only when it
  is newer than the record's save, and never when it is empty. A saved name can
  no longer be hidden by yesterday's text.
- The rule behind all of it: **a rule that cannot fail a command is a wish.**

## Naming: quadrature, rotation, phasor — 2026-11-19

Settled by the operator: these numbers are not "imaginary", and the term is
banned from new prose and code. "Euler transform" was proposed and refused: it is
already a series transform in combinatorics, and "Euler angles" are a different
(3D) rotation convention, so it would add confusion rather than remove it.

The field's words, and the ones to use here:

- **complex number** — the numbers themselves (`a + bi`). Standard, neutral.
- **Gaussian rational** — a complex number with rational parts; **Gaussian
  integer** when both parts are whole. This is the object the project uses.
- **Gaussian rotation** (or **unit complex multiplication**) — multiplying by a
  unit Gaussian rational, i.e. a rotation by a rational angle. A p-triple is its
  integer generator.
- **quarter turn** — the 90° case, `× i` or `× (−i)`. Fully integer, closes in
  four steps.
- **quadrature component** — the part 90° out of phase (the engineering term, as
  in I/Q signals). Use it where "the imaginary part" was meant as "the component
  at a right angle".
- **phasor** — a unit complex number read as amplitude and phase. Use it for the
  prime mover travelling the circle, and for the pendulum stack, where the field
  already says "phasor" for exactly that.

The physical reading is worth keeping in the prose: a rotation is a rotation, the
circle is a circle, and the 90° part is a quadrature. Nothing in the geometry is
hypothetical.

## The prime mover, and who owns git — 2026-11-19

- **Curves may be driven by a circle, not a linear t.** The operator's reframing
  is in `state/PRIME-MOVER-int.md`: `PMx, PMy` travel the unit circle over
  `PM ∈ [−2π, 2π]`, the points come from p-triples (7-24-25 from (25, 0) to
  (24, ±7)), the points are reused, and the + and − walks are different sets.
  A new family says which driver it uses; the root family stays linear.
- **A fixed p-triple never closes at 2π.** Niven: rational cosines belong only to
  0°, 60°, 90°, 120°, 180°, so a repeated triple misses by a little more each
  step. The file names the three honest routes (state the gap, change the last
  triple, or use quarter and half turns) and requires the choice to be declared.
- **DeepSeek2 owns git.** It commits and pushes when `prepush` is green and
  reports the hash; DeepSeek1 decides, reviews and writes the handoff. One
  committer at a time, so two sessions cannot interleave a history.

## Data: SQLite through Prisma is the record — 2026-11-19

Settled by the operator after the naming loss and the desk save that never ran.

- **SQLite through Prisma** holds what a human edits: names, importance,
  rotation, pieces, border uid, stars, plate stars, users and sandbox saves. A
  save is a transaction; a bad uid is refused before a row is written.
- **The JSON files are seed and export.** `curve-registry.json` seeds the
  database; `curve-notes.json` and the star files are written on save and pushed
  to GitHub every five minutes, so a dead disk loses minutes, not data.
- **Snapshots are automatic** on dev start, before a build and before a
  migration: `.backup`, `PRAGMA integrity_check`, the last 20 kept, `npm run
  restore`. WAL is on.
- **The user directory is not public.** It is the one store deliberately kept
  out of GitHub.


## 2026-11-19 — the prime mover's method: remove the blind part, then station by the circle

Settled, with the reasons, so the argument is not had twice.

**1. A curve's circular part is invisible to a walk on the circle.** On any point with
`x² + y² = 1`, every term `c(x² + y²)` is the constant `c`. So an equation's circular part
cannot show up in a figure drawn on the walk: the character is the remainder. This is why
"take the circle out" is a method and not a decoration — it removes exactly the part the
walk cannot see.

**2. Removing a radial part cannot reshape a parametric curve.** For `x(t), y(t)`, any
removal acts along the radius, so the direction at each station is unchanged. A figure
that shows a different outline has changed the direction somewhere, which the circle
cannot do. The honest reform is therefore a **re-stationing**: `t = Y/(1+X)`, exact and
rational, so the curve lands on the lattice without a new shape claim.

**3. A rosette from a linkage is exact only when the closure is rational.** Closing a
four-bar joint is a circle–circle intersection; it is rational exactly when the closure
quadratic has a rational square discriminant. The parallelogram family satisfies this for
every rational crank direction; a general Grashof crank-rocker does not, so its figure
stays sampled and says so.

**4. Every algorithm's figure carries its formula.** A drawing without its equation cannot
be analysed: the reader cannot tell whether the reform is simpler. This is a rule for the
page, recorded because the table-only version of Fig. 9 was rejected by the operator.

**5. The reformed curve is stored as a re-stationing, not as `z·(P − C)/P`.** Settled
2026-11-19, when the row was entered as `c-0272`. The rule in §12 of the spec writes the
reformed point as `z·(P − C)/P`, but `P = x² + y²` is zero wherever the lace curve passes
the origin, so that curve has poles there and cannot be a record. The form that can be
stored is the re-stationing: the *same* curve sampled at `t = Y/(1+X)`, each station an
exact rational with its own rational point of the circle. Reason: it is the only form of
the reform that is exact everywhere, and it keeps the honest claim — a radial removal
cannot bend the curve, so the outline is unchanged. `scripts/circle_split.py`
(`reformed_record`) derives it, `scripts/add_circle_reform.py` enters it, and
`tests/test_circle_split.py` checks the row, the note and the drawing against one
derivation.

## The desk: one row per curve, a new curve beside its parent — 2026-11-21

Settled by the operator: "we might have 5 different versions from one spine, and that is good",
then "i want to choose the name if i want a new curve... and see it show up next to the old
curve in /plates ... all with UIDs".

- **A tuning row holds the four values for one uid.** *Save* merges it: only the four values
  and the turn are replaced, so a chosen name, a construction and every field the tune does
  not own survive. A save is one transaction, then the JSON copy, then the plate.
- **A new curve is a record, not a row.** It takes the next letter uid on its spine
  (`c-0002` → `c-0002a`), copies the geometry, records `params.variantOf`, and gets its own
  page. It is rendered at once, so it sits beside its parent on `/plates`.
- **A variant of a variant stays in the original series** (`c-0002a` → `c-0002b`), because the
  spine is taken from `params.variantOf`.
- **A name is unique** across registry names, aliases and uids, compared without case. A
  collision is refused and names the owning curve; it is never quietly suffixed.
- **The order is by uid for now.** `c-0002`, `c-0002a`, `c-0003` puts a variant next to its
  parent. The ten stars will take over the order later; that is not built.
- **The character rail is one law, not a choice.** `distance = base × (1 + strength ×
  profile)`, with the fold guard capping the whole width. A local pinch cap was tried on
  2026-11-21 and reverted: it is a second construction, and at the same saved number it drew a
  band about four times too wide. The operator: "you cant cheat and use another way to make
  the character rails."
- **The cap is solved directly, not by halving** (settled 2026-11-21). The rule is
  `distance × peak ≤ 0.9`; the used width is the largest safe width, so the band never narrows
  as the slider rises. Halving made it jump (`c-0002`: 2.2 % → 1.15 % at the next step).

## The unsaved default is 1.5 %, and an outline keeps its precision — 2026-11-21

- **A curve with no desk row starts at width 1.5 %**, plus 2, minus 2, bow. A saved row always
  uses its own values. The operator: "instead of 6%, set width of offsets to 1.5% for the ones
  i havent saved." Reason: 6 % was the old guard's *asked* width, drawn at about 1.5 % after
  halving; now that the guard is solved directly, 6 % is a genuinely wide band, so the untouched
  default is the width it used to draw.
- **The registry copies a sampled outline at six decimals, never two.** Two decimals is coarser
  than the step between samples on a curve of size 1–3, and it turns a smooth curve into a run
  of axis-aligned steps: `c-0143` (y = x² as a t² cover) drew as a staircase, not a parabola
  (2026-11-21, operator: "please fix underlying graph"). Identity still rounds to two decimals;
  the drawing does not. `scripts/repair_registry_paths.py` repairs, `tests/test_registry_paths.py`
  keeps it.

## A path rail's cap is continuous — 2026-11-21

The path rail keeps the one law: `distance = base × (1 + strength × profile)` over the refined
walk, with the rule that the distance stays below half the local radius. What changed is how the
rule is applied: a continuous ceiling that moves at most 0.25 per unit of arc length, not a
per-station value. The per-station cap jumped wherever the curvature did — on `c-0273` the
distance moved 4 % of the curve's size in one step and the edge made 105 sharp turns — and the
plate hid it by printing the spine only. The operator: "go for it", 2026-11-21. All 129 `path`
records, with the 56 `polyline` ones, now print two rails; the page draws the same band.

## The wonks are working shapes, not collection curves — 2026-11-21

The operator settled this before: the **wonks** are the raw halves, the kept curves are the
**doubles** (the "dwonkies", `double-…`, about 59 records). The 27 wonk records were therefore
taken out of the collection — registry, plates, figures and database — with
`scripts/remove_curve_records.mjs` (`--match '^wonk-[0-9]+$'`), which reports every file and keeps
a registry copy in `state/backups/`. The wonk **desk rows stay**, so `/hybrids-wonk` keeps its
source; the doubles are untouched.

## The plates page shows the chosen curves, and says why — 2026-11-21

The operator: "put the curves with stars? just dont put the ones with 1 star... that is why we
need the explanation below the curve."

- **A curve is shown when its rating is 2/10 or more.** A new curve (a variant) joins a kept
  parent even before it is rated; 1/10 and unrated are out. The rating is `importance`, edited in
  the database note, not the old boolean `starred` flag.
- **Every card prints a provenance sentence.** For a base: "Chosen at 5/10 · found in the finder."
  For a variant: "Variant of c-0001 (amper, 5/10) · width 1 % · ...". When a note was saved with
  the curve, that note is the proof; otherwise the formula, family or source is named.
  `app/src/lib/provenance.js`; guarded by `app/tests/provenance.test.mjs`.
- **Order is by uid for now**, so a variant sits beside its parent. The ten stars will take over
  the order later.
- The 2-star curves are included by the explicit rule; a 2-star curve that does not belong is
  demoted to 1 and leaves the page. That is the operator's decision, not a hidden filter.

## Every curve states its stars — 2026-11-21

The operator: "add the stars to every curve either stored or none if unstarred so far."

- **One explicit value per curve**: the rating 1–10 saved in the database note, or `none` while
  it is unstarred. `loadRegistry` sets `record.stars` (`number | null`); the export
  `data/curves.json` carries `stars` on every row. `none` is the absence of a rating, not a 0.
- **One source**: the note's `importance`. The registry seed does not gain a second copy.
- **Printed everywhere a curve appears**: `/figures` (all curves), `/curves/<uid>`, `/tune/<uid>`
  say `stars 5/10` or `stars none`; `/plates` carries the rating in its provenance sentence.
  `app/src/lib/provenance.js` (`starsOf`, `starsLabel`); guarded by `tests/test_curve_stars.py`.

## Ten stars are the rating, stored in place — 2026-11-21

The operator: "ten stars i can click and store."

- On `/tune/<uid>` a row of ten stars and a **none**. A click stores at once through
  `POST /api/curve-stars`, which writes the note's `importance` (0 = none) in one transaction
  and refreshes `data/curves.json`. The page label and every other page follow; 2/10 or more is
  on `/plates`.
- The status says `saving stars…`, `stars saved`, or `stars not saved: …`; a failure repaints the
  previous value. Clicking the star that is already set clears it to none.
- The rating has one source: the note's `importance`. The star row is the editor; the pages are
  readers.

## Marginalia: the docs carry the curves at a quarter scale — 2026-11-21

The operator: "documentation design that uses all these curves at about 1/4 size: ornamentation
in nice places on the page (astro starlight ... customize ... template ...)".

- **The name is Marginalia.** The theme is a recorded Starlight customisation, not a rewrite:
  `app/src/theme/marginalia/README.md` is the template record, the CSS and the `Head` override
  are the whole change, and the config adds two lines.
- **Every curve is an ornament at a quarter of the text width.** One single-stroke SVG per
  curve (the spine only), generated by `scripts/marginalia.mjs`; the set is gitignored and the
  tracked manifest is `ornaments.json`. The gallery `/ornaments/` is four-up, so each is exactly
  that quarter.
- **The placements:** the page title (25 % of the column), an `h2` companion, a blockquote's
  corner, the footer's flourish, the sidebar's foot. Each page gets four curves by a hash of its
  path, so a page is stable and the whole set is used across the docs.
- **Masks, not pictures:** the ornaments take the page's ink in light and dark from one file.

## Side curves are per-construction partners — 2026-11-21

The operator: "use only per-construction partner." The similarity and the width offset are not
the rule.

- **A side curve is the same construction with one parameter reduced**, about the construction's
  own centre (the origin): the mobile's arm length `r → r − d` (equal radii: `P_d = (1 − d)P`),
  the hybrid's middle weight `k → k − d`, the double's half radius `r → r − d` before the mirror.
  No normal estimate and no curvature cut: the curve is smooth because of how it is built.
- **The gap is the construction's, and it is measured.** For the mobile it is `d·|P|`, zero where
  the construction passes its centre — not a constant width. That is honest, not a defect.
- **The sandbox is the rule's home**: `scripts/side_curves.mjs` → `/workbench/side-curves.html`.
  Each of the three families states its parameter and formula; the width rail is a faint
  reference.
- **The migration is per family, never a silent switch.** The 212 PH rows need their speed or
  family parameter; the finder paths their generator parameter. Until a family's rule exists,
  the plates and the tune page keep the character width rail, labelled as the reference.

## No parallel curves as a general side curve — 2026-11-21

The operator: "NO PARALLEL CURVES AS A GENERAL RULE. PARALLEL CURVES LOOK TOO MECHANICAL,
EXCEPT FOR SCROLLWORK, AND A FEW SELECT CASES."

- **The side curve is the per-construction partner.** A parallel offset is not the general
  route: it is too mechanical, and at high curvature it is where an offset is least valid
  (the normal changes fastest, and the edge wobbles or folds).
- **Exceptions:** scrollwork, and a short list of select cases the operator will name. Only
  there may a parallel rail stay.
- **The character/width rails are legacy on the general set.** The plates and the tune page
  keep them only as a labelled reference until each family's partner rule lands. Nothing is
  stripped from the curated book plates silently; the migration is per family.
- **The standard tools, not hand-rolled geometry:** d3's centripetal Catmull-Rom for the drawn
  curve; the repository's Levien parallel-Bézier port (`app/src/lib/parallel-bezier.ts`,
  `curve_lab/parallel_bezier.py`) for the scrollwork/fitted exception. The overlapping-dot
  stroke is a thin drawing layer; the geometry is the construction.
- **The sandbox is the rule's home:** `/workbench/side-curves.html` has no parallel curve. The
  spine, the partner, the parameter and formula per family, and the measured gap.
