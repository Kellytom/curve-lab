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

## Current (2026-11-19)

- **Landed:** the data layer (SQLite/Prisma, backups, GitHub sync), Astro 7 on
  Node 24, and the handoff commands. Kept as the record.
- **Name the 212 chosen curves** — in flight; the desk is `/names`.
- **The pictures** — the Gallery of Illuminations and the figures sheet, after
  the naming.
- Sprint 1 (the grid bill) is parked behind these; resume it when the pictures
  are signed off.

## Sprint queue — the found curves to plates (2026-11-18)

`state/SPRINT-int.md` holds the six-sprint plan; its **Sprint 1 (the grid bill)**
is the next action and is what `next-fhandoff-int.md` names. Earlier rows above
stay landed; this queue runs in parallel with the book and the app.

## Short-term milestone — the book, Christmas 2026

The operator's aim (2026-11-17): export PNG plates now for a book, with SVGs
and cubic Béziers later. Mostly symmetric curves, with character offsets, and
integer stations where a branch can attach.

| # | action | `Proves:` | needs |
|---|---|---|---|
| B1 | **plate pipeline** | six plates, white ground, no text, 300 dpi, tight to the curve; a plain gallery; seven tests | **landed 2026-11-17** |
| B2 | **landed 2026-11-17** — choose the plate set | 27 saved curves in the gallery, each with its character rails; the operator can pick | B1 |
| B3 | balance stations | for one curve, a page lists the lattice stations at a grid whose tangent is vertical, horizontal or a 3-4-5 direction, and any pair balanced about y = k; all exact; a test pins one | B1 |
| B4 | LibreOffice contact sheet | the plates inserted at trim size, one per page, and a PDF proof; no upscaling | B2 |
| B5 | **landed 2026-11-17** — character offsets | 25 of the 27 plates carry character rails (width %, plus/minus, bow/s/taper); the gallery prints them; two are spine-only because the base offset folds | B1 |
| B6 | **square and frame lab** | a live page: curve a, curve b, counts across and down, an a/b pattern, leg angle, print size, fill; the joins and leaf tips measured; a 1 pt stroke floor at 1–4 in; 18 JS tests | **landed 2026-11-17** |
| B7 | **landed 2026-11-17** — real curves in the lab | the selectors list the saved curves and none of the sandbox cubics; the lab draws `plate_math.js` groups with their character rails; the readout prints the paths and the note | B6 |
| B8 | **landed 2026-11-17** — the chain form | two curves end to end (a shallow leg, a steep leg), not flipped, with the join angle printed | B6 |

**The live action is B8, the chain form.** The book is at B2/B4; the JS port's
first slice is landed.

**B3 — balance, not symmetry.** A *balance station* is a lattice point at a
chosen grid whose tangent has a declared clean direction: vertical, horizontal,
or a Pythagorean slope such as 3/4. The branch then leaves at a clean angle. A
*balanced pair* is two such stations related by a declared horizontal axis
y = k — equal offsets above and below, or mirrored tangent angles — without the
curve itself being symmetric. For a PH or integer curve the derivative is a
polynomial, so a direction (a, b) is the rational root of `a·y' − b·x' = 0`, and
the rational-root theorem plus the station's grid condition enumerates the
candidates exactly; `scripts/ph_quintic_hits.py` already has the gcd method.
The one clean case proved so far is the symmetric PH candidate: a horizontal
tangent at t = 1/2, on grid 15 at (0, 5) after the station shift. Do not call
this symmetry; call it balance.

| # | session | the one action | `Proves:` | needs |
|---|---|---|---|---|
| S1 | **landed 2026-11-17** — cone terminal, proof half | Draw the two-arc cone terminal, default and **symmetric**, and wire it into the terminal report | A page shows the two arcs, `R = 2 × half`, both arc centres and the `√3 × half` tip at three offsets, and shows the symmetric mode snapping a leaned pair onto the centreline with its `shift` and `axis_twist` printed; a test regenerates the page; `tests/test_cone_terminal.py` still passes | engine, symmetric mode and eleven tests landed 2026-11-17 |
| S2 | **landed 2026-11-17** — offset catalogue: the integer cubic rail | Add the exact PH offset rail for `integer-105`, drawn beside the Levien fit on the same curve | A card shows both rails; the exact one is labelled exact; the fit reports its measured deviation; a test pins the exact rail | none |
| S3 | `Section` wiring (engine) | Terminals and clearance read `Section` instead of re-deriving width from the rails | The plant-form proof prints the same numbers before and after; a test fails if a terminal computes its own width again | S1 |
| S4 | **landed 2026-11-17** — curve completeness audit | One script checks every stored curve has a picture, grid, crossings, notes and a page link, and fills what is missing | `scripts/curve_audit.py` prints **179 rows and 0 gaps**; `tests/test_curve_audit.py` keeps it so | S2 |
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

## Future exploration — the map, not the queue

`state/EXPLORATION-int.md` holds the operator's ideas for what the set has not
tried: the pendulum mobile, Gaussian/Pythagorean transforms on the polynomial
rows, tweaks stored as rows, character rails on every curve including the set-aside
ones, tails, the review of what was never followed up, and the empty cells of
(crossings x inflections) from `state/SIMILARITY-int.md`. Nothing there starts
without the operator saying so.

## Parked — not in this plan

| thing | why it is parked | where it is recorded |
|---|---|---|
| One figure pipeline (review item 2) | Blocked on the operator's accept/reject of the factored views. Collapsing it now deletes evidence for an undecided judgement. | `TODO.md` "From the 2026-11-16 review" |
| Bézier step | The operator parked it until the curves and engine are complete. | `next-fhandoff-int.md` history; this plan's S5 |
| Primal studies (fire, water, earth, air) | After the ornament grammar, per `app/src/content/docs/docs/primal.md`. | `goals.md` |
| W03 fleur grammar, W04 twenty parameter sets | Board order, not this queue. | `state/BACKLOG-int.md`, `workbench/ornament-board.html` |
| Modulated width (former Stage IV) | Its own proof, after the ornament grammar. | `goals.md` |
| Other polygons (pentagon, pentagram) | Operator, 2026-11-17: squares and rectangles first; the same corner rule holds (54°, 18°) when they come back. | this table; `founder/LOG.md` |

## Astro app — the operator's new stack

| # | action | `Proves:` | needs |
|---|---|---|---|
| A1 | **lab + save in Astro** | the page at :4321 renders the 88 curves; a star and **save to workbench** write `workbench/starred.json`; 4 save tests in the gate | **landed 2026-11-17** |
| A2 | **landed 2026-11-17** — port the book gallery | an Astro page lists the star file and the simple designs; the generated `book/index.html` is retired | A1 |
| A3 | port pages on touch (the next action) | each moved page is deleted from the generators in the same commit; the shared maths stays one file | A2 |
| A4 | the Python bridge | one Node entry point calls the exact engine (or the spline connector) with a whitelisted operation, and a test round-trips one result | A1 |

**Note:** the book (B1–B5) and the older JS port feed Astro; A2 is the next
wiring step after B3/B4 if the operator keeps the book first.

## How a session ends

1. Its `Proves:` line is true, or the session stops and says why.
2. The action's own paths are committed; the suite is green (`scripts/test.py`,
   and `--browser` when a page control moved).
3. `state/HANDOFF-int.md` gets one block: what landed, what is next, what was
   tried and rejected.
4. `next-fhandoff-int.md` names the next row of this table, or `/fstart` parks it
   if the operator changes direction.
