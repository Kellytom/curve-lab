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
  so its rail is fitted. A symmetric PH curve is the third option and is not
  built.

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
