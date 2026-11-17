# PLAN-int — the next few sessions

**This is a rolling plan.** The top row that is not marked landed is the next
session's action. It is edited at every handoff — a finished row is marked
*landed* and kept, a blocked one moves to *Parked* with the reason, a new
direction goes to the top — and it is never rewritten from memory. It is the
queue behind `next-fhandoff-int.md`; that file names only the one action.

Each action has a `Proves:` line, so it can be judged done without re-reading
the project. The order follows the operator's instruction, 2026-11-17: **the
curves and the engine are complete before the cubic Bézier step.**

**How much a session takes is the operator's call.** Work the queue from the top,
one action at a time, each committed when its `Proves:` line is true and reported
in one line. Keep going to the next row while the operator wants more; stop when
they say stop, when a row is blocked, or when a `Proves:` line needs a decision
nobody has made — and then write the question instead of picking.

| # | session | the one action | `Proves:` | needs |
|---|---|---|---|---|
| S1 | **landed 2026-11-17** — cone terminal, proof half | Draw the two-arc cone terminal, default and **symmetric**, and wire it into the terminal report | A page shows the two arcs, `R = 2 × half`, both arc centres and the `√3 × half` tip at three offsets, and shows the symmetric mode snapping a leaned pair onto the centreline with its `shift` and `axis_twist` printed; a test regenerates the page; `tests/test_cone_terminal.py` still passes | engine, symmetric mode and eleven tests landed 2026-11-17 |
| S2 | offset catalogue: the integer cubic rail | Add the exact PH offset rail for `integer-105`, drawn beside the Levien fit on the same curve | A card shows both rails; the exact one is labelled exact; the fit reports its measured deviation; a test pins the exact rail | none |
| S3 | `Section` wiring (engine) | Terminals and clearance read `Section` instead of re-deriving width from the rails | The plant-form proof prints the same numbers before and after; a test fails if a terminal computes its own width again | S1 |
| S4 | curve completeness audit | One script checks every stored curve has a picture, grid, crossings, notes and a page link, and fills what is missing | `scripts/curve_audit.py` prints 179 rows and 0 gaps; the report is committed | S2 |
| S5 | Bézier fitting | Fit three stored curves with cubic spans and print span count and deviation as a share of the curve's size | `scripts/bezier_fit.py` and `tests/test_bezier_fit.py`, deviation under the tolerance the script states | S1–S4 |

## Why this order

- **S1** finishes the terminal layer the review left alone, and the engine half
  is already proven, so the session is page work and one report line.
- **S2** is the oldest open item in `goals.md` (the integer curves have no rails)
  and it produces a measured comparison, not a drawing.
- **S3** removes the "three notions of the same station" the 2026-10-26 review
  named; it is engine consolidation, done after the terminal that uses it.
- **S4** makes the 179 stored curves trustworthy as a set, which is what "the
  curves are complete" has to mean.
- **S5** is the Bézier step, only when the four above are true.

## Parked — not in this plan

| thing | why it is parked | where it is recorded |
|---|---|---|
| One figure pipeline (review item 2) | Blocked on the operator's accept/reject of the factored views. Collapsing it now deletes evidence for an undecided judgement. | `TODO.md` "From the 2026-11-16 review" |
| Bézier step | The operator parked it until the curves and engine are complete. | `next-fhandoff-int.md` history; this plan's S5 |
| Primal studies (fire, water, earth, air) | After the ornament grammar, per `docs/PRIMAL.md`. | `goals.md` |
| W03 fleur grammar, W04 twenty parameter sets | Board order, not this queue. | `state/BACKLOG-int.md`, `workbench/ornament-board.html` |
| Modulated width (former Stage IV) | Its own proof, after the ornament grammar. | `goals.md` |

## How a session ends

1. Its `Proves:` line is true, or the session stops and says why.
2. The action's own paths are committed; the suite is green (`scripts/test.py`,
   and `--browser` when a page control moved).
3. `state/HANDOFF-int.md` gets one block: what landed, what is next, what was
   tried and rejected.
4. `next-fhandoff-int.md` names the next row of this table, or `/fstart` parks it
   if the operator changes direction.
