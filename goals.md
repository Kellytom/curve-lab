# Goals

The long arc: **plant-forms first, ornament-forms after.** The plant-form is the
first complete ornament: one full line, two rails, an ending, growth marks and
branches. The grammar is the deliverable, not one drawing.

## Plant-forms

Build a plant-form in this order. Each step must be visible in the proof page;
none may be skipped by drawing a pretty outline over a missing rule.

1. **Take a stalk.** One stem curve from the catalogue (a LAC, PH, Euler or
   recovered spine). The stalk is the centreline; it is not the outline.
2. **Make the two-sided offsets.** Use the exact/numeric offset route; the two
   rails stand off the stalk. Separate neighbouring curves by **2 × offset plus
   a little breathing room** so no two offsets touch or cross. A width is not a
   style: the offset distance is a declared number and the same number is used
   by the ending and the branches.
3. **Give it an ending.** Every stalk ends in one of:
   - a **flower** from the flower grammar (cardioid, trifolium, quadrifolium,
     astroid at present);
   - a **seagrass / leaf ending**;
   - if there is no flower or head, a **simple cone terminal**: two arcs of
     **radius 2 × the offset**, one from each rail, meeting in the middle at the
     centreline tip. Tangent to the rail at the base, pointed at the middle —
     a cone, not a blunt cap. **No bare tip.**
4. **Mark the integer-lattice hits.** Draw the points where the stalk centreline
   crosses the **integer lattice** in model space. Map those hits to the page;
   do not snap the stalk to the page grid.
5. **Add the growth mark.** At a lattice hit, put a small **pyramid on each side
   of the parallel curves** — a simple vine thorn. The base sits on the offset
   rail; the apex points outward. It is a mark, not a new curve family: small,
   local, and only at the lattice hits.
6. **Branch at some growth points.** At selected hits, branch off with smaller
   curves. Lower branches are **bigger than upper branches**; the scale falls
   with height. A branch inherits the offset, ending and terminal rules; it may
   carry its own lattice marks.
7. **Prove the form.** A plant-form page/print showing the stalk, both rails,
   the chosen ending, the lattice hits, the growth marks and at least one
   branch — with the offset distance and terminal radius written on it.

## Geometry rules

- **mm internally; +y up.** Flip at SVG/page output and say where.
- The **integer lattice** is in model space. The page grid is a ruler, not the
  lattice.
- Offset separation is **2 × offset + breathing room**; a catalogue of offsets
  is a set of non-touching curves, not a pile.
- The **cone terminal radius is 2 × offset**. The two arcs are tangent to the
  rails at their bases and meet at the centreline tip. The construction must
  state where the arc centres sit; the goal is a cone, not an approximate
  rounding.
- **Growth marks only at integer-lattice hits.** One pyramid on each rail at a
  hit; no marks between hits.
- **Lower branches bigger than upper branches.** The exact scale law is open;
  the monotonic rule is not.
- **No bare tip:** flower, seagrass, or cone terminal.
- Exactness follows the offset tier: PH/rational offsets may be exact; sampled
  curves are fitted. Do not claim exactness without a rail and its error.

## Ornament-forms

After the plant-form grammar is proved, apply the same construction — full line,
two rails, endings, lattice growth marks, branches — to ornament that is not
botanical: scrolls, volutes, fleur/cruciform, the recovered plates, the primal
studies, and the archetypal ornaments. The plant-form is the first ornament; it
is not a separate art project.

## Order of work

1. **Offset catalogue.** `workbench/stem-library-offset.html`, OffS1…: the
   formulaic offsets first, then the LACs via `design_from_spans` →
   `build_rail`; two-sided offsets; every pair separated by 2 × offset plus
   breathing room. Add multiple stems only after the base is settled.
2. **Cone terminal.** Add the two-arc, radius-2×offset cap to the terminal
   layer (`curve_lab/terminals.py` or a plant terminal module), with a proof of
   tangency and a test that rejects a bare tip.
3. **Growth-mark grammar.** Lattice-hit detection, the pyramid pair, and the
   rule that marks only sit at hits.
4. **Branch grammar.** Select hits, scale the branch down with height, and give
   the branch its own ending/terminal.
5. **Plant-form proof.** One complete stalk → offsets → ending → lattice marks →
   branch, then a small orchard of variants.
6. **Ornament-forms.** Reuse the grammar on the ornament families.

## Existing pieces

- `scripts/stem_library.py` and `workbench/stem-library.html` — the stalk
  catalogue (S and SM cards).
- `curve_lab/offsets.py` — `build_rail`, `cusp_ranges`, the offset machinery.
- `curve_lab/terminals.py` — `butt`, `point`, `arc`, `round`, `taper`; the new
  cone terminal belongs here unless it needs a plant-specific module.
- `curve_lab/piece.py`, `curve_lab/clearance.py` — `Piece`, `Trace`,
  `piece_clearance()`.
- `workbench/flowers.html`, `scripts/stems_print.py` — the flowers sheet and
  the stem/ending placement.
- `docs/FLOWERS-int.md`, `docs/PHILOSOPHY.md`, `docs/CLEARANCE.md`,
  `docs/JUNCTION.md` — the durable prose.

## Open decisions

- The integer lattice is model-space integer; confirm whether it is the design
  box or the page frame.
- The exact cone-terminal construction: arc centres, tangency points, and
  whether the two arcs meet at a true point or a tiny tangent join.
- Growth-mark size: fixed model size, or proportional to the local offset /
  branch scale.
- Seagrass/leaf ending grammar: blade count, taper, and how it joins the rails.
- Branch selection and scale law: which lattice hits branch, and the monotonic
  lower-bigger rule as a formula.
- Which flower forms are legal endings; the flowers page currently offers four.
- Whether the offset page and the plant-form proof are one page or two.
