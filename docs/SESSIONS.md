# The next sessions — proposed, not yet agreed

One focused action per session: build it, verify it, commit it, refresh
`next-fhandoff.md` with `/fhandoff`. This page exists because the public plan
(`PLAN.md` in the docs repository) states the order and the gates but not the
work inside each step. The order here follows `HANDOFF.md`; the code blocks are
**target APIs**, sketches to argue about, not shipped signatures.

## 1. Promotion gate 4 — one study from chains

**State:** gates 1–3 are done (`3f7a603`). This is the open one.

The condition is: *one W03 study is drawn entirely from Pythagorean chains.*
Study 01 is the target. Its spans already have the chain's own law in them:

| P01 span | chain law |
|---|---|
| line | zero turns |
| circular arc | constant turn per chord |
| Euler span (10°) | turns increasing linearly |
| corner between spans | an exact `quarter` or a whole triangle turn |

The blocker is arithmetic, not shape. A chain's heading is
`heading0 * triangle.direction ** k`, so every heading change is a whole
multiple of one triangle angle. P01's start heading is `atan2(305, 65) =
77.97°`, and its spans turn by 25°, 35° and 10°. No single triangle angle
divides 77.97° and 25°, so the chain cannot reproduce P01's node table exactly.

**Decision needed (operator):** which conformance rule?

- **A. Law-fitted, drift measured.** Build each span by its own law at a chosen
  `alpha` (e.g. 1°), re-anchor each span on the previous chain node, and report
  the worst distance to P01's nodes and headings. Accept if under a stated
  budget (say 2 units on a 1180-unit study).
- **B. Node parity.** Keep the 12 P01 nodes and headings as fixed constraints,
  and solve for a chain that passes through them. In general this has no exact
  solution in the group, so it becomes an optimisation with a published
  residual — more work, and a weaker claim than the layer usually makes.
- **C. Re-parameterise P01** so its angles are whole triangle turns (a new
  study, visibly close but not the old one).

Recommendation: **A**, because it keeps the exactness claim where it is true
(the plan of the chain) and states the drift to the old drawing as a
measurement, which is the posture used everywhere else in this project.

### Measured before writing the study

`scripts/spine_study_probe.py` walks the right half as one composite chain and
compares each span boundary with P01's node (rotated into the chain's frame):

| step | chords | worst drift | end heading |
|---|---|---|---|
| 1.0° | 115 | 14.9 units (0.99% of the 1510-unit height) | 16.94° |
| 0.5° | 221 | 30.0 units (1.98%) | 17.86° |
| 0.25° | 431 | 18.9 units (1.25%) | 16.23° |
| 0.1° | — | did not finish in two minutes (exact integers) | — |

The drift does not fall with the angle: it is dominated by quantising the
corners (P01's foot/tail corner is 77.97°), each of which swings the rest of
the study on a long lever. Finer steps also cost exact digits fast, so 0.1° is
already unaffordable in whole-number arithmetic. The band adds two 180° arcs
at the same cost.

That makes the decision sharper, not softer. A chain study is a **new plan with
a measured resemblance**, not a re-drawing of P01's node table. If the gate
means "the study is a chain object", option A passes with the table above. If
it means "P01's geometry, drawn by chains", the honest answer is that exact
chains cannot get there — option C (re-parameterise) or the float hybrid is the
only route, and both change what is being claimed.

**Files:** `clothoid_lab/spine_study.py` (new), `scripts/spine_study_01.py`,
`tests/test_spine_study.py`, `docs/spine-study-01.html`.

```python
# target API
def chain_for_span(span, alpha, chord, start):  # -> Spiral
    """line: turns 0; arc: constant turn; euler: turns 0,1,2,..."""

def study_01_from_chains(STUDY_01, alpha=math.radians(1.0)) -> Piece:
    """Every stroke a chain; returns Piece + a drift report."""
```

**Verify:** the study renders; every node/heading drift is reported against
P01; the worst drift is under the agreed budget; mirror is exact; tests.
**Commit:** `feat(spine): draw study 01 from Pythagorean chains`

## 2. W03 — the canonical fleur

`fleur_canonical()` from the measured reference
(`reference/fleur/png/metrics.json`: aspect 1.43, fill 0.17, symmetry 0.83),
with exact clothoid segments, the band as a `Bundle`, terminals per stroke, the
centre seam declared, and a silhouette render beside the numbers. Study 01
stays as history; do not conform studies 02–20 until the silhouette is
approved.

```python
def fleur_canonical(metrics=None, width=None) -> Piece:
    """The measured silhouette: petals, band, seam, terminals, contacts."""
```

**Verify:** silhouette against the reference metrics (aspect, fill,
symmetry); `piece_clearance()` passes with the seam contact; tests.
**Commit:** `feat(fleur): add the canonical fleur from the measured reference`

## 3. W04 — twenty parameter sets

Port the twenty option sets, generate P01–P20, add a CLI (one piece by id, plus
a contact sheet), and carry each piece's prompt and measured error.

```sh
.venv/bin/python -m clothoid_lab.studies --id P07 --out out/P07.svg
.venv/bin/python -m clothoid_lab.studies --sheet out/fleur-sheet.svg
```

**Verify:** 20 SVGs, 20 prompts, no failed joins, contact sheet reviewed.
**Commit:** `feat(fleur): generate the twenty fleur studies`

## 4. Turned terminals

The cap limit is 120°; a hairpin and the wrapped bulb turn past it. Fire needs
them. Build them as terminals that report their turn, and refuse a fold.

```python
# terminals.py
def terminal_turn(kind: str) -> float: ...
# piece.py: a terminal may be a cap or a turned end; the report says which
```

**Verify:** each turned end on a straight ribbon; a fold is refused; the W02
strip gains a turned-end row; tests.
**Commit:** `feat(terminals): add turned ends past the 120 degree cap limit`

## 5. Primal — earth

Terraces with corners and a taper. One grammar, one study, one page. Earth is
first because it needs no turned ends and no junctions beyond a declared join.

**Files:** `clothoid_lab/primal.py` (replace the sketch), `scripts/primal.py`,
`tests/test_primal.py`.
**Verify:** the card's `check` block (segment count, max turn, max corner, end
terminal) passes; the page renders; tests.
**Commit:** `feat(primal): earth as terraces with declared corners`

## 6. Primal — water

Sweep and reversal, round ends. The reversal is where the spine layer's apsis
rule and the engine's G1 span meet; carry the corner, do not smooth it.

**Verify:** reversal reported, no disallowed crossing in the sweep, tests.
**Commit:** `feat(primal): water as a sweep with a declared reversal`

## 7. Primal — air

Billowing arcs, round ends. The first study that wants a `Bundle` (several full
lines that must not touch), so `piece_clearance()` and the bundle report are
both exercised.

**Verify:** bundle clearance with one declared contact; tests.
**Commit:** `feat(primal): air as billows in a bundle`

## 8. Primal — fire (after session 4)

The Euler tongue with a point, and the first study that needs the turned ends.
Do not start it before session 4 lands.

**Commit:** `feat(primal): fire as an Euler tongue with turned ends`

## Then the archetypes

Fleur, acanthus, palmette — each one piece, one silhouette, measured. They come
after the primals because they reuse the same terminals, junctions and bundle.

## What this page does not decide

- The gate-4 conformance rule (session 1).
- Whether the public `PLAN.md` should link here, and which of these blocks are
  published. The docs repository is a separate, cleaned copy; do not mirror
  this page until the rule and the order are agreed.
- Any deploy, auth or board change. The board is generated; edit
  `scripts/board/`, never `docs/ornament-board.html`.
