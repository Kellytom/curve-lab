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

---

## How to use this file

- Nothing here starts without the operator saying so; `state/PLAN-int.md` owns
  the order.
- When an idea lands, move it to `state/ACHIEVEMENTS-int.md` with the command
  that re-derives it, and delete it here.
- When an idea is refused, say why here and keep the row — a refusal is a result.
