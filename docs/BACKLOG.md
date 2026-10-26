# Backlog — the ornament pass

The **order** is chosen on the visual board: [`docs/ornament-board.html`](ornament-board.html).
Labels are stable: **P01–P20** plates, **W01–W10** work items, **D01–D06**
design decisions. The board is the authority on what comes next; this file keeps
the execution detail for each label.

Open the board, rank, tag, then copy the order back into the session.

## Rules

- One item at a time; one verify; one commit. Do not bundle.
- Keep the public URL private; auth/rate limiting stays deferred.
- Never touch `out/play-template.svg`.
- Do not change `vendor/` or the cap JSON.
- If an item needs a taste or product decision, put the question under it and
  stop; do not invent. Record the answer on the board under D01–D06.
- If a verify fails twice for the same reason, stop and write the reason.
- Deploy only where marked; app deploys are thin now (about 30 s).
- Tests must stay green: `.venv/bin/python -m unittest discover tests` (96 now).

## Done

- **M0 — image split.** Engine base `clothoid-engine:2026-10-26` plus a thin app
  image. First app-only deploy took 30 s; revision `clothoid-web-00004-nwx`;
  parity passed. Commit `eb67f4c`.

## W01 — Piece model

A piece is several named traces: the half-stroke, the band, the two parallels,
then the mirror. The engine renders one chain today, so this is the gate.

- Add a `Piece` (or `Trace` list) model: named chains, style/layer per trace,
  a mirror flag, and the page/frame metadata.
- Teach the SVG writer to emit several paths and a mirrored group.
- Tests: a two-trace piece with a mirror; metadata round trip.
- Do not change the single-design CLI path.

**Verify:** tests + one SVG that opens in Inkscape.
**Commit:** `feat: add a piece model for several traces`

## W02 — Terminal vocabulary

- Point (corner), arc (small 5ⁿ radius), round (half-width), taper (converging
  rails). Apply to open trace ends; report the terminal like a join.
- Keep the current blunt join as `butt` so nothing regresses.
- Tests: each terminal on a straight ribbon; a fold/negative-width rejection.

**Verify:** tests + a one-page terminal strip.
**Commit:** `feat: add point, arc, round and taper terminals`

## W03 — Fleur grammar

- Port the old half-stroke grammar from `ornaments/assets/ornament_set.js`:
  foot, tail, band, petal, lance, with its lines, 5ⁿ arcs and Euler spans.
- Use W01 for the piece, W02 for the ends. The mirror is W01's.
- First target: **P01**, study 01, at its old parameter values.
- Keep the report: spans, joins, copy error, fold. No fill.

**Verify:** `P01` renders; its joins are the old grades or better; tests.
**Commit:** `feat: port the fleur grammar to clothoid spans`

## W04 — Twenty parameter sets

- Port all twenty option sets from `ornament_set.js`; generate **P01–P20**.
- CLI: one piece by id, plus a contact sheet.
- Each piece carries its prompt and its measured error.
- This is the first “all the ornaments” milestone.

**Verify:** 20 SVGs, 20 prompts, no failed joins; contact sheet reviewed.
**Commit:** `feat: generate the twenty fleur studies`

## W05 — Stage II: eight storeys

Monstrance, pillar, flower, crib, church, ship, crucifix, tree. Reuse the part
library; no new curve grammar unless a piece demands it.

**Verify:** 8 pieces, one contact sheet, joins reported.
**Commit:** `feat: add the eight Stage II storeys`

## W06 — Stage III: six analogies

Building, body, plant, eucharist, communion of saints, altar. Each piece is one
analogy; every part named.

**Verify:** 6 pieces, one contact sheet, joins reported.
**Commit:** `feat: add the six Stage III analogies`

## W07 — Stage IV–V: boteh and scroll

The bent leaf on the round back, then the scroll and the volute. The paisley
grammar and the spiral units.

**Verify:** the boteh family and the scroll/volute set render; fold reported.
**Commit:** `feat: add the boteh and scroll families`

## W08 — Drapery and church decoration

Hanging cloth, folds, the curtain and the corridor. The fold report is the
design instrument; a fold must be chosen, not discovered.

**Verify:** one drapery study at a stated width, fold ranges printed.
**Commit:** `feat: add the drapery studies`

## W09 — Sliders per family

Tune the chosen grammar's parameters in the browser. The JSON stays the source
of truth; the sliders are a layer over the family parameters, not raw segments.

- Depends on W03/W04.
- Extend the headless layout gate to the new controls.

**Verify:** headless Chrome at 390 px; a slider changes the SVG; tests.
**Commit:** `feat(web): add sliders for the ornament families`

## W10 — Persistence and share

Remember a design across reloads and put it in a link. Later than the geometry,
but cheap. Depends on nothing.

**Verify:** reload restores; a `#d=` link restores; tests.
**Commit:** `feat(web): remember and share designs`

## Blocked

- **Auth and rate limiting.** Deferred by operator decision; keep the URL
  private.
- **Parametric caps.** Needs a product decision about which cap family is worth
  parameterising; do not invent one.
