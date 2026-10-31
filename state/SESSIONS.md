# The next sessions — proposed, not yet agreed

One focused action per session: build it, verify it, commit it, refresh
`next-fhandoff.md` with `/fhandoff`. This page exists because the public plan
(`PLAN.md` in the docs repository) states the order and the gates but not the
work inside each step. The order here follows `HANDOFF.md`; the code blocks are
**target APIs**, sketches to argue about, not shipped signatures.

## 1. Promotion gate 4 — one study from chains

**State: done.** Gates 1–3 landed in `3f7a603`; gate 4 is met under the
operator's fidelity rule (2026-10-30): **worst span-end drift at most 1.6% of the
study height**. The candidate at 0.5° steps measures **1.29%**. The full rule,
its precedent and its caveats are in `FIDELITY.md`; read that before quoting the
number.

The condition was: *one W03 study is drawn entirely from Pythagorean chains.*
Study 01 is the target. Its spans already have the chain's own law in them:

| P01 span | chain law |
|---|---|
| line | zero turns |
| circular arc | constant turn per chord |
| Euler span (10°) | turns increasing linearly |
| corner between spans | an exact `quarter` or a whole triangle turn |

The arithmetic is the constraint. A chain's heading is
`heading0 * triangle.direction ** k`, so every heading change is a whole
multiple of one triangle angle. P01's start heading is `atan2(305, 65) =
77.97°`, and its spans turn by 25°, 35° and 10°. No single triangle angle
divides 77.97° and 25°, so the chain cannot reproduce P01's node table exactly.

### The measured table (study 01, right half)

In P01's own frame; the study height is 1510 units.

| turn step | chords | worst drift | of height | build |
|---|---|---|---|---|
| 2° | 62 | 66.19 units | 4.38% | 0.08 s |
| 1° | 115 | 21.38 units | 1.42% | 0.08 s |
| 0.5° | 221 | 19.44 units | **1.29%** | 0.25 s |
| 0.25° | 431 | 20.76 units | 1.38% | 1.45 s |
| 0.125° | 852 | 1.67 units | **0.11%** | 9.44 s |
| 0.0625° | — | did not finish in 60 s | — | — |

The coarse steps are not monotone: independently rounded corners can add or
cancel, so 0.5° beats 0.25° by luck. At 0.125° the grid is fine enough that the
residual collapses. **Finer triangles do converge; cost rises steeply.** An
earlier version of this page said the drift "does not fall with the angle"; that
was wrong and is corrected here.

The chain study is still a **new plan with a measured resemblance**, not P01's
node table: the ported P01 matches within 0.03 units, the chain candidate within
19.44. Do not call it parity.

**Files:** `clothoid_lab/spine_study.py` (new), `scripts/spine_study_01.py`,
`tests/test_spine_study.py`, `workbench/spine-study-01.html`.

```python
# shipped API
def composite(spans, alpha_deg=0.5, start=(0, 0), heading=0.0):
    """Walk the spans as one rational chain; return points, span ends, heading."""

def study_01_from_chains(alpha_deg=0.5) -> Piece:
    """The right half mirrored, plus the band, every stroke a chain."""

def report(alpha_deg=0.5) -> dict:
    """Per-span drift from P01, the worst, and the study height."""
```

**Verify:** the study renders; every span end is reported against P01; the
worst is at most 1.6% of height; the metric is named; tests.
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

Choose the centre seam and any branch points on the **exact** curve, pin them,
then generate the practical profile for output (`FIDELITY.md`).

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
  `scripts/board/`, never `workbench/ornament-board.html`.
