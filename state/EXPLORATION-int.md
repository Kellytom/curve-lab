# EXPLORATION-int — what is not built yet, and why it might be worth it

The operator's ideas (2026-11-19), written down so they are not lost and not
started by accident. This is a map for the next block of work, not a plan with
dates; `state/PLAN-int.md` decides order, this file says what is on the map.

Each entry says: the idea, what already exists, what is actually new, and the
first measurable step.

---

## 1. The pendulum mobile — a vane that swings while the parts twirl

**The idea.** A mobile has a main vane that swings one way and then the other,
like a pendulum, while the smaller parts hang from it and twirl. The curve that
traces the small part is a *compound* motion: the vane's turn plus the part's
own rotation. That is not the same as a single rational rotation of a curve.

**What exists.** `scripts/mobile_exact.py` (compound rational rotations, grids
5, 10, 15, 50), `scripts/mobile_arcs.py` (a mobile cut between two rational
parameters, exact endpoints and tangents, one arc turning −90°), and the
`mobile-*` families in the registry.

**What is new.** Two independent motions — a swing `θ(t)` and a spin `φ(t)` —
composed into one trace, with both kept rational. A pendulum swing whose
amplitude decays is not a polynomial in `t`, so the honest options are: a
sawtooth swing (linear up, linear down) which is piecewise rational; or a swing
driven by the same root construction as the rows, so the composition stays a
polynomial. The second is the one worth trying first.

**First step.** One vanes-and-parts curve whose trace is a polynomial in `t`,
computed exactly, and whose grid is stated. If the composition does not stay
polynomial, say so and label it sampled — never claim exactness for a composed
motion that left the grid.

---

## 2. Gaussian and Pythagorean transforms on the polynomial rows

**The idea.** Take the basic curve `±var₁·t⁷ ± var₂·t⁶ …` and apply integer
Pythagorean transforms to it — the Gaussian rationals `a + bi` with `a² + b² = 1`
(`3-4-5`, `5-12-13`, `8-15-17`) — because "we have not used imaginary numbers
sufficiently".

**What exists.** `curve_lab/pyth_cubic.py` (the integer cubic family and its
catalogue), `curve_lab/pyth_g2.py`, the `pythagorean-spiral` turn lattice, and
the settled rule in `DESIGN-int` §Rotations are Gaussian rationals: a PH curve's
speed turns by half the angle, so rows stay whole only when `tan(θ/2)` is
rational.

**What is new.** Applying a Gaussian rational to *the general row polynomial*,
not to the PH speed pair and not only to cubics: rotate, scale, and re-normalise,
then ask what the grid becomes and whether the result is a curve the set does
not already hold. A rotation of the whole trace is a one-line operation on the
sampled path; the interesting question is the *integer* result and its cost.

**First step.** Take one stored curve, apply `q = 1/2, 1/3, 1/4, 1/5` turns,
and print for each: the scale needed to make the rows whole, the grid, and
whether the shape is new (the analysis table can answer the last one).

---

## 3. Tweaks stored in the database

**The idea.** Now that the data is organised, add ways to tweak a curve and keep
the tweak in the database, so a variant is a row and not a drawing.

**What exists.** `Note` (name, importance, rotation, pieces, border uid, sides,
border turn), `CurveMetric` (the measurements), and the API that validates and
stores note fields in a transaction.

**What is new.** A `Tweak` concept: the operation (a share on a coefficient, a
root added, a bow, a rail width), its parameters, the curve it was applied to,
and the result. Then a curve can carry its lineage, and two variants of one
parent can be compared by number.

**First step.** One table and one API route for a single tweak kind (a share of
a mirrored pair), proven by writing it, reading it back after a restart, and
recomputing the metric row from it.

---

## 4. Character rails on every curve — accepted and unstarred alike

**The idea.** Go back through all the curves, chosen and set aside, and give each
its character rails. "The character curves often reveal things about the primary
curves that are not seen at first. What looks like a line creates a form with
strong character and interest once the rails are put on it."

**What exists.** `workbench/plate_math.js` `characterRail` (width %, plus/minus,
bow/s/taper), the plate exporter, and the job now in flight that makes offsets
stored data (`Note.offsets`, `widthPct`, `plus`, `minus`, `profile`).

**What is new.** Applying it to *all 262*, including the 172 that are set aside,
and recording the result — not just to the 90 plates.

**First step.** With the offset fields landed, render every curve with and
without rails and record which fold (the 0.2% floor) and which gain a form worth
keeping. That is a table, not a taste.

---

## 5. Curves with a little tail

**The idea.** "There may also be simple curves with a little tail that once they
are worked on will produce beautiful curved forms."

**What exists.** The terminals layer (`curve_lab/terminals.py`), the ending fit
(`scripts/ending_fit.py`), and the leaf/chain central designs.

**What is new.** A deliberate appendage: a short span that leaves the main curve
at one end and curls — half a turn, a cusp, a hook — with the join declared.
Small changes of a coefficient at the top powers are the usual source of a tail;
the analysis table can flag curves whose end tangent is far from their chord.

**First step.** Find the stored curves whose end tangent is more than 30° off
their chord (a number `CurveMetric` can hold), and try a tail on three of them.

---

## 6. The review — a vein of gold may already be in the ground

**The idea.** "A careful review of all we have done may reveal a vein of gold we
can mine."

**What exists.** 262 measured curves, the register of faults, the achievements
ledger, and the plates. What has not been done is a pass that asks: which of
these results were never followed up?

**First step.** Read `state/ACHIEVEMENTS-int.md` and `state/HANDOFF-int.md` for
lines ending in "open", "unbuilt" or "not adopted", and list them with the
number that proves them. That list is the mine.

---

## 7. The empty cells — where the set has never been

From `state/SIMILARITY-int.md` (2026-11-19): **77 of 117** cells of
(crossing pairs × inflections) hold no curve. Examples with no occupant:
0 crossings with 4, 6, 7 or 8 inflections; 1 crossing with 7 or 8; 2 crossings
with none. These are shapes the registry simply does not contain, and the same
row-based search can reach them.

**First step.** Aim one search run at one empty cell with the grid under 1000,
and see whether the cell fills. If it does not, the cell may be arithmetically
empty — which is a result worth writing down.

**Run 2026-11-23:** three answers, in order.

1. `parametric_search.py --cell 0,4 --n 600` (the looping family): **0 of 600**.
2. `--family graph --cell 0,4 --n 600` (y = p(t), x = t, small whole coefficients):
   **0 of 600**; the measured inflections in (0, 1) never went above 3.
3. **The cell fills, by construction.** Take `p''(t) = (t − 1/10)(t − 3/10)(t − 1/2)
   (t − 7/10)(t − 2)` — four roots inside (0, 1), one outside — and integrate twice
   with zero constant and linear terms:

       x = t
       y = t²·(−21/2000) + t³·(29/480) + t⁴·(−79/500) + t⁵·(203/1000) + t⁶·(−3/25) + t⁷·(1/42)

   `curve_lab/measure.py` reads **4 inflections**, grid 2162160000000, bend 1.0000
   (a graph), and x = t is monotone so the crossing count is **0**. The cell is
   empty in the collection, not in the arithmetic.

**What that means.** The empty cells are empty because no record has those numbers,
not because the shape is impossible. Adding this graph would fill (0, 4) with a
plain polynomial, which is not a plant form — so the question for the operator is
whether a cell is worth filling with a shape that carries no design idea. A better
test is whether a *family we want* (a stem, a petal) can be pushed into the cell.

**Tool notes.** `--cell C,I` scans every candidate with the exact core, not only the
2+ crossing winners; `--family graph` draws y = p(t), x = t. Crossings are counted
on t ∈ [−1, 1] and inflections are read in (0, 1) by `measure.inflections`, so the
two numbers describe the same curve but not the same parameter window — worth
remembering when a cell match looks surprising.

---

---

## 8. The alternating odd polynomial, parametric

**The idea.** `y = x - x³ + x⁵ - x⁷`, and the same as a *parametric* curve:
`x = t`, `y = t - t³ + t⁵ - t⁷`. Signs alternate, powers are odd, the
coefficients are one.

**What exists.** The general row form already holds this curve: speed rows are
the derivative of each coordinate, so this is a position polynomial with speed
`x' = 1`, `y' = 1 - 3t² + 5t⁴ - 7t⁶`. Nothing new is needed to measure it: grid,
bend, inflections and crossings all come from the exact core.

**Why it is worth a look, not just a check.** The alternating signs give a shape
that flattens at one end and climbs at the other — a "wing" profile. At degree 7
it has three stationary points of `y`, so it is a candidate for a leaf with a
tail (see §5) rather than a knot.

**First step.** Measure it as a row curve (grid, inflections, crossings) and put
it beside the closest curve in `state/SIMILARITY-int.md`. If it is already in the
set's neighbourhood, the family is covered; if it is in an empty cell, it is a
new family and the higher degrees (`t⁹`, `t¹¹`) are a search axis.

---

## 9. An imaginary variable in the polynomial

**The idea.** Put an imaginary number in the variable of
`y = ±var₁t⁷ ± var₂t⁶ …`: evaluate at `t = i·s` instead of a real `t`.

**What that does, worked out.** With `P(z) = Σ aₖ zᵏ` and `z = i s`:

- even powers `z^{2m} = (-1)^m s^{2m}` — real;
- odd powers `z^{2m+1} = i (-1)^m s^{2m+1}` — imaginary.

So the curve is `x(s) = Re P(i s)` (the even terms, sign-flipped every other
one) and `y(s) = Im P(i s)` (the odd terms, likewise). Two real polynomials,
whole coefficients, on the same grid: the imaginary variable is a **sign
rotation of the coefficients**, not an approximation.

**One trap, found by working the example.** If the polynomial has only odd
powers — the operator's `y = x - x³ + x⁵ - x⁷` — then `P(i s)` is purely
imaginary and the curve is a **straight vertical line**. `x` is identically zero.
The transform only makes a plane curve when both parities are present, which is
exactly the general `±var₁t⁷ ± var₂t⁶` form. Say this in the notes so the idea is
not judged by the degenerate case.

**Why it is worth doing.** It is a second, independent way to fill the empty
cells: the same coefficient sets, read as a different curve. It also connects to
§2 (Gaussian transforms): multiplying by `i` is the quarter turn, and this is the
same operation applied to the variable rather than to the speed.

**First step.** Take three stored curves, form `P(i s)`, and report grid,
inflections and crossings for each. If the results land in empty cells of the
analysis, the transform is a search method, not a curiosity.

## How to use this file

- Nothing here starts without the operator saying so; `state/PLAN-int.md` owns
  the order.
- When an idea lands, move it to `state/ACHIEVEMENTS-int.md` with the command
  that re-derives it, and delete it here.
- When an idea is refused, say why here and keep the row — a refusal is a result.

---

## 10. Complex-coefficient search — TABLED, with the reason

**The idea.** Curves as one complex polynomial, `z(t) = Σ (a_k + i b_k) t^k`,
degree to 11, then simplified to integer rows and sections. A real coefficient
makes a graph, which cannot loop; a coefficient carrying `i` turns that term a
quarter turn, so `A + iB` is how a polynomial gets loops. This is the programme,
stated in full, and it is right.

**Attempted (2026-11-19).** `scripts/parametric_search.py`: 400 random
coefficient patterns, crossings counted on a sampled polyline. **Zero candidates
with two or more crossings.**

**Why that is not a result.** The same counter, pointed at `c-0262`, reports **1**
crossing where `scripts/ph_crossings.py` reports **9**. The counter samples by
index, and these curves loop tightly near one end, so it walks past the loops. A
blind counter and an empty space produce the same number. Do not read the zero
as "the space is empty".

**Next, in this order — both cheap.**

1. **Calibrate the counter**: it must report 9 on `c-0262`, 10+ on `c-0253` and
   19 on `c-0260` before it scores anything. Until then, no search result counts.
2. **Search from the knots out**: take one stored loop and add a quarter-turned
   copy of another stored curve, `A + iB`, then vary `B` and its sign. That uses
   curves known to loop rather than hoping a random coefficient set does.

`scripts/parametric_search.py` keeps its history and its serials; the page order
is newest first and starred pinned, so a future run lands on top by itself.

## Rich chat display — first step

Publish one existing answer as a page (`/chat-display/<date>-<slug>/`) and put the link in the chat
reply. Spec: `state/SPEC-chat-display-int.md`. Parked behind the curves and the book.

## The human figure in the centre — first step

The Sacred Heart (and the Immaculate Heart) built from the existing heart form plus a flame and
a cross, drawn at plate size with side curves, before any record. See `TODO.md`,
"The human figure in the centre". A traced statue is the fallback, labelled sampled.

## The classical canon — the direction for all the curves (2026-11-26)

The operator, 2026-11-26: "interesting curves, classic designs, roman, greek, french … this is the
direction we are taking with all the curves".

The first evidence is in hand: `workbench/quintic-guides-ornament.svg` (Fig. QG3) is 100 six-point
curves in ten classical families — cyma recta and reversa, echinus, Ionic volute, ogee arch,
rocaille, acanthus, arabesque, trefoil, Vitruvian scroll. It also measured the limit: **one
polynomial quintic holds one lobe comfortably** (fit error ≤ 0.5 grid units on the cyma, echinus,
volute and rocaille) and **fails on multi-lobe forms** (2.0–2.4 on the trefoil, arabesque and
acanthus). So the canon splits into two kinds of work.

**Lines, each with its first measurable step**

1. **Mouldings — exact, from arcs.** Cyma recta, cyma reversa, echinus, ovolo, cavetto, torus are
   pairs of circular arcs. First step: a moulding set built from arcs with their centres and
   radii, tangency solved, proportions checked against a cited source (Vitruvius III–IV, or
   Palladio I) rather than invented.
2. **The volute — exact, from arcs, not one curve.** The Ionic volute is a logarithmic spiral; the
   classical construction approximates it with a centred series of arcs. First step: one published
   proportional construction drawn as arcs only, with the arc centres and radii printed and the
   deviation from the true spiral measured.
3. **Gothic tracery — arcs meeting at a point.** The ogee arch and the trefoil are arc compositions;
   today's fit error shows why a single quintic cannot carry them. First step: a two-arc ogee with
   the tangency at the apex solved, then the trefoil as three arcs.
4. **The French scroll — the asymmetric lobe.** Rocaille C and S scrolls. First step: one C-scroll
   and its mirror as a pair, with the inflection and the two radii printed; the fit error today is
   0.50, so a quintic holds one of these already.
5. **Arabesque and vine — the bridge to `goals.md`.** A stem whose amplitude grows along the run is
   the plant-form arc the project already names. First step: one vine with a measured growth law,
   then check it against the ornament grammar rather than beside it.
6. **Greek meander — a boundary case, not a curve.** It is a polyline on a lattice, so it belongs to
   the grid work, not the Bézier work; only its rounded variant is a curve. First step: say which
   one is meant before drawing either.
7. **Rational quintics — the enabling decision.** Exact circles, ellipses and hyperbolas need
   weights; `state/QUINTIC-CONTROLS-int.md` records the gap. First step: add weights to the JSON
   schema and one family, then prove a circle comes back with radial error 0.

The order I would take: 1, then 3, then 2 — the arcs are exact and cheap, and they set the
moulding vocabulary the ornament grammar will need anyway.
