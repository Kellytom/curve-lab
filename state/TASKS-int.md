# TASKS-int — the working checklist for this session

Checked means done and verified in the repo. Unchecked means not done, with the
reason in the row. No item is removed: a dropped item keeps its line and gains
a reason.

## Grid and lattice hits

- [x] Showcase: a grid and its hits behind all 399 panels.
- [x] `plant_forms.figure`: pillar, monstrance, the three proofs, ending fit,
      modulated width (37 figures).
- [x] Stem library: 177 figures.
- [x] The piece renderer (`svg.document`, opt-in `grid=True, marks=True`):
      fleur sets, fleur grammar, study 01, piece model, dual G2 piece, primal,
      spine sheet, branch points, practical curve.
- [x] Catalogue cards, generators page, curves-all, hearts, euler match,
      euler sections, euler square, stem-offset library, modulated width.
- [x] stage-two (11/11) and catenary (25/25) by the overlay pass.
- [x] The tails: grid-explained, showcase-notes, pythagorean-families,
      curve-families, lac-parallel, modulated-width-proof, spine-study-01.
- [x] Hub thumbnails rebuilt from the decorated pages.
- [x] One mark colour, `#b23a2b`, everywhere: 15,146 marks, 0 non-red.
- [x] No gold in any figure; the integer construction is red.
- [x] Marks sampled evenly per curve, so they no longer stop halfway.
- [x] Ornament board: thumbnails left clean, lightbox decorated — verified in
      Chrome, 18 rules and 24 hits inside the dialog.
- [x] fleur-studies page — left out of the grid work by instruction; the page
      itself still regenerates from the board build.
- [x] Board writes into `workbench/`, not `sandbox/`; the untracked directory
      is gone.

## Showcase fixes

- [x] 11f is one complete bicorn; 11g is four, moved to the origin and turned
      90° apart.
- [x] 13a smoothed by corner cutting over 26 triangles (max curvature
      3.2 → 1.8, no overshoot spikes).
- [x] 20a runs a finer rung schedule: 15 integer nodes instead of 11.
- [x] 19b growth marks are thorn triangles on the curve's normal.
- [x] The Rays figure has a grid and red hits on the 24 rays.
- [x] 6a/6b and every other dot read red, not gold.

## Pages

- [x] `workbench/showcase-effects.html` — "34 · Cloud effects", 7 figures,
      with a Composite curves section for the Euler clouds.
- [x] Page 2 is `showcase-notes.html`: "Not on this showcase" lives there.
- [x] `showcase-effects` registered in the manifest and the hub (60 pages).

## Integer cubics

- [x] Deep dive: an S cubic hits the lattice at exactly t = 0, ½, 1 at scale 1
      (3 points), and at t = k/q when the drawing is scaled by q³.
- [x] Hit ladder measured and published: 3 / 3 / 5 / 5 / 9 / 11 / 29 at
      q³ = 1, 8, 27, 64, 125, 1000, 15625 — a section on the catalogue page.
- [x] The cubic panels now draw their own integer points and state the count.
- [x] Rotating by another p-triple angle adds no hits: measured, kept as a
      negative result rather than a missing feature.

## Housekeeping

- [x] Senior-dev consolidation pass recorded in `TODO.md`, to run after the
      showcase and its notes are finished.
- [x] This ledger.

## Known limits, recorded rather than hidden

- [ ] The board's lightbox grid is in page units, not the design's own units.
      The design JSON (`desc id="curve-lab-design"`) would give true units for
      the `curve_lab` plates; that refinement is not done.
- [ ] Optional refinement: use the design units from
      `desc id="curve-lab-design"` for the `curve_lab` plates in the board
      lightbox. Page units were what was asked for; this would make the marks
      quotable in millimetres.
