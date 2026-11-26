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

## Split — DeepSeek1 owns the side curves, DeepSeek2 the NURBS flow (2026-11-21)

The operator: "deep1 will do the side curves (rails, offsets, whatever) and deep2 will
continue working on nurbs and curve flow from here to inkscape and back."

- **DeepSeek1:** the side curves — the per-construction partners (row speed scale, mobile
  arm, double half radius, hybrid weight), the character rail law and its fold guard, the
  tune page, the sandbox and the partner preview, the side curves on the plates, and the
  scrollwork/select exceptions. `workbench/plate_math.js`, `scripts/lib/plate-row.mjs`,
  `scripts/lib/plate-partner.mjs`, `scripts/print_plates.mjs`, `scripts/side_curves.mjs`,
  `scripts/partner_preview.mjs`.
- **DeepSeek2:** the NURBS work and the curve flow from here to Inkscape and back — the
  reduction, `app/src/lib/reduction/`, the chebyshev/parallel-bezier code, and the
  `/reduce/` desk. The plain-number formatter and its test in the tree are theirs.

Neither reserves files; the rule is the operator's latest words and the registers. Read
`docs/SIDE-CURVES.md` before changing a rail or the preset.


## Current (2026-11-24) — consolidated: the gothic desk done, the book rasters next

- **Done 2026-11-24/25 — the trim desk and its suggestion:** rational `t = p/q` cuts with the
  mirror end `(q−p)/q`, the plates-first list, rows sampling, per-branch cut marks, the tune→trim
  door, and a `recommendTrim` suggestion (constant-curvature legs, break at the curvature change
  or crossing, pull back 0.5 %, snap to a p-triple). c-0022 turned 180°; the plates page no
  longer reloads on background renders; the image-tracking policy settled.
- **Next 2 — c-0022's shape:** the operator says it looks wrong before any trimming. The plate
  and figure agree with the stored rows; compare the record with the wave3 definition and the old
  diamond figure, then correct the record or record the finding.

- **Done 2026-11-23/24 (this session):** the gothic desk (`/gothic/`, `/gothic/<uid>`) over every
  stored curve, with the measured mirror, the one-arm cut and the `?set=gothic` view; the cut as
  exact `t = 1/2 ∓ q`; the two-panel figure with the original and its integer hits; the
  rational-`t` menu; the Tschirnhausen pieces finished as six glue-ready Study rows; the four
  source pages named on the desk; the live browser check; register rows 70/71; the data repairs
  (transform slot, conversion slot, emblem generator, figures, draft badge, stills).
- **Next 1 — the missing book rasters** (`c-0398`–`c-0419`, the sidechat's next action): render
  the 3000 px plates with `print_plates.mjs --missing`, verify each file, and list them; the
  operator's book.
- **Done 2026-11-24 — the glue quintic (G3)** and its TypeScript conversion: `app/src/lib/glue.ts`
  with the six-condition solver, `glue-sandbox.ts`, `tests/js/glue.test.ts`; the page takes κ and
  dκ/ds at each end and prints all six numbers; the test pins 1e-9. The quintic's own loop mode is
  the next glue action.
- **Done 2026-11-24 — the crossings counter in TypeScript.** `app/src/lib/crossings.ts` is the
  twin of `curve_lab/crossings.py` (grid buckets, the same strict-orientation test);
  `tests/js/crossings.test.ts` matches the brute force on 50 random walks, pins a figure-eight
  and a triple point (three pairs), and the stored path records. The Python file stays for its
  Python consumers until they move.
- **Done 2026-11-24 — the analysis in TypeScript.** `app/src/lib/curve-analysis.ts` +
  `scripts/analyse_curves.ts` (the CLI): the exact metrics from `measure.ts`, the sampled spine,
  the stable crossing pairs. Six records deep-equal the committed JSON; `workbench/curve-analysis.json`
  is regenerated from the TS (405 rows: five last-decimal float differences and one semantic
  change — c-0217's two pairs at a near-stationary point were a sample-parameter artifact and are
  gone). `scripts/analyse_curves.py` is retired.
- **Next 2 — the TypeScript ports still to do:** `scripts/root_search.py`,
  `scripts/coupler_curves.py` (same algorithms, `.ts`), and `tests/test_regressions.py` → a TS
  register for the Node and browser checks.
- **Next 3 — a studied curve to a plate** needs the operator's word (Study row vs record).
- **Blocked:** the start-point shift / the symmetric cut's final reading; the human figure.



- **Landed 2026-11-23:** the rail crossings (`1f4ce27f`: dots, hidden spans, `rail-holes.json`),
  the tune page's readout and other-kinds strip (`39308c52`), the hub's stills and notes menu
  (`595cb33b`, `cedd703b`), the fold record (`9f832662`), the branch rule (`d791a41e`), the cut
  desk (`5d0208f6`, `c1c69719`, `1f7cbf59`, `69b490c0`, `6e458d6d`) and the shell's half-inch
  margin (`3dd2fca0`).
- **Not landed:** the start-point shift (needs the operator's word on the two endpoints); the
  human figure (needs the composition and the source image).
- **Next:** the 11 classical curves still missing from the collection (the count from
  `state/GAPS-int.md`), then the book set.

## Current (2026-11-22) — the side curves: equal offsets, then the starting point

- **Landed:** the equal-offset law (`3ceba869`) — the two sides take one strength (the average
  of the saved plus/minus); the bow is zero at the ends; no scaling of the drawn curve. The
  equal-sides and equal-ends test is `tests/js/plate-offset.test.mjs`.
- **Focus:** the starting-point shift — where a curve's offset endpoints differ by (dx, dy),
  move the curve's start by (dx/2, dy/2) so the gaps match. One plate generation with the
  finished law, not a loop.
- **Next:** the named scrollwork/select exceptions (the six flourish, curlicue, logspiral,
  involute are the candidates); the plate preset migration is this offset law.
- **DeepSeek2:** the NURBS reduction and the Inkscape round-trip; leave `/reduce/` and the
  plain-number formatter to them.

## Current (2026-11-21, late) — the review desk, Marginalia, the partners

- **Landed:** the review desk (`/review/`, bulk stars, scopes, refusals); the ten clickable stars;
  the plates curated (194 of 371, provenance, star order with variants); Marginalia (the docs
  ornament theme, all 371 at a quarter scale, the dot stroke); the wonks out; the side curves as
  per-construction partners (the sandbox with the row/mobile/double/hybrid families, d3 plotting,
  3 pt legend, optional caps); the row-family preview sheet (`partner-preview.html`, one row per
  family, the speed-scaled partners); the 11-degree reduction handed to DeepSeek2.
- **Next:** migrate the plates per family, starting with the row family; the operator names the
  scrollwork and select exceptions; `/fhandoff` after the next block.
- **Parked:** Sprint 1; the W01–W04 board order.

## Current (2026-11-21) — the tuning desk, the outlines, the path rails

- **Landed:** desk saves (save / new curve with its own uid / collision refusal / the save
  state); paired sliders; the fold guard solved directly, so the width never jumps; the first
  paint and the live redraw use one maths and one frame; stored outlines at six decimals
  (register 44); unsaved width 1.5 %; every stored outline draws the plate's band and the page
  matches (register 45). The plates and the 56 figures were re-rendered.
- **Next:** `/fhandoff` to write the block; then the ten-star order on `/plates`, once the
  operator names the ten. The path band action is landed.
- **Parked:** Sprint 1 (the grid bill); the W01–W04 board order.

## Current (2026-11-20, late) — the plates and the lab

- **Landed:** the four character values reach the plate (three faults, one row law in
  `scripts/lib/plate-row.mjs`, register row 39); `/tune/<uid>` draws again and starts from
  the saved row (row 40); `/tune/` is a live lab in the browser gate; the plate ground is
  transparent, and masters (3000 px) and web copies (1600 px) are both grey+alpha and both
  gitignored; `state/RESPONSIBILITIES-int.md` says overlap is allowed.
- **Next — the path-curve band fill.** The rail must be a band, not a blob, on a curve with
  corners and self-crossings (`c-0273`). Same action as the last handoff; it did not land.
- **Parked:** none.

## Current (2026-11-20, night) — the hybrid desk and the doubles

- **Landed:** the hybrid desk (343 candidates, Save / move to notes / reject, stars, names,
  drafts, duplicate refusal); the wonk page (28 wonks as text, pieces cut at `y = x`, doubles
  mirrored back, brown dots where the ends meet the cut); 125 saved rows promoted to records
  (c-0273 … c-0397, 397 curves, figures and thumbnails); the 45° preset recorded on every
  double with `exact: false`.
- **Next 1 — the clean rotated formula.** All doubles are displayed at 45°; write the turn
  into the parametric form instead of applying a matrix, e.g. delaying the cosine by half a
  period (`x = C(t)`, `y = S(t − 1/2)`), and prove the result is the same figure rotated.
- **Next 2 — the rotation control.** A preset per family (0 / 45 / 90) that turns the drawing
  and records the matrix; 45 stays `exact: false` and says so on the figure.
- **Next 3 — naming the promoted 125.** They are records with path-safe names; the naming
  desk can give them real names, the way the 212 were named.
- **Next 4 — promotion after every save.** `promote_saved.py` is run by hand; the sync or a
  script should pick up new saved rows so a keep does not wait for a session.
- **Parked:** the `data/` JSON dictionary and the sandbox export (sidechat), the print export.

## Current (2026-11-19, late)

- **Landed:** the naming desk (90 chosen, 90 named, 172 set aside), the frames
  (`illus-` A and B, 180 plates), the analysis table (`CurveMetric`, 262 rows),
  the message bus, recovery parity and job ownership, the stack page, and the
  essay on the logic of beauty.
- **The focus now: new families along the prime-mover line.** Circle-driven
  parametrics from p-triple tables (`state/PRIME-MOVER-int.md`), whole-control
  Béziers with loops, and the two-tone/fill design pass. The seven curated
  finds (six `bezier-loop-*`, one mobile) are in the collection and starred.
- **In flight (DeepSeek2):** variants **C** (corner rule) and **D** (C plus a
  tangent seam and a 50%/9% proportion), with a paragraph per A/B/C/D block.
- **Paused on a decision:** the print export (`scripts/book_export.mjs`, 3000 px,
  300 dpi, manifest) waits on whether the "scriptures" are a caption on the
  plate or text pages beside it.
- **Next after that:** the design report's top rows (`state/DESIGN-TODO-int.md`),
  then the exploration map (`state/EXPLORATION-int.md`) — the mobile, the
  Gaussian transforms, tails, and the 77 empty cells.
- Sprint 1 (the grid bill) stays parked behind these.

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
