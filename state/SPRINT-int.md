# SPRINT-int — from found curves to plates, one session at a time

The job: take the curves found in the finder and get them onto a working integer
grid, with character offsets, so they can become book plates — and make the
records compatible enough that the sandbox and the plate exporter both read them.

This plan is written so any one sprint can be a whole session. Each has a
finish line you can judge without re-reading the conversation, and each names
the pain it expects.

## Where we start (measured 2026-11-18)

- **55 curves** in `workbench/finder.json`, in eight families.
- **29 position-polynomial, 25 rational, 0 PH-speed.** The sandbox gallery loads
  speed rows only, so **no finder curve loads there today**. That is the gap.
- Grids already visible: `48` (the 45° tangent curves), `567`, `3328`, `4864`
  (the loops). A grid of 4864 means every coordinate needs 4864 parts to be whole.
- The 5 starred curves are all septic loops, all mirror-symmetric about `y = x`.
- Tschirnhausen is off the board (operator, 2026-11-18).

## The rule that governs all of it

A formula is not "compatible" until its **kind** is declared and every tool that
reads it knows what to do with that kind:

| kind | what it holds | sandbox | plates |
|---|---|---|---|
| `position-poly` | `x(t), y(t)` polynomial rows | no | yes (sample) |
| `rational` | numerator and denominator per coordinate | no | yes (sample) |
| `ph-speed` | two rows `u, v` with `x' = u²−v²`, `y' = 2uv` | **yes** | yes |

Nothing is converted between kinds by approximation. A curve that cannot be
expressed as speed rows is simply not loadable in the sandbox, and says so.

---

## Sprint 1 — the grid bill

**Objective.** For every one of the 55 curves, state the integer form and the
grid it needs. No curve changes yet.

**Steps**

1. Rebuild each curve's exact polynomials from its `definition` (the annotator
   `scripts/curve_record_view.py` already does this for the formula line).
2. Clear denominators: multiply by the lcm, record the **scale** used.
3. Divide out the gcd of all coefficients, record the **minimal scale**.
4. Write `workbench/curve-records.json` (`curve-lab.records/1`): one row per
   curve with `kind`, `scale`, `grid`, `degree`, `formula`, `variables`.
5. Calibrate: `lace-1of8-3` must come out at grid **1155**, as the stored record
   says; if it does not, the method is wrong and the sprint stops there.

**Finish line (`Proves:`).** 55 rows; every row has a kind and a grid; the
calibration passes; the row for each of the 5 starred curves is printed in the
report with its grid and scale.

**Pain expected.** Rational curves have numerator *and* denominator; the grid is
the lcm over both. A mistake there makes every grid too small.

## Sprint 2 — shrink the grids

**Objective.** For each curve, the smallest equivalent scale, or a written reason
why it cannot shrink.

**Steps**

1. Divide rows by their gcd (already in Sprint 1) and check for common factors
   between numerator and denominator on rational curves.
2. Try the alternative settings that do not change the shape where the family
   allows it — e.g. the same loop solved from a different parameter pair.
3. Mark irreducible curves with the arithmetic reason, not "big".

**Finish line.** A table of before/after grids; the starred five improved or
proven minimal; no curve above 5000 without a reason on its row.

**Pain expected.** Some grids are genuinely large because the crossing parameters
are ¾ and ⅘; shrinking means choosing a different crossing pair, which changes
the shape — a decision, not a calculation. Those go to the operator.

## Sprint 3 — character offsets on every card

**Objective.** Each finder curve carries `character {width, plus, minus,
profile}` and its card draws the rails.

**Steps**

1. Add `character` to the record, defaulting to the plate values
   (`1.5%`, `2/2`, `bow`).
2. Draw the rails with the plate maths (`plate_math.group`), including the fold
   guard: shrink the width when `|d·κ|` would fold; at the 0.2% floor the card is
   spine-only and says so.
3. Show the rail values on the card.

**Finish line.** Every card either shows rails or says `spine only` with the
reason; a JS test pins one railed and one spine-only case.

**Pain expected.** The finder draws sampled polylines, not the analytic curve, so
the normal at a sampled point is an estimate. For plates this is what already
happens; for the fold test it is not exact — state that on the card.

## Sprint 4 — the plate bridge

**Objective.** One finder curve of each kind becomes a real PNG.

**Steps**

1. A `send to book` action writes a row into `book/plates.json` with a fresh
   serial, carrying kind, definition and character.
2. `scripts/plates_export.mjs` learns to sample from a record's `definition`
   instead of only `real-curves.json` names.
3. Export one position-poly, one rational, one ph-speed curve.

**Finish line.** Three PNGs at 300 dpi, white ground, no text, tight bounding
box, each with its character rails; the gallery lists them with their captions;
a test checks the file exists and the size.

**Pain expected.** The exporter currently assumes a curve name in
`real-curves.json`. The sampling path is the change; the rendering is already
right.

## Sprint 5 — the sandbox door

**Objective.** The sandbox reads the same records and loads what it can.

**Steps**

1. Teach the sandbox gallery to accept `kind: ph-speed` rows from
   `curve-records.json`.
2. For other kinds, show them in a read-only "finder" tab with kind, grid and the
   reason they cannot load.
3. Find one exact PH curve among our families to prove the door (if none exists,
   the tab is read-only and that is the answer).

**Finish line.** One curve loads in the sandbox from a record and draws; the other
kinds are listed with their reason; no silent conversion.

**Pain expected.** We may have **no** ph-speed curves left after Tschirnhausen
was retired. If so, this sprint ends by recording that the sandbox cannot be fed
from the finder at all — a real finding, not a failure.

## Sprint 6 — pick the book set

**Objective.** The operator chooses 10–20 curves; the book gets plates.

**Steps**

1. Star the keepers in the finder.
2. Export the starred set to plates with their character rails.
3. Print the contact sheet and the manifest.

**Finish line.** Every starred curve has a plate; the gallery shows only them;
`book/plates.json` names the set.

**Pain expected.** This one needs the operator, not the engine.

---

## How a session runs

1. Read this file, then `state/HANDOFF-int.md` tail and the register.
2. Take the **first sprint not marked done**. Work only its steps.
3. Stop at its finish line; do not slip into the next sprint.
4. Commit the sprint's own paths, then `/fhandoff` appends the block.
5. If a finish line needs a decision (a shape change, a set choice), write the
   question in `state/HANDOFF-int.md` and stop — do not pick for the operator.

## Out of scope

New curve families, Tschirnhausen, the sandbox's own controls, and the hub's
layout. Those are parked in `TODO.md`; this plan is about the 55 we have.
